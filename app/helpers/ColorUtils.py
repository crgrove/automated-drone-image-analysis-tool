import numpy as np
import cv2


class ColorUtils:
    """Provides functions to aid in the manipulation of colors."""

    @staticmethod
    def getColorRange(rgb, r_range, g_range, b_range):
        """
        Calculate a color range based on a base RGB color and specified ranges for each color channel.

        Args:
            rgb (tuple[int, int, int]): The RGB values representing the base color.
            r_range (int): The range for the red channel.
            g_range (int): The range for the green channel.
            b_range (int): The range for the blue channel.

        Returns:
            tuple[tuple[int, int, int], tuple[int, int, int]]: The RGB values representing the minimum and maximum colors for the specified range.
        """
        upper_r = min(rgb[0] + r_range, 255)
        upper_g = min(rgb[1] + g_range, 255)
        upper_b = min(rgb[2] + b_range, 255)

        lower_r = max(rgb[0] - r_range, 0)
        lower_g = max(rgb[1] - g_range, 0)
        lower_b = max(rgb[2] - b_range, 0)

        return (lower_r, lower_g, lower_b), (upper_r, upper_g, upper_b)
