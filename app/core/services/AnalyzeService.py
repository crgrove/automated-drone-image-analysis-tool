import operator
import cv2
import os
import numpy as np
import imghdr
import shutil
import xml.etree.ElementTree as ET
import time

from pathlib import Path
from multiprocessing import Pool, pool
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from core.services.LoggerService import LoggerService
from core.services.HistogramNormalizationService import HistogramNormalizationService
from core.services.KMeansClustersService import KMeansClustersService
from core.services.XmlService import XmlService
"""****Import Algorithm Services****"""
from algorithms.ColorRange.services.ColorRangeService import ColorRangeService
from algorithms.RXAnomaly.services.RXAnomalyService import RXAnomalyService
from algorithms.MatchedFilter.services.MatchedFilterService import MatchedFilterService
from algorithms.ThermalRange.services.ThermalRangeService import ThermalRangeService
from algorithms.ThermalAnomaly.services.ThermalAnomalyService import ThermalAnomalyService
"""****End Algorithm Import****"""


class AnalyzeService(QObject):
    """Service to process images using a selected algorithm"""
    # Signals to send info back to the GUI
    sig_msg = pyqtSignal(str)
    sig_aois = pyqtSignal()
    sig_done = pyqtSignal(int, int)

    def __init__(self, id, algorithm, input, output, identifier_color, min_area, num_processes,
                 max_aois, aoi_radius, histogram_reference_path, kmeans_clusters, thermal, options):
        """
        __init__ constructor

        :Int id: numeric id
        :Dict algorithm: the algorithm to be used for analysis
        :String input: the path to the input directory containing the images to be processed
        :String output: the path to the output directory where images will be stored
        :Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
        :Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
        :Int num_processes: the number of concurrent processes to be used to process images
        :Int max_aois: the threshold for a maximum number of areas of interest in a single image before a warning is produced
        :Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
        :String histogram_reference_path: the path to the histogram matching reference image
        :Int kmeans_clusters: the number of clusters(colors) to maintain in the image
        :Bool thermal: is this a thermal image algorithm
        :Dictionary options: additional algorithm-specific options
        """
        self.logger = LoggerService()
        self.xmlService = XmlService()
        super().__init__()
        self.algorithm = algorithm
        self.input = input
        self.output_dir = output
        self.output = os.path.join(output, "ADIAT_Results")
        self.identifier_color = identifier_color
        self.options = options
        self.min_area = min_area
        self.aoi_radius = aoi_radius
        self.num_processes = num_processes
        self.max_aois = max_aois
        self.max_aois_limit_exceeded = False
        self.hist_ref_path = histogram_reference_path
        self.kmeans_clusters = kmeans_clusters
        self.__id = id
        self.images_with_aois = []
        self.cancelled = False
        self.is_thermal = thermal

        self.pool = Pool(self.num_processes)

    @pyqtSlot()
    def processFiles(self):
        """
        processFiles iterates through all of the files in a directory and processes the image using the selected algorithm and features.
        """
        try:
            self.setupOutputDir()
            self.xmlService.addSettingsToXml(
                input_dir=self.input,
                output_dir=self.output_dir,
                identifier_color=self.identifier_color,
                algorithm=self.algorithm['name'],
                thermal=self.is_thermal,
                num_processes=self.num_processes,
                min_area=self.min_area,
                hist_ref_path=self.hist_ref_path,
                kmeans_clusters=self.kmeans_clusters,
                options=self.options
            )
            image_files = []

            start_time = time.time()
            for subdir, dirs, files in os.walk(self.input):
                for file in files:
                    file_path = Path(file)
                    if self.is_thermal and file_path.suffix != 'irg':
                        image_files.append(os.path.join(subdir, file))
                    elif not self.is_thermal:
                        image_files.append(os.path.join(subdir, file))

            ttl_images = len(image_files)
            self.sig_msg.emit(f"Processing {ttl_images} files")

            # Process each image using multiprocessing
            for file in image_files:
                if os.path.isdir(file):
                    ttl_images -= 1
                    continue

                if imghdr.what(file) is not None and self.pool._state == pool.RUN:
                    self.pool.apply_async(
                        AnalyzeService.processFile,
                        (
                            self.algorithm,
                            self.identifier_color,
                            self.min_area,
                            self.aoi_radius,
                            self.options,
                            file,
                            self.input,
                            self.output,
                            self.hist_ref_path,
                            self.kmeans_clusters,
                            self.is_thermal
                        ),
                        callback=self.processComplete
                    )
                else:
                    ttl_images -= 1
                    self.sig_msg.emit(f"Skipping {file} :: File is not an image")

            # Close the pool and ensure all processes are done
            self.pool.close()
            self.pool.join()

            # Generate the output XML with the information gathered during processing
            self.images_with_aois = sorted(self.images_with_aois, key=operator.itemgetter('path'))
            for img in self.images_with_aois:
                self.xmlService.addImageToXml(img)

            file_path = os.path.join(self.output, "ADIAT_Data.xml")
            self.xmlService.saveXmlFile(file_path)
            ttl_time = round(time.time() - start_time, 3)
            self.sig_done.emit(self.__id, len(self.images_with_aois))
            self.sig_msg.emit(f"Total Processing Time: {ttl_time} seconds")
            self.sig_msg.emit(f"Total Images Processed: {ttl_images}")

        except Exception as e:
            self.logger.error(f"An error occurred during processing: {e}")
        
    @staticmethod
    def processFile(algorithm, identifier_color, min_area, aoi_radius, options, full_path, input_dir, output_dir, hist_ref_path, kmeans_clusters, thermal):
        """
        processFile processes a single image using the selected algorithm and features
        :Dict algorithm: the algorithm to be used
        :Tuple(int,int,int) identifier_color: the RGB values for the color to be used to highlight areas of interest
        :Int min_area: the size in pixels that an object must meet or exceed to qualify as an area of interest
        :Int aoi_radius: radius to be added to the min enclosing circle around an area of interest.
        :Dictionary options: additional algorithm-specific options
        :String full_path: the path to the image being analyzed
        :String input_dir: the path to the input directory containing the images to be processed
        :String output_dir: the path to the output directory where images will be stored
        :String hist_ref_path: the path to the histogram matching reference image
        :Int kmeans_clusters: the number of clusters(colors) to maintain in the image
        :Bool thermal: is this a thermal image algorithm
        :return numpy.ndarray, List: the numpy.ndarray representation of the image augmented with areas of interest circled and a list of the areas of interest
        """
        img = cv2.imdecode(np.fromfile(full_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if not thermal:
            # if the histogram reference image path is not empty, create an instance of the HistogramNormalizationService
            histogram_service = None
            if hist_ref_path is not None:
                histogram_service = HistogramNormalizationService(hist_ref_path)
                img = histogram_service.matchHistograms(img)

            # if the kmeans clusters number is not empty, create an instance of the KMeansClustersService
            kmeans_service = None
            if kmeans_clusters is not None:
                kmeans_service = KMeansClustersService(kmeans_clusters)
                img = kmeans_service.generateClusters(img)

        # Create an instance of the algorithm class
        cls = globals()[algorithm['service']]
        instance = cls(identifier_color, min_area, aoi_radius, algorithm['combine_overlapping_aois'], options)

        try:
            # process the image using the algorithm
            return instance.processImage(img, full_path, input_dir, output_dir)
        except Exception as e:
            logger = LoggerService()
            logger.error(e)

    @pyqtSlot()
    def processComplete(self, result):
        """
        processComplete processes the analyzed image

        :concurrent.futures._base.Future future: object representing the execution of the callable
        """
        if result.input_path is not None:
            path = Path(result.input_path)
            file_name = path.name
        # returned by processFile method
        if result.error_message is not None:
            self.sig_msg.emit("Unable to process " + file_name + " :: " + result.error_message)
            return
        if result.areas_of_interest is not None:
            self.images_with_aois.append({"path": result.output_path, "aois": result.areas_of_interest})
            self.sig_msg.emit('Areas of interest identified in ' + file_name)
            if result.base_contour_count > self.max_aois and not self.max_aois_limit_exceeded:
                self.sig_aois.emit()
                self.max_aois_limit_exceeded = True
        else:
            self.sig_msg.emit('No areas of interested identified in ' + file_name)

    @pyqtSlot()
    def processCancel(self):
        """
        processCancel cancels any asynchronous processes that have not completed
        """
        self.cancelled = True
        self.sig_msg.emit("--- Cancelling Image Processing ---")
        self.pool.terminate()

    def setupOutputDir(self):
        """
        setupOutputDir creates the output directory
        """
        try:
            if (os.path.exists(self.output)):
                try:
                    shutil.rmtree(self.output)
                except Exception as e:
                    self.logger.error(e)
            os.makedirs(self.output)
        except Exception as e:
            self.logger.error(e)
