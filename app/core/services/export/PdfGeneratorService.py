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
from helpers.MetaDataHelper import MetaDataHelper

import traceback


class PDFDocTemplate(BaseDocTemplate):
    """Custom document template with TOC support."""

    def __init__(self, filename, organization="[ORGANIZATION]", **kwargs):
        """
        Initialize a custom document template.

        Args:
            filename (str): The file path for the generated PDF document.
            organization (str): Organization name for the footer
            **kwargs: Additional arguments for the BaseDocTemplate class.
        """
        self.allowSplitting = 0
        self.organization = organization
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
        Register entries for the Table of Contents.
        Optimized to avoid unnecessary string operations for non-Paragraph flowables.

        Args:
            flowable (Flowable): A flowable object, such as a Paragraph.
        """
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


class PdfGeneratorService:
    """Service for generating PDF reports from analysis results."""

    def __init__(self, viewer, organization="", search_name="", images=None, include_images_without_flagged_aois=False):
        """
        Initialize the PDF generator service.

        Args:
            viewer: Reference to the viewer instance for accessing necessary data and methods.
            organization: Organization name for the report
            search_name: Search/mission name for the report
            images: List of images to include in the PDF (if None, will use viewer.images)
            include_images_without_flagged_aois: Whether to include images without flagged AOIs
        """

        self.logger = LoggerService()
        self.viewer = viewer
        self.organization = organization if organization else "[ORGANIZATION]"
        self.search_name = search_name if search_name else "Analysis"
        self.include_images_without_flagged_aois = include_images_without_flagged_aois
        self.images = images  # Store the images to use for PDF generation
        self.story = []
        self.doc = None
        self._initialize_styles()

        # Performance optimization: Cache rotated images per image path
        self._rotated_image_cache = {}  # key: (image_path, bearing) -> rotated_img_array
        self._image_service_cache = {}  # key: image_path -> ImageService instance

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

            self.doc = PDFDocTemplate(output_path, organization=self.organization, pagesize=letter)

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
            map_bytes = self._generate_overview_map()
            if map_bytes:
                map_img = Image(map_bytes, width=7 * inch, height=5.25 * inch)
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

            # Update progress before the potentially slow multiBuild operation
            if progress_callback:
                progress_callback(total_flagged_aois, total_flagged_aois, "Building PDF document...")

            # Build the PDF
            # Note: multiBuild is necessary for TOC as it processes the document twice
            # (once to collect TOC entries, once to build with page numbers)
            self.doc.multiBuild(self.story)

        except Exception as e:
            # print(traceback.format_exc())
            self.logger.error(f"PDF generation failed: {str(e)}")
            raise

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
                self.logger.info("PDF generation cancelled by user")
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
            position_str = image_service.get_position(self.viewer.position_format) or "N/A"
            agl_str = f"{image_service.get_relative_altitude(self.viewer.distance_unit)}{self.viewer.distance_unit}"
            orientation_str = f"{bearing}°"
            gsd_str = f"{image_service.get_average_gsd()}cm/px"

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
                    self.logger.info("PDF generation cancelled by user")
                    return

                # Create 0x (full image, north-up) - top half, edge to edge
                # Pass cache key to enable caching
                full_img, full_aoi_pos = self._create_full_rotated_image(
                    img_array, aoi, bearing, identifier_color, cache_key=original_path
                )

                # Create 3x and 6x images (without circles - they'll be added in composite)
                # Pass cache key to enable caching
                medium_img, medium_aoi_pos = self._create_zoomed_aoi_image(
                    img_array, aoi, 3, bearing, identifier_color, draw_circle=False, cache_key=original_path
                )
                closeup_img, closeup_aoi_pos = self._create_zoomed_aoi_image(
                    img_array, aoi, 6, bearing, identifier_color, draw_circle=False, cache_key=original_path
                )

                # Create composite image with connector lines between images
                if full_img is not None and medium_img is not None and closeup_img is not None:
                    composite_img = self._create_composite_with_connectors(
                        full_img, full_aoi_pos,
                        medium_img, medium_aoi_pos,
                        closeup_img, closeup_aoi_pos,
                        aoi['radius']
                    )

                    # Add composite image
                    # Reduced quality to 70 for significantly smaller file size while maintaining acceptable visual quality
                    # This should reduce file size by ~40-50% compared to 85% quality
                    _, buffer = cv2.imencode('.jpg', composite_img, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    composite_bytes = BytesIO(buffer)

                    # Use full page width
                    composite_img_obj = Image(composite_bytes, width=7.5 * inch, height=6 * inch)
                    composite_img_obj.hAlign = 'CENTER'
                    self.story.append(composite_img_obj)
                    self.story.append(Spacer(1, 10))

                # Add additional metadata
                metadata_lines = []

                # Add AOI GPS coordinates if available
                aoi_gps = self._calculate_aoi_gps(img, aoi)
                if aoi_gps:
                    aoi_gps_str = f"{aoi_gps['latitude']:.6f}, {aoi_gps['longitude']:.6f}"
                    metadata_lines.append(f"<b>Estimated AOI GPS Location:</b> {aoi_gps_str}")

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
            BytesIO: Image bytes of the overview map, or None if no GPS data
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

            # Encode to bytes (reduced quality to 75 for smaller file size - maps don't need high detail)
            _, buffer = cv2.imencode('.jpg', map_img, [cv2.IMWRITE_JPEG_QUALITY, 75])
            return BytesIO(buffer)

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
            # Use OpenStreetMap tiles (prefer 'map' for streets/trails visibility)
            tile_source = 'map'
            cache_path = cache_dir / f"{tile_source}_{zoom}_{x_tile}_{y_tile}.png"

            # Check cache first
            if cache_path.exists():
                tile_img = cv2.imread(str(cache_path))
                if tile_img is not None and tile_img.shape[0] == 256 and tile_img.shape[1] == 256:
                    return tile_img

            # Download tile
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

            # Calculate AOI GPS coordinates using the convenience method
            result = aoi_service.calculate_gps_with_custom_altitude(image_dict, aoi, custom_alt_ft)

            if result:
                lat, lon = result
                return {
                    'latitude': lat,
                    'longitude': lon
                }

            return None

        except Exception:
            return None

    def _rotate_image_north_up(self, img_array, bearing, cache_key=None):
        """
        Rotate image so north is up. Uses caching to avoid re-rotating the same image.

        Args:
            img_array: Image as numpy array
            bearing: Drone bearing in degrees (0-360)
            cache_key: Optional cache key for this image (to enable caching)

        Returns:
            Rotated image array
        """
        if bearing is None:
            return img_array

        # Check cache if cache_key provided
        if cache_key is not None:
            cache_entry = (cache_key, bearing)
            if cache_entry in self._rotated_image_cache:
                return self._rotated_image_cache[cache_entry]

        height, width = img_array.shape[:2]
        center = (width / 2, height / 2)

        # Rotate by -bearing to make north up
        rotation_matrix = cv2.getRotationMatrix2D(center, -bearing, 1.0)

        # Calculate new dimensions to fit rotated image
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))

        # Adjust rotation matrix for translation
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # Perform rotation
        rotated = cv2.warpAffine(img_array, rotation_matrix, (new_width, new_height),
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

        # Cache the result if cache_key provided
        if cache_key is not None:
            cache_entry = (cache_key, bearing)
            self._rotated_image_cache[cache_entry] = rotated

        return rotated

    def _transform_aoi_center(self, aoi_center, bearing, img_width, img_height):
        """
        Transform AOI center coordinates after image rotation using the same matrix as cv2.warpAffine.

        Args:
            aoi_center: Original (x, y) center
            bearing: Rotation angle in degrees
            img_width: Original image width
            img_height: Original image height

        Returns:
            Transformed (x, y) center in rotated image
        """
        if bearing is None:
            return aoi_center

        # Create the same rotation matrix as used in _rotate_image_north_up
        center = (img_width / 2, img_height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, -bearing, 1.0)

        # Calculate new dimensions
        cos = abs(rotation_matrix[0, 0])
        sin = abs(rotation_matrix[0, 1])
        new_width = int((img_height * sin) + (img_width * cos))
        new_height = int((img_height * cos) + (img_width * sin))

        # Adjust rotation matrix for translation (same as image rotation)
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # Apply the transformation to the AOI point
        aoi_point = np.array([[aoi_center]], dtype=np.float32)
        transformed_point = cv2.transform(aoi_point, rotation_matrix)
        new_x, new_y = transformed_point[0][0]

        return (int(new_x), int(new_y))

    def _create_zoomed_aoi_image(self, img_array, aoi, zoom_level, bearing, identifier_color, draw_circle=True, cache_key=None):
        """
        Create a zoomed view of an AOI with optional connector line.

        Args:
            img_array: Original image array
            aoi: AOI dictionary
            zoom_level: Zoom factor (2, 3, 4, 10, or 'closeup')
            bearing: Drone bearing for north rotation
            identifier_color: RGB tuple for AOI circle
            draw_circle: Whether to draw the AOI circle
            cache_key: Optional cache key for rotated image caching

        Returns:
            Tuple of (zoomed_image_array, aoi_position_in_crop) or None
        """
        try:
            # First rotate the image (will use cache if available)
            rotated_img = self._rotate_image_north_up(img_array, bearing, cache_key=cache_key)
            height, width = img_array.shape[:2]
            rot_height, rot_width = rotated_img.shape[:2]

            # Transform AOI center to rotated coordinates
            transformed_center = self._transform_aoi_center(aoi['center'], bearing, width, height)
            x, y = transformed_center
            radius = aoi['radius']

            # Calculate crop size based on zoom level
            # Use larger multipliers for better context
            if zoom_level == 2:
                crop_radius = radius * 8  # Show good context around AOI
            elif zoom_level == 3:
                crop_radius = radius * 3
            elif zoom_level == 4:
                crop_radius = radius * 5  # Moderate zoom
            elif zoom_level == 6:
                crop_radius = radius * 6  # Moderate zoom for 6x
            elif zoom_level == 10:
                crop_radius = int(radius * 1.5)
            else:  # closeup
                crop_radius = int(radius * 1.1)

            # Calculate crop bounds centered on AOI
            sx = max(0, int(x - crop_radius))
            sy = max(0, int(y - crop_radius))
            ex = min(rot_width, int(x + crop_radius))
            ey = min(rot_height, int(y + crop_radius))

            # Crop the image
            cropped = rotated_img[sy:ey, sx:ex].copy()

            # Calculate AOI position in cropped image
            aoi_x_in_crop = int(x - sx)
            aoi_y_in_crop = int(y - sy)

            # Draw AOI circle on the image (if requested)
            if draw_circle:
                color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])  # RGB to BGR
                cv2.circle(cropped, (aoi_x_in_crop, aoi_y_in_crop), radius, color_bgr, 3)

            return cropped, (aoi_x_in_crop, aoi_y_in_crop)

        except Exception as e:
            self.logger.error(f"Error creating zoomed AOI image: {e}")
            return None, None

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

            color_result = aoi_service.get_aoi_representative_color(aoi)
            if color_result:
                # Return hue angle with color square (matching viewer display)
                color_hex = color_result['hex']
                hue_degrees = color_result['hue_degrees']
                return f"Hue: {hue_degrees}° {color_hex} <font color='{color_hex}'>■</font>"

            return None

        except Exception as e:
            self.logger.error(f"Error calculating average color: {e}")
            return None

    def _create_composite_with_connectors(self, full_img, full_aoi_pos, medium_img, medium_aoi_pos, closeup_img, closeup_aoi_pos, aoi_radius):
        """
        Create a composite image with all three zoom levels and connector lines between them.

        Args:
            full_img: 0x full rotated image
            full_aoi_pos: AOI position in full image
            medium_img: 3x zoomed image
            medium_aoi_pos: AOI position in medium image
            closeup_img: 6x zoomed image
            closeup_aoi_pos: AOI position in closeup image
            aoi_radius: Radius of the AOI circle

        Returns:
            Composite image with connector lines
        """
        try:
            # Get dimensions
            full_h, full_w = full_img.shape[:2]
            medium_h, medium_w = medium_img.shape[:2]
            closeup_h, closeup_w = closeup_img.shape[:2]

            # Calculate composite dimensions
            # Use full image width as reference
            composite_w = full_w

            # Calculate target dimensions for bottom images (each takes half width)
            bottom_target_w = composite_w // 2

            # Scale medium image to fit half width while maintaining aspect ratio
            medium_scale = bottom_target_w / medium_w
            medium_scaled_h = int(medium_h * medium_scale)
            medium_scaled_w = bottom_target_w
            medium_scaled = cv2.resize(medium_img, (medium_scaled_w, medium_scaled_h), interpolation=cv2.INTER_AREA)
            medium_aoi_scaled = (int(medium_aoi_pos[0] * medium_scale), int(medium_aoi_pos[1] * medium_scale))

            # Scale closeup image to fit half width while maintaining aspect ratio
            closeup_scale = bottom_target_w / closeup_w
            closeup_scaled_h = int(closeup_h * closeup_scale)
            closeup_scaled_w = bottom_target_w
            closeup_scaled = cv2.resize(closeup_img, (closeup_scaled_w, closeup_scaled_h), interpolation=cv2.INTER_AREA)
            closeup_aoi_scaled = (int(closeup_aoi_pos[0] * closeup_scale), int(closeup_aoi_pos[1] * closeup_scale))

            # Calculate composite height
            max_bottom_h = max(medium_scaled_h, closeup_scaled_h)
            composite_h = full_h + max_bottom_h + 20  # 20px gap

            # Create white canvas
            composite = np.ones((composite_h, composite_w, 3), dtype=np.uint8) * 255

            # Place full image at top (already full width)
            composite[0:full_h, 0:full_w] = full_img

            # Place closeup (6x) image bottom left (fill left half)
            closeup_y = full_h + 20
            closeup_x = 0
            composite[closeup_y:closeup_y + closeup_scaled_h, closeup_x:closeup_x + closeup_scaled_w] = closeup_scaled

            # Place medium (3x) image bottom right (fill right half)
            medium_y = full_h + 20
            medium_x = composite_w // 2
            composite[medium_y:medium_y + medium_scaled_h, medium_x:medium_x + medium_scaled_w] = medium_scaled

            # Calculate AOI positions in composite image
            full_aoi_composite = (full_aoi_pos[0], full_aoi_pos[1])
            medium_aoi_composite = (medium_x + medium_aoi_scaled[0], medium_y + medium_aoi_scaled[1])
            closeup_aoi_composite = (closeup_x + closeup_aoi_scaled[0], closeup_y + closeup_aoi_scaled[1])

            # Helper function to calculate line endpoint at circle edge
            def calculate_circle_edge_point(start_pt, circle_center, circle_radius):
                # Calculate direction vector
                dx = circle_center[0] - start_pt[0]
                dy = circle_center[1] - start_pt[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance == 0:
                    return circle_center

                # Normalize and scale to circle edge
                scale = (distance - circle_radius) / distance
                end_x = int(start_pt[0] + dx * scale)
                end_y = int(start_pt[1] + dy * scale)
                return (end_x, end_y)

            # Draw connector lines to edge of AOI circle
            # Medium to full (straight line to circle edge)
            medium_line_end = calculate_circle_edge_point(medium_aoi_composite, full_aoi_composite, aoi_radius)
            cv2.line(composite, medium_aoi_composite, medium_line_end, (255, 0, 255), 3)

            # Closeup to full (straight line to circle edge)
            closeup_line_end = calculate_circle_edge_point(closeup_aoi_composite, full_aoi_composite, aoi_radius)
            cv2.line(composite, closeup_aoi_composite, closeup_line_end, (255, 0, 255), 3)

            return composite

        except Exception as e:
            self.logger.error(f"Error creating composite image: {e}")
            # Return full image as fallback
            return full_img

    def _create_full_rotated_image(self, img_array, aoi, bearing, identifier_color, cache_key=None):
        """
        Create a full rotated image (0x zoom) with AOI marked, cropped to fit without stretching.

        Args:
            img_array: Original full image array
            aoi: AOI dictionary
            bearing: Drone bearing for north rotation
            identifier_color: RGB tuple for AOI circle
            cache_key: Optional cache key for rotated image caching

        Returns:
            Tuple of (cropped_rotated_image, aoi_position_in_cropped_image)
        """
        try:
            # Rotate the full image (will use cache if available)
            rotated_img = self._rotate_image_north_up(img_array, bearing, cache_key=cache_key)
            height, width = img_array.shape[:2]
            rot_height, rot_width = rotated_img.shape[:2]

            # Transform AOI center to rotated coordinates
            transformed_center = self._transform_aoi_center(aoi['center'], bearing, width, height)
            x, y = transformed_center
            radius = aoi['radius']

            # Calculate crop to fit page width while maintaining aspect ratio
            # Target: 7.5 inch width, ~3.5 inch height (for top half of page)
            target_aspect = 7.5 / 3.5  # Width / Height ratio

            # Calculate crop dimensions maintaining aspect ratio
            crop_width = rot_width
            crop_height = int(crop_width / target_aspect)

            # If calculated height exceeds image, adjust
            if crop_height > rot_height:
                crop_height = rot_height
                crop_width = int(crop_height * target_aspect)

            # Ensure AOI is in the crop - center crop around AOI
            crop_x = max(0, min(x - crop_width // 2, rot_width - crop_width))
            crop_y = max(0, min(y - crop_height // 2, rot_height - crop_height))

            # Crop the rotated image
            cropped = rotated_img[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width].copy()

            # Calculate AOI position in cropped image
            aoi_x_in_crop = x - crop_x
            aoi_y_in_crop = y - crop_y

            # Draw AOI circle on the cropped image
            color_bgr = (identifier_color[2], identifier_color[1], identifier_color[0])
            cv2.circle(cropped, (aoi_x_in_crop, aoi_y_in_crop), radius, color_bgr, 3)

            return cropped, (aoi_x_in_crop, aoi_y_in_crop)

        except Exception as e:
            self.logger.error(f"Error creating full rotated image: {e}")
            return None, None
