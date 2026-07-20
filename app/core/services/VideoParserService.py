import os
import shutil
from bisect import bisect_left
from pathlib import Path
import re
import cv2
import math
import pandas as pd
from datetime import datetime, timedelta, timezone

from PySide6.QtCore import QObject, Signal, Slot

from core.services.LoggerService import LoggerService
from helpers.MetaDataHelper import MetaDataHelper
from helpers.VideoFileHelper import detect_thumbnail_track, get_video_creation_time, remux_to_main_track, is_ffmpeg_available, _FFMPEG_USER_MSG


class VideoParserService(QObject):
    """Service to parse video into images.

    Extracts frames from video files at specified intervals and optionally
    embeds GPS metadata from SRT subtitle files.

    Attributes:
        sig_msg: Signal emitted with status messages (str).
        sig_done: Signal emitted when processing completes (id, count).
    """

    # Signals to send info back to the GUI
    sig_msg = Signal(str)
    sig_done = Signal(int, int)

    def __init__(self, id, video, metadata_path, output, interval):
        """Initialize the VideoParserService with parameters for video processing.

        Args:
            id: Numeric ID for this parser instance.
            video: Path to the video file to be processed.
            metadata_path: Path to a metadata file (SRT or CSV) with GPS data.
            output: Path to the output directory where images will be stored.
            interval: Time interval in seconds between frames to capture.
        """
        self.logger = LoggerService()
        super().__init__()
        self.__id = id
        self.video_path = video
        self.metadata_path = metadata_path
        self.output_dir = output
        self.interval = interval
        self.cancelled = False

    @Slot()
    def process_video(self):
        """Convert video frames to still images and attach GPS metadata if provided.

        Supports SRT subtitle files (DJI) and CSV flight logs (Skydio).
        Captures images at specified intervals, embedding GPS metadata into each
        image where available. Emits sig_msg for status updates and sig_done when complete.
        """
        remuxed_temp_path = None
        try:
            cap = cv2.VideoCapture(self.video_path)

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Detect thumbnail track (e.g. Skydio X10 embeds MJPEG cover art as stream 0)
            if cap.isOpened() and detect_thumbnail_track(cap):
                self.sig_msg.emit("Detected thumbnail track in video, remuxing to select main video track...")
                cap.release()
                remuxed_temp_path = remux_to_main_track(self.video_path, self.logger)
                if remuxed_temp_path:
                    cap = cv2.VideoCapture(remuxed_temp_path)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                else:
                    if not is_ffmpeg_available():
                        self.sig_msg.emit(f"Error: {_FFMPEG_USER_MSG}")
                    else:
                        self.sig_msg.emit("Error: Failed to remux video file.")
                    self.sig_done.emit(self.__id, 0)
                    return

            if not cap.isOpened() or fps == 0 or frame_count == 0:
                self.sig_msg.emit("Error: Invalid video file or unreadable format.")
                self.sig_done.emit(self.__id, 0)
                return

            duration = round(frame_count / fps)
            est_capture = math.floor(duration / self.interval) + 1
            self.sig_msg.emit(f"Video length: {duration} seconds. Estimated {est_capture} images will be captured.")

            # Parse metadata file if provided
            srt_list = []
            csv_entries = []
            video_start_utc = None
            metadata_format = self._detect_metadata_format(self.metadata_path)

            if metadata_format == 'srt':
                srt_list = self._parse_srt_file(self.metadata_path)
                if srt_list is None:
                    return
            elif metadata_format == 'csv':
                result = self._parse_csv_flight_log(self.metadata_path, self.video_path)
                if result is None:
                    return
                video_start_utc, csv_entries = result
                if video_start_utc is None:
                    self.sig_msg.emit("Error: Could not determine video start time from MP4 metadata.")
                    self.sig_msg.emit("Ensure the video file has creation_time metadata (ffprobe required).")
                    self.sig_done.emit(self.__id, 0)
                    return
            else:
                self.sig_msg.emit("Metadata File Not Provided")

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

                output_file = f"{self.output_dir}/{base_name}_{time_marker}s.jpg"
                cv2.imwrite(output_file, image)

                if metadata_format == 'srt':
                    # Get the actual timestamp after reading the frame
                    ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                    video_time = datetime(1900, 1, 1) + timedelta(milliseconds=ms)
                    item = next((item for item in srt_list if item["start"] <= video_time <= item["end"]), None)
                    if item and item["latitude"] and item["longitude"]:
                        MetaDataHelper.add_gps_data(output_file, item["latitude"], item["longitude"], item["altitude"])
                elif metadata_format == 'csv':
                    frame_utc = video_start_utc + timedelta(seconds=time_marker)
                    entry = self._find_closest_csv_entry(csv_entries, frame_utc)
                    if entry and entry['latitude'] and entry['longitude']:
                        MetaDataHelper.add_gps_data(output_file, entry['latitude'], entry['longitude'], entry['altitude_m'])

                image_count += 1
                time_marker += self.interval

                if image_count % 10 == 0:
                    self.sig_msg.emit(f"{image_count} images captured")

            cap.release()  # Ensure proper cleanup
            if remuxed_temp_path:
                try:
                    os.unlink(remuxed_temp_path)
                except OSError:
                    pass
            self.sig_done.emit(self.__id, image_count)

        except Exception as e:
            self.logger.error(f"Error in process_video: {str(e)}")
            self.sig_msg.emit(f"Processing error: {str(e)}")
            if remuxed_temp_path:
                try:
                    os.unlink(remuxed_temp_path)
                except OSError:
                    pass
            self.sig_done.emit(self.__id, 0)

    def _detect_metadata_format(self, path):
        """Determine the metadata file format from its extension.

        Args:
            path: File path string.

        Returns:
            'srt', 'csv', or None.
        """
        if not path:
            return None
        ext = os.path.splitext(path)[1].lower()
        if ext == '.srt':
            return 'srt'
        if ext == '.csv':
            return 'csv'
        return None

    def _parse_srt_file(self, srt_path):
        """Parse a DJI SRT subtitle file for GPS metadata.

        Args:
            srt_path: Path to the SRT file.

        Returns:
            List of dicts with start, end, latitude, longitude, altitude keys,
            or None on parse failure.
        """
        self.sig_msg.emit("Parsing SRT File")
        srt_list = []
        try:
            srt_data = Path(srt_path).read_text()
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
            return srt_list
        except Exception as e:
            self.sig_msg.emit(f"Error parsing SRT file: {str(e)}")
            return None

    def _parse_csv_flight_log(self, csv_path, video_path):
        """Parse a Skydio CSV flight log for GPS metadata.

        Args:
            csv_path: Path to the CSV flight log.
            video_path: Path to the video file (used to extract creation_time).

        Returns:
            Tuple of (video_start_utc, sorted list of entry dicts) or None on failure.
            Each entry dict has: utc_time, latitude, longitude, altitude_m.
        """
        self.sig_msg.emit("Parsing CSV flight log...")
        try:
            df = pd.read_csv(csv_path)

            # Validate required columns
            required_cols = ['Datetime (UTC)', 'Latitude', 'Longitude', 'GPS Altitude (ft MSL)']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                self.sig_msg.emit(f"Error: CSV missing required columns: {', '.join(missing)}")
                return None

            # Parse timestamps and convert altitude from feet to meters
            df['utc_time'] = pd.to_datetime(df['Datetime (UTC)'], utc=True)
            df['altitude_m'] = df['GPS Altitude (ft MSL)'] * 0.3048
            df = df.sort_values('utc_time').reset_index(drop=True)

            csv_entries = []
            for _, row in df.iterrows():
                csv_entries.append({
                    'utc_time': row['utc_time'].to_pydatetime(),
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude'],
                    'altitude_m': row['altitude_m']
                })

            self.sig_msg.emit(f"Loaded {len(csv_entries)} GPS entries from CSV")

            # Get video start time from MP4 container metadata
            video_start_utc = get_video_creation_time(video_path, self.logger)
            if video_start_utc:
                self.sig_msg.emit(f"Video start time (UTC): {video_start_utc.isoformat()}")
            return (video_start_utc, csv_entries)

        except Exception as e:
            self.sig_msg.emit(f"Error parsing CSV flight log: {str(e)}")
            return None

    def _find_closest_csv_entry(self, csv_entries, target_utc, max_delta_seconds=5.0):
        """Find the CSV entry closest in time to the target UTC timestamp.

        Uses binary search for efficiency on the sorted entry list.

        Args:
            csv_entries: Sorted list of entry dicts with 'utc_time' keys.
            target_utc: Target UTC datetime to match.
            max_delta_seconds: Maximum allowed time difference in seconds.

        Returns:
            The closest entry dict, or None if no entry is within max_delta_seconds.
        """
        if not csv_entries:
            return None

        timestamps = [e['utc_time'] for e in csv_entries]
        pos = bisect_left(timestamps, target_utc)

        # Check the entries at pos and pos-1 to find the closest
        best = None
        best_delta = None
        for i in [pos - 1, pos]:
            if 0 <= i < len(csv_entries):
                delta = abs((csv_entries[i]['utc_time'] - target_utc).total_seconds())
                if best_delta is None or delta < best_delta:
                    best_delta = delta
                    best = csv_entries[i]

        if best_delta is not None and best_delta <= max_delta_seconds:
            return best
        return None

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
