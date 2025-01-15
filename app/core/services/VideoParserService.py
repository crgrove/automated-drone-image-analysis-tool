import os
import shutil
from pathlib import Path
import re
import cv2
import math
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper


class VideoParserService(QObject):
    """Service to parse video into images."""

    # Signals to send info back to the GUI
    sig_msg = pyqtSignal(str)
    sig_done = pyqtSignal(int, int)

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

    @pyqtSlot()
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
            duration = round(frame_count / fps)
            est_capture = math.floor(duration / self.interval) + 1
            self.sig_msg.emit("Video length: %i seconds. %i images will be captured" % (duration, est_capture))

            # Ensure the file provided is a video file.
            if not cap.isOpened() or fps == 0:
                self.sig_msg.emit("SRT File Not Provided")
                self.sig_done.emit(self.__id, 0)
                return

            srt_list = []
            if self.srt_path:
                self.sig_msg.emit("Parsing SRT File")
                srt_data = Path(self.srt_path).read_text()
                srt_entries = re.split("(?:\r?\n){2,}", srt_data)
                for entry in srt_entries:
                    data = re.split("(?:\r?\n)", entry)
                    if len(data) == 6:
                        times = re.split(r"\s.*\s", data[1])
                        start_time = datetime.strptime(times[0], '%H:%M:%S,%f')
                        end_time = datetime.strptime(times[1], '%H:%M:%S,%f')

                        uav_data = re.findall(r'(?<=\[).+?(?=\])', data[4])
                        uav_dict = {split[0]: split[1] for entry in uav_data for split in [re.split(r"\s*:\s*", entry)]}

                        srt_list.append({
                            "start": start_time,
                            "end": end_time,
                            "latitude": float(uav_dict.get('latitude')) if 'latitude' in uav_dict else None,
                            "longitude": float(uav_dict.get('longitude')) if 'longitude' in uav_dict else None,
                            "altitude": float(uav_dict.get('altitude', 0))
                        })
            else:
                self.sig_msg.emit("SRT File Not Provided")

            self._setup_output_dir()
            time_marker = 0
            image_count = 0
            base_name = os.path.basename(self.video_path)
            self.sig_msg.emit("Capturing images")
            success = True
            while success and not self.cancelled:
                frame_id = int(fps * time_marker)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
                time = datetime(1900, 1, 1) + timedelta(milliseconds=cap.get(cv2.CAP_PROP_POS_MSEC))

                item = next((item for item in srt_list if item["start"] <= time <= item["end"]), None)
                success, image = cap.read()
                if success:
                    output_file = f"{self.output_dir}/{base_name}_{time_marker}s.jpg"
                    cv2.imwrite(output_file, image)
                    if item and item["latitude"] and item["longitude"]:
                        MetaDataHelper.add_gps_data(output_file, item["latitude"], item["longitude"], item["altitude"])
                    image_count += 1
                time_marker += self.interval
                if image_count % 10 == 0:
                    self.sig_msg.emit(f"{image_count} images captured")
            self.sig_done.emit(self.__id, image_count)
        except Exception as e:
            self.logger.error(e)

    @pyqtSlot()
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
