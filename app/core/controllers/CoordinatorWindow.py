import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                               QTabWidget, QGroupBox, QProgressBar, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from core.services.LoggerService import LoggerService
from core.services.SearchProjectService import SearchProjectService


class CoordinatorWindow(QMainWindow):
    """Main window for coordinating multi-batch search reviews."""

    def __init__(self, theme="Light"):
        """
        Initialize the Coordinator Window.

        Args:
            theme (str): The current theme (Light/Dark).
        """
        super().__init__()
        self.theme = theme
        self.logger = LoggerService()
        self.project_service = None
        self.project_path = None

        self._setup_ui()
        self.setWindowTitle("Search Coordinator")
        self.resize(1200, 800)

    def _setup_ui(self):
        """Set up the main UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Top action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.new_project_btn = QPushButton("Create New Search")
        self.new_project_btn.setMinimumHeight(40)
        self.new_project_btn.clicked.connect(self._create_new_project)
        button_layout.addWidget(self.new_project_btn)

        self.open_project_btn = QPushButton("Open Existing Search")
        self.open_project_btn.setMinimumHeight(40)
        self.open_project_btn.clicked.connect(self._open_project)
        button_layout.addWidget(self.open_project_btn)

        self.save_project_btn = QPushButton("Save Search")
        self.save_project_btn.setMinimumHeight(40)
        self.save_project_btn.setEnabled(False)
        self.save_project_btn.clicked.connect(self._save_project)
        button_layout.addWidget(self.save_project_btn)

        self.add_batch_btn = QPushButton("Add Batches to Search")
        self.add_batch_btn.setMinimumHeight(40)
        self.add_batch_btn.setEnabled(False)
        self.add_batch_btn.setToolTip("Add more batch XML files to the current search project")
        self.add_batch_btn.clicked.connect(self._add_batches)
        button_layout.addWidget(self.add_batch_btn)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Project info section
        self.info_group = self._create_project_info_section()
        main_layout.addWidget(self.info_group)

        # Tabs for different views
        self.tab_widget = QTabWidget()

        # Dashboard tab
        self.dashboard_widget = self._create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")

        # Batch Status tab
        self.batch_status_widget = self._create_batch_status_tab()
        self.tab_widget.addTab(self.batch_status_widget, "Batch Status")

        # AOI Analysis tab
        self.aoi_analysis_widget = self._create_aoi_analysis_tab()
        self.tab_widget.addTab(self.aoi_analysis_widget, "AOI Analysis")

        main_layout.addWidget(self.tab_widget)

        # Bottom action buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        self.load_review_btn = QPushButton("Load Review XML")
        self.load_review_btn.setMinimumHeight(40)
        self.load_review_btn.setEnabled(False)
        self.load_review_btn.clicked.connect(self._load_review)
        bottom_layout.addWidget(self.load_review_btn)

        self.export_results_btn = QPushButton("Export Consolidated Results")
        self.export_results_btn.setMinimumHeight(40)
        self.export_results_btn.setEnabled(False)
        self.export_results_btn.clicked.connect(self._export_results)
        bottom_layout.addWidget(self.export_results_btn)

        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def _create_project_info_section(self):
        """Create the project information section."""
        group = QGroupBox("Project Information")
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Project Name
        self.project_name_label = QLabel("No project loaded")
        self.project_name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(QLabel("Project:"))
        layout.addWidget(self.project_name_label)

        # Created by
        self.created_by_label = QLabel("-")
        layout.addWidget(QLabel("Created by:"))
        layout.addWidget(self.created_by_label)

        # Created date
        self.created_date_label = QLabel("-")
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.created_date_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_dashboard_tab(self):
        """Create the visual dashboard tab with key metrics and progress."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Top metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        # Create metric cards
        self.total_batches_card = self._create_metric_card("Total Batches", "0", "#3498db")
        self.total_images_card = self._create_metric_card("Total Images", "0", "#9b59b6")
        self.total_reviews_card = self._create_metric_card("Total Reviews", "0", "#2ecc71")
        self.unique_reviewers_card = self._create_metric_card("Reviewers", "0", "#e67e22")

        metrics_layout.addWidget(self.total_batches_card)
        metrics_layout.addWidget(self.total_images_card)
        metrics_layout.addWidget(self.total_reviews_card)
        metrics_layout.addWidget(self.unique_reviewers_card)

        layout.addLayout(metrics_layout)

        # Progress section
        progress_group = QGroupBox("Review Progress")
        progress_layout = QVBoxLayout()

        # Overall completion
        completion_layout = QHBoxLayout()
        completion_layout.addWidget(QLabel("Overall Completion:"))
        self.completion_progress = QProgressBar()
        self.completion_progress.setMinimumHeight(30)
        self.completion_progress.setTextVisible(True)
        completion_layout.addWidget(self.completion_progress)
        self.completion_percent_label = QLabel("0%")
        self.completion_percent_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        completion_layout.addWidget(self.completion_percent_label)
        progress_layout.addLayout(completion_layout)

        # Batch status breakdown
        status_layout = QHBoxLayout()

        # Not Reviewed
        not_reviewed_layout = QVBoxLayout()
        self.not_reviewed_count = QLabel("0")
        self.not_reviewed_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c;")
        self.not_reviewed_count.setAlignment(Qt.AlignCenter)
        not_reviewed_layout.addWidget(self.not_reviewed_count)
        not_reviewed_layout.addWidget(QLabel("Not Reviewed"), alignment=Qt.AlignCenter)
        status_layout.addLayout(not_reviewed_layout)

        # In Progress
        in_progress_layout = QVBoxLayout()
        self.in_progress_count = QLabel("0")
        self.in_progress_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #f39c12;")
        self.in_progress_count.setAlignment(Qt.AlignCenter)
        in_progress_layout.addWidget(self.in_progress_count)
        in_progress_layout.addWidget(QLabel("In Progress"), alignment=Qt.AlignCenter)
        status_layout.addLayout(in_progress_layout)

        # Complete
        complete_layout = QVBoxLayout()
        self.complete_count = QLabel("0")
        self.complete_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #27ae60;")
        self.complete_count.setAlignment(Qt.AlignCenter)
        complete_layout.addWidget(self.complete_count)
        complete_layout.addWidget(QLabel("Complete"), alignment=Qt.AlignCenter)
        status_layout.addLayout(complete_layout)

        progress_layout.addLayout(status_layout)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # AOI Summary section
        aoi_group = QGroupBox("AOI Summary")
        aoi_layout = QHBoxLayout()

        total_aois_layout = QVBoxLayout()
        self.total_aois_count = QLabel("0")
        self.total_aois_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db;")
        self.total_aois_count.setAlignment(Qt.AlignCenter)
        total_aois_layout.addWidget(self.total_aois_count)
        total_aois_layout.addWidget(QLabel("Total AOIs"), alignment=Qt.AlignCenter)
        aoi_layout.addLayout(total_aois_layout)

        flagged_aois_layout = QVBoxLayout()
        self.flagged_aois_count = QLabel("0")
        self.flagged_aois_count.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c;")
        self.flagged_aois_count.setAlignment(Qt.AlignCenter)
        flagged_aois_layout.addWidget(self.flagged_aois_count)
        flagged_aois_layout.addWidget(QLabel("Flagged AOIs"), alignment=Qt.AlignCenter)
        aoi_layout.addLayout(flagged_aois_layout)

        aoi_group.setLayout(aoi_layout)
        layout.addWidget(aoi_group)

        # Reviewer list
        reviewer_group = QGroupBox("Active Reviewers")
        reviewer_layout = QVBoxLayout()
        self.reviewer_list = QLabel("No reviewers yet")
        self.reviewer_list.setWordWrap(True)
        reviewer_layout.addWidget(self.reviewer_list)
        reviewer_group.setLayout(reviewer_layout)
        layout.addWidget(reviewer_group)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_metric_card(self, title, value, color):
        """Create a metric display card."""
        card = QGroupBox(title)
        card.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {color};
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 5px;
            }}
        """)

        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        card.setLayout(layout)

        # Store reference to value label for updating
        card.value_label = value_label

        return card

    def _create_batch_status_tab(self):
        """Create the batch status table tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel("Batch review status and assignments. Load reviewer XMLs to update progress.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Table
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(6)
        self.batch_table.setHorizontalHeaderLabels([
            "Batch ID", "Algorithm", "Images", "Reviews", "Reviewers", "Status"
        ])
        self.batch_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.batch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.batch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.batch_table.setAlternatingRowColors(True)

        layout.addWidget(self.batch_table)

        widget.setLayout(layout)
        return widget

    def _create_aoi_analysis_tab(self):
        """Create the AOI analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel("Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Table
        self.aoi_table = QTableWidget()
        self.aoi_table.setColumnCount(5)
        self.aoi_table.setHorizontalHeaderLabels([
            "Image", "Location", "Flag Count", "Reviewers", "Comments"
        ])
        self.aoi_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.aoi_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.aoi_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.aoi_table.setAlternatingRowColors(True)

        layout.addWidget(self.aoi_table)

        widget.setLayout(layout)
        return widget

    def _create_new_project(self):
        """Create a new search project."""
        from PySide6.QtWidgets import QInputDialog

        # Get project name
        project_name, ok = QInputDialog.getText(
            self,
            "New Search Project",
            "Enter project name:"
        )

        if not ok or not project_name:
            return

        # Get coordinator name
        coordinator_name, ok = QInputDialog.getText(
            self,
            "Coordinator Information",
            "Enter your name:"
        )

        if not ok:
            return

        # Select batch XML files
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Select Batch Files")
        msg.setText("Select Initial Batch XML Files")
        msg.setInformativeText(
            "You can select multiple ADIAT_Data.xml files from different folders.\n\n"
            "Tips:\n"
            "• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files\n"
            "• You can add more batches later using 'Add Batches to Search' button\n"
            "• Each batch should be a processed ADIAT_Data.xml file"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if msg.exec() != QMessageBox.Ok:
            return

        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)",
            "",
            "XML Files (*.xml)"
        )

        if not file_paths:
            return

        # Create project
        self.project_service = SearchProjectService()
        if self.project_service.create_new_project(project_name, file_paths, coordinator_name):
            # Save project
            default_name = f"ADIAT_Search_{project_name.replace(' ', '_')}.xml"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Search Project",
                default_name,
                "XML Files (*.xml)"
            )

            if save_path:
                if self.project_service.save_project(save_path):
                    self.project_path = save_path
                    self._update_all_displays()
                    self._enable_project_controls(True)
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Search project '{project_name}' created successfully!"
                    )
                else:
                    QMessageBox.critical(self, "Error", "Failed to save project file.")
        else:
            QMessageBox.critical(self, "Error", "Failed to create project.")

    def _open_project(self):
        """Open an existing search project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Search Project",
            "",
            "Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)"
        )

        if not file_path:
            return

        self.project_service = SearchProjectService(file_path)
        if self.project_service.load_project(file_path):
            self.project_path = file_path
            self._update_all_displays()
            self._enable_project_controls(True)
            QMessageBox.information(self, "Success", "Project loaded successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to load project file.")

    def _save_project(self):
        """Save the current project."""
        if self.project_service and self.project_path:
            if self.project_service.save_project(self.project_path):
                QMessageBox.information(self, "Success", "Project saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save project.")

    def _add_batches(self):
        """Add more batches to the current project."""
        if not self.project_service:
            QMessageBox.warning(self, "No Project", "Please create or open a project first.")
            return

        # Instruction message
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Add Batches")
        msg.setText("Add More Batch XML Files")
        msg.setInformativeText(
            "Select additional ADIAT_Data.xml batch files to add to this search.\n\n"
            "Tips:\n"
            "• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files\n"
            "• Files can be in different folders\n"
            "• Each batch should be a processed ADIAT_Data.xml file\n"
            "• New batches will be numbered sequentially"
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if msg.exec() != QMessageBox.Ok:
            return

        # Select batch XML files
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)",
            "",
            "XML Files (*.xml)"
        )

        if not file_paths:
            return

        # Add batches
        added_count = self.project_service.add_batches_to_project(file_paths)

        if added_count > 0:
            # Save project automatically
            if self.project_path:
                self.project_service.save_project(self.project_path)

            # Update displays
            self._update_all_displays()

            QMessageBox.information(
                self,
                "Success",
                f"Successfully added {added_count} batch(es) to the project!\n"
                f"Total batches: {len(self.project_service.project_data['batches'])}"
            )
        else:
            QMessageBox.warning(
                self,
                "No Batches Added",
                "No batches were added. Check that the XML files are valid ADIAT_Data.xml files."
            )

    def _load_review(self):
        """Load a reviewer's XML file into the project."""
        if not self.project_service:
            return

        # Select reviewer XML file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reviewer's ADIAT_Data.xml File",
            "",
            "XML Files (*.xml)"
        )

        if not file_path:
            return

        # Get list of batches for selection
        batch_status = self.project_service.get_batch_status()
        if not batch_status:
            QMessageBox.warning(self, "No Batches", "No batches found in project.")
            return

        # Let user select which batch this review is for
        from PySide6.QtWidgets import QInputDialog
        batch_ids = [b['batch_id'] for b in batch_status]
        batch_id, ok = QInputDialog.getItem(
            self,
            "Select Batch",
            "Which batch does this review belong to?",
            batch_ids,
            0,
            False
        )

        if not ok:
            return

        # Add review to batch
        if self.project_service.add_review_to_batch(batch_id, file_path):
            self.project_service.save_project(self.project_path)
            self._update_all_displays()
            QMessageBox.information(self, "Success", "Review data loaded and merged successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to load review data.")

    def _export_results(self):
        """Export consolidated results."""
        if not self.project_service:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Consolidated Results",
            "ADIAT_Data_Consolidated.xml",
            "XML Files (*.xml)"
        )

        if file_path:
            if self.project_service.export_consolidated_results(file_path):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Consolidated results exported to:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Error", "Failed to export results.")

    def _update_all_displays(self):
        """Update all display elements with current project data."""
        if not self.project_service:
            return

        summary = self.project_service.get_project_summary()
        if not summary:
            return

        # Update project info
        self.project_name_label.setText(summary['project_name'])
        self.created_by_label.setText(summary['created_by'])
        self.created_date_label.setText(summary['created_date'][:10] if summary['created_date'] else '-')

        # Update dashboard metrics
        self.total_batches_card.value_label.setText(str(summary['total_batches']))
        self.total_images_card.value_label.setText(str(summary['total_images']))
        self.total_reviews_card.value_label.setText(str(summary['total_reviews']))
        self.unique_reviewers_card.value_label.setText(str(summary['unique_reviewers']))

        # Update progress
        completion = int(summary['completion_percentage'])
        self.completion_progress.setValue(completion)
        self.completion_percent_label.setText(f"{completion}%")

        # Update status counts
        self.not_reviewed_count.setText(str(summary['batches_not_reviewed']))
        self.in_progress_count.setText(str(summary['batches_in_progress']))
        self.complete_count.setText(str(summary['batches_complete']))

        # Update AOI counts
        self.total_aois_count.setText(str(summary['total_aois']))
        self.flagged_aois_count.setText(str(summary['flagged_aois']))

        # Update reviewer list
        if summary['reviewer_names']:
            reviewer_text = ", ".join(summary['reviewer_names'])
            self.reviewer_list.setText(reviewer_text)
        else:
            self.reviewer_list.setText("No reviewers yet")

        # Update batch table
        self._update_batch_table()

        # Update AOI table
        self._update_aoi_table()

    def _update_batch_table(self):
        """Update the batch status table."""
        if not self.project_service:
            return

        batch_status = self.project_service.get_batch_status()
        self.batch_table.setRowCount(len(batch_status))

        for row, batch in enumerate(batch_status):
            self.batch_table.setItem(row, 0, QTableWidgetItem(batch['batch_id']))
            self.batch_table.setItem(row, 1, QTableWidgetItem(batch['algorithm']))
            self.batch_table.setItem(row, 2, QTableWidgetItem(str(batch['image_count'])))
            self.batch_table.setItem(row, 3, QTableWidgetItem(str(batch['review_count'])))
            self.batch_table.setItem(row, 4, QTableWidgetItem(batch['reviewers']))

            # Status with color coding
            status_item = QTableWidgetItem(batch['status'])
            if batch['status'] == "Not Reviewed":
                status_item.setForeground(QColor("#e74c3c"))
            elif batch['status'] == "In Progress":
                status_item.setForeground(QColor("#f39c12"))
            else:
                status_item.setForeground(QColor("#27ae60"))
            self.batch_table.setItem(row, 5, status_item)

    def _update_aoi_table(self):
        """Update the AOI analysis table."""
        if not self.project_service or not self.project_service.xml:
            return

        root = self.project_service.xml.getroot()
        consolidated_elem = root.find('consolidated_aois')

        if not consolidated_elem:
            return

        aois = consolidated_elem.findall('aoi')
        self.aoi_table.setRowCount(len(aois))

        for row, aoi_elem in enumerate(aois):
            # Image path (basename only)
            image_path = aoi_elem.findtext('image_path', '')
            self.aoi_table.setItem(row, 0, QTableWidgetItem(os.path.basename(image_path)))

            # Location
            location = aoi_elem.findtext('center', '(0, 0)')
            self.aoi_table.setItem(row, 1, QTableWidgetItem(location))

            # Flag count
            flag_count = aoi_elem.findtext('flag_count', '0')
            flag_item = QTableWidgetItem(flag_count)
            if int(flag_count) > 0:
                flag_item.setForeground(QColor("#e74c3c"))
                flag_item.setBackground(QColor("#ffe6e6"))
            self.aoi_table.setItem(row, 2, flag_item)

            # Reviewers
            reviews_elem = aoi_elem.find('reviews')
            reviewers = []
            comments = []

            if reviews_elem:
                for review in reviews_elem.findall('review'):
                    reviewer_name = review.get('reviewer_name', 'Unknown')
                    reviewers.append(reviewer_name)

                    comment = review.findtext('comment', '')
                    if comment:
                        comments.append(f"[{reviewer_name}] {comment}")

            self.aoi_table.setItem(row, 3, QTableWidgetItem(", ".join(reviewers)))
            self.aoi_table.setItem(row, 4, QTableWidgetItem(" | ".join(comments)))

    def _enable_project_controls(self, enabled):
        """Enable or disable project-related controls."""
        self.save_project_btn.setEnabled(enabled)
        self.add_batch_btn.setEnabled(enabled)
        self.load_review_btn.setEnabled(enabled)
        self.export_results_btn.setEnabled(enabled)
