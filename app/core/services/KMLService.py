import simplekml


class KMLService:
    """Service to generate a KML file with points representing locations where images with areas of interest were taken."""

    def __init__(self):
        """
        Initialize the KMLService, creating a new KML document.
        """
        self.kml = simplekml.Kml()

    def add_points(self, points):
        """
        Add a list of points to the KML document.

        Args:
            points (list[dict]): List of dictionaries, each containing 'name' (str), 'lat' (float), and 'long' (float) keys
                                 representing the point's name, latitude, and longitude respectively.
        """
        for point in points:
            self.kml.newpoint(name=point["name"], coords=[(point["long"], point["lat"])])

    def save_kml(self, path):
        """
        Save the KML document to the specified file path.

        Args:
            path (str): The file path where the KML document will be stored.
        """
        self.kml.save(path)
