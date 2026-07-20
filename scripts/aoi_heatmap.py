# aoi_heatmap.py
# Generates a heatmap of all AOI detection positions across images from an ADIAT XML results file.
# Useful for identifying systematic detection patterns like chromatic aberrations or bad pixels.
#
# Usage:
#   python scripts/aoi_heatmap.py                          # Opens file picker dialog
#   python scripts/aoi_heatmap.py path/to/ADIAT_DATA.XML   # Direct path
#   python scripts/aoi_heatmap.py data.xml -o heatmap.png   # Custom output path
#   python scripts/aoi_heatmap.py data.xml --grid-size 300   # Higher resolution grid

import argparse
import os
import sys
from ast import literal_eval
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def get_xml_path(args):
    """Get the XML file path from CLI args or a file picker dialog."""
    if args.xml_file:
        path = args.xml_file
        if not os.path.isfile(path):
            print(f"Error: File not found: {path}")
            sys.exit(1)
        return path

    # Try tkinter file dialog
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Select ADIAT XML Results File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        root.destroy()
        if not path:
            print("No file selected.")
            sys.exit(0)
        return path
    except ImportError:
        print("Error: No XML file specified and tkinter is not available.")
        print("Usage: python scripts/aoi_heatmap.py <path_to_ADIAT_DATA.XML>")
        sys.exit(1)


def parse_aoi_data(xmlPath):
    """Parse the ADIAT XML file to extract image paths and AOI positions.

    Args:
            xmlPath: Path to the ADIAT_DATA.XML file.

    Returns:
            List of dicts with 'path' and 'aois' keys. Each AOI has 'center' and 'radius'.
    """
    tree = ET.parse(xmlPath)
    root = tree.getroot()
    xmlDir = os.path.dirname(os.path.abspath(xmlPath))

    imageData = []
    imagesXml = root.find('images')
    if imagesXml is None:
        return imageData

    for imageXml in imagesXml:
        path = imageXml.get('path')
        if not path:
            continue

        # Resolve the image path (same logic as XmlService.get_images)
        path = path.replace('/', os.sep)
        if not os.path.isabs(path):
            path = os.path.join(xmlDir, path)

        aois = []
        for aoiXml in imageXml:
            centerStr = aoiXml.get('center', '(0, 0)')
            radiusStr = aoiXml.get('radius', '0')
            try:
                center = literal_eval(centerStr)
                radius = int(radiusStr)
                aois.append({'center': center, 'radius': radius})
            except (ValueError, SyntaxError):
                continue

        if aois:
            imageData.append({'path': path, 'aois': aois})

    return imageData


def get_image_dimensions(imagePath):
    """Read image dimensions without loading pixel data.

    Args:
            imagePath: Path to the image file.

    Returns:
            (width, height) tuple, or None if the file cannot be read.
    """
    try:
        with Image.open(imagePath) as img:
            return img.size  # (width, height)
    except Exception:
        return None


def normalize_coordinates(imageData):
    """Normalize all AOI positions to [0, 1] range using image dimensions.

    Args:
            imageData: List of image dicts from parse_aoi_data().

    Returns:
            Tuple of (numpy array of shape (N, 2) with normalized coords, stats dict).
    """
    normalizedPoints = []
    totalAois = 0
    skippedImages = 0
    skippedAois = 0
    resolvedImages = 0
    dimensionCache = {}

    for entry in imageData:
        path = entry['path']
        totalAois += len(entry['aois'])

        # Cache dimension lookups
        if path not in dimensionCache:
            dimensionCache[path] = get_image_dimensions(path)

        dims = dimensionCache[path]
        if dims is None:
            skippedImages += 1
            skippedAois += len(entry['aois'])
            continue

        resolvedImages += 1
        width, height = dims

        for aoi in entry['aois']:
            cx, cy = aoi['center']
            normX = max(0.0, min(1.0, cx / width))
            normY = max(0.0, min(1.0, cy / height))
            normalizedPoints.append([normX, normY])

    stats = {
        'totalImages': len(imageData),
        'resolvedImages': resolvedImages,
        'skippedImages': skippedImages,
        'totalAois': totalAois,
        'plottedAois': len(normalizedPoints),
        'skippedAois': skippedAois
    }

    if not normalizedPoints:
        return np.empty((0, 2)), stats

    return np.array(normalizedPoints), stats


