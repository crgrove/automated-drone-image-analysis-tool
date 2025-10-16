#!/usr/bin/env python3
"""
test_motion_detection.py - Test script for real-time motion detection feature

Tests both static and moving camera modes with sample video or webcam input.
"""

import sys
import os
import cv2
import numpy as np
import time
from pathlib import Path

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.services.RealtimeMotionDetectionService import (
    RealtimeMotionDetector, DetectionMode, MotionAlgorithm
)


def test_with_webcam():
    """Test motion detection with webcam (static camera mode)."""
    print("Testing motion detection with webcam (Static mode)...")
    
    # Initialize detector
    detector = RealtimeMotionDetector()
    detector.update_config(
        mode=DetectionMode.STATIC,
        algorithm=MotionAlgorithm.MOG2,
        sensitivity=0.7,
        min_area=1000,
        show_vectors=True
    )
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return False
    
    print("Press 'q' to quit, 's' to switch modes, 'a' to change algorithm")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        detections, camera_motion, annotated_frame = detector.process_frame(frame)
        
        # Add FPS counter
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            print(f"FPS: {fps:.2f}, Detections: {len(detections)}")
        
        # Display result
        cv2.imshow('Motion Detection', annotated_frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Switch mode
            current_mode = detector.get_config()['mode']
            if current_mode == 'static':
                detector.update_config(mode=DetectionMode.MOVING)
                print("Switched to MOVING mode")
            else:
                detector.update_config(mode=DetectionMode.STATIC)
                print("Switched to STATIC mode")
        elif key == ord('a'):
            # Change algorithm
            current_algo = detector.get_config()['algorithm']
            algorithms = [MotionAlgorithm.FRAME_DIFF, MotionAlgorithm.MOG2, 
                         MotionAlgorithm.KNN, MotionAlgorithm.OPTICAL_FLOW]
            current_idx = next((i for i, a in enumerate(algorithms) 
                              if a.value == current_algo), 0)
            next_idx = (current_idx + 1) % len(algorithms)
            detector.update_config(algorithm=algorithms[next_idx])
            print(f"Switched to {algorithms[next_idx].value} algorithm")
    
    cap.release()
    cv2.destroyAllWindows()
    return True


def test_with_video(video_path):
    """Test motion detection with video file (moving camera mode)."""
    print(f"Testing motion detection with video: {video_path}")
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False
    
    # Initialize detector
    detector = RealtimeMotionDetector()
    detector.update_config(
        mode=DetectionMode.AUTO,  # Auto-detect camera motion
        algorithm=MotionAlgorithm.MOG2,
        sensitivity=0.5,
        min_area=500,
        compensation_strength=0.8,
        show_camera_motion=True,
        show_vectors=True
    )
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return False
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video info: {fps:.1f} FPS, {total_frames} frames")
    
    print("Press 'q' to quit, SPACE to pause, 'm' to toggle mode")
    
    frame_count = 0
    paused = False
    detection_count = 0
    
    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("End of video reached")
                break
            
            # Process frame
            detections, camera_motion, annotated_frame = detector.process_frame(frame)
            
            # Track detections
            if detections:
                detection_count += len(detections)
            
            frame_count += 1
            
            # Print stats every second
            if frame_count % int(fps) == 0:
                seconds = frame_count / fps
                print(f"Time: {seconds:.1f}s, Total detections: {detection_count}")
                if camera_motion:
                    print(f"  Camera motion: ({camera_motion.global_velocity[0]:.1f}, "
                          f"{camera_motion.global_velocity[1]:.1f}), "
                          f"Confidence: {camera_motion.confidence:.2f}")
        else:
            # When paused, just show the last frame
            annotated_frame = annotated_frame if 'annotated_frame' in locals() else frame
        
        # Display result
        cv2.imshow('Motion Detection - Video', annotated_frame)
        
        # Handle keyboard input
        key = cv2.waitKey(30 if not paused else 0) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
            print("Paused" if paused else "Resumed")
        elif key == ord('m'):
            # Toggle between AUTO and MOVING modes
            current_mode = detector.get_config()['mode']
            if current_mode == 'auto':
                detector.update_config(mode=DetectionMode.MOVING)
                print("Switched to MOVING mode (forced)")
            else:
                detector.update_config(mode=DetectionMode.AUTO)
                print("Switched to AUTO mode")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nTest completed: {frame_count} frames processed, {detection_count} total detections")
    return True


def create_test_video():
    """Create a simple test video with moving objects."""
    print("Creating test video with synthetic motion...")
    
    width, height = 640, 480
    fps = 30
    duration = 10  # seconds
    output_path = "test_motion_video.mp4"
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Create frames with moving rectangles
    for frame_num in range(fps * duration):
        # Create black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add moving white rectangle (simulating object motion)
        t = frame_num / fps
        x = int(100 + 300 * np.sin(t))
        y = int(height // 2 + 100 * np.cos(t * 2))
        cv2.rectangle(frame, (x, y), (x + 50, y + 50), (255, 255, 255), -1)
        
        # Add another moving object
        x2 = int(width - 150 - 200 * np.sin(t * 0.7))
        y2 = int(100 + 200 * np.sin(t * 1.5))
        cv2.circle(frame, (x2, y2), 30, (0, 255, 0), -1)
        
        # Simulate camera motion every 3 seconds
        if (frame_num // fps) % 3 == 0:
            # Add global shift to simulate camera motion
            shift_x = int(10 * np.sin(frame_num * 0.1))
            shift_y = int(5 * np.cos(frame_num * 0.1))
            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            frame = cv2.warpAffine(frame, M, (width, height))
        
        # Add timestamp
        cv2.putText(frame, f"Frame: {frame_num}, Time: {t:.1f}s", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()
    print(f"Test video created: {output_path}")
    return output_path


def main():
    """Main test function."""
    print("Motion Detection Test Script")
    print("============================\n")
    
    import argparse
    parser = argparse.ArgumentParser(description='Test motion detection')
    parser.add_argument('--webcam', action='store_true', 
                       help='Test with webcam (static mode)')
    parser.add_argument('--video', type=str, 
                       help='Test with video file path')
    parser.add_argument('--create-test-video', action='store_true',
                       help='Create a synthetic test video')
    
    args = parser.parse_args()
    
    if args.create_test_video:
        video_path = create_test_video()
        test_with_video(video_path)
    elif args.webcam:
        test_with_webcam()
    elif args.video:
        test_with_video(args.video)
    else:
        # Default: try webcam first, then create test video
        print("No arguments provided. Testing with webcam...")
        if not test_with_webcam():
            print("\nWebcam not available. Creating and testing with synthetic video...")
            video_path = create_test_video()
            test_with_video(video_path)
    
    print("\nTest completed!")


if __name__ == "__main__":
    main()