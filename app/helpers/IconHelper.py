"""
IconHelper - Generic icon utility for the application.

Provides icon creation utilities based on theme. Each component is responsible
for applying its own icons using these utilities.
"""

import qtawesome as qta


class IconHelper:
    """
    Generic helper for creating themed icons.

    Provides utility methods for icon creation without coupling to specific UI components.
    """

    @staticmethod
    def get_icon_color(theme):
        """
        Get the appropriate icon color for the given theme.

        Args:
            theme (str): Theme name ('Dark' or 'Light')

        Returns:
            str: Icon color string for qtawesome
        """
        return 'lightgray' if theme == "Dark" else 'darkgray'

    @staticmethod
    def create_icon(icon_name, theme, **options):
        """
        Create a themed icon.

        Args:
            icon_name (str): Font Awesome icon name (e.g. 'fa6s.magnifying-glass')
            theme (str): Theme name ('Dark' or 'Light')
            **options: Additional options to pass to qta.icon()

        Returns:
            QIcon: Themed icon
        """
        color = IconHelper.get_icon_color(theme)
        return qta.icon(icon_name, color=color, **options)
