"""
UI file for StreamViewerWindow - Main streaming detection window.

This UI provides the container for streaming algorithms, similar to how
MainWindow_ui.py provides the container for image analysis algorithms.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QSplitter, QGroupBox, QTextEdit, QStatusBar, QLabel,
                               QScrollArea)
from PySide6.QtCore import Qt


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
        
        # Stream controls group
        streamControlGroup = QGroupBox("Stream Controls")
        streamControlGroup.setObjectName("streamControlGroup")
        streamControlLayout = QVBoxLayout(streamControlGroup)
        
        # Stream control placeholder
        self.streamControlPlaceholder = QWidget()
        self.streamControlPlaceholder.setObjectName("streamControlPlaceholder")
        streamControlLayout.addWidget(self.streamControlPlaceholder)
        
        right_layout.addWidget(streamControlGroup)
        
        # Algorithm controls placeholder (will be replaced with loaded algorithm)
        algorithmControlGroup = QGroupBox("Algorithm Controls")
        algorithmControlGroup.setObjectName("algorithmControlGroup")
        self.algorithmControlLayout = QVBoxLayout(algorithmControlGroup)
        self.algorithmControlLayout.setObjectName("algorithmControlLayout")
        
        # Placeholder widget for algorithm
        self.algorithmControlPlaceholder = QWidget()
        self.algorithmControlPlaceholder.setObjectName("algorithmControlPlaceholder")
        self.algorithmControlLayout.addWidget(self.algorithmControlPlaceholder)
        
        right_layout.addWidget(algorithmControlGroup)
        
        # Recording group placeholder
        self.recordingGroup = QGroupBox("Recording")
        self.recordingGroup.setObjectName("recordingGroup")
        self.recordingLayout = QVBoxLayout(self.recordingGroup)
        self.recordingLayout.setObjectName("recordingLayout")
        self.recordingPlaceholder = QWidget()
        self.recordingPlaceholder.setObjectName("recordingPlaceholder")
        self.recordingLayout.addWidget(self.recordingPlaceholder)
        right_layout.addWidget(self.recordingGroup)
        
        # Stats group
        statsGroup = QGroupBox("Statistics")
        statsGroup.setObjectName("statsGroup")
        statsLayout = QVBoxLayout(statsGroup)
        
        self.statsLabel = QLabel("No stream connected")
        self.statsLabel.setObjectName("statsLabel")
        self.statsLabel.setWordWrap(True)
        statsLayout.addWidget(self.statsLabel)
        
        right_layout.addWidget(statsGroup)
        
        right_layout.addStretch()
        
        # Wrap the right control panel in a scroll area to keep all controls reachable
        right_scroll = QScrollArea()
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
        StreamViewerWindow.setWindowTitle("ADIAT - Real-Time Stream Detection")
        self.infoPanel.setPlaceholderText("Stream information and logs will appear here...")
        self.statsLabel.setText("No stream connected")

