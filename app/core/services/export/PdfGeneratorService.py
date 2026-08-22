from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QBuffer, QUrl, QEventLoop
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

import os
import cv2
import numpy as np
from io import BytesIO
from datetime import datetime
import re
import math
import colorsys
import requests
from pathlib import Path
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from helpers.LocationInfo import LocationInfo
from helpers.ColorUtils import ColorUtils
from core.services.LoggerService import LoggerService
from core.services.image.ImageService import ImageService
from core.services.image.AOIService import AOIService
from core.services.image.AOICompositeService import AOICompositeService
from helpers.MetaDataHelper import MetaDataHelper

import traceback


class PDFDocTemplate(BaseDocTemplate):
    """Custom document template with TOC support."""

    def __init__(self, filename, organization="[ORGANIZATION]", progress_callback=None, **kwargs):
        """
        Initialize a custom document template.

        Args:
            filename (str): The file path for the generated PDF document.
            organization (str): Organization name for the footer
            progress_callback: Optional callback function(current, total, message) for progress updates
            **kwargs: Additional arguments for the BaseDocTemplate class.
        """
        self.allowSplitting = 0
        self.organization = organization
        self.progress_callback = progress_callback
        self.total_flowables = 0
        self.current_flowable = 0
        self.build_pass = 0  # Track which pass we're on (0 = TOC collection, 1 = actual build)
        BaseDocTemplate.__init__(self, filename, **kwargs)

        # Letter dimensions in cm
        page_width, page_height = letter  # (21.59 cm, 27.94 cm)
        min_margin = 0.635 * cm

        # Frame dimensions - leave space at bottom for footer
        footer_space = 1.5 * cm
        frame_width = page_width - (2 * min_margin)
        frame_height = page_height - (2 * min_margin) - footer_space
        x_margin = min_margin
        y_margin = min_margin + footer_space

        template = PageTemplate('normal', [Frame(x_margin, y_margin, frame_width, frame_height, id='F1')],
                                onPage=self.add_footer)
        self.addPageTemplates(template)

    def add_footer(self, canvas, doc):
        """
        Add footer to each page.

        Args:
            canvas: The canvas object to draw on
            doc: The document object
        """
        canvas.saveState()
        page_width, page_height = letter

        # Draw footer text
        footer_text = f"CONFIDENTIAL | {self.organization} | Page {doc.page}"
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(page_width / 2, 0.5 * cm, footer_text)

        canvas.restoreState()

    def afterFlowable(self, flowable):
        """
        Register entries for the Table of Contents and track progress.
        Optimized to avoid unnecessary string operations for non-Paragraph flowables.

        Args:
            flowable (Flowable): A flowable object, such as a Paragraph.
        """
        # Track progress during build
        # Note: multiBuild processes the document twice (TOC collection + actual build)
        # This is why there's a delay at 100% - it's actually building the PDF
        if self.progress_callback and hasattr(self, 'total_flowables') and self.total_flowables > 0:
            self.current_flowable += 1
            # Update progress: first pass (TOC collection) is ~50%, second pass (build) is 50-100%
            # Throttle updates to every 2% to reduce callback overhead
            update_interval = max(1, self.total_flowables // 50)
            if self.current_flowable % update_interval == 0:
                if self.build_pass == 0:
                    # First pass: 0-50%
                    progress = min(50, int((self.current_flowable / self.total_flowables) * 50))
                    self.progress_callback(
                        progress,
                        100,
                        f"Collecting table of contents... ({self.current_flowable}/{self.total_flowables})"
                    )
                else:
                    # Second pass: 50-100%
                    progress = 50 + min(50, int((self.current_flowable / self.total_flowables) * 50))
                    self.progress_callback(
                        progress,
                        100,
                        f"Building PDF pages... ({self.current_flowable}/{self.total_flowables})"
                    )

        # Early exit for non-Paragraph flowables (most common case)
        if flowable.__class__.__name__ != 'Paragraph':
            return

        # Only process Paragraphs with heading styles
        style = getattr(flowable, 'style', None)
        if not style or not hasattr(style, 'name'):
            return

        style_name = style.name
        if style_name not in ('Heading2', 'Heading3'):
            return

        text = flowable.getPlainText()
        label = text

        # Sanitize the key to use only alphanumerics, underscore and hyphen.
        # This will remove parentheses and other punctuation that may break ReportLab's parser.
        sanitized_key = re.sub(r"[^\w\-]", "", text).strip()

        if style_name == 'Heading2':
            key = f"h2-{sanitized_key}"
            self.canv.bookmarkPage(key)
            self.notify('TOCEntry', (0, label, self.page, key))
        elif style_name == 'Heading3':
            key = f"h3-{sanitized_key}"
            self.canv.bookmarkPage(key)
            self.notify('TOCEntry', (1, label, self.page, key))

    def build(self, flowables, filename=None, **buildKwds):
        """
        Override build to track which pass we're on and reset counters.
        """
        if self.build_pass == 0:
            # First pass: count total flowables for progress tracking
            self.total_flowables = len(flowables)
            self.current_flowable = 0
        else:
            # Second pass: reset counter
            self.current_flowable = 0

        # Call parent build with all keyword arguments properly forwarded
        result = BaseDocTemplate.build(self, flowables, filename=filename, **buildKwds)

        # Increment pass counter after build completes
        self.build_pass += 1

        return result


class PdfGeneratorService:
    """Service for generating PDF reports from analysis results."""

    def __init__(self, viewer, organization="", search_name="", images=None, include_images_without_flagged_aois=False, map_tile_source="map"):
        """
        Initialize the PDF generator service.

        Args:
            viewer: Reference to the viewer instance for accessing necessary data and methods.
            organization: Organization name for the report
            search_name: Search/mission name for the report
            images: List of images to include in the PDF (if None, will use viewer.images)
            include_images_without_flagged_aois: Whether to include images without flagged AOIs
            map_tile_source: Tile source for overview map ('map' or 'satellite')
        """

        self.logger = LoggerService()
        self.viewer = viewer
        self.organization = organization if organization else "[ORGANIZATION]"
        self.search_name = search_name if search_name else "Analysis"
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.map_tile_source = map_tile_source if map_tile_source in ("map", "satellite") else "map"
        self.images = images  # Store the images to use for PDF generation
        self.story = []
        self.doc = None
        self._initialize_styles()

        # Composite service builds the multi-zoom AOI images; it caches rotated
        # images per path, cleared after each image to prevent memory buildup
        self._composite_service = AOICompositeService(logger=self.logger)
        self._image_service_cache = {}  # key: image_path -> ImageService instance
        self._temp_files = []  # Track temporary files for cleanup

    def generate_report(self, output_path, progress_callback=None, cancel_check=None):
        """
        Generate a PDF report of the analysis results.

        Args:
            output_path (str): The file path where the PDF should be saved.
            progress_callback: Optional callback function(current, total, message) for progress updates
            cancel_check: Optional function that returns True if operation should be cancelled
        """
        try:
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"Output directory {output_dir} is not writable")

            # Validate images before starting
            for img in (self.images or self.viewer.images):
                if not os.path.exists(img['path']):
                    raise FileNotFoundError(f"Image not found: {img['path']}")

            self.doc = PDFDocTemplate(
                output_path,
                organization=self.organization,
                pagesize=letter,
                progress_callback=progress_callback
            )

            # Add title with date/time and placeholder logo
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Load the logo using QPixmap
            logo_pixmap = QPixmap(":/ADIAT_Full.png")  # Use resource file path

            # Save the QPixmap to a QBuffer
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            logo_pixmap.save(buffer, "PNG")  # Save the pixmap as PNG in the buffer
            logo_bytes = buffer.data()  # Get the binary data from the buffer

            # Convert the QBuffer data to BytesIO for ReportLab
            logo_io = BytesIO(logo_bytes)
            logo = Image(logo_io, width=2 * inch, height=2 * inch)
            logo.hAlign = 'CENTER'
            self.story.append(logo)
            self.story.append(Spacer(1, 12))

            self.story.append(Paragraph(f"{self.organization} - {self.search_name}<br/>{current_datetime}", self.h1))
            self.story.append(Spacer(1, 20))

            # Add overview map
            map_path = self._generate_overview_map()
            if map_path:
                map_img = Image(map_path, width=7 * inch, height=5.25 * inch)
                map_img.hAlign = 'CENTER'
                self.story.append(map_img)
                self.story.append(Spacer(1, 20))

            # Add page break after title page content
            self.story.append(PageBreak())

            # Add algorithm settings section
            self._add_algorithm_settings()
            self.story.append(Spacer(1, 20))

            # Add Images section header
            self.story.append(Paragraph(f"Images ({len(self.images)})", self.h2))
            self.story.append(Spacer(1, 10))

            # Add image details
            self._add_image_details(progress_callback=progress_callback, cancel_check=cancel_check)

            # Check for cancellation after image details are added
            if cancel_check and cancel_check():
                # self.logger.info("PDF generation cancelled by user")
                return  # Exit early - finally block will clean up temp files

            # Update progress to show finalization
            if progress_callback:
                # Cache the count to avoid recalculating
                total_flagged_aois = self._count_flagged_aois()
                progress_callback(total_flagged_aois, total_flagged_aois, "Preparing Table of Contents...")

            # Add TOC after all content is generated
            toc = self._create_toc()

            # Find the index of the first PageBreak (which marks the end of the title page)
            # Optimize: use next() with generator for early exit
            first_page_break_idx = next(
                (i for i, flowable in enumerate(self.story) if isinstance(flowable, PageBreak)),
                -1
            )

            # Optimize list insertion: use list slicing instead of two separate inserts
            # This is more efficient than two O(n) insert operations
            if first_page_break_idx != -1:
                # Insert TOC and PageBreak in one operation using list slicing
                insert_pos = first_page_break_idx + 1
                self.story[insert_pos:insert_pos] = [toc, PageBreak()]
            else:
                # Fallback if no PageBreak was found (shouldn't happen with current logic)
                self.logger.error("No PageBreak found after title page content. Inserting TOC at beginning.")
                self.story[0:0] = [toc, PageBreak()]

            # Set total flowables for progress tracking
            self.doc.total_flowables = len(self.story)

            # Update progress before the potentially slow multiBuild operation
            if progress_callback:
                progress_callback(0, 100, "Starting PDF build...")

            # Build the PDF
            # Note: multiBuild is necessary for TOC as it processes the document twice
            # (once to collect TOC entries, once to build with page numbers)
            # Progress is tracked in PDFDocTemplate.handle_flowable()
            self.doc.multiBuild(self.story)

            # Final progress update
            if progress_callback:
                progress_callback(100, 100, "PDF generation complete!")

        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"PDF generation failed: {str(e)}")
            raise
        finally:
            # Clean up temporary files
            self._cleanup_temp_files()
            # Clear caches to free memory
            self._clear_caches()

    def _create_toc(self):
        """
        Create and configure the Table of Contents (TOC).

        Returns:
            TableOfContents: A configured Table of Contents object.
        """
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                fontSize=14,
                name='TOCHeading2',
                leftIndent=10,  # Ensure no indentation for Heading2
                firstLineIndent=-20,
                spaceBefore=5,
                leading=16
            ),
            ParagraphStyle(
                fontSize=12,  # Reduced size for Heading3 (image titles)
                name='TOCHeading3',
                leftIndent=20,
                firstLineIndent=0,
                spaceBefore=0,
                leading=14
            ),
        ]
        return toc

    def _add_algorithm_settings(self):
        """
        Add the algorithm settings section to the report.
        """
        self.story.append(Paragraph("Algorithm Settings", self.h2))
        settings, algorithm = self.viewer.xml_service.get_settings()
        # self.story.append(Paragraph(f"Algorithm: {algorithm}", self.styles['Normal']))

        # Process settings with color squares
        for key, value in settings.items():
            rgb_value = value if isinstance(value, tuple) else ColorUtils.parse_rgb_string(str(value))
            if rgb_value and len(rgb_value) == 3:
                r, g, b = rgb_value
                color_hex = f"#{r:02x}{g:02x}{b:02x}"
                self.story.append(Paragraph(
                    f"{key}: {value} <font color='{color_hex}'>■</font>",
                    self.styles['Normal']
                ))
            elif isinstance(value, dict):
                nested_values = []
                for k, v in value.items():
                    rgb_value = ColorUtils.parse_rgb_string(str(v))
                    if rgb_value and len(rgb_value) == 3:
                        r, g, b = rgb_value
                        color_hex = f"#{r:02x}{g:02x}{b:02x}"
                        nested_values.append(f"{k}: {v} <font color='{color_hex}'>■</font>")
                    else:
                        nested_values.append(f"{k}: {v}")
                self.story.append(Paragraph(f"{key}: {{{', '.join(nested_values)}}}", self.styles['Normal']))
            else:
                self.story.append(Paragraph(f"{key}: {value}", self.styles['Normal']))

        self.story.append(PageBreak())

    def _count_flagged_aois(self):
        """Count total AOIs to process across all non-hidden images.

        Returns:
            int: Total number of AOIs to process
        """
        total_aois = 0
        for img in (self.images):
            if not img.get('hidden', False):
                # Count AOIs (already filtered by controller)
                total_aois += len(img.get('areas_of_interest', []))
        return total_aois

    @staticmethod
    def _report_value(value, unit):
        """Format a metadata value for the report, or "N/A" when there isn't one.

        A report that prints "Noneft" or a substituted 0 is worse than one that
        says nothing: the first is noise and the second is indistinguishable
        from a real reading. Video-derived imagery carries no camera
        intrinsics, so several of these are legitimately absent.

        Args:
            value: The measurement, or None when the image does not carry it.
            unit (str): Unit suffix to append when there is a value.

        Returns:
            str: "<value><unit>", or "N/A".
        """
        if value is None or value == "":
            return "N/A"
        return f"{value}{unit}"

    def _add_image_details(self, progress_callback=None, cancel_check=None):
        """
        Add detailed AOI pages to the report.
        Each flagged AOI gets its own page with zoomed views and metadata.

        Args:
            progress_callback: Optional callback function(current, total, message) for progress updates
            cancel_check: Optional function that returns True if operation should be cancelled
        """
        identifier_color = self.viewer.settings.get('identifier_color', (255, 255, 0))

        # Count total flagged AOIs for progress tracking
        total_flagged_aois = self._count_flagged_aois()

        current_aoi_count = 0

        for img in (self.images):
            # Check for cancellation
            if cancel_check and cancel_check():
                # self.logger.info("PDF generation cancelled by user")
                return
            if img.get('hidden', False):
                continue

            # Get AOIs for this image (already filtered by controller)
            flagged_aois = img.get('areas_of_interest', [])

            # Skip if no AOIs (shouldn't happen with controller filtering, but safety check)
            if not flagged_aois:
                continue

            # Get image path (use 'path' field which viewer uses for display)
            image_path = img.get('path', '')
            mask_path = img.get('mask_path', '')

            # Get original image path for GPS metadata
            original_path = img.get('original_path', image_path) if 'original_path' in img else image_path

            # Reuse ImageService if already created (optimization)
            # Use original_path to ensure GPS/EXIF data is available
            cache_key = original_path
            if cache_key not in self._image_service_cache:
                # Use original_path instead of image_path to ensure GPS metadata is available
                image_service = ImageService(original_path, mask_path)
                self._image_service_cache[cache_key] = image_service
            else:
                image_service = self._image_service_cache[cache_key]

            # Get img_array for color calculations (matches viewer's current_image_array)
            display_img_array = image_service.img_array  # Already in RGB format

            # Reuse image array from ImageService instead of reloading (optimization)
            # Convert RGB to BGR for cv2 operations
            img_array = cv2.cvtColor(display_img_array, cv2.COLOR_RGB2BGR)

            # Get image metadata
            bearing = image_service.get_camera_yaw() or 0

            # Get GPS and other metadata from original image
            # ImageService now uses original_path, so GPS should be available
            # Anything the image does not carry reads "N/A". Formatting a
            # missing value with its unit produced "AGL: Noneft" and
            # "Nonecm/px" in the report, and a missing yaw fell back to 0,
            # which reads as a real due-north heading rather than an absence.
            position_str = image_service.get_position(self.viewer.position_format) or "N/A"
            agl_str = self._report_value(
                image_service.get_relative_altitude(self.viewer.distance_unit),
                self.viewer.distance_unit
            )
            orientation_str = self._report_value(image_service.get_camera_yaw(), "°")
            gsd_str = self._report_value(image_service.get_average_gsd(), "cm/px")

            # Add image header once per image (not per AOI)
            self.story.append(Paragraph(img['name'], self.h3))

            # Add metadata as separate paragraph
            metadata_text = f"GPS Coordinates: {position_str} (camera's position, not ground location) | "
            metadata_text += f"AGL: {agl_str} | Drone Orientation: {orientation_str} | Estimated Average GSD: {gsd_str}"
            self.story.append(Paragraph(metadata_text, self.styles['Normal']))
            self.story.append(Spacer(1, 10))

            # Process each flagged AOI
            for aoi_idx, aoi in enumerate(flagged_aois):
                # Update progress
                current_aoi_count += 1
                if progress_callback:
                    progress_callback(
                        current_aoi_count,
                        total_flagged_aois,
                        f"Processing {img['name']} - AOI {aoi_idx + 1} of {len(flagged_aois)}..."
                    )

                # Check for cancellation before processing each AOI
                if cancel_check and cancel_check():
                    # self.logger.info("PDF generation cancelled by user")
                    return

                # Create the multi-zoom composite (full rotated image + 3x/6x insets
                # with connector lines), cached per image path
                composite_img = self._composite_service.create_composite(
                    img_array, aoi, bearing, identifier_color, cache_key=original_path
                )

                if composite_img is not None:
                    # Use temporary file instead of BytesIO to reduce memory usage
                    # This is critical for large image sets on Mac
                    temp_file = self._save_image_to_temp_file(composite_img, quality=70)

                    # Use full page width
                    composite_img_obj = Image(temp_file, width=7.5 * inch, height=6 * inch)
                    composite_img_obj.hAlign = 'CENTER'
                    self.story.append(composite_img_obj)
                    self.story.append(Spacer(1, 10))

                    # Explicitly delete large numpy arrays to free memory immediately
                    del composite_img

                # Add additional metadata
                metadata_lines = []

                # Add AOI GPS coordinates if available
                aoi_gps = self._calculate_aoi_gps(img, aoi)
                if aoi_gps:
                    lat, lon = aoi_gps['latitude'], aoi_gps['longitude']
                    aoi_gps_str = f"{lat:.6f}, {lon:.6f}"

                    # Create Google Maps link
                    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                    maps_link = f'<a href="{maps_url}" color="blue"><u>(Open in Google Maps)</u></a>'
                    placemark_name = f"{img['name']} - AOI {aoi_idx + 1}"
                    geo_url = f"geo:{lat},{lon},u=20&({placemark_name})"
                    geo_link = f'<a href="{geo_url}" color="blue"><u>(Open in GPS)</u></a>'

                    metadata_lines.append(f"<b>Estimated AOI GPS Location:</b> {aoi_gps_str} {maps_link} {geo_link}")

                metadata_lines.append(f"<b>AOI Pixel Area:</b> {aoi.get('area', 0):.0f}")

                # Add confidence score if available
                if 'confidence' in aoi:
                    confidence = aoi['confidence']
                    score_type = aoi.get('score_type', 'unknown')
                    raw_score = aoi.get('raw_score', 0)
                    score_method = aoi.get('score_method', 'mean')
                    metadata_lines.append(
                        f"<b>Confidence Score:</b> {confidence:.1f}% "
                        f"({score_type}, raw: {raw_score:.3f} {score_method})"
                    )

                # Add average color info from displayed image (matching viewer behavior)
                avg_color_info = self._get_aoi_average_info(img, aoi)
                if avg_color_info:
                    metadata_lines.append(f"<b>Average Color:</b> {avg_color_info}")

                # Add user comment
                user_comment = aoi.get('user_comment', '')
                if user_comment:
                    metadata_lines.append(f"<b>Comment:</b> {user_comment}")

                # Add metadata as paragraph
                if metadata_lines:
                    metadata_text = "<br/>".join(metadata_lines)
                    self.story.append(Paragraph(metadata_text, self.styles['Normal']))

                # Page break between AOIs
                self.story.append(PageBreak())

            # Clear rotated image cache after processing all AOIs for this image
            # This prevents memory buildup when processing large image sets
            # Only clear entries for this specific image to preserve cache for other images
            self._composite_service.clear_cache_for(original_path)

            # Clear image arrays from memory after processing all AOIs for this image
            # This is critical for large image sets to prevent memory exhaustion
            del img_array
            del display_img_array

            # Clear image array from ImageService cache to free memory
            # Metadata (GPS, bearing, etc.) is already extracted, so we don't need the full image array anymore
            if cache_key in self._image_service_cache:
                image_service = self._image_service_cache[cache_key]
                if hasattr(image_service, 'img_array') and image_service.img_array is not None:
                    image_service.img_array = None

    def _initialize_styles(self):
        """Initialize paragraph styles for the document."""
        self.styles = getSampleStyleSheet()
        self.h1 = ParagraphStyle(
            name='Heading1',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=50,
            alignment=1  # Center align
        )
        self.h2 = ParagraphStyle(
            name='Heading2',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20
        )
        self.h3 = ParagraphStyle(
            name='Heading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            leftIndent=0,
            fontName="Helvetica",
            alignment=0
        )
        self.h4 = ParagraphStyle(
            name='Heading4',
            parent=self.styles['Heading4'],
            fontSize=12,
            leftIndent=0,
            fontName="Helvetica",
            alignment=0,
            spaceAfter=0
        )

    def _generate_overview_map(self):
        """
        Generate an overview map showing all images and flagged AOIs with map tile background.

        Returns:
            str: Path to temporary file containing the overview map image, or None if no GPS data
        """
        try:
            # Collect GPS data for ALL images (not just flagged)
            gps_locations = []
            identifier_color = self.viewer.settings.get('identifier_color', (255, 255, 0))

            for idx, img in enumerate(self.images):
                # Include hidden images in the map

                # Get GPS coords from original image path
                image_path = img.get('original_path', img['path']) if 'original_path' in img else img['path']
                exif_data = MetaDataHelper.get_exif_data_piexif(image_path)
                gps_coords = LocationInfo.get_gps(exif_data=exif_data)

                if not gps_coords:
                    continue

                # Check for flagged AOIs
                has_flagged = False
                flagged_aoi_coords = []
                if 'areas_of_interest' in img:
                    for aoi in img['areas_of_interest']:
                        if aoi.get('flagged', False):
                            has_flagged = True
                            # Calculate AOI GPS coordinates if possible
                            aoi_gps = self._calculate_aoi_gps(img, aoi)
                            if aoi_gps:
                                flagged_aoi_coords.append(aoi_gps)

                gps_locations.append({
                    'lat': gps_coords['latitude'],
                    'lon': gps_coords['longitude'],
                    'has_flagged': has_flagged,
                    'flagged_aois': flagged_aoi_coords,
                    'name': img.get('name', f'Image {idx}')
                })

            if not gps_locations:
                return None

            # Calculate bounds
            lats = [loc['lat'] for loc in gps_locations]
            lons = [loc['lon'] for loc in gps_locations]

            # Add flagged AOI coordinates to bounds
            for loc in gps_locations:
                for aoi in loc['flagged_aois']:
                    lats.append(aoi['latitude'])
                    lons.append(aoi['longitude'])

            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)

            # Add padding (10% of range)
            lat_range = max_lat - min_lat or 0.01
            lon_range = max_lon - min_lon or 0.01
            min_lat -= lat_range * 0.1
            max_lat += lat_range * 0.1
            min_lon -= lon_range * 0.1
            max_lon += lon_range * 0.1

            # Map image dimensions
            img_width, img_height = 2000, 1500

            # Download and composite map tiles as background
            map_img = self._download_map_tiles(min_lat, max_lat, min_lon, max_lon, img_width, img_height)

            def lat_lon_to_pixel(lat, lon):
                """Convert lat/lon to pixel coordinates."""
                x = int((lon - min_lon) / (max_lon - min_lon) * img_width)
                y = int((max_lat - lat) / (max_lat - min_lat) * img_height)
                return x, y

            # Draw connections between points (chronologically)
            for i in range(len(gps_locations) - 1):
                pt1 = lat_lon_to_pixel(gps_locations[i]['lat'], gps_locations[i]['lon'])
                pt2 = lat_lon_to_pixel(gps_locations[i + 1]['lat'], gps_locations[i + 1]['lon'])
                cv2.line(map_img, pt1, pt2, (255, 255, 255), 3)  # White line with border
                cv2.line(map_img, pt1, pt2, (150, 150, 150), 2)

            # Draw image locations
            for loc in gps_locations:
                pt = lat_lon_to_pixel(loc['lat'], loc['lon'])
                # Use different colors based on whether image has flagged AOIs
                if loc['has_flagged']:
                    cv2.circle(map_img, pt, 12, (0, 100, 255), -1)  # Orange for images with flagged AOIs
                    cv2.circle(map_img, pt, 14, (0, 0, 0), 2)  # Black outline
                else:
                    cv2.circle(map_img, pt, 8, (100, 100, 100), -1)  # Gray for images without flagged AOIs
                    cv2.circle(map_img, pt, 10, (255, 255, 255), 2)  # White outline

                # Draw flagged AOI markers
                for aoi in loc['flagged_aois']:
                    aoi_pt = lat_lon_to_pixel(aoi['latitude'], aoi['longitude'])
                    # Use identifier color for AOI markers
                    color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])  # RGB to BGR
                    cv2.circle(map_img, aoi_pt, 8, color_bgr, -1)
                    cv2.circle(map_img, aoi_pt, 10, (0, 0, 0), 2)

            # Add north arrow with white background
            arrow_x, arrow_y = img_width - 80, 80
            cv2.circle(map_img, (arrow_x, arrow_y + 20), 35, (255, 255, 255), -1)
            cv2.circle(map_img, (arrow_x, arrow_y + 20), 35, (0, 0, 0), 2)
            cv2.arrowedLine(map_img, (arrow_x, arrow_y + 40), (arrow_x, arrow_y), (0, 0, 0), 3, tipLength=0.3)
            cv2.putText(map_img, 'N', (arrow_x - 10, arrow_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

            # Add title with white background
            title_text = 'Overview Map'
            (text_width, text_height), baseline = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
            cv2.rectangle(map_img, (10, 10), (30 + text_width, 50 + text_height), (255, 255, 255), -1)
            cv2.rectangle(map_img, (10, 10), (30 + text_width, 50 + text_height), (0, 0, 0), 2)
            cv2.putText(map_img, title_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)

            # Add legend with white background
            legend_x, legend_y_start = 20, img_height - 120
            cv2.rectangle(map_img, (legend_x - 10, legend_y_start - 10),
                          (450, img_height - 20), (255, 255, 255), -1)
            cv2.rectangle(map_img, (legend_x - 10, legend_y_start - 10),
                          (450, img_height - 20), (0, 0, 0), 2)

            legend_y = legend_y_start + 10
            cv2.circle(map_img, (legend_x + 20, legend_y), 12, (0, 100, 255), -1)
            cv2.circle(map_img, (legend_x + 20, legend_y), 14, (0, 0, 0), 2)
            cv2.putText(map_img, 'Images with flagged AOIs', (legend_x + 44, legend_y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

            legend_y += 35
            cv2.circle(map_img, (legend_x + 20, legend_y), 8, (100, 100, 100), -1)
            cv2.circle(map_img, (legend_x + 20, legend_y), 10, (255, 255, 255), 2)
            cv2.putText(map_img, 'Images without flagged AOIs', (legend_x + 44, legend_y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

            legend_y += 35
            color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])
            cv2.circle(map_img, (legend_x + 20, legend_y), 8, color_bgr, -1)
            cv2.circle(map_img, (legend_x + 20, legend_y), 10, (0, 0, 0), 2)
            cv2.putText(map_img, 'Flagged AOI locations', (legend_x + 44, legend_y + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

            # Save to temporary file instead of BytesIO to reduce memory usage
            temp_file = self._save_image_to_temp_file(map_img, quality=75)
            # Explicitly delete large numpy array to free memory
            del map_img
            return temp_file

        except Exception as e:
            self.logger.error(f"Error generating overview map: {e}")
            return None

    def _download_map_tiles(self, min_lat, max_lat, min_lon, max_lon, img_width, img_height):
        """
        Download and composite map tiles for the given bounds.

        Args:
            min_lat, max_lat, min_lon, max_lon: Geographic bounds
            img_width, img_height: Target image dimensions

        Returns:
            np.ndarray: Composited map image
        """
        try:
            # Tile size (standard for OSM and ESRI)
            tile_size = 256

            # Calculate appropriate zoom level
            zoom = self._calculate_tile_zoom(min_lat, max_lat, min_lon, max_lon, img_width, img_height, tile_size)

            # Convert bounds to tile coordinates
            min_tile_x, max_tile_y = self._lat_lon_to_tile(min_lat, min_lon, zoom)
            max_tile_x, min_tile_y = self._lat_lon_to_tile(max_lat, max_lon, zoom)

            # Ensure correct order
            if min_tile_x > max_tile_x:
                min_tile_x, max_tile_x = max_tile_x, min_tile_x
            if min_tile_y > max_tile_y:
                min_tile_y, max_tile_y = max_tile_y, min_tile_y

            # Calculate number of tiles needed
            num_tiles_x = max_tile_x - min_tile_x + 1
            num_tiles_y = max_tile_y - min_tile_y + 1

            # Create canvas for tiles
            canvas_width = num_tiles_x * tile_size
            canvas_height = num_tiles_y * tile_size
            tile_canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 245

            # Setup cache directory
            cache_dir = Path(tempfile.gettempdir()) / "adiat_map_cache"
            cache_dir.mkdir(exist_ok=True)

            # Download and place tiles in parallel for better performance
            tile_coords = [(tx, ty) for ty in range(min_tile_y, max_tile_y + 1)
                           for tx in range(min_tile_x, max_tile_x + 1)]

            # Use ThreadPoolExecutor for parallel tile downloads
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_coord = {
                    executor.submit(self._get_tile, tx, ty, zoom, cache_dir): (tx, ty)
                    for tx, ty in tile_coords
                }

                for future in as_completed(future_to_coord):
                    tx, ty = future_to_coord[future]
                    try:
                        tile_img = future.result()
                        if tile_img is not None:
                            # Calculate position in canvas
                            x_offset = (tx - min_tile_x) * tile_size
                            y_offset = (ty - min_tile_y) * tile_size

                            # Place tile
                            tile_canvas[y_offset:y_offset + tile_size, x_offset:x_offset + tile_size] = tile_img
                    except Exception as e:
                        self.logger.error(f"Error downloading tile ({tx}, {ty}): {e}")
                        # Place gray tile as fallback
                        x_offset = (tx - min_tile_x) * tile_size
                        y_offset = (ty - min_tile_y) * tile_size
                        tile_canvas[y_offset:y_offset + tile_size, x_offset:x_offset + tile_size] = np.ones((tile_size, tile_size, 3), dtype=np.uint8) * 230

            # Convert geographic bounds to pixel coordinates in tile canvas
            min_lat_pixel_y = self._lat_to_pixel_y(min_lat, zoom, tile_size)
            max_lat_pixel_y = self._lat_to_pixel_y(max_lat, zoom, tile_size)
            min_lon_pixel_x = self._lon_to_pixel_x(min_lon, zoom, tile_size)
            max_lon_pixel_x = self._lon_to_pixel_x(max_lon, zoom, tile_size)

            # Calculate crop region (to match exact bounds)
            crop_x1 = int(min_lon_pixel_x - min_tile_x * tile_size)
            crop_y1 = int(max_lat_pixel_y - min_tile_y * tile_size)
            crop_x2 = int(max_lon_pixel_x - min_tile_x * tile_size)
            crop_y2 = int(min_lat_pixel_y - min_tile_y * tile_size)

            # Ensure crop bounds are valid
            crop_x1 = max(0, min(crop_x1, canvas_width))
            crop_y1 = max(0, min(crop_y1, canvas_height))
            crop_x2 = max(crop_x1, min(crop_x2, canvas_width))
            crop_y2 = max(crop_y1, min(crop_y2, canvas_height))

            # Crop to exact bounds
            cropped = tile_canvas[crop_y1:crop_y2, crop_x1:crop_x2]

            # Resize to target dimensions
            if cropped.shape[0] > 0 and cropped.shape[1] > 0:
                resized = cv2.resize(cropped, (img_width, img_height), interpolation=cv2.INTER_AREA)
                return resized
            else:
                # Fallback to gray background
                return np.ones((img_height, img_width, 3), dtype=np.uint8) * 245

        except Exception as e:
            self.logger.error(f"Error downloading map tiles: {e}")
            # Fallback to gray background
            return np.ones((img_height, img_width, 3), dtype=np.uint8) * 245

    def _lat_lon_to_tile(self, lat, lon, zoom):
        """Convert latitude/longitude to tile coordinates."""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    def _lat_to_pixel_y(self, lat, zoom, tile_size):
        """Convert latitude to pixel Y coordinate."""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        return (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n * tile_size

    def _lon_to_pixel_x(self, lon, zoom, tile_size):
        """Convert longitude to pixel X coordinate."""
        n = 2.0 ** zoom
        return (lon + 180.0) / 360.0 * n * tile_size

    def _calculate_tile_zoom(self, min_lat, max_lat, min_lon, max_lon, map_width, map_height, tile_size):
        """Calculate appropriate zoom level for given bounds."""
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon

        # Prevent division by zero
        if lat_diff == 0:
            lat_diff = 0.001
        if lon_diff == 0:
            lon_diff = 0.001

        # Calculate zoom for width and height
        zoom_x = math.log2(360 / lon_diff * map_width / tile_size)
        zoom_y = math.log2(180 / lat_diff * map_height / tile_size)

        # Use minimum zoom to ensure all points fit
        zoom = min(zoom_x, zoom_y)

        # Clamp to valid range (0-18) and leave some margin
        return max(1, min(18, int(zoom) - 1))

    def _get_tile(self, x_tile, y_tile, zoom, cache_dir):
        """
        Get a tile (from cache or download).

        Args:
            x_tile, y_tile: Tile coordinates
            zoom: Zoom level
            cache_dir: Cache directory path

        Returns:
            np.ndarray: Tile image (256x256x3) or None
        """
        try:
            tile_source = self.map_tile_source
            cache_path = cache_dir / f"{tile_source}_{zoom}_{x_tile}_{y_tile}.png"

            # Check cache first
            if cache_path.exists():
                tile_img = cv2.imread(str(cache_path))
                if tile_img is not None and tile_img.shape[0] == 256 and tile_img.shape[1] == 256:
                    return tile_img

            # Download tile from selected source
            if tile_source == 'satellite':
                url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
            else:
                url = f"https://tile.openstreetmap.org/{zoom}/{x_tile}/{y_tile}.png"

            # Use requests with timeout
            headers = {'User-Agent': 'ADIAT/1.0'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Save to cache
                with open(cache_path, 'wb') as f:
                    f.write(response.content)

                # Convert to numpy array
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                tile_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

                if tile_img is not None:
                    return tile_img

            # Fallback to gray tile
            return np.ones((256, 256, 3), dtype=np.uint8) * 230

        except Exception:
            # Return gray tile on error
            return np.ones((256, 256, 3), dtype=np.uint8) * 230

    def _calculate_aoi_gps(self, img, aoi):
        """
        Calculate GPS coordinates for an AOI.

        Args:
            img: Image dictionary
            aoi: AOI dictionary

        Returns:
            Dict with latitude/longitude or None
        """
        try:
            # Get original image path (not mask/thumbnail)
            original_path = img.get('original_path', img['path']) if 'original_path' in img else img['path']

            # Create image dict for AOIService
            image_dict = {
                'path': original_path,
                'mask_path': img.get('mask_path', '')
            }

            # Reuse ImageService if available (optimization)
            cache_key = original_path
            img_array = None
            if cache_key in self._image_service_cache:
                img_array = self._image_service_cache[cache_key].img_array

            aoi_service = AOIService(image_dict, img_array=img_array)

            # Get custom altitude if available
            custom_alt_ft = None
            if hasattr(self.viewer, 'custom_agl_altitude_ft') and self.viewer.custom_agl_altitude_ft and self.viewer.custom_agl_altitude_ft > 0:
                custom_alt_ft = self.viewer.custom_agl_altitude_ft

            # Get terrain preference
            use_terrain = getattr(self.viewer, 'use_terrain_elevation', True)

            # Calculate AOI GPS coordinates using the convenience method
            result = aoi_service.calculate_gps_with_custom_altitude(image_dict, aoi, custom_alt_ft, use_terrain)

            if result:
                lat, lon = result
                return {
                    'latitude': lat,
                    'longitude': lon
                }

            return None

        except Exception:
            return None

    def _get_aoi_average_info(self, image, aoi):
        """
        Calculate average color information for an AOI.

        Args:
            image: Image metadata dictionary
            aoi: AOI dictionary with center, radius, and optionally detected_pixels

        Returns:
            String with hue color info, or None
        """
        try:
            # Reuse ImageService if available (optimization)
            original_path = image.get('original_path', image['path']) if 'original_path' in image else image['path']
            cache_key = original_path
            img_array = None
            if cache_key in self._image_service_cache:
                img_array = self._image_service_cache[cache_key].img_array

            aoi_service = AOIService(image, img_array=img_array)

            color_result = aoi_service.get_cached_or_representative_color(aoi)
            if color_result:
                # Return hue angle with color square (matching viewer display)
                color_hex = color_result['hex']
                hue_degrees = color_result['hue_degrees']
                return f"Hue: {hue_degrees}° {color_hex} <font color='{color_hex}'>■</font>"

            return None

        except Exception as e:
            self.logger.error(f"Error calculating average color: {e}")
            return None

    def _save_image_to_temp_file(self, img_array, quality=70):
        """
        Save image array to a temporary file instead of keeping it in memory.

        This reduces memory usage for large image sets by writing images to disk
        and letting ReportLab read them when needed, rather than keeping all
        images in BytesIO buffers in memory.

        Args:
            img_array: Image as numpy array (BGR format)
            quality: JPEG quality (0-100)

        Returns:
            str: Path to temporary file
        """
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg', prefix='adiat_pdf_')
            os.close(temp_fd)  # Close file descriptor, we'll use the path

            # Encode and save to file
            _, buffer = cv2.imencode('.jpg', img_array, [cv2.IMWRITE_JPEG_QUALITY, quality])
            with open(temp_path, 'wb') as f:
                f.write(buffer.tobytes())

            # Track for cleanup
            self._temp_files.append(temp_path)

            return temp_path
        except Exception as e:
            self.logger.error(f"Error saving image to temp file: {e}")
            # Fallback to BytesIO if temp file fails
            _, buffer = cv2.imencode('.jpg', img_array, [cv2.IMWRITE_JPEG_QUALITY, quality])
            return BytesIO(buffer)

    def _cleanup_temp_files(self):
        """Clean up temporary files created during PDF generation."""
        for temp_path in self._temp_files:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                self.logger.warning(f"Failed to delete temp file {temp_path}: {e}")
        self._temp_files.clear()

    def _clear_caches(self):
        """Clear all caches to free memory."""
        self._composite_service.clear_cache()
        # Don't clear ImageService cache here as it might be reused
        # Individual entries are cleared after each image is processed
