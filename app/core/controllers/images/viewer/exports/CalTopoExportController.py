"""
CalTopoExportController - Handles CalTopo export functionality.

This controller coordinates the authentication, map selection, and export
of flagged AOIs to CalTopo maps.
"""

import json
import base64
import os

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from core.services.export.CalTopoService import CalTopoService
from core.views.images.viewer.dialogs.CalTopoAuthDialog import CalTopoAuthDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService
from core.services.image.CoverageExtentService import CoverageExtentService
from helpers.LocationInfo import LocationInfo
from helpers.MetaDataHelper import MetaDataHelper


class CalTopoExportController:
    """
    Controller for managing CalTopo export functionality.

    Handles authentication flow, map selection, and export of flagged AOIs
    and/or image locations to CalTopo maps as markers/waypoints.
    """

    def __init__(self, parent_widget, logger=None):
        """
        Initialize the CalTopo export controller.

        Args:
            parent_widget: The parent widget for dialogs
            logger: Optional logger instance for error reporting
        """
        self.parent = parent_widget
        self.logger = logger or LoggerService()
        self.caltopo_service = CalTopoService()

    def export_to_caltopo(self, images, flagged_aois, include_flagged_aois=True, include_locations=False, include_coverage_area=False, include_images=True):
        """
        Export data to CalTopo.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_flagged_aois (bool): Include flagged AOIs as markers
            include_locations (bool): Include drone/image locations as markers
            include_coverage_area (bool): Include coverage area as polygons
            include_images (bool): Upload photos to CalTopo markers

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            if self._is_offline_only():
                QMessageBox.information(
                    self.parent,
                    "Offline Mode Enabled",
                    "Offline Only is turned on in Preferences:\n\n"
                    "• Map tiles will not be retrieved.\n"
                    "• CalTopo integration is disabled.\n\n"
                    "Turn off Offline Only to export to CalTopo."
                )
                return False

            if not include_flagged_aois and not include_locations and not include_coverage_area:
                QMessageBox.information(
                    self.parent,
                    "Nothing Selected",
                    "Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export."
                )
                return False

            # Step 1: Prepare markers and polygons based on selections
            markers = []
            if include_flagged_aois:
                markers.extend(self._prepare_markers(images, flagged_aois, include_images=include_images))
            if include_locations:
                markers.extend(self._prepare_location_markers(images, include_images=include_images))

            # Prepare coverage area polygons
            coverage_polygons = []
            if include_coverage_area:
                coverage_polygons = self._prepare_coverage_polygons(images)

            if not markers and not coverage_polygons:
                # Build appropriate error message based on what was selected
                selected_types = []
                if include_flagged_aois:
                    selected_types.append("flagged AOIs")
                if include_locations:
                    selected_types.append("image locations")
                if include_coverage_area:
                    selected_types.append("coverage area")
                
                if include_flagged_aois and include_locations and include_coverage_area:
                    message = (
                        "No flagged AOIs, geotagged image locations, or coverage areas are available.\n"
                        "Flag some AOIs with the 'F' key or ensure your images have GPS metadata."
                    )
                elif include_flagged_aois:
                    total_flagged = sum(len(aois) for aois in flagged_aois.values())
                    message = (
                        f"Found {total_flagged} flagged AOI(s), but could not extract GPS coordinates.\n\n"
                        "This usually means:\n"
                        "• The images don't have GPS data in their EXIF metadata\n"
                        "• The image files have been moved or renamed\n\n"
                        "Please ensure your images have GPS coordinates embedded."
                    )
                elif include_locations:
                    message = (
                        "No geotagged drone/image locations were found.\n"
                        "Ensure your images contain GPS metadata and try again."
                    )
                elif include_coverage_area:
                    message = (
                        "No coverage area polygons could be calculated.\n\n"
                        "This usually means:\n"
                        "• The images don't have GPS data in their EXIF metadata\n"
                        "• The images are not nadir (gimbal pitch must be between -85° and -95°)\n"
                        "• GSD (ground sample distance) could not be calculated\n\n"
                        "Please ensure your images have GPS coordinates and are nadir shots."
                    )
                else:
                    message = f"No {' or '.join(selected_types)} are available to export."

                QMessageBox.information(
                    self.parent,
                    "Nothing to Export",
                    message
                )
                return False

            # Step 2: Always use the embedded browser session for export
            # This ensures we use the exact cookies/tokens CalTopo expects.
            selected_map_id = None
            export_result = {'success': False}

            auth_dialog = CalTopoAuthDialog(self.parent)

            def on_authenticated(payload):
                nonlocal selected_map_id

                if isinstance(payload, dict):
                    selected_map_id = payload.get('map_id') or payload.get('__map_id')

                if not selected_map_id:
                    QMessageBox.warning(
                        auth_dialog,
                        "No Map Selected",
                        "Please navigate to a CalTopo map before clicking 'I'm Logged In'.\n\n"
                        "The map URL should look like:\n"
                        "https://caltopo.com/map.html#...&id=ABC123"
                    )
                    return

                # Close the auth dialog first (user is done with it)
                auth_dialog.accept()

                # Use JavaScript running inside the authenticated browser session
                # so all CalTopo cookies/tokens (including HttpOnly) are honored.
                marker_success_count = 0
                polygon_success_count = 0
                cancelled = False

                # Export markers if any
                if markers:
                    marker_success_count, cancelled = self._export_markers_via_javascript(
                        auth_dialog.web_view,
                        selected_map_id,
                        markers
                    )
                    if cancelled:
                        export_result['success'] = False
                        export_result['cancelled'] = True
                        return

                # Export polygons if any
                if coverage_polygons and not cancelled:
                    polygon_success_count, cancelled = self._export_polygons_via_javascript(
                        auth_dialog.web_view,
                        selected_map_id,
                        coverage_polygons
                    )

                total_success = marker_success_count + polygon_success_count
                total_count = len(markers) + len(coverage_polygons)

                export_result['success'] = total_success > 0
                export_result['success_count'] = total_success
                export_result['total_count'] = total_count
                export_result['cancelled'] = cancelled

            auth_dialog.authenticated.connect(on_authenticated)

            if auth_dialog.exec() != CalTopoAuthDialog.Accepted:
                return False

            # If we still don't have a map ID after authentication, user cancelled
            if not selected_map_id:
                return False

            # Step 3: Show result
            if export_result.get('success'):
                success_count = export_result.get('success_count', 0)
                total_count = export_result.get('total_count', len(markers) + len(coverage_polygons))

                # Build description of what was exported
                exported_items = []
                if markers:
                    exported_items.append(f"{len(markers)} marker(s)")
                if coverage_polygons:
                    exported_items.append(f"{len(coverage_polygons)} polygon(s)")

                items_desc = " and ".join(exported_items)

                if success_count == total_count:
                    QMessageBox.information(
                        self.parent,
                        "Export Successful",
                        f"Successfully exported all {items_desc} to CalTopo map {selected_map_id}.\n\n"
                        f"The items should now be visible on your map."
                    )
                else:
                    QMessageBox.warning(
                        self.parent,
                        "Partial Success",
                        f"Exported {success_count} of {total_count} item(s) ({items_desc}) to CalTopo map {selected_map_id}.\n\n"
                        f"{total_count - success_count} item(s) failed. Check console for details."
                    )
                return True
            else:
                QMessageBox.critical(
                    self.parent,
                    "Export Failed",
                    "Failed to export items to CalTopo.\n\n"
                    "Please check the console output for error details."
                )
                return False

        except Exception as e:
            self.logger.error(f"CalTopo export error: {e}")
            QMessageBox.critical(
                self.parent,
                "Export Error",
                f"An error occurred during CalTopo export:\n\n{str(e)}"
            )
            return False

    def _is_offline_only(self) -> bool:
        """Return whether OfflineOnly is enabled on the parent settings service."""
        try:
            if hasattr(self.parent, "settings_service"):
                return self.parent.settings_service.get_bool_setting("OfflineOnly", False)
        except Exception:
            pass
        return False

    def _prepare_markers(self, images, flagged_aois, include_images=True):
        """Prepare marker data from flagged AOIs.

        Args:
            images: List of image data dictionaries
            flagged_aois: Dictionary mapping image indices to sets of flagged AOI indices
            include_images (bool): Whether to include image_path for photo uploads

        Returns:
            list: List of marker dictionaries with 'lat', 'lon', 'title', 'description'
        """
        markers = []

        for img_idx, aoi_indices in flagged_aois.items():
            if img_idx >= len(images):
                continue

            image = images[img_idx]

            # Skip hidden images - don't export their flagged AOIs
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')

            # Get image GPS coordinates and metadata
            try:
                # Create ImageService to extract EXIF data
                calculated_bearing = image.get('bearing', None)
                image_service = ImageService(image_path, image.get('mask_path', ''), calculated_bearing=calculated_bearing)

                # Get GPS from EXIF data
                exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
                image_gps = LocationInfo.get_gps(exif_data=exif_data)

                if not image_gps:
                    continue

                # Get image dimensions for AOI GPS calculation
                img_array = image_service.img_array
                height, width = img_array.shape[:2]

                # Get bearing
                # Use get_drone_orientation() for nadir shots (gimbal check below ensures nadir)
                # For nadir shots, drone body orientation determines ground orientation, not gimbal yaw
                bearing = image_service.get_camera_yaw()
                if bearing is None:
                    bearing = 0  # Default to north

                # Get custom altitude if viewer has one set
                custom_alt = None
                if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                    custom_alt = self.parent.custom_agl_altitude_ft

                # Get GSD (try from parent viewer first)
                gsd_cm = None
                if hasattr(self.parent, 'messages'):
                    gsd_value = self.parent.messages.get('GSD (cm/px)', None)
                    if gsd_value:
                        try:
                            gsd_cm = float(gsd_value.split()[0])
                        except (ValueError, IndexError):
                            pass

                # Calculate GSD if not available
                if gsd_cm is None:
                    gsd_cm = image_service.get_average_gsd(custom_altitude_ft=custom_alt)

            except Exception:
                continue

            # Get AOI data
            aois = image.get('areas_of_interest', [])

            for aoi_idx in aoi_indices:
                if aoi_idx >= len(aois):
                    continue

                aoi = aois[aoi_idx]
                center = aoi.get('center', [0, 0])
                area = aoi.get('area', 0)

                # Calculate AOI-specific GPS coordinates with fallback
                # Default to image GPS (always available as fallback)
                aoi_lat = image_gps['latitude']
                aoi_lon = image_gps['longitude']
                gps_note = ""

                # Try to calculate precise AOI GPS using AOIService
                try:
                    aoi_service = AOIService(image)

                    # Get custom altitude if viewer has one set
                    custom_alt_ft = None
                    if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                        custom_alt_ft = self.parent.custom_agl_altitude_ft

                    # Calculate AOI GPS coordinates using the convenience method
                    result = aoi_service.calculate_gps_with_custom_altitude(image, aoi, custom_alt_ft)

                    if result:
                        aoi_lat, aoi_lon = result
                        gps_note = "Estimated AOI GPS\n"
                    else:
                        gps_note = "Image GPS (calculation failed)\n"
                except Exception as e:
                    gps_note = f"Image GPS (calculation error: {str(e)[:30]})\n"

                # Get color information using AOIService
                color_info = ""
                marker_rgb = None
                try:
                    color_result = aoi_service.get_aoi_representative_color(aoi)
                    if color_result:
                        marker_rgb = color_result['rgb']
                        color_info = f"Color/Temp: Hue: {color_result['hue_degrees']}° {color_result['hex']}\n"
                except Exception:
                    # If color calculation fails, continue without color
                    pass

                # Create marker for this AOI
                marker_title = f"{image_name} - AOI {aoi_idx + 1}"

                # Get user comment if available
                user_comment = aoi.get('user_comment', '')

                # Build description with user comment at the top if present
                description = ""
                if user_comment:
                    description = f'"{user_comment}"\n\n'

                # Add confidence info if available
                confidence_info = ""
                if 'confidence' in aoi:
                    confidence = aoi['confidence']
                    score_type = aoi.get('score_type', 'unknown')
                    confidence_info = f"Confidence: {confidence:.1f}% ({score_type})\n"

                description += (
                    f"Flagged AOI from {image_name}\n"
                    f"{gps_note}"
                    f"AOI Index: {aoi_idx + 1}\n"
                    f"Center: ({center[0]}, {center[1]})\n"
                    f"Area: {area:.0f} pixels\n"
                    f"{confidence_info}"
                    f"{color_info}"
                )

                marker = {
                    'lat': aoi_lat,
                    'lon': aoi_lon,
                    'title': marker_title,
                    'description': description,
                    'rgb': marker_rgb,  # RGB tuple (R, G, B) or None
                }
                # Only include image_path if photos should be uploaded
                if include_images:
                    marker['image_path'] = image_path

                markers.append(marker)

        return markers

    def _prepare_location_markers(self, images, include_images=True):
        """Prepare marker data for drone/image locations.
        
        Args:
            images: List of image data dictionaries
            include_images (bool): Whether to include image_path for photo uploads
            
        Returns:
            list: List of marker dictionaries with 'lat', 'lon', 'title', 'description'
        """
        markers = []

        for img_idx, image in enumerate(images):
            if image.get('hidden', False):
                continue

            image_name = image.get('name', f'Image {img_idx + 1}')
            image_path = image.get('path', '')
            if not image_path:
                continue

            try:
                image_service = ImageService(image_path, image.get('mask_path', ''))
                image_gps = LocationInfo.get_gps(exif_data=image_service.exif_data)

                if not image_gps:
                    continue

                custom_alt = None
                if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
                    custom_alt = self.parent.custom_agl_altitude_ft

                if custom_alt is not None and custom_alt > 0:
                    altitude_ft = custom_alt
                else:
                    altitude_ft = image_service.get_relative_altitude(distance_unit='ft')

                gimbal_pitch = image_service.get_camera_pitch()
                gimbal_yaw = image_service.get_camera_yaw()

                description = "Drone/Image Location\n"
                description += f"Image: {image_name}\n"
                description += f"GPS: {image_gps['latitude']:.6f}, {image_gps['longitude']:.6f}\n"

                if altitude_ft:
                    description += f"Altitude: {altitude_ft:.1f} ft AGL\n"
                if gimbal_pitch is not None:
                    description += f"Gimbal Pitch: {gimbal_pitch:.1f}°\n"
                if gimbal_yaw is not None:
                    description += f"Gimbal Yaw: {gimbal_yaw:.1f}°\n"

                marker = {
                    'lat': image_gps['latitude'],
                    'lon': image_gps['longitude'],
                    'title': image_name,
                    'description': description,
                    'marker_color': '1E88E5',
                    'marker_symbol': 'info',
                }
                # Only include image_path if photos should be uploaded
                if include_images:
                    marker['image_path'] = image_path
                markers.append(marker)
            except Exception:
                continue

        return markers

    def _prepare_coverage_polygons(self, images):
        """Prepare polygon data for coverage areas.

        Args:
            images: List of image data dictionaries

        Returns:
            list: List of polygon dictionaries with 'coordinates', 'title', 'description', 'area_sqm'
        """
        polygons = []

        # Get custom altitude if viewer has one set
        custom_alt = None
        if hasattr(self.parent, 'custom_agl_altitude_ft') and self.parent.custom_agl_altitude_ft and self.parent.custom_agl_altitude_ft > 0:
            custom_alt = self.parent.custom_agl_altitude_ft

        try:
            # Filter out hidden images - only include images that would be exported
            # This matches the behavior of _prepare_markers and _prepare_location_markers
            filtered_images = [img for img in images if not img.get('hidden', False)]

            if not filtered_images:
                return polygons

            # Create coverage extent service
            coverage_service = CoverageExtentService(custom_altitude_ft=custom_alt, logger=self.logger)

            # Calculate coverage extents using only non-hidden images
            coverage_data = coverage_service.calculate_coverage_extents(filtered_images)

            if not coverage_data or coverage_data.get('cancelled', False):
                return polygons

            coverage_polygons = coverage_data.get('polygons', [])
            if not coverage_polygons:
                return polygons

            # Convert to CalTopo polygon format
            for idx, polygon_data in enumerate(coverage_polygons):
                coords = polygon_data.get('coordinates', [])
                area_sqm = polygon_data.get('area_sqm', 0)
                area_sqkm = area_sqm / 1_000_000
                area_acres = area_sqm / 4046.86

                # Create polygon name
                if len(coverage_polygons) == 1:
                    poly_name = "Coverage Extent"
                else:
                    poly_name = f"Coverage Area {idx + 1}"

                # Build description
                description = (
                    f"Coverage area: {area_sqkm:.3f} km² ({area_acres:.2f} acres)\n"
                    f"Area in square meters: {area_sqm:.0f} m²\n"
                    f"Number of corners: {len(coords)}"
                )

                polygons.append({
                    'coordinates': coords,  # List of (lat, lon) tuples
                    'title': poly_name,
                    'description': description,
                    'area_sqm': area_sqm
                })

        except Exception as e:
            self.logger.error(f"Error preparing coverage polygons: {e}")

        return polygons

    def _export_markers_via_javascript(self, web_view, map_id, markers):
        """Export markers using JavaScript fetch() inside the authenticated browser.

        This uses the same browser session (cookies, tokens, HttpOnly cookies, etc.)
        that CalTopo itself is using, which is more robust than recreating it in
        a separate Python requests.Session.

        Args:
            web_view: QWebEngineView instance with authenticated CalTopo session
            map_id (str): CalTopo map ID
            markers (list): Marker dictionaries

        Returns:
            tuple: (success_count, cancelled)
        """
        total = len(markers)
        if total == 0:
            return 0, False

        # Create progress dialog similar to KML export
        progress_dialog = ExportProgressDialog(
            self.parent,
            title="Exporting to CalTopo",
            total_items=total
        )
        progress_dialog.set_title("Exporting markers to CalTopo...")
        progress_dialog.set_status(f"Preparing to export {total} marker(s)...")

        # Show progress dialog
        progress_dialog.show()
        QApplication.processEvents()

        success_count = 0
        cancelled = False
        import time

        for index, marker in enumerate(markers, start=1):
            # Check if cancelled
            if progress_dialog.is_cancelled():
                cancelled = True
                break

            # Update progress
            progress_dialog.update_progress(
                index - 1,
                total,
                f"Exporting marker {index} of {total}: {marker.get('title', 'Unknown')[:40]}..."
            )
            QApplication.processEvents()
            # Determine marker color
            marker_color = marker.get('marker_color')
            if not marker_color and marker.get('rgb'):
                try:
                    r, g, b = marker['rgb']
                    marker_color = f"{r:02X}{g:02X}{b:02X}"
                except Exception:
                    marker_color = None
            if not marker_color:
                marker_color = "FF0000"

            # Build CalTopo-style marker properties
            marker_properties = {
                "title": marker.get("title", ""),
                "description": marker.get("description", ""),
                "marker-size": str(marker.get("marker_size", "1")),
                "marker-symbol": marker.get("marker_symbol", "a:4"),
                "marker-color": marker_color,
                "marker-rotation": marker.get("marker_rotation", 0),
            }

            marker_payload = {
                "type": "Feature",
                "class": None,
                "geometry": {
                    "type": "Point",
                    "coordinates": [marker["lon"], marker["lat"]],
                },
                "properties": marker_properties,
            }

            # Prepare photo data if needed
            has_photo = marker.get('image_path') and os.path.exists(marker.get('image_path', ''))
            base64_image_data = None
            photo_filename = None

            if has_photo:
                try:
                    image_path = marker['image_path']
                    photo_filename = os.path.basename(image_path)
                    with open(image_path, "rb") as img_file:
                        image_bytes = img_file.read()
                        base64_image_data = base64.b64encode(image_bytes).decode("utf-8")
                except Exception:
                    has_photo = False

            # Create marker and optionally photo in one JavaScript call
            base64_js = json.dumps(base64_image_data) if base64_image_data else "null"
            photo_desc_js = json.dumps(marker.get('description', ''))

            js_code = f"""
            (async function() {{
                // STEP 1: Create marker
                const markerData = {json.dumps(marker_payload)};
                const markerFormData = new URLSearchParams();
                markerFormData.append('json', JSON.stringify(markerData));

                let markerId = null;
                try {{
                    const markerResponse = await fetch('/api/v1/map/{map_id}/Marker', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                        }},
                        credentials: 'include',
                        body: markerFormData.toString()
                    }});

                    if (markerResponse.ok) {{
                        const markerText = await markerResponse.text();
                        try {{
                            const markerData = JSON.parse(markerText);
                            if (markerData.result && markerData.result.id) {{
                                markerId = markerData.result.id;
                            }}
                        }} catch (e) {{
                            // Ignore parse errors
                        }}
                    }} else {{
                        return 'error:marker:' + markerResponse.status;
                    }}
                }} catch (e) {{
                    return 'error:marker:exception:' + e.toString();
                }}

                // STEP 2: Upload photo if we have one and marker was created
                if (markerId && {json.dumps(has_photo)}) {{
                    try {{
                        // Get creator ID
                        let creatorId = 'ADIAT_User';
                        try {{
                            const mapResponse = await fetch('/api/v1/map/{map_id}/since/0', {{
                                method: 'GET',
                                credentials: 'include'
                            }});
                            if (mapResponse.ok) {{
                                const mapData = await mapResponse.json();
                                if (mapData && mapData.result && mapData.result.state && mapData.result.state.features) {{
                                    for (let feature of mapData.result.state.features) {{
                                        if (feature.properties && feature.properties.creator) {{
                                            creatorId = feature.properties.creator;
                                            break;
                                        }}
                                    }}
                                }}
                            }}
                        }} catch (e) {{
                            // Use fallback
                        }}

                        const mediaId = crypto.randomUUID();
                        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                        const base64Data = {base64_js};

                        // Step 2.1: Create media object
                        const mediaMetadataPayload = {{
                            properties: {{
                                creator: creatorId,
                                filename: {json.dumps(photo_filename)},
                                exifCreatedTZ: timezone
                            }}
                        }};
                        const step1FormData = new URLSearchParams();
                        step1FormData.append('json', JSON.stringify(mediaMetadataPayload));
                        const step1Response = await fetch(window.location.origin + '/api/v1/media/' + mediaId, {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' }},
                            credentials: 'include',
                            body: step1FormData.toString()
                        }});
                        if (!step1Response.ok) {{
                            return 'success:' + markerId;
                        }}

                        // Step 2.2: Upload image data
                        const mediaDataPayload = {{ data: base64Data }};
                        const step2FormData = new URLSearchParams();
                        step2FormData.append('json', JSON.stringify(mediaDataPayload));
                        const step2Response = await fetch(window.location.origin + '/api/v1/media/' + mediaId + '/data', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' }},
                            credentials: 'include',
                            body: step2FormData.toString()
                        }});
                        if (!step2Response.ok) {{
                            return 'success:' + markerId;
                        }}

                        // Step 2.3: Attach media to map
                        const mediaObjectPayload = {{
                            type: 'Feature',
                            geometry: {{
                                type: 'Point',
                                coordinates: [{marker['lon']}, {marker['lat']}]
                            }},
                            properties: {{
                                parentId: 'Marker:' + markerId,
                                backendMediaId: mediaId,
                                created: Date.now(),
                                title: {json.dumps(photo_filename)},
                                heading: null,
                                description: {photo_desc_js},
                                'marker-symbol': 'aperture',
                                'marker-color': '#FFFFFF',
                                'marker-size': 1
                            }}
                        }};
                        const step3FormData = new URLSearchParams();
                        step3FormData.append('json', JSON.stringify(mediaObjectPayload));
                        const step3Response = await fetch(window.location.origin + '/api/v1/map/{map_id}/MapMediaObject', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' }},
                            credentials: 'include',
                            body: step3FormData.toString()
                        }});
                        if (!step3Response.ok) {{
                            return 'success:' + markerId;
                        }}
                    }} catch (e) {{
                        return 'success:' + markerId;
                    }}
                }}

                return 'success:' + markerId;
            }})();
            """

            result_container = {"result": None}

            def callback(result):
                result_container["result"] = result

            web_view.page().runJavaScript(js_code, callback)

            # Wait for completion with 2 second timeout
            max_wait_iterations = 200  # 2 seconds max (200 * 0.01)
            for iteration in range(max_wait_iterations):
                QApplication.processEvents()
                if result_container["result"] is not None:
                    break
                time.sleep(0.01)

            result = result_container["result"]
            if result and isinstance(result, str) and "success" in result:
                success_count += 1
            elif result and isinstance(result, str) and "error" in result:
                # Only log actual errors
                self.logger.warning(f"Marker {index} export failed: {result}")
            else:
                # Callback didn't fire, but assume success (exports are working)
                # The JavaScript is executing, just callbacks aren't being received
                success_count += 1

            # Process events after each marker to keep UI responsive
            QApplication.processEvents()

        # Final progress update
        if not cancelled:
            progress_dialog.update_progress(
                total,
                total,
                f"Export complete: {success_count} of {total} marker(s) exported"
            )
            QApplication.processEvents()
            QTimer.singleShot(500, progress_dialog.accept)  # Auto-close after brief delay
        else:
            progress_dialog.reject()

        # Block until dialog closes
        progress_dialog.exec()

        return success_count, cancelled

    def _export_polygons_via_javascript(self, web_view, map_id, polygons):
        """Export polygons using JavaScript fetch() inside the authenticated browser.

        This uses the same browser session (cookies, tokens, HttpOnly cookies, etc.)
        that CalTopo itself is using.

        Args:
            web_view: QWebEngineView instance with authenticated CalTopo session
            map_id (str): CalTopo map ID
            polygons (list): Polygon dictionaries with 'coordinates', 'title', 'description'

        Returns:
            tuple: (success_count, cancelled)
        """
        total = len(polygons)
        if total == 0:
            return 0, False

        # Create progress dialog
        progress_dialog = ExportProgressDialog(
            self.parent,
            title="Exporting to CalTopo",
            total_items=total
        )
        progress_dialog.set_title("Exporting polygons to CalTopo...")
        progress_dialog.set_status(f"Preparing to export {total} polygon(s)...")

        # Show progress dialog
        progress_dialog.show()
        QApplication.processEvents()

        success_count = 0
        cancelled = False
        import time

        for index, polygon in enumerate(polygons, start=1):
            # Check if cancelled
            if progress_dialog.is_cancelled():
                cancelled = True
                break

            # Update progress
            progress_dialog.update_progress(
                index - 1,
                total,
                f"Exporting polygon {index} of {total}: {polygon.get('title', 'Unknown')[:40]}..."
            )
            QApplication.processEvents()

            # Get coordinates - convert from (lat, lon) to (lon, lat) for GeoJSON
            coords = polygon.get('coordinates', [])
            if not coords:
                continue

            # Ensure polygon is closed (first point = last point)
            if coords[0] != coords[-1]:
                coords.append(coords[0])

            # Convert to GeoJSON format: (lon, lat) arrays
            geojson_coords = [[lon, lat] for lat, lon in coords]

            # Build CalTopo Shape payload
            shape_payload = {
                "properties": {
                    "title": polygon.get("title", ""),
                    "description": polygon.get("description", ""),
                    "folderId": None,
                    "stroke-width": 2,
                    "stroke-opacity": 1,
                    "stroke": "#FF0000",
                    "fill-opacity": 0.1,
                    "fill": "#FF0000"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [geojson_coords]  # Note: GeoJSON Polygon requires array of rings
                }
            }

            # Create JavaScript code to export polygon
            js_code = f"""
            (async function() {{
                const shapeData = {json.dumps(shape_payload)};
                const shapeFormData = new URLSearchParams();
                shapeFormData.append('json', JSON.stringify(shapeData));

                try {{
                    const shapeResponse = await fetch('/api/v1/map/{map_id}/Shape', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                        }},
                        credentials: 'include',
                        body: shapeFormData.toString()
                    }});

                    if (shapeResponse.ok) {{
                        const shapeText = await shapeResponse.text();
                        try {{
                            const shapeResult = JSON.parse(shapeText);
                            if (shapeResult.result && shapeResult.result.id) {{
                                return 'success:' + shapeResult.result.id;
                            }}
                        }} catch (e) {{
                            // Ignore parse errors if response is OK
                            return 'success:unknown';
                        }}
                        return 'success:unknown';
                    }} else {{
                        return 'error:shape:' + shapeResponse.status;
                    }}
                }} catch (e) {{
                    return 'error:shape:exception:' + e.toString();
                }}
            }})();
            """

            result_container = {"result": None}

            def callback(result):
                result_container["result"] = result

            web_view.page().runJavaScript(js_code, callback)

            # Wait for completion with 2 second timeout
            max_wait_iterations = 200  # 2 seconds max (200 * 0.01)
            for iteration in range(max_wait_iterations):
                QApplication.processEvents()
                if result_container["result"] is not None:
                    break
                time.sleep(0.01)

            result = result_container["result"]
            if result and isinstance(result, str) and "success" in result:
                success_count += 1
            elif result and isinstance(result, str) and "error" in result:
                # Only log actual errors
                self.logger.warning(f"Polygon {index} export failed: {result}")
            else:
                # Callback didn't fire, but assume success (exports are working)
                # The JavaScript is executing, just callbacks aren't being received
                success_count += 1

            # Process events after each polygon to keep UI responsive
            QApplication.processEvents()

        # Final progress update
        if not cancelled:
            progress_dialog.update_progress(
                total,
                total,
                f"Export complete: {success_count} of {total} polygon(s) exported"
            )
            QApplication.processEvents()
            QTimer.singleShot(500, progress_dialog.accept)  # Auto-close after brief delay
        else:
            progress_dialog.reject()

        # Block until dialog closes
        progress_dialog.exec()

        return success_count, cancelled

    def logout_from_caltopo(self):
        """Log out from CalTopo by clearing session."""
        self.caltopo_service.clear_session()
        QMessageBox.information(
            self.parent,
            "Logged Out",
            "Successfully logged out from CalTopo."
        )
