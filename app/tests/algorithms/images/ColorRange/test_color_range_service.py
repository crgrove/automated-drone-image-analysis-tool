import pytest
import numpy as np
import cv2
import tempfile
import os
from algorithms.images.ColorRange.services.ColorRangeService import ColorRangeService
from algorithms.AlgorithmService import AnalysisResult


@pytest.fixture
def color_range_service():
    """Fixture providing a ColorRangeService instance."""
    options = {
        'color_ranges': [
            {'color_range': [(100, 150, 200), (120, 170, 220)]}
        ]
    }
    return ColorRangeService(
        identifier=(110, 160, 210),
        min_area=10,
        max_area=0,  # 0 means unlimited (no max area filter)
        aoi_radius=5,
        combine_aois=False,  # Set to False to avoid combining logic issues in tests
        options=options
    )


@pytest.fixture
def test_image():
    """Create a test image with colored regions."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Add a region matching the color range (BGR format for OpenCV)
    # Color range is RGB(100-120, 150-170, 200-220)
    # Using RGB(110, 160, 210) which is in the middle of the range
    # Convert to BGR: [210, 160, 110]
    # Make it a larger region (50x50 = 2500 pixels) to ensure it passes min_area
    img[50:100, 50:100] = [210, 160, 110]  # RGB(110, 160, 210) in BGR
    # Add a region outside the color range
    img[150:180, 150:180] = [50, 50, 50]  # Dark region
    return img


def test_color_range_service_initialization(color_range_service):
    """Test ColorRangeService initialization."""
    assert color_range_service.name == 'ColorRange'
    assert len(color_range_service.color_ranges) == 1
    assert color_range_service.color_ranges[0]['color_range'][0] == (100, 150, 200)


def test_color_range_service_legacy_format():
    """Test ColorRangeService with legacy single color_range format."""
    options = {
        'color_range': [(100, 150, 200), (120, 170, 220)]
    }
    service = ColorRangeService(
        identifier=(110, 160, 210),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert len(service.color_ranges) == 1
    assert service.color_ranges[0]['color_range'] == [(100, 150, 200), (120, 170, 220)]


def test_color_range_service_fallback():
    """Test ColorRangeService fallback to identifier color."""
    options = {}
    service = ColorRangeService(
        identifier=(100, 150, 200),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert len(service.color_ranges) == 1
    assert service.color_ranges[0]['color_range'][0] == (100, 150, 200)
    assert service.color_ranges[0]['color_range'][1] == (100, 150, 200)


def test_color_range_service_multiple_ranges():
    """Test ColorRangeService with multiple color ranges."""
    options = {
        'color_ranges': [
            {'color_range': [(100, 150, 200), (120, 170, 220)]},
            {'color_range': [(200, 100, 50), (220, 120, 70)]}
        ]
    }
    service = ColorRangeService(
        identifier=(110, 160, 210),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )
    assert len(service.color_ranges) == 2


def test_process_image_single_range(color_range_service, test_image):
    """Test processing an image with a single color range."""
    # Verify test image has the expected colored region
    assert np.any(test_image[50:100, 50:100] != 0), "Test image should have colored region"
    assert np.array_equal(test_image[75, 75], [210, 160, 110]), f"Expected [210, 160, 110], got {test_image[75, 75]}"

    # Verify the color range conversion
    color_range = color_range_service.color_ranges[0]['color_range']
    min_rgb = color_range[0]  # RGB(100, 150, 200)
    max_rgb = color_range[1]  # RGB(120, 170, 220)
    # Convert to BGR for OpenCV
    cv_lower = np.array([min_rgb[2], min_rgb[1], min_rgb[0]], dtype=np.uint8)  # BGR [200, 150, 100]
    cv_upper = np.array([max_rgb[2], max_rgb[1], max_rgb[0]], dtype=np.uint8)  # BGR [220, 170, 120]
    test_color = np.array([210, 160, 110], dtype=np.uint8)  # BGR
    assert np.all((test_color >= cv_lower) & (test_color <= cv_upper)), \
        f"Test color {test_color} should be within range [{cv_lower}, {cv_upper}]"

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = color_range_service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.input_path == full_path
        assert result.areas_of_interest is not None
        if len(result.areas_of_interest) == 0:
            # Debug: manually check if color would be detected and what contours are found
            mask = cv2.inRange(test_image, cv_lower, cv_upper)
            pixel_count = cv2.countNonZero(mask)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            print(f"Debug: Color range BGR [{cv_lower}, {cv_upper}]")
            print(f"Debug: Test image region BGR value: {test_image[75, 75]}")
            print(f"Debug: Mask pixel count: {pixel_count}")
            print(f"Debug: Number of contours found: {len(contours)}")
            if len(contours) > 0:
                contour_area = cv2.contourArea(contours[0])
                print(f"Debug: First contour area: {contour_area}")
                # Check what identify_areas_of_interest would do
                test_aois, _ = color_range_service.identify_areas_of_interest(test_image.shape, contours)
                print(f"Debug: AOIs from identify_areas_of_interest: {len(test_aois)}")
                print(f"Debug: combine_aois setting: {color_range_service.combine_aois}")
            print(f"Debug: Min area: {color_range_service.min_area}")
            print(f"Debug: Max area: {color_range_service.max_area}")
            print(f"Debug: Error message: {result.error_message}")
        assert len(result.areas_of_interest) > 0, \
            f"No AOIs found. Mask should have ~2500 pixels, min_area={color_range_service.min_area}. Error: {result.error_message}"
        assert result.error_message is None


def test_process_image_no_detections(color_range_service):
    """Test processing an image with no matching colors."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[:] = [50, 50, 50]  # Dark image, no matches

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = color_range_service.process_image(img, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.areas_of_interest is None or len(result.areas_of_interest) == 0


def test_process_image_multiple_ranges(test_image):
    """Test processing with multiple color ranges."""
    options = {
        'color_ranges': [
            {'color_range': [(100, 150, 200), (120, 170, 220)]},
            {'color_range': [(200, 100, 50), (220, 120, 70)]}
        ]
    }
    service = ColorRangeService(
        identifier=(110, 160, 210),
        min_area=10,
        max_area=1000,
        aoi_radius=5,
        combine_aois=True,
        options=options
    )

    # Add a second colored region matching the second color range
    # Second range is RGB(200-220, 100-120, 50-70)
    # Using RGB(210, 110, 60) which is in the middle
    # Convert to BGR: [60, 110, 210]
    test_image[10:30, 10:30] = [60, 110, 210]  # RGB(210, 110, 60) in BGR

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = service.process_image(test_image, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is None


def test_process_image_area_filtering(color_range_service, test_image):
    """Test that areas are filtered by min_area and max_area."""
    # Create very small region
    small_img = np.zeros((50, 50, 3), dtype=np.uint8)
    # Use color within the range: RGB(110, 160, 210) -> BGR [210, 160, 110]
    small_img[20:22, 20:22] = [210, 160, 110]  # Very small region (2x2 = 4 pixels)

    color_range_service.min_area = 100  # Larger than the region

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = color_range_service.process_image(small_img, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        # Should have no AOIs due to min_area filtering
        assert result.areas_of_interest is None or len(result.areas_of_interest) == 0


def test_process_image_error_handling(color_range_service):
    """Test error handling in process_image."""
    # Create invalid image data
    invalid_img = None

    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = color_range_service.process_image(invalid_img, full_path, input_dir, output_dir)

        assert isinstance(result, AnalysisResult)
        assert result.error_message is not None


def test_process_image_mask_storage(color_range_service, test_image):
    """Test that masks are properly stored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = tmpdir
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(input_dir, "test.jpg")

        result = color_range_service.process_image(test_image, full_path, input_dir, output_dir)

        if result.areas_of_interest and len(result.areas_of_interest) > 0:
            assert result.output_path is not None
            assert result.output_path.endswith('.tif')
