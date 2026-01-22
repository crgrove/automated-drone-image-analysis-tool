<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
<context>
    <name>AIPersonDetector</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="27"/>
        <source>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="31"/>
        <source>Confidence Threshold</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="44"/>
        <source>Adjust the confidence threshold for person detection.
• Range: 0% to 100% (slider -1 to 100, -1 displays as 0%)
• Default: 50%
The AI model assigns a confidence score to each person detection:
• Lower values (0-30%): Accept low-confidence detections (more detections, more false positives)
• Medium values (31-60%): Balanced detection (recommended for most cases)
• Higher values (61-100%): Only accept high-confidence detections (fewer detections, fewer false positives)
Confidence represents the AI model&apos;s certainty that a detected object is a person.
Start with 50% and adjust based on your accuracy requirements.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="81"/>
        <source>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="86"/>
        <source>50</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="100"/>
        <source>GPU status and availability information.
Shows whether GPU acceleration is available for AI person detection.
• GPU Available: AI detection will use GPU for faster processing
• CPU Only: AI detection will use CPU (slower but still functional)
GPU acceleration significantly improves processing speed for AI models.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="107"/>
        <source>GPU Label</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="81"/>
        <source>GPU Not Available</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="87"/>
        <source>GPU Available</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizard</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="40"/>
        <source>How confident should ADIAT be before marking something as a person?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="56"/>
        <source>Note: A higher setting may increase false positives.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOICommentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="27"/>
        <source>AOI Comment</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="37"/>
        <source>Add a comment for this flagged AOI (max 256 characters):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="44"/>
        <source>Enter your comment here...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="57"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="59"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOIController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="435"/>
        <source>Comment saved</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="437"/>
        <source>Comment cleared</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="524"/>
        <source>Copy Data</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="598"/>
        <source>AOI data copied</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="678"/>
        <source>Invalid image index</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="683"/>
        <source>Invalid AOI index</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="746"/>
        <source>Could not calculate AOI location. Diagnostic info copied to clipboard!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="752"/>
        <source>Could not calculate AOI location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1110"/>
        <source>Temperature sorting unavailable (no thermal data)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1425"/>
        <source>Cannot Delete AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1427"/>
        <source>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1436"/>
        <source>Delete AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1438"/>
        <source>Are you sure you want to delete this AOI? This action cannot be undone.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOICreationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="23"/>
        <source>Create AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="31"/>
        <source>Create AOI?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="39"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="43"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOIFilterDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="55"/>
        <source>Filter AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="64"/>
        <source>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="69"/>
        <source>Flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="72"/>
        <source>Show Only Flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="76"/>
        <source>Only AOIs marked with a flag will be displayed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="84"/>
        <source>Comment Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="88"/>
        <source>Enable Comment Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="95"/>
        <source>Pattern:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="98"/>
        <source>e.g., *work* or crack* or *damage</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="106"/>
        <source>Use * as wildcard for any characters (case-insensitive)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="110"/>
        <source>Only AOIs with non-empty comments matching the pattern will be shown</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="118"/>
        <source>Color Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="122"/>
        <source>Enable Color Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="129"/>
        <source>Target Hue:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="131"/>
        <source>Select Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="143"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="362"/>
        <source>No color selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="151"/>
        <source>Hue Range (±):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="169"/>
        <source>AOIs with hue within ±range of target will be shown</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="177"/>
        <source>Pixel Area Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="181"/>
        <source>Enable Pixel Area Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="188"/>
        <source>Minimum Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="202"/>
        <source>Maximum Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="218"/>
        <source>Temperature Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="222"/>
        <source>Enable Temperature Filter</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="276"/>
        <source>Temperature filtering unavailable (no thermal data)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="291"/>
        <source>Clear All Filters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="297"/>
        <source>Apply</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="302"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="337"/>
        <source>Select Target Hue</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOINeighborGalleryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="338"/>
        <source>AOI in Neighboring Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="389"/>
        <source>Reset View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="392"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="399"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOINeighborTrackingController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="105"/>
        <source>No AOI Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="106"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="130"/>
        <source>Cannot Calculate GPS</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="132"/>
        <source>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="140"/>
        <source>Searching for AOI in neighboring images...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="141"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="145"/>
        <source>Tracking AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="181"/>
        <source>Tracking Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="182"/>
        <source>An error occurred while tracking the AOI:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="207"/>
        <source>No Neighbors Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="208"/>
        <source>The AOI was not found in any neighboring images.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="233"/>
        <source>Search Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="234"/>
        <source>An error occurred during the search:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="285"/>
        <source>Display Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="286"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOIUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="250"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="333"/>
        <source>AOI Information
Right-click to copy data to clipboard</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="256"/>
        <source>

Score Type: {type}
Raw Score: {score} ({method})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="307"/>
        <source>Confidence Score: {score:.1f}%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="373"/>
        <source>Unflag AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="373"/>
        <source>Flag AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="390"/>
        <source>Comment:
{comment}

Click to edit comment</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="398"/>
        <source>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="415"/>
        <source>Calculate and show GPS location for this AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="433"/>
        <source>Delete this AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="471"/>
        <source>Area</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="471"/>
        <source>Areas</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="473"/>
        <source>{filtered} of {total} {label}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="482"/>
        <source>Area of Interest</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Areas of Interest</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="487"/>
        <source>{count} {label}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="630"/>
        <source>Loading AOIs...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="671"/>
        <source>Loading AOIs... ({current}/{total})</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AlertManager</name>
    <message>
        <location filename="../app/core/services/AlertService.py" line="292"/>
        <source>ADIAT - Color Detection Alerts</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="567"/>
        <source>ADIAT - Color Detection Alert</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="608"/>
        <source>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="618"/>
        <source>
Details:
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="622"/>
        <source>  #{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="642"/>
        <source>ADIAT - Detection Alert</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmParametersPage.py" line="164"/>
        <source>{algorithm} Algorithm Settings</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AltitudeController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>meters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>feet</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="109"/>
        <source>Negative Altitude Detected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="111"/>
        <source>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="130"/>
        <source>Override Altitude</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="132"/>
        <source>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="180"/>
        <source>Custom AGL set to {value:.1f} {unit}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>BearingRecoveryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="124"/>
        <source>Missing Bearings Detected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="132"/>
        <source>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="150"/>
        <source>📁 Load Track File (KML/GPX/CSV)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="156"/>
        <source>🧭 Auto-Calculate from Image GPS</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="174"/>
        <source>Preparing...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="190"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="195"/>
        <source>Skip</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="259"/>
        <source>Select Track File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="261"/>
        <source>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="345"/>
        <source>Bearings set for {count} images ({source})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="350"/>
        <source>, {count} flagged near turns</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="352"/>
        <source>, {count} hover estimates</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="354"/>
        <source>, {count} time gaps</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="361"/>
        <source>Bearing Calculation Complete</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="362"/>
        <source>{summary}.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="389"/>
        <source>Bearing Calculation Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="391"/>
        <source>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="411"/>
        <source>Cancelled</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="422"/>
        <source>Cancelling...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="435"/>
        <source>Bearing Recovery Not Needed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="437"/>
        <source>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="452"/>
        <source>
&lt;h3&gt;What is Bearing Recovery?&lt;/h3&gt;

&lt;p&gt;&lt;b&gt;Bearing&lt;/b&gt; (also called heading, yaw, or course) is the direction the drone/camera
was pointing when an image was captured, measured in degrees clockwise from North (0-360°).&lt;/p&gt;

&lt;h4&gt;Why is it important?&lt;/h4&gt;
&lt;p&gt;Bearings are essential for:&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;Accurate georeferencing and mapping&lt;/li&gt;
&lt;li&gt;Proper image alignment and stitching&lt;/li&gt;
&lt;li&gt;Understanding camera field of view&lt;/li&gt;
&lt;li&gt;Analysis of detected objects in geographic context&lt;/li&gt;
&lt;/ul&gt;

&lt;h4&gt;Recovery Methods:&lt;/h4&gt;

&lt;p&gt;&lt;b&gt;Load Track File (KML/GPX/CSV)&lt;/b&gt;&lt;br/&gt;
Uses an external GPS track log from your drone or flight controller. The track contains
timestamped positions that allow precise bearing interpolation. Most accurate method.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Auto-Calculate from Image GPS&lt;/b&gt;&lt;br/&gt;
Estimates bearings using only the GPS coordinates embedded in your images. Analyzes the
flight pattern to determine direction of travel. Works well for systematic flight patterns
like lawn-mower surveys.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Skip&lt;/b&gt;&lt;br/&gt;
Proceed without bearing recovery. Some features may not work correctly.&lt;/p&gt;
        </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="483"/>
        <source>About Bearing Recovery</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CacheLocationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="35"/>
        <source>Cache Not Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="47"/>
        <source>Cached Data Not Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="56"/>
        <source>The following cached items were not found:
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="66"/>
        <source>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="80"/>
        <source>Locate Cache Folder...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="85"/>
        <source>Skip (Generate On-Demand)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="122"/>
        <source>Select ADIAT_Results Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="136"/>
        <source>Invalid Cache Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="138"/>
        <source>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoAPIMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="42"/>
        <source>Select CalTopo Map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="68"/>
        <source>Select a CalTopo map:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="77"/>
        <source>Search:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="79"/>
        <source>Filter maps by name...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="111"/>
        <source>Update Credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="117"/>
        <source>Select Map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="121"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="150"/>
        <source>No account data available.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="515"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="540"/>
        <source>Credentials Updated</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="516"/>
        <source>Credentials have been updated and the map list has been refreshed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="521"/>
        <source>Update Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="523"/>
        <source>Failed to refresh account data with new credentials.

Please check your credentials and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="530"/>
        <source>Update Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="531"/>
        <source>An error occurred while updating credentials:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="542"/>
        <source>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="559"/>
        <source>No Map Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="560"/>
        <source>Please select a map from the list.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoAuthDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="96"/>
        <source>CalTopo Login &amp; Map Selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="173"/>
        <source>Current map: Not selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="177"/>
        <source>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="191"/>
        <source>I&apos;m Logged In - Export Data</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="193"/>
        <source>Click this after logging in and navigating to your map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="196"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="264"/>
        <source>Initialization Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="265"/>
        <source>Failed to initialize CalTopo browser:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="308"/>
        <source>Failed to Load</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="310"/>
        <source>Failed to load CalTopo. Please check your internet connection and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="341"/>
        <source>Current map: {map_id}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="358"/>
        <source>No Map Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="360"/>
        <source>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="369"/>
        <source>Browser Not Ready</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="370"/>
        <source>The CalTopo browser is still loading. Please wait a moment and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="376"/>
        <source>Starting export...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="394"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="557"/>
        <source>Authentication Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="395"/>
        <source>Browser not initialized. Please try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="559"/>
        <source>Could not capture session cookies. Please ensure you are logged in to CalTopo.

