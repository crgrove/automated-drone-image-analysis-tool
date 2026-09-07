"""
UI file for StreamViewerWindow - Main streaming detection window.

This UI provides the container for streaming algorithms, similar to how
MainWindow_ui.py provides the container for image analysis algorithms.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QSplitter, QGroupBox, QTextEdit, QStatusBar, QLabel)
from PySide6.QtCore import QCoreApplication, Qt

from core.views.components.CollapsibleSection import CollapsibleSection
from core.views.components.SteadyScrollArea import SteadyScrollArea


class Ui_StreamViewerWindow:
    """UI for the main streaming detection window."""
    
    def setupUi(self, StreamViewerWindow):
        """Setup the streaming viewer window UI."""
        if not StreamViewerWindow.objectName():
            StreamViewerWindow.setObjectName("StreamViewerWindow")
        
        StreamViewerWindow.resize(1600, 900)
        # Allow the window to fit on smaller displays while keeping a sensible default
        StreamViewerWindow.setMinimumSize(800, 600)
        
        # Central widget
        self.centralwidget = QWidget(StreamViewerWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Main layout
        main_layout = QHBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        
        # Left panel - Video display area
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # Video display placeholder
        self.videoLabel = QLabel("Video Stream")
        self.videoLabel.setObjectName("videoLabel")
        self.videoLabel.setAlignment(Qt.AlignCenter)
        self.videoLabel.setStyleSheet("QLabel { background-color: #000; color: #fff; }")
        # Use a smaller minimum so the layout can shrink on low‑resolution screens
        self.videoLabel.setMinimumSize(400, 300)
        left_layout.addWidget(self.videoLabel, 1)
        
        # Playback control placeholder (will be replaced with actual widget)
        self.playbackControlWidget = QWidget()
        self.playbackControlWidget.setObjectName("playbackControlWidget")
        self.playbackControlWidget.setMaximumHeight(80)
        left_layout.addWidget(self.playbackControlWidget)
        
        # Thumbnail placeholder
        self.thumbnailWidget = QWidget()
        self.thumbnailWidget.setObjectName("thumbnailWidget")
        self.thumbnailWidget.setMaximumHeight(120)
        left_layout.addWidget(self.thumbnailWidget)
        
        # Info panel
        self.infoPanel = QTextEdit()
        self.infoPanel.setObjectName("infoPanel")
        self.infoPanel.setReadOnly(True)
        self.infoPanel.setMaximumHeight(100)
        left_layout.addWidget(self.infoPanel)
        
        self.splitter.addWidget(left_panel)
        
        # Right panel - Control area (wrapped in a scroll area so controls are not cut off)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Stream controls group. Collapsible: it matters during setup and
        # mostly just takes room once a source is running.
        self.streamControlGroup = CollapsibleSection("Stream Controls")
        self.streamControlGroup.setObjectName("streamControlGroup")

        # Stream control placeholder
        self.streamControlPlaceholder = QWidget()
        self.streamControlPlaceholder.setObjectName("streamControlPlaceholder")
        self.streamControlGroup.addWidget(self.streamControlPlaceholder)

        right_layout.addWidget(self.streamControlGroup)

        # Map. Lives here rather than under the video because the left pane
        # is wide and short — a map there ends up a useless letterbox strip.
        # Collapsible for the operators who do not want it at all.
        self.mapGroup = CollapsibleSection("Map")
        self.mapGroup.setObjectName("mapGroup")
        self.mapPlaceholder = QWidget()
        self.mapPlaceholder.setObjectName("mapPlaceholder")
        self.mapPlaceholder.setMinimumHeight(280)
        self.mapGroup.addWidget(self.mapPlaceholder)
        right_layout.addWidget(self.mapGroup)

        # Algorithm controls placeholder (will be replaced with loaded algorithm)
        self.algorithmControlGroup = QGroupBox("Algorithm Controls")
        self.algorithmControlGroup.setObjectName("algorithmControlGroup")
        self.algorithmControlLayout = QVBoxLayout(self.algorithmControlGroup)
        self.algorithmControlLayout.setObjectName("algorithmControlLayout")

        # Placeholder widget for algorithm
        self.algorithmControlPlaceholder = QWidget()
        self.algorithmControlPlaceholder.setObjectName("algorithmControlPlaceholder")
        self.algorithmControlLayout.addWidget(self.algorithmControlPlaceholder)

        right_layout.addWidget(self.algorithmControlGroup)
        
        # Recording group placeholder
        self.recordingGroup = QGroupBox("Recording")
        self.recordingGroup.setObjectName("recordingGroup")
        self.recordingLayout = QVBoxLayout(self.recordingGroup)
        self.recordingLayout.setObjectName("recordingLayout")
        self.recordingPlaceholder = QWidget()
        self.recordingPlaceholder.setObjectName("recordingPlaceholder")
        self.recordingLayout.addWidget(self.recordingPlaceholder)
        right_layout.addWidget(self.recordingGroup)
        
        right_layout.addStretch()
        
        # Wrap the right control panel in a scroll area to keep all controls
        # reachable. SteadyScrollArea (not QScrollArea) so the panel does not
        # scroll away when a control disables itself and hands off focus.
        right_scroll = SteadyScrollArea()
        right_scroll.setObjectName("rightScrollArea")
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_panel)
        
        self.splitter.addWidget(right_scroll)
        
        # Set splitter initial sizes (70% left, 30% right)
        self.splitter.setSizes([700, 300])
        
        main_layout.addWidget(self.splitter)
        
        StreamViewerWindow.setCentralWidget(self.centralwidget)
        
        # Status bar
        self.statusbar = QStatusBar(StreamViewerWindow)
        self.statusbar.setObjectName("statusbar")
        StreamViewerWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(StreamViewerWindow)
    
    def retranslateUi(self, StreamViewerWindow):
        """Set UI text/translations."""
        # QCoreApplication.translate spelled out at every call site, not
        # bound to a local alias. pyside6-lupdate matches the call
        # syntactically, so an alias makes every string here invisible to
        # extraction - which is how this window's own title and its four
        # group headings ended up with no catalog entry in any language
        # while the file looked correct. Generated *_ui.py files write it
        # out in full for the same reason; match them.
        StreamViewerWindow.setWindowTitle(QCoreApplication.translate("StreamViewerWindow", "ADIAT - Real-Time Stream Detection"))
        self.videoLabel.setText(QCoreApplication.translate("StreamViewerWindow", "Video Stream"))
        self.streamControlGroup.setTitle(QCoreApplication.translate("StreamViewerWindow", "Stream Controls"))
        self.mapGroup.setTitle(QCoreApplication.translate("StreamViewerWindow", "Map"))
        self.algorithmControlGroup.setTitle(QCoreApplication.translate("StreamViewerWindow", "Algorithm Controls"))
        self.recordingGroup.setTitle(QCoreApplication.translate("StreamViewerWindow", "Recording"))
        self.infoPanel.setPlaceholderText(QCoreApplication.translate("StreamViewerWindow", "Stream information and logs will appear here..."))

