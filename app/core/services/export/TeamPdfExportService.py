"""
TeamPdfExportService - PDF report generation for team-based AOI verification.

Inherits from PdfGeneratorService to reuse all existing PDF features (composite
images with 0x/3x/6x zoom, GPS links, confidence scores, colour info, overview
map, north-up rotation, etc.) and adds team-specific report structure.
"""

import cv2
import numpy as np
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QBuffer

from core.services.export.PdfGeneratorService import PdfGeneratorService, PDFDocTemplate
from core.services.LoggerService import LoggerService


class TeamPdfExportService(PdfGeneratorService):
    """Generates per-team and master summary PDFs for field verification.

    Extends PdfGeneratorService so every AOI detail page retains the full
    composite image (0x/3x/6x), metadata, GPS links, confidence, colour,
    and all other features from the standard report.
    """

    def __init__(self, viewer, logger=None, organization="", search_name="",
                 map_tile_source="map"):
        super().__init__(
            viewer,
            organization=organization,
            search_name=search_name,
            images=None,
            include_images_without_flagged_aois=False,
            map_tile_source=map_tile_source,
        )
        if logger:
            self.logger = logger

    # =================================================================
    #  Per-team report
    # =================================================================
    def generate_team_report(
        self, output_path, aoi_entries, team_name, team_color,
        all_entries, teams, progress_callback=None, cancel_check=None,
    ):
        """Create a PDF for a single team with full AOI detail pages.

        Args:
            output_path: Destination file path.
            aoi_entries: List of entry dicts belonging to this team.
            team_name: Display name of the team.
            team_color: Hex colour string for this team.
            all_entries: Complete list (all teams) for the overview map context.
            teams: Full team definitions list [{name, color}].
            progress_callback: Optional (current, total, message) callback.
            cancel_check: Optional callable returning True to abort.
        """
        try:
            self.story = []
            team_images = self._entries_to_images(aoi_entries)
            self.images = team_images

            self.doc = PDFDocTemplate(
                output_path,
                organization=self.organization,
                pagesize=letter,
                progress_callback=progress_callback,
            )

            # --- cover page ---
            self._add_cover(
                title="Field Verification Report",
                subtitle=team_name,
                extra_lines=[f"AOIs assigned: {len(aoi_entries)}"],
            )

            # --- team overview map (colour-coded by team) ---
            team_map = self._generate_team_overview_map(
                all_entries, teams, highlight_team=team_name,
            )
            if team_map:
                self.story.append(Paragraph("Team Overview Map", self.h2))
                map_img = Image(team_map, width=7 * inch, height=5.25 * inch)
                map_img.hAlign = 'CENTER'
                self.story.append(map_img)
                self.story.append(PageBreak())

            # --- standard overview map (image GPS + flagged AOI markers) ---
            std_map = self._generate_overview_map()
            if std_map:
                self.story.append(Paragraph("AOI Overview Map", self.h2))
                map_img = Image(std_map, width=7 * inch, height=5.25 * inch)
                map_img.hAlign = 'CENTER'
                self.story.append(map_img)
                self.story.append(PageBreak())

            # --- full AOI detail pages (inherited from PdfGeneratorService) ---
            self._add_image_details(
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

            self.doc.multiBuild(self.story)

        except Exception as e:
            self.logger.error(f"Team PDF generation failed: {e}")
            raise
        finally:
            self._cleanup_temp_files()
            self._clear_caches()

    # =================================================================
    #  Master summary report
    # =================================================================
    def generate_master_report(self, output_path, all_entries, teams,
                               progress_callback=None, cancel_check=None):
        """Create a summary PDF showing all teams and their assignments."""
        try:
            self.story = []
            all_images = self._entries_to_images(all_entries)
            self.images = all_images

            self.doc = PDFDocTemplate(
                output_path,
                organization=self.organization,
                pagesize=letter,
                progress_callback=progress_callback,
            )

            # --- cover ---
            unassigned_count = sum(1 for e in all_entries if not e.get('team'))
            self._add_cover(
                title="Verification Summary",
                extra_lines=[
                    f"Total flagged AOIs: {len(all_entries)}",
                    f"Teams: {len(teams)}",
                    f"Unassigned: {unassigned_count}",
                ],
            )

            # --- team table ---
            self._add_team_table(all_entries, teams)
            self.story.append(PageBreak())

            # --- team overview map ---
            team_map = self._generate_team_overview_map(all_entries, teams)
            if team_map:
                self.story.append(Paragraph("Overview Map — All Teams", self.h2))
                map_img = Image(team_map, width=7 * inch, height=5.25 * inch)
                map_img.hAlign = 'CENTER'
                self.story.append(map_img)
                self.story.append(PageBreak())

            # --- per-team AOI lists ---
            for t in teams:
                entries = [e for e in all_entries if e.get('team') == t['name']]
                if not entries:
                    continue
                self.story.append(Paragraph(f"{t['name']} ({len(entries)} AOIs)", self.h2))
                for e in entries:
                    self.story.append(Paragraph(
                        f"&bull; AOI #{e['aoi_index'] + 1} — {e['image_name']} "
                        f"(Lat {e['latitude']:.6f}, Lon {e['longitude']:.6f})",
                        self.styles['Normal'],
                    ))
                self.story.append(PageBreak())

            # Unassigned section
            unassigned_entries = [e for e in all_entries if not e.get('team')]
            if unassigned_entries:
                self.story.append(Paragraph(
                    f"Unassigned ({len(unassigned_entries)} AOIs)", self.h2,
                ))
                for e in unassigned_entries:
                    self.story.append(Paragraph(
                        f"&bull; AOI #{e['aoi_index'] + 1} — {e['image_name']} "
                        f"(Lat {e['latitude']:.6f}, Lon {e['longitude']:.6f})",
                        self.styles['Normal'],
                    ))
                self.story.append(PageBreak())

            # --- full AOI detail pages ---
            self._add_image_details(
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )

            self.doc.multiBuild(self.story)

        except Exception as e:
            self.logger.error(f"Master PDF generation failed: {e}")
            raise
        finally:
            self._cleanup_temp_files()
            self._clear_caches()

    # =================================================================
    #  Helpers
    # =================================================================
    def _add_cover(self, title, subtitle=None, extra_lines=None):
        """Add a styled cover page."""
        logo_pixmap = QPixmap(":/ADIAT_Full.png")
        buf = QBuffer()
        buf.open(QBuffer.ReadWrite)
        logo_pixmap.save(buf, "PNG")
        logo = Image(BytesIO(buf.data()), width=2 * inch, height=2 * inch)
        logo.hAlign = 'CENTER'
        self.story.append(logo)
        self.story.append(Spacer(1, 12))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        heading_parts = [title]
        if subtitle:
            heading_parts.append(f"<b>{subtitle}</b>")
        heading_parts.append(now)
        self.story.append(Paragraph("<br/>".join(heading_parts), self.h1))
        self.story.append(Spacer(1, 12))

        if extra_lines:
            for line in extra_lines:
                self.story.append(Paragraph(line, self.styles['Normal']))
        self.story.append(PageBreak())

    def _add_team_table(self, all_entries, teams):
        """Add a summary table of teams and AOI counts."""
        table_data = [['Team', 'AOIs Assigned']]
        for t in teams:
            count = sum(1 for e in all_entries if e.get('team') == t['name'])
            table_data.append([t['name'], str(count)])
        unassigned = sum(1 for e in all_entries if not e.get('team'))
        if unassigned:
            table_data.append(['(Unassigned)', str(unassigned)])

        tbl = Table(table_data, colWidths=[4 * inch, 2 * inch])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#ECF0F1')]),
        ]))
        self.story.append(tbl)

    def _entries_to_images(self, entries):
        """Convert flat AOI entry list into the image-dict format expected by
        PdfGeneratorService._add_image_details().

        Groups entries by image_index and creates image dicts with only the
        relevant AOIs included.
        """
        viewer_images = self.viewer.images
        grouped: dict[int, list] = {}
        for e in entries:
            grouped.setdefault(e['image_index'], []).append(e)

        result = []
        for img_idx in sorted(grouped.keys()):
            if img_idx >= len(viewer_images):
                continue
            src = viewer_images[img_idx]
            img_copy = src.copy()
            all_aois = src.get('areas_of_interest', [])
            aoi_indices = sorted({e['aoi_index'] for e in grouped[img_idx]})
            img_copy['areas_of_interest'] = [
                all_aois[i] for i in aoi_indices if i < len(all_aois)
            ]
            if img_copy['areas_of_interest']:
                result.append(img_copy)
        return result

    # =================================================================
    #  Team-colour-coded overview map
    # =================================================================
    def _generate_team_overview_map(self, entries, teams, highlight_team=None):
        """Build an overview map with AOI positions colour-coded by team."""
        if not entries:
            return None

        try:
            lats = [e['latitude'] for e in entries]
            lons = [e['longitude'] for e in entries]
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)

            lat_range = max_lat - min_lat or 0.01
            lon_range = max_lon - min_lon or 0.01
            min_lat -= lat_range * 0.1
            max_lat += lat_range * 0.1
            min_lon -= lon_range * 0.1
            max_lon += lon_range * 0.1

            img_w, img_h = 2000, 1500
            map_img = self._download_map_tiles(
                min_lat, max_lat, min_lon, max_lon, img_w, img_h,
            )

            color_map = {t['name']: t['color'] for t in teams}

            def to_px(lat, lon):
                x = int((lon - min_lon) / (max_lon - min_lon) * img_w)
                y = int((max_lat - lat) / (max_lat - min_lat) * img_h)
                return x, y

            for e in entries:
                pt = to_px(e['latitude'], e['longitude'])
                hex_c = color_map.get(e.get('team', ''), '#BBBBBB')
                bgr = self._hex_to_bgr(hex_c)

                is_hl = (highlight_team is not None
                         and e.get('team') == highlight_team)
                radius = 10 if is_hl else 6
                cv2.circle(map_img, pt, radius, bgr, -1)
                cv2.circle(map_img, pt, radius + 2, (0, 0, 0), 2)

            # North arrow
            ax, ay = img_w - 80, 80
            cv2.circle(map_img, (ax, ay + 20), 35, (255, 255, 255), -1)
            cv2.circle(map_img, (ax, ay + 20), 35, (0, 0, 0), 2)
            cv2.arrowedLine(
                map_img, (ax, ay + 40), (ax, ay), (0, 0, 0), 3, tipLength=0.3,
            )
            cv2.putText(
                map_img, 'N', (ax - 10, ay - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2,
            )

            # Legend
            ly = img_h - (40 + 30 * len(teams) + 30)
            lx = 20
            legend_h = 30 * (len(teams) + 1) + 20
            cv2.rectangle(
                map_img, (lx - 10, ly - 10), (380, ly + legend_h),
                (255, 255, 255), -1,
            )
            cv2.rectangle(
                map_img, (lx - 10, ly - 10), (380, ly + legend_h),
                (0, 0, 0), 2,
            )

            for t in teams:
                bgr = self._hex_to_bgr(t['color'])
                cv2.circle(map_img, (lx + 15, ly + 15), 8, bgr, -1)
                cv2.circle(map_img, (lx + 15, ly + 15), 10, (0, 0, 0), 2)
                cv2.putText(
                    map_img, t['name'], (lx + 35, ly + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1,
                )
                ly += 30

            # Unassigned legend entry
            cv2.circle(map_img, (lx + 15, ly + 15), 8, (187, 187, 187), -1)
            cv2.circle(map_img, (lx + 15, ly + 15), 10, (0, 0, 0), 2)
            cv2.putText(
                map_img, 'Unassigned', (lx + 35, ly + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1,
            )

            temp_file = self._save_image_to_temp_file(map_img, quality=75)
            del map_img
            return temp_file

        except Exception as e:
            self.logger.error(f"Error generating team overview map: {e}")
            return None

    @staticmethod
    def _hex_to_bgr(hex_str: str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            return (187, 187, 187)
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return (b, g, r)
