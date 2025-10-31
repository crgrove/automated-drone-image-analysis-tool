"""
HelpDialog - Displays keyboard shortcuts, button functions, and mouse controls.

Shows a comprehensive help dialog with all viewer functionality.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QScrollArea
from PySide6.QtCore import Qt, QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QFont, QPixmap
import base64


class HelpDialog(QDialog):
    """Dialog displaying viewer help information."""

    def __init__(self, parent=None):
        """
        Initialize the help dialog.

        Args:
            parent: Parent widget (main viewer)
        """
        super().__init__(parent)
        self.setWindowTitle("Viewer Help")
        self.setModal(False)
        self.resize(800, 700)
        self.parent_viewer = parent

        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()

        # Create scrollable text area
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(self.get_help_content())

        # Set font
        font = QFont()
        font.setPointSize(10)
        text_edit.setFont(font)

        layout.addWidget(text_edit)

        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def icon_to_base64(self, icon, size=25):
        """
        Convert a QIcon to base64 encoded PNG string.

        Args:
            icon: QIcon to convert
            size: Size of the icon in pixels

        Returns:
            str: Base64 encoded PNG data URL
        """
        if icon.isNull():
            return ""

        # Convert icon to pixmap
        pixmap = icon.pixmap(size, size)

        # Convert pixmap to PNG bytes
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        buffer.close()

        # Encode to base64
        base64_data = base64.b64encode(byte_array.data()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

    def get_button_icons(self):
        """
        Extract button icons from the parent viewer.

        Returns:
            dict: Dictionary of button names to base64 encoded icon data
        """
        icons = {}

        if not self.parent_viewer:
            return icons

        # Get icons from toolbar buttons
        button_mapping = {
            'adjustments': 'adjustmentsButton',
            'measure': 'measureButton',
            'magnify': 'magnifyButton',
            'kml': 'kmlButton',
            'pdf': 'pdfButton',
            'zip': 'zipButton'
        }

        for key, button_name in button_mapping.items():
            if hasattr(self.parent_viewer, button_name):
                button = getattr(self.parent_viewer, button_name)
                icon = button.icon()
                icons[key] = self.icon_to_base64(icon)

        return icons

    def get_help_content(self):
        """
        Generate HTML help content.

        Returns:
            str: HTML formatted help content
        """
        # Get button icons from parent viewer
        icons = self.get_button_icons()

        # Create icon HTML tags
        def icon_html(key):
            if key in icons and icons[key]:
                return f'<img src="{icons[key]}" width="25" height="25" style="vertical-align: middle; margin-right: 8px; border: 1px solid #555; border-radius: 3px; background: #3a3a3a; padding: 3px;" />'
            else:
                return '<span class="button-icon">?</span>'

        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #2196F3; margin-top: 20px; margin-bottom: 10px; }}
                h3 {{ color: #1976D2; margin-top: 15px; margin-bottom: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                td:first-child {{ font-weight: bold; width: 30%; }}
                .section {{ margin-bottom: 20px; }}
                .button-icon {{
                    display: inline-block;
                    width: 35px;
                    height: 35px;
                    text-align: center;
                    line-height: 35px;
                    font-size: 20px;
                    background: linear-gradient(145deg, #4a4a4a, #2a2a2a);
                    border: 1px solid #555;
                    border-radius: 4px;
                    margin-right: 8px;
                    vertical-align: middle;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
            </style>
        </head>
        <body>
            <h1 style="color: #1565C0; text-align: center;">ADIAT Image Viewer Help</h1>

            <div class="section">
                <h2>⌨️ Keyboard Shortcuts</h2>
                <table>
                    <tr>
                        <td>→ (Right Arrow)</td>
                        <td>Next image</td>
                    </tr>
                    <tr>
                        <td>← (Left Arrow)</td>
                        <td>Previous image</td>
                    </tr>
                    <tr>
                        <td>↑ (Up Arrow) or U</td>
                        <td>Unhide/show current image</td>
                    </tr>
                    <tr>
                        <td>↓ (Down Arrow) or P</td>
                        <td>Hide current image</td>
                    </tr>
                    <tr>
                        <td>Shift + F</td>
                        <td>Select AOI at cursor position</td>
                    </tr>
                    <tr>
                        <td>F</td>
                        <td>Flag/unflag currently selected AOI</td>
                    </tr>
                    <tr>
                        <td>R</td>
                        <td>Show north-oriented view of current image (rotated based on bearing)</td>
                    </tr>
                    <tr>
                        <td>H</td>
                        <td>Toggle highlight pixels of interest</td>
                    </tr>
                    <tr>
                        <td>M</td>
                        <td>Open GPS map view</td>
                    </tr>
                    <tr>
                        <td>C</td>
                        <td>Enter AOI creation mode</td>
                    </tr>
                    <tr>
                        <td>G</td>
                        <td>Toggle between Gallery View (all images) and Single Image View</td>
                    </tr>
                    <tr>
                        <td>E</td>
                        <td>Upscale currently visible portion of image</td>
                    </tr>
                    <tr>
                        <td>Shift + E</td>
                        <td>Export coverage extent KML (generates polygons showing geographic area covered by all images)</td>
                    </tr>
                    <tr>
                        <td>Shift + O</td>
                        <td>Override altitude for all images (manually set custom AGL altitude for GSD calculations)</td>
                    </tr>
                    <tr>
                        <td>Ctrl + H</td>
                        <td>Open image adjustments dialog</td>
                    </tr>
                    <tr>
                        <td>Ctrl + M</td>
                        <td>Open measure tool</td>
                    </tr>
                    <tr>
                        <td>Scroll Wheel</td>
                        <td>Zoom in/out on image</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>🔘 Toolbar Buttons</h2>

                <h3>Image Tools</h3>
                <table>
                    <tr>
                        <td>{icon_html('adjustments')} Adjustments</td>
                        <td>Open image adjustment dialog (exposure, highlights, shadows, and clarity)</td>
                    </tr>
                    <tr>
                        <td>{icon_html('measure')} Measure</td>
                        <td>Measure distances on the image</td>
                    </tr>
                    <tr>
                        <td>{icon_html('magnify')} Magnify</td>
                        <td>Toggle magnifying glass tool (shows zoomed view at cursor)</td>
                    </tr>
                </table>

                <h3>Export Tools</h3>
                <table>
                    <tr>
                        <td>{icon_html('kml')} KML Export</td>
                        <td>Export results to KML format for viewing in Google Earth</td>
                    </tr>
                    <tr>
                        <td>{icon_html('pdf')} PDF Export</td>
                        <td>Generate PDF report with images and AOIs</td>
                    </tr>
                    <tr>
                        <td>{icon_html('zip')} ZIP Export</td>
                        <td>Export images and data as ZIP archive</td>
                    </tr>
                    <tr>
                        <td>{icon_html('caltopo')} CalTopo Export</td>
                        <td>Export AOIs to CalTopo for mapping integration</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>⚙️ Toggles and Checkboxes</h2>
                <table>
                    <tr>
                        <td>Show Overlay</td>
                        <td>Display compass, scale bar, and north arrow overlay on image</td>
                    </tr>
                    <tr>
                        <td>Highlight Pixels</td>
                        <td>Toggle drawing the highlight of pixels of interest (same as H key)</td>
                    </tr>
                    <tr>
                        <td>Show AOIs</td>
                        <td>Display Areas of Interest (AOIs) circles on the image</td>
                    </tr>
                    <tr>
                        <td>Skip Hidden</td>
                        <td>Skip hidden images when navigating with arrow keys</td>
                    </tr>
                    <tr>
                        <td>Hide Image Toggle</td>
                        <td>Toggle current image hidden/visible state</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>🖱️ Mouse Controls</h2>

                <h3>Main Image Area</h3>
                <table>
                    <tr>
                        <td>Left Click</td>
                        <td>Create new AOI (circle mode) at cursor location</td>
                    </tr>
                    <tr>
                        <td>Left Click + Drag</td>
                        <td>Draw a rectangle to zoom to that section</td>
                    </tr>
                    <tr>
                        <td>Scroll Wheel</td>
                        <td>Zoom in/out</td>
                    </tr>
                    <tr>
                        <td>Middle Click</td>
                        <td>Open magnifier</td>
                    </tr>
                    <tr>
                        <td>Right Click</td>
                        <td>Pan the image</td>
                    </tr>
                </table>

                <h3>AOI Thumbnail Panel</h3>
                <table>
                    <tr>
                        <td>Left Click</td>
                        <td>Jump to that image</td>
                    </tr>
                    <tr>
                        <td>Right Click</td>
                        <td>Copy AOI Data (GPS coordinates, color, etc) to clipboard</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>🎯 AOI Management</h2>
                <table>
                    <tr>
                        <td>⬍ Sort Button</td>
                        <td>Sort AOIs by various criteria (color, size, and distance)</td>
                    </tr>
                    <tr>
                        <td>⊙ Filter Button</td>
                        <td>Filter AOIs by status (flagged, color, and size range)</td>
                    </tr>
                    <tr>
                        <td>AOI List Item Click</td>
                        <td>Select and view that AOI in the main image</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>📍 GPS and Navigation</h2>
                <table>
                    <tr>
                        <td>GPS Coordinates Link</td>
                        <td>Click on GPS coordinates in status bar to:
                            <ul>
                                <li>Copy coordinates to clipboard</li>
                                <li>Open in Google Maps</li>
                                <li>Open in CalTopo</li>
                                <li>Show on GPS map</li>
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <td>Jump To Field</td>
                        <td>Enter image number and press Enter to jump directly to that image</td>
                    </tr>
                    <tr>
                        <td>Previous/Next Buttons</td>
                        <td>Navigate to previous/next image (respects "Skip Hidden" setting)</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>📊 Status Bar Information</h2>
                <p>The bottom status bar displays:</p>
                <ul>
                    <li><b>GPS Coordinates:</b> Latitude and longitude of current image (clickable)</li>
                    <li><b>Relative Altitude:</b> The altitude of the drone relative to its take off point</li>
                    <li><b>Estimated Average GSD:</b> The estimated Ground Sampling Distance (cm/px) calculated from the drones Relative Altitude. WARNING, may not be accurate</li>
                    <li><b>Color Values:</b> The RGB, HSV, or temperature pixel value at the current cursor position</li>
                    <li><b>Drone Orientation:</b> Drone bearing angle</li>
                </ul>
            </div>

            <div class="section">
                <h2>💡 Tips</h2>
                <ul>
                    <li>Use <b>Shift+F</b> to quickly select AOIs without clicking on them precisely</li>
                    <li>Press <b>F</b> to flag important AOIs for quick filtering later</li>
                    <li>Use the <b>magnifying glass</b> to inspect fine details without zooming the entire view</li>
                    <li>Left click on on an AOIs document icon to add <b>comments</b> for that AOI. Comments are exported in reports and CalTopo markers</li>
                    <li>The <b>measure tool</b> uses the estimated GSD for calculating measurements. WARNING it may not be accurate</li>
                    <li>Press <b>M</b> to open the GPS map and see the spatial distribution of all images and selected AOI</li>
                    <li>Press <b>R</b> to view images oriented to true north based on drone heading</li>
                </ul>
            </div>

        </body>
        </html>
        """
