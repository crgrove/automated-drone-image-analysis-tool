import os
import uuid
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from core.services.LoggerService import LoggerService
from core.services.XmlService import XmlService


class SearchProjectService:
    """Service for managing search projects with multiple batches and reviewers."""

    def __init__(self, project_path=None):
        """
        Initialize the SearchProjectService.

        Args:
            project_path (str, optional): Path to an existing search project XML file.
        """
        self.project_path = project_path
        self.logger = LoggerService()
        self.project_data = {
            'metadata': {},
            'batches': [],
            'consolidated_aois': []
        }

        if project_path and os.path.exists(project_path):
            self.load_project(project_path)
        else:
            # Initialize empty project
            self.xml = None

    def create_new_project(self, project_name, batch_xml_paths, coordinator_name=""):
        """
        Create a new search project from initial batch XML files.

        Args:
            project_name (str): Name of the search project.
            batch_xml_paths (list): List of paths to initial ADIAT_Data.xml batch files.
            coordinator_name (str): Name of the coordinator creating the project.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Create root element
            root = ET.Element('search_project')

            # Add metadata
            metadata = ET.SubElement(root, 'metadata')
            ET.SubElement(metadata, 'name').text = project_name
            ET.SubElement(metadata, 'created_date').text = datetime.now().isoformat()
            ET.SubElement(metadata, 'created_by').text = coordinator_name

            # Process each batch XML
            batches_elem = ET.SubElement(root, 'batches')

            for idx, xml_path in enumerate(batch_xml_paths):
                if not os.path.exists(xml_path):
                    self.logger.warning(f"Batch XML not found: {xml_path}")
                    continue

                # Load batch XML to extract metadata
                xml_service = XmlService(xml_path)
                settings, image_count = xml_service.get_settings()
                images = xml_service.get_images()

                # Create batch element
                batch = ET.SubElement(batches_elem, 'batch')
                batch_id = f"batch_{idx + 1:03d}"
                ET.SubElement(batch, 'batch_id').text = batch_id
                ET.SubElement(batch, 'original_xml_path').text = xml_path
                ET.SubElement(batch, 'algorithm').text = settings.get('algorithm', 'Unknown')
                ET.SubElement(batch, 'image_count').text = str(image_count)

                # Store settings
                settings_elem = ET.SubElement(batch, 'settings')
                for key, value in settings.items():
                    if key != 'options':
                        setting = ET.SubElement(settings_elem, 'setting')
                        setting.set('name', key)
                        setting.set('value', str(value))

                # Store image paths for tracking
                images_elem = ET.SubElement(batch, 'images')
                for image in images:
                    img_elem = ET.SubElement(images_elem, 'image')
                    img_elem.set('path', image.get('path', ''))

                # Initialize empty reviews section
                ET.SubElement(batch, 'reviews')

            # Initialize consolidated AOIs section
            ET.SubElement(root, 'consolidated_aois')

            self.xml = ET.ElementTree(root)
            self._parse_project_data()

            return True

        except Exception as e:
            self.logger.error(f"Error creating new project: {e}")
            return False

    def load_project(self, project_path):
        """
        Load an existing search project from XML file.

        Args:
            project_path (str): Path to the search project XML file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.project_path = project_path
            self.xml = ET.parse(project_path)
            self._parse_project_data()
            return True

        except Exception as e:
            self.logger.error(f"Error loading project: {e}")
            return False

    def _parse_project_data(self):
        """Parse XML tree into project_data dictionary."""
        if not self.xml:
            return

        root = self.xml.getroot()

        # Parse metadata
        metadata_elem = root.find('metadata')
        if metadata_elem is not None:
            self.project_data['metadata'] = {
                'name': metadata_elem.findtext('name', ''),
                'created_date': metadata_elem.findtext('created_date', ''),
                'created_by': metadata_elem.findtext('created_by', '')
            }

        # Parse batches
        batches = []
        batches_elem = root.find('batches')
        if batches_elem is not None:
            for batch_elem in batches_elem.findall('batch'):
                batch = {
                    'batch_id': batch_elem.findtext('batch_id', ''),
                    'original_xml_path': batch_elem.findtext('original_xml_path', ''),
                    'algorithm': batch_elem.findtext('algorithm', ''),
                    'image_count': int(batch_elem.findtext('image_count', '0')),
                    'reviews': []
                }

                # Parse reviews
                reviews_elem = batch_elem.find('reviews')
                if reviews_elem is not None:
                    for review_elem in reviews_elem.findall('review'):
                        review = {
                            'review_id': review_elem.findtext('review_id', ''),
                            'reviewer_name': review_elem.findtext('reviewer_name', ''),
                            'review_date': review_elem.findtext('review_date', ''),
                            'xml_path': review_elem.findtext('xml_path', ''),
                            'images_viewed': int(review_elem.findtext('images_viewed', '0')),
                            'aois_flagged': int(review_elem.findtext('aois_flagged', '0'))
                        }
                        batch['reviews'].append(review)

                batches.append(batch)

        self.project_data['batches'] = batches

    def add_batches_to_project(self, batch_xml_paths):
        """
        Add new batches to an existing project.

        Args:
            batch_xml_paths (list): List of paths to ADIAT_Data.xml batch files to add.

        Returns:
            int: Number of batches successfully added.
        """
        try:
            if not self.xml:
                self.logger.error("No project loaded")
                return 0

            root = self.xml.getroot()
            batches_elem = root.find('batches')
            if batches_elem is None:
                self.logger.error("Invalid project structure - no batches element")
                return 0

            # Find the highest existing batch number
            existing_batches = batches_elem.findall('batch')
            max_batch_num = 0
            for batch in existing_batches:
                batch_id = batch.findtext('batch_id', '')
                # Extract number from batch_XXX format
                try:
                    num = int(batch_id.split('_')[1])
                    max_batch_num = max(max_batch_num, num)
                except (IndexError, ValueError):
                    pass

            added_count = 0

            for idx, xml_path in enumerate(batch_xml_paths):
                if not os.path.exists(xml_path):
                    self.logger.warning(f"Batch XML not found: {xml_path}")
                    continue

                # Load batch XML to extract metadata
                xml_service = XmlService(xml_path)
                settings, image_count = xml_service.get_settings()
                images = xml_service.get_images()

                # Create batch element
                batch = ET.SubElement(batches_elem, 'batch')
                batch_num = max_batch_num + idx + 1
                batch_id = f"batch_{batch_num:03d}"
                ET.SubElement(batch, 'batch_id').text = batch_id
                ET.SubElement(batch, 'original_xml_path').text = xml_path
                ET.SubElement(batch, 'algorithm').text = settings.get('algorithm', 'Unknown')
                ET.SubElement(batch, 'image_count').text = str(image_count)

                # Store settings
                settings_elem = ET.SubElement(batch, 'settings')
                for key, value in settings.items():
                    if key != 'options':
                        setting = ET.SubElement(settings_elem, 'setting')
                        setting.set('name', key)
                        setting.set('value', str(value))

                # Store image paths for tracking
                images_elem = ET.SubElement(batch, 'images')
                for image in images:
                    img_elem = ET.SubElement(images_elem, 'image')
                    img_elem.set('path', image.get('path', ''))

                # Initialize empty reviews section
                ET.SubElement(batch, 'reviews')

                added_count += 1

            # Update parsed data
            self._parse_project_data()

            return added_count

        except Exception as e:
            self.logger.error(f"Error adding batches: {e}")
            return 0

    def add_review_to_batch(self, batch_id, review_xml_path):
        """
        Add a reviewer's XML file to a batch.

        Args:
            batch_id (str): ID of the batch being reviewed.
            review_xml_path (str): Path to the reviewer's ADIAT_Data.xml file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Load review XML
            review_service = XmlService(review_xml_path)
            review_meta = review_service.get_review_metadata()
            images = review_service.get_images()

            if not review_meta or not review_meta.get('review_id'):
                self.logger.error("Review XML missing review metadata")
                return False

            # Find batch in XML
            root = self.xml.getroot()
            batches_elem = root.find('batches')
            batch_elem = None

            for batch in batches_elem.findall('batch'):
                if batch.findtext('batch_id') == batch_id:
                    batch_elem = batch
                    break

            if batch_elem is None:
                self.logger.error(f"Batch {batch_id} not found")
                return False

            # Add review to batch
            reviews_elem = batch_elem.find('reviews')
            review_elem = ET.SubElement(reviews_elem, 'review')
            ET.SubElement(review_elem, 'review_id').text = review_meta['review_id']
            ET.SubElement(review_elem, 'reviewer_name').text = review_meta['reviewer_name']
            ET.SubElement(review_elem, 'review_date').text = review_meta['review_date']
            ET.SubElement(review_elem, 'xml_path').text = review_xml_path

            # Count viewed images and flagged AOIs
            images_viewed = len(images)
            aois_flagged = sum(
                sum(1 for aoi in img['areas_of_interest'] if aoi.get('flagged', False))
                for img in images
            )

            ET.SubElement(review_elem, 'images_viewed').text = str(images_viewed)
            ET.SubElement(review_elem, 'aois_flagged').text = str(aois_flagged)

            # Merge AOI data
            self._merge_aoi_data(batch_id, images, review_meta)

            # Update parsed data
            self._parse_project_data()

            return True

        except Exception as e:
            self.logger.error(f"Error adding review: {e}")
            return False

    def _merge_aoi_data(self, batch_id, images, review_meta):
        """
        Merge AOI data from a review into consolidated_aois.

        Args:
            batch_id (str): Batch ID for this review.
            images (list): List of images from the review.
            review_meta (dict): Review metadata.
        """
        root = self.xml.getroot()
        consolidated_elem = root.find('consolidated_aois')

        for image in images:
            image_path = image.get('path', '')

            for aoi in image.get('areas_of_interest', []):
                # Try to find matching AOI
                matched = False
                center = aoi.get('center', (0, 0))

                for existing_aoi in consolidated_elem.findall('aoi'):
                    # Match by image path and center coordinates (within tolerance)
                    existing_path = existing_aoi.findtext('image_path', '')
                    existing_center = eval(existing_aoi.findtext('center', '(0, 0)'))

                    if existing_path == image_path:
                        # Check if centers are close (within 10 pixels)
                        if abs(existing_center[0] - center[0]) <= 10 and abs(existing_center[1] - center[1]) <= 10:
                            # Match found - update existing AOI
                            self._update_existing_aoi(existing_aoi, aoi, review_meta, batch_id)
                            matched = True
                            break

                if not matched:
                    # Create new AOI entry
                    self._create_new_aoi(consolidated_elem, aoi, image_path, review_meta, batch_id)

    def _update_existing_aoi(self, aoi_elem, new_aoi, review_meta, batch_id):
        """Update an existing consolidated AOI with new review data."""
        # Increment flag count if this review flagged it
        if new_aoi.get('flagged', False):
            flag_count = int(aoi_elem.findtext('flag_count', '0'))
            flag_count_elem = aoi_elem.find('flag_count')
            if flag_count_elem is not None:
                flag_count_elem.text = str(flag_count + 1)
            else:
                ET.SubElement(aoi_elem, 'flag_count').text = str(flag_count + 1)

        # Add review data
        reviews_elem = aoi_elem.find('reviews')
        if reviews_elem is None:
            reviews_elem = ET.SubElement(aoi_elem, 'reviews')

        review = ET.SubElement(reviews_elem, 'review')
        review.set('review_id', review_meta.get('review_id', ''))
        review.set('reviewer_name', review_meta.get('reviewer_name', ''))
        review.set('batch_id', batch_id)

        ET.SubElement(review, 'flagged').text = str(new_aoi.get('flagged', False))
        comment = new_aoi.get('user_comment', '')
        if comment:
            ET.SubElement(review, 'comment').text = comment

    def _create_new_aoi(self, consolidated_elem, aoi, image_path, review_meta, batch_id):
        """Create a new consolidated AOI entry."""
        aoi_elem = ET.SubElement(consolidated_elem, 'aoi')
        ET.SubElement(aoi_elem, 'image_path').text = image_path
        ET.SubElement(aoi_elem, 'center').text = str(aoi.get('center', (0, 0)))
        ET.SubElement(aoi_elem, 'radius').text = str(aoi.get('radius', 0))
        ET.SubElement(aoi_elem, 'area').text = str(aoi.get('area', 0))

        flag_count = 1 if aoi.get('flagged', False) else 0
        ET.SubElement(aoi_elem, 'flag_count').text = str(flag_count)

        # Add review data
        reviews_elem = ET.SubElement(aoi_elem, 'reviews')
        review = ET.SubElement(reviews_elem, 'review')
        review.set('review_id', review_meta.get('review_id', ''))
        review.set('reviewer_name', review_meta.get('reviewer_name', ''))
        review.set('batch_id', batch_id)

        ET.SubElement(review, 'flagged').text = str(aoi.get('flagged', False))
        comment = aoi.get('user_comment', '')
        if comment:
            ET.SubElement(review, 'comment').text = comment

    def get_project_summary(self):
        """
        Get summary statistics for the project.

        Returns:
            dict: Summary statistics including batch counts, review counts, etc.
        """
        if not self.project_data['batches']:
            return None

        total_batches = len(self.project_data['batches'])
        total_images = sum(b['image_count'] for b in self.project_data['batches'])
        total_reviews = sum(len(b['reviews']) for b in self.project_data['batches'])

        # Calculate batch status
        not_reviewed = sum(1 for b in self.project_data['batches'] if len(b['reviews']) == 0)
        in_progress = sum(1 for b in self.project_data['batches'] if len(b['reviews']) == 1)
        complete = sum(1 for b in self.project_data['batches'] if len(b['reviews']) >= 2)

        # Get unique reviewers
        all_reviewers = set()
        for batch in self.project_data['batches']:
            for review in batch['reviews']:
                all_reviewers.add(review['reviewer_name'])

        # Count consolidated AOIs and flagged AOIs
        root = self.xml.getroot() if self.xml else None
        total_aois = 0
        flagged_aois = 0

        if root:
            consolidated_elem = root.find('consolidated_aois')
            if consolidated_elem:
                total_aois = len(consolidated_elem.findall('aoi'))
                flagged_aois = sum(
                    1 for aoi in consolidated_elem.findall('aoi')
                    if int(aoi.findtext('flag_count', '0')) > 0
                )

        return {
            'project_name': self.project_data['metadata'].get('name', ''),
            'created_date': self.project_data['metadata'].get('created_date', ''),
            'created_by': self.project_data['metadata'].get('created_by', ''),
            'total_batches': total_batches,
            'total_images': total_images,
            'total_reviews': total_reviews,
            'unique_reviewers': len(all_reviewers),
            'reviewer_names': list(all_reviewers),
            'batches_not_reviewed': not_reviewed,
            'batches_in_progress': in_progress,
            'batches_complete': complete,
            'total_aois': total_aois,
            'flagged_aois': flagged_aois,
            'completion_percentage': (complete / total_batches * 100) if total_batches > 0 else 0
        }

    def get_batch_status(self):
        """
        Get detailed status for each batch.

        Returns:
            list: List of dictionaries with batch status information.
        """
        batch_status = []

        for batch in self.project_data['batches']:
            review_count = len(batch['reviews'])

            if review_count == 0:
                status = "Not Reviewed"
            elif review_count == 1:
                status = "In Progress"
            else:
                status = "Complete"

            reviewer_names = [r['reviewer_name'] for r in batch['reviews']]

            batch_status.append({
                'batch_id': batch['batch_id'],
                'algorithm': batch['algorithm'],
                'image_count': batch['image_count'],
                'review_count': review_count,
                'reviewers': ', '.join(reviewer_names) if reviewer_names else 'None',
                'status': status,
                'xml_path': batch['original_xml_path']
            })

        return batch_status

    def save_project(self, path=None):
        """
        Save the search project to XML file.

        Args:
            path (str, optional): Path to save to. Uses self.project_path if not provided.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            save_path = path or self.project_path

            if not save_path:
                self.logger.error("No save path specified")
                return False

            if self.xml:
                with open(save_path, 'wb') as f:
                    self.xml.write(f, encoding='utf-8', xml_declaration=True)

                self.project_path = save_path
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error saving project: {e}")
            return False

    def export_consolidated_results(self, output_path):
        """
        Export consolidated results to a new ADIAT_Data.xml file.

        Args:
            output_path (str): Path to save the consolidated XML file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Create new XML structure similar to ADIAT_Data.xml
            root = ET.Element('data')

            # Add settings from first batch
            if self.project_data['batches']:
                first_batch_path = self.project_data['batches'][0]['original_xml_path']
                if os.path.exists(first_batch_path):
                    xml_service = XmlService(first_batch_path)
                    settings, _ = xml_service.get_settings()

                    settings_elem = ET.SubElement(root, 'settings')
                    for key, value in settings.items():
                        if key != 'options':
                            settings_elem.set(key, str(value))

            # Add consolidated images and AOIs
            images_elem = ET.SubElement(root, 'images')

            if self.xml:
                consolidated_elem = self.xml.getroot().find('consolidated_aois')
                if consolidated_elem:
                    # Group AOIs by image
                    aois_by_image = {}
                    for aoi_elem in consolidated_elem.findall('aoi'):
                        img_path = aoi_elem.findtext('image_path', '')
                        if img_path not in aois_by_image:
                            aois_by_image[img_path] = []
                        aois_by_image[img_path].append(aoi_elem)

                    # Create image entries
                    for img_path, aois in aois_by_image.items():
                        image_elem = ET.SubElement(images_elem, 'image')
                        image_elem.set('path', img_path)
                        image_elem.set('hidden', 'False')

                        for aoi_elem in aois:
                            aoi = ET.SubElement(image_elem, 'areas_of_interest')
                            aoi.set('center', aoi_elem.findtext('center', '(0, 0)'))
                            aoi.set('radius', aoi_elem.findtext('radius', '0'))
                            aoi.set('area', aoi_elem.findtext('area', '0'))

                            # Mark as flagged if flag_count > 0
                            flag_count = int(aoi_elem.findtext('flag_count', '0'))
                            aoi.set('flagged', str(flag_count > 0))

                            # Combine all reviewer comments
                            reviews_elem = aoi_elem.find('reviews')
                            if reviews_elem:
                                comments = []
                                for review in reviews_elem.findall('review'):
                                    reviewer = review.get('reviewer_name', 'Unknown')
                                    comment = review.findtext('comment', '')
                                    if comment:
                                        comments.append(f"[{reviewer}] {comment}")

                                if comments:
                                    aoi.set('user_comment', ' | '.join(comments))

            # Save to file
            tree = ET.ElementTree(root)
            with open(output_path, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)

            return True

        except Exception as e:
            self.logger.error(f"Error exporting consolidated results: {e}")
            return False
