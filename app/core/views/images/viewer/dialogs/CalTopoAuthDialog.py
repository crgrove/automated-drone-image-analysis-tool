"""
CalTopoAuthDialog - Authentication dialog for CalTopo login.

This dialog provides an in-app browser for CalTopo authentication
using QWebEngineView.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
import os


class CalTopoAuthDialog(QDialog):
    """
    Dialog for CalTopo authentication.

    Displays CalTopo login page in an embedded browser and captures
    session cookies upon successful login.
    """

    # Signal emitted when authentication is successful
    authenticated = Signal(dict)  # Emits cookies dictionary

    def __init__(self, parent=None):
        """
        Initialize the authentication dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("CalTopo Login & Map Selection")
        self.resize(900, 700)
        self.setModal(True)

        self.cookies_captured = False
        self.map_id = None
        self.map_url = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)  # Reduce dialog margins
        layout.setSpacing(2)  # Reduce spacing between widgets

        # Current map display with instructions inline - compact layout
        map_info_layout = QHBoxLayout()
        map_info_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        map_info_layout.setSpacing(10)  # Tighter spacing

        self.current_map_label = QLabel("Current map: Not selected")
        self.current_map_label.setStyleSheet("padding: 2px; font-size: 11px; color: #666;")
        map_info_layout.addWidget(self.current_map_label)

        # Instructions on the right
        info_label = QLabel("(Login → Navigate to your map → Click 'I'm Logged In')")
        info_label.setStyleSheet("padding: 2px; font-size: 10px; color: #888;")
        map_info_layout.addWidget(info_label)
        map_info_layout.addStretch()

        layout.addLayout(map_info_layout, 0)  # Stretch factor 0 = fixed height

        # Web view for login with persistent profile
        self.web_view = QWebEngineView()

        # Create a persistent profile so cookies are saved between sessions
        profile_path = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
            "CalTopoProfile"
        )
        self.profile = QWebEngineProfile("CalTopoProfile")
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        # Set the profile on a new page
        from PySide6.QtWebEngineCore import QWebEnginePage
        page = QWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(page)

        # Load CalTopo - start at the main map page (will redirect to login if not authenticated)
        self.web_view.setUrl(QUrl("https://caltopo.com/map.html"))

        # Monitor URL changes to detect successful login
        self.web_view.urlChanged.connect(self.on_url_changed)

        layout.addWidget(self.web_view, 1)  # Stretch factor 1 = expands to fill space

        # Button row
        button_layout = QHBoxLayout()

        # Manual login confirmation button (always enabled as fallback)
        self.manual_done_button = QPushButton("I'm Logged In - Capture Session")
        self.manual_done_button.clicked.connect(self.on_manual_done_clicked)
        self.manual_done_button.setToolTip("Click this after logging in if the Done button doesn't activate")

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.on_done_clicked)
        self.done_button.setEnabled(False)  # Disabled until login detected
        self.done_button.setVisible(False)  # Hide initially, show when auto-detected

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.manual_done_button)
        button_layout.addWidget(self.done_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout, 0)  # Stretch factor 0 = fixed height

        self.setLayout(layout)

    def on_url_changed(self, url):
        """Handle URL changes to detect successful login and extract map ID.

        Args:
            url (QUrl): New URL
        """
        url_string = url.toString()

        # Debug: print URL to help diagnose
        print(f"CalTopo URL changed to: {url_string}")

        # Extract map ID from URL if present
        # CalTopo URLs can be:
        # - https://caltopo.com/map.html#ll=lat,lon&...&id=ABC123
        # - https://caltopo.com/m/ABC123
        # - https://caltopo.com/app/map/ABC123
        import re

        map_id = None
        if '#' in url_string and 'id=' in url_string:
            # Extract from hash parameter: #...&id=ABC123
            match = re.search(r'[#&]id=([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)
        elif '/m/' in url_string:
            # Extract from /m/ABC123 format
            match = re.search(r'/m/([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)
        elif '/map/' in url_string:
            # Extract from /app/map/ABC123 or /map/ABC123 format
            match = re.search(r'/map/([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)

        if map_id:
            self.map_id = map_id
            self.map_url = url_string
            self.current_map_label.setText(f"Current map: {map_id}")
            self.current_map_label.setStyleSheet("padding: 5px; font-size: 11px; color: #2E7D32; font-weight: bold;")
            print(f"Map ID detected: {map_id}")

        # Check if user has navigated away from login page
        # This indicates successful authentication
        # CalTopo redirects to map.html or other pages after successful login
        if ('caltopo.com' in url_string and
            ('/map.html' in url_string or
             '/app' in url_string or
             '/m/' in url_string or
             ('/login' not in url_string and '/accounts/login' not in url_string))):

            print("Login detected! Enabling Done button.")
            self.cookies_captured = True

    def on_manual_done_clicked(self):
        """Handle manual 'I'm Logged In' button click."""
        # We don't need to extract cookies anymore - JavaScript will use them automatically
        # Just emit the map ID
        cookies = {}
        if self.map_id:
            cookies['__map_id'] = self.map_id
            cookies['__map_url'] = self.map_url

        self.authenticated.emit(cookies)
        self.accept()

    def on_done_clicked(self):
        """Handle Done button click - extract cookies and close."""
        if not self.cookies_captured:
            QMessageBox.warning(
                self,
                "Not Logged In",
                "Please log in to CalTopo first before clicking Done."
            )
            return

        # Extract cookies from the web view
        # Note: QWebEngineCore cookie API is asynchronous
        # For simplicity, we'll extract cookies from the profile
        # A more robust implementation would use cookie_store signals

        # Alternative: Extract from page
        self.web_view.page().runJavaScript(
            "document.cookie",
            self.handle_cookies
        )

    def extract_all_cookies(self):
        """Extract ALL cookies including HttpOnly from the cookie store."""
        cookie_store = self.profile.cookieStore()
        self.collected_cookies = {}

        def on_cookie_added(cookie):
            """Called for each cookie in the store."""
            # Only capture caltopo.com cookies
            if 'caltopo.com' in cookie.domain():
                name = cookie.name().data().decode('utf-8')
                value = cookie.value().data().decode('utf-8')
                self.collected_cookies[name] = value
                print(f"DEBUG: Captured cookie: {name} = {value[:20]}...")

        # Connect to cookie added signal
        cookie_store.cookieAdded.connect(on_cookie_added)

        # Request all cookies
        cookie_store.loadAllCookies()

        # Wait a moment for cookies to be loaded
        from PySide6.QtCore import QTimer, QEventLoop
        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec()

        # Disconnect signal
        cookie_store.cookieAdded.disconnect(on_cookie_added)

        # Now emit with all collected cookies
        if self.collected_cookies:
            # Store map_id in cookies dict for the controller to access
            if self.map_id:
                self.collected_cookies['__map_id'] = self.map_id
                self.collected_cookies['__map_url'] = self.map_url

            print(f"DEBUG: Total cookies collected: {len(self.collected_cookies)}")
            print(f"DEBUG: Cookie names: {list(self.collected_cookies.keys())}")

            self.authenticated.emit(self.collected_cookies)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Authentication Failed",
                "Could not capture session cookies. Please try again."
            )

    def handle_cookies(self, cookie_string):
        """Handle cookies extracted from JavaScript.

        Args:
            cookie_string (str): Cookie string from document.cookie
        """
        # This method is deprecated - use extract_all_cookies instead
        # Kept for compatibility but redirects to new method
        self.extract_all_cookies()

    def get_map_id(self):
        """Get the extracted map ID.

        Returns:
            str: Map ID or None
        """
        return self.map_id
