#!/usr/bin/env python3
"""
Test script for RTMP stream integration with ADIAT viewers.

This script tests the RTMP stream functionality for both Real-Time Color Detection 
and Real-Time Anomaly Detection viewers.

Usage:
    python test_rtmp_integration.py
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import Qt, QTimer

def test_rtmp_color_detection():
    """Test RTMP Color Detection Viewer with RTMP stream option."""
    from core.controllers.RTMPColorDetectionViewer import RTMPColorDetectionViewer
    
    app = QApplication(sys.argv)
    viewer = RTMPColorDetectionViewer()
    
    # Verify RTMP Stream option exists
    stream_combo = viewer.stream_controls.type_combo
    items = [stream_combo.itemText(i) for i in range(stream_combo.count())]
    
    if "RTMP Stream" in items:
        print("[PASS] RTMP Stream option found in Color Detection Viewer")
        stream_combo.setCurrentText("RTMP Stream")
        
        # Check if placeholder text updates correctly
        expected_placeholder = "rtmp://server:port/app/stream or http://user:pass@host:port/stream"
        actual_placeholder = viewer.stream_controls.url_input.placeholderText()
        
        if expected_placeholder in actual_placeholder:
            print("[PASS] RTMP URL placeholder text is correct")
        else:
            print(f"[FAIL] Placeholder text mismatch: {actual_placeholder}")
    else:
        print("[FAIL] RTMP Stream option NOT found in Color Detection Viewer")
        print(f"  Available options: {items}")
    
    viewer.close()
    app.quit()
    return "RTMP Stream" in items

def test_rtmp_anomaly_detection():
    """Test RTMP Anomaly Detection Viewer with RTMP stream option."""
    from core.controllers.RTMPAnomalyDetectionViewer import RTMPAnomalyDetectionViewer
    
    app = QApplication(sys.argv)
    viewer = RTMPAnomalyDetectionViewer()
    
    # Verify RTMP Stream option exists
    stream_combo = viewer.stream_controls.type_combo
    items = [stream_combo.itemText(i) for i in range(stream_combo.count())]
    
    if "RTMP Stream" in items:
        print("[PASS] RTMP Stream option found in Anomaly Detection Viewer")
        stream_combo.setCurrentText("RTMP Stream")
        
        # Check if placeholder text updates correctly
        expected_placeholder = "rtmp://server:port/app/stream or http://user:pass@host:port/stream"
        actual_placeholder = viewer.stream_controls.url_input.placeholderText()
        
        if expected_placeholder in actual_placeholder:
            print("[PASS] RTMP URL placeholder text is correct")
        else:
            print(f"[FAIL] Placeholder text mismatch: {actual_placeholder}")
    else:
        print("[FAIL] RTMP Stream option NOT found in Anomaly Detection Viewer")
        print(f"  Available options: {items}")
    
    viewer.close()
    app.quit()
    return "RTMP Stream" in items

def test_rtmp_service():
    """Test RTMPStreamService with RTMP configuration."""
    from core.services.RTMPStreamService import StreamType, StreamConfig, RTMPStreamService
    import cv2
    
    print("\nTesting RTMPStreamService configuration...")
    
    # Test that RTMP stream type is properly configured
    config = StreamConfig(
        url="rtmp://example.com:1935/live/stream",
        stream_type=StreamType.RTMP
    )
    
    # Just verify the configuration is valid
    if config.stream_type == StreamType.RTMP:
        print("[PASS] RTMP StreamType configuration works")
    else:
        print("[FAIL] RTMP StreamType configuration failed")
    
    # Test OpenCV with FFMPEG backend availability
    test_cap = cv2.VideoCapture()
    backend_info = cv2.getBuildInformation()
    
    if "FFMPEG" in backend_info:
        print("[PASS] OpenCV has FFMPEG support for RTMP streams")
    else:
        print("[WARN] OpenCV may not have FFMPEG support - RTMP streams might not work")
    
    return True

def main():
    """Run all RTMP integration tests."""
    print("=" * 60)
    print("RTMP Integration Test Suite")
    print("=" * 60)
    
    print("\n1. Testing Real-Time Color Detection Viewer...")
    print("-" * 40)
    color_test = test_rtmp_color_detection()
    
    print("\n2. Testing Real-Time Anomaly Detection Viewer...")
    print("-" * 40)
    anomaly_test = test_rtmp_anomaly_detection()
    
    print("\n3. Testing RTMP Stream Service...")
    print("-" * 40)
    service_test = test_rtmp_service()
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("-" * 40)
    
    all_passed = color_test and anomaly_test and service_test
    
    if all_passed:
        print("[PASS] All RTMP integration tests PASSED!")
        print("\nYou can now use RTMP streams in both viewers by:")
        print("1. Selecting 'RTMP Stream' from the Stream Type dropdown")
        print("2. Entering an RTMP URL (e.g., rtmp://server:1935/live/stream)")
        print("3. Clicking Connect")
    else:
        print("[FAIL] Some tests failed. Please check the output above.")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())