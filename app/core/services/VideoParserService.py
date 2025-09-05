import os
import shutil
from pathlib import Path
import re
import cv2
import math
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal, Slot

from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper


class VideoParserService(QObject):
    """Service to parse video into images."""

    # Signals to send info back to the GUI
    sig_msg = Signal(str)
    sig_done = Signal(int, int)

    def __init__(self, id, video, srt, output, interval):
        """
        Initialize the VideoParserService with parameters for video processing.

        Args:
            id (int): Numeric ID.
            video (str): Path to the video file to be processed.
            srt (str): Path to the SRT file with metadata for processing.
            output (str): Path to the output directory where images will be stored.
            interval (int): Time interval in seconds between frames to capture.
        """
        self.logger = LoggerService()
        super().__init__()
        self.__id = id
        self.video_path = video
        self.srt_path = srt
        self.output_dir = output
        self.interval = interval
        self.cancelled = False

    @Slot()
    def process_video(self):
        """
        Convert video frames to still images and attach metadata from an SRT file if provided.

        Captures images at specified intervals, extracting GPS metadata from the SRT file
        and embedding it into each image where available.
        """
        try:
            cap = cv2.VideoCapture(self.video_path)

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            if not cap.isOpened() or fps == 0 or frame_count == 0:
                self.sig_msg.emit("Error: Invalid video file or unreadable format.")
                self.sig_done.emit(self.__id, 0)
                return

            duration = round(frame_count / fps)
            est_capture = math.floor(duration / self.interval) + 1
            self.sig_msg.emit(f"Video length: {duration} seconds. Estimated {est_capture} images will be captured.")

            # Parse SRT file if provided
            srt_list = []
            if self.srt_path:
                self.sig_msg.emit("Parsing SRT File")
                try:
                    srt_data = Path(self.srt_path).read_text()
                    srt_entries = re.split("(?:\r?\n){2,}", srt_data)
                    for entry in srt_entries:
                        data = re.split("(?:\r?\n)", entry)
                        if len(data) >= 5:
                            times = re.split(r"\s.*\s", data[1])
                            start_time = datetime.strptime(times[0], '%H:%M:%S,%f')
                            end_time = datetime.strptime(times[1], '%H:%M:%S,%f')

                            uav_data = re.findall(r'(?<=\[).+?(?=\])', data[4])
                            uav_dict = {split[0]: split[1] for entry in uav_data for split in [re.split(r"\s*:\s*", entry)]}
                            longitude = float(uav_dict.get('longitude')) if 'longitude' in uav_dict else None
                            # Extra logic for longitude misspelling in some SRT files
                            if longitude is None:
                                longitude = float(uav_dict.get('longtitude')) if 'longtitude' in uav_dict else None
                            srt_list.append({
                                "start": start_time,
                                "end": end_time,
                                "latitude": float(uav_dict.get('latitude')) if 'latitude' in uav_dict else None,
                                "longitude": longitude,
                                "altitude": float(uav_dict.get('altitude', 0))
                            })
                except Exception as e:
                    self.sig_msg.emit(f"Error parsing SRT file: {str(e)}")
                    return
            else:
                self.sig_msg.emit("SRT File Not Provided")
            self._setup_output_dir()
            time_marker = 0
            image_count = 0
            base_name = os.path.basename(self.video_path)

            self.sig_msg.emit("Capturing images")

            while not self.cancelled:
                frame_id = int(fps * time_marker)

                # Ensure we don't go beyond the total frames
                if frame_id >= frame_count:
                    self.sig_msg.emit("Reached end of video.")
                    break

                # Seek to the correct frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
                success, image = cap.read()
                if not success:
                    self.sig_msg.emit(f"Frame capture failed at frame {frame_id}, stopping.")
                    break

                # Get the actual timestamp after reading the frame
                ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                video_time = datetime(1900, 1, 1) + timedelta(milliseconds=ms)

                # Find corresponding SRT metadata
                item = next((item for item in srt_list if item["start"] <= video_time <= item["end"]), None)

                output_file = f"{self.output_dir}/{base_name}_{time_marker}s.jpg"
                cv2.imwrite(output_file, image)

                if item and item["latitude"] and item["longitude"]:
                    MetaDataHelper.add_gps_data(output_file, item["latitude"], item["longitude"], item["altitude"])

                image_count += 1
                time_marker += self.interval

                if image_count % 10 == 0:
                    self.sig_msg.emit(f"{image_count} images captured")

            cap.release()  # Ensure proper cleanup
            self.sig_done.emit(self.__id, image_count)

        except Exception as e:
            self.logger.error(f"Error in process_video: {str(e)}")
            self.sig_msg.emit(f"Processing error: {str(e)}")
            self.sig_done.emit(self.__id, 0)

    @Slot()
    def process_cancel(self):
        """
        Cancel the video processing operation.
        """
        self.cancelled = True
        self.sig_msg.emit("--- Cancelling Video Processing ---")

    def _setup_output_dir(self):
        """
        Create the output directory for storing captured images.
        """
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except Exception as e:
            self.logger.error(e)
