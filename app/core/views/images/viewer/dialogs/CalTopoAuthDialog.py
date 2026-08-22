"""
CalTopoAuthDialog - Authentication dialog for CalTopo login.

This dialog provides an in-app browser for CalTopo authentication
using QWebEngineView with improved performance and UX.
"""

import traceback

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QApplication
from PySide6.QtCore import Qt, Signal, QUrl, QStandardPaths, QTimer, QPoint, QSize
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
import os
import re
import json
import shutil
import sqlite3
import tempfile
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
        # Only errors are worth recording. CalTopo's own page emits a steady
        # stream of info/warning chatter (deprecated Google Maps APIs, resize
        # observer notices) that buries anything useful.
        if level != QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            return

        output = f"[JS ERROR] {message}"
        if sourceID and lineNumber:
            output += f" ({sourceID}:{lineNumber})"
        self.logger.warning(output)

        # Also call callback if provided (for UI display)
        if self.log_callback:
            self.log_callback(output)


class CalTopoAuthDialog(TranslationMixin, QDialog):
    """
    Dialog for CalTopo authentication.

    Displays the CalTopo login page in an embedded browser and captures the
    session once the user has signed in and opened a map. This dialog is a
    login surface only - the export itself runs over plain HTTP using the
    captured session, not inside the page.

    Cookies are merged from three sources in increasing order of freshness:
    the profile's on-disk store (the only source for a restored HttpOnly
    session), document.cookie, and the live cookieAdded stream.
    """

    # Signal emitted when authentication is successful
    authenticated = Signal(dict)  # Emits cookies dictionary

    # One profile for the whole application run. A per-dialog profile is torn
    # down with its dialog, taking the logged-in session with it, so a second
    # export in the same run had to authenticate again. Holding it at class
    # level also satisfies Qt's requirement that a profile outlive the pages
    # using it.
    _shared_profile = None

    # cookieAdded fires once, when a cookie is set. A second export in the same
    # run builds a new dialog, which would otherwise start with an empty view of
    # a session captured by the first one, so this accumulates at class level
    # alongside the profile that owns it.
    _cookies_from_store = {}

    # Name of the cookie that actually carries the CalTopo session.
    SESSION_COOKIE_NAME = "SESSION"

    # Snapshot of the persisted cookies, taken once before the profile opens.
    #
    # cookieAdded reports cookies as they are SET - including HttpOnly ones, so
    # a sign-in performed in this window is captured normally. What it never
    # reports is a cookie RESTORED from a previous run (measured: 0 of 35, and
    # loadAllCookies() adds nothing), which is exactly the state a returning
    # user is in. Reading the store covers that, and it has to happen here:
    # while a profile is live Chromium holds the file with no sharing at all -
    # copy, plain read, sqlite read-only and a full-sharing Win32 CreateFileW
    # all fail with a sharing violation.
    _disk_cookies = {}

    @classmethod
    def _get_shared_profile(cls):
        """Return the application-wide CalTopo browser profile, creating it once.

        Returns:
            QWebEngineProfile: Profile with on-disk cookie persistence enabled.
        """
        if cls._shared_profile is None:
            app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            profile_path = os.path.join(app_data, "CalTopoProfile")
            # Chromium manages its own directory layout under the cache path and
            # will try to migrate anything it finds there. Pointing it at the
            # storage directory produces "Unable to move the cache: Access is
            # denied", so the two get separate locations.
            cache_path = os.path.join(app_data, "CalTopoProfileCache")
            os.makedirs(profile_path, exist_ok=True)
            os.makedirs(cache_path, exist_ok=True)

            # Read the persisted cookies BEFORE the profile opens the store.
            # Once it does, the file cannot be opened by anything until the
            # profile is destroyed (see _disk_cookies).
            cls._disk_cookies = cls._read_persisted_cookies(profile_path)

            profile = QWebEngineProfile("CalTopoProfile")
            profile.setPersistentStoragePath(profile_path)
            profile.setCachePath(cache_path)
            # CalTopo's login cookies are session cookies; without Force they
            # are dropped on exit and the login never survives a restart.
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            cls._shared_profile = profile

        return cls._shared_profile

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
        self.account_id = None
        self.web_view = None
        self.profile = None
        self._web_view_loaded = False
        self._cookies_from_js = {}
        self._cookie_monitor_connected = False

        self.setup_ui()
        self._apply_translations()

        # Show dialog immediately (before web view loads)
        self.show()
        QApplication.processEvents()

        # Build the web view NOW, not on a timer. Attaching a QWebEngineView
        # forces native-window re-creation on this dialog, and Qt delivers a
        # Hide event when that happens. If it lands inside a modal loop,
        # QDialog::setVisible(False) exits that loop: exec() returned Rejected
        # a fraction of a second after being called, before the user had done
        # anything, and the caller then abandoned the export while the login
        # window stayed on screen.
        self._lazy_load_web_view()
        QApplication.processEvents()

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
        self.current_map_label.setStyleSheet("padding: 5px; font-size: 11px; color: palette(placeholder-text);")
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

        # Buttons in a QDialog are autoDefault by default, so pressing Return
        # while typing into the CalTopo login form fired "I'm Logged In"
        # instead of submitting the form - which then complained that no map
        # was selected. The page owns the Return key here, not this dialog.
        for button in (self.manual_done_button, self.cancel_button):
            button.setAutoDefault(False)
            button.setDefault(False)

        button_layout.addStretch()
        button_layout.addWidget(self.manual_done_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def keyPressEvent(self, event):
        """Keep Return/Enter inside the web page instead of closing the dialog.

        QDialog treats Return as "activate the default button". In a dialog
        whose whole purpose is an embedded login form, that hijacks the key the
        user is pressing to submit their password.

        Args:
            event: The QKeyEvent being delivered.
        """
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.accept()
            return
        super().keyPressEvent(event)

    def done(self, result):
        """Drop the shared cookie store connection before closing.

        Args:
            result: QDialog result code.
        """
        self._disconnect_cookie_monitor()
        super().done(result)

    def _disconnect_cookie_monitor(self):
        """Detach this dialog from the shared profile's cookie store."""
        if not self._cookie_monitor_connected:
            return
        self._cookie_monitor_connected = False
        try:
            self.profile.cookieStore().cookieAdded.disconnect(self._on_cookie_added)
        except (RuntimeError, TypeError):
            # Already gone; nothing to detach.
            pass

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
            # Reuse the application-wide profile so an existing login is still
            # in effect (see _get_shared_profile).
            self.profile = self._get_shared_profile()

            # Monitor cookies as they're added. The store is shared, so this
            # connection must be dropped when the dialog closes (see done()),
            # otherwise every export leaves another dead receiver behind.
            cookie_store = self.profile.cookieStore()
            cookie_store.cookieAdded.connect(self._on_cookie_added)
            self._cookie_monitor_connected = True

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
            # Class-level store: see SESSION_COOKIE_NAME above.
            CalTopoAuthDialog._cookies_from_store[key] = cookie_dict

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
        # Re-read the address bar now. Relying solely on urlChanged means a map
        # that was already open, or reached by a route that did not emit the
        # signal, is never noticed - and the export then refuses with "No Map
        # Selected" while the user is plainly looking at their map.
        if self.web_view is not None:
            self.on_url_changed(self.web_view.url())

        if not self.map_id:
            self.logger.warning(
                f"CalTopo login: no map ID found in the current URL "
                f"({self.web_view.url().toString() if self.web_view else 'no web view'})"
            )
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
                isLoggedIn: false,
                accountId: ''
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

            // CalTopo exposes the signed-in account on the global `sarsoft`
            // object. Media uploads must be attributed to that id; the
            // properties probed here previously (__INITIAL_STATE__, .user-menu)
            // do not exist on CalTopo, so nothing was ever learned.
            try {
                if (typeof sarsoft !== 'undefined' && sarsoft.account) {
                    result.isLoggedIn = true;
                    result.accountId = sarsoft.account.id || '';
                }
            } catch (e) {
                // Leave accountId empty; the caller falls back.
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
                    self.account_id = js_data.get('accountId') or None
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

            # Step 2: Get cookies from cookie store (includes HttpOnly).
            #
            # Deferred to a fresh event-loop turn on purpose. This function is
            # a runJavaScript reply callback, and while that stack is live the
            # browser process runs no further tasks: cookieAdded is never
            # delivered, loadAllCookies() reports nothing, and the fetch() this
            # script just issued to force HttpOnly cookie processing never even
            # reaches the network. Doing the work here made cookie capture
            # depend on luck, and any real work done here deadlocks outright.
            QTimer.singleShot(0, self._extract_cookies_from_store)

        # Execute JavaScript to get cookies
        self.web_view.page().runJavaScript(js_code, on_js_result)

    def _extract_cookies_from_store(self):
        """
        Ask the cookie store to replay everything it holds, then finish.

        The persistent ``cookieAdded`` connection made when the view was built
        records cookies as they arrive; ``loadAllCookies`` re-announces any that
        predate it. Completion is a plain timer continuation rather than a
        nested event loop: the previous version could wedge if its two timers
        both fired before ``loop.exec()`` was reached, because each checked
        ``loop.isRunning()`` and skipped ``quit()``.
        """
        self.profile.cookieStore().loadAllCookies()
        QTimer.singleShot(1500, self._finish_cookie_capture)

    # Chromium timestamps are microseconds since 1601-01-01.
    _CHROMIUM_EPOCH_OFFSET_SECONDS = 11644473600

    def _cookies_from_disk(self):
        """Return the snapshot of persisted cookies taken before the profile opened.

        Returns:
            dict: {(name, domain, path): cookie_dict} for caltopo.com cookies.
        """
        return dict(type(self)._disk_cookies)

    @classmethod
    def _read_persisted_cookies(cls, storage_path):
        """Read CalTopo cookies out of a profile's on-disk cookie store.

        This is the equivalent of Android's CookieManager.getCookie(url), which
        the reference implementation relies on. Qt has no getter:
        QWebEngineCookieStore announces cookies only as they are *set*, and
        loadAllCookies() delivers nothing for cookies restored from disk
        (measured: 0 of 35 on a real profile). CalTopo's SESSION cookie is also
        HttpOnly, so document.cookie cannot see it - which left a returning,
        already-logged-in user holding nothing but analytics cookies.

        MUST be called before a QWebEngineProfile opens this directory: while
        one is live the file cannot be opened by any means.

        QtWebEngine writes cookie values in plaintext, so no decryption is
        needed; any encrypted row is skipped rather than guessed at.

        Args:
            storage_path (str): The profile's persistent storage directory.

        Returns:
            dict: {(name, domain, path): cookie_dict} for caltopo.com cookies.
        """
        logger = LoggerService()
        cookies = {}
        if not storage_path:
            return cookies

        source = os.path.join(storage_path, "Cookies")
        if not os.path.exists(source):
            logger.warning(f"CalTopo login: no cookie store at {source}")
            return cookies

        # Work on a copy: SQLite would otherwise create journal files inside
        # the live profile directory.
        temp_dir = tempfile.mkdtemp(prefix="adiat-caltopo-cookies-")
        try:
            copy_path = os.path.join(temp_dir, "Cookies")
            shutil.copy2(source, copy_path)

            connection = sqlite3.connect(copy_path)
            try:
                rows = connection.execute(
                    "SELECT host_key, name, value, encrypted_value, path, "
                    "is_secure, is_httponly, expires_utc FROM cookies"
                ).fetchall()
            finally:
                connection.close()

            skipped_encrypted = 0
            for host_key, name, value, encrypted_value, path, secure, httponly, expires in rows:
                if 'caltopo.com' not in (host_key or ''):
                    continue
                if not value and encrypted_value:
                    skipped_encrypted += 1
                    continue

                domain_has_dot = (host_key or '').startswith('.')
                domain = host_key[1:] if domain_has_dot else host_key

                expires_seconds = None
                if expires:
                    expires_seconds = int(expires / 1_000_000) - cls._CHROMIUM_EPOCH_OFFSET_SECONDS

                cookies[(name, domain, path or '/')] = {
                    'name': name,
                    'value': value,
                    'domain': domain,
                    'path': path or '/',
                    'secure': bool(secure),
                    'expires': expires_seconds,
                    'rest': {'HttpOnly': bool(httponly)},
                    'version': 0,
                    'port': None,
                    'port_specified': False,
                    'domain_initial_dot': domain_has_dot,
                    'domain_specified': bool(domain),
                    'path_specified': True,
                    'discard': expires_seconds is None,
                    'comment': None,
                    'comment_url': None,
                }

            if skipped_encrypted:
                logger.warning(
                    f"CalTopo login: skipped {skipped_encrypted} encrypted cookie value(s)"
                )
        except (OSError, sqlite3.Error) as e:
            logger.warning(f"CalTopo login: could not read the cookie store: {e}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        return cookies

    def _finish_cookie_capture(self):
        """Combine the captured cookies and hand them to the caller."""
        # Disk first (the only source for a restored HttpOnly session), then
        # the live sources, which are fresher and so take precedence.
        disk_cookies = self._cookies_from_disk()

        all_cookies = {}
        all_cookies.update(disk_cookies)
        all_cookies.update(self._cookies_from_js)
        all_cookies.update(self._cookies_from_store)

        cookie_list = list(all_cookies.values())

        # Require the actual session cookie. Any other cookie makes the list
        # non-empty while authenticating as nobody, which previously sailed
        # through this gate and produced a run of silent 401s.
        if not any(cookie['name'] == self.SESSION_COOKIE_NAME for cookie in cookie_list):
            self.logger.warning(
                f"CalTopo login: no '{self.SESSION_COOKIE_NAME}' cookie was captured, so the "
                f"session is not usable. Got {sorted(c['name'] for c in cookie_list)} "
                f"({len(disk_cookies)} from disk, {len(self._cookies_from_store)} from the "
                f"store, {len(self._cookies_from_js)} from JS)."
            )
            QMessageBox.warning(
                self,
                self.tr("Authentication Failed"),
                self.tr(
                    "Could not read your CalTopo session.\n\n"
                    "Make sure you are signed in to CalTopo in this window and have "
                    "opened your map, then click 'I'm Logged In - Export Data' again."
                )
            )
            self._reset_button()
            return

        # Emit with collected cookies
        payload = {
            'cookies': cookie_list,
            'map_id': self.map_id,
            'map_url': self.map_url,
            'account_id': self.account_id
        }

        # The receiver decides whether the payload is usable and accepts the
        # dialog itself. Accepting unconditionally closed the dialog even when
        # the payload was rejected (no map selected), and exec() then returned
        # Accepted, so the caller bailed out with no explanation at all.
        self.authenticated.emit(payload)
        if self.result() != QDialog.Accepted:
            self.logger.warning(
                "CalTopo login: the session was captured but the caller did not accept it "
                "(usually no map ID). The dialog stays open so you can navigate to a map."
            )
            self._reset_button()

    def _reset_button(self):
        """
        Reset the button to its original state.

        Re-enables the manual done button and restores its original text.
        """
        self.manual_done_button.setEnabled(True)
        self.manual_done_button.setText(self.tr("I'm Logged In - Export Data"))

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
