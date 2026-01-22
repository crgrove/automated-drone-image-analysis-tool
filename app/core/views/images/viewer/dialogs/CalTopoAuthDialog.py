"""
CalTopoAuthDialog - Authentication dialog for CalTopo login.

This dialog provides an in-app browser for CalTopo authentication
using QWebEngineView with improved performance and UX.
"""

import sys
import traceback

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QProgressBar, QApplication
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QTimer, QEventLoop, QPoint, QSize
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
import os
import re
import json
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin


class CalTopoWebEnginePage(QWebEnginePage):
    """Custom QWebEnginePage that captures console messages."""

    def __init__(self, profile, parent, log_callback=None):
        """
        Initialize with optional log callback for displaying messages.

        Args:
            profile: QWebEngineProfile instance
            parent: Parent widget
            log_callback: Optional callback function for displaying log messages
        """
        super().__init__(profile, parent)
        self.logger = LoggerService()
        self.log_callback = log_callback

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """
        Capture JavaScript console messages and print them to Python console/terminal.

        Args:
            level: JavaScript console message level
            message: Message text
            lineNumber: Line number where message originated
            sourceID: Source file identifier
        """
        level_names = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }
        level_str = level_names.get(level, "LOG")

        # Log ALL console messages - no filtering
        output = f"[JS {level_str}] {message}"
        # self.logger.debug(output)

        if sourceID and lineNumber:
            # source_info = f"  Source: {sourceID}:{lineNumber}"
            # self.logger.debug(source_info)
            pass

        # Also call callback if provided (for UI display)
        if self.log_callback:
            self.log_callback(output)