Try:
1. Make sure you&apos;re logged in
2. Navigate to a map
3. Wait a few seconds for cookies to be set
4. Click &apos;I&apos;m Logged In&apos; again</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoCredentialDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="33"/>
        <source>CalTopo API Credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="76"/>
        <source>CalTopo Team API Credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="85"/>
        <source>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="97"/>
        <source>How to get your API credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="101"/>
        <source>Opens CalTopo API documentation in your browser</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="107"/>
        <source>Change credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="114"/>
        <source>Team ID:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="116"/>
        <source>6-digit alphanumeric Team ID</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="123"/>
        <source>Credential ID:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="125"/>
        <source>Credential ID</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="132"/>
        <source>Credential Secret:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="134"/>
        <source>Credential Secret (will be encrypted)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="146"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="309"/>
        <source>Test Credentials</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="148"/>
        <source>Test the credentials by calling the CalTopo API</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="150"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="154"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Invalid Input</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <source>Please enter a Team ID.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <source>Please enter a Credential ID.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Please enter a Credential Secret.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="267"/>
        <source>Testing...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="282"/>
        <source>Credentials Valid</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="283"/>
        <source>The credentials are valid and successfully authenticated with CalTopo API.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="288"/>
        <source>Credentials Invalid</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <source>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="301"/>
        <source>Test Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="302"/>
        <source>An error occurred while testing credentials:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="442"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1508"/>
        <source>Offline Mode Enabled</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="444"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1510"/>
        <source>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="455"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1521"/>
        <source>Nothing Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="457"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1523"/>
        <source>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="465"/>
        <source>Preparing Export Data</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="468"/>
        <source>Preparing data for export...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="469"/>
        <source>Processing images and AOIs...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="513"/>
        <source>Preparation Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="515"/>
        <source>An error occurred while preparing export data:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="524"/>
        <source>flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="526"/>
        <source>image locations</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="528"/>
        <source>coverage area</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="532"/>
        <source>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="538"/>
        <source>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="546"/>
        <source>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="551"/>
        <source>No coverage area polygons could be calculated.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The images are not nadir (gimbal pitch must be between -85° and -95°)
• GSD (ground sample distance) could not be calculated

