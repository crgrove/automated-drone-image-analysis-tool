import simplekml
from helpers.LocationInfo import LocationInfo


class KMLGeneratorService:
    """Service to generate a KML file with points representing locations where images with areas of interest were taken."""

    def __init__(self):
        """
        Initializes the KMLGeneratorService by creating a new KML document.
        """
        self.kml = simplekml.Kml()

    def add_points(self, points):
        """
        Adds a list of geographic points to the KML document.

        Args:
            points (list of dict): A list of dictionaries, each containing:
                - 'name' (str): The name/label for the point.
                - 'lat' (float): Latitude of the point.
                - 'long' (float): Longitude of the point.
        """
        for point in points:
            self.kml.newpoint(name=point["name"], coords=[(point["long"], point["lat"])])

    def save_kml(self, path):
        """
        Saves the KML document to a file.

        Args:
            path (str): The file path where the KML document will be stored.
        """
        self.kml.save(path)

    def generate_kml_export(self, images, output_path):
        """
        Filters and extracts GPS coordinates from a list of images, then generates and saves a KML file.

        Args:
            images (list of dict): List of image metadata dictionaries. Each should contain:
                - 'name' (str): Image name.
                - 'path' (str): Path to the image file.
                - 'hidden' (bool): Whether the image is marked as hidden.

            output_path (str): The path to save the generated KML file.
        """
        kml_points = []
        for image in images:
            if image['hidden']:
                continue
            gps_coords = LocationInfo.get_gps(full_path=image['path'])
            if gps_coords:
                point = {
                    "name": image['name'],
                    "long": gps_coords['longitude'],
                    "lat": gps_coords['latitude']
                }
                kml_points.append(point)
        self.add_points(kml_points)
        self.save_kml(output_path)