class CalTopoAuthDialog(TranslationMixin, QDialog):
    """
    Dialog for CalTopo authentication.

    Displays CalTopo login page in an embedded browser and captures
    session cookies upon successful login.

    Improvements:
    - Lazy-loads web view for faster initial display
    - Proper window positioning relative to parent
    - WindowModal to prevent parent window movement
    - JavaScript-based cookie extraction (more reliable)
    - Cookie store fallback for HttpOnly cookies
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
        self.logger = LoggerService()
        self.setWindowTitle(self.tr("CalTopo Login & Map Selection"))
        self.setMinimumSize(800, 600)

        # Use WindowModal to prevent affecting parent window position
        self.setWindowModality(Qt.WindowModal)

        # Position dialog relative to parent window
        self._position_relative_to_parent()

        self.cookies_captured = False
        self.map_id = None
        self.map_url = None
        self.web_view = None
        self.profile = None
        self._web_view_loaded = False
        self._cookies_from_js = {}
        self._cookies_from_store = {}

        self.setup_ui()
        self._apply_translations()

        # Show dialog immediately (before web view loads)
        self.show()
        QApplication.processEvents()

        # Defer web view loading to avoid blocking
        QTimer.singleShot(100, self._lazy_load_web_view)

    def _position_relative_to_parent(self):
        """
        Position dialog centered on parent window's screen.

        Calculates the dialog position to center it on the parent window,
        ensuring it stays within screen bounds.
        """
        if self.parent():
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()

            # Get dialog size
            dialog_size = QSize(900, 700)

            # Center on parent
            dialog_pos = QPoint(
                parent_center.x() - dialog_size.width() // 2,
                parent_center.y() - dialog_size.height() // 2
            )

            # Ensure dialog stays on screen
            screen = self.parent().screen() if hasattr(self.parent(), 'screen') else None
            if screen:
                screen_geometry = screen.availableGeometry()
                dialog_pos.setX(max(screen_geometry.left(),
                                    min(dialog_pos.x(),
                                        screen_geometry.right() - dialog_size.width())))
                dialog_pos.setY(max(screen_geometry.top(),
                                    min(dialog_pos.y(),
                                        screen_geometry.bottom() - dialog_size.height())))

            self.move(dialog_pos)
            self.resize(dialog_size)

    def setup_ui(self):
        """
        Set up the dialog UI.

        Creates and arranges all UI elements including map info label,
        web view container, and action buttons.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Current map display with instructions
        map_info_layout = QHBoxLayout()
        map_info_layout.setContentsMargins(0, 0, 0, 0)

        self.current_map_label = QLabel(self.tr("Current map: Not selected"))
        self.current_map_label.setStyleSheet("padding: 5px; font-size: 11px; color: #666;")
        map_info_layout.addWidget(self.current_map_label)

        info_label = QLabel(self.tr("(Login → Navigate to your map → Click 'I'm Logged In')"))
        info_label.setStyleSheet("padding: 5px; font-size: 10px; color: #888;")
        map_info_layout.addWidget(info_label)
        map_info_layout.addStretch()

        layout.addLayout(map_info_layout)

        # Placeholder for web view (will be added when loaded)
        self.web_view_container = QVBoxLayout()
        layout.addLayout(self.web_view_container, 1)

        # Button row
        button_layout = QHBoxLayout()

        self.manual_done_button = QPushButton(self.tr("I'm Logged In - Export Data"))
        self.manual_done_button.clicked.connect(self.on_manual_done_clicked)
        self.manual_done_button.setToolTip(self.tr("Click this after logging in and navigating to your map"))
        self.manual_done_button.setEnabled(False)  # Disabled until web view loads

        self.cancel_button = QPushButton(self.tr("Cancel"))
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.manual_done_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _lazy_load_web_view(self):
        """
        Lazy-load the web view to avoid blocking dialog display.

        Creates the QWebEngineView with persistent profile for cookie storage,
        sets up cookie monitoring, and loads the CalTopo login page.
        """
        if self._web_view_loaded:
            return

        self._web_view_loaded = True

        try:
            # Create persistent profile for cookies

            profile_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
                "CalTopoProfile"
            )
            self.profile = QWebEngineProfile("CalTopoProfile")
            self.profile.setPersistentStoragePath(profile_path)
            self.profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )

            # Monitor cookies as they're added
            cookie_store = self.profile.cookieStore()
            cookie_store.cookieAdded.connect(self._on_cookie_added)

            # Create web view
            self.web_view = QWebEngineView()

            # Set the profile on a new page with console message capturing
            page = CalTopoWebEnginePage(self.profile, self.web_view)
            self.web_view.setPage(page)

            # Monitor URL changes to detect successful login and map selection
            self.web_view.urlChanged.connect(self.on_url_changed)

            # Monitor load progress
            self.web_view.loadProgress.connect(self._on_load_progress)
            self.web_view.loadFinished.connect(self._on_load_finished)

            # Add to layout
            self.web_view_container.addWidget(self.web_view)

            # Load CalTopo
            self.web_view.setUrl(QUrl("https://caltopo.com/map.html"))

            # Enable button once web view is ready
            QTimer.singleShot(1000, lambda: self.manual_done_button.setEnabled(True))

        except Exception as e:
            self.logger.error(f"ERROR: Failed to initialize web view: {e}")
            self.logger.error(traceback.format_exc())
            QMessageBox.critical(
                self,
                self.tr("Initialization Error"),
                self.tr("Failed to initialize CalTopo browser:\n{error}").format(error=str(e))
            )

    def _on_cookie_added(self, cookie):
        """
        Called when a cookie is added to the store.

        Args:
            cookie: QNetworkCookie instance that was added.

        Tracks CalTopo-related cookies for later extraction.
        """
        domain = cookie.domain()

        # Track all caltopo.com cookies (including .caltopo.com with leading dot)
        # Both 'caltopo.com' and '.caltopo.com' are valid
        if 'caltopo.com' in domain or domain == '' or not domain:
            cookie_dict = self._cookie_to_dict(cookie)
            key = (cookie_dict['name'], cookie_dict['domain'], cookie_dict['path'])
            self._cookies_from_store[key] = cookie_dict

    def _on_load_progress(self, progress):
        """
        Handle web view load progress.

        Args:
            progress: Load progress percentage (0-100).
        """
        # Just monitor progress, no UI updates needed
        pass

    def _on_load_finished(self, success):
        """
        Handle web view load completion.

        Args:
            success: True if page loaded successfully, False otherwise.

        Shows a warning message if the page failed to load.
        """
        if not success:
            QMessageBox.warning(
                self,
                self.tr("Failed to Load"),
                self.tr(
                    "Failed to load CalTopo. Please check your internet connection and try again."
                )
            )

    def on_url_changed(self, url):
        """Handle URL changes to detect successful login and extract map ID.

        Args:
            url (QUrl): New URL
        """
        url_string = url.toString()

        # Extract map ID from URL
        map_id = None
        if '#' in url_string and 'id=' in url_string:
            match = re.search(r'[#&]id=([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)
        elif '/m/' in url_string:
            match = re.search(r'/m/([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)
        elif '/map/' in url_string:
            match = re.search(r'/map/([A-Z0-9]+)', url_string, re.IGNORECASE)
            if match:
                map_id = match.group(1)

        if map_id:
            self.map_id = map_id
            self.map_url = url_string
            self.current_map_label.setText(
                self.tr("Current map: {map_id}").format(map_id=map_id)
            )
            self.current_map_label.setStyleSheet(
                "padding: 5px; font-size: 11px; color: #2E7D32; font-weight: bold;"
            )

    def on_manual_done_clicked(self):
        """
        Handle manual 'I'm Logged In' button click.

        Validates that a map is selected and the web view is ready,
        then triggers cookie extraction after a short delay to ensure
        cookies are set.
        """
        if not self.map_id:
            QMessageBox.warning(
                self,
                self.tr("No Map Selected"),
                self.tr(
                    "Please navigate to a CalTopo map before capturing the session.\n\n"
                    "The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123)."
                )
            )
            return

        if not self.web_view:
            QMessageBox.warning(
                self,
                self.tr("Browser Not Ready"),
                self.tr("The CalTopo browser is still loading. Please wait a moment and try again.")
            )
            return

        # Disable button and show progress
        self.manual_done_button.setEnabled(False)
        self.manual_done_button.setText(self.tr("Starting export..."))
        QApplication.processEvents()

        # Wait a moment to ensure cookies are set, then extract
        # This is important because cookies might be set asynchronously
        QTimer.singleShot(1000, self.extract_all_cookies)

    def extract_all_cookies(self):
        """
        Extract ALL cookies using JavaScript and cookie store.

        Combines cookies from both JavaScript (document.cookie) and
        the cookie store (including HttpOnly cookies). Emits the
        authenticated signal with the collected cookies and map information.
        """
        if not self.profile or not self.web_view:
            QMessageBox.warning(
                self,
                self.tr("Authentication Failed"),
                self.tr("Browser not initialized. Please try again.")
            )
            self._reset_button()
            return

        # Reset JS cookies, but preserve store cookies (they were collected via cookieAdded signal)
        self._cookies_from_js = {}

        # Step 1: Get cookies via JavaScript and trigger a request to force cookie loading
        # Making a fetch request will cause the browser to send all cookies (including HttpOnly)
        # This should trigger cookieAdded signals for any cookies that weren't already captured
        js_code = """
        (function() {
            var result = {
                cookies: {},
                isLoggedIn: false
            };

            // Get accessible cookies
            if (document.cookie) {
                document.cookie.split(';').forEach(function(cookie) {
                    var parts = cookie.trim().split('=');
                    if (parts.length >= 2) {
                        var name = parts[0].trim();
                        var value = parts.slice(1).join('=').trim();
                        result.cookies[name] = value;
                    }
                });
            }

            // Check if user appears to be logged in
            if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.user) {
                result.isLoggedIn = true;
            } else if (document.querySelector('[data-user-id]') || document.querySelector('.user-menu')) {
                result.isLoggedIn = true;
            } else if (window.location.pathname.includes('/m/') && !window.location.pathname.includes('/login')) {
                result.isLoggedIn = true;
            }

            // Trigger a request to force all cookies to be sent/loaded
            // This will cause HttpOnly cookies to be processed by the cookie store
            fetch('/api/v1/account/maps', {
                method: 'GET',
                credentials: 'include',
                cache: 'no-cache'
            }).catch(function(e) {
                // Ignore errors - we just want to trigger cookie processing
            });

            return JSON.stringify(result);
        })();
        """

        def on_js_result(result):
            """Process JavaScript cookie extraction result."""
            try:
                if result:
                    js_data = json.loads(result)
                    js_cookies = js_data.get('cookies', {})

                    for name, value in js_cookies.items():
                        # Create cookie dict from JS cookies
                        cookie_dict = {
                            'name': name,
                            'value': value,
                            'domain': '.caltopo.com',
                            'path': '/',
                            'secure': True,
                            'expires': None,
                            'rest': {},
                            'version': 0,
                            'port': None,
                            'port_specified': False,
                            'domain_initial_dot': True,
                            'domain_specified': True,
                            'path_specified': True,
                            'discard': True,
                            'comment': None,
                            'comment_url': None
                        }
                        key = (name, '.caltopo.com', '/')
                        self._cookies_from_js[key] = cookie_dict
            except (json.JSONDecodeError, Exception):
                pass

            # Step 2: Get cookies from cookie store (includes HttpOnly)
            self._extract_cookies_from_store()

        # Execute JavaScript to get cookies
        self.web_view.page().runJavaScript(js_code, on_js_result)

    def _extract_cookies_from_store(self):
        """
        Extract cookies from the cookie store (includes HttpOnly cookies).

        Uses loadAllCookies() to trigger cookieAdded signals for all
        existing cookies, then combines them with JavaScript-extracted cookies.
        """
        cookie_store = self.profile.cookieStore()
        loop = QEventLoop()
        cookies_loaded = False
        new_cookies_count = 0

        def on_cookie_added_during_load(cookie):
            """Called when loadAllCookies triggers cookieAdded for existing cookies."""
            nonlocal new_cookies_count
            domain = cookie.domain()

            # Track all caltopo.com cookies (including .caltopo.com with leading dot)
            if 'caltopo.com' in domain or domain == '' or not domain:
                cookie_dict = self._cookie_to_dict(cookie)
                key = (cookie_dict['name'], cookie_dict['domain'], cookie_dict['path'])
                if key not in self._cookies_from_store:
                    self._cookies_from_store[key] = cookie_dict
                    new_cookies_count += 1

        def finish_loading():
            """Finish loading cookies."""
            nonlocal cookies_loaded
            cookies_loaded = True
            if loop.isRunning():
                loop.quit()

        # Connect to cookieAdded to capture cookies when loadAllCookies triggers them
        cookie_store.cookieAdded.connect(on_cookie_added_during_load)

        # Use loadAllCookies to trigger cookieAdded for all existing cookies
        cookie_store.loadAllCookies()

        # Also try to access cookies by making a request that will cause them to be processed
        # The JavaScript fetch request should trigger cookie processing
        # Wait a bit for the fetch request and cookie processing
        QTimer.singleShot(1500, finish_loading)

        # Also set a timeout
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(finish_loading)
        timeout_timer.start(3000)

        # Process events and wait
        QApplication.processEvents()
        loop.exec()
        timeout_timer.stop()

        # Disconnect the temporary handler
        try:
            cookie_store.cookieAdded.disconnect(on_cookie_added_during_load)
        except Exception:
            pass

        # Combine cookies from both sources (store takes precedence for duplicates)
        all_cookies = {}
        all_cookies.update(self._cookies_from_js)
        all_cookies.update(self._cookies_from_store)  # Store cookies override JS cookies

        cookie_list = list(all_cookies.values())

        # Validate we got cookies
        if not cookie_list:
            QMessageBox.warning(
                self,
                self.tr("Authentication Failed"),
                self.tr(
                    "Could not capture session cookies. Please ensure you are logged in to CalTopo.\n\n"
                    "Try:\n"
                    "1. Make sure you're logged in\n"
                    "2. Navigate to a map\n"
                    "3. Wait a few seconds for cookies to be set\n"
                    "4. Click 'I'm Logged In' again"
                )
            )
            self._reset_button()
            return

        # Emit with collected cookies
        payload = {
            'cookies': cookie_list,
            'map_id': self.map_id,
            'map_url': self.map_url
        }

        self.authenticated.emit(payload)
        self.accept()

    def _reset_button(self):
        """
        Reset the button to its original state.

        Re-enables the manual done button and restores its original text.
        """
        self.manual_done_button.setEnabled(True)
        self.manual_done_button.setText("I'm Logged In - Export Data")

    def get_map_id(self):
        """Get the extracted map ID.

        Returns:
            str: Map ID or None
        """
        return self.map_id

    def _cookie_to_dict(self, cookie):
        """
        Convert QNetworkCookie to a serializable dict.

        Args:
            cookie: QNetworkCookie instance to convert.

        Returns:
            dict: Dictionary containing all cookie attributes in a format
                compatible with the requests library.
        """
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        domain = cookie.domain() or 'caltopo.com'
        path = cookie.path() or '/'

        # Normalize domain - remove leading dot for requests library compatibility
        # Store the original format in domain_initial_dot
        domain_has_dot = domain.startswith('.')
        if domain_has_dot:
            domain_normalized = domain[1:]  # Remove leading dot
        else:
            domain_normalized = domain

        expires = None
        if not cookie.isSessionCookie():
            expiration = cookie.expirationDate()
            if expiration.isValid():
                expires = expiration.toSecsSinceEpoch()

        return {
            'name': name,
            'value': value,
            'domain': domain_normalized,  # Store without leading dot for requests
            'path': path,
            'secure': cookie.isSecure(),
            'expires': expires,
            'rest': {'HttpOnly': cookie.isHttpOnly()},
            'version': 0,
            'port': None,
            'port_specified': False,
            'domain_initial_dot': domain_has_dot,  # Remember original format
            'domain_specified': bool(domain),
            'path_specified': bool(path),
            'discard': cookie.isSessionCookie(),
            'comment': None,
            'comment_url': None
        }
