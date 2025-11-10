import numpy as np
import cv2


class ColorUtils:
    """Provides functions to aid in the manipulation of colors."""

    @staticmethod
    def get_rgb_color_range(
        rgb, r_range, g_range, b_range
    ):
        """
        Calculate a color range based on a base RGB color and specified ranges for each color channel.

        Args:
            rgb (tuple[int, int, int]): The RGB values representing the base color.
            r_range (int): The range for the red channel.
            g_range (int): The range for the green channel.
            b_range (int): The range for the blue channel.

        Returns:
            tuple[tuple[int, int, int], tuple[int, int, int]]: The RGB values
                representing the minimum and maximum colors for the specified range.
        """
        upper_r = min(rgb[0] + r_range, 255)
        upper_g = min(rgb[1] + g_range, 255)
        upper_b = min(rgb[2] + b_range, 255)

        lower_r = max(rgb[0] - r_range, 0)
        lower_g = max(rgb[1] - g_range, 0)
        lower_b = max(rgb[2] - b_range, 0)

        return (lower_r, lower_g, lower_b), (upper_r, upper_g, upper_b)

    @staticmethod
    def get_hsv_color_range(hsv, h_range, s_range, v_range):
        """
        Calculate HSV color ranges based on a base HSV color and specified thresholds.
        Handles hue wraparound for OpenCV (H: 0-179, S: 0-255, V: 0-255).

        Args:
            hsv (tuple[int, int, int]): The base HSV color (OpenCV range: H=0-179, S/V=0-255).
            h_range (int): Allowed hue deviation (distance from target H).
            s_range (int): Allowed saturation deviation.
            v_range (int): Allowed value (brightness) deviation.

        Returns:
            list[tuple[np.ndarray, np.ndarray]]:
                A list of (lower, upper) pairs for use with cv2.inRange.
                One pair if no wraparound, two pairs if wraparound occurs.
        """
        target_h, target_s, target_v = [int(x) for x in hsv]

        # Saturation and value (no wraparound needed)
        lower_s = max(0, target_s - s_range)
        upper_s = min(255, target_s + s_range)
        lower_v = max(0, target_v - v_range)
        upper_v = min(255, target_v + v_range)

        # Hue wraparound logic (OpenCV H is 0-179)
        lower_h = target_h - h_range
        upper_h = target_h + h_range

        if h_range >= 90:
            # Select all hues
            lower_bound = np.array([0, lower_s, lower_v])
            upper_bound = np.array([179, upper_s, upper_v])
            return [(lower_bound, upper_bound)]

        elif lower_h < 0:
            # Wraps around, e.g., H=5, h_range=10 => H in [175,179] and [0,15]
            lower_bound1 = np.array([180 + lower_h, lower_s, lower_v])
            upper_bound1 = np.array([179, upper_s, upper_v])
            lower_bound2 = np.array([0, lower_s, lower_v])
            upper_bound2 = np.array([upper_h, upper_s, upper_v])
            return [
                (lower_bound1, upper_bound1),
                (lower_bound2, upper_bound2)
            ]
        elif upper_h > 179:
            # Wraps around, e.g., H=175, h_range=10 => H in [165,179] and [0,5]
            lower_bound1 = np.array([lower_h, lower_s, lower_v])
            upper_bound1 = np.array([179, upper_s, upper_v])
            lower_bound2 = np.array([0, lower_s, lower_v])
            upper_bound2 = np.array([upper_h - 180, upper_s, upper_v])
            return [
                (lower_bound1, upper_bound1),
                (lower_bound2, upper_bound2)
            ]
        else:
            # Normal case, no wraparound
            lower_bound = np.array([lower_h, lower_s, lower_v])
            upper_bound = np.array([upper_h, upper_s, upper_v])
            return [(lower_bound, upper_bound)]

    @staticmethod
    def parse_rgb_string(value):
        """Parse RGB values from string like '(0, 85, 255)' or similar formats.

        Args:
            value (str): String containing RGB values.

        Returns:
            tuple: RGB values as (r,g,b) tuple, or None if parsing fails.
        """
        if isinstance(value, str):
            # Remove parentheses, brackets, etc.
            clean_str = value.strip('()[]{}')
            try:
                # Split on commas and convert to integers
                parts = [int(x.strip()) for x in clean_str.split(',')]
                if len(parts) == 3:
                    return tuple(parts)
            except Exception:
                return None
        return None
