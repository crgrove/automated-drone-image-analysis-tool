from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
import tempfile
import os
import qimage2ndarray
from PyQt5.QtCore import Qt
from helpers.LocationInfo import LocationInfo
import cv2
from helpers.ColorUtils import ColorUtils

class PDFDocTemplate(BaseDocTemplate):
    """Custom document template with TOC support."""
    
    def __init__(self, filename, **kwargs):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kwargs)
        template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        """Registers TOC entries."""
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                key = f'h1-{text}'
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (0, text, self.page, key))
            elif style == 'Heading2':
                key = f'h2-{text}'
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (1, text, self.page, key))

class PdfGeneratorService:
    """Service for generating PDF reports from analysis results."""

    def __init__(self, viewer):
        """
        Initialize the PDF generator service.
        
        Args:
            viewer: Reference to the viewer instance for accessing necessary data and methods
        """
        self.viewer = viewer
        self.temp_files = []

    def generate_report(self, output_path):
        """
        Generate a PDF report of the analysis results.
        
        Args:
            output_path (str): The file path where the PDF should be saved
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
            
            doc = PDFDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Define heading styles
            h1 = ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            
            h2 = ParagraphStyle(
                name='Heading2',
                parent=styles['Heading2'],
                fontSize=18,
                spaceAfter=20
            )

            # Add title and TOC
            story.append(Paragraph("Analysis Report", h1))
            toc = self._create_toc()
            story.append(toc)
            story.append(PageBreak())

            # Add algorithm settings section
            self._add_algorithm_settings(story, styles, h1)
            story.append(Spacer(1, 20))

            # Add total areas of interest
            total_aoi = sum(len(img['areas_of_interest']) for img in self.viewer.images)
            story.append(Paragraph(f"Total Areas of Interest: {total_aoi}", h1))
            story.append(PageBreak())

            # Add image details
            self._add_image_details(story, h1, h2, styles, doc)

            # Build the PDF
            doc.multiBuild(story)

            # Clean up temporary files
            self._cleanup_temp_files()

        except Exception as e:
            self.viewer.logger.error(f"PDF generation failed: {str(e)}")
            self._cleanup_temp_files()
            raise

    def _create_toc(self):
        """Create and configure the table of contents."""
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(
                fontSize=14, 
                name='TOCHeading1',
                leftIndent=20, 
                firstLineIndent=-20, 
                spaceBefore=5, 
                leading=16
            ),
            ParagraphStyle(
                fontSize=12, 
                name='TOCHeading2',
                leftIndent=40, 
                firstLineIndent=-20, 
                spaceBefore=0, 
                leading=12
            )
        ]
        return toc

    def _add_algorithm_settings(self, story, styles, h1):
        """Add algorithm settings section to the report."""
        # Algorithm Information
        story.append(Paragraph("Algorithm Settings", h1))
        settings, algorithm = self.viewer.xmlService.getSettings()
        story.append(Paragraph(f"Algorithm: {algorithm}", styles['Normal']))

        # Process settings with color squares
        for key, value in settings.items():
            rgb_value = value if isinstance(value, tuple) else ColorUtils.parse_rgb_string(str(value))

            if rgb_value and len(rgb_value) == 3:
                r, g, b = rgb_value
                color_hex = f"#{r:02x}{g:02x}{b:02x}"
                story.append(Paragraph(
                    f"{key}: {value} <font color='{color_hex}'>■</font>",
                    styles['Normal']
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
                story.append(Paragraph(f"{key}: {{{', '.join(nested_values)}}}", styles['Normal']))
            else:
                story.append(Paragraph(f"{key}: {value}", styles['Normal']))

        story.append(Spacer(1, 20))

    def _add_image_details(self, story, h1, h2, styles, doc):
        """Add image details section to the report."""
        for img in self.viewer.images:
            # Skip hidden images if show_hidden is False
            if not self.viewer.show_hidden and img.get('hidden', False):
                continue

            if len(img['areas_of_interest']) > 0:
                # Image Header
                story.append(Paragraph(f"Image: {img['name']}", h1))
                
                # GPS Coordinates
                gps_coords = LocationInfo.getGPS(img['path'])
                if gps_coords:
                    position = self.viewer.getPosition(gps_coords['latitude'], gps_coords['longitude'])
                    story.append(Paragraph(f"GPS Coordinates: {position}", styles['Normal']))
                story.append(Spacer(1, 20))

                # Add full image
                self._add_full_image(story, img, doc)
                story.append(Spacer(1, 20))

                # Add areas of interest
                self._add_areas_of_interest(story, img, h2)
                story.append(PageBreak())

    def _add_full_image(self, story, img, doc):
        try:
            """Add full image to the report."""
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            self.temp_files.append(temp_file.name)
            temp_file.close()

            # Save full image
            img_arr = qimage2ndarray.imread(img['path'])
            if img_arr is None:
                self.viewer.logger.error(f"Failed to load image: {img['path']}")
                return
            qimg = qimage2ndarray.array2qimage(img_arr)
            scaled_img = qimg.scaled(1500, 1500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            scaled_img.save(temp_file.name)

            # Add to PDF with proper sizing
            img_obj = Image(temp_file.name)
            available_width = doc.width
            available_height = doc.height * 0.5
            img_width = img_obj.imageWidth
            img_height = img_obj.imageHeight
            
            if img_width == 0 or img_height == 0:
                self.viewer.logger.error(f"Invalid image dimensions for {img['path']}")
                return
            scale = min(available_width / max(img_width, 1), available_height / max(img_height, 1))
            img_obj.drawWidth = img_width * scale
            img_obj.drawHeight = img_height * scale
            story.append(img_obj)
        except Exception as e:
            self.viewer.logger.error(f"Error processing image {img['path']}: {str(e)}")

    def _add_areas_of_interest(self, story, img, h2):
        """Add areas of interest to the report."""
        visible_aois = [aoi for aoi in img['areas_of_interest'] if not aoi.get('hidden', False)]
        for i, aoi in enumerate(visible_aois, 1):
            story.append(Paragraph(f"Area of Interest #{i}", h2))
            story.append(Paragraph(
                f"Pixel Coordinates: ({aoi['center'][0]}, {aoi['center'][1]})", 
                ParagraphStyle('Normal')
            ))

            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            self.temp_files.append(temp_file.name)
            temp_file.close()

            # Generate AOI thumbnail
            try:
                img_arr = qimage2ndarray.imread(img['path'])
                if img_arr is None:
                    self.viewer.logger.error(f"Failed to load image for AOI: {img['path']}")
                    continue
                    
                # Calculate crop coordinates
                x, y = aoi['center']
                size = 100  # Size of the crop area
                startx = max(0, x - size)
                starty = max(0, y - size)
                endx = min(img_arr.shape[1], x + size)
                endy = min(img_arr.shape[0], y + size)
                
                # Crop and save thumbnail
                cropped = img_arr[starty:endy, startx:endx]
                # Convert from BGR to RGB before saving
                cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                cv2.imwrite(temp_file.name, cropped_rgb)
                
                img_obj = Image(temp_file.name, width=3*inch, height=3*inch)
                story.append(img_obj)
                story.append(Spacer(1, 20))
            except Exception as e:
                self.viewer.logger.error(f"Error creating AOI thumbnail: {str(e)}")

    def _cleanup_temp_files(self):
        """Clean up temporary files created during PDF generation."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except Exception as e:
                self.viewer.logger.error(f"Failed to delete temporary file {temp_file}: {str(e)}")
                # pass  # Log error if needed
        self.temp_files = []
