"""
TeamPlanningController - Business logic for team-based AOI assignment.

Manages the lifecycle of the TeamPlanningDialog, builds the AOI dataset
from the viewer's flagged AOIs, handles team CRUD, assignment persistence,
and delegates PDF export to TeamPdfExportService.
"""

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication

from core.views.images.viewer.dialogs.TeamPlanningDialog import TeamPlanningDialog
from core.views.images.viewer.dialogs.ExportProgressDialog import ExportProgressDialog
from core.services.image.AOIService import AOIService
from core.services.export.TeamPdfExportService import TeamPdfExportService
from core.services.LoggerService import LoggerService
from helpers.TranslationMixin import TranslationMixin
from helpers.MetaDataHelper import MetaDataHelper
from helpers.LocationInfo import LocationInfo

import os


class TeamPlanningController(TranslationMixin, QObject):
    """Orchestrates team-planning workflow between Viewer and dialog."""

    def __init__(self, parent_viewer):
        super().__init__(parent_viewer)
        self.viewer = parent_viewer
        self.logger = LoggerService()
        self.dialog: TeamPlanningDialog | None = None

        # Flat list of dicts used by map and lists.
        # Each entry: {uid, image_index, aoi_index, latitude, longitude,
        #              image_name, team, team_color, area, flagged, ...}
        self._aoi_entries: list[dict] = []
        self._uid_counter = 0

    # -------------------------------------------------------- public API
    def show(self):
        """Open (or re-focus) the team planning dialog."""
        self._build_aoi_entries()

        if not self._aoi_entries:
            QMessageBox.information(
                self.viewer,
                self.tr("No Flagged AOIs"),
                self.tr(
                    "There are no flagged AOIs to assign.\n\n"
                    "Flag at least one AOI in the viewer before "
                    "using Plan Verification."
                ),
            )
            return

        if self.dialog is None or not self.dialog.isVisible():
            self.dialog = TeamPlanningDialog(self.viewer)
            self._wire_signals()
            self._load_persisted_state()
            self.dialog.show()
        else:
            self.dialog.raise_()
            self.dialog.activateWindow()

        self._push_data_to_dialog()

    def close(self):
        if self.dialog and self.dialog.isVisible():
            self.dialog.close()
            self.dialog = None

    # ------------------------------------------------ data construction
    def _build_aoi_entries(self):
        """Collect all flagged AOIs with GPS positions into a flat list."""
        self._aoi_entries.clear()
        self._uid_counter = 0
        flagged = self.viewer.aoi_controller.flagged_aois
        images = self.viewer.images
        use_terrain = getattr(self.viewer, 'use_terrain_elevation', True)

        for img_idx, aoi_indices in flagged.items():
            if img_idx >= len(images):
                continue
            img = images[img_idx]
            if img.get('hidden', False):
                continue
            aois = img.get('areas_of_interest', [])
            aoi_service = AOIService(img)

            for aoi_idx in sorted(aoi_indices):
                if aoi_idx >= len(aois):
                    continue
                aoi = aois[aoi_idx]
                gps = aoi_service.calculate_gps_with_custom_altitude(
                    img, aoi, use_terrain=use_terrain,
                )
                if gps is None:
                    continue
                lat, lon = gps

                team_name = aoi.get('team', '')
                self._aoi_entries.append({
                    'uid': self._uid_counter,
                    'image_index': img_idx,
                    'aoi_index': aoi_idx,
                    'latitude': lat,
                    'longitude': lon,
                    'image_name': os.path.basename(img.get('path', '')),
                    'team': team_name,
                    'team_color': '',
                    'area': aoi.get('area', 0),
                })
                self._uid_counter += 1

        self._sync_team_colors()

    def _sync_team_colors(self):
        """Set team_color on every entry based on current team definitions."""
        if self.dialog:
            teams = self.dialog.get_teams()
        else:
            teams = self.viewer.xml_service.get_team_planning()
        color_map = {t['name']: t['color'] for t in teams}
        for e in self._aoi_entries:
            e['team_color'] = color_map.get(e['team'], '')

    # --------------------------------------------------- persistence
    def _load_persisted_state(self):
        """Restore teams and assignments from XML."""
        teams = self.viewer.xml_service.get_team_planning()
        if teams and self.dialog:
            self.dialog.set_teams(teams)

    def _persist_teams(self):
        """Write current team list to XML."""
        if not self.dialog:
            return
        teams = self.dialog.get_teams()
        self.viewer.xml_service.save_team_planning(teams)
        self.viewer.xml_service.save_xml_file(self.viewer.xml_path)

    def _persist_assignment(self, entry: dict):
        """Write a single AOI team assignment to XML."""
        self.viewer.xml_service.save_aoi_team(
            entry['image_index'], entry['aoi_index'],
            entry['team'], self.viewer.images,
        )
        self.viewer.xml_service.save_xml_file(self.viewer.xml_path)

    # --------------------------------------------------- signal wiring
    def _wire_signals(self):
        d = self.dialog
        d.teams_changed.connect(self._on_teams_changed)
        d.map_view.selection_changed.connect(self._on_map_selection_changed)

        # Replace dialog placeholder connections with controller logic
        try:
            d.team_list.currentRowChanged.disconnect()
        except RuntimeError:
            pass
        d.team_list.currentRowChanged.connect(self._on_team_selected)

        try:
            d.aoi_list.currentRowChanged.disconnect()
        except RuntimeError:
            pass
        d.aoi_list.currentRowChanged.connect(self._on_aoi_list_clicked)

        try:
            d.btn_assign.clicked.disconnect()
        except RuntimeError:
            pass
        d.btn_assign.clicked.connect(self._on_assign)

        d.export_team_pdf.connect(self._export_single_team_pdf)
        d.export_all_pdfs.connect(self._export_all_pdfs)

    # -------------------------------------------------------- handlers
    def _push_data_to_dialog(self):
        """Send current AOI data to the dialog's map and refresh counts."""
        self._sync_team_colors()
        self.dialog.map_view.set_aoi_data(self._aoi_entries)
        self._refresh_counts()

    def _on_teams_changed(self):
        self._persist_teams()
        # Unassign AOIs that belong to a team that no longer exists
        valid_names = {t['name'] for t in self.dialog.get_teams()}
        for entry in self._aoi_entries:
            if entry.get('team') and entry['team'] not in valid_names:
                entry['team'] = ''
                self._persist_assignment(entry)
        self._sync_team_colors()
        uid_colors = {e['uid']: e['team_color'] for e in self._aoi_entries}
        self.dialog.map_view.update_marker_colors(uid_colors)
        self._refresh_counts()

    def _on_map_selection_changed(self, uids: list[int]):
        """Visual feedback only — actual assignment happens on button click."""
        pass

    def _on_assign(self):
        """Assign selected AOIs on the map to the currently selected team."""
        if not self.dialog:
            return
        team_name = self.dialog.get_selected_team_name()
        if team_name is None:
            QMessageBox.information(
                self.dialog,
                self.tr("No Team Selected"),
                self.tr("Select a target team (or 'Unassigned') in the list first."),
            )
            return

        selected_uids = self.dialog.map_view.get_selected_uids()
        if not selected_uids:
            QMessageBox.information(
                self.dialog,
                self.tr("No AOIs Selected"),
                self.tr(
                    "Select one or more AOIs on the map first.\n"
                    "Click on markers, or use Rectangle Select for area selection."
                ),
            )
            return

        uid_set = set(selected_uids)
        for entry in self._aoi_entries:
            if entry['uid'] in uid_set:
                entry['team'] = team_name
                self._persist_assignment(entry)

        self._sync_team_colors()
        uid_colors = {e['uid']: e['team_color'] for e in self._aoi_entries}
        self.dialog.map_view.update_marker_colors(uid_colors)
        self.dialog.map_view.clear_selection()
        self._refresh_counts()
        self._refresh_aoi_list_for_selected_team()

    def _on_team_selected(self, row: int):
        self._refresh_aoi_list_for_selected_team()
        # Highlight on map
        if self.dialog:
            team_name = self.dialog.get_selected_team_name()
            self.dialog.map_view.highlight_team(
                team_name if team_name else None, self._aoi_entries,
            )

    def _on_aoi_list_clicked(self, row: int):
        """Centre the map on the clicked AOI."""
        if not self.dialog or row < 0:
            return
        item = self.dialog.aoi_list.item(row)
        if not item:
            return
        uid = item.data(Qt.ItemDataRole.UserRole)
        entry = next((e for e in self._aoi_entries if e['uid'] == uid), None)
        if entry:
            pt = self.dialog.map_view._lat_lon_to_scene(
                entry['latitude'], entry['longitude'],
            )
            self.dialog.map_view.centerOn(pt)

    # ------------------------------------------------------- refresh
    def _refresh_counts(self):
        if not self.dialog:
            return
        unassigned = sum(1 for e in self._aoi_entries if not e.get('team'))
        self.dialog.update_unassigned_count(unassigned)
        for team in self.dialog.get_teams():
            count = sum(
                1 for e in self._aoi_entries if e.get('team') == team['name']
            )
            self.dialog.update_team_count(team['name'], count)

    def _refresh_aoi_list_for_selected_team(self):
        if not self.dialog:
            return
        team_name = self.dialog.get_selected_team_name()
        if team_name is None:
            self.dialog.set_aoi_list_items([])
            return
        items = []
        for e in self._aoi_entries:
            matches = (e.get('team') == team_name) if team_name else not e.get('team')
            if matches:
                items.append({
                    'label': f"AOI #{e['aoi_index'] + 1} - {e['image_name']}",
                    'uid': e['uid'],
                })
        self.dialog.set_aoi_list_items(items)

    # ------------------------------------------------------- PDF export
    def _export_single_team_pdf(self, team_name: str):
        """Generate a PDF report for one team."""
        team_entries = [e for e in self._aoi_entries if e.get('team') == team_name]
        if not team_entries:
            QMessageBox.information(
                self.dialog,
                self.tr("No AOIs"),
                self.tr("Team '{name}' has no assigned AOIs.").format(name=team_name),
            )
            return

        teams = self.dialog.get_teams() if self.dialog else []
        team_color = next(
            (t['color'] for t in teams if t['name'] == team_name), '#888888'
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self.dialog,
            self.tr("Save Team PDF"),
            f"Verification_{team_name}.pdf",
            self.tr("PDF files (*.pdf)"),
        )
        if not file_path:
            return

        self._run_pdf_generation(
            file_path, team_entries, team_name, team_color, teams,
        )

    def _export_all_pdfs(self):
        """Generate per-team PDFs + master summary in a chosen folder."""
        folder = QFileDialog.getExistingDirectory(
            self.dialog, self.tr("Select Export Folder"),
        )
        if not folder:
            return

        teams = self.dialog.get_teams() if self.dialog else []
        all_entries = self._aoi_entries

        progress = ExportProgressDialog(
            self.dialog,
            title=self.tr("Exporting Team PDFs"),
            total_items=len(teams) + 1,
        )
        progress.show()
        QApplication.processEvents()

        try:
            for i, team in enumerate(teams):
                if progress.is_cancelled():
                    break
                team_entries = [
                    e for e in all_entries if e.get('team') == team['name']
                ]
                if not team_entries:
                    continue
                path = os.path.join(folder, f"Verification_{team['name']}.pdf")
                progress.update_progress(
                    i, len(teams) + 1,
                    self.tr("Generating PDF for {name}...").format(name=team['name']),
                )
                QApplication.processEvents()
                self._generate_team_pdf(
                    path, team_entries, team['name'], team['color'], teams,
                )

            if not progress.is_cancelled():
                # Master summary
                progress.update_progress(
                    len(teams), len(teams) + 1,
                    self.tr("Generating master summary..."),
                )
                QApplication.processEvents()
                master_path = os.path.join(folder, "Verification_Summary.pdf")
                self._generate_master_pdf(master_path, all_entries, teams)

                progress.update_progress(
                    len(teams) + 1, len(teams) + 1,
                    self.tr("Export complete"),
                )

        except Exception as exc:
            self.logger.error(f"Team PDF export failed: {exc}")
            QMessageBox.critical(
                self.dialog,
                self.tr("Export Error"),
                self.tr("PDF generation failed: {error}").format(error=str(exc)),
            )
        finally:
            progress.accept()

        if not progress.is_cancelled():
            QMessageBox.information(
                self.dialog,
                self.tr("Export Complete"),
                self.tr("Team PDFs saved to:\n{folder}").format(folder=folder),
            )

    # ------------------------------------------------ PDF generation helpers
    def _make_pdf_service(self):
        """Create a TeamPdfExportService using the dialog's current tile source."""
        tile_src = self.dialog.get_map_tile_source() if self.dialog else 'map'
        return TeamPdfExportService(
            self.viewer,
            logger=self.logger,
            map_tile_source=tile_src,
        )

    def _run_pdf_generation(self, path, entries, team_name, team_color, teams):
        progress = ExportProgressDialog(
            self.dialog,
            title=self.tr("Generating PDF Report"),
            total_items=len(entries),
        )
        progress.show()
        QApplication.processEvents()

        try:
            self._generate_team_pdf(path, entries, team_name, team_color, teams)
            progress.update_progress(len(entries), len(entries), self.tr("Done"))
            progress.accept()
            QMessageBox.information(
                self.dialog,
                self.tr("Success"),
                self.tr("PDF report generated successfully!"),
            )
        except Exception as exc:
            self.logger.error(f"Team PDF generation failed: {exc}")
            progress.reject()
            QMessageBox.critical(
                self.dialog,
                self.tr("Export Error"),
                self.tr("PDF generation failed: {error}").format(error=str(exc)),
            )

    def _generate_team_pdf(self, path, entries, team_name, team_color, teams):
        svc = self._make_pdf_service()
        svc.generate_team_report(
            output_path=path,
            aoi_entries=entries,
            team_name=team_name,
            team_color=team_color,
            all_entries=self._aoi_entries,
            teams=teams,
        )

    def _generate_master_pdf(self, path, all_entries, teams):
        svc = self._make_pdf_service()
        svc.generate_master_report(
            output_path=path,
            all_entries=all_entries,
            teams=teams,
        )
