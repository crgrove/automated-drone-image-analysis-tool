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

    def ground_x(self, row, col):
        """
        Computes the X ground coordinate corresponding to a pixel in the image.

        Args:
            row (int): The row index of the pixel.
            col (int): The column index of the pixel.

        Returns:
            float: The X coordinate on the ground (in meters).
        """
        tilt = np.radians(self.title_angle)
        cx = self.principalPoint[0]
        cy = self.principalPoint[1]
        x = (col - cx) * self.pel_size
        y = (row - cy) * self.pel_size

        p_cam = np.array([x, y, -self.focal_length])
        R = np.array([
            [1, 0, 0],
            [0, np.cos(tilt), -np.sin(tilt)],
            [0, np.sin(tilt),  np.cos(tilt)],
        ])
        p_world = R @ p_cam
        scale = self.altitude / -p_world[2]
        ground_pos = p_world[:2] * scale
        return ground_pos[0]
