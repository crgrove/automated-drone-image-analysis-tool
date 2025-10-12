import numpy as np


class GSDService:
    """Service to calculate Ground Sampling Distance (GSD) and related geometry from drone imagery."""

    def __init__(self, focal_length, image_size, altitude, tilt_angle, sensor, principalPoint=None):
        """
        Initializes the GSDService with camera and flight parameters.

        Args:
            focal_length (float): Focal length of the camera in millimeters.
            image_size (tuple): Size of the image in pixels as (width, height).
            altitude (float): Altitude of the drone in meters.
            tilt_angle (float): Tilt angle of the camera in degrees (0 is nadir).
            sensor (tuple): Sensor size in millimeters as (width_mm, height_mm).
            principalPoint (tuple, optional): Principal point in millimeters as (x_mm, y_mm).
                                              If None, defaults to image center.
        """
        sensor_mm = sensor
        self.pel_size = (sensor_mm[0] / image_size[0]) * 1e-3  # pixel size in meters
        self.focal_length = focal_length * 1e-3  # focal length in meters
        self.image = image_size
        self.altitude = altitude
        self.title_angle = tilt_angle
        if principalPoint:
            self.principalPoint = (
                (principalPoint[0] * 1e-3) / self.pel_size,
                (principalPoint[1] * 1e-3) / self.pel_size
            )
        else:
            self.principalPoint = (self.image[0] / 2, self.image[1] / 2)

    def compute_gsd(self, row, col):
        """
        Computes the Ground Sampling Distance (GSD) at a specific image pixel.

        Args:
            row (int): The row index of the pixel.
            col (int): The column index of the pixel.

        Returns:
            float: GSD at the specified pixel in centimeters.
        """
        tilt = np.radians(self.title_angle)
        cx = self.principalPoint[0]
        cy = self.principalPoint[1]

        x1 = (col - cx) * self.pel_size
        x2 = (col + 1 - cx) * self.pel_size
        y = (row - cy) * self.pel_size

        p1_cam = np.array([x1, y, -self.focal_length])
        p2_cam = np.array([x2, y, -self.focal_length])

        R_tilt = np.array([
            [1, 0, 0],
            [0, np.cos(tilt), -np.sin(tilt)],
            [0, np.sin(tilt),  np.cos(tilt)],
        ])
        p1_world = R_tilt @ p1_cam
        p2_world = R_tilt @ p2_cam

        def intersect_ground(p):
            scale = self.altitude / -p[2]
            return p[:2] * scale

        g1 = intersect_ground(p1_world)
        g2 = intersect_ground(p2_world)

        gsd = np.linalg.norm(g2 - g1)
        return gsd * 100  # convert to centimeters

    def compute_gsd_for_all_pixels(self):
        """
        Computes the GSD for all pixels in the image.

        Returns:
            np.ndarray: A 2D array of shape (height, width) with GSD values in centimeters.
        """
        tilt_rad = np.radians(self.title_angle)
        cos_t = np.cos(tilt_rad)
        sin_t = np.sin(tilt_rad)

        width = int(self.image[0])
        height = int(self.image[1])
        cy = self.principalPoint[1]

        rows = np.arange(height)
        y = (rows - cy) * self.pel_size

        scale = self.altitude / (self.focal_length * cos_t - y * sin_t)
        gsd_row = self.pel_size * scale * 100  # in centimeters

        gsd_full = np.tile(gsd_row[:, np.newaxis], (1, width))
        return gsd_full

    def compute_average_gsd(self):
        """
        Computes the average GSD across the entire image.

        Returns:
            float: The average GSD in centimeters.
        """
        tilt_rad = np.radians(self.title_angle)
        cos_t = np.cos(tilt_rad)
        sin_t = np.sin(tilt_rad)

        height = int(self.image[1])
        cy = self.principalPoint[1]

        rows = np.arange(height)
        y = (rows - cy) * self.pel_size

        scale = self.altitude / (self.focal_length * cos_t - y * sin_t)
        gsd_row = self.pel_size * scale * 100  # in centimeters

        avg_gsd = np.mean(gsd_row)
        return avg_gsd

    def compute_average_gsd_between_points(self, row1, col1, row2, col2):
        """
        Computes the average GSD between two image points.
        
        Uses trapezoidal approximation: average of GSD at both endpoints.
        This is more accurate than using GSD at just one point when GSD varies
        across the image (e.g., oblique shots).

        Args:
            row1 (float): Row coordinate of first point.
            col1 (float): Column coordinate of first point.
            row2 (float): Row coordinate of second point.
            col2 (float): Column coordinate of second point.

        Returns:
            float: Average GSD between the two points in centimeters.
        """
        gsd1 = self.compute_gsd(row1, col1)
        gsd2 = self.compute_gsd(row2, col2)
        return (gsd1 + gsd2) / 2.0

    def compute_ground_distance(self, row1, col1, row2, col2):
        """
        Computes the ground distance between two image points accounting for variable GSD.
        
        For oblique imagery, GSD varies across the image, so this method uses the
        average GSD between the two points for more accurate ground distance calculation.

        Args:
            row1 (float): Row coordinate of first point (typically image center).
            col1 (float): Column coordinate of first point (typically image center).
            row2 (float): Row coordinate of second point (e.g., AOI center).
            col2 (float): Column coordinate of second point (e.g., AOI center).

        Returns:
            tuple: (ground_distance_x, ground_distance_y) in meters, where:
                   - ground_distance_x: ground distance in the column (horizontal) direction
                   - ground_distance_y: ground distance in the row (vertical) direction
        """
        # Get average GSD between the two points
        avg_gsd_cm = self.compute_average_gsd_between_points(row1, col1, row2, col2)
        avg_gsd_m = avg_gsd_cm / 100.0  # Convert to meters
        
        # Calculate pixel distances
        pixel_offset_x = col2 - col1
        pixel_offset_y = row2 - row1
        
        # Convert to ground distances using average GSD
        ground_distance_x = pixel_offset_x * avg_gsd_m
        ground_distance_y = pixel_offset_y * avg_gsd_m
        
        return (ground_distance_x, ground_distance_y)