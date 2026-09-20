"""CombinedPdfReportService - One PDF report collating a folder of results.

Builds a single reportlab document from several ADIAT_Data.xml runs: cover,
run-summary table, a combined overview map, then each run's algorithm
settings and full per-AOI detail pages. The detail pages reuse
PdfGeneratorService's machinery unchanged, so a collated run's pages match
the single-run report exactly.

PdfGeneratorService reads a handful of attributes off a live Viewer; a
collation has no Viewer, so each run is represented by a RunReportContext -
a lightweight stand-in carrying exactly the attributes the base service
reads (images, xml_service, settings, position_format, distance_unit,
use_terrain_elevation). The service swaps the active context per run.

TOC/bookmark note: PDFDocTemplate derives bookmark keys from heading TEXT,
so repeated headings collide across runs (every run has "Algorithm Settings";
WALDO image names repeat between flights). Run headings therefore carry a
unique numeric prefix, image names are prefixed with their run number, and
the per-run settings header uses a non-TOC style.
"""

import os
from datetime import datetime
from io import BytesIO

from PySide6.QtCore import QBuffer
from PySide6.QtGui import QPixmap
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table, TableStyle

from core.services.export.PdfGeneratorService import PdfGeneratorService, PDFDocTemplate
from core.services.export.ReviewMergeService import ReviewMergeService
from helpers.ColorUtils import ColorUtils
from helpers.PathHelper import cross_platform_basename


class RunReportContext:
    """Per-run stand-in for the Viewer attributes PdfGeneratorService reads.

    Deliberately has NO custom_agl_altitude_ft attribute: the base service's
    hasattr() guard then skips the operator altitude override, which cannot
    meaningfully apply to a run reviewed on another machine.
    """

    def __init__(self, xml_path, run_name, images, xml_service, settings,
                 position_format, distance_unit, use_terrain_elevation,
                 unavailable_count, total_aoi_count, reviewer_names=None):
        self.xml_path = xml_path
        self.run_name = run_name
        self.images = images
        self.xml_service = xml_service
        self.settings = settings
        self.position_format = position_format
        self.distance_unit = distance_unit
        self.use_terrain_elevation = use_terrain_elevation
        self.unavailable_count = unavailable_count
        self.total_aoi_count = total_aoi_count
        self.reviewer_names = reviewer_names or []

    @property
    def review_count(self):
        return len(self.reviewer_names)

    @classmethod
    def from_xml(cls, xml_path, position_format, distance_unit,
                 include_images_without_flagged_aois=False,
                 use_terrain_elevation=True, path_resolver=None):
        """Load one results XML into a report-ready context.

        Convenience single-file path: parses, then applies the same filter
        as :meth:`from_merged`.
        """
        merge_service = ReviewMergeService()
        records = merge_service.load_run_records([xml_path])
        if not records:
            raise ValueError(f"Unreadable results file: {xml_path}")
        merged = merge_service.merge_group(records)
        return cls.from_merged(
            merged, position_format, distance_unit,
            include_images_without_flagged_aois=include_images_without_flagged_aois,
            use_terrain_elevation=use_terrain_elevation,
            path_resolver=path_resolver)

    @classmethod
    def from_merged(cls, merged_run, position_format, distance_unit,
                    include_images_without_flagged_aois=False,
                    use_terrain_elevation=True, path_resolver=None):
        """Build a context from a (possibly multi-reviewer) MergedRun.

        Filtering mirrors the single-run PDFExportController, extended by the
        merge policy: hidden images are dropped; an image keeps its flagged
        AOIs plus any COMMENTED unflagged ones (reviewer attention must not
        be silently dropped); an image with neither is included, with all its
        AOIs, only when the include flag is set. Images missing on this
        computer are first offered to ``path_resolver`` (a results-folder
        scan session can find them even though the XML travelled alone), then
        counted and skipped.

        Args:
            merged_run: ReviewMergeService.MergedRun.
            position_format: PositionFormat preference string.
            distance_unit: 'ft' or 'm' (already normalized).
            include_images_without_flagged_aois: The report scope flag.
            use_terrain_elevation: UseTerrainElevation preference.
            path_resolver: Optional callable(stored_path) -> located | None.

        Returns:
            RunReportContext
        """
        images = []
        unavailable = 0
        total_aois = 0
        for img in merged_run.images:
            if img.get('hidden', False):
                continue
            path = img.get('path', '')
            if path and not os.path.exists(path) and path_resolver is not None:
                located = path_resolver(path)
                if located:
                    img = dict(img)
                    img['path'] = located
                    path = located
            if not path or not os.path.exists(path):
                unavailable += 1
                continue
            img = dict(img)
            img['name'] = cross_platform_basename(path)
            aois = img.get('areas_of_interest', [])
            reviewed = [aoi for aoi in aois
                        if aoi.get('flagged', False) or aoi.get('user_comment')]
            if reviewed:
                img['areas_of_interest'] = reviewed
            elif not include_images_without_flagged_aois:
                continue
            total_aois += len(img['areas_of_interest'])
            images.append(img)

        return cls(
            xml_path=merged_run.xml_path,
            run_name=merged_run.run_name,
            images=images,
            xml_service=merged_run.xml_service,
            settings=merged_run.settings,
            position_format=position_format,
            distance_unit=distance_unit,
            use_terrain_elevation=use_terrain_elevation,
            unavailable_count=unavailable,
            total_aoi_count=total_aois,
            reviewer_names=merged_run.reviewer_names,
        )


class CombinedPdfReportService(PdfGeneratorService):
    """Collate several results XMLs into one PDF report."""

    def __init__(self, organization="", search_name="",
                 include_images_without_flagged_aois=False,
                 map_tile_source="map",
                 position_format='Lat/Long - Decimal Degrees',
                 distance_unit='ft', use_terrain_elevation=True,
                 recovery_session=None):
        """
        Args:
            organization: Organization name for the cover.
            search_name: Search/mission name for the cover.
            include_images_without_flagged_aois: Report scope flag, applied
                per run exactly as in the single-run report.
            map_tile_source: 'map' or 'satellite' for the overview map.
            position_format: PositionFormat preference string.
            distance_unit: 'ft' or 'm' (already normalized).
            use_terrain_elevation: UseTerrainElevation preference.
            recovery_session: Optional RecoverySession from the folder scan.
                Lets an XML that travelled without its images (a reviewer's
                copy) find them under the scanned tree.
        """
        super().__init__(
            viewer=None,
            organization=organization,
            search_name=search_name,
            images=[],
            include_images_without_flagged_aois=include_images_without_flagged_aois,
            map_tile_source=map_tile_source,
        )
        self.position_format = position_format
        self.distance_unit = distance_unit
        self.use_terrain_elevation = use_terrain_elevation
        self.recovery_session = recovery_session

    def _path_resolver(self):
        """callable(stored_path) -> located path, from the scan session."""
        session = self.recovery_session
        if session is None:
            return None
        return session.resolve_file

    def load_contexts(self, xml_paths):
        """Parse, group and merge every results XML into report contexts.

        Copies of the SAME run (identical detection payload; several people
        reviewed the same batch on different computers) are merged into one
        context carrying combined flags, comments and corrected positions.
        Unreadable files are skipped with a log.
        """
        merge_service = ReviewMergeService(logger=self.logger)
        records = merge_service.load_run_records(xml_paths)
        contexts = []
        for group in merge_service.group_records(records):
            try:
                merged = merge_service.merge_group(group)
                contexts.append(RunReportContext.from_merged(
                    merged, self.position_format, self.distance_unit,
                    include_images_without_flagged_aois=self.include_images_without_flagged_aois,
                    use_terrain_elevation=self.use_terrain_elevation,
                    path_resolver=self._path_resolver(),
                ))
            except Exception as e:
                self.logger.error(
                    f"Combined report: skipping run group "
                    f"({group[0].xml_path}): {e}")
        return contexts

    def generate_combined_report(self, output_path, xml_paths,
                                 progress_callback=None, cancel_check=None):
        """Generate the collated PDF.

        Args:
            output_path: Destination PDF path.
            xml_paths: The ADIAT_Data.xml files to collate.
            progress_callback: Optional (current, total, message) callback.
            cancel_check: Optional callable returning True to abort.

        Raises:
            ValueError: When no run contributes any exportable image.
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if progress_callback:
                progress_callback(0, 100, "Reading results files...")
            contexts = self.load_contexts(xml_paths)
            usable = [ctx for ctx in contexts if ctx.images]
            if not usable:
                raise ValueError(
                    "None of the results contain exportable images on this computer")

            # Unique-per-run image names keep the text-derived TOC bookmark
            # keys collision-free (WALDO names repeat between flights).
            for run_idx, ctx in enumerate(usable, start=1):
                for img in ctx.images:
                    img['name'] = f"[{run_idx}] {img['name']}"

            self.doc = PDFDocTemplate(
                output_path,
                organization=self.organization,
                pagesize=letter,
                progress_callback=progress_callback,
            )
            self.story = []

            # ---- cover ----
            self._add_logo()
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.story.append(Paragraph(
                f"{self.organization} - {self.search_name}<br/>{current_datetime}",
                self.h1))
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph(
                f"Combined report of {len(usable)} result sets", self.styles['Normal']))
            self.story.append(Spacer(1, 16))

            # ---- run summary table (every scanned run, even skipped ones) ----
            self._add_run_summary_table(contexts)
            self.story.append(Spacer(1, 20))

            # ---- combined overview map: all runs' images on one map ----
            if progress_callback:
                progress_callback(0, 100, "Building combined overview map...")
            self.viewer = usable[0]
            self.images = [img for ctx in usable for img in ctx.images]
            map_path = self._generate_overview_map()
            if map_path:
                map_img = Image(map_path, width=7 * inch, height=5.25 * inch)
                map_img.hAlign = 'CENTER'
                self.story.append(map_img)
            self.story.append(PageBreak())

            # ---- per-run sections ----
            grand_total = sum(ctx.total_aoi_count for ctx in usable)
            offset = 0
            for run_idx, ctx in enumerate(usable, start=1):
                if cancel_check and cancel_check():
                    return
                self.viewer = ctx
                self.images = ctx.images

                # Unique numeric prefix -> unique h2 bookmark key + TOC entry
                self.story.append(Paragraph(f"{run_idx}. {ctx.run_name}", self.h2))
                if ctx.review_count > 1:
                    names = ", ".join(ctx.reviewer_names)
                    self.story.append(Paragraph(
                        f"Merged from {ctx.review_count} reviewer copies "
                        f"({names}). Flags, comments and corrected positions "
                        f"are combined; each AOI appears once.",
                        self.styles['Normal']))
                if ctx.unavailable_count:
                    self.story.append(Paragraph(
                        f"{ctx.unavailable_count} image(s) were not available on this "
                        f"computer and were skipped.", self.styles['Normal']))
                self.story.append(Spacer(1, 8))

                self._add_run_settings(ctx)
                self.story.append(Spacer(1, 12))

                run_offset = offset

                def run_progress(current, total, message,
                                 _offset=run_offset, _name=ctx.run_name):
                    if progress_callback:
                        progress_callback(_offset + current, max(grand_total, 1),
                                          f"{_name}: {message}")

                self._add_image_details(
                    progress_callback=run_progress if progress_callback else None,
                    cancel_check=cancel_check)
                offset += ctx.total_aoi_count

                # Bound memory: one run's decoded images must not pile onto
                # the next run's.
                self._image_service_cache.clear()
                self._composite_service.clear_cache()

                self.story.append(PageBreak())

            if cancel_check and cancel_check():
                return

            # ---- TOC (inserted after the cover's PageBreak) + build ----
            if progress_callback:
                progress_callback(grand_total, max(grand_total, 1),
                                  "Preparing Table of Contents...")
            toc = self._create_toc()
            first_page_break_idx = next(
                (i for i, flowable in enumerate(self.story)
                 if isinstance(flowable, PageBreak)), -1)
            if first_page_break_idx != -1:
                insert_pos = first_page_break_idx + 1
                self.story[insert_pos:insert_pos] = [toc, PageBreak()]
            else:
                self.story[0:0] = [toc, PageBreak()]

            self.doc.total_flowables = len(self.story)
            if progress_callback:
                progress_callback(0, 100, "Starting PDF build...")
            self.doc.multiBuild(self.story)
            if progress_callback:
                progress_callback(100, 100, "PDF generation complete!")

        except Exception as e:
            self.logger.error(f"Combined PDF generation failed: {e}")
            raise
        finally:
            self._cleanup_temp_files()
            self._clear_caches()

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _add_logo(self):
        """Cover logo, identical to the single-run report's."""
        logo_pixmap = QPixmap(":/ADIAT_Full.png")
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        logo_pixmap.save(buffer, "PNG")
        logo_io = BytesIO(buffer.data())
        logo = Image(logo_io, width=2 * inch, height=2 * inch)
        logo.hAlign = 'CENTER'
        self.story.append(logo)
        self.story.append(Spacer(1, 12))

    def _add_run_summary_table(self, contexts):
        """One row per run: what is in this report, and what is not."""
        header = ["#", "Run", "Algorithm", "Images", "AOIs", "Reviewers", "Unavailable"]
        rows = [header]
        run_idx = 0
        for ctx in contexts:
            if ctx.images:
                run_idx += 1
                label = str(run_idx)
            else:
                label = "-"
            rows.append([
                label,
                ctx.run_name,
                ctx.settings.get('algorithm', 'Unknown'),
                str(len(ctx.images)),
                str(ctx.total_aoi_count),
                str(ctx.review_count) if ctx.review_count > 1 else "",
                str(ctx.unavailable_count) if ctx.unavailable_count else "",
            ])

        table = Table(rows, hAlign='CENTER')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3d3d3d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f0f0f0')]),
            ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ]))
        self.story.append(table)

    def _add_run_settings(self, ctx):
        """The run's algorithm settings, headed with a NON-TOC style.

        The base _add_algorithm_settings uses an h2 heading; repeated across
        runs that floods the TOC and collides the text-derived bookmark keys,
        so the body is reproduced here under a plain bold header.
        """
        self.story.append(Paragraph(
            "<b>Algorithm Settings</b>", self.styles['Normal']))
        settings = ctx.settings
        for key, value in settings.items():
            rgb_value = (value if isinstance(value, tuple)
                         else ColorUtils.parse_rgb_string(str(value)))
            if rgb_value and len(rgb_value) == 3:
                r, g, b = rgb_value
                color_hex = f"#{r:02x}{g:02x}{b:02x}"
                self.story.append(Paragraph(
                    f"{key}: {value} <font color='{color_hex}'>■</font>",
                    self.styles['Normal']))
            elif isinstance(value, dict):
                nested_values = []
                for k, v in value.items():
                    nested_rgb = ColorUtils.parse_rgb_string(str(v))
                    if nested_rgb and len(nested_rgb) == 3:
                        r, g, b = nested_rgb
                        color_hex = f"#{r:02x}{g:02x}{b:02x}"
                        nested_values.append(f"{k}: {v} <font color='{color_hex}'>■</font>")
                    else:
                        nested_values.append(f"{k}: {v}")
                self.story.append(Paragraph(
                    f"{key}: {{{', '.join(nested_values)}}}", self.styles['Normal']))
            else:
                self.story.append(Paragraph(f"{key}: {value}", self.styles['Normal']))
