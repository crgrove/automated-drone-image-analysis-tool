import math


class GridReviewService:
    """Pure-logic helpers for the viewer's grid review mode.

    Grid review overlays an N x M grid on an image so a reviewer can sweep
    every cell systematically at a fixed zoom. This service holds all the
    Qt-free math and (de)serialization: cell geometry, scan ordering,
    GSD-based grid-size suggestion, reviewed-cell persistence format, and
    progress computation. State itself lives on the image dicts/XML managed
    by XmlService; runtime orchestration lives in GridReviewController.

    Cells are identified by their row-major index (0 = top-left, increasing
    left-to-right then top-to-bottom) regardless of the scan order used for
    navigation, so persisted indices stay valid if scan order ever changes.
    """

    @staticmethod
    def cell_rects(width, height, rows, cols):
        """Compute the pixel rectangle of every grid cell.

        Uses the same ceil-then-clamp tiling convention as
        AlgorithmService.split_image so grid cells line up with algorithm
        segments when the counts match. Cells tile the image exactly: no
        gaps, no overlaps; the last row/column absorbs the remainder.

        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            rows: Number of grid rows (>= 1).
            cols: Number of grid columns (>= 1).

        Returns:
            List of (x, y, w, h) tuples in row-major order.
        """
        rows = max(1, int(rows))
        cols = max(1, int(cols))
        row_height = math.ceil(height / rows)
        col_width = math.ceil(width / cols)

        rects = []
        for i in range(rows):
            y = i * row_height
            h = max(0, min((i + 1) * row_height, height) - y)
            for j in range(cols):
                x = j * col_width
                w = max(0, min((j + 1) * col_width, width) - x)
                rects.append((x, y, w, h))
        return rects

    @staticmethod
    def serpentine_order(rows, cols):
        """Compute the boustrophedon scan sequence over a grid.

        Row 0 runs left-to-right, row 1 right-to-left, and so on — the
        same systematic sweep pattern a human searcher uses, minimizing
        the jump between consecutive cells.

        Args:
            rows: Number of grid rows.
            cols: Number of grid columns.

        Returns:
            List of row-major cell indices in scan order.
        """
        rows = max(1, int(rows))
        cols = max(1, int(cols))
        order = []
        for i in range(rows):
            row = range(i * cols, (i + 1) * cols)
            if i % 2 == 1:
                row = reversed(row)
            order.extend(row)
        return order

    @staticmethod
    def suggest_grid(image_w, image_h, gsd_cm, viewport_w, viewport_h,
                     min_person_px=60, person_height_cm=180, min_n=2, max_n=12):
        """Suggest a grid size so a person is comfortably visible per cell.

        When one cell fills the viewport, a person of person_height_cm
        should span at least min_person_px on screen. Coarser GSD (fewer
        image pixels per person) therefore yields smaller cells / more of
        them.

        Args:
            image_w: Image width in pixels.
            image_h: Image height in pixels.
            gsd_cm: Ground sample distance in cm/pixel, or None if unknown.
            viewport_w: Viewer viewport width in screen pixels.
            viewport_h: Viewer viewport height in screen pixels.
            min_person_px: Minimum on-screen person height in pixels.
            person_height_cm: Assumed person height in cm.
            min_n: Minimum rows/cols in the suggestion.
            max_n: Maximum rows/cols in the suggestion.

        Returns:
            (rows, cols) tuple, or None when gsd/viewport data is unusable.
        """
        if gsd_cm is None or gsd_cm <= 0:
            return None
        if not image_w or not image_h or image_w <= 0 or image_h <= 0:
            return None
        if not viewport_w or not viewport_h or viewport_w <= 0 or viewport_h <= 0:
            return None

        person_image_px = person_height_cm / gsd_cm
        if person_image_px <= 0:
            return None

        max_cell_w = viewport_w * person_image_px / min_person_px
        max_cell_h = viewport_h * person_image_px / min_person_px

        cols = min(max(math.ceil(image_w / max_cell_w), min_n), max_n)
        rows = min(max(math.ceil(image_h / max_cell_h), min_n), max_n)
        return (rows, cols)

    @staticmethod
    def person_screen_px(gsd_cm, cell_w, viewport_w, person_height_cm=180):
        """Compute a person's on-screen height when one cell fills the view.

        Used by the grid settings dialog to annotate its suggestion
        ("person is approximately N px on screen at cell zoom").

        Args:
            gsd_cm: Ground sample distance in cm/pixel, or None.
            cell_w: Cell width in image pixels.
            viewport_w: Viewport width in screen pixels.
            person_height_cm: Assumed person height in cm.

        Returns:
            On-screen person height in pixels, or None when inputs are unusable.
        """
        if gsd_cm is None or gsd_cm <= 0 or not cell_w or cell_w <= 0:
            return None
        if not viewport_w or viewport_w <= 0:
            return None
        person_image_px = person_height_cm / gsd_cm
        return person_image_px * (viewport_w / cell_w)

    @staticmethod
    def parse_reviewed(attr):
        """Parse a persisted reviewed-cells attribute string.

        Tolerant of junk: non-integer tokens and negative values are
        skipped silently so a hand-edited or corrupted attribute never
        breaks loading.

        Args:
            attr: Attribute string like "0,1,5", or None/empty.

        Returns:
            Set of reviewed row-major cell indices.
        """
        reviewed = set()
        if not attr:
            return reviewed
        for token in str(attr).split(','):
            token = token.strip()
            if not token:
                continue
            try:
                index = int(token)
            except ValueError:
                continue
            if index >= 0:
                reviewed.add(index)
        return reviewed

    @staticmethod
    def serialize_reviewed(cells):
        """Serialize reviewed cell indices for XML persistence.

        Args:
            cells: Iterable of row-major cell indices.

        Returns:
            Sorted comma-separated string like "0,1,5".
        """
        return ','.join(str(index) for index in sorted(set(cells)))

    @staticmethod
    def image_progress(image, default_rows, default_cols):
        """Compute review progress for one image.

        Images with no stored grid count against the default grid size
        with zero cells reviewed, so run-level percentages stay meaningful
        before a sweep starts.

        Args:
            image: Image dict from XmlService.get_images().
            default_rows: Grid rows assumed for images without stored grids.
            default_cols: Grid cols assumed for images without stored grids.

        Returns:
            (reviewed_count, total_cells) tuple.
        """
        grid = image.get('grid_review') if image else None
        if grid:
            total = grid['rows'] * grid['cols']
            # Clamp to the valid range in case a stale attribute carries
            # indices from a larger grid.
            reviewed = len({c for c in grid['reviewed'] if 0 <= c < total})
        else:
            total = max(1, int(default_rows)) * max(1, int(default_cols))
            reviewed = 0
        return (reviewed, total)

    @staticmethod
    def run_progress(images, default_rows, default_cols):
        """Compute review progress across a whole run.

        Hidden images are excluded — they are out of the review scope by
        definition.

        Args:
            images: Images list from XmlService.get_images().
            default_rows: Grid rows assumed for images without stored grids.
            default_cols: Grid cols assumed for images without stored grids.

        Returns:
            (reviewed_count, total_cells) tuple across all visible images.
        """
        reviewed_sum = 0
        total_sum = 0
        for image in images or []:
            if image.get('hidden'):
                continue
            reviewed, total = GridReviewService.image_progress(image, default_rows, default_cols)
            reviewed_sum += reviewed
            total_sum += total
        return (reviewed_sum, total_sum)
