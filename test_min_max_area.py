#!/usr/bin/env python3
"""
Test script for improved min/max area validation
"""

import sys
from PyQt5.QtWidgets import QApplication
from app.core.controllers.MainWindow import MainWindow

def test_min_max_area():
    """Test the improved min/max area validation."""
    
    print("=" * 60)
    print("Testing Improved Min/Max Area Validation")
    print("=" * 60)
    print()
    print("Expected Behavior:")
    print("1. Type '500' in max area field")
    print("   - Should NOT change min area while typing")
    print("   - Should only validate when you press Tab/Enter or click away")
    print()
    print("2. If max < min when you finish editing:")
    print("   - Shows a popup notification")
    print("   - Automatically adjusts the other field")
    print()
    print("3. No changes happen during typing, only on 'editingFinished'")
    print("=" * 60)
    print()
    print("Opening main window for testing...")
    print("Try typing values in min/max area fields")
    print()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Set some initial values for testing
    window.minAreaSpinBox.setValue(100)
    window._minAreaOriginal = 100
    window.maxAreaSpinBox.setValue(1000)
    window._maxAreaOriginal = 1000
    
    print("Initial values:")
    print(f"  Min Area: {window.minAreaSpinBox.value()}")
    print(f"  Max Area: {window.maxAreaSpinBox.value()}")
    print()
    print("Test scenarios to try:")
    print("1. Type '5' in max area (making it less than min)")
    print("2. Type '2000' in min area (making it greater than max)")
    print("3. Type '500' in max area (should work without issues)")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_min_max_area()