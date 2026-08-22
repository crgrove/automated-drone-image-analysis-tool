"""
PhotoPayload - Prepares image bytes for a CalTopo photo upload.

CalTopo takes photo data as base64 inside a form-urlencoded field, which
inflates a file by roughly 43% before it leaves the machine: base64 costs 33%,
and percent-encoding base64's '+' and '/' costs another 8%. A 31.6 MB drone
still therefore becomes 45.4 MB on the wire and around 780 ms of CPU, of which
620 ms is the percent-encoding alone. That encoding cannot be made cheaper -
measured against urlencode, quote_plus is identical and str.translate is 27x
slower - so the only lever is sending fewer pixels.

Capping the long edge first is worth 26x at 2048 px (45.4 MB -> 1.75 MB).
Images already within the cap, such as the generated AOI composites and
thumbnails, are passed through untouched so they are never re-compressed.
"""

import base64
import io
import os

from PIL import Image

# Longest edge, in pixels, for an image taken straight from the camera.
#
# 2048 keeps ~3 MP - ample for the context photo on a location marker, and for
# the fallback when an AOI composite could not be generated - while cutting the
# upload by a factor of 26. Raise it for more detail at proportionally more
# upload time (4096 is ~7x, 3072 ~12x); set it to None to upload originals
# unchanged.
MAX_UPLOAD_EDGE = 2048

# Quality for re-encoded JPEGs. 85 is visually indistinguishable here and about
# half the size of 95.
JPEG_QUALITY = 85


def encode_photo(photo_path, max_edge=MAX_UPLOAD_EDGE, logger=None):
    """Read an image and return it base64-encoded, downscaled if oversized.

    Falls back to the file's original bytes whenever the image cannot be
    resized, so a decode problem costs upload time rather than the photo.

    Args:
        photo_path (str): Path to the image file.
        max_edge (int): Longest permitted edge in pixels, or None to send the
            file unchanged.
        logger: Optional LoggerService for diagnostics.

    Returns:
        tuple: (base64_data: str, filename: str)

    Raises:
        OSError: If the file cannot be read at all.
    """
    with open(photo_path, 'rb') as image_file:
        raw = image_file.read()

    filename = os.path.basename(photo_path)

    if max_edge:
        resized = _downscale(raw, max_edge, photo_path, logger)
        if resized is not None:
            if logger is not None:
                logger.info(
                    f"CalTopo photo {filename}: {len(raw) / 1048576:.1f} MB -> "
                    f"{len(resized) / 1048576:.1f} MB for upload"
                )
            raw = resized

    return base64.b64encode(raw).decode('utf-8'), filename


def _downscale(raw, max_edge, photo_path, logger):
    """Return JPEG bytes capped to max_edge, or None to keep the original.

    Args:
        raw (bytes): Original file contents.
        max_edge (int): Longest permitted edge in pixels.
        photo_path (str): Source path, for diagnostics.
        logger: Optional LoggerService.

    Returns:
        bytes or None: Re-encoded image, or None when it should not be touched.
    """
    try:
        image = Image.open(io.BytesIO(raw))

        if max(image.width, image.height) <= max_edge:
            # Already small enough - generated composites and thumbnails land
            # here, and re-compressing them would only lose detail.
            return None

        # draft() lets the JPEG decoder scale during decoding rather than
        # after, which is measurably cheaper than a full-resolution decode.
        image.draft('RGB', (max_edge, max_edge))
        image.thumbnail((max_edge, max_edge), Image.LANCZOS)

        buffer = io.BytesIO()
        save_kwargs = {'format': 'JPEG', 'quality': JPEG_QUALITY}

        # Keep EXIF so CalTopo still sees capture time, camera and GPS.
        exif = image.info.get('exif')
        if exif:
            save_kwargs['exif'] = exif

        image.convert('RGB').save(buffer, **save_kwargs)
        return buffer.getvalue()

    except Exception as e:
        if logger is not None:
            logger.warning(
                f"Could not downscale {photo_path} for upload ({e}); "
                f"sending the original."
            )
        return None