def generate_heatmap(normalizedCoords, gridSize=200, sigma=3.0):
    """Generate a color-mapped heatmap image from normalized coordinates.

    Args:
            normalizedCoords: Numpy array of shape (N, 2) with values in [0, 1].
            gridSize: Number of bins in each dimension.
            sigma: Gaussian smoothing sigma.

    Returns:
            BGR heatmap image as numpy array.
    """
    histogram, xEdges, yEdges = np.histogram2d(
        normalizedCoords[:, 0],
        normalizedCoords[:, 1],
        bins=gridSize,
        range=[[0, 1], [0, 1]]
    )

    # histogram2d returns (x, y) but image convention is (row, col) = (y, x)
    histogram = histogram.T

    smoothed = gaussian_filter(histogram, sigma=sigma)

    # Normalize to 0-255
    normalized = np.zeros_like(smoothed, dtype=np.uint8)
    if smoothed.max() > 0:
        cv2.normalize(smoothed, normalized, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    colorMapped = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    return colorMapped


def build_color_bar(height, barWidth=30):
    """Create a vertical color bar strip.

    Args:
            height: Height of the color bar in pixels.
            barWidth: Width of the color bar in pixels.

    Returns:
            BGR image of the color bar.
    """
    gradient = np.linspace(255, 0, height).astype(np.uint8)
    gradient = np.tile(gradient.reshape(-1, 1), (1, barWidth))
    return cv2.applyColorMap(gradient, cv2.COLORMAP_JET)


def annotate_heatmap(heatmapImg, stats, displaySize=800):
    """Scale up and annotate the heatmap with title, stats, color bar, and crosshair.

    Args:
            heatmapImg: BGR heatmap image from generate_heatmap().
            stats: Statistics dict from normalize_coordinates().
            displaySize: Target display size in pixels.

    Returns:
            Annotated BGR image.
    """
    # Scale the heatmap to display size
    scaled = cv2.resize(heatmapImg, (displaySize, displaySize), interpolation=cv2.INTER_LINEAR)

    titleHeight = 50
    statsHeight = 80
    colorBarWidth = 60
    colorBarPadding = 10

    totalWidth = displaySize + colorBarWidth + colorBarPadding * 2
    totalHeight = titleHeight + displaySize + statsHeight

    canvas = np.zeros((totalHeight, totalWidth, 3), dtype=np.uint8)
    canvas[:] = (40, 40, 40)  # Dark gray background

    # Place the heatmap
    hmTop = titleHeight
    hmLeft = 0
    canvas[hmTop:hmTop + displaySize, hmLeft:hmLeft + displaySize] = scaled

    # Draw center crosshair on the heatmap area
    centerX = hmLeft + displaySize // 2
    centerY = hmTop + displaySize // 2
    crossColor = (200, 200, 200)
    cv2.line(canvas, (centerX - 20, centerY), (centerX + 20, centerY), crossColor, 1)
    cv2.line(canvas, (centerX, centerY - 20), (centerX, centerY + 20), crossColor, 1)

    # Draw border around heatmap
    cv2.rectangle(canvas, (hmLeft, hmTop), (hmLeft + displaySize - 1, hmTop + displaySize - 1), (180, 180, 180), 1)

    # Title
    cv2.putText(canvas, "AOI Detection Heatmap", (10, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Color bar
    cbLeft = displaySize + colorBarPadding
    cbTop = hmTop + 20
    cbHeight = displaySize - 40
    colorBar = build_color_bar(cbHeight)
    canvas[cbTop:cbTop + cbHeight, cbLeft:cbLeft + 30] = colorBar
    cv2.rectangle(canvas, (cbLeft, cbTop), (cbLeft + 29, cbTop + cbHeight - 1), (180, 180, 180), 1)
    cv2.putText(canvas, "High", (cbLeft, cbTop - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    cv2.putText(canvas, "Low", (cbLeft, cbTop + cbHeight + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # Stats panel
    statsTop = hmTop + displaySize + 10
    line1 = f"Images: {stats['resolvedImages']}/{stats['totalImages']}"
    line2 = f"AOIs plotted: {stats['plottedAois']}/{stats['totalAois']}"
    if stats['skippedImages'] > 0:
        line2 += f"  ({stats['skippedAois']} skipped - image files not found)"

    cv2.putText(canvas, line1, (10, statsTop + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(canvas, line2, (10, statsTop + 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    # Edge/center labels
    cv2.putText(canvas, "Top-Left", (hmLeft + 5, hmTop + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)
    cv2.putText(canvas, "Bottom-Right", (hmLeft + displaySize - 95, hmTop + displaySize - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1)

    return canvas


def main():
    parser = argparse.ArgumentParser(
        description="Generate a heatmap of AOI detection positions from an ADIAT XML results file."
    )
    parser.add_argument('xml_file', nargs='?', default=None,
                        help="Path to ADIAT_DATA.XML. If omitted, a file picker dialog opens.")
    parser.add_argument('-o', '--output', default=None,
                        help="Output PNG path. Defaults to aoi_heatmap.png in the XML directory.")
    parser.add_argument('-g', '--grid-size', type=int, default=200,
                        help="Heatmap grid resolution (default: 200).")
    parser.add_argument('-s', '--sigma', type=float, default=3.0,
                        help="Gaussian smoothing sigma (default: 3.0).")
    parser.add_argument('--no-display', action='store_true',
                        help="Save output only, do not display.")
    args = parser.parse_args()

    print("AOI Heatmap Generator")
    print("=" * 40)

    xmlPath = get_xml_path(args)
    print(f"XML file: {xmlPath}")

    # Parse XML
    print("\nParsing XML...")
    imageData = parse_aoi_data(xmlPath)
    if not imageData:
        print("No images with areas of interest found in the XML file.")
        sys.exit(0)

    totalAois = sum(len(entry['aois']) for entry in imageData)
    print(f"  Found {len(imageData)} images with {totalAois} areas of interest")

    # Normalize coordinates
    print("\nReading image dimensions...")
    normalizedCoords, stats = normalize_coordinates(imageData)
    print(f"  {stats['resolvedImages']} images resolved successfully")
    if stats['skippedImages'] > 0:
        print(f"  {stats['skippedImages']} images not found (skipped)")

    if normalizedCoords.shape[0] == 0:
        print("\nNo AOIs could be plotted (image files not accessible).")
        print("Ensure the image files are accessible from the paths in the XML.")
        sys.exit(1)

    # Generate heatmap
    print(f"\nGenerating heatmap ({args.grid_size}x{args.grid_size} grid, sigma={args.sigma})...")
    heatmapImg = generate_heatmap(normalizedCoords, gridSize=args.grid_size, sigma=args.sigma)
    print(f"  {stats['plottedAois']} AOIs plotted")

    # Annotate
    annotated = annotate_heatmap(heatmapImg, stats)

    # Output
    if args.output:
        outputPath = args.output
    else:
        outputPath = os.path.join(os.path.dirname(os.path.abspath(xmlPath)), "aoi_heatmap.png")

    cv2.imwrite(outputPath, annotated)
    print(f"\nOutput saved: {outputPath}")

    if not args.no_display:
        print("Press any key to close the display window...")
        cv2.imshow("AOI Detection Heatmap", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
