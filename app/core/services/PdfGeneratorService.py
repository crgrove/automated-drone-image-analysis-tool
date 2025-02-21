from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame

from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer

import os
import cv2
from io import BytesIO
from datetime import datetime
import re

from helpers.LocationInfo import LocationInfo
from helpers.ColorUtils import ColorUtils
from core.services.LoggerService import LoggerService

import traceback


class PDFDocTemplate(BaseDocTemplate):
    """Custom document template with TOC support."""

    def __init__(self, filename, **kwargs):
        """
        Initialize a custom document template.

        Args:
            filename (str): The file path for the generated PDF document.
            **kwargs: Additional arguments for the BaseDocTemplate class.
        """
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kwargs)

        # Letter dimensions in cm
        page_width, page_height = letter  # (21.59 cm, 27.94 cm)
        min_margin = 0.635 * cm

        # Frame dimensions
        frame_width = page_width - (2 * min_margin)  # Minimize left and right margins
        frame_height = page_height - (2 * min_margin)  # Optional: Minimize top and bottom margins
        x_margin = min_margin  # Left margin
        y_margin = min_margin  # Bottom margin

        template = PageTemplate('normal', [Frame(x_margin, y_margin, frame_width, frame_height, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        """
        Register entries for the Table of Contents.

        Args:
            flowable (Flowable): A flowable object, such as a Paragraph.
        """
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            label = re.sub(r'\(.*?\)', '', text)
            style = flowable.style.name

            if style == 'Heading2':
                key = f'h2-{text}'
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (0, label, self.page, key))
            elif style == 'Heading3':
                # Include image names in TOC, exclude GPS data
                key = f'h3-{text}'
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (1, label, self.page, key))


class PdfGeneratorService:
    """Service for generating PDF reports from analysis results."""

    def __init__(self, viewer):
        """
        Initialize the PDF generator service.

        Args:
            viewer: Reference to the viewer instance for accessing necessary data and methods.
        """

        self.logger = LoggerService()
        self.viewer = viewer
        self.story = []
        self.doc = None
        self._initialize_styles()

    def generate_report(self, output_path):
        """
        Generate a PDF report of the analysis results.

        Args:
            output_path (str): The file path where the PDF should be saved.
        """
        try:
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"Output directory {output_dir} is not writable")

            # Validate images before starting
            for img in self.viewer.images:
                if not os.path.exists(img['path']):
                    raise FileNotFoundError(f"Image not found: {img['path']}")

            self.doc = PDFDocTemplate(output_path, pagesize=letter)

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

            self.story.append(Paragraph(f"ADIAT Analysis Report {current_datetime}", self.h1))

            # Add TOC
            toc = self._create_toc()
            self.story.append(toc)
            self.story.append(PageBreak())

            # Add algorithm settings section
            self._add_algorithm_settings()
            self.story.append(Spacer(1, 20))

            # Add image details
            self._add_image_details()

            # Build the PDF
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
        settings, algorithm = self.viewer.xmlService.get_settings()
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

    def _add_image_details(self):
        """
        Add details about images to the report.
        """
        visible_images = [img for img in self.viewer.images if not img.get('hidden', False)]
        self.story.append(Paragraph(f"Images ({len(visible_images)})", self.h2))
        for img in visible_images:
            if img.get('hidden', True):
                continue

            gps_coords = LocationInfo.get_gps(img['path'])
            if gps_coords:
                position = self.viewer.get_position(gps_coords['latitude'], gps_coords['longitude'])
                self.story.append(Paragraph(f"{img['name']} (Location: {position})", self.h3))
            else:
                self.story.append(Paragraph(f"{img['name']}", self.h3))

            self.story.append(Spacer(1, 5))
            self._add_full_image(img)
            self.story.append(Spacer(1, 10))
            self._add_areas_of_interest(img)
            self.story.append(PageBreak())

    def _add_full_image(self, img):
        """
        Add a resized full image to the report.

        Args:
            img (dict): The image data including path and metadata.
        """
        try:
            image = cv2.imread(img['path'])
            if image is None:
                self.logger.error(f"Failed to load image: {img['path']}")
                return

            # Get the original dimensions
            original_height, original_width = image.shape[:2]

            # Define the maximum width
            max_width = 400

            # Check if the width needs resizing
            if original_width > max_width:
                scaling_factor = max_width / original_width
                new_width = max_width
                new_height = int(original_height * scaling_factor)
                resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            else:
                resized_image = image

            _, buffer = cv2.imencode('.jpg', resized_image)
            image_bytes = BytesIO(buffer)

            img_obj = Image(image_bytes, hAlign="CENTER")
            self.story.append(img_obj)
        except Exception as e:
            self.logger.error(f"Error processing image {img['path']}: {str(e)}")

    def _add_areas_of_interest(self, img):
        """
        Add areas of interest to the report.

        Args:
            img (dict): The image data including areas of interest.
        """
        self.story.append(Paragraph("Areas of Interest", self.h4))
        visible_aois = [aoi for aoi in img['areas_of_interest'] if not aoi.get('hidden', False)]
        data = []
        num_columns = 4
        num_rows = (len(visible_aois) + num_columns - 1) // num_columns

        for i in range(num_rows):
            row = []
            for j in range(num_columns):
                aoi_index = i * num_columns + j
                if aoi_index < len(visible_aois):
                    aoi = visible_aois[aoi_index]
                    try:
                        img_arr = cv2.imread(img['path'])
                        if img_arr is None:
                            self.logger.error(f"Failed to load image for AOI: {img['path']}")
                            continue

                        x, y = aoi['center']
                        radius = aoi['radius'] + 10

                        sx, sy = max(0, x - radius), max(0, y - radius)
                        ex, ey = min(img_arr.shape[1] - 1, x + radius), min(img_arr.shape[0] - 1, y + radius)

                        cropped = img_arr[sy:ey, sx:ex]

                        thumbnail_size = (120, 120)
                        cropped_resized = cv2.resize(cropped, thumbnail_size, interpolation=cv2.INTER_AREA)
                        _, buffer = cv2.imencode('.jpg', cropped_resized)
                        image_bytes = BytesIO(buffer)

                        img_obj = Image(image_bytes)
                        img_obj.hAlign = 'CENTER'

                        coord_paragraph = Paragraph(f"X:{x}, Y:{y}", ParagraphStyle('Normal', alignment=1))
                        container = Table([[img_obj], [coord_paragraph]], colWidths=[1.5 * inch])
                        container.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                        ]))
                        row.append(container)
                    except Exception as e:
                        self.logger.error(f"Error creating AOI thumbnail: {str(e)}")
                else:
                    row.append(None)

            data.append(row)

        table = Table(data, colWidths=[2 * inch] * num_columns, spaceBefore=20, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20)
        ]))
        self.story.append(table)

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