Please ensure your images have GPS coordinates and are nadir shots.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="560"/>
        <source>No {types} are available to export.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="565"/>
        <source>Nothing to Export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="586"/>
        <source>No Map Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="588"/>
        <source>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="650"/>
        <source>{count} marker(s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="654"/>
        <source>{count} polygon(s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="657"/>
        <source> and </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="662"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1717"/>
        <source>Export Successful</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="664"/>
        <source>Successfully exported all {items} to CalTopo map {map_id}.

The items should now be visible on your map.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="671"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1726"/>
        <source>Partial Success</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="673"/>
        <source>Exported {success} of {total} item(s) ({items}) to CalTopo map {map_id}.

{failed} item(s) failed. Check console for details.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="687"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1739"/>
        <source>Export Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="689"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1741"/>
        <source>Failed to export items to CalTopo.

Please check the console output for error details.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="699"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1647"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1752"/>
        <source>Export Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="701"/>
        <source>An error occurred during CalTopo export:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1002"/>
        <source>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1046"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1330"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1678"/>
        <source>Exporting to CalTopo</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1049"/>
        <source>Exporting markers to CalTopo...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1051"/>
        <source>Preparing to export {count} marker(s)...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1296"/>
        <source>Export complete: {success} of {total} marker(s) exported</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1333"/>
        <source>Exporting polygons to CalTopo...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1335"/>
        <source>Preparing to export {count} polygon(s)...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1462"/>
        <source>Export complete: {success} of {total} polygon(s) exported</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1480"/>
        <source>Logged Out</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1481"/>
        <source>Successfully logged out from CalTopo.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1546"/>
        <source>Loading CalTopo Maps</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1549"/>
        <source>Connecting to CalTopo...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1550"/>
        <source>Fetching account data and maps...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1588"/>
        <source>Connection Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1590"/>
        <source>An error occurred while connecting to CalTopo API:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1598"/>
        <source>Authentication Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1600"/>
        <source>Failed to authenticate with CalTopo API.

Please check your credentials and try again.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1649"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1754"/>
        <source>An error occurred during CalTopo API export:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1681"/>
        <source>Exporting to CalTopo...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1682"/>
        <source>Preparing data and exporting...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1719"/>
        <source>Successfully exported all {total} item(s) to CalTopo map.

The items should now be visible on your map.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1728"/>
        <source>Exported {success} of {total} item(s) to CalTopo map.

{failed} item(s) failed. Check console for details.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="35"/>
        <source>Select CalTopo Map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="51"/>
        <source>Select a CalTopo map to export flagged AOIs:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="60"/>
        <source>Search:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="62"/>
        <source>Filter maps by name...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="83"/>
        <source>Select Map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMapDialog.py" line="87"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CalTopoMethodDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="34"/>
        <source>CalTopo Export Method</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="52"/>
        <source>Select CalTopo Export Method</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="61"/>
        <source>Choose how you want to authenticate with CalTopo:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="68"/>
        <source>Export Method</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="72"/>
        <source>API (Recommended for CalTopo Team Account)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="75"/>
        <source>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="79"/>
        <source>Browser Login</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="81"/>
        <source>Use browser-based authentication.
Log in through an embedded browser window.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="96"/>
        <source>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="109"/>
        <source>Continue</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="113"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ClickableColorSwatch</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/views/ColorRowWidget.py" line="55"/>
        <location filename="../app/algorithms/images/ColorRange/views/ColorRowWizardWidget.py" line="64"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="83"/>
        <source>RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="71"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="71"/>
        <source>HSV: ({h}, {s}, {v})
Click to change color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="78"/>
        <source>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="52"/>
        <source>Color Anomaly</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="53"/>
        <source>Motion Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="54"/>
        <source>Fusion</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="59"/>
        <source>Input &amp;&amp; Processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="60"/>
        <source>Frame</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="61"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="12"/>
        <source>Color Anomaly Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="16"/>
        <source>Enable Color Anomaly Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="27"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="38"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="56"/>
        <source>Motion Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="65"/>
        <source>Do you want to enable motion detection?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="73"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="79"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="66"/>
        <source>Color Selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="67"/>
        <source>Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="68"/>
        <source>Input &amp;&amp; Processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="69"/>
        <source>Frame</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="70"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="79"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="82"/>
        <source>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="102"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="105"/>
        <source>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="145"/>
        <source>Min Object Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="151"/>
        <source>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="160"/>
        <source>Max Object Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="166"/>
        <source>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="175"/>
        <source>Confidence Threshold:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="182"/>
        <source>Minimum confidence score to accept a detection (0-100%).
Confidence is calculated from:
• Size score: area relative to max area
• Shape score: solidity (how compact/regular the shape is)
• Final: average of both scores

Lower values (0-30%) = accept more detections, including weak/fragmented ones.
Higher values (70-100%) = only high-quality detections, well-formed shapes.
Recommended: 50% for balanced filtering, 30% for more detections, 70% for strict quality.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="193"/>
        <source>50%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="318"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="371"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="406"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="660"/>
        <source>Color_{index}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="489"/>
        <source>Color Ranges: {count} colors</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorDetectionWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="52"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="62"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="244"/>
        <source>Color Ranges: {count} colors</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="329"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorListDialog</name>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="30"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="30"/>
        <source>Select Color from List</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="42"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="42"/>
        <source>Search:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="44"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="44"/>
        <source>Filter by name or uses…</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="61"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="61"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>RGB</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <source>HSV</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="61"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Uses</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorListDialog.py" line="73"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="73"/>
        <source>Use Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorPickerDialog</name>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerDialog.py" line="35"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="35"/>
        <source>Select Color from Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerDialog.py" line="55"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="55"/>
        <source>Use Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorPickerImageViewer</name>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <source>Load Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <source>Color Selector</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <source>Select Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="173"/>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="230"/>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="588"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="173"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="230"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="588"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="174"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="174"/>
        <source>Could not load image: {path}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <source>Error loading image: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <source>Error setting image: {error}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="42"/>
        <source>Add a new color range to detect. Each color can have its own RGB range tolerances.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="45"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="52"/>
        <source>color.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="83"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="88"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="95"/>
        <source>eye.png</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="43"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="324"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRangeDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="39"/>
        <source>HSV Color Range Selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="381"/>
        <source>Select Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRangeViewer</name>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="14"/>
        <source>Color Range Viewer</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="37"/>
        <source>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="42"/>
        <source>Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="76"/>
        <source>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="81"/>
        <source>Unselected</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="69"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="79"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="258"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CoordinateController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="124"/>
        <source>GPS Coordinates: {coords}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="150"/>
        <source>📋 Copy coordinates</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="154"/>
        <source>🗺️ Open in Google Maps</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="158"/>
        <source>🌍 View in Google Earth</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="162"/>
        <source>📱 Send via WhatsApp</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="166"/>
        <source>📨 Send via Telegram</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="238"/>
        <source>Coordinates copied</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="248"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="262"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="325"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="345"/>
        <source>Coordinates unavailable</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="332"/>
        <source>Coordinate: {lat}, {lon} — {maps}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="352"/>
        <source>Coordinates: {lat}, {lon}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="392"/>
        <source>No bearing info available</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="433"/>
        <source>North-Oriented View (Rotated {angle:.1f}°)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="465"/>
        <source>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="475"/>
        <source>↑ NORTH</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="484"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="495"/>
        <source>Error: {error}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CoordinatorWindow</name>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="30"/>
        <source>Search Coordinator</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="49"/>
        <source>Create New Search</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="54"/>
        <source>Open Existing Search</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="59"/>
        <source>Save Search</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="65"/>
        <source>Add Batches to Search</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="69"/>
        <source>Add more batch XML files to the current search project</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="87"/>
        <source>Dashboard</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="91"/>
        <source>Batch Status</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="95"/>
        <source>AOI Analysis</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="103"/>
        <source>Load Review XML</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="109"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="610"/>
        <source>Export Consolidated Results</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="121"/>
        <source>Project Information</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="126"/>
        <source>No project loaded</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="128"/>
        <source>Project:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="133"/>
        <source>Created by:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="138"/>
        <source>Date:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="157"/>
        <source>Total Batches</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="158"/>
        <source>Total Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="159"/>
        <source>Total Reviews</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="160"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="305"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="337"/>
        <source>Reviewers</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="170"/>
        <source>Review Progress</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="175"/>
        <source>Overall Completion:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="180"/>
        <source>0%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="194"/>
        <source>Not Reviewed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="203"/>
        <source>In Progress</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="212"/>
        <source>Complete</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="220"/>
        <source>AOI Summary</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="228"/>
        <source>Total AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="236"/>
        <source>Flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="243"/>
        <source>Active Reviewers</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="245"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="666"/>
        <source>No reviewers yet</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="292"/>
        <source>Batch review status and assignments. Load reviewer XMLs to update progress.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="301"/>
        <source>Batch ID</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="302"/>
        <source>Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="303"/>
        <source>Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="304"/>
        <source>Reviews</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="306"/>
        <source>Status</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="325"/>
        <source>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="334"/>
        <source>Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="335"/>
        <source>Location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="336"/>
        <source>Flag Count</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="338"/>
        <source>Comments</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="355"/>
        <source>New Search Project</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="356"/>
        <source>Enter project name:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="365"/>
        <source>Coordinator Information</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="366"/>
        <source>Enter your name:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="375"/>
        <source>Select Batch Files</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="376"/>
        <source>Select Initial Batch XML Files</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="379"/>
        <source>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="393"/>
        <source>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="395"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="410"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="510"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="557"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="612"/>
        <source>XML Files (*.xml)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="408"/>
        <source>Save Search Project</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="420"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="453"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="469"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="529"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="593"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="619"/>
        <source>Success</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="421"/>
        <source>Search project &apos;{project}&apos; created successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="428"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="459"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="599"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="623"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="429"/>
        <source>Failed to save project file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <source>Failed to create project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="438"/>
        <source>Open Search Project</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="440"/>
        <source>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="454"/>
        <source>Project loaded successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="460"/>
        <source>Failed to load project file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="470"/>
        <source>Project saved successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <source>Failed to save project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="480"/>
        <source>No Project</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="481"/>
        <source>Please create or open a project first.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="488"/>
        <source>Add Batches</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="489"/>
        <source>Add More Batch XML Files</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="492"/>
        <source>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="508"/>
        <source>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="531"/>
        <source>Successfully added {count} batch(es) to the project!
Total batches: {total}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="541"/>
        <source>No Batches Added</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="543"/>
        <source>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="555"/>
        <source>Select Reviewer&apos;s ADIAT_Data.xml File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="568"/>
        <source>No Batches</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="569"/>
        <source>No batches found in project.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="577"/>
        <source>Select Batch</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="578"/>
        <source>Which batch does this review belong to?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="594"/>
        <source>Review data loaded and merged successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="600"/>
        <source>Failed to load review data.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="620"/>
        <source>Consolidated results exported to:
{path}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="623"/>
        <source>Failed to export results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="649"/>
        <source>{value}%</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>CoverageExtentExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="129"/>
        <source>Generate Coverage Extent KML</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="131"/>
        <source>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="145"/>
        <source>Save Coverage Extent KML</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="147"/>
        <source>KML files (*.kml)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="156"/>
        <source>Generating Coverage Extent KML</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="159"/>
        <source>Calculating coverage extent...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="202"/>
        <source>Error generating coverage extent KML</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="208"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="256"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="209"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="257"/>
        <source>Failed to generate coverage extent KML:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="239"/>
        <source>Coverage extent generation cancelled</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="250"/>
        <source>Error generating coverage extent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="263"/>
        <source>No valid images found for coverage extent calculation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="269"/>
        <source>Coverage Extent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="271"/>
        <source>Could not calculate coverage extent.

Images processed: {processed}
Images skipped: {skipped}

Images may be skipped for the following reasons:
  • Missing GPS data in EXIF
  • No valid GSD (missing altitude/focal length)
  • Gimbal not nadir (must be -85° to -95°)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="293"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="294"/>
        <source>{value:.2f} acres</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="298"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="299"/>
        <source>{value:.3f} km²</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="302"/>
        <source>Coverage extent KML saved: {area}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="311"/>
        <source>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="319"/>
        <source>Coverage Extent KML Generated</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="321"/>
        <source>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>DirectoriesPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="55"/>
        <source>Select Input Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="72"/>
        <source>Select Output Directory</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="58"/>
        <source>Processing...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="72"/>
        <source>Starting...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="76"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="103"/>
        <source>Cancelling...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="104"/>
        <source>Cancellation requested...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>FrameTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="214"/>
        <source>Invalid Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="215"/>
        <source>{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="217"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="226"/>
        <source>Aspect Ratio Mismatch</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="228"/>
        <source>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GPSMapController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="54"/>
        <source>No GPS data found in images</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GPSMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="39"/>
        <source>GPS Map View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="91"/>
        <source>Zoom In (+)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="95"/>
        <source>Zoom Out (-)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="99"/>
        <source>Fit All (F)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="107"/>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="189"/>
        <source>Satellite View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="115"/>
        <source>Click point to select • Drag to pan • Scroll to zoom</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="186"/>
        <source>Map View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="223"/>
        <source>⚠ {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="233"/>
        <source>Map Tile Loading Issue</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="235"/>
        <source>{error}

The map will continue to work with cached tiles where available.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GPSMapView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1085"/>
        <source>Copy Data</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GalleryUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="289"/>
        <source>0 AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="330"/>
        <source>AOI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="330"/>
        <source>AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="332"/>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="355"/>
        <source>{count} {label}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="350"/>
        <source>Area of Interest</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="352"/>
        <source>Areas of Interest</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GeneralSettingsPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="121"/>
        <source>Select AOI Highlight Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="159"/>
        <source>Benchmark Complete</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="161"/>
        <source>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="27"/>
        <source>Select a target color from an image to detect.
Opens a color picker that allows you to:
• Load an image from the input folder
• Click on pixels to sample colors
• Automatically calculates HSV values
• Sets Hue, Saturation, and Value ranges
The selected color becomes the center of your HSV detection range.
Adjust the +/- range values to capture color variations.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="37"/>
        <source> Pick Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="44"/>
        <source>color.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="57"/>
        <source>Visual preview of the currently selected target color.
Shows the center color of your HSV detection range.
The actual detection will match colors within the specified +/- ranges around this color.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="92"/>
        <source>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="97"/>
        <source>Hue Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="109"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="215"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="315"/>
        <source>-</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="121"/>
        <source>Lower hue range tolerance.
• Range: 0 to 179
• Default: 20
Subtracts from the target hue value to define the lower bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, minus 20 = detects hues from 80-100.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="147"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="250"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="350"/>
        <source>+</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="159"/>
        <source>Upper hue range tolerance.
• Range: 0 to 179
• Default: 20
Adds to the target hue value to define the upper bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, plus 20 = detects hues from 100-120.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="198"/>
        <source>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="203"/>
        <source>Saturation Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="227"/>
        <source>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="262"/>
        <source>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="298"/>
        <source>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="303"/>
        <source>Value Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="327"/>
        <source>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="362"/>
        <source>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="410"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="415"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="422"/>
        <source>eye.png</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRangeAssistant</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="661"/>
        <source>HSV Color Range Assistant - Click Selection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1476"/>
        <source>
&lt;h2&gt;HSV Color Range Assistant - Help&lt;/h2&gt;

&lt;p&gt;This tool helps you pick the HSV color range of a specific color in a photo.
Click on the BROWSE button to open an image.&lt;/p&gt;

&lt;h3&gt;Navigation:&lt;/h3&gt;
&lt;p&gt;• Use the mouse scroll wheel to zoom in/out of the image&lt;br&gt;
• Use the left mouse button to drag the image around and pan it&lt;/p&gt;

&lt;h3&gt;Color Selection:&lt;/h3&gt;
&lt;p&gt;• Hold the &lt;b&gt;CTRL/OPTION key&lt;/b&gt; while left clicking on a color in the image that you want to select&lt;br&gt;
• All pixels in the image that share that HSV color value will be selected and highlighted in white&lt;/p&gt;

&lt;h3&gt;Selection Radius:&lt;/h3&gt;
        &lt;p&gt;You can adjust the Selection Radius of the mouse cursor to be larger or smaller.
        When you CTRL click it will select all colors within that radius of the mouse cursor.&lt;/p&gt;

&lt;h3&gt;Corrections:&lt;/h3&gt;
&lt;p&gt;If you make a mistake you can UNDO the last selection or you can press the RESET button to start over.&lt;/p&gt;

&lt;h3&gt;Mask Preview:&lt;/h3&gt;
        &lt;p&gt;On the right side the Mask Preview section will show you what pixels in the image were selected.
        If you see pixels outside of your target object that you are selecting that means you may need to
        adjust the Color Tolerance or be more careful with your selections.&lt;/p&gt;
</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1504"/>
        <source>HSV Color Range Assistant - Help</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="95"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="118"/>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="123"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="427"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="49"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="59"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="343"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HSVColorRowWizardWidget</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="392"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="392"/>
        <source>H: {h_min}-{h_max}°, S: {s_min}-{s_max}, V: {v_min}-{v_max}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>HelpDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="25"/>
        <source>Viewer Help</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="60"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ImageAdjustmentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="83"/>
        <source>Image Adjustment</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="96"/>
        <source>Adjustments</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="124"/>
        <source>Exposure:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="127"/>
        <source>Highlights:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="130"/>
        <source>Shadows:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="133"/>
        <source>Clarity:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="136"/>
        <source>Radius:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="146"/>
        <source>Reset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="147"/>
        <source>Apply</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="148"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ImageAnalysisGuide</name>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="14"/>
        <source>Image Analysis Guide</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="39"/>
        <source>Welcome to ADIAT</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="67"/>
        <source>Please select the ADIAT_Data.xml file from previous analysis:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="79"/>
        <source>No file selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="94"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="266"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="307"/>
        <source>Browse...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="123"/>
        <source>What would you like to do?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="160"/>
        <source>Start New Image Analysis</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="178"/>
        <source>Review Existing Image Analysis</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="223"/>
        <source>Select Directories</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="245"/>
        <source>Where are the images you want to analyze?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="286"/>
        <source>Where do you want ADIAT to store the output files?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="348"/>
        <source>Image Capture Information</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="370"/>
        <source>What drone/camera was used to capture images?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="400"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="452"/>
        <source>ft</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="457"/>
        <source>m</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="495"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="516"/>
        <source>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="526"/>
        <source>--</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="565"/>
        <source>Search Target Size</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="590"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="621"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="660"/>
        <source>ALGORITHM SELECTION GUIDE</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="682"/>
        <source>Are you using thermal images?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="727"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1114"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="758"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1099"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="831"/>
        <source>Reset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="888"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="147"/>
        <source>Algorithm Parameters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="918"/>
        <source>General Settings</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="940"/>
        <source>What color should be used to highlight Areas of Interest (AOIs)?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="960"/>
        <source>Select Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1009"/>
        <source>How many images should be processed at the same time?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1033"/>
        <source>Run Benchmark</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1056"/>
        <source>What resolution should images be processed at?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1084"/>
        <source>Were the images captured in different lighting conditions?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1177"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1189"/>
        <source>Skip this wizard in the future</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1217"/>
        <source>Back</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1229"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="261"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="266"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="272"/>
        <source>Continue</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="102"/>
        <source>ADIAT Image Analysis Guide</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="256"/>
        <source>Load Results</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="269"/>
        <source>Start Processing</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ImageLoadController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="112"/>
        <source>(Image {current} of {total})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="352"/>
        <source>Error Loading Image</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>LoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="12"/>
        <source>Generating Report</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="29"/>
        <source>Report generation in progress...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="33"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MRMap</name>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="29"/>
        <source>Number of segments to divide each image into for MR Map analysis.
Each segment is processed independently for multi-resolution feature detection.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in images with varying features.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="38"/>
        <source>Image Segments:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="56"/>
        <source>Select the number of segments to divide each image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The MR Map (Multi-Resolution Map) algorithm analyzes features at multiple scales:
• 1 segment: Process whole image (best for small images or uniform content)
• More segments: Analyze local regions independently (better for large images)
Higher segment counts improve detection in images with varying features across the scene.
Recommended: 4-9 segments for typical drone imagery.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="67"/>
        <source>1</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="72"/>
        <source>2</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="77"/>
        <source>4</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="82"/>
        <source>6</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="87"/>
        <source>9</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="92"/>
        <source>16</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="97"/>
        <source>25</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="102"/>
        <source>36</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="131"/>
        <source>Color Space:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="149"/>
        <source>Select the color space for MR Map analysis.
The MR Map algorithm analyzes features in different color representations:
• LAB: Perceptually uniform color space (default, better for color difference analysis)
• RGB: Standard red-green-blue color space (good for general use)
• HSV: Hue-Saturation-Value color space (better for color-based feature detection)
Different color spaces can improve detection depending on the image content.
Recommended: LAB for most cases, HSV for color-rich imagery.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="159"/>
        <source>LAB</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="164"/>
        <source>RGB</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="169"/>
        <source>HSV</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="198"/>
        <source>Window size for multi-resolution analysis.
Determines the spatial scale of features to detect.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="202"/>
        <source>Window Size:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="209"/>
        <source>Set the window size for multi-resolution analysis.
• Range: 1 to 10
• Default: 5
The MR Map algorithm analyzes features at multiple spatial scales using sliding windows:
• Smaller values (1-3): Detect fine details and small features
• Medium values (4-6): Balanced detection (recommended for most cases)
• Larger values (7-10): Detect larger features and patterns
Window size affects the spatial resolution of feature detection.
Larger windows provide more context but may miss small objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="254"/>
        <source>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="258"/>
        <source>Threshold:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="271"/>
        <source>Adjust the detection threshold for MR Map algorithm.
• Range: 1 to 200
• Default: 100
• Slider is inverted: LEFT = higher threshold, RIGHT = lower threshold
The MR Map algorithm detects features at multiple spatial resolutions:
• Lower values (1-50): Very sensitive, detects many features (may include noise)
• Medium values (51-150): Balanced detection (recommended for most cases)
• Higher values (151-200): Less sensitive, only detects prominent features
Threshold controls how distinct a feature must be to be detected.
Note: Slider appearance is inverted - move left for stricter, right for more lenient.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="326"/>
        <source>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="331"/>
        <source>100</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MRMapWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="21"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="41"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="56"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="92"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="105"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="22"/>
        <source>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="52"/>
        <source>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="57"/>
        <location filename="../resources/views/images/MainWindow.ui" line="133"/>
        <location filename="../resources/views/images/MainWindow.ui" line="597"/>
        <source> Select</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="64"/>
        <location filename="../resources/views/images/MainWindow.ui" line="140"/>
        <source>folder.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="76"/>
        <source>Path to the output folder for saving analysis results.
Click the Select button to browse for a destination folder.
Results include:
• Processed images with detected objects marked
• CSV file with detection coordinates and metadata
• KML file for viewing results in mapping applications
• Additional algorithm-specific output files</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="97"/>
        <source>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="101"/>
        <source>Input Folder:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="113"/>
        <source>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="117"/>
        <source>Output Folder:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="129"/>
        <source>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="152"/>
        <source>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="209"/>
        <source>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="213"/>
        <source>Min Object Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="225"/>
        <source>Set the minimum object area in pixels for detection filtering.
• Range: 1 to 999 pixels
• Default: 10 pixels
Objects smaller than this threshold will be filtered out and not detected.
• Lower values: Detect smaller objects (may increase false positives)
• Higher values: Only detect larger objects (reduces noise)
Use to filter out small artifacts and noise in detection results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="269"/>
        <source>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="273"/>
        <source>Max Object Area (px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="288"/>
        <source>Set the maximum object area in pixels for detection filtering.
• Range: 0 to 99999 pixels
• Default: 0 (None - no maximum filter applied)
• Special value: 0 displays as &quot;None&quot;
Objects larger than this threshold will be filtered out and not detected.
• Lower values: Only detect smaller objects
• Higher values: Allow detection of larger objects
• Set to 0 (None): No maximum size filtering
Use to exclude very large false positive detections like shadows or terrain features.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="299"/>
        <source>None</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="323"/>
        <source>Disable the maximum size filter and allow detections of any size.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="326"/>
        <source>No max limit</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="359"/>
        <source>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="363"/>
        <source>Object Identifer Color:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="370"/>
        <source>Select the color used to mark detected objects in output images.
• Default: Green (RGB: 0, 255, 0)
Click to open a color picker dialog and choose a different marker color.
The selected color will be used for:
• Drawing circles/rectangles around detected objects
• Highlighting AOI locations on output images
• Creating visual markers in the results viewer
Choose a color that contrasts well with your image content for best visibility.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="395"/>
        <source>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="399"/>
        <source>Max Processes: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="417"/>
        <source>Set the maximum number of parallel processes for image analysis.
• Range: 1 to 20 processes
• Default: 10 processes
The application uses multiprocessing to analyze multiple images simultaneously:
• Higher values: Faster processing (uses more CPU cores and memory)
• Lower values: Slower processing (uses fewer system resources)
• Recommended: Set to number of CPU cores or slightly higher
• For systems with limited RAM, reduce this value to prevent memory issues
Each process analyzes one image at a time, so more processes = more parallel image processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="446"/>
        <source>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="450"/>
        <source>Processing Resolution:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="468"/>
        <source>Select processing resolution as percentage of original image size:
• 100%: Original resolution (no scaling, highest quality, slowest)
• 75%: High quality (~56% of pixels, ~1.8x faster)
• 50%: Balanced quality (25% of pixels, ~4x faster) - RECOMMENDED
• 33%: Fast processing (~11% of pixels, ~9x faster)
• 25%: Very fast (6% of pixels, ~16x faster)
• 10%: Ultra fast (1% of pixels, ~100x faster)

Percentage scaling preserves original aspect ratio.
Works with any image size, orientation, or aspect ratio.

Min/Max Area values are always specified in original resolution.
All results are returned in original resolution coordinates.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="530"/>
        <source>Enable histogram normalization preprocessing on images before detection.
Histogram normalization adjusts image colors to match a reference image:
• Equalizes lighting and color differences across images
• Corrects for varying sun angles, shadows, and atmospheric conditions
• Standardizes color appearance across image set
• Improves consistency of detection results
When enabled, select a reference image with ideal lighting/color conditions.
Useful when processing images taken at different times or under varying conditions.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="540"/>
        <source>Normalize Histograms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="555"/>
        <source>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="559"/>
        <source>Reference Image:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="571"/>
        <source>Path to the reference image for histogram normalization.
Click the Select button to choose an image.
Choose an image with ideal lighting and color conditions:
• Clear, well-lit image from your dataset
• Representative of the desired appearance
• Typical lighting conditions for your mission
All other images will be color-adjusted to match this reference.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="592"/>
        <source>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="604"/>
        <source>image.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="642"/>
        <source>Select the detection algorithm to use for image analysis.

Each algorithm has specific strengths and use cases:

• HSV Color Range: Best for detecting specific colored objects
• Color Range (RGB): Alternative color detection using RGB color space
• RX Anomaly: Statistical detection for unusual/anomalous objects
• Thermal Anomaly: Detects temperature anomalies in thermal imagery
• Thermal Range: Temperature-based detection in thermal images
• Matched Filter: Target-based detection using spectral matching
• MR Map: Multi-resolution feature detection at various scales
• AI Person Detector: Machine learning for detecting people

Hover over the algorithm dropdown for detailed descriptions of each algorithm.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="658"/>
        <source>Algorithm:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="682"/>
        <source>Select the detection algorithm for your image analysis task.
Each algorithm has unique strengths and optimal use cases:

═══════════════════════════════════════════════════
HSV COLOR RANGE
═══════════════════════════════════════════════════
What it does: Detects objects by specific color ranges using HSV color space
Strengths:
• Best for detecting brightly colored objects (orange, yellow, red clothing)
• Robust to lighting variations (HSV separates color from brightness)
• Highly customizable with per-channel ranges
• Interactive color selection tools available
Weaknesses:
• Requires careful color range tuning for optimal results
• May struggle with color variations in shadows
• Not effective for colorless or camouflaged objects
Best for: Search &amp; Rescue (colored clothing, equipment), colored vehicles, tents, colored tarps

═══════════════════════════════════════════════════
COLOR RANGE (RGB)
═══════════════════════════════════════════════════
What it does: Detects objects by RGB color ranges
Strengths:
• Simple and intuitive RGB color specification
• Fast processing speed
• Good for basic color-based detection
Weaknesses:
• More sensitive to lighting changes than HSV
• RGB channels mix color and brightness information
• Less flexible than HSV for complex color variations
Best for: Controlled lighting situations, quick basic color detection, simple scenarios

═══════════════════════════════════════════════════
RX ANOMALY
═══════════════════════════════════════════════════
What it does: Statistical anomaly detection - finds pixels that are unusual compared to background
Strengths:
• Detects objects that don&apos;t match the background (no target sample needed)
• Excellent for finding camouflaged or partially hidden objects
• Works across all image types (RGB, thermal, multispectral)
• Automatically adapts to scene characteristics
• Good for detecting subtle differences
Weaknesses:
• May detect natural anomalies (rocks, vegetation changes)
• Requires tuning sensitivity to balance detection vs false positives
• Higher segment counts significantly increase processing time
• Less effective in highly varied/cluttered backgrounds
Best for: Missing person searches (human among vegetation), camouflaged objects, unknown targets, anything unusual in the scene

═══════════════════════════════════════════════════
THERMAL ANOMALY
═══════════════════════════════════════════════════
What it does: Detects temperature anomalies in thermal imagery (hot/cold spots)
Strengths:
• Finds temperature outliers automatically (no specific temp needed)
• Excellent for detecting heat sources (people, animals, fires)
• Works day or night with thermal cameras
• Detects through light vegetation
• Adjustable for hot, cold, or both types of anomalies
Weaknesses:
• Requires thermal (FLIR) imagery
• May detect sun-heated objects (rocks, vehicles)
• Temperature gradients can cause false positives
• Affected by ambient temperature and weather
Best for: Night searches, detecting people/animals by body heat, finding heat sources, cold spot detection

═══════════════════════════════════════════════════
THERMAL RANGE
═══════════════════════════════════════════════════
What it does: Temperature-based detection within a specific temperature range
Strengths:
• Precise temperature-based detection
• Excellent for finding humans (body temp ~35-40°C / 95-104°F)
• Filters out non-target temperatures effectively
• Works day or night with thermal cameras
• Very reliable when target temperature is known
Weaknesses:
• Requires thermal (FLIR) imagery with temperature data
• Must know target temperature range in advance
• Ambient conditions affect target temperature
• May miss targets in extreme weather (hypothermia cases)
Best for: Human detection (known body temp), specific temperature targets, fire detection (high temp range)

═══════════════════════════════════════════════════
MATCHED FILTER
═══════════════════════════════════════════════════
What it does: Target-based detection using spectral signature matching
Strengths:
• Very precise when you have a target sample
• Uses spectral/color &quot;signature&quot; of target for matching
• Reduces false positives by matching known target characteristics
• Good for detecting specific object types
Weaknesses:
• Requires a reference image or color sample of the target
• Less effective if target appearance varies significantly
• Lighting differences can affect matching accuracy
• Not suitable for unknown targets
Best for: Finding specific known objects (specific vehicle color, specific clothing), when you have a target sample to match

═══════════════════════════════════════════════════
MR MAP (Multi-Resolution Map)
═══════════════════════════════════════════════════
What it does: Multi-resolution feature detection at various spatial scales
Strengths:
• Detects features at multiple scales simultaneously
• Good for finding objects of varying sizes
• Effective for complex scene analysis
• Can detect both large and small features in one pass
Weaknesses:
• More computationally intensive
• Requires careful parameter tuning
• Higher segment counts significantly increase processing time
• May produce more false positives requiring filtering
Best for: Complex scenes with varying object sizes, when target size is unknown, general feature mapping

═══════════════════════════════════════════════════
AI PERSON DETECTOR
═══════════════════════════════════════════════════
What it does: Deep learning AI model trained specifically to detect people
Strengths:
• Extremely accurate for detecting people in various poses
• Works with partial visibility and varied clothing
• No color/temperature requirements - works on regular RGB images
• Trained on millions of images for robust detection
• Detects people in complex backgrounds
• Minimal parameter tuning needed
Weaknesses:
• Only detects people (not vehicles, equipment, etc.)
• Computationally intensive - slower processing
• Requires adequate image resolution
• May struggle with very distant/small people
• Less effective with heavy occlusion
Best for: Search &amp; Rescue operations (missing persons), people counting, situations where only human detection is needed

═══════════════════════════════════════════════════
ALGORITHM SELECTION GUIDE
═══════════════════════════════════════════════════
• For colorful objects (bright clothing, gear): HSV Color Range
• For thermal cameras searching people: Thermal Range or Thermal Anomaly
• For camouflaged or hidden subjects: RX Anomaly
• For detecting people specifically: AI Person Detector
• When you have a target sample: Matched Filter
• For unknown targets that stand out: RX Anomaly or Thermal Anomaly
• For fastest processing: Color Range (RGB) or HSV Color Range
• For most accurate people detection: AI Person Detector</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="894"/>
        <source>Start processing images with the selected algorithm.
Requirements before starting:
• Input folder must be selected with valid images
• Output folder must be selected
• Algorithm must be selected
• All required algorithm parameters must be configured
Processing will:
• Analyze all images in the input folder using the selected algorithm
• Apply global filters (min/max area, K-Means, histogram normalization)
• Save results to output folder (marked images, CSV, KML files)
• Display progress and results in the output window
Click Cancel during processing to stop the analysis.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="918"/>
        <source>Start</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="949"/>
        <source>Cancel the currently running image analysis process.
Stops processing immediately and safely terminates all worker processes.
Effects of canceling:
• All running analysis processes are stopped
• Partial results are saved up to the cancellation point
• Images already processed will have output files in the output folder
• Processing can be restarted after cancellation
• Returns to the ready state
Use when you need to stop processing to adjust settings or fix issues.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="963"/>
        <source> Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="970"/>
        <source>cancel.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="998"/>
        <source>Open the Results Viewer to review detection results.
Available after processing completes successfully.
The Results Viewer provides:
• Interactive image browsing with detected objects highlighted
• Side-by-side comparison of original and processed images
• Navigation through all processed images
• AOI (Area of Interest) details and metadata
• GPS coordinates for detected objects
• Export options for selected detections
• Zoom and pan capabilities
• Filtering and sorting of detection results
Use to review, verify, and export analysis results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1018"/>
        <source> View Results</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1028"/>
        <source>search</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1085"/>
        <source>Menu</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1096"/>
        <source>Help</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1107"/>
        <source>Image Analysis Wizard</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1110"/>
        <source>Launch the Image Analysis Guide wizard to configure analysis settings.
Opens a step-by-step wizard to:
• Select input and output directories
• Configure image capture settings (drone, altitude, GSD)
• Set target object size
• Choose detection algorithm
• Configure algorithm-specific parameters
• Set general processing options
The wizard will close this window and open with all settings pre-populated.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1128"/>
        <source>Load Results File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1131"/>
        <source>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1144"/>
        <source>Preferences</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1147"/>
        <source>Open the Preferences dialog to configure application settings.
Adjust global settings including:
• Application theme (Light/Dark)
• Max AOI warning threshold
• AOI circle radius for clustering
• Coordinate system format (Lat/Long, UTM)
• Temperature unit (Fahrenheit/Celsius)
• Distance unit (Meters/Feet)
• Drone sensor configuration file
All changes are saved automatically.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1166"/>
        <source>Video Parser</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1169"/>
        <source>Open the Video Parser utility to extract frames from video files.
Convert video footage into individual frame images for analysis.
Features:
• Extract frames at specified time intervals
• Optional SRT file support for GPS metadata
• Supports common video formats (MP4, AVI, MOV, etc.)
• Embeds location data into extracted frames
Use to prepare video footage for image-based analysis.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1186"/>
        <source>Streaming Detector</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1189"/>
        <source>Switch to the Streaming Detector</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1199"/>
        <source>Real-Time Anomaly Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1202"/>
        <source>Open the Real-Time Anomaly Detection window for advanced live analysis.
Combines multiple detection algorithms for comprehensive real-time anomaly detection.
Features:
• Motion detection with background subtraction
• Color quantization anomaly detection
• Advanced streaming video processing
• Detection fusion and temporal filtering
• Real-time performance optimization
• Multi-threaded processing for better performance
• Enhanced detection accuracy through algorithm combination
Designed for detecting unusual objects, movement, and colors in real-time video streams.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1222"/>
        <source>Search Coordinator</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1225"/>
        <source>Open the Search Coordinator window for managing multi-batch review projects.
Features:
• Create and manage search projects with multiple batches
• Track reviewer progress across multiple image sets
• Consolidate review results from multiple reviewers
• View dashboard with search status and metrics
• Export consolidated results
• Manage batch assignments and reviewer coordination
Ideal for large-scale searches with multiple reviewers and image batches.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1241"/>
        <source>Ctrl+Shift+C</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1246"/>
        <source>Manual</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1249"/>
        <source>Open the online help documentation in your web browser.
Access comprehensive documentation, tutorials, and user guides.
Provides detailed information on all features and algorithms.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1261"/>
        <source>Community Forum</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1264"/>
        <source>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1276"/>
        <source>YouTube Channel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="71"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="234"/>
        <source>Select the detection algorithm for your image analysis task:

HSV COLOR RANGE: Detects brightly colored objects (clothing, vehicles, tents)
  • Best for: Colored objects in varying lighting conditions
  • Limitation: Requires color tuning, not for camouflaged objects

COLOR RANGE (RGB): Simple RGB color detection, fast processing
  • Best for: Basic color detection in controlled lighting
  • Limitation: Sensitive to lighting changes

RX ANOMALY: Finds objects that don&apos;t match background (no sample needed)
  • Best for: Camouflaged/hidden subjects, unknown targets
  • Limitation: May detect natural anomalies, slower with more segments

THERMAL ANOMALY: Detects hot/cold spots in thermal imagery
  • Best for: Night searches, detecting people/animals by body heat
  • Limitation: Requires thermal camera, may detect sun-heated objects

THERMAL RANGE: Temperature-based detection (e.g., 35-40°C for humans)
  • Best for: Human detection with thermal camera (known body temp)
  • Limitation: Requires thermal camera, must know target temperature

MATCHED FILTER: Matches targets using color signature from sample
  • Best for: Specific known objects when you have a target sample
  • Limitation: Requires reference image, not for unknown targets

MR MAP: Multi-resolution detection for objects of varying sizes
  • Best for: Complex scenes with unknown target sizes
  • Limitation: Slower processing, more false positives

AI PERSON DETECTOR: Deep learning model for accurate people detection
  • Best for: Search &amp; Rescue, finding people in any clothing/pose
  • Limitation: Only detects people, slower processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="309"/>
        <source>Select AOI Highlight Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="323"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="341"/>
        <source>Select Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="358"/>
        <source>Select a Reference Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="360"/>
        <source>Images (*.png *.jpg)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="408"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="440"/>
        <source>Value Adjusted</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="410"/>
        <source>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="442"/>
        <source>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="520"/>
        <source>Please set the input and output directories.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="526"/>
        <source>--- Starting image processing ---</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="593"/>
        <source>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="616"/>
        <source>Area of Interest Limit ({limit}) exceeded. Continue?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="619"/>
        <source>Area of Interest Limit Exceeded</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="643"/>
        <source>--- Image Processing Completed ---</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="646"/>
        <source>{count} images with areas of interest identified</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="652"/>
        <source>No areas of interest identified</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="671"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1076"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1099"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1115"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1131"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1147"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="680"/>
        <source>Select File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="700"/>
        <source>Select Results Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="733"/>
        <source>Failed to scan folder: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="755"/>
        <source>No Results Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="756"/>
        <source>No ADIAT_DATA.XML files were found in the selected folder.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="773"/>
        <source>Failed to display results: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="784"/>
        <source>Scan failed: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="827"/>
        <source>Failed to open viewer: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1023"/>
        <source>Error Loading Results</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1024"/>
        <source>Failed to load results file:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1077"/>
        <source>Failed to open Streaming Detector:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1100"/>
        <source>Failed to open Search Coordinator:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1116"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1132"/>
        <source>Failed to open Community Help:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1148"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1272"/>
        <source>Invalid Value</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MapExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="34"/>
        <source>Map Export Options</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="45"/>
        <source>Configure Map Export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="53"/>
        <source>Export Type</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="56"/>
        <source>KML File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="58"/>
        <source>Export to a KML file for use in Google Earth, etc.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="60"/>
        <source>CalTopo</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="61"/>
        <source>Export directly to a CalTopo map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="73"/>
        <source>Data to Include</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="76"/>
        <source>Drone/Image Locations</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="78"/>
        <source>Include markers for each drone image location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="80"/>
        <source>Flagged Areas of Interest</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="82"/>
        <source>Include markers for flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="84"/>
        <source>Coverage Area</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="86"/>
        <source>Include polygon(s) showing the geographic coverage extent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="88"/>
        <source>Include images without flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="90"/>
        <source>If unchecked, only export locations for images that have flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="101"/>
        <source>CalTopo Options</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="104"/>
        <source>Include Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="106"/>
        <source>Upload photos to CalTopo markers (CalTopo only)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="126"/>
        <source>Export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="130"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MatchedFilter</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="42"/>
        <source>Add a new color signature for matched filter detection. Each color can have its own threshold value.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="45"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="52"/>
        <source>color.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="83"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the thresholds before processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="88"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="95"/>
        <source>eye.png</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MatchedFilterController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="42"/>
        <source>No Colors Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="299"/>
        <source>Please add at least one color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilterWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="47"/>
        <source>No Targets Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="57"/>
        <source>View Range</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="218"/>
        <source>Please add at least one target color to detect.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MeasureDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="62"/>
        <source>Measure Distance</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="75"/>
        <source>Ground Sample Distance</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="78"/>
        <source>GSD:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="80"/>
        <source>Enter GSD value</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="84"/>
        <source>cm/px</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="92"/>
        <source>Measurement</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="95"/>
        <source>Distance:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="96"/>
        <source>--</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="107"/>
        <source>Click on the image to place the first point,
then click again to place the second point.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="115"/>
        <source>Clear</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="117"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="269"/>
        <source>No GSD value</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MediaSelector</name>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool (ADIAT)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="31"/>
        <source>What type of media are you working with?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="86"/>
        <source>Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="163"/>
        <source>RTMP, Video Files, HDMI Capture</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="169"/>
        <source>Streaming</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MotionDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="65"/>
        <source>Detection Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="70"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="74"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="295"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="317"/>
        <source>Auto</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="71"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="318"/>
        <source>Static Camera</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="72"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="319"/>
        <source>Moving Camera</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="76"/>
        <source>Mode:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="79"/>
        <source>Auto Mode: Detecting...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="85"/>
        <source>Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="90"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="334"/>
        <source>Frame Difference</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="91"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="96"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="335"/>
        <source>MOG2 Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="92"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="336"/>
        <source>KNN Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="93"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="337"/>
        <source>Optical Flow</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="94"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="338"/>
        <source>Feature Matching</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="98"/>
        <source>Algorithm:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="104"/>
        <source>Detection Parameters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="109"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="348"/>
        <source>Sensitivity: {value}%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="120"/>
        <source>Min Area:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="130"/>
        <source>Max Area:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="140"/>
        <source>Threshold:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="150"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="376"/>
        <source>Compensation: {value}%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="162"/>
        <source>Visualization</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="165"/>
        <source>Show Motion Vectors</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="170"/>
        <source>Show Camera Motion</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="178"/>
        <source>Detection Statistics</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="181"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="448"/>
        <source>Detections: 0</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="184"/>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="274"/>
        <source>Camera Motion: None</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="187"/>
        <source>FPS: 0.0</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="190"/>
        <source>Processing: 0.0ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="236"/>
        <source>Motion</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="256"/>
        <source>Detections: {count} | Total Area: {total} | Avg: {avg}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="266"/>
        <source>Camera Motion: ({x}, {y}) Confidence: {confidence}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="286"/>
        <source> (GPU)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="286"/>
        <source> (CPU)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="288"/>
        <source>FPS: {fps:.1f}{gpu}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="291"/>
        <source>Processing: {time:.1f}ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="297"/>
        <source>Auto Mode: {mode} ({confidence:.0%})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="308"/>
        <source>Auto Mode: {mode}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="432"/>
        <source>Total Detections</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="433"/>
        <source>Last Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="440"/>
        <source>{seconds:.1f}s ago</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionController.py" line="441"/>
        <source>Never</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="12"/>
        <source>Detection Mode</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="16"/>
        <source>Mode:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="22"/>
        <source>Auto</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="25"/>
        <source>Static Camera</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="28"/>
        <source>Moving Camera</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="37"/>
        <source>Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="41"/>
        <source>Algorithm:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="47"/>
        <source>Frame Difference</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="50"/>
        <source>MOG2 Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="53"/>
        <source>KNN Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="56"/>
        <source>Optical Flow</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="59"/>
        <source>Feature Matching</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="68"/>
        <source>Detection Parameters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="72"/>
        <source>Sensitivity: 50%</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="87"/>
        <source>Min Area:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MotionDetectionWizard.ui" line="103"/>
        <source>Max Area:</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>MotionDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionWizardController.py" line="36"/>
        <source>Auto</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionWizardController.py" line="37"/>
        <source>MOG2 Background</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/MotionDetection/controllers/MotionDetectionWizardController.py" line="48"/>
        <source>Sensitivity: {value}%</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PDFExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="150"/>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="159"/>
        <source>No Images to Export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="152"/>
        <source>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="161"/>
        <source>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="171"/>
        <source>Save PDF File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="173"/>
        <source>PDF files (*.pdf)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="214"/>
        <source>Generating PDF Report</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="217"/>
        <source>Generating PDF Report...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="258"/>
        <source>Failed to generate PDF file: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="274"/>
        <source>Success</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="275"/>
        <source>PDF report generated successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="292"/>
        <source>PDF generation failed: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="306"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PDFExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="27"/>
        <source>PDF Export Settings</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="35"/>
        <source>Enter the following information for the PDF report:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="44"/>
        <source>Enter organization name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="45"/>
        <source>Organization:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="49"/>
        <source>Enter search name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="50"/>
        <source>Search Name:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="55"/>
        <source>Export Options:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="60"/>
        <source>Include images without flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="62"/>
        <source>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="69"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="71"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PathValidationController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="87"/>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="137"/>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="170"/>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="220"/>
        <source>
  ... and {count} more</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="92"/>
        <source>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="100"/>
        <source>Source Images Not Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="111"/>
        <source>Select Source Images Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="143"/>
        <source>Some Images Still Missing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="145"/>
        <source>Found {found} of {total} images.

Still missing:
{missing}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="175"/>
        <source>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="183"/>
        <source>Detection Masks Not Found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="194"/>
        <source>Select Masks Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="226"/>
        <source>Some Masks Still Missing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="228"/>
        <source>Found {found} of {total} masks.

Still missing:
{missing}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>Preferences</name>
    <message>
        <location filename="../resources/views/Preferences.ui" line="14"/>
        <source>Preferences</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="48"/>
        <source>Select the application theme appearance.
Changes the overall color scheme and visual style.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="52"/>
        <source>Theme:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="64"/>
        <source>Choose the application theme:
• Light: Bright theme with light backgrounds and dark text
• Dark: Dark theme with dark backgrounds and light text
Changes apply immediately to all windows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="71"/>
        <source>Light</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="76"/>
        <source>Dark</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="107"/>
        <source>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="111"/>
        <source>Max Areas of Interest: </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="123"/>
        <source>Set the warning threshold for total AOIs detected during processing.
• Range: 0 to 1000
• Default: 100
When this number of AOIs is detected across all images:
• UI displays a warning message
• User can cancel processing, adjust settings, and rerun
• If no action taken, detection continues automatically
Use lower values to catch high detection counts early.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="154"/>
        <source>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="158"/>
        <source>Area of Interest Circle Radius(px):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="170"/>
        <source>Set the radius for combining nearby AOIs during detection.
• Range: 0 to 100 pixels
• Default: 25 pixels
When AOIs are within this radius of each other:
• They are combined into a single AOI
• Process repeats until no neighbors remain within radius
• Larger values: Combines more distant detections (fewer total AOIs)
• Smaller values: Keeps detections separate (more individual AOIs)
Use to consolidate clustered detections into single objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="202"/>
        <source>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="206"/>
        <source>Coordinate System:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="218"/>
        <source>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="226"/>
        <source>Lat/Long - Decimal Degrees</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="231"/>
        <source>Lat/Long - Degrees, Minutes, Seconds</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="236"/>
        <source>UTM</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="255"/>
        <source>Unit for displaying temperature measurements from thermal imagery.
Used when analyzing thermal images from thermal cameras.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="259"/>
        <source>Temperature Unit:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="271"/>
        <source>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="280"/>
        <source>Fahrenheit</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="285"/>
        <source>Celsius</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="304"/>
        <source>Unit for displaying distance and altitude measurements.
Used for drone altitude, object distances, and spatial calculations.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="308"/>
        <source>Distance Unit:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="320"/>
        <source>Select the distance unit for measurements:
• Meters (m): Metric distance unit (international standard)
  - 1 meter = 3.281 feet
  - Used for altitude, GSD, and distance calculations
• Feet (ft): Imperial distance unit (US standard)
  - 1 foot = 0.3048 meters
  - Common in US aviation and surveying
Applies to altitude displays, GSD calculations, and distance measurements.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="331"/>
        <source>Meters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="336"/>
        <source>Feet</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="355"/>
        <source>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="359"/>
        <source>Offline Only Mode:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="371"/>
        <source>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="374"/>
        <location filename="../resources/views/Preferences.ui" line="415"/>
        <source>Enable</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="392"/>
        <source>Use terrain elevation data (DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="397"/>
        <source>Use Terrain Elevation:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="409"/>
        <source>Enable terrain-corrected AOI positioning using DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="433"/>
        <source>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="437"/>
        <source>Terrain Cache:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="449"/>
        <source>0 tiles (0 MB)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="474"/>
        <source>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="478"/>
        <source>Clear Cache</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="510"/>
        <source>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="514"/>
        <source>Drone Sensor File Version:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="539"/>
        <source>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="543"/>
        <source>TextLabel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="571"/>
        <source>Replace the current drone sensor configuration file.
Allows updating to a newer version or custom sensor specifications.
Required file format: JSON with drone models, sensors, focal lengths, and dimensions.
Use this when:
• New drone models are available
• Sensor specifications need updating
• Custom camera configurations are needed
Backup existing file before replacing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="581"/>
        <source>Replace</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="601"/>
        <source>Close the Preferences window.
All changes are saved automatically when modified.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="72"/>
        <location filename="../app/core/controllers/Perferences.py" line="224"/>
        <source>{version}_{date}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="155"/>
        <source>{tiles} tiles ({size_mb:.1f} MB)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="161"/>
        <source>Not available</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="163"/>
        <location filename="../app/core/controllers/Perferences.py" line="171"/>
        <location filename="../app/core/controllers/Perferences.py" line="199"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="172"/>
        <source>Terrain service not available.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="178"/>
        <source>Clear Terrain Cache</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="180"/>
        <source>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="193"/>
        <source>Cache Cleared</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="194"/>
        <source>Cleared {count} cached terrain tiles.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="200"/>
        <source>Failed to clear cache: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="210"/>
        <source>Select a Drone Sensor File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Perferences.py" line="212"/>
        <source>Pickle Files (*.pkl)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>QtImageViewer</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/QtImageViewer.py" line="313"/>
        <source>Open image</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>RXAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="29"/>
        <source>Number of segments to divide each image into for analysis.
The RX algorithm analyzes each segment independently to detect local anomalies.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in images with varying backgrounds.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="38"/>
        <source>Image Segments:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="62"/>
        <source>Select the number of segments to divide each image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The RX Anomaly algorithm uses statistical analysis to detect unusual pixels:
• 1 segment: Analyzes the whole image at once (best for small images)
• More segments: Analyzes local regions independently (better for large images)
Higher segment counts improve detection in images with varying backgrounds.
Recommended: 4-9 segments for typical drone imagery.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="73"/>
        <source>1</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="78"/>
        <source>2</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="83"/>
        <source>4</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="88"/>
        <source>6</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="93"/>
        <source>9</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="98"/>
        <source>16</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="103"/>
        <source>25</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="108"/>
        <source>36</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="137"/>
        <source>Detection sensitivity for anomaly detection.
• Range: 1 to 10
• Default: 5
Controls how statistically different a pixel must be from the background to be detected:
• Lower values (1-3): DECREASE detections - less sensitive, only detects strong anomalies
• Higher values (7-10): INCREASE detections - more sensitive, detects subtle anomalies
Higher sensitivity finds more potential targets but may include noise/false positives.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="146"/>
        <source>Sensitivity:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="159"/>
        <source>Adjust the detection sensitivity for anomaly detection.
• Range: 1 to 10
• Default: 5
The RX algorithm uses statistical analysis to find pixels that differ from the background:
• Lower values (1-3): Less sensitive, only detects strong anomalies (fewer false positives)
• Medium values (4-6): Balanced detection (recommended for most cases)
• Higher values (7-10): More sensitive, detects subtle anomalies (more detections, may include noise)
Anomalies are pixels that are statistically different from the surrounding background.
Use lower sensitivity for clean images, higher for finding subtle targets.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="205"/>
        <source>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="209"/>
        <source>5</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizard</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="29"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="49"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="64"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="100"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="113"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>RecentColorWidget</name>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="68"/>
        <source>&lt;b&gt;RGB:&lt;/b&gt; ({r}, {g}, {b})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="97"/>
        <source>&lt;br&gt;&lt;b&gt;H (°):&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="100"/>
        <source> &lt;b&gt;S (%):&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="103"/>
        <source> &lt;b&gt;V (%):&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="112"/>
        <source>&lt;br&gt;&lt;b&gt;R:&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="115"/>
        <source> &lt;b&gt;G:&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="118"/>
        <source> &lt;b&gt;B:&lt;/b&gt; {min}-{max}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="124"/>
        <source>&lt;br&gt;&lt;b&gt;Threshold:&lt;/b&gt; {value}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>RecentColorsDialog</name>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="151"/>
        <source>Recent Colors</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="162"/>
        <source>Select a recently used color:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/Shared/views/RecentColorsDialog.py" line="178"/>
        <source>No recent colors found</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ResultsFolderDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="115"/>
        <source>Load Results Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="124"/>
        <source>Found {count} result(s)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Missing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="170"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="216"/>
        <source>Open in Google Maps</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="226"/>
        <source>No images available - cannot get GPS location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="228"/>
        <source>No GPS coordinates found in images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="248"/>
        <source>Open in Results Viewer</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ReviewOrNewPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="70"/>
        <source>No file selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="114"/>
        <source>Select ADIAT Results File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="125"/>
        <source>File Name Warning</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="127"/>
        <source>The selected file does not appear to be an ADIAT_Data.xml file.

Do you want to continue with this file?</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ReviewerNameDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="25"/>
        <source>Reviewer Name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="45"/>
        <source>Review Tracking</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="51"/>
        <source>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="60"/>
        <source>Your Name:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="64"/>
        <source>Enter your name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="65"/>
        <source>Enter your full name or identifier for review tracking</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="71"/>
        <source>Remember my name</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="74"/>
        <source>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="86"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="91"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="123"/>
        <source>Name Required</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="124"/>
        <source>Please enter your name to continue.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ScanProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="51"/>
        <source>Scanning for Results</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StatusController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="44"/>
        <source>GPS Coordinates</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="45"/>
        <source>Relative Altitude</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="46"/>
        <source>Gimbal Orientation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="47"/>
        <source>Estimated Average GSD</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="48"/>
        <source>Temperature</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="49"/>
        <source>Color Values</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="50"/>
        <source>Drone Orientation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="115"/>
        <source>Error Loading Images</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="121"/>
        <source>No active images available.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="125"/>
        <source>No other images available.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="86"/>
        <source>Are you looking for specific colors?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="159"/>
        <source>Color Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="160"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="164"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="181"/>
        <source>Color Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="184"/>
        <source>Algorithm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="186"/>
        <source>{algorithm} Parameters</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamConnectionPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="25"/>
        <source>Click Scan to find devices...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="41"/>
        <source>480p</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="42"/>
        <source>720p</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="43"/>
        <source>1080p</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="44"/>
        <source>4K</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="156"/>
        <source>Choose the video file you want to analyze. Use Browse to pick a file from disk.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="158"/>
        <source>Video File:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="159"/>
        <source>Click Browse to select a video file...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="165"/>
        <source>Enter the capture device index (0, 1, 2, ...) for your HDMI input.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="167"/>
        <source>Device Index:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="168"/>
        <source>0</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="174"/>
        <source>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="176"/>
        <source>Stream URL:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="177"/>
        <source>rtmp://server:port/app/streamKey</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="190"/>
        <source>OpenCV not available; enter index manually.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="203"/>
        <source>Device {index}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="212"/>
        <source>No capture devices found.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="253"/>
        <source>Select Video File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="256"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamControlWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="706"/>
        <source>Stream Connection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="708"/>
        <source>Configure and connect to video source (file, HDMI capture, or RTMP stream)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="713"/>
        <source>Stream Type:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="715"/>
        <source>File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="716"/>
        <source>HDMI Capture</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="717"/>
        <source>RTMP Stream</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="720"/>
        <source>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="729"/>
        <source>Stream URL/Path:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="736"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="937"/>
        <source>Click to browse for video file...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="740"/>
        <source>Enter or browse for the video source:
• File: Click to browse for video file (MP4, AVI, MOV, etc.)
• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="749"/>
        <source>Select HDMI capture device</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="751"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1081"/>
        <source>Scanning for devices...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="755"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="887"/>
        <source>Browse...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="759"/>
        <source>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="766"/>
        <source>Scan...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="768"/>
        <source>Scan for available HDMI capture devices</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="775"/>
        <source>Connect</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="778"/>
        <source>Connect to the specified video source and begin processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="780"/>
        <source>Disconnect</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="784"/>
        <source>Disconnect from the current video source and stop processing.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="791"/>
        <source>Status: Disconnected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="793"/>
        <source>Current connection status</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="796"/>
        <source>Performance</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="797"/>
        <source>Real-time performance metrics</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="801"/>
        <source>Video: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="802"/>
        <source>Original video resolution</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="803"/>
        <source>Processing: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="805"/>
        <source>Resolution used for detection processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="809"/>
        <source>Video FPS: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="810"/>
        <source>Native frame rate of the video source</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="811"/>
        <source>Proc FPS: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="813"/>
        <source>Actual frames per second being processed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="817"/>
        <source>Time: -- ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="819"/>
        <source>Time in milliseconds to process each frame</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="821"/>
        <source>Latency: -- ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="823"/>
        <source>End-to-end latency from frame capture to display</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="827"/>
        <source>Frames: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="828"/>
        <source>Total number of frames processed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="829"/>
        <source>Detections: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="830"/>
        <source>Number of detections in current frame</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="844"/>
        <source>Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="849"/>
        <source>Start Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="852"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="854"/>
        <source>Stop Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="857"/>
        <source>Stop the current recording and save to file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="864"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1037"/>
        <source>Status: Not Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="867"/>
        <source>Current recording status and output file path</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="871"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1044"/>
        <source>Duration: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="873"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="882"/>
        <source>Save to:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="885"/>
        <source>Directory where video recordings will be saved.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="889"/>
        <source>Choose a folder to store recordings.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="945"/>
        <source>rtmp://server:port/app/stream</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="961"/>
        <source>Invalid Device</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="962"/>
        <source>Please select a valid HDMI capture device.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="972"/>
        <source>Invalid URL</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="973"/>
        <source>Please enter a valid stream URL.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="990"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="997"/>
        <source>Status: {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1025"/>
        <source>Status: Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1029"/>
        <source>Output: {value}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1041"/>
        <source>Duration: {value}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1070"/>
        <source>Select Recording Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1090"/>
        <source>Device {index}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1099"/>
        <source>No capture devices found</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1109"/>
        <source>Error scanning devices: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1136"/>
        <source>Video: {width}x{height}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1143"/>
        <source>Processing: {width}x{height}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1157"/>
        <source>Video FPS: {fps:.1f}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1160"/>
        <source>Proc FPS: {fps:.1f}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1168"/>
        <source>Time: {time:.1f} ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1171"/>
        <source>Latency: {latency:.1f} ms</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1179"/>
        <source>Frames: {count}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1182"/>
        <source>Detections: {count}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1189"/>
        <source>Select Video File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1192"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamGeneralPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamGeneralPage.py" line="55"/>
        <source>Select Recording Folder</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamTargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="85"/>
        <source>House</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamViewerWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="86"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="175"/>
        <source>Live View</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="180"/>
        <source>Gallery</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="221"/>
        <source>Menu</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="222"/>
        <source>Streaming Analysis Wizard</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="223"/>
        <source>Image Analysis</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="224"/>
        <source>Preferences</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="231"/>
        <source>Help</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="232"/>
        <source>Manual</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="233"/>
        <source>Community Forum</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="234"/>
        <source>YouTube Channel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="257"/>
        <source>Start Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="260"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="262"/>
        <source>Stop Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="265"/>
        <source>Stop the current recording and save to file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="272"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1653"/>
        <source>Status: Not Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="275"/>
        <source>Current recording status and output file path</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="279"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1655"/>
        <source>Duration: --</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="281"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="286"/>
        <source>Save to:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="290"/>
        <source>Directory where video recordings will be saved.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="292"/>
        <source>Browse...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="294"/>
        <source>Choose a folder to store recordings.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="345"/>
        <source>Select Recording Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="365"/>
        <source>Algorithm:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="367"/>
        <source>Select which streaming detection algorithm to use</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="373"/>
        <source>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="416"/>
        <source>Gallery Threshold:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="419"/>
        <source>Number of frames a detection must be seen before appearing in the Gallery tab</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="426"/>
        <source> frames</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="429"/>
        <source>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="626"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="645"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="658"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="672"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="686"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="700"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1669"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="627"/>
        <source>Failed to open Streaming Analysis Guide:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="646"/>
        <source>Failed to open Image Analysis:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="659"/>
        <source>Failed to open Preferences:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="673"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="687"/>
        <source>Failed to open Community Forum:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="701"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="803"/>
        <source>Loaded: {algorithm}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="819"/>
        <source>Error loading algorithm: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="823"/>
        <source>Algorithm Load Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1282"/>
        <source>Algorithm switched to {label}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1307"/>
        <source>{state} - {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1308"/>
        <source>Connected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1308"/>
        <source>Disconnected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1318"/>
        <source>✓ Connected: {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1345"/>
        <source>✗ Disconnected: {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1552"/>
        <source>No detections found.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1556"/>
        <source>Detection Results ({count} found):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1568"/>
        <source>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1578"/>
        <source>#{index}: Type({cls})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1583"/>
        <source> Conf({confidence:.2f})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1628"/>
        <source>Recording started: {path}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1635"/>
        <source>Recording stopped</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1649"/>
        <source>Status: Recording to {path}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1667"/>
        <source>✗ Error: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1731"/>
        <source>Live Stream</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1733"/>
        <source>Cannot seek in live stream.

Detection was first seen at frame {frame}.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamingGuide</name>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="14"/>
        <source>Streaming Setup Guide</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="51"/>
        <source>Connect to Your Stream</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="115"/>
        <source>Pre-recorded video file with playback controls</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="122"/>
        <source>File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="161"/>
        <source>Live HDMI capture device (enter device index)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="168"/>
        <source>HDMI</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="204"/>
        <source>Network stream via RTMP URL</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="211"/>
        <source>RTMP</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="254"/>
        <source>File: Use local video files (MP4, MOV, etc.) with timeline controls.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="269"/>
        <source>HDMI: Connect to a live HDMI capture device.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="284"/>
        <source>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="328"/>
        <source>Connection Details</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="347"/>
        <source>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="364"/>
        <source>Stream URL/Path:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="373"/>
        <source>Click Browse to select a file or enter a URL...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="385"/>
        <source>Browse...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="399"/>
        <source>Auto Connect:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="411"/>
        <source>Connect as soon as the guide finishes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="423"/>
        <source>Capture Devices:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="444"/>
        <source>Scan...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="484"/>
        <source>Processing Resolution:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="532"/>
        <source>Image Capture Information</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="554"/>
        <source>What drone/camera was used to capture images?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="584"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="636"/>
        <source>ft</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="641"/>
        <source>m</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="679"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="700"/>
        <source>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="710"/>
        <source>--</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="749"/>
        <source>Search Target Size</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="774"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="805"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="847"/>
        <source>Detection &amp; Processing</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="869"/>
        <source>Are you looking for specific colors?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="914"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="945"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1018"/>
        <source>Reset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1091"/>
        <source>Algorithm Parameters</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1126"/>
        <source>Close</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1138"/>
        <source>Skip this streaming guide next time</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1166"/>
        <source>Back</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1178"/>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="138"/>
        <source>Continue</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="84"/>
        <source>ADIAT Streaming Setup Guide</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="136"/>
        <source>Open Stream Viewer</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>TargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="85"/>
        <source>House</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ThermalAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="29"/>
        <source>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="45"/>
        <source>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="54"/>
        <source>Above or Below Mean</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="59"/>
        <source>Above Mean</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="64"/>
        <source>Below Mean</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="77"/>
        <source>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="81"/>
        <source>Anomaly Threshold:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="88"/>
        <source>Set the anomaly detection threshold in standard deviations.
• Range: 0 to 7 standard deviations
• Default: 4
Defines how different a temperature must be from the mean to be detected:
• Lower values (1-2): Very sensitive, detects subtle temperature differences (more detections)
• Medium values (3-5): Balanced detection (recommended for most cases)
• Higher values (6-7): Only detects extreme temperature differences (fewer detections)
Example: Value of 4 detects pixels 4 standard deviations above/below mean temperature.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="113"/>
        <source>Number of segments to divide each thermal image into for analysis.
Each segment is analyzed independently for local thermal anomalies.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in scenes with temperature gradients.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="122"/>
        <source>Image Segments:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="146"/>
        <source>Select the number of segments to divide each thermal image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The algorithm calculates mean temperature for each segment independently:
• 1 segment: Global temperature analysis (best for uniform scenes)
• More segments: Local temperature analysis (better for varying backgrounds)
Higher segment counts improve detection in scenes with temperature gradients.
Recommended: 4-9 segments for typical thermal drone imagery.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="157"/>
        <source>1</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="162"/>
        <source>2</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="167"/>
        <source>4</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="172"/>
        <source>6</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="177"/>
        <source>9</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="182"/>
        <source>16</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="187"/>
        <source>25</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="192"/>
        <source>36</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="37"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="57"/>
        <source>No</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="72"/>
        <source>Yes</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="105"/>
        <source>What type of anomalies are you looking for?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="122"/>
        <source>Warmer than surroundings</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="134"/>
        <source>Cooler than surroundings</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="146"/>
        <source>Both</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="185"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="198"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ThermalRange</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="14"/>
        <source>Form</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="29"/>
        <source>Minimum temperature threshold for detection in thermal images.
• Range: -30°C to 50°C
• Default: 35°C
Defines the lower bound of the temperature detection range:
• Lower values: INCREASE detections - accepts cooler objects
• Higher values: DECREASE detections - only warmer objects detected
Combined with Maximum Temp to create a detection range (e.g., 35-40°C for human body temperature).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="38"/>
        <source>Minimum Temp (°C)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="50"/>
        <source>Set the minimum temperature for detection in Celsius.
• Range: -30°C to 50°C
• Default: 35°C
Pixels with temperatures at or above this threshold will be detected.
• Lower values: Detect cooler objects (more detections)
• Higher values: Only detect warmer objects (fewer detections)
Note: Temperature displayed in Celsius, converted based on Preferences setting.
Use for finding objects within a specific temperature range (e.g., people 35-40°C).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="94"/>
        <source>Maximum temperature threshold for detection in thermal images.
• Range: -30°C to 93°C
• Default: 40°C
Defines the upper bound of the temperature detection range:
• Lower values: DECREASE detections - only cooler objects detected
• Higher values: INCREASE detections - accepts warmer objects
Combined with Minimum Temp to create a detection range (e.g., 35-40°C for human body temperature).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="103"/>
        <source>Maximum Temp (°C)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="115"/>
        <source>Set the maximum temperature for detection in Celsius.
• Range: -30°C to 93°C
• Default: 40°C
Pixels with temperatures at or below this threshold will be detected.
• Lower values: Only detect cooler objects (fewer detections)
• Higher values: Detect warmer objects (more detections)
Note: Temperature displayed in Celsius, converted based on Preferences setting.
Detection occurs for pixels between minimum and maximum temperatures (inclusive).</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ThermalRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="108"/>
        <source>Minimum Temp ({degree} F)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="114"/>
        <source>Maximum Temp ({degree} F)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ThermalRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRangeWizard.ui" line="34"/>
        <source>What range of temperatures should ADIAT look for?</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>TrackGalleryWidget</name>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="144"/>
        <source>1 detection</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="146"/>
        <source>{count} detections</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>UnifiedMapExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="382"/>
        <source>No Data Selected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="383"/>
        <source>Please select at least one type of data to export.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="408"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="509"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="543"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="577"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="622"/>
        <source>Export Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="409"/>
        <source>An error occurred during export:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="426"/>
        <source>Save Map Export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="428"/>
        <source>KML files (*.kml)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="510"/>
        <source>Failed to export to KML:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="544"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="578"/>
        <source>Failed to export to CalTopo:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="594"/>
        <source>Map export completed successfully!</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="609"/>
        <source>Map export cancelled</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="623"/>
        <source>Map export failed:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>UpscaleDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="187"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="359"/>
        <source>Upscaled View - {level}x</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="229"/>
        <source>Upscale Method:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="264"/>
        <source>Upres Again</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="267"/>
        <source>Upscale the currently visible portion by {factor}x</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="271"/>
        <source>Quit</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="274"/>
        <source>Close this upscale window</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="367"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="379"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="459"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="524"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="556"/>
        <source>Upscale Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="368"/>
        <source>Error during initial upscale: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="380"/>
        <source>Unable to extract visible image portion.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="389"/>
        <source>Maximum Upscale Reached</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="391"/>
        <source>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="405"/>
        <source>Image Too Large</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="407"/>
        <source>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="418"/>
        <source>Image Too Small</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="420"/>
        <source>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="460"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="557"/>
        <source>An error occurred during upscaling:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="479"/>
        <source>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="491"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="752"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="496"/>
        <source>Upscaling (OpenCV EDSR)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="525"/>
        <source>Failed to start upscaling:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="595"/>
        <source>Method Not Available</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="597"/>
        <source>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="751"/>
        <source>Downloading {model_name} model...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>VideoDisplayWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="652"/>
        <source>No Stream Connected</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>VideoParser</name>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="14"/>
        <source>Video Parser</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="45"/>
        <source>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="62"/>
        <source>SRT subtitle file containing GPS telemetry and timestamp data.
Optional: Provides location information for extracted frames.
Without SRT file, frames will have no GPS metadata.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="67"/>
        <source>The SRT file contains timestamped information about the video file.  It is optional, but without it output images won&apos;t include location information.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="70"/>
        <source>SRT File (optional): </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="82"/>
        <source>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="86"/>
        <source>Output Folder:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="98"/>
        <source>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="115"/>
        <source>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="119"/>
        <location filename="../resources/views/images/VideoParser.ui" line="161"/>
        <location filename="../resources/views/images/VideoParser.ui" line="199"/>
        <source>Select</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="129"/>
        <source>folder.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="141"/>
        <source>Select the source video file to parse.
Video will be split into individual frame images.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="145"/>
        <source>Video File:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="157"/>
        <source>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="176"/>
        <source>Path to the optional SRT subtitle file with GPS telemetry data.
SRT files contain timestamp and location information for video frames.
If provided, extracted frames will include GPS metadata (latitude, longitude, altitude).
Can be left empty if location data is not needed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="194"/>
        <source>Browse for optional SRT subtitle file containing GPS telemetry.
SRT files are commonly created by DJI drones and other video recording devices.
Opens a file selection dialog for SRT files.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="218"/>
        <source>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="223"/>
        <source>Time Interval (seconds):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="235"/>
        <source>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="300"/>
        <source>Start extracting frames from the video file.
Requirements:
• Video file must be selected
• Output folder must be selected
• Time interval must be set (default: 5 seconds)
The process will extract frames at the specified interval and save them as images.
If SRT file is provided, GPS metadata will be embedded in the extracted frames.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="319"/>
        <source>Start</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="350"/>
        <source>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="359"/>
        <source> Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="366"/>
        <source>cancel.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="396"/>
        <source>Progress and status output window.
Displays real-time information during frame extraction:
• Current frame being processed
• Frame timestamps and numbers
• GPS coordinates (if SRT file is provided)
• Progress percentage and completion status
• Any errors or warnings encountered
Shows total frames extracted when complete.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="57"/>
        <source>Select a Video File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="72"/>
        <source>Select a SRT file</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="73"/>
        <source>SRT (*.srt)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="90"/>
        <source>Select Directory</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="110"/>
        <source>Please set the video file and output directory.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="115"/>
        <source>--- Starting video processing ---</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="164"/>
        <source>Confirmation</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="165"/>
        <source>Are you sure you want to cancel the video processing in progress?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="201"/>
        <source>--- Video Processing Completed ---</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="203"/>
        <source>{count} images created</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="256"/>
        <source>Error Starting Processing</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>Viewer</name>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="112"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="133"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="886"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1057"/>
        <source>TextLabel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="161"/>
        <source>View keyboard shortcuts and help</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="199"/>
        <source>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="205"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="350"/>
        <source>Show Overlay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="225"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="841"/>
        <source>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="255"/>
        <source>Highlight Pixels of Interest(H)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="277"/>
        <source>Show AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="306"/>
        <source>Map with Image Locations (M)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="322"/>
        <source>North-Oriented View of Image (R)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="338"/>
        <source>Adjust Image (Ctrl+H)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="341"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="369"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="406"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="450"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="487"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="529"/>
        <source>...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="354"/>
        <source>adjustments.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="366"/>
        <source>Measure Distance (Ctrl+M)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="382"/>
        <source>ruler.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="389"/>
        <source>Toggle Magnifying Glass (Middle Mouse)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="419"/>
        <source>magnify.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="433"/>
        <source>Map Export (KML / CalTopo)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="463"/>
        <source>map.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="470"/>
        <source>Generate PDF Report</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="500"/>
        <source>pdf.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="512"/>
        <source>Generate Zip Bundle</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="542"/>
        <source>zip.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="567"/>
        <source>Skip hidden images when navigating.
When enabled, Previous/Next buttons will skip over images marked as hidden.
Use to focus on images that haven&apos;t been reviewed or marked for exclusion.
Keyboard shortcut: H to hide/unhide current image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="573"/>
        <source>Skip Hidden</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="612"/>
        <source>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="619"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="639"/>
        <source>Hide Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="631"/>
        <source>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="667"/>
        <source>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="672"/>
        <source>Jump To:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="697"/>
        <source>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="711"/>
        <source>Previous Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="718"/>
        <source>previous.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="733"/>
        <source>Next Image</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="740"/>
        <source>next.png</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="896"/>
        <source>Filter AOIs by color and pixel area</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="968"/>
        <source>Sort By</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="980"/>
        <source>Sort Areas of Interest (AOIs) in the list.
Choose how to order the detected objects:
• Pixel Area: Sort by size (largest to smallest)
• Distance: Sort by distance from image center or reference point
• Color: Group by similar colors
• Detection Order: Original order from analysis
Sorting helps prioritize review of larger or closer objects.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1068"/>
        <source>Open</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="113"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="133"/>
        <source>Load Results Failed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="135"/>
        <source>Cannot load results without valid image and mask locations.

The viewer will now close.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="151"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1030"/>
        <source>Skip Hidden ({count}) </source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="213"/>
        <source>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="456"/>
        <source>No Dataset</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="457"/>
        <source>No dataset is currently loaded.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="464"/>
        <source>Generate Cache</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="466"/>
        <source>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="479"/>
        <source>Initializing cache generation...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="480"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="485"/>
        <source>Generating Cache</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="522"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="523"/>
        <source>Failed to start cache generation:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="541"/>
        <source>Cache Generated</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="543"/>
        <source>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="574"/>
        <source>Cache Generation Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="576"/>
        <source>An error occurred during cache generation:

{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="744"/>
        <source>AOI Not Visible</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="746"/>
        <source>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="852"/>
        <source>Show Pixels of Interest (H or Ctrl+I)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="860"/>
        <source>Toggle AOI Circles</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1202"/>
        <source>Missing Dependency</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1204"/>
        <source>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1213"/>
        <source>Upscale Error</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1215"/>
        <source>An error occurred while opening the upscale dialog:
{error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1453"/>
        <source>Unknown Reviewer</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1516"/>
        <source>Loading gallery...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ZipExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="133"/>
        <source>Save Zip File</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="135"/>
        <source>Zip files (*.zip)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="166"/>
        <source>No images to export</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="401"/>
        <source>ZIP file created</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="407"/>
        <source>Failed to generate Zip file: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="428"/>
        <source>Error</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>ZipExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="18"/>
        <source>ZIP Export Options</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="26"/>
        <source>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="34"/>
        <source>Export Native data (original files + XML)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="35"/>
        <source>Export Augmented images (viewer overlays + metadata)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="50"/>
        <source>Include images without flagged AOIs</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="53"/>
        <source>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="59"/>
        <source>OK</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="60"/>
        <source>Cancel</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
