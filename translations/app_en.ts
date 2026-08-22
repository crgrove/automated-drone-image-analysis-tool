<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
<context>
    <name>AIPersonDetector</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="27"/>
        <source>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</source>
        <translation>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="31"/>
        <source>Confidence Threshold</source>
        <translation>Confidence Threshold</translation>
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
        <translation>Adjust the confidence threshold for person detection.
• Range: 0% to 100% (slider -1 to 100, -1 displays as 0%)
• Default: 50%
The AI model assigns a confidence score to each person detection:
• Lower values (0-30%): Accept low-confidence detections (more detections, more false positives)
• Medium values (31-60%): Balanced detection (recommended for most cases)
• Higher values (61-100%): Only accept high-confidence detections (fewer detections, fewer false positives)
Confidence represents the AI model&apos;s certainty that a detected object is a person.
Start with 50% and adjust based on your accuracy requirements.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="81"/>
        <source>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</source>
        <translation>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="86"/>
        <source>50</source>
        <translation>50</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="100"/>
        <source>GPU status and availability information.
Shows whether GPU acceleration is available for AI person detection.
• GPU Available: AI detection will use GPU for faster processing
• CPU Only: AI detection will use CPU (slower but still functional)
GPU acceleration significantly improves processing speed for AI models.</source>
        <translation>GPU status and availability information.
Shows whether GPU acceleration is available for AI person detection.
• GPU Available: AI detection will use GPU for faster processing
• CPU Only: AI detection will use CPU (slower but still functional)
GPU acceleration significantly improves processing speed for AI models.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="107"/>
        <source>GPU Label</source>
        <translation>GPU Label</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="54"/>
        <source>Person Detection</source>
        <translation>Person Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="55"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Processing</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="56"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="57"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Cleanup</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="78"/>
        <source>Model</source>
        <translation>Model</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="80"/>
        <source>Force CPU (disable DirectML)</source>
        <translation>Force CPU (disable DirectML)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="81"/>
        <source>Use 1024 model (higher quality, slower)</source>
        <translation>Use 1024 model (higher quality, slower)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="86"/>
        <source>Detection</source>
        <translation>Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="91"/>
        <source>Confidence Threshold:</source>
        <translation>Confidence Threshold:</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="81"/>
        <source>GPU Not Available</source>
        <translation>GPU Not Available</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="87"/>
        <source>GPU Available</source>
        <translation>GPU Available</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="91"/>
        <source>FPS: {fps} | Processing: {ms}ms</source>
        <translation>FPS: {fps} | Processing: {ms}ms</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="96"/>
        <source>{status} | Tile fallback active</source>
        <translation>{status} | Tile fallback active</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizard</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="40"/>
        <source>How confident should ADIAT be before marking something as a person?</source>
        <translation>How confident should ADIAT be before marking something as a person?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="56"/>
        <source>Note: A higher setting may increase false positives.</source>
        <translation>Note: A higher setting may increase false positives.</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizardController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="33"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="52"/>
        <source>Very 
Confident</source>
        <translation>Very
Confident</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="34"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="53"/>
        <source>Confident</source>
        <translation>Confident</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="35"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="54"/>
        <source>Balanced</source>
        <translation>Balanced</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="36"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="55"/>
        <source>Permissive</source>
        <translation>Permissive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="37"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="56"/>
        <source>Very 
Permissive</source>
        <translation>Very
Permissive</translation>
    </message>
</context>
<context>
    <name>AOICommentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="27"/>
        <source>AOI Comment</source>
        <translation>AOI Comment</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="37"/>
        <source>Add a comment for this flagged AOI (max 256 characters):</source>
        <translation>Add a comment for this flagged AOI (max 256 characters):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="44"/>
        <source>Enter your comment here...</source>
        <translation>Enter your comment here...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="57"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="59"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>AOIController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="381"/>
        <source>No AOI #{number} in this analysis.</source>
        <translation>No AOI #{number} in this analysis.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="394"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="404"/>
        <source>AOI #{number} is hidden by the current filter.</source>
        <translation>AOI #{number} is hidden by the current filter.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="700"/>
        <source>Comment saved</source>
        <translation>Comment saved</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="702"/>
        <source>Comment cleared</source>
        <translation>Comment cleared</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="791"/>
        <source>Copy Data</source>
        <translation>Copy Data</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="797"/>
        <source>Find Similar AOIs</source>
        <translation>Find Similar AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="900"/>
        <source>AOI data copied</source>
        <translation>AOI data copied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="987"/>
        <source>Invalid image index</source>
        <translation>Invalid image index</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="992"/>
        <source>Invalid AOI index</source>
        <translation>Invalid AOI index</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1061"/>
        <source>Could not calculate AOI location. Diagnostic info copied to clipboard!</source>
        <translation>Could not calculate AOI location. Diagnostic info copied to clipboard!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1067"/>
        <source>Could not calculate AOI location</source>
        <translation>Could not calculate AOI location</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1088"/>
        <source>Terrain elevation: {value}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1091"/>
        <source>Terrain-corrected</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1097"/>
        <source> (~{value} resolution)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1102"/>
        <source>Flat terrain assumed</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1538"/>
        <source>Temperature sorting unavailable (no thermal data)</source>
        <translation>Temperature sorting unavailable (no thermal data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1890"/>
        <source>Cannot Delete AOI</source>
        <translation>Cannot Delete AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1892"/>
        <source>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</source>
        <translation>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1901"/>
        <source>Delete AOI</source>
        <translation>Delete AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1903"/>
        <source>Are you sure you want to delete this AOI? This action cannot be undone.</source>
        <translation>Are you sure you want to delete this AOI? This action cannot be undone.</translation>
    </message>
</context>
<context>
    <name>AOICreationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="23"/>
        <source>Create AOI</source>
        <translation>Create AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="31"/>
        <source>Create AOI?</source>
        <translation>Create AOI?</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="39"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="43"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>AOIFilterDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="74"/>
        <source>Filter AOIs</source>
        <translation>Filter AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="91"/>
        <source>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</source>
        <translation>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="96"/>
        <source>Flagged AOIs</source>
        <translation>Flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="99"/>
        <source>Show Only Flagged AOIs</source>
        <translation>Show Only Flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="103"/>
        <source>Only AOIs marked with a flag will be displayed</source>
        <translation>Only AOIs marked with a flag will be displayed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="111"/>
        <source>Comment Filter</source>
        <translation>Comment Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="115"/>
        <source>Enable Comment Filter</source>
        <translation>Enable Comment Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="122"/>
        <source>Pattern:</source>
        <translation>Pattern:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="125"/>
        <source>e.g., damage or crack</source>
        <translation>e.g., damage or crack</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="133"/>
        <source>Case-insensitive substring match (e.g. &quot;blue&quot; matches &quot;blueface&quot;)</source>
        <translation>Case-insensitive substring match (e.g. &quot;blue&quot; matches &quot;blueface&quot;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="137"/>
        <source>Only AOIs with non-empty comments matching the pattern will be shown</source>
        <translation>Only AOIs with non-empty comments matching the pattern will be shown</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="145"/>
        <source>Color Filter</source>
        <translation>Color Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="149"/>
        <source>Enable Color Filter</source>
        <translation>Enable Color Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="156"/>
        <source>Show Only This Color</source>
        <translation>Show Only This Color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="157"/>
        <source>Exclude This Color</source>
        <translation>Exclude This Color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="174"/>
        <source>Target Hue:</source>
        <translation>Target Hue:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="176"/>
        <source>Select Color</source>
        <translation>Select Color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="188"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="556"/>
        <source>No color selected</source>
        <translation>No color selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="196"/>
        <source>Hue Range (±):</source>
        <translation>Hue Range (±):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="214"/>
        <source>AOIs with hue within ±range of target will be shown</source>
        <translation>AOIs with hue within ±range of target will be shown</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="222"/>
        <source>Pixel Area Filter</source>
        <translation>Pixel Area Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="226"/>
        <source>Enable Pixel Area Filter</source>
        <translation>Enable Pixel Area Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="233"/>
        <source>Minimum Area (px):</source>
        <translation>Minimum Area (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="247"/>
        <source>Maximum Area (px):</source>
        <translation>Maximum Area (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="263"/>
        <source>Temperature Filter</source>
        <translation>Temperature Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="267"/>
        <source>Enable Temperature Filter</source>
        <translation>Enable Temperature Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="321"/>
        <source>Temperature filtering unavailable (no thermal data)</source>
        <translation>Temperature filtering unavailable (no thermal data)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="336"/>
        <source>Spatial Filters</source>
        <translation>Spatial Filters</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="341"/>
        <source>Detection Density Heatmap</source>
        <translation>Detection Density Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="347"/>
        <source>Off</source>
        <translation>Off</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="348"/>
        <source>Filter Hot Zones</source>
        <translation>Filter Hot Zones</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="349"/>
        <source>Show Hot Zones Only</source>
        <translation>Show Hot Zones Only</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="374"/>
        <source>Threshold:</source>
        <translation>Threshold:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="392"/>
        <source>View Heatmap</source>
        <translation>View Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="405"/>
        <source>Heatmap filtering unavailable (image dimensions not in dataset)</source>
        <translation>Heatmap filtering unavailable (image dimensions not in dataset)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="418"/>
        <source>Image Mask Filter</source>
        <translation>Image Mask Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="422"/>
        <source>Enable Image Mask Filter</source>
        <translation>Enable Image Mask Filter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="429"/>
        <source>Show Only Detections in Mask</source>
        <translation>Show Only Detections in Mask</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="430"/>
        <source>Exclude Detections in Mask</source>
        <translation>Exclude Detections in Mask</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="449"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="630"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="690"/>
        <source>No mask image selected</source>
        <translation>No mask image selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="454"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="458"/>
        <source>Clear</source>
        <translation>Clear</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="465"/>
        <source>White regions = areas of interest. Mask is scaled to each image&apos;s dimensions.</source>
        <translation>White regions = areas of interest. Mask is scaled to each image&apos;s dimensions.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="483"/>
        <source>Clear All Filters</source>
        <translation>Clear All Filters</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="489"/>
        <source>Apply</source>
        <translation>Apply</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="494"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="531"/>
        <source>Select Target Hue</source>
        <translation>Select Target Hue</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="607"/>
        <source>Select Mask Image</source>
        <translation>Select Mask Image</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="609"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)</source>
        <translation>Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="618"/>
        <source>Invalid Image</source>
        <translation>Invalid Image</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="619"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Could not load the selected image. Please choose a valid image file.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="637"/>
        <source>AOIs in high-density zones (above threshold) will be hidden</source>
        <translation>AOIs in high-density zones (above threshold) will be hidden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="640"/>
        <source>Only AOIs in high-density zones (above threshold) will be shown</source>
        <translation>Only AOIs in high-density zones (above threshold) will be shown</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="643"/>
        <source>Heatmap spatial filtering is disabled</source>
        <translation>Heatmap spatial filtering is disabled</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="649"/>
        <source>Heatmap</source>
        <translation>Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="650"/>
        <source>No heatmap data available. Ensure image dimensions are present in the dataset.</source>
        <translation>No heatmap data available. Ensure image dimensions are present in the dataset.</translation>
    </message>
</context>
<context>
    <name>AOINeighborGalleryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="341"/>
        <source>AOI in Neighboring Images</source>
        <translation>AOI in Neighboring Images</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="414"/>
        <source>Reset View</source>
        <translation>Reset View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="417"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Reset zoom and fit all thumbnails in view</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="424"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="380"/>
        <source>Showing the {count} nearest images containing this AOI; there are more. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to navigate to that image.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="385"/>
        <source>Found AOI in {count} image(s). Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to navigate to that image.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>AOINeighborTrackingController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="192"/>
        <source>No AOI Selected</source>
        <translation>No AOI Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="193"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Please select an AOI first by clicking on it in the thumbnail panel.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="404"/>
        <source>Cannot Calculate GPS</source>
        <translation>Cannot Calculate GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="406"/>
        <source>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</source>
        <translation>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="225"/>
        <source>Searching for AOI in neighboring images...</source>
        <translation>Searching for AOI in neighboring images...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="226"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="230"/>
        <source>Tracking AOI</source>
        <translation>Tracking AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="297"/>
        <source>Tracking Error</source>
        <translation>Tracking Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="298"/>
        <source>An error occurred while tracking the AOI:
{error}</source>
        <translation>An error occurred while tracking the AOI:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="436"/>
        <source>No Neighbors Found</source>
        <translation>No Neighbors Found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="437"/>
        <source>The AOI was not found in any neighboring images.</source>
        <translation>The AOI was not found in any neighboring images.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="467"/>
        <source>Search Error</source>
        <translation>Search Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="468"/>
        <source>An error occurred during the search:
{error}</source>
        <translation>An error occurred during the search:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="584"/>
        <source> (no detections)</source>
        <translation> (no detections)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="599"/>
        <source>Display Error</source>
        <translation>Display Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="600"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>An error occurred while displaying results:
{error}</translation>
    </message>
</context>
<context>
    <name>AOISimilarityController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="141"/>
        <source>No AOI Selected</source>
        <translation>No AOI Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="142"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Please select an AOI first by clicking on it in the thumbnail panel.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="159"/>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="311"/>
        <source>Similarity Search Error</source>
        <translation>Similarity Search Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="160"/>
        <source>An error occurred while starting the similarity search:
{error}</source>
        <translation>An error occurred while starting the similarity search:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="171"/>
        <source>Analyzing AOIs for visual similarity...</source>
        <translation>Analyzing AOIs for visual similarity...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="172"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="176"/>
        <source>Find Similar AOIs</source>
        <translation>Find Similar AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="233"/>
        <source>Analyzing AOI {done} of {total}...</source>
        <translation>Analyzing AOI {done} of {total}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="278"/>
        <source>No Similar AOIs</source>
        <translation>No Similar AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="279"/>
        <source>No other AOIs could be analyzed for similarity.</source>
        <translation>No other AOIs could be analyzed for similarity.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="312"/>
        <source>The similarity search could not be completed:
{error}</source>
        <translation>The similarity search could not be completed:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="418"/>
        <source>Display Error</source>
        <translation>Display Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="419"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>An error occurred while displaying results:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="471"/>
        <source>Flagged {count} AOI(s)</source>
        <translation>Flagged {count} AOI(s)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="474"/>
        <source>Removed flag from {count} AOI(s)</source>
        <translation>Removed flag from {count} AOI(s)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="506"/>
        <source>Comment saved on {count} AOI(s)</source>
        <translation>Comment saved on {count} AOI(s)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="509"/>
        <source>Comment cleared on {count} AOI(s)</source>
        <translation>Comment cleared on {count} AOI(s)</translation>
    </message>
</context>
<context>
    <name>AOISimilarityResultsDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="442"/>
        <source>Similar AOIs</source>
        <translation>Similar AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="479"/>
        <source>Top {shown} of {total} AOIs ranked by similarity to {reference}. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to jump to that AOI.</source>
        <translation>Top {shown} of {total} AOIs ranked by similarity to {reference}. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to jump to that AOI.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="500"/>
        <source>Select All</source>
        <translation>Select All</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="504"/>
        <source>Clear Selection</source>
        <translation>Clear Selection</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="508"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="556"/>
        <source>{count} selected</source>
        <translation>{count} selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="514"/>
        <source>Flag</source>
        <translation>Flag</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="515"/>
        <source>Flag all checked AOIs</source>
        <translation>Flag all checked AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="520"/>
        <source>Unflag</source>
        <translation>Unflag</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="521"/>
        <source>Remove the flag from all checked AOIs</source>
        <translation>Remove the flag from all checked AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="526"/>
        <source>Comment...</source>
        <translation>Comment...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="527"/>
        <source>Add or edit the comment on all checked AOIs</source>
        <translation>Add or edit the comment on all checked AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="538"/>
        <source>Reset View</source>
        <translation>Reset View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="541"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Reset zoom and fit all thumbnails in view</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="546"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="581"/>
        <source>AOI #{number}</source>
        <translation>AOI #{number}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="582"/>
        <source>the selected AOI</source>
        <translation>the selected AOI</translation>
    </message>
</context>
<context>
    <name>AOIUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="250"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="346"/>
        <source>AOI Information
Right-click to copy data to clipboard</source>
        <translation>AOI Information
Right-click to copy data to clipboard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="256"/>
        <source>

Score Type: {type}
Raw Score: {score} ({method})</source>
        <translation>

Score Type: {type}
Raw Score: {score} ({method})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="320"/>
        <source>Confidence Score: {score:.1f}%</source>
        <translation>Confidence Score: {score:.1f}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Unflag AOI</source>
        <translation>Unflag AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Flag AOI</source>
        <translation>Flag AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="403"/>
        <source>Comment:
{comment}

Click to edit comment</source>
        <translation>Comment:
{comment}

Click to edit comment</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="411"/>
        <source>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</source>
        <translation>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="428"/>
        <source>Calculate and show GPS location for this AOI</source>
        <translation>Calculate and show GPS location for this AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="446"/>
        <source>Delete this AOI</source>
        <translation>Delete this AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Area</source>
        <translation>Area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Areas</source>
        <translation>Areas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="486"/>
        <source>{filtered} of {total} {label}</source>
        <translation>{filtered} of {total} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="495"/>
        <source>Area of Interest</source>
        <translation>Area of Interest</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="497"/>
        <source>Areas of Interest</source>
        <translation>Areas of Interest</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="500"/>
        <source>{count} {label}</source>
        <translation>{count} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="643"/>
        <source>Loading AOIs...</source>
        <translation>Loading AOIs...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="684"/>
        <source>Loading AOIs... ({current}/{total})</source>
        <translation>Loading AOIs... ({current}/{total})</translation>
    </message>
</context>
<context>
    <name>AlertManager</name>
    <message>
        <location filename="../app/core/services/AlertService.py" line="294"/>
        <source>ADIAT - Color Detection Alerts</source>
        <translation>ADIAT - Color Detection Alerts</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="569"/>
        <source>ADIAT - Color Detection Alert</source>
        <translation>ADIAT - Color Detection Alert</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="610"/>
        <source>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</source>
        <translation>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="620"/>
        <source>
Details:
</source>
        <translation>
Details:
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="624"/>
        <source>  #{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}
</source>
        <translation>  #{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="644"/>
        <source>ADIAT - Detection Alert</source>
        <translation>ADIAT - Detection Alert</translation>
    </message>
</context>
<context>
    <name>AlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmParametersPage.py" line="165"/>
        <source>{algorithm} Algorithm Settings</source>
        <translation>{algorithm} Algorithm Settings</translation>
    </message>
</context>
<context>
    <name>AlgorithmSelectionPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="92"/>
        <source>Are you using thermal images?</source>
        <translation>Are you using thermal images?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="156"/>
        <source>Are you looking for anomalies within a specific temperature range?</source>
        <translation>Are you looking for anomalies within a specific temperature range?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="159"/>
        <source>Do you specifically want to detect people?</source>
        <translation>Do you specifically want to detect people?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="168"/>
        <source>Do you want to detect anomalies relative to local surroundings?</source>
        <translation>Do you want to detect anomalies relative to local surroundings?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="185"/>
        <source>Are you trying to find a specific color?</source>
        <translation>Are you trying to find a specific color?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="190"/>
        <source>Do you want to manually adjust the color range?</source>
        <translation>Do you want to manually adjust the color range?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="193"/>
        <source>Do your images contain complex backgrounds or structures?</source>
        <translation>Do your images contain complex backgrounds or structures?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="200"/>
        <source>Do your images include shadows or areas with uneven lighting?</source>
        <translation>Do your images include shadows or areas with uneven lighting?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="226"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Selected Algorithm: {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlignImageController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="46"/>
        <source>No image available to align</source>
        <translation>No image available to align</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="52"/>
        <source>This image has no GPS data and cannot be aligned</source>
        <translation>This image has no GPS data and cannot be aligned</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="84"/>
        <source>Could not save the alignment</source>
        <translation>Could not save the alignment</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="95"/>
        <source>Image alignment saved</source>
        <translation>Image alignment saved</translation>
    </message>
</context>
<context>
    <name>AlignImageDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="53"/>
        <source>This saved alignment looks mirrored - re-place each corner handle on its matching photo corner (coloured squares).</source>
        <translation>This saved alignment looks mirrored - re-place each corner handle on its matching photo corner (coloured squares).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="60"/>
        <source>Align Image</source>
        <translation>Align Image</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="130"/>
        <source>Rotate the drone image to line it up with the map. The small coloured squares mark the photo&apos;s corners - drag each corner handle onto the map where its matching-coloured photo corner belongs. For extra accuracy, add tie points: put the IMAGE end on a feature in the drone photo and the MAP end on the same feature on the map.</source>
        <translation>Rotate the drone image to line it up with the map. The small coloured squares mark the photo&apos;s corners - drag each corner handle onto the map where its matching-coloured photo corner belongs. For extra accuracy, add tie points: put the IMAGE end on a feature in the drone photo and the MAP end on the same feature on the map.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="137"/>
        <source>Rotation:</source>
        <translation>Rotation:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="138"/>
        <source>Map opacity:</source>
        <translation>Map opacity:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="139"/>
        <source>FOV overlay opacity:</source>
        <translation>FOV overlay opacity:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="140"/>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="192"/>
        <source>Show Street Map</source>
        <translation>Show Street Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="141"/>
        <source>Add Tie Point</source>
        <translation>Add Tie Point</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="142"/>
        <source>Reset</source>
        <translation>Reset</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="195"/>
        <source>Show Satellite</source>
        <translation>Show Satellite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="218"/>
        <source>Corners look mirrored</source>
        <translation>Corners look mirrored</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="220"/>
        <source>The four corners appear mirrored - the drone image would map to the ground flipped.

Each corner handle is colour-matched to a corner of the drone photo (the small coloured squares). Make sure every handle sits where its matching photo corner belongs.</source>
        <translation>The four corners appear mirrored - the drone image would map to the ground flipped.

Each corner handle is colour-matched to a corner of the drone photo (the small coloured squares). Make sure every handle sits where its matching photo corner belongs.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="230"/>
        <source>Go Back and Fix</source>
        <translation>Go Back and Fix</translation>
    </message>
</context>
<context>
    <name>AlignImageView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="425"/>
        <source>IMAGE</source>
        <translation>IMAGE</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="427"/>
        <source>MAP</source>
        <translation>MAP</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="672"/>
        <source>Remove Tie Point</source>
        <translation>Remove Tie Point</translation>
    </message>
</context>
<context>
    <name>AltitudeController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>meters</source>
        <translation>meters</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>feet</source>
        <translation>feet</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="109"/>
        <source>Negative Altitude Detected</source>
        <translation>Negative Altitude Detected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="111"/>
        <source>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</source>
        <translation>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="130"/>
        <source>Override Altitude</source>
        <translation>Override Altitude</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="132"/>
        <source>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</source>
        <translation>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="180"/>
        <source>Custom AGL set to {value:.1f} {unit}</source>
        <translation>Custom AGL set to {value:.1f} {unit}</translation>
    </message>
</context>
<context>
    <name>AnalyzeService</name>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="161"/>
        <source>Processing {count} files</source>
        <translation>Processing {count} files</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="205"/>
        <source>Skipping {file} :: File is not an image</source>
        <translation>Skipping {file} :: File is not an image</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="210"/>
        <source>All {count} images queued, processing started...</source>
        <translation>All {count} images queued, processing started...</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="268"/>
        <source>{images} images with {aois} areas of interest identified</source>
        <translation>{images} images with {aois} areas of interest identified</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="274"/>
        <source>Total Processing Time: {seconds} seconds</source>
        <translation>Total Processing Time: {seconds} seconds</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="277"/>
        <source>Total Images Processed: {count}</source>
        <translation>Total Images Processed: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="495"/>
        <source>Unable to process {file} :: {error} ({percent}%)</source>
        <translation>Unable to process {file} :: {error} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="518"/>
        <source>{count} areas of interest identified in {file} ({percent}%)</source>
        <translation>{count} areas of interest identified in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="535"/>
        <source>No areas of interest identified in {file} ({percent}%)</source>
        <translation>No areas of interest identified in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="617"/>
        <source>--- Cancelling Image Processing ---</source>
        <translation>--- Cancelling Image Processing ---</translation>
    </message>
</context>
<context>
    <name>BearingRecoveryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="124"/>
        <source>Missing Bearings Detected</source>
        <translation>Missing Bearings Detected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="132"/>
        <source>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</source>
        <translation>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="150"/>
        <source>📁 Load Track File (KML/GPX/CSV)</source>
        <translation>📁 Load Track File (KML/GPX/CSV)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="156"/>
        <source>🧭 Auto-Calculate from Image GPS</source>
        <translation>🧭 Auto-Calculate from Image GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="174"/>
        <source>Preparing...</source>
        <translation>Preparing...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="190"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="195"/>
        <source>Skip</source>
        <translation>Skip</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="259"/>
        <source>Select Track File</source>
        <translation>Select Track File</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="261"/>
        <source>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</source>
        <translation>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="345"/>
        <source>Bearings set for {count} images ({source})</source>
        <translation>Bearings set for {count} images ({source})</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="350"/>
        <source>, {count} flagged near turns</source>
        <translation>, {count} flagged near turns</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="352"/>
        <source>, {count} hover estimates</source>
        <translation>, {count} hover estimates</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="354"/>
        <source>, {count} time gaps</source>
        <translation>, {count} time gaps</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="361"/>
        <source>Bearing Calculation Complete</source>
        <translation>Bearing Calculation Complete</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="362"/>
        <source>{summary}.</source>
        <translation>{summary}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="389"/>
        <source>Bearing Calculation Failed</source>
        <translation>Bearing Calculation Failed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="391"/>
        <source>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</source>
        <translation>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="411"/>
        <source>Cancelled</source>
        <translation>Cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="422"/>
        <source>Cancelling...</source>
        <translation>Cancelling...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="435"/>
        <source>Bearing Recovery Not Needed</source>
        <translation>Bearing Recovery Not Needed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="437"/>
        <source>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</source>
        <translation>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</translation>
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
        <translation>
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
        </translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="483"/>
        <source>About Bearing Recovery</source>
        <translation>About Bearing Recovery</translation>
    </message>
</context>
<context>
    <name>CacheLocationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="35"/>
        <source>Cache Not Found</source>
        <translation>Cache Not Found</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="47"/>
        <source>Cached Data Not Found</source>
        <translation>Cached Data Not Found</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="56"/>
        <source>The following cached items were not found:
</source>
        <translation>The following cached items were not found:
</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="66"/>
        <source>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</source>
        <translation>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="80"/>
        <source>Locate Cache Folder...</source>
        <translation>Locate Cache Folder...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="85"/>
        <source>Skip (Generate On-Demand)</source>
        <translation>Skip (Generate On-Demand)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="122"/>
        <source>Select ADIAT_Results Folder</source>
        <translation>Select ADIAT_Results Folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="136"/>
        <source>Invalid Cache Folder</source>
        <translation>Invalid Cache Folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="138"/>
        <source>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</source>
        <translation>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</translation>
    </message>
</context>
<context>
    <name>CalTopoAPIMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="42"/>
        <source>Select CalTopo Map</source>
        <translation>Select CalTopo Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="68"/>
        <source>Select a CalTopo map:</source>
        <translation>Select a CalTopo map:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="77"/>
        <source>Search:</source>
        <translation>Search:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="79"/>
        <source>Filter maps by name...</source>
        <translation>Filter maps by name...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="111"/>
        <source>Update Credentials</source>
        <translation>Update Credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="117"/>
        <source>Select Map</source>
        <translation>Select Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="121"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="150"/>
        <source>No account data available.</source>
        <translation>No account data available.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="515"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="540"/>
        <source>Credentials Updated</source>
        <translation>Credentials Updated</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="516"/>
        <source>Credentials have been updated and the map list has been refreshed.</source>
        <translation>Credentials have been updated and the map list has been refreshed.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="521"/>
        <source>Update Failed</source>
        <translation>Update Failed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="523"/>
        <source>Failed to refresh account data with new credentials.

Please check your credentials and try again.</source>
        <translation>Failed to refresh account data with new credentials.

Please check your credentials and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="530"/>
        <source>Update Error</source>
        <translation>Update Error</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="531"/>
        <source>An error occurred while updating credentials:

{error}</source>
        <translation>An error occurred while updating credentials:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="542"/>
        <source>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</source>
        <translation>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="559"/>
        <source>No Map Selected</source>
        <translation>No Map Selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="560"/>
        <source>Please select a map from the list.</source>
        <translation>Please select a map from the list.</translation>
    </message>
</context>
<context>
    <name>CalTopoAuthDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="155"/>
        <source>CalTopo Login &amp; Map Selection</source>
        <translation>CalTopo Login &amp; Map Selection</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="240"/>
        <source>Current map: Not selected</source>
        <translation>Current map: Not selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="244"/>
        <source>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</source>
        <translation>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="258"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="799"/>
        <source>I&apos;m Logged In - Export Data</source>
        <translation>I&apos;m Logged In - Export Data</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="260"/>
        <source>Click this after logging in and navigating to your map</source>
        <translation>Click this after logging in and navigating to your map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="263"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="369"/>
        <source>Initialization Error</source>
        <translation>Initialization Error</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="370"/>
        <source>Failed to initialize CalTopo browser:
{error}</source>
        <translation>Failed to initialize CalTopo browser:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="414"/>
        <source>Failed to Load</source>
        <translation>Failed to Load</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="416"/>
        <source>Failed to load CalTopo. Please check your internet connection and try again.</source>
        <translation>Failed to load CalTopo. Please check your internet connection and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="447"/>
        <source>Current map: {map_id}</source>
        <translation>Current map: {map_id}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="475"/>
        <source>No Map Selected</source>
        <translation>No Map Selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="477"/>
        <source>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</source>
        <translation>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="486"/>
        <source>Browser Not Ready</source>
        <translation>Browser Not Ready</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="487"/>
        <source>The CalTopo browser is still loading. Please wait a moment and try again.</source>
        <translation>The CalTopo browser is still loading. Please wait a moment and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="493"/>
        <source>Starting export...</source>
        <translation>Starting export...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="511"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="762"/>
        <source>Authentication Failed</source>
        <translation>Authentication Failed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="512"/>
        <source>Browser not initialized. Please try again.</source>
        <translation>Browser not initialized. Please try again.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="764"/>
        <source>Could not read your CalTopo session.

Make sure you are signed in to CalTopo in this window and have opened your map, then click &apos;I&apos;m Logged In - Export Data&apos; again.</source>
        <translation>Could not read your CalTopo session.

Make sure you are signed in to CalTopo in this window and have opened your map, then click &apos;I&apos;m Logged In - Export Data&apos; again.</translation>
    </message>
</context>
<context>
    <name>CalTopoCredentialDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="33"/>
        <source>CalTopo API Credentials</source>
        <translation>CalTopo API Credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="54"/>
        <source>Enter new credential secret...</source>
        <translation>Enter new credential secret...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="76"/>
        <source>CalTopo Team API Credentials</source>
        <translation>CalTopo Team API Credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="85"/>
        <source>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</source>
        <translation>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="97"/>
        <source>How to get your API credentials</source>
        <translation>How to get your API credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="101"/>
        <source>Opens CalTopo API documentation in your browser</source>
        <translation>Opens CalTopo API documentation in your browser</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="107"/>
        <source>Change credentials</source>
        <translation>Change credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="114"/>
        <source>Team ID:</source>
        <translation>Team ID:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="116"/>
        <source>6-digit alphanumeric Team ID</source>
        <translation>6-digit alphanumeric Team ID</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="123"/>
        <source>Credential ID:</source>
        <translation>Credential ID:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="125"/>
        <source>Credential ID</source>
        <translation>Credential ID</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="132"/>
        <source>Credential Secret:</source>
        <translation>Credential Secret:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="134"/>
        <source>Credential Secret (will be encrypted)</source>
        <translation>Credential Secret (will be encrypted)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="146"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="344"/>
        <source>Test Credentials</source>
        <translation>Test Credentials</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="148"/>
        <source>Test the credentials by calling the CalTopo API</source>
        <translation>Test the credentials by calling the CalTopo API</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="150"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="204"/>
        <source>Enter credential secret...</source>
        <translation>Enter credential secret...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="286"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="294"/>
        <source>Invalid Input</source>
        <translation>Invalid Input</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="286"/>
        <source>Please enter a Team ID.</source>
        <translation>Please enter a Team ID.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <source>Please enter a Credential ID.</source>
        <translation>Please enter a Credential ID.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="294"/>
        <source>Please enter a Credential Secret.</source>
        <translation>Please enter a Credential Secret.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="261"/>
        <source>Invalid Credential Secret</source>
        <translation>Invalid Credential Secret</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="263"/>
        <source>The Credential Secret cannot be used to sign a CalTopo request.

Copy it exactly as shown on the CalTopo Team Admin page under Service Accounts - it is a long base64 string, not the Credential ID or the Team ID.

Details: {error}</source>
        <translation>The Credential Secret cannot be used to sign a CalTopo request.

Copy it exactly as shown on the CalTopo Team Admin page under Service Accounts - it is a long base64 string, not the Credential ID or the Team ID.

Details: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="302"/>
        <source>Testing...</source>
        <translation>Testing...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="317"/>
        <source>Credentials Valid</source>
        <translation>Credentials Valid</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="318"/>
        <source>The credentials are valid and successfully authenticated with CalTopo API.</source>
        <translation>The credentials are valid and successfully authenticated with CalTopo API.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="323"/>
        <source>Credentials Invalid</source>
        <translation>Credentials Invalid</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="325"/>
        <source>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</source>
        <translation>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="336"/>
        <source>Test Error</source>
        <translation>Test Error</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="337"/>
        <source>An error occurred while testing credentials:

{error}</source>
        <translation>An error occurred while testing credentials:

{error}</translation>
    </message>
</context>
<context>
    <name>CalTopoExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="488"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1298"/>
        <source>Offline Mode Enabled</source>
        <translation>Offline Mode Enabled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="490"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1300"/>
        <source>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</source>
        <translation>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="501"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1311"/>
        <source>Nothing Selected</source>
        <translation>Nothing Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="503"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1313"/>
        <source>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</source>
        <translation>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="511"/>
        <source>Preparing Export Data</source>
        <translation>Preparing Export Data</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="514"/>
        <source>Preparing data for export...</source>
        <translation>Preparing data for export...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="515"/>
        <source>Processing images and AOIs...</source>
        <translation>Processing images and AOIs...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="560"/>
        <source>Preparation Error</source>
        <translation>Preparation Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="562"/>
        <source>An error occurred while preparing export data:

{error}</source>
        <translation>An error occurred while preparing export data:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="571"/>
        <source>flagged AOIs</source>
        <translation>flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="573"/>
        <source>image locations</source>
        <translation>image locations</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="575"/>
        <source>coverage area</source>
        <translation>coverage area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="579"/>
        <source>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</source>
        <translation>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="585"/>
        <source>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</source>
        <translation>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="593"/>
        <source>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</source>
        <translation>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="608"/>
        <source>No {types} are available to export.</source>
        <translation>No {types} are available to export.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="613"/>
        <source>Nothing to Export</source>
        <translation>Nothing to Export</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="638"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="681"/>
        <source>No Map Selected</source>
        <translation>No Map Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="640"/>
        <source>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</source>
        <translation>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="683"/>
        <source>No CalTopo map was selected, so there was nothing to export to.

Open your map in the CalTopo window before clicking &apos;I&apos;m Logged In - Export Data&apos;.</source>
        <translation>No CalTopo map was selected, so there was nothing to export to.

Open your map in the CalTopo window before clicking &apos;I&apos;m Logged In - Export Data&apos;.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1613"/>
        <source>Nothing could be exported to CalTopo.

The reason was written to the log (adiat_logs.txt) and the console.</source>
        <translation>Nothing could be exported to CalTopo.

The reason was written to the log (adiat_logs.txt) and the console.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1622"/>
        <source>Photos uploaded: {uploaded} of {total}.</source>
        <translation>Photos uploaded: {uploaded} of {total}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1630"/>
        <source>Successfully exported all {total} item(s) to CalTopo.

The items should now be visible on your map.</source>
        <translation>Successfully exported all {total} item(s) to CalTopo.

The items should now be visible on your map.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1639"/>
        <source>Exported {created} of {total} item(s) to CalTopo.{photos}

Details for anything that failed were written to the log (adiat_logs.txt) and the console.</source>
        <translation>Exported {created} of {total} item(s) to CalTopo.{photos}

Details for anything that failed were written to the log (adiat_logs.txt) and the console.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1628"/>
        <source>Export Successful</source>
        <translation>Export Successful</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1637"/>
        <source>Partial Success</source>
        <translation>Partial Success</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1611"/>
        <source>Export Failed</source>
        <translation>Export Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="719"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1378"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1573"/>
        <source>Export Error</source>
        <translation>Export Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="721"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1575"/>
        <source>An error occurred during CalTopo export:

{error}</source>
        <translation>An error occurred during CalTopo export:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1055"/>
        <source>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</source>
        <translation>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1535"/>
        <source>Exporting to CalTopo</source>
        <translation>Exporting to CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1266"/>
        <source>Logged Out</source>
        <translation>Logged Out</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="598"/>
        <source>No coverage area polygons could be calculated.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The images are not nadir (gimbal pitch must be between -85° and -95°;
  WALDO images: boresight within 40° of nadir)
• GSD (ground sample distance) could not be calculated

Please ensure your images have GPS coordinates and are near-nadir shots.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1267"/>
        <source>Successfully logged out from CalTopo.</source>
        <translation>Successfully logged out from CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1426"/>
        <source>Loading CalTopo Maps</source>
        <translation>Loading CalTopo Maps</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1429"/>
        <source>Connecting to CalTopo...</source>
        <translation>Connecting to CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1430"/>
        <source>Fetching account data and maps...</source>
        <translation>Fetching account data and maps...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1485"/>
        <source>Connection Error</source>
        <translation>Connection Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1487"/>
        <source>An error occurred while connecting to CalTopo API:

{error}</source>
        <translation>An error occurred while connecting to CalTopo API:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="696"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1490"/>
        <source>Authentication Failed</source>
        <translation>Authentication Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="697"/>
        <source>No CalTopo session cookies were captured. Please log in and try again.</source>
        <translation>No CalTopo session cookies were captured. Please log in and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1380"/>
        <source>An error occurred during CalTopo API export:

{error}</source>
        <translation>An error occurred during CalTopo API export:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1492"/>
        <source>CalTopo did not accept these credentials.

The reason was written to the log (adiat_logs.txt) and the console.

Would you like to re-enter your Team ID, Credential ID and Credential Secret?</source>
        <translation>CalTopo did not accept these credentials.

The reason was written to the log (adiat_logs.txt) and the console.

Would you like to re-enter your Team ID, Credential ID and Credential Secret?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1538"/>
        <source>Exporting to CalTopo...</source>
        <translation>Exporting to CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1539"/>
        <source>Preparing data and exporting...</source>
        <translation>Preparing data and exporting...</translation>
    </message>
</context>
<context>
    <name>CalTopoMethodDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="34"/>
        <source>CalTopo Export Method</source>
        <translation>CalTopo Export Method</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="52"/>
        <source>Select CalTopo Export Method</source>
        <translation>Select CalTopo Export Method</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="61"/>
        <source>Choose how you want to authenticate with CalTopo:</source>
        <translation>Choose how you want to authenticate with CalTopo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="68"/>
        <source>Export Method</source>
        <translation>Export Method</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="72"/>
        <source>API (Recommended for CalTopo Team Account)</source>
        <translation>API (Recommended for CalTopo Team Account)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="75"/>
        <source>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</source>
        <translation>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="79"/>
        <source>Browser Login</source>
        <translation>Browser Login</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="81"/>
        <source>Use browser-based authentication.
Log in through an embedded browser window.</source>
        <translation>Use browser-based authentication.
Log in through an embedded browser window.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="96"/>
        <source>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</source>
        <translation>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="109"/>
        <source>Continue</source>
        <translation>Continue</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="113"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>CleanupTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="32"/>
        <source>Temporal Voting</source>
        <translation>Temporal Voting</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="35"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Enable Temporal Voting (reduce flicker)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="38"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="48"/>
        <source>Window Frames (M):</source>
        <translation>Window Frames (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="53"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="61"/>
        <source>Threshold (N of M):</source>
        <translation>Threshold (N of M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="66"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be &lt;= Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be &lt;= Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="78"/>
        <source>Detection Cleanup</source>
        <translation>Detection Cleanup</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="82"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Enable Aspect Ratio Filtering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="85"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="94"/>
        <source>Min Ratio:</source>
        <translation>Min Ratio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="100"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 = reject if height is more than 5x width.</source>
        <translation>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 = reject if height is more than 5x width.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="107"/>
        <source>Max Ratio:</source>
        <translation>Max Ratio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="113"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="122"/>
        <source>Detection Clustering</source>
        <translation>Detection Clustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="125"/>
        <source>Enable Detection Clustering</source>
        <translation>Enable Detection Clustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="128"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="137"/>
        <source>Clustering Distance (px):</source>
        <translation>Clustering Distance (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="142"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</translation>
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
        <translation>RGB: ({r}, {g}, {b})
Click to change color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="71"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="71"/>
        <source>HSV: ({h}, {s}, {v})
Click to change color</source>
        <translation>HSV: ({h}, {s}, {v})
Click to change color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="78"/>
        <source>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="67"/>
        <source>Color Anomaly</source>
        <translation>Color Anomaly</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="68"/>
        <source>Motion Detection</source>
        <translation>Motion Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="69"/>
        <source>Fusion</source>
        <translation>Fusion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="77"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Processing</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="78"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="79"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Cleanup</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="146"/>
        <source>Enable Motion Detection</source>
        <translation>Enable Motion Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="149"/>
        <source>Turn ON to highlight moving objects in the scene.
Most users can leave all other settings at their defaults.
Works best for stationary or slow-moving cameras and can be combined
with Color-Based Anomaly Detection for more robust results.</source>
        <translation>Turn ON to highlight moving objects in the scene.
Most users can leave all other settings at their defaults.
Works best for stationary or slow-moving cameras and can be combined
with Color-Based Anomaly Detection for more robust results.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="162"/>
        <source>Algorithm</source>
        <translation>Algorithm</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="167"/>
        <source>Type:</source>
        <translation>Type:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="169"/>
        <source>FRAME_DIFF</source>
        <translation>FRAME_DIFF</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="170"/>
        <source>MOG2</source>
        <translation>MOG2</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="171"/>
        <source>KNN</source>
        <translation>KNN</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="174"/>
        <source>Motion detection algorithm (advanced setting):

• FRAME_DIFF – Fast and simple; very sensitive to any motion.
• MOG2 – Balanced and adaptive (recommended for most scenes).
• KNN – More robust to noise and complex backgrounds.

If you are unsure, leave this set to MOG2.</source>
        <translation>Motion detection algorithm (advanced setting):

• FRAME_DIFF – Fast and simple; very sensitive to any motion.
• MOG2 – Balanced and adaptive (recommended for most scenes).
• KNN – More robust to noise and complex backgrounds.

If you are unsure, leave this set to MOG2.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="185"/>
        <source>Detection Parameters</source>
        <translation>Detection Parameters</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="191"/>
        <source>Motion Threshold:</source>
        <translation>Motion Threshold:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="196"/>
        <source>Minimum pixel intensity change to consider as motion (1-255).
Lower values = more sensitive, detects subtle motion, more false positives.
Higher values = less sensitive, only strong motion, fewer false positives.
Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.</source>
        <translation>Minimum pixel intensity change to consider as motion (1-255).
Lower values = more sensitive, detects subtle motion, more false positives.
Higher values = less sensitive, only strong motion, fewer false positives.
Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="204"/>
        <source>Blur Kernel (odd):</source>
        <translation>Blur Kernel (odd):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="210"/>
        <source>Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).
Smooths the frame before motion detection to reduce noise.
Larger values = more smoothing, less noise, less detail.
Smaller values = less smoothing, more detail, more noise.
Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.</source>
        <translation>Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).
Smooths the frame before motion detection to reduce noise.
Larger values = more smoothing, less noise, less detail.
Smaller values = less smoothing, more detail, more noise.
Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="219"/>
        <source>Morphology Kernel:</source>
        <translation>Morphology Kernel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="225"/>
        <source>Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).
Removes small noise and fills holes in detections.
Larger values = remove more noise, merge nearby detections.
Smaller values = preserve detail, keep detections separate.
Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.</source>
        <translation>Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).
Removes small noise and fills holes in detections.
Larger values = remove more noise, merge nearby detections.
Smaller values = preserve detail, keep detections separate.
Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="236"/>
        <source>Persistence Filter</source>
        <translation>Persistence Filter</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="241"/>
        <source>Window Frames (M):</source>
        <translation>Window Frames (M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="246"/>
        <source>Size of temporal window for persistence filtering (2-30 frames).
Motion must appear in N out of M consecutive frames to be confirmed.
Larger values = longer memory, more stable, slower response.
Smaller values = shorter memory, faster response, more flicker.
Recommended: 3 for 30fps video (100ms window), 5 for 60fps.</source>
        <translation>Size of temporal window for persistence filtering (2-30 frames).
Motion must appear in N out of M consecutive frames to be confirmed.
Larger values = longer memory, more stable, slower response.
Smaller values = shorter memory, faster response, more flicker.
Recommended: 3 for 30fps video (100ms window), 5 for 60fps.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="254"/>
        <source>Threshold (N of M):</source>
        <translation>Threshold (N of M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="259"/>
        <source>Number of frames within window where motion must appear (N of M).
Higher values = more stringent, filters flickering false positives.
Lower values = more lenient, detects brief/intermittent motion.
Must be ≤ Window Frames.
Recommended: 2 (motion in 2 of last 3 frames).</source>
        <translation>Number of frames within window where motion must appear (N of M).
Higher values = more stringent, filters flickering false positives.
Lower values = more lenient, detects brief/intermittent motion.
Must be ≤ Window Frames.
Recommended: 2 (motion in 2 of last 3 frames).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="270"/>
        <source>Background Subtraction (MOG2/KNN)</source>
        <translation>Background Subtraction (MOG2/KNN)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="275"/>
        <source>History Frames:</source>
        <translation>History Frames:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="280"/>
        <source>Number of frames to learn background model (10-500).
Only applies to MOG2 and KNN algorithms.
Longer history = adapts slower to lighting changes, more stable.
Shorter history = adapts faster, less stable.
Recommended: 50 (~1.7 sec at 30fps) for general use.</source>
        <translation>Number of frames to learn background model (10-500).
Only applies to MOG2 and KNN algorithms.
Longer history = adapts slower to lighting changes, more stable.
Shorter history = adapts faster, less stable.
Recommended: 50 (~1.7 sec at 30fps) for general use.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="288"/>
        <source>Variance Threshold:</source>
        <translation>Variance Threshold:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="293"/>
        <source>Variance threshold for background/foreground classification (1.0-100.0).
Only applies to MOG2 and KNN algorithms.
Lower values = more sensitive, detects subtle changes, more false positives.
Higher values = less sensitive, only strong foreground objects.
Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.</source>
        <translation>Variance threshold for background/foreground classification (1.0-100.0).
Only applies to MOG2 and KNN algorithms.
Lower values = more sensitive, detects subtle changes, more false positives.
Higher values = less sensitive, only strong foreground objects.
Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="301"/>
        <source>Detect Shadows (slower)</source>
        <translation>Detect Shadows (slower)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="303"/>
        <source>Enables shadow detection in MOG2 background subtractor.
Helps distinguish shadows from actual objects (reduces false positives).
Adds ~10-20% processing overhead.
Recommended: ON for outdoor scenes with strong shadows, OFF for speed.</source>
        <translation>Enables shadow detection in MOG2 background subtractor.
Helps distinguish shadows from actual objects (reduces false positives).
Adds ~10-20% processing overhead.
Recommended: ON for outdoor scenes with strong shadows, OFF for speed.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="313"/>
        <source>Object Size Filter</source>
        <translation>Object Size Filter</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="318"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="454"/>
        <source>Min Object Area (px):</source>
        <translation>Min Object Area (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="323"/>
        <source>Minimum detection area in pixels (1-100000).
Filters out very small detections such as noise, insects, or raindrops.
Lower values = detect smaller objects (more noise).
Higher values = only larger objects (less noise).
Recommended: 5-10 for person-sized motion, 50-100 for vehicles.</source>
        <translation>Minimum detection area in pixels (1-100000).
Filters out very small detections such as noise, insects, or raindrops.
Lower values = detect smaller objects (more noise).
Higher values = only larger objects (less noise).
Recommended: 5-10 for person-sized motion, 50-100 for vehicles.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="331"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="467"/>
        <source>Max Object Area (px):</source>
        <translation>Max Object Area (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="336"/>
        <source>Maximum detection area in pixels (10-1000000).
Filters out very large regions such as full-frame lighting changes or giant shadows.
Lower values = only small/medium objects.
Higher values = allow large objects.
Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.</source>
        <translation>Maximum detection area in pixels (10-1000000).
Filters out very large regions such as full-frame lighting changes or giant shadows.
Lower values = only small/medium objects.
Higher values = allow large objects.
Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="347"/>
        <source>Camera Movement Detection</source>
        <translation>Camera Movement Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="350"/>
        <source>Pause on Camera Movement</source>
        <translation>Pause on Camera Movement</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="353"/>
        <source>Automatically pauses motion detection when camera is moving/panning.
Prevents false positives caused by camera movement (entire scene appears to move).
Detects camera movement by measuring percentage of frame with motion.
Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.</source>
        <translation>Automatically pauses motion detection when camera is moving/panning.
Prevents false positives caused by camera movement (entire scene appears to move).
Detects camera movement by measuring percentage of frame with motion.
Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="361"/>
        <source>Threshold:</source>
        <translation>Threshold:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="366"/>
        <source>Percentage of frame with motion to consider as camera movement (1-100%).
If more than this % of pixels show motion, pause detection.
Lower values = detect camera movement sooner (more pauses).
Higher values = tolerate more motion before pausing (fewer pauses).
Recommended: 15% for drone/handheld, 30% for shaky tripod.</source>
        <translation>Percentage of frame with motion to consider as camera movement (1-100%).
If more than this % of pixels show motion, pause detection.
Lower values = detect camera movement sooner (more pauses).
Higher values = tolerate more motion before pausing (fewer pauses).
Recommended: 15% for drone/handheld, 30% for shaky tripod.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="380"/>
        <source>Show Advanced Motion Settings</source>
        <translation>Show Advanced Motion Settings</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="383"/>
        <source>Advanced users can expand this to adjust the motion algorithm
and detailed thresholds (sensitivity, filters, background model).
If you are unsure, leave this unchecked and use the defaults.</source>
        <translation>Advanced users can expand this to adjust the motion algorithm
and detailed thresholds (sensitivity, filters, background model).
If you are unsure, leave this unchecked and use the defaults.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="402"/>
        <source>Enable Color-Based Anomaly Detection</source>
        <translation>Enable Color-Based Anomaly Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="405"/>
        <source>Detects pixels whose colors are statistically rare in the frame.
Conceptually similar to MRMap&apos;s rarity-based detection for images.
Works well for: bright colored clothing, vehicles, equipment in natural scenes.
Can be combined with Motion Detection for more robust detection.</source>
        <translation>Detects pixels whose colors are statistically rare in the frame.
Conceptually similar to MRMap&apos;s rarity-based detection for images.
Works well for: bright colored clothing, vehicles, equipment in natural scenes.
Can be combined with Motion Detection for more robust detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="413"/>
        <source>Color Rarity Settings</source>
        <translation>Color Rarity Settings</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="418"/>
        <source>Color Resolution (bins):</source>
        <translation>Color Resolution (bins):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="424"/>
        <source>Controls how finely colors are grouped into histogram bins (3-8 bits).
Analogous to MRMap&apos;s color binning.
Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.
Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.
Recommended: 4-5 for a balanced number of detections; use lower for very clean results,
and higher only when you need to pull out very subtle color differences.</source>
        <translation>Controls how finely colors are grouped into histogram bins (3-8 bits).
Analogous to MRMap&apos;s color binning.
Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.
Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.
Recommended: 4-5 for a balanced number of detections; use lower for very clean results,
and higher only when you need to pull out very subtle color differences.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="432"/>
        <source>4 bits</source>
        <translation>4 bits</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="436"/>
        <source>Rarity Threshold (% of colors):</source>
        <translation>Rarity Threshold (% of colors):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="442"/>
        <source>Sensitivity threshold for how rare a color must be to be flagged (0-100%).
Computed from the distribution of color-bin counts in the frame, similar in role
to MRMap&apos;s detection threshold.
Lower values (10-20%) = stricter: only very rare colors (fewer detections).
Medium values (25-40%) = balanced (recommended for general use).
Higher values (40-60%) = more sensitive: includes more common colors (more detections).</source>
        <translation>Sensitivity threshold for how rare a color must be to be flagged (0-100%).
Computed from the distribution of color-bin counts in the frame, similar in role
to MRMap&apos;s detection threshold.
Lower values (10-20%) = stricter: only very rare colors (fewer detections).
Medium values (25-40%) = balanced (recommended for general use).
Higher values (40-60%) = more sensitive: includes more common colors (more detections).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="459"/>
        <source>Minimum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s minimum AOI area.
Lower values = detect smaller colored objects (more noise).
Higher values = only larger colored regions (less noise).
Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.</source>
        <translation>Minimum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s minimum AOI area.
Lower values = detect smaller colored objects (more noise).
Higher values = only larger colored regions (less noise).
Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="472"/>
        <source>Maximum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s maximum AOI area.
Lower values = only detect smaller colored objects.
Higher values = allow larger colored regions.
Recommended: 50000 for general use, 10000 for small-object-only searches.</source>
        <translation>Maximum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s maximum AOI area.
Lower values = only detect smaller colored objects.
Higher values = allow larger colored regions.
Recommended: 50000 for general use, 10000 for small-object-only searches.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="480"/>
        <source>Blob Detection Method:</source>
        <translation>Blob Detection Method:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="482"/>
        <source>Find Contours</source>
        <translation>Find Contours</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="483"/>
        <source>Connected Components</source>
        <translation>Connected Components</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="486"/>
        <source>Method for extracting blob regions from the detection mask:

Find Contours: Traditional OpenCV contour detection (default).
  Better for irregular shapes, provides detailed contour outlines.

Connected Components: Uses cv2.connectedComponentsWithStats.
  Provides direct blob statistics in a single pass.</source>
        <translation>Method for extracting blob regions from the detection mask:

Find Contours: Traditional OpenCV contour detection (default).
  Better for irregular shapes, provides detailed contour outlines.

Connected Components: Uses cv2.connectedComponentsWithStats.
  Provides direct blob statistics in a single pass.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="497"/>
        <source>Color Space (Lighting Invariance)</source>
        <translation>Color Space (Lighting Invariance)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="502"/>
        <source>Color Space:</source>
        <translation>Color Space:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="504"/>
        <source>RGB</source>
        <translation>RGB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="505"/>
        <source>HSV</source>
        <translation>HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="506"/>
        <source>LAB</source>
        <translation>LAB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="509"/>
        <source>Color space for histogram-based anomaly detection:

RGB: Uses all 3 color channels. Fast, but sensitive to lighting.
  A red shirt in shadow may not match a red shirt in sunlight.

HSV (Hue-based): Uses only Hue channel - lighting invariant.
  Red stays red regardless of brightness. Good for colored objects.
  Filters out grays/whites where hue is undefined.

LAB (a,b chromaticity): Uses a,b channels - lighting invariant, perceptually uniform.
  No discontinuity at red (unlike HSV). Best for search &amp; rescue.
  Filters out neutral grays where a,b are near zero.</source>
        <translation>Color space for histogram-based anomaly detection:

RGB: Uses all 3 color channels. Fast, but sensitive to lighting.
  A red shirt in shadow may not match a red shirt in sunlight.

HSV (Hue-based): Uses only Hue channel - lighting invariant.
  Red stays red regardless of brightness. Good for colored objects.
  Filters out grays/whites where hue is undefined.

LAB (a,b chromaticity): Uses a,b channels - lighting invariant, perceptually uniform.
  No discontinuity at red (unlike HSV). Best for search &amp; rescue.
  Filters out neutral grays where a,b are near zero.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="522"/>
        <source>HSV Min Saturation:</source>
        <translation>HSV Min Saturation:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="529"/>
        <source>Minimum saturation for HSV mode (0-255).
Pixels below this saturation are ignored (grays, whites, blacks).
These have undefined/noisy hue values.
Lower = include more desaturated colors (may add noise).
Higher = only vivid colors (may miss faded/shadowed objects).
Recommended: 30-50 for general use.</source>
        <translation>Minimum saturation for HSV mode (0-255).
Pixels below this saturation are ignored (grays, whites, blacks).
These have undefined/noisy hue values.
Lower = include more desaturated colors (may add noise).
Higher = only vivid colors (may miss faded/shadowed objects).
Recommended: 30-50 for general use.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="542"/>
        <source>LAB Min Chroma:</source>
        <translation>LAB Min Chroma:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="549"/>
        <source>Minimum chroma (color intensity) for LAB mode (0-128).
Chroma = distance from neutral gray in a,b plane.
Pixels below this are ignored (near-neutral grays).
Lower = include more muted colors.
Higher = only vivid, saturated colors.
Recommended: 10-20 for general use.</source>
        <translation>Minimum chroma (color intensity) for LAB mode (0-128).
Chroma = distance from neutral gray in a,b plane.
Pixels below this are ignored (near-neutral grays).
Lower = include more muted colors.
Higher = only vivid, saturated colors.
Recommended: 10-20 for general use.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="567"/>
        <source>Color Match Expansion</source>
        <translation>Color Match Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="570"/>
        <source>Allow Similar Colors (Hue Expansion)</source>
        <translation>Allow Similar Colors (Hue Expansion)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="573"/>
        <source>Lets the detector treat similar colors as the same object.
For example, a red jacket that looks slightly orange in some frames will still be grouped together.
Turn this OFF if you only care about one very specific color shade.
Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).</source>
        <translation>Lets the detector treat similar colors as the same object.
For example, a red jacket that looks slightly orange in some frames will still be grouped together.
Turn this OFF if you only care about one very specific color shade.
Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="581"/>
        <source>Color Match Range:</source>
        <translation>Color Match Range:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="586"/>
        <source>How wide to stretch the color match around each detected color.
Smaller values = stay very close to the original color (more specific).
Larger values = include a wider range of similar colors (more forgiving).
Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.</source>
        <translation>How wide to stretch the color match around each detected color.
Smaller values = stay very close to the original color (more specific).
Larger values = include a wider range of similar colors (more forgiving).
Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="592"/>
        <source>±5 (~10°)</source>
        <translation>±5 (~10°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="599"/>
        <source>Color Exclusion</source>
        <translation>Color Exclusion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="602"/>
        <source>Enable Color Exclusion</source>
        <translation>Enable Color Exclusion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="605"/>
        <source>Exclude specific background colors from color anomaly detection.
Useful for ignoring dominant scene colors such as grass, sky, or buildings.
Click on the color wheel below to choose colors to ignore.
Selected colors are highlighted with a dark border.</source>
        <translation>Exclude specific background colors from color anomaly detection.
Useful for ignoring dominant scene colors such as grass, sky, or buildings.
Click on the color wheel below to choose colors to ignore.
Selected colors are highlighted with a dark border.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="613"/>
        <source>Click on color wheel to exclude colors (20° steps, 0-360°):</source>
        <translation>Click on color wheel to exclude colors (20° steps, 0-360°):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="618"/>
        <source>Click on any color segment to toggle exclusion on/off.
Segments represent broad color ranges (e.g., blues, greens, reds).
Use this to teach the system which background colors to ignore.</source>
        <translation>Click on any color segment to toggle exclusion on/off.
Segments represent broad color ranges (e.g., blues, greens, reds).
Use this to teach the system which background colors to ignore.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="635"/>
        <source>Detection Fusion</source>
        <translation>Detection Fusion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="638"/>
        <source>Enable Fusion (when both motion and color enabled)</source>
        <translation>Enable Fusion (when both motion and color enabled)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="641"/>
        <source>Combines motion and color detections when both are enabled.
Only active when both Motion and Color detection are ON.
Different modes control how detections are merged.
Recommended: ON for robust multi-modal detection.</source>
        <translation>Combines motion and color detections when both are enabled.
Only active when both Motion and Color detection are ON.
Different modes control how detections are merged.
Recommended: ON for robust multi-modal detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="649"/>
        <source>Fusion Mode:</source>
        <translation>Fusion Mode:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="651"/>
        <source>UNION</source>
        <translation>UNION</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="652"/>
        <source>INTERSECTION</source>
        <translation>INTERSECTION</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="653"/>
        <source>COLOR_PRIORITY</source>
        <translation>COLOR_PRIORITY</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="654"/>
        <source>MOTION_PRIORITY</source>
        <translation>MOTION_PRIORITY</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="657"/>
        <source>How to combine motion and color detections:

• UNION: Show all detections from both (most detections).
  Use for: Maximum coverage, don&apos;t miss anything.

• INTERSECTION: Only show detections found by both (fewest false positives).
  Use for: High confidence, reduce false positives.

• COLOR_PRIORITY: Show color detections + motion detections that match color.
  Use for: Trust color more (e.g., bright colored objects).

• MOTION_PRIORITY: Show motion detections + color detections that match motion.
  Use for: Trust motion more (e.g., moving camouflaged objects).</source>
        <translation>How to combine motion and color detections:

• UNION: Show all detections from both (most detections).
  Use for: Maximum coverage, don&apos;t miss anything.

• INTERSECTION: Only show detections found by both (fewest false positives).
  Use for: High confidence, reduce false positives.

• COLOR_PRIORITY: Show color detections + motion detections that match color.
  Use for: Trust color more (e.g., bright colored objects).

• MOTION_PRIORITY: Show motion detections + color detections that match motion.
  Use for: Trust motion more (e.g., moving camouflaged objects).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="757"/>
        <source>{value} bits</source>
        <translation>{value} bits</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="770"/>
        <source>±{value} (~{degrees}°)</source>
        <translation>±{value} (~{degrees}°)</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionController.py" line="142"/>
        <source>FPS: {fps} | Processing: {time}ms</source>
        <translation>FPS: {fps} | Processing: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="12"/>
        <source>Color Anomaly Detection</source>
        <translation>Color Anomaly Detection</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="16"/>
        <source>Enable Color Anomaly Detection</source>
        <translation>Enable Color Anomaly Detection</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="27"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>How aggressively should ADIAT be searching for anomalies?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="38"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Note: A higher setting will find more potential anomalies but may also increase false positives.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="56"/>
        <source>Motion Detection</source>
        <translation>Motion Detection</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="65"/>
        <source>Do you want to enable motion detection?</source>
        <translation>Do you want to enable motion detection?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="73"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="79"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="48"/>
        <source>Very 
Conservative</source>
        <translation>Very
Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="49"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="50"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="51"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="52"/>
        <source>Very 
Aggressive</source>
        <translation>Very
Aggressive</translation>
    </message>
</context>
<context>
    <name>ColorDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="76"/>
        <source>Color Selection</source>
        <translation>Color Selection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="77"/>
        <source>Detection</source>
        <translation>Detection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="78"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Processing</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="79"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="80"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Cleanup</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="108"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="111"/>
        <source>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</source>
        <translation>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="131"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="134"/>
        <source>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</source>
        <translation>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="157"/>
        <source>No colors configured. Add at least one color to start detection.</source>
        <translation>No colors configured. Add at least one color to start detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="178"/>
        <source>Min Object Area (px):</source>
        <translation>Min Object Area (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="184"/>
        <source>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</source>
        <translation>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="193"/>
        <source>Max Object Area (px):</source>
        <translation>Max Object Area (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="199"/>
        <source>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</source>
        <translation>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="208"/>
        <source>Confidence Threshold:</source>
        <translation>Confidence Threshold:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="215"/>
        <source>Minimum confidence score to accept a detection (0-100%).
Confidence is calculated from:
• Size score: area relative to max area
• Shape score: solidity (how compact/regular the shape is)
• Final: average of both scores

Lower values (0-30%) = accept more detections, including weak/fragmented ones.
Higher values (70-100%) = only high-quality detections, well-formed shapes.
Recommended: 50% for balanced filtering, 30% for more detections, 70% for strict quality.</source>
        <translation>Minimum confidence score to accept a detection (0-100%).
Confidence is calculated from:
• Size score: area relative to max area
• Shape score: solidity (how compact/regular the shape is)
• Final: average of both scores

Lower values (0-30%) = accept more detections, including weak/fragmented ones.
Higher values (70-100%) = only high-quality detections, well-formed shapes.
Recommended: 50% for balanced filtering, 30% for more detections, 70% for strict quality.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="226"/>
        <source>50%</source>
        <translation>50%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="342"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="395"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="430"/>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="665"/>
        <source>Color_{index}</source>
        <translation>Color_{index}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="513"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Color Ranges: {count} colors</translation>
    </message>
</context>
<context>
    <name>ColorDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionController.py" line="134"/>
        <source>FPS: {fps} | Processing: {time}ms</source>
        <translation>FPS: {fps} | Processing: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorDetectionWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="52"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="62"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="244"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Color Ranges: {count} colors</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="329"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="57"/>
        <source>Hue Histogram Unavailable</source>
        <translation>Hue Histogram Unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="59"/>
        <source>No color image data is available for the current image.</source>
        <translation>No color image data is available for the current image.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="14"/>
        <source>Hue Histogram</source>
        <translation>Hue Histogram</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="23"/>
        <source>Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.</source>
        <translation>Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="32"/>
        <source>AOIs Only</source>
        <translation>AOIs Only</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Reset Zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="61"/>
        <source>Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="74"/>
        <source>Visible Hue Range</source>
        <translation>Visible Hue Range</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="64"/>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="174"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="127"/>
        <source>Hover over the histogram to inspect a hue band.</source>
        <translation>Hover over the histogram to inspect a hue band.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="61"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="85"/>
        <source>Minimum: --</source>
        <translation>Minimum: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="62"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="92"/>
        <source>Maximum: --</source>
        <translation>Maximum: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="115"/>
        <source>Reset Range</source>
        <translation>Reset Range</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="30"/>
        <source>No hue histogram data available</source>
        <translation>No hue histogram data available</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="180"/>
        <source>Hover hue: {value}°</source>
        <translation>Hover hue: {value}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="188"/>
        <source>Minimum: {minimum}°</source>
        <translation>Minimum: {minimum}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="193"/>
        <source>Maximum: {maximum}°</source>
        <translation>Maximum: {maximum}°</translation>
    </message>
</context>
<context>
    <name>ColorListDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="30"/>
        <source>Select Color from List</source>
        <translation>Select Color from List</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="42"/>
        <source>Search:</source>
        <translation>Search:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="44"/>
        <source>Filter by name or uses…</source>
        <translation>Filter by name or uses…</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Name</source>
        <translation>Name</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>RGB</source>
        <translation>RGB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <source>HSV</source>
        <translation>HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Uses</source>
        <translation>Uses</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="73"/>
        <source>Use Color</source>
        <translation>Use Color</translation>
    </message>
</context>
<context>
    <name>ColorPickerDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="35"/>
        <source>Select Color from Image</source>
        <translation>Select Color from Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="55"/>
        <source>Use Color</source>
        <translation>Use Color</translation>
    </message>
</context>
<context>
    <name>ColorPickerImageViewer</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <source>Load Image</source>
        <translation>Load Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <source>Color Selector</source>
        <translation>Color Selector</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <source>Select Image</source>
        <translation>Select Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="173"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="230"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="588"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="174"/>
        <source>Could not load image: {path}</source>
        <translation>Could not load image: {path}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <source>Error loading image: {error}</source>
        <translation>Error loading image: {error}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <source>Error setting image: {error}</source>
        <translation>Error setting image: {error}</translation>
    </message>
</context>
<context>
    <name>ColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="42"/>
        <source>Add a new color range to detect. Each color can have its own RGB range tolerances.</source>
        <translation>Add a new color range to detect. Each color can have its own RGB range tolerances.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="45"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="52"/>
        <source>color.png</source>
        <translation>color.png</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="83"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="88"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="95"/>
        <source>eye.png</source>
        <translation>eye.png</translation>
    </message>
</context>
<context>
    <name>ColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="43"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="324"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>ColorRangeDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="39"/>
        <source>HSV Color Range Selection</source>
        <translation>HSV Color Range Selection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="122"/>
        <source>Color Range Selection</source>
        <translation>Color Range Selection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="206"/>
        <source>Preview</source>
        <translation>Preview</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="210"/>
        <source>Original Image</source>
        <translation>Original Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="216"/>
        <source>Original image preview.
Shows the unmodified input image for reference.
Use this to compare with the filtered result below.</source>
        <translation>Original image preview.
Shows the unmodified input image for reference.
Use this to compare with the filtered result below.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="222"/>
        <source>Filtered Result</source>
        <translation>Filtered Result</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="228"/>
        <source>Filtered result preview.
Shows pixels that match your current HSV color range settings.
Updates in real-time as you adjust the color and range values.
Matching pixels are shown, non-matching pixels appear black.</source>
        <translation>Filtered result preview.
Shows pixels that match your current HSV color range settings.
Updates in real-time as you adjust the color and range values.
Matching pixels are shown, non-matching pixels appear black.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="235"/>
        <source>Show mask only</source>
        <translation>Show mask only</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="237"/>
        <source>Toggle between masked color result and grayscale mask.
• Unchecked (default): Shows the original image with matching colors visible
• Checked: Shows a black and white mask where white = matching pixels
Use the mask view to clearly see which pixels are being detected.</source>
        <translation>Toggle between masked color result and grayscale mask.
• Unchecked (default): Shows the original image with matching colors visible
• Checked: Shows a black and white mask where white = matching pixels
Use the mask view to clearly see which pixels are being detected.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="244"/>
        <source>Original:</source>
        <translation>Original:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="246"/>
        <source>Result:</source>
        <translation>Result:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="262"/>
        <source>Pick from Image...</source>
        <translation>Pick from Image...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="268"/>
        <source>Test on Image</source>
        <translation>Test on Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="270"/>
        <source>Test current HSV range settings on the loaded image.
Manually triggers a preview update to see detection results.
Preview updates automatically as you adjust settings.</source>
        <translation>Test current HSV range settings on the loaded image.
Manually triggers a preview update to see detection results.
Preview updates automatically as you adjust settings.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="280"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="282"/>
        <source>Cancel color selection.
Discards all changes and closes the dialog without applying the color range.</source>
        <translation>Cancel color selection.
Discards all changes and closes the dialog without applying the color range.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="287"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="289"/>
        <source>Apply color selection.
Saves the current HSV color range settings and closes the dialog.
The selected color range will be used for image analysis.</source>
        <translation>Apply color selection.
Saves the current HSV color range settings and closes the dialog.
The selected color range will be used for image analysis.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="309"/>
        <source>Custom Colors</source>
        <translation>Custom Colors</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="312"/>
        <source>Standard Dialog...</source>
        <translation>Standard Dialog...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="318"/>
        <source>Add Current</source>
        <translation>Add Current</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="381"/>
        <source>Select Color</source>
        <translation>Select Color</translation>
    </message>
</context>
<context>
    <name>ColorRangeViewer</name>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="14"/>
        <source>Color Range Viewer</source>
        <translation>Color Range Viewer</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="37"/>
        <source>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</source>
        <translation>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="42"/>
        <source>Selected</source>
        <translation>Selected</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="76"/>
        <source>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</source>
        <translation>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="81"/>
        <source>Unselected</source>
        <translation>Unselected</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="69"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="79"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="258"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>ColorSwatchButton</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="596"/>
        <source>RGB: ({r}, {g}, {b})</source>
        <translation>RGB: ({r}, {g}, {b})</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="609"/>
        <source>Empty slot - add a custom color</source>
        <translation>Empty slot - add a custom color</translation>
    </message>
</context>
<context>
    <name>CoordinateController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="122"/>
        <source>GPS Coordinates: {coords}</source>
        <translation>GPS Coordinates: {coords}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="148"/>
        <source>📋 Copy coordinates</source>
        <translation>📋 Copy coordinates</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="152"/>
        <source>🗺️ Open in Google Maps</source>
        <translation>🗺️ Open in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="156"/>
        <source>🌍 View in Google Earth</source>
        <translation>🌍 View in Google Earth</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="160"/>
        <source>📱 Send via WhatsApp</source>
        <translation>📱 Send via WhatsApp</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="164"/>
        <source>📨 Send via Telegram</source>
        <translation>📨 Send via Telegram</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="236"/>
        <source>Coordinates copied</source>
        <translation>Coordinates copied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="246"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="260"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="323"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="343"/>
        <source>Coordinates unavailable</source>
        <translation>Coordinates unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="330"/>
        <source>Coordinate: {lat}, {lon} — {maps}</source>
        <translation>Coordinate: {lat}, {lon} — {maps}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="350"/>
        <source>Coordinates: {lat}, {lon}</source>
        <translation>Coordinates: {lat}, {lon}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="390"/>
        <source>No bearing info available</source>
        <translation>No bearing info available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="412"/>
        <source>North-Oriented View (Rotated {angle:.1f}°)</source>
        <translation>North-Oriented View (Rotated {angle:.1f}°)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="444"/>
        <source>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</source>
        <translation>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="454"/>
        <source>↑ NORTH</source>
        <translation>↑ NORTH</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="463"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="474"/>
        <source>Error: {error}</source>
        <translation>Error: {error}</translation>
    </message>
</context>
<context>
    <name>CoordinatorWindow</name>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="39"/>
        <source>Search Coordinator</source>
        <translation>Search Coordinator</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="58"/>
        <source>Create New Search</source>
        <translation>Create New Search</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="63"/>
        <source>Open Existing Search</source>
        <translation>Open Existing Search</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="68"/>
        <source>Save Search</source>
        <translation>Save Search</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="74"/>
        <source>Add Batches to Search</source>
        <translation>Add Batches to Search</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="78"/>
        <source>Add more batch XML files to the current search project</source>
        <translation>Add more batch XML files to the current search project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="96"/>
        <source>Dashboard</source>
        <translation>Dashboard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="100"/>
        <source>Batch Status</source>
        <translation>Batch Status</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="104"/>
        <source>AOI Analysis</source>
        <translation>AOI Analysis</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="112"/>
        <source>Review Selected Batch</source>
        <translation>Review Selected Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="116"/>
        <source>Open the selected batch&apos;s results in the Viewer to review (same as double-clicking the batch).</source>
        <translation>Open the selected batch&apos;s results in the Viewer to review (same as double-clicking the batch).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="122"/>
        <source>Load Review XML</source>
        <translation>Load Review XML</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="128"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="658"/>
        <source>Export Consolidated Results</source>
        <translation>Export Consolidated Results</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="140"/>
        <source>Project Information</source>
        <translation>Project Information</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="145"/>
        <source>No project loaded</source>
        <translation>No project loaded</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="147"/>
        <source>Project:</source>
        <translation>Project:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="152"/>
        <source>Created by:</source>
        <translation>Created by:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="157"/>
        <source>Date:</source>
        <translation>Date:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="176"/>
        <source>Total Batches</source>
        <translation>Total Batches</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="177"/>
        <source>Total Images</source>
        <translation>Total Images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="178"/>
        <source>Total Reviews</source>
        <translation>Total Reviews</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="179"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="327"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="361"/>
        <source>Reviewers</source>
        <translation>Reviewers</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="189"/>
        <source>Review Progress</source>
        <translation>Review Progress</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="194"/>
        <source>Overall Completion:</source>
        <translation>Overall Completion:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="199"/>
        <source>0%</source>
        <translation>0%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="213"/>
        <source>Not Reviewed</source>
        <translation>Not Reviewed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="222"/>
        <source>In Progress</source>
        <translation>In Progress</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="231"/>
        <source>Complete</source>
        <translation>Complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="239"/>
        <source>AOI Summary</source>
        <translation>AOI Summary</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="247"/>
        <source>Total AOIs</source>
        <translation>Total AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="255"/>
        <source>Flagged AOIs</source>
        <translation>Flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="262"/>
        <source>Active Reviewers</source>
        <translation>Active Reviewers</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="264"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="714"/>
        <source>No reviewers yet</source>
        <translation>No reviewers yet</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="312"/>
        <source>Batch review status and assignments. Load reviewer XMLs to update progress. Double-click a batch to open its results in the Viewer.</source>
        <translation>Batch review status and assignments. Load reviewer XMLs to update progress. Double-click a batch to open its results in the Viewer.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="323"/>
        <source>Batch ID</source>
        <translation>Batch ID</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="324"/>
        <source>Algorithm</source>
        <translation>Algorithm</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="325"/>
        <source>Images</source>
        <translation>Images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="326"/>
        <source>Reviews</source>
        <translation>Reviews</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="328"/>
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="349"/>
        <source>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</source>
        <translation>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="358"/>
        <source>Image</source>
        <translation>Image</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="359"/>
        <source>Location</source>
        <translation>Location</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="360"/>
        <source>Flag Count</source>
        <translation>Flag Count</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="362"/>
        <source>Comments</source>
        <translation>Comments</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="379"/>
        <source>New Search Project</source>
        <translation>New Search Project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="380"/>
        <source>Enter project name:</source>
        <translation>Enter project name:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="389"/>
        <source>Coordinator Information</source>
        <translation>Coordinator Information</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="390"/>
        <source>Enter your name:</source>
        <translation>Enter your name:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="399"/>
        <source>Select Batch Files</source>
        <translation>Select Batch Files</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="400"/>
        <source>Select Initial Batch XML Files</source>
        <translation>Select Initial Batch XML Files</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="403"/>
        <source>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</source>
        <translation>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="417"/>
        <source>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</source>
        <translation>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="419"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="434"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="558"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="605"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="660"/>
        <source>XML Files (*.xml)</source>
        <translation>XML Files (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <source>Save Search Project</source>
        <translation>Save Search Project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="444"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="517"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="577"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="641"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="667"/>
        <source>Success</source>
        <translation>Success</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="445"/>
        <source>Search project &apos;{project}&apos; created successfully!</source>
        <translation>Search project &apos;{project}&apos; created successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="452"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="456"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="492"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="506"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="521"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="647"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="671"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="453"/>
        <source>Failed to save project file.</source>
        <translation>Failed to save project file.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="456"/>
        <source>Failed to create project.</source>
        <translation>Failed to create project.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="462"/>
        <source>Open Search Project</source>
        <translation>Open Search Project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="464"/>
        <source>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</source>
        <translation>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="474"/>
        <source>Project loaded successfully!</source>
        <translation>Project loaded successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="493"/>
        <source>Search project file not found:
{path}</source>
        <translation>Search project file not found:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="507"/>
        <source>Failed to load project file.</source>
        <translation>Failed to load project file.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="518"/>
        <source>Project saved successfully!</source>
        <translation>Project saved successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="521"/>
        <source>Failed to save project.</source>
        <translation>Failed to save project.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="528"/>
        <source>No Project</source>
        <translation>No Project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="529"/>
        <source>Please create or open a project first.</source>
        <translation>Please create or open a project first.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="536"/>
        <source>Add Batches</source>
        <translation>Add Batches</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="537"/>
        <source>Add More Batch XML Files</source>
        <translation>Add More Batch XML Files</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="540"/>
        <source>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</source>
        <translation>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="556"/>
        <source>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</source>
        <translation>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="579"/>
        <source>Successfully added {count} batch(es) to the project!
Total batches: {total}</source>
        <translation>Successfully added {count} batch(es) to the project!
Total batches: {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="589"/>
        <source>No Batches Added</source>
        <translation>No Batches Added</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="591"/>
        <source>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</source>
        <translation>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="603"/>
        <source>Select Reviewer&apos;s ADIAT_Data.xml File</source>
        <translation>Select Reviewer&apos;s ADIAT_Data.xml File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="616"/>
        <source>No Batches</source>
        <translation>No Batches</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="617"/>
        <source>No batches found in project.</source>
        <translation>No batches found in project.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="625"/>
        <source>Select Batch</source>
        <translation>Select Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="626"/>
        <source>Which batch does this review belong to?</source>
        <translation>Which batch does this review belong to?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="642"/>
        <source>Review data loaded and merged successfully!</source>
        <translation>Review data loaded and merged successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="648"/>
        <source>Failed to load review data.</source>
        <translation>Failed to load review data.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="668"/>
        <source>Consolidated results exported to:
{path}</source>
        <translation>Consolidated results exported to:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="671"/>
        <source>Failed to export results.</source>
        <translation>Failed to export results.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="697"/>
        <source>{value}%</source>
        <translation>{value}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="758"/>
        <source>No Batch Selected</source>
        <translation>No Batch Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="759"/>
        <source>Select a batch in the table, then click Review Selected Batch.</source>
        <translation>Select a batch in the table, then click Review Selected Batch.</translation>
    </message>
</context>
<context>
    <name>CoverageExtentExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="129"/>
        <source>Generate Coverage Extent KML</source>
        <translation>Generate Coverage Extent KML</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="131"/>
        <source>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</source>
        <translation>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="145"/>
        <source>Save Coverage Extent KML</source>
        <translation>Save Coverage Extent KML</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="147"/>
        <source>KML files (*.kml)</source>
        <translation>KML files (*.kml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="160"/>
        <source>Generating Coverage Extent KML</source>
        <translation>Generating Coverage Extent KML</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="163"/>
        <source>Calculating coverage extent...</source>
        <translation>Calculating coverage extent...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="209"/>
        <source>Error generating coverage extent KML</source>
        <translation>Error generating coverage extent KML</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="215"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="263"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="216"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="264"/>
        <source>Failed to generate coverage extent KML:
{error}</source>
        <translation>Failed to generate coverage extent KML:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="246"/>
        <source>Coverage extent generation cancelled</source>
        <translation>Coverage extent generation cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="257"/>
        <source>Error generating coverage extent</source>
        <translation>Error generating coverage extent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="270"/>
        <source>No valid images found for coverage extent calculation</source>
        <translation>No valid images found for coverage extent calculation</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="276"/>
        <source>Coverage Extent</source>
        <translation>Coverage Extent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="278"/>
        <source>Could not calculate coverage extent.

Images processed: {processed}
Images skipped: {skipped}

Images may be skipped for the following reasons:
  • Missing GPS data in EXIF
  • No valid GSD (missing altitude/focal length)
  • Gimbal not nadir (must be -85° to -95°;
    WALDO: boresight within 40° of nadir)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="301"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="302"/>
        <source>{value:.2f} acres</source>
        <translation>{value:.2f} acres</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="306"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="307"/>
        <source>{value:.3f} km²</source>
        <translation>{value:.3f} km²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="310"/>
        <source>Coverage extent KML saved: {area}</source>
        <translation>Coverage extent KML saved: {area}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="319"/>
        <source>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</source>
        <translation>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="327"/>
        <source>Coverage Extent KML Generated</source>
        <translation>Coverage Extent KML Generated</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="329"/>
        <source>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</source>
        <translation>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</translation>
    </message>
</context>
<context>
    <name>DetectionRowWidget</name>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="62"/>
        <source>CLASS</source>
        <translation>CLASS</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="74"/>
        <source>--%</source>
        <translation>--%</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="81"/>
        <source>--, --</source>
        <translation>--, --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="88"/>
        <source>--:--:--</source>
        <translation>--:--:--</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="95"/>
        <source>Feed: --</source>
        <translation>Feed: --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="109"/>
        <source>View</source>
        <translation>View</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="112"/>
        <source>Open the full-size thumbnail and metadata.</source>
        <translation>Open the full-size thumbnail and metadata.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="119"/>
        <source>Copy GPS</source>
        <translation>Copy GPS</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="122"/>
        <source>Copy the detection&apos;s coordinates to the clipboard in the operator-preferred format.</source>
        <translation>Copy the detection&apos;s coordinates to the clipboard in the operator-preferred format.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="115"/>
        <source>{name} ({code})</source>
        <translation>{name} ({code})</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="124"/>
        <source>Feed: {feed}</source>
        <translation>Feed: {feed}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="132"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Aircraft serial: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="150"/>
        <source>no
thumb</source>
        <translation>no
thumb</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="156"/>
        <source>bad
thumb</source>
        <translation>bad
thumb</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="224"/>
        <source>Detection</source>
        <translation>Detection</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="283"/>
        <source>No image available.</source>
        <translation>No image available.</translation>
    </message>
</context>
<context>
    <name>DirectoriesPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="55"/>
        <source>Select Input Directory</source>
        <translation>Select Input Directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="72"/>
        <source>Select Output Directory</source>
        <translation>Select Output Directory</translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="65"/>
        <source>Processing...</source>
        <translation>Processing...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="79"/>
        <source>Starting...</source>
        <translation>Starting...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="83"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="135"/>
        <source>Cancelling...</source>
        <translation>Cancelling...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="136"/>
        <source>Cancellation requested...</source>
        <translation>Cancellation requested...</translation>
    </message>
</context>
<context>
    <name>FlightMapView</name>
    <message>
        <location filename="../app/core/views/components/FlightMapView.py" line="550"/>
        <source>QtWebEngine not available — install PySide6-Addons for the interactive map. Showing list view instead.</source>
        <translation type="unfinished">QtWebEngine not available — install PySide6-Addons for the interactive map. Showing list view instead.</translation>
    </message>
</context>
<context>
    <name>FlightPairingDialog</name>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="14"/>
        <source>Add Flight Feed</source>
        <translation>Add Flight Feed</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="27"/>
        <source>Ask the drone operator to read out the 6-character pairing code shown on their controller.</source>
        <translation>Ask the drone operator to read out the 6-character pairing code shown on their controller.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="40"/>
        <source>e.g. K3F7PM</source>
        <translation>e.g. K3F7PM</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="85"/>
        <source>Pairing…</source>
        <translation>Pairing…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="98"/>
        <source>Looking up code, exchanging keys, gathering ICE candidates.</source>
        <translation>Looking up code, exchanging keys, gathering ICE candidates.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="135"/>
        <source>Pairing failed</source>
        <translation>Pairing failed</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="69"/>
        <location filename="../resources/views/flight/flight_pairing.ui" line="200"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="207"/>
        <source>Connect</source>
        <translation>Connect</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="67"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="85"/>
        <source>drone has {current}/{limit} viewers</source>
        <translation>drone has {current}/{limit} viewers</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="98"/>
        <source>known device — same fingerprint as last pair</source>
        <translation>known device — same fingerprint as last pair</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="101"/>
        <source>new device</source>
        <translation>new device</translation>
    </message>
</context>
<context>
    <name>FlightTile</name>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="462"/>
        <source>Feed {code}</source>
        <translation>Feed {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="366"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="385"/>
        <source>Network: {state}</source>
        <translation>Network: {state}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="379"/>
        <source>latency: {ms:.0f}ms</source>
        <translation>latency: {ms:.0f}ms</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="381"/>
        <source>latency: --</source>
        <translation>latency: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="459"/>
        <source>{name} · {code}</source>
        <translation>{name} · {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="484"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Aircraft serial: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="522"/>
        <source>Rename Feed</source>
        <translation>Rename Feed</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="524"/>
        <source>Nickname for this drone (persists across new pairing codes via the aircraft serial number). Leave blank to clear.</source>
        <translation>Nickname for this drone (persists across new pairing codes via the aircraft serial number). Leave blank to clear.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="556"/>
        <source>Initializing</source>
        <translation>Initializing</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="557"/>
        <source>Connecting</source>
        <translation>Connecting</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="558"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="559"/>
        <source>Connected</source>
        <translation>Connected</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="560"/>
        <source>Disconnected</source>
        <translation>Disconnected</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="561"/>
        <source>Failed</source>
        <translation>Failed</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="562"/>
        <source>Closed</source>
        <translation>Closed</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="576"/>
        <source>Rename Feed...</source>
        <translation>Rename Feed...</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="593"/>
        <source>Restore</source>
        <translation>Restore</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="597"/>
        <source>Maximize</source>
        <translation>Maximize</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="582"/>
        <source>Full Screen</source>
        <translation>Full Screen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="603"/>
        <source>Mute Detections in Gallery</source>
        <translation>Mute Detections in Gallery</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="619"/>
        <source>Stop Recording</source>
        <translation>Stop Recording</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="625"/>
        <source>Start Recording…</source>
        <translation>Start Recording…</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="632"/>
        <source>Replay Recording</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="638"/>
        <source>Reconnect</source>
        <translation>Reconnect</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="644"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
</context>
<context>
    <name>FlightTileContents</name>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="44"/>
        <source>Waiting for video…</source>
        <translation>Waiting for video…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="90"/>
        <source>Network: new</source>
        <translation>Network: new</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="97"/>
        <source>0x0</source>
        <translation>0x0</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="104"/>
        <source>0 fps</source>
        <translation>0 fps</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="111"/>
        <source>0 kbps</source>
        <translation>0 kbps</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="118"/>
        <source>latency: --</source>
        <translation>latency: --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="145"/>
        <source>Watch this feed&apos;s last recording.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="152"/>
        <source>Record this feed: video, detections, telemetry and map.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>FlightTileController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="218"/>
        <source>Looking up code {code} and connecting to the drone.</source>
        <translation>Looking up code {code} and connecting to the drone.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="293"/>
        <source>Name this device</source>
        <translation>Name this device</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="295"/>
        <source>Give this publisher a name so you can recognise it next time (e.g. &apos;Operator A&apos;s M4E&apos;).</source>
        <translation>Give this publisher a name so you can recognise it next time (e.g. &apos;Operator A&apos;s M4E&apos;).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="313"/>
        <source>Device &apos;{label}&apos; presented a different DTLS fingerprint than the last time you paired with it. This could mean the controller was reset, a different controller is using the label, or somebody is impersonating it.

Reject if you weren&apos;t expecting this.</source>
        <translation>Device &apos;{label}&apos; presented a different DTLS fingerprint than the last time you paired with it. This could mean the controller was reset, a different controller is using the label, or somebody is impersonating it.

Reject if you weren&apos;t expecting this.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="480"/>
        <source>Pairing ended before video could start. Ask the operator to generate a new code and try again.</source>
        <translation>Pairing ended before video could start. Ask the operator to generate a new code and try again.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1006"/>
        <source>Waiting for video before recording can start</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1017"/>
        <source>Choose recording folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1109"/>
        <source>REC ● {filename}</source>
        <translation type="unfinished">REC ● {filename}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1124"/>
        <source>Recording saved</source>
        <translation type="unfinished">Recording saved</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1156"/>
        <source>No finished recording to replay yet</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1180"/>
        <source>Could not open replay: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="1187"/>
        <source>Recording error: {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="321"/>
        <source>Fingerprint mismatch — &apos;{label}&apos;</source>
        <translation>Fingerprint mismatch — &apos;{label}&apos;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="330"/>
        <source>Fingerprint changed on {ts}; previous identity was overwritten after operator review.</source>
        <translation>Fingerprint changed on {ts}; previous identity was overwritten after operator review.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="422"/>
        <source>This drone already has {current} viewers connected (maximum {limit}). Ask one to disconnect, or try again later.</source>
        <translation>This drone already has {current} viewers connected (maximum {limit}). Ask one to disconnect, or try again later.</translation>
    </message>
</context>
<context>
    <name>FlightViewerController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="553"/>
        <source>New flight session</source>
        <translation>New flight session</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="555"/>
        <source>Mobile started a new flight under code {code}. The previous session&apos;s detections are still saved on this computer. Discard them, or keep them archived?</source>
        <translation>Mobile started a new flight under code {code}. The previous session&apos;s detections are still saved on this computer. Discard them, or keep them archived?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="681"/>
        <source>Image Analysis</source>
        <translation>Image Analysis</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="702"/>
        <source>Recording Replay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="725"/>
        <source>Streaming Detector</source>
        <translation>Streaming Detector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="742"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="743"/>
        <source>Failed to open {target}:
{error}</source>
        <translation>Failed to open {target}:
{error}</translation>
    </message>
</context>
<context>
    <name>FlightViewerWindow</name>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="14"/>
        <source>ADIAT Flight Viewer</source>
        <translation>ADIAT Flight Viewer</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="21"/>
        <source>Add a feed to begin.  Use Add Feed in the toolbar.</source>
        <translation>Add a feed to begin.  Use Add Feed in the toolbar.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="78"/>
        <source>Main Toolbar</source>
        <translation>Main Toolbar</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="99"/>
        <source>+ Add Feed</source>
        <translation>+ Add Feed</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="49"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="68"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="102"/>
        <source>Pair with an ADIAT Mobile drone controller using a 6-character code.</source>
        <translation>Pair with an ADIAT Mobile drone controller using a 6-character code.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="107"/>
        <source>Mission Gallery</source>
        <translation>Mission Gallery</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="116"/>
        <source>Show or hide the aggregate Mission Gallery panel.</source>
        <translation>Show or hide the aggregate Mission Gallery panel.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="121"/>
        <source>Save Layout</source>
        <translation>Save Layout</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="124"/>
        <source>Save the current dock arrangement for next session.</source>
        <translation>Save the current dock arrangement for next session.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="129"/>
        <source>Restore Layout</source>
        <translation>Restore Layout</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="132"/>
        <source>Apply the last saved dock arrangement.</source>
        <translation>Apply the last saved dock arrangement.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="137"/>
        <source>Close Viewer</source>
        <translation>Close Viewer</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="142"/>
        <source>Map</source>
        <translation>Map</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="151"/>
        <source>Show or hide the detection map dock.</source>
        <translation>Show or hide the detection map dock.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="156"/>
        <source>Open Recording…</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="159"/>
        <source>Watch a recording: video, detections, telemetry and map.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="164"/>
        <source>Open Image Analysis</source>
        <translation>Open Image Analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="167"/>
        <source>Switch to the Image Analysis window for post-flight image review.</source>
        <translation>Switch to the Image Analysis window for post-flight image review.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="172"/>
        <source>Open Streaming Detector</source>
        <translation>Open Streaming Detector</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="175"/>
        <source>Switch to the Streaming Detector window for RTMP / HDMI capture sessions.</source>
        <translation>Switch to the Streaming Detector window for RTMP / HDMI capture sessions.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="180"/>
        <source>ADIAT Help</source>
        <translation>ADIAT Help</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="183"/>
        <source>Open the ADIAT documentation in your browser.</source>
        <translation>Open the ADIAT documentation in your browser.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightViewerWindow.py" line="273"/>
        <source>Rename Feed...</source>
        <translation>Rename Feed...</translation>
    </message>
</context>
<context>
    <name>FrameTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="52"/>
        <source>Enable Processing Region Mask</source>
        <translation>Enable Processing Region Mask</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="55"/>
        <source>Enable to restrict detection processing to a specific region of the video.
Useful for excluding edges, UI overlays, or focusing on specific areas.
Improves performance by not processing masked regions.</source>
        <translation>Enable to restrict detection processing to a specific region of the video.
Useful for excluding edges, UI overlays, or focusing on specific areas.
Improves performance by not processing masked regions.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="67"/>
        <source>Enable Frame Buffer</source>
        <translation>Enable Frame Buffer</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="69"/>
        <source>Exclude a uniform border from all edges of the video.
Enter the number of pixels to exclude from each edge.
The inner area will be processed for detections.</source>
        <translation>Exclude a uniform border from all edges of the video.
Enter the number of pixels to exclude from each edge.
The inner area will be processed for detections.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="77"/>
        <source>Frame Buffer Settings</source>
        <translation>Frame Buffer Settings</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="82"/>
        <source>Buffer (pixels):</source>
        <translation>Buffer (pixels):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="87"/>
        <source>Number of pixels to exclude from all edges (0-1000).
A value of 50 excludes 50 pixels from top, bottom, left, and right.
Useful for removing UI overlays or camera lens distortion at edges.
This value is based on the original video resolution.</source>
        <translation>Number of pixels to exclude from all edges (0-1000).
A value of 50 excludes 50 pixels from top, bottom, left, and right.
Useful for removing UI overlays or camera lens distortion at edges.
This value is based on the original video resolution.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="97"/>
        <source>Enable Image Mask</source>
        <translation>Enable Image Mask</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="99"/>
        <source>Load a black/white image as a custom mask.
White areas will be processed, black areas excluded.
The mask will be scaled to match the video resolution.</source>
        <translation>Load a black/white image as a custom mask.
White areas will be processed, black areas excluded.
The mask will be scaled to match the video resolution.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="107"/>
        <source>Image Mask Settings</source>
        <translation>Image Mask Settings</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="114"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="211"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="332"/>
        <source>No mask image selected</source>
        <translation>No mask image selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="117"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="118"/>
        <source>Select a black/white image file to use as mask</source>
        <translation>Select a black/white image file to use as mask</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="121"/>
        <source>Clear</source>
        <translation>Clear</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="122"/>
        <source>Clear the selected mask image</source>
        <translation>Clear the selected mask image</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="128"/>
        <source>White = Process, Black = Exclude</source>
        <translation>White = Process, Black = Exclude</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="136"/>
        <source>Visualization</source>
        <translation>Visualization</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="139"/>
        <source>Show mask overlay on video</source>
        <translation>Show mask overlay on video</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="142"/>
        <source>Display the processing region on the rendered video.
Frame mode: Shows a cyan rectangle outline of the processed area.
Image mask: Shows a semi-transparent overlay of excluded regions.</source>
        <translation>Display the processing region on the rendered video.
Frame mode: Shows a cyan rectangle outline of the processed area.
Image mask: Shows a semi-transparent overlay of excluded regions.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="226"/>
        <source>Invalid Image</source>
        <translation>Invalid Image</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="227"/>
        <source>{error}</source>
        <translation>{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="229"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Could not load the selected image. Please choose a valid image file.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="238"/>
        <source>Aspect Ratio Mismatch</source>
        <translation>Aspect Ratio Mismatch</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="240"/>
        <source>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</source>
        <translation>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</translation>
    </message>
</context>
<context>
    <name>GPSMapController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="104"/>
        <source>No GPS data found in images</source>
        <translation>No GPS data found in images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="191"/>
        <source>POD overlay cleared — the elevation/canopy source changed. Recalculate to refresh it.</source>
        <translation>POD overlay cleared — the elevation/canopy source changed. Recalculate to refresh it.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="202"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Downloading tiles is disabled in Offline Only mode</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="233"/>
        <source>Calculate POD Coverage?</source>
        <translation>Calculate POD Coverage?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="234"/>
        <source>Coverage data is ready. Calculate the probability-of-detection heatmap for this mission now? (May take several minutes.)</source>
        <translation>Coverage data is ready. Calculate the probability-of-detection heatmap for this mission now? (May take several minutes.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="293"/>
        <source>Your local USGS 3DEP tiles only partially cover this mission.</source>
        <translation>Your local USGS 3DEP tiles only partially cover this mission.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="296"/>
        <source>Your local USGS 3DEP tiles do not cover this mission.</source>
        <translation>Your local USGS 3DEP tiles do not cover this mission.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="300"/>
        <source>Local Elevation Coverage</source>
        <translation>Local Elevation Coverage</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="302"/>
        <source>Frames outside the local tiles will use online AWS Terrain Tiles (~30 m) elevation instead. You can download 1 m tiles for this area first, or continue with the fallback.</source>
        <translation>Frames outside the local tiles will use online AWS Terrain Tiles (~30 m) elevation instead. You can download 1 m tiles for this area first, or continue with the fallback.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="305"/>
        <source>Download Tiles...</source>
        <translation>Download Tiles...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="307"/>
        <source>Continue</source>
        <translation>Continue</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="336"/>
        <source>POD calculation is unavailable</source>
        <translation>POD calculation is unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="355"/>
        <source>The tile downloader is unavailable</source>
        <translation>The tile downloader is unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="385"/>
        <source>Download Canopy Data?</source>
        <translation>Download Canopy Data?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="386"/>
        <source>No canopy-height data is configured for this mission.

Download elevation and canopy tiles for this area now so the canopy overlay and terrain-aware detection coverage can use them?

This downloads Meta/WRI canopy height (1 m) and sets it as the canopy source, replacing any LANDFIRE selection (LANDFIRE tiles must be added manually).</source>
        <translation>No canopy-height data is configured for this mission.

Download elevation and canopy tiles for this area now so the canopy overlay and terrain-aware detection coverage can use them?

This downloads Meta/WRI canopy height (1 m) and sets it as the canopy source, replacing any LANDFIRE selection (LANDFIRE tiles must be added manually).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="569"/>
        <source>Not covered — no looks</source>
        <translation>Not covered — no looks</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="570"/>
        <source>Terrain occlusion</source>
        <translation>Terrain occlusion</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="571"/>
        <source>Canopy</source>
        <translation>Canopy</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="572"/>
        <source>Image resolution (GSD)</source>
        <translation>Image resolution (GSD)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="573"/>
        <source>None</source>
        <translation>None</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="575"/>
        <source>Unknown</source>
        <translation>Unknown</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="602"/>
        <source>Altitude basis: reported ATO (approximate over terrain)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="783"/>
        <source>Building canopy overlay...</source>
        <translation>Building canopy overlay...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="809"/>
        <source>No canopy data covers this area</source>
        <translation>No canopy data covers this area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="869"/>
        <source>POD: {pod}% (beta)   Looks: {looks}</source>
        <translation>POD: {pod}% (beta)   Looks: {looks}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="872"/>
        <source>Limiting factor: {factor}</source>
        <translation>Limiting factor: {factor}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="911"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="924"/>
        <source>Image {n}</source>
        <translation>Image {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="912"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="927"/>
        <source>View {name}</source>
        <translation>View {name}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1296"/>
        <source>Update AOI Location?</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1297"/>
        <source>Move this AOI to {lat:.6f}, {lon:.6f}?

That is {dist:.1f} m from its previous position. The corrected location is saved with the results and used for exports.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1309"/>
        <source>AOI location updated</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1319"/>
        <source>AOI location reset to the computed estimate</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="884"/>
        <source>Find location in images</source>
        <translation>Find location in images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="931"/>
        <source>{name} (no flagged AOIs)</source>
        <translation>{name} (no flagged AOIs)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1066"/>
        <source>GPS coordinate not in any images</source>
        <translation>GPS coordinate not in any images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="593"/>
        <source>{value} ft</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="595"/>
        <source>{value} m</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="596"/>
        <source>Altitude basis: takeoff elevation {elev}</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>GPSMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="60"/>
        <source>GPS Map View</source>
        <translation>GPS Map View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="116"/>
        <source>Zoom In (+)</source>
        <translation>Zoom In (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="120"/>
        <source>Zoom Out (-)</source>
        <translation>Zoom Out (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="124"/>
        <source>Fit All (F)</source>
        <translation>Fit All (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="128"/>
        <source>Rotate (R)</source>
        <translation>Rotate (R)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="136"/>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="348"/>
        <source>Satellite View</source>
        <translation>Satellite View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="143"/>
        <source>POD Overlay</source>
        <translation>POD Overlay</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="147"/>
        <source>Run a map export with the POD option to generate this overlay</source>
        <translation>Run a map export with the POD option to generate this overlay</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="152"/>
        <source>POD (beta)</source>
        <translation>POD (beta)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="153"/>
        <source>Look count</source>
        <translation>Look count</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="154"/>
        <source>Canopy height</source>
        <translation>Canopy height</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="164"/>
        <source>POD overlay opacity</source>
        <translation>POD overlay opacity</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="170"/>
        <source>Download Canopy Tiles</source>
        <translation>Download Canopy Tiles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="177"/>
        <source>Calculate POD</source>
        <translation>Calculate POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="179"/>
        <source>Compute the terrain-aware probability-of-detection heatmap for this mission (may take several minutes)</source>
        <translation>Compute the terrain-aware probability-of-detection heatmap for this mission (may take several minutes)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="188"/>
        <source>Click point to select • Drag to pan • Scroll to zoom • Drag AOI marker to correct its location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="273"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Downloading tiles is disabled in Offline Only mode</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="275"/>
        <source>Download elevation and canopy-height tiles for this mission&apos;s area</source>
        <translation>Download elevation and canopy-height tiles for this mission&apos;s area</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="345"/>
        <source>Map View</source>
        <translation>Map View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="382"/>
        <source>⚠ {error}</source>
        <translation>⚠ {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="392"/>
        <source>Map Tile Loading Issue</source>
        <translation>Map Tile Loading Issue</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="394"/>
        <source>{error}

The map will continue to work with cached tiles where available.</source>
        <translation>{error}

The map will continue to work with cached tiles where available.</translation>
    </message>
</context>
<context>
    <name>GPSMapView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1278"/>
        <source>Copy Data</source>
        <translation>Copy Data</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1282"/>
        <source>Reset to estimated position</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1422"/>
        <source>Position corrected by user</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1423"/>
        <source>Drag to correct the location</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1873"/>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1984"/>
        <source>Zoom FOV</source>
        <translation>Zoom FOV</translation>
    </message>
</context>
<context>
    <name>GalleryUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="369"/>
        <source>0 AOIs</source>
        <translation>0 AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOI</source>
        <translation>AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOIs</source>
        <translation>AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="412"/>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="435"/>
        <source>{count} {label}</source>
        <translation>{count} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="430"/>
        <source>Area of Interest</source>
        <translation>Area of Interest</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="432"/>
        <source>Areas of Interest</source>
        <translation>Areas of Interest</translation>
    </message>
</context>
<context>
    <name>GeneralSettingsPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="121"/>
        <source>Select AOI Highlight Color</source>
        <translation>Select AOI Highlight Color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="159"/>
        <source>Benchmark Complete</source>
        <translation>Benchmark Complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="161"/>
        <source>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</source>
        <translation>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</translation>
    </message>
</context>
<context>
    <name>GridReviewController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="151"/>
        <source>Grid review works in single-image mode — exit the gallery first.</source>
        <translation>Grid review works in single-image mode — exit the gallery first.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="273"/>
        <source>This image keeps its existing grid — the new size applies to unstarted images.</source>
        <translation>This image keeps its existing grid — the new size applies to unstarted images.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="320"/>
        <source>Apply Grid to All Images</source>
        <translation>Apply Grid to All Images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="322"/>
        <source>{n} image(s) already have review progress recorded at a different grid size.

Reset their progress and apply {rows}×{cols} to them too?

Yes resets them; No keeps them at their current size.</source>
        <translation>{n} image(s) already have review progress recorded at a different grid size.

Reset their progress and apply {rows}×{cols} to them too?

Yes resets them; No keeps them at their current size.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="391"/>
        <source>Image fully reviewed — advancing</source>
        <translation>Image fully reviewed — advancing</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="628"/>
        <source>cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed</source>
        <translation>cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed</translation>
    </message>
</context>
<context>
    <name>GridReviewDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="52"/>
        <source>Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)</source>
        <translation>Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="55"/>
        <source>Suggested: {rows}×{cols}</source>
        <translation>Suggested: {rows}×{cols}</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="14"/>
        <source>Grid Review Settings</source>
        <translation>Grid Review Settings</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="23"/>
        <source>Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.</source>
        <translation>Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="32"/>
        <source>Rows</source>
        <translation>Rows</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="52"/>
        <source>Columns</source>
        <translation>Columns</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="74"/>
        <source>Mark cells reviewed when advancing (Space)</source>
        <translation>Mark cells reviewed when advancing (Space)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="84"/>
        <source>Draw a 3×3 guide inside the active cell to focus your scan. Visual only — it does not change what gets reviewed.</source>
        <translation>Draw a 3×3 guide inside the active cell to focus your scan. Visual only — it does not change what gets reviewed.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="87"/>
        <source>Show 3×3 focus guide inside each cell</source>
        <translation>Show 3×3 focus guide inside each cell</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="97"/>
        <source>Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.</source>
        <translation>Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="100"/>
        <source>Apply this grid size to all images</source>
        <translation>Apply this grid size to all images</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="112"/>
        <source>No grid suggestion available (image GSD unknown).</source>
        <translation>No grid suggestion available (image GSD unknown).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="119"/>
        <source>Use Suggestion</source>
        <translation>Use Suggestion</translation>
    </message>
</context>
<context>
    <name>HSVColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
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
        <translation>Select a target color from an image to detect.
Opens a color picker that allows you to:
• Load an image from the input folder
• Click on pixels to sample colors
• Automatically calculates HSV values
• Sets Hue, Saturation, and Value ranges
The selected color becomes the center of your HSV detection range.
Adjust the +/- range values to capture color variations.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="37"/>
        <source> Pick Color</source>
        <translation> Pick Color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="44"/>
        <source>color.png</source>
        <translation>color.png</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="57"/>
        <source>Visual preview of the currently selected target color.
Shows the center color of your HSV detection range.
The actual detection will match colors within the specified +/- ranges around this color.</source>
        <translation>Visual preview of the currently selected target color.
Shows the center color of your HSV detection range.
The actual detection will match colors within the specified +/- ranges around this color.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="92"/>
        <source>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</source>
        <translation>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="97"/>
        <source>Hue Range</source>
        <translation>Hue Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="109"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="215"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="315"/>
        <source>-</source>
        <translation>-</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="121"/>
        <source>Lower hue range tolerance.
• Range: 0 to 179
• Default: 20
Subtracts from the target hue value to define the lower bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, minus 20 = detects hues from 80-100.</source>
        <translation>Lower hue range tolerance.
• Range: 0 to 179
• Default: 20
Subtracts from the target hue value to define the lower bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, minus 20 = detects hues from 80-100.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="147"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="250"/>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="350"/>
        <source>+</source>
        <translation>+</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="159"/>
        <source>Upper hue range tolerance.
• Range: 0 to 179
• Default: 20
Adds to the target hue value to define the upper bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, plus 20 = detects hues from 100-120.</source>
        <translation>Upper hue range tolerance.
• Range: 0 to 179
• Default: 20
Adds to the target hue value to define the upper bound.
Lower values = stricter color matching, higher values = more color variation accepted.
Example: Target hue 100, plus 20 = detects hues from 100-120.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="198"/>
        <source>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</source>
        <translation>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="203"/>
        <source>Saturation Range</source>
        <translation>Saturation Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="227"/>
        <source>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</source>
        <translation>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="262"/>
        <source>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</source>
        <translation>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="298"/>
        <source>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</source>
        <translation>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="303"/>
        <source>Value Range</source>
        <translation>Value Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="327"/>
        <source>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</source>
        <translation>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="362"/>
        <source>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</source>
        <translation>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="410"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="415"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="422"/>
        <source>eye.png</source>
        <translation>eye.png</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeAssistant</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="661"/>
        <source>HSV Color Range Assistant - Click Selection</source>
        <translation>HSV Color Range Assistant - Click Selection</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="694"/>
        <source>Interactive image viewer with color selection.

NAVIGATION:
• Mouse wheel: Zoom in/out
• Left-click drag: Pan around image
• Double-click: Fit image to view

COLOR SELECTION:
• Hold CTRL + Left-click: Select similar colors
• Hold CTRL+SHIFT + Left-click: Remove/erase selection
• [ ] keys: Adjust selection radius
• CTRL+Z: Undo last selection
• CTRL+SHIFT+Z: Redo

DISPLAY:
• White overlay = selected pixels
• Yellow text = HSV values at cursor position
• Circular cursor appears when holding CTRL</source>
        <translation>Interactive image viewer with color selection.

NAVIGATION:
• Mouse wheel: Zoom in/out
• Left-click drag: Pan around image
• Double-click: Fit image to view

COLOR SELECTION:
• Hold CTRL + Left-click: Select similar colors
• Hold CTRL+SHIFT + Left-click: Remove/erase selection
• [ ] keys: Adjust selection radius
• CTRL+Z: Undo last selection
• CTRL+SHIFT+Z: Redo

DISPLAY:
• White overlay = selected pixels
• Yellow text = HSV values at cursor position
• Circular cursor appears when holding CTRL</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="741"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="743"/>
        <source>Browse for an image file to load.
Opens a file dialog to select an image from your computer.
• Supported formats: PNG, JPG, JPEG, BMP
• Load an image to start selecting colors
The image will be displayed in the main viewer on the left.</source>
        <translation>Browse for an image file to load.
Opens a file dialog to select an image from your computer.
• Supported formats: PNG, JPG, JPEG, BMP
• Load an image to start selecting colors
The image will be displayed in the main viewer on the left.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="753"/>
        <source>Reset</source>
        <translation>Reset</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="755"/>
        <source>Reset all selections and start over.
• Clears all selected pixels (white overlay)
• Resets HSV ranges to defaults
• Clears the mask preview
• Undoable with CTRL+Z
Use this to start fresh without reloading the image.</source>
        <translation>Reset all selections and start over.
• Clears all selected pixels (white overlay)
• Resets HSV ranges to defaults
• Clears the mask preview
• Undoable with CTRL+Z
Use this to start fresh without reloading the image.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="766"/>
        <source>Selection Radius:</source>
        <translation>Selection Radius:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="768"/>
        <source>Size of the circular selection cursor.
Determines how many pixels are sampled when you CTRL+Click.</source>
        <translation>Size of the circular selection cursor.
Determines how many pixels are sampled when you CTRL+Click.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="777"/>
        <source>Set the selection cursor radius in pixels.
• Range: 1-50 pixels
• Default: 1 pixel (single pixel selection)
Larger radius:
• Samples more pixels when clicking
• Averages colors within the circle
• Good for selecting gradients or textured areas
Smaller radius:
• More precise selection
• Better for solid colors
Keyboard shortcuts: [ decrease, ] increase by 2 pixels</source>
        <translation>Set the selection cursor radius in pixels.
• Range: 1-50 pixels
• Default: 1 pixel (single pixel selection)
Larger radius:
• Samples more pixels when clicking
• Averages colors within the circle
• Good for selecting gradients or textured areas
Smaller radius:
• More precise selection
• Better for solid colors
Keyboard shortcuts: [ decrease, ] increase by 2 pixels</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="793"/>
        <source>Color Tolerance:</source>
        <translation>Color Tolerance:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="795"/>
        <source>HSV color matching tolerance.
Controls how similar colors must be to get selected.</source>
        <translation>HSV color matching tolerance.
Controls how similar colors must be to get selected.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="803"/>
        <source>Set color tolerance for similar pixel detection.
• Range: 0-50
• Default: 2
When you CTRL+Click, pixels are selected if their HSV values are within this tolerance:
• 0: Exact match only (very strict)
• 2-5: Small variations (recommended for most cases)
• 10+: Large variations (may select too many colors)
Higher tolerance:
• Selects more similar colors
• Good for images with lighting variation
• May include unwanted colors
Lower tolerance:
• More precise color matching
• May miss some pixels of target color</source>
        <translation>Set color tolerance for similar pixel detection.
• Range: 0-50
• Default: 2
When you CTRL+Click, pixels are selected if their HSV values are within this tolerance:
• 0: Exact match only (very strict)
• 2-5: Small variations (recommended for most cases)
• 10+: Large variations (may select too many colors)
Higher tolerance:
• Selects more similar colors
• Good for images with lighting variation
• May include unwanted colors
Lower tolerance:
• More precise color matching
• May miss some pixels of target color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="825"/>
        <source>CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius</source>
        <translation>CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="831"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="833"/>
        <source>Show detailed help and instructions.
Opens a dialog with:
• Step-by-step usage instructions
• Navigation controls explanation
• Color selection techniques
• Keyboard shortcuts reference
Click here if you&apos;re unsure how to use this tool.</source>
        <translation>Show detailed help and instructions.
Opens a dialog with:
• Step-by-step usage instructions
• Navigation controls explanation
• Color selection techniques
• Keyboard shortcuts reference
Click here if you&apos;re unsure how to use this tool.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="859"/>
        <source>Selected Color</source>
        <translation>Selected Color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="861"/>
        <source>Average color of all selected pixels.
Shows the center/mean color that will be used for HSV range detection.</source>
        <translation>Average color of all selected pixels.
Shows the center/mean color that will be used for HSV range detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="866"/>
        <source>Color:</source>
        <translation>Color:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="868"/>
        <source>Visual preview of the average selected color.
This is the center color calculated from all selected pixels.</source>
        <translation>Visual preview of the average selected color.
This is the center color calculated from all selected pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="876"/>
        <source>Color swatch showing the average of all selected pixels.
This becomes the center color for HSV range detection.</source>
        <translation>Color swatch showing the average of all selected pixels.
This becomes the center color for HSV range detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="881"/>
        <source>HEX:</source>
        <translation>HEX:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="883"/>
        <source>Hexadecimal representation of the selected color.
Format: #RRGGBB</source>
        <translation>Hexadecimal representation of the selected color.
Format: #RRGGBB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="889"/>
        <source>Hex color code of the average selected color.
Can be used to identify the exact RGB color value.</source>
        <translation>Hex color code of the average selected color.
Can be used to identify the exact RGB color value.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="894"/>
        <source>HSV:</source>
        <translation>HSV:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="896"/>
        <source>HSV values of the selected color.
H = Hue (0-360°), S = Saturation (0-100%), V = Value (0-100%)</source>
        <translation>HSV values of the selected color.
H = Hue (0-360°), S = Saturation (0-100%), V = Value (0-100%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="902"/>
        <source>HSV color values of the average selected color.
This is the center point of your color range.</source>
        <translation>HSV color values of the average selected color.
This is the center point of your color range.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="910"/>
        <source>HSV Ranges</source>
        <translation>HSV Ranges</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="912"/>
        <source>HSV color range configuration.
Defines the detection range for each HSV channel.
Center values are calculated from selected pixels.
Buffer values add extra tolerance to catch color variations.</source>
        <translation>HSV color range configuration.
Defines the detection range for each HSV channel.
Center values are calculated from selected pixels.
Buffer values add extra tolerance to catch color variations.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="920"/>
        <source>Channel</source>
        <translation>Channel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="921"/>
        <source>HSV color channel (Hue, Saturation, Value)</source>
        <translation>HSV color channel (Hue, Saturation, Value)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="924"/>
        <source>Center</source>
        <translation>Center</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="925"/>
        <source>Average value of selected pixels for this channel</source>
        <translation>Average value of selected pixels for this channel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="928"/>
        <source>- Buffer</source>
        <translation>- Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="929"/>
        <source>Extra tolerance below center value (lower bound buffer)</source>
        <translation>Extra tolerance below center value (lower bound buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="932"/>
        <source>+ Buffer</source>
        <translation>+ Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="933"/>
        <source>Extra tolerance above center value (upper bound buffer)</source>
        <translation>Extra tolerance above center value (upper bound buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="936"/>
        <source>Final Range</source>
        <translation>Final Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="937"/>
        <source>Complete detection range (min-max) after applying buffers</source>
        <translation>Complete detection range (min-max) after applying buffers</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="941"/>
        <source>Hue:</source>
        <translation>Hue:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="942"/>
        <source>Hue channel (color type): 0-360 degrees on color wheel</source>
        <translation>Hue channel (color type): 0-360 degrees on color wheel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="947"/>
        <source>Center hue value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-360° (red=0°, green=120°, blue=240°)</source>
        <translation>Center hue value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-360° (red=0°, green=120°, blue=240°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="957"/>
        <source>Hue lower bound buffer (subtract from center).
• Range: 0-360°
• Adds tolerance below the center hue
• Larger values detect more hues in the minus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Hue lower bound buffer (subtract from center).
• Range: 0-360°
• Adds tolerance below the center hue
• Larger values detect more hues in the minus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="971"/>
        <source>Hue upper bound buffer (add to center).
• Range: 0-360°
• Adds tolerance above the center hue
• Larger values detect more hues in the plus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Hue upper bound buffer (add to center).
• Range: 0-360°
• Adds tolerance above the center hue
• Larger values detect more hues in the plus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="983"/>
        <source>Final hue detection range.
Shows the complete min-max hue range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Final hue detection range.
Shows the complete min-max hue range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="990"/>
        <source>WARNING: Too wide of a Hue range can result in false positives!</source>
        <translation>WARNING: Too wide of a Hue range can result in false positives!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="994"/>
        <source>Hue range warning.
Your total hue range exceeds 60°.
Wide hue ranges may detect many different colors.
Consider narrowing the buffers for more accurate detection.</source>
        <translation>Hue range warning.
Your total hue range exceeds 60°.
Wide hue ranges may detect many different colors.
Consider narrowing the buffers for more accurate detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1002"/>
        <source>Sat:</source>
        <translation>Sat:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1003"/>
        <source>Saturation channel (color intensity): 0-100%</source>
        <translation>Saturation channel (color intensity): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1008"/>
        <source>Center saturation value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=gray, 100%=vivid color)</source>
        <translation>Center saturation value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=gray, 100%=vivid color)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1018"/>
        <source>Saturation lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center saturation
• Larger values detect more desaturated/grayish colors
• Be careful: very low saturation includes gray colors
WARNING: Lower bound &lt; 25% may include unwanted gray/desaturated colors</source>
        <translation>Saturation lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center saturation
• Larger values detect more desaturated/grayish colors
• Be careful: very low saturation includes gray colors
WARNING: Lower bound &lt; 25% may include unwanted gray/desaturated colors</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1032"/>
        <source>Saturation upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center saturation
• Larger values detect more saturated/vivid colors
• Higher saturation generally safe to increase</source>
        <translation>Saturation upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center saturation
• Larger values detect more saturated/vivid colors
• Higher saturation generally safe to increase</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1043"/>
        <source>Final saturation detection range.
Shows the complete min-max saturation range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Final saturation detection range.
Shows the complete min-max saturation range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1050"/>
        <source>WARNING: Too low of a Saturation level can result in false positives!</source>
        <translation>WARNING: Too low of a Saturation level can result in false positives!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1054"/>
        <source>Saturation range warning.
Your lower saturation bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unwanted gray or desaturated objects.</source>
        <translation>Saturation range warning.
Your lower saturation bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unwanted gray or desaturated objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1062"/>
        <source>Val:</source>
        <translation>Val:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1063"/>
        <source>Value channel (brightness): 0-100%</source>
        <translation>Value channel (brightness): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1068"/>
        <source>Center value/brightness (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=black, 100%=bright)</source>
        <translation>Center value/brightness (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=black, 100%=bright)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1078"/>
        <source>Value lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center brightness
• Larger values detect darker versions of the color
• Be careful: very low value includes very dark/black colors
WARNING: Lower bound &lt; 25% may include unwanted shadows or dark objects</source>
        <translation>Value lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center brightness
• Larger values detect darker versions of the color
• Be careful: very low value includes very dark/black colors
WARNING: Lower bound &lt; 25% may include unwanted shadows or dark objects</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1092"/>
        <source>Value upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center brightness
• Larger values detect brighter versions of the color
• Higher brightness generally safe to increase</source>
        <translation>Value upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center brightness
• Larger values detect brighter versions of the color
• Higher brightness generally safe to increase</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1103"/>
        <source>Final value/brightness detection range.
Shows the complete min-max brightness range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Final value/brightness detection range.
Shows the complete min-max brightness range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1110"/>
        <source>WARNING: Too low of a Value level can result in false positives!</source>
        <translation>WARNING: Too low of a Value level can result in false positives!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1114"/>
        <source>Value range warning.
Your lower value bound is below 25%.
Low value includes very dark colors.
May detect unwanted shadows or dark objects.</source>
        <translation>Value range warning.
Your lower value bound is below 25%.
Low value includes very dark colors.
May detect unwanted shadows or dark objects.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1124"/>
        <source>Statistics</source>
        <translation>Statistics</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1126"/>
        <source>Statistics about your current selection.
Shows how many pixels are selected and what percentage of the image they represent.</source>
        <translation>Statistics about your current selection.
Shows how many pixels are selected and what percentage of the image they represent.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1130"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1225"/>
        <source>Selected Pixels: 0</source>
        <translation>Selected Pixels: 0</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1132"/>
        <source>Number of pixels currently selected.
Shows the total count of white-highlighted pixels in the main viewer.
Updates in real-time as you select colors.</source>
        <translation>Number of pixels currently selected.
Shows the total count of white-highlighted pixels in the main viewer.
Updates in real-time as you select colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1137"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1226"/>
        <source>Coverage: 0%</source>
        <translation>Coverage: 0%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1139"/>
        <source>Percentage of image covered by selection.
Shows what portion of the total image is selected.
• Low %: Precise selection, may miss some target pixels
• High %: Broad selection, may include unwanted areas</source>
        <translation>Percentage of image covered by selection.
Shows what portion of the total image is selected.
• Low %: Precise selection, may miss some target pixels
• High %: Broad selection, may include unwanted areas</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1148"/>
        <source>Mask Preview</source>
        <translation>Mask Preview</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1150"/>
        <source>Black and white preview of the detection mask.
Shows what pixels will be detected with current HSV ranges and buffers.</source>
        <translation>Black and white preview of the detection mask.
Shows what pixels will be detected with current HSV ranges and buffers.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1161"/>
        <source>Grayscale mask preview.
• White pixels: Will be detected with current settings
• Black pixels: Will NOT be detected
Updates automatically when you adjust buffers.
Use this to verify your HSV range captures the target without false positives.</source>
        <translation>Grayscale mask preview.
• White pixels: Will be detected with current settings
• Black pixels: Will NOT be detected
Updates automatically when you adjust buffers.
Use this to verify your HSV range captures the target without false positives.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1179"/>
        <source>Select Image</source>
        <translation>Select Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1180"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp)</source>
        <translation>Images (*.png *.jpg *.jpeg *.bmp)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1237"/>
        <source>Selected Pixels: {0:,}</source>
        <translation>Selected Pixels: {0:,}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1238"/>
        <source>Coverage: {0:.1f}%</source>
        <translation>Coverage: {0:.1f}%</translation>
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
        <translation>
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
</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1504"/>
        <source>HSV Color Range Assistant - Help</source>
        <translation>HSV Color Range Assistant - Help</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="97"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="120"/>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="125"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="176"/>
        <source>Hue Expansion</source>
        <translation>Hue Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="178"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="468"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="53"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="63"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="99"/>
        <source>Hue Expansion</source>
        <translation>Hue Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="101"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="408"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>HSVColorRowWizardWidget</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="392"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="392"/>
        <source>H: {h_min}-{h_max}°, S: {s_min}-{s_max}, V: {v_min}-{v_max}</source>
        <translation>H: {h_min}-{h_max}°, S: {s_min}-{s_max}, V: {v_min}-{v_max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="212"/>
        <source>Match
Tolerance:</source>
        <translation>Match
Tolerance:</translation>
    </message>
</context>
<context>
    <name>HSVRangePickerWidget</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="90"/>
        <source>HEX:</source>
        <translation>HEX:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="93"/>
        <source>Hexadecimal color code input.
Enter colors as hex codes (e.g., #FF0000 for red).</source>
        <translation>Hexadecimal color code input.
Enter colors as hex codes (e.g., #FF0000 for red).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="102"/>
        <source>Enter a hexadecimal color code.
• Format: #RRGGBB (e.g., #FF0000 for red, #00FF00 for green)
• Also accepts short format: #RGB (e.g., #F00 for red)
Type or paste a hex code to quickly set a specific color.
The color will be converted to HSV automatically.</source>
        <translation>Enter a hexadecimal color code.
• Format: #RRGGBB (e.g., #FF0000 for red, #00FF00 for green)
• Also accepts short format: #RGB (e.g., #F00 for red)
Type or paste a hex code to quickly set a specific color.
The color will be converted to HSV automatically.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="111"/>
        <source>Reset to Default</source>
        <translation>Reset to Default</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="114"/>
        <source>Reset to default color and ranges.
• Color: Pure red (H:0°, S:100%, V:100%)
• Hue range: ±20° (total 40° range)
• Saturation range: ±20%
• Value range: ±20%
Use this to start over with standard settings.</source>
        <translation>Reset to default color and ranges.
• Color: Pure red (H:0°, S:100%, V:100%)
• Hue range: ±20° (total 40° range)
• Saturation range: ±20%
• Value range: ±20%
Use this to start over with standard settings.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="137"/>
        <source>Saturation / Value</source>
        <translation>Saturation / Value</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="141"/>
        <source>Saturation and Value (brightness) selector.
Saturation controls color intensity (left=gray, right=vivid).
Value controls brightness (bottom=dark, top=bright).</source>
        <translation>Saturation and Value (brightness) selector.
Saturation controls color intensity (left=gray, right=vivid).
Value controls brightness (bottom=dark, top=bright).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="149"/>
        <source>Interactive Saturation/Value selector.
• Click anywhere to set the center color&apos;s saturation and brightness
• White circle = current center color position
• White rectangle = detection range (adjustable)
• Drag white corner handles to adjust saturation/value ranges
• Horizontal range = saturation tolerance
• Vertical range = value/brightness tolerance
Larger ranges detect more color variations but may include unwanted colors.</source>
        <translation>Interactive Saturation/Value selector.
• Click anywhere to set the center color&apos;s saturation and brightness
• White circle = current center color position
• White rectangle = detection range (adjustable)
• Drag white corner handles to adjust saturation/value ranges
• Horizontal range = saturation tolerance
• Vertical range = value/brightness tolerance
Larger ranges detect more color variations but may include unwanted colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="165"/>
        <source>Hue</source>
        <translation>Hue</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="169"/>
        <source>Hue (color type) selector.
Hue represents the actual color: red, orange, yellow, green, cyan, blue, purple, magenta.</source>
        <translation>Hue (color type) selector.
Hue represents the actual color: red, orange, yellow, green, cyan, blue, purple, magenta.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="176"/>
        <source>Interactive Hue color ring selector.
• Click on the ring to select a hue (color type)
• White line = current center hue
• Gray arcs and lines = hue detection range (adjustable)
• Drag white circle handles to adjust hue range
• Left handle = lower bound (minus range)
• Right handle = upper bound (plus range)
Warning: Hue ranges wider than 60° may detect too many colors.</source>
        <translation>Interactive Hue color ring selector.
• Click on the ring to select a hue (color type)
• White line = current center hue
• Gray arcs and lines = hue detection range (adjustable)
• Drag white circle handles to adjust hue range
• Left handle = lower bound (minus range)
• Right handle = upper bound (plus range)
Warning: Hue ranges wider than 60° may detect too many colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="205"/>
        <source>Use Image</source>
        <translation>Use Image</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="208"/>
        <source>Open HSV Color Range Assistant.
Advanced tool for selecting colors from an image:
• Load an image from your input folder
• Click on pixels to sample colors
• Automatically calculates optimal HSV ranges
• See real-time preview of detection results
Recommended for finding the best color range for your target.</source>
        <translation>Open HSV Color Range Assistant.
Advanced tool for selecting colors from an image:
• Load an image from your input folder
• Click on pixels to sample colors
• Automatically calculates optimal HSV ranges
• See real-time preview of detection results
Recommended for finding the best color range for your target.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="219"/>
        <source>Pick Screen Color</source>
        <translation>Pick Screen Color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="222"/>
        <source>Pick a color from anywhere on your screen.
Opens a color picker that lets you:
• Click anywhere on your screen to sample a color
• Sample from other applications or images
The picked color will be set as the center color.
Ranges remain unchanged - adjust manually after picking.</source>
        <translation>Pick a color from anywhere on your screen.
Opens a color picker that lets you:
• Click anywhere on your screen to sample a color
• Sample from other applications or images
The picked color will be set as the center color.
Ranges remain unchanged - adjust manually after picking.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="232"/>
        <source>Add to Custom Colors</source>
        <translation>Add to Custom Colors</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="235"/>
        <source>Save current color to Custom Colors palette.
Adds the current center color to the first empty slot in Custom Colors.
• Only saves the color, not the ranges
• Click saved colors to quickly reuse them
• Custom colors persist across sessions
Useful for building a palette of frequently used colors.</source>
        <translation>Save current color to Custom Colors palette.
Adds the current center color to the first empty slot in Custom Colors.
• Only saves the color, not the ranges
• Click saved colors to quickly reuse them
• Custom colors persist across sessions
Useful for building a palette of frequently used colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="253"/>
        <source>Basic Colors:</source>
        <translation>Basic Colors:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="256"/>
        <source>Preset basic color palette.
Quick access to common colors like red, orange, yellow, green, cyan, blue, purple, and grayscale.
Click any color swatch to set it as the center color.</source>
        <translation>Preset basic color palette.
Quick access to common colors like red, orange, yellow, green, cyan, blue, purple, and grayscale.
Click any color swatch to set it as the center color.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="264"/>
        <source>Basic color swatches.
Click any color to quickly set it as your center color.
• Top row: Primary colors and tints
• Bottom row: Grayscale and darker shades
Useful for quickly selecting standard colors.</source>
        <translation>Basic color swatches.
Click any color to quickly set it as your center color.
• Top row: Primary colors and tints
• Bottom row: Grayscale and darker shades
Useful for quickly selecting standard colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="274"/>
        <source>Custom Colors:</source>
        <translation>Custom Colors:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="277"/>
        <source>Your saved custom color palette.
Colors you&apos;ve saved using &apos;Add to Custom Colors&apos; button.
Click any saved color to reuse it.</source>
        <translation>Your saved custom color palette.
Colors you&apos;ve saved using &apos;Add to Custom Colors&apos; button.
Click any saved color to reuse it.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="285"/>
        <source>Custom color swatches.
Click any color to set it as your center color.
• Empty slots shown as gray
• Use &apos;Add to Custom Colors&apos; button to save current color
• Custom colors persist across sessions
Build your own palette of frequently used colors.</source>
        <translation>Custom color swatches.
Click any color to set it as your center color.
• Empty slots shown as gray
• Use &apos;Add to Custom Colors&apos; button to save current color
• Custom colors persist across sessions
Build your own palette of frequently used colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="461"/>
        <source>Current HSV color range summary.
Shows the center color and detection ranges in real-time.
Warning indicators appear when ranges may cause detection issues.</source>
        <translation>Current HSV color range summary.
Shows the center color and detection ranges in real-time.
Warning indicators appear when ranges may cause detection issues.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Center HSV:</source>
        <translation>Center HSV:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Hue Range:</source>
        <translation>Hue Range:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Sat Range:</source>
        <translation>Sat Range:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Val Range:</source>
        <translation>Val Range:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="472"/>
        <source>Current center HSV color values.
H = Hue (0-360°), S = Saturation (0-100%), V = Value/brightness (0-100%).</source>
        <translation>Current center HSV color values.
H = Hue (0-360°), S = Saturation (0-100%), V = Value/brightness (0-100%).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="473"/>
        <source>Hue detection range (minus/plus from center).
Total range = minus + plus. Warning shown if total &gt; 60°.</source>
        <translation>Hue detection range (minus/plus from center).
Total range = minus + plus. Warning shown if total &gt; 60°.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="474"/>
        <source>Saturation detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Saturation detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="475"/>
        <source>Value detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Value detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="497"/>
        <source>⚠ Too wide!</source>
        <translation>⚠ Too wide!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="502"/>
        <source>Hue range warning.
Your hue range is wider than 60° total.
Wide hue ranges may detect too many different colors.
Consider narrowing the range for more accurate detection.</source>
        <translation>Hue range warning.
Your hue range is wider than 60° total.
Wide hue ranges may detect too many different colors.
Consider narrowing the range for more accurate detection.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="510"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="523"/>
        <source>⚠ Too low!</source>
        <translation>⚠ Too low!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="515"/>
        <source>Saturation range warning.
Your saturation lower bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unintended gray or desaturated colors.</source>
        <translation>Saturation range warning.
Your saturation lower bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unintended gray or desaturated colors.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="528"/>
        <source>Value range warning.
Your value lower bound is below 25%.
Low value includes very dark colors.
May detect shadows or dark unintended objects.</source>
        <translation>Value range warning.
Your value lower bound is below 25%.
Low value includes very dark colors.
May detect shadows or dark unintended objects.</translation>
    </message>
</context>
<context>
    <name>HeatmapViewerDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="34"/>
        <source>AOI Detection Heatmap</source>
        <translation>AOI Detection Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="59"/>
        <source>Threshold</source>
        <translation>Threshold</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="62"/>
        <source>Percentile:</source>
        <translation>Percentile:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="81"/>
        <source>Grid Resolution</source>
        <translation>Grid Resolution</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="86"/>
        <source>Low (100)</source>
        <translation>Low (100)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="87"/>
        <source>Medium (200)</source>
        <translation>Medium (200)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="88"/>
        <source>High (400)</source>
        <translation>High (400)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="114"/>
        <source>Hot zones (colored) show high-density detection areas. Gray zones are below the threshold. Adjust the threshold to control what counts as a hot zone.</source>
        <translation>Hot zones (colored) show high-density detection areas. Gray zones are below the threshold. Adjust the threshold to control what counts as a hot zone.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="126"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="150"/>
        <source>No heatmap data available</source>
        <translation>No heatmap data available</translation>
    </message>
</context>
<context>
    <name>HelpDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="25"/>
        <source>Viewer Help</source>
        <translation>Viewer Help</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="60"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
</context>
<context>
    <name>ImageAdjustmentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="83"/>
        <source>Image Adjustment</source>
        <translation>Image Adjustment</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="96"/>
        <source>Adjustments</source>
        <translation>Adjustments</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="124"/>
        <source>Exposure:</source>
        <translation>Exposure:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="127"/>
        <source>Highlights:</source>
        <translation>Highlights:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="130"/>
        <source>Shadows:</source>
        <translation>Shadows:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="133"/>
        <source>Clarity:</source>
        <translation>Clarity:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="136"/>
        <source>Radius:</source>
        <translation>Radius:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="146"/>
        <source>Reset</source>
        <translation>Reset</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="147"/>
        <source>Apply</source>
        <translation>Apply</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="148"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
</context>
<context>
    <name>ImageAnalysisGuide</name>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="14"/>
        <source>Image Analysis Guide</source>
        <translation>Image Analysis Guide</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="39"/>
        <source>Welcome to ADIAT</source>
        <translation>Welcome to ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="67"/>
        <source>Select a results file from a previous analysis: an ADIAT_Data.xml result, or a batch&apos;s Search Coordinator project (ADIAT_Search_*.xml).</source>
        <translation>Select a results file from a previous analysis: an ADIAT_Data.xml result, or a batch&apos;s Search Coordinator project (ADIAT_Search_*.xml).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="79"/>
        <source>No file selected</source>
        <translation>No file selected</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="94"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="266"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="307"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="123"/>
        <source>What would you like to do?</source>
        <translation>What would you like to do?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="160"/>
        <source>Start New Image Analysis</source>
        <translation>Start New Image Analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="178"/>
        <source>Review Existing Image Analysis</source>
        <translation>Review Existing Image Analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="223"/>
        <source>Select Directories</source>
        <translation>Select Directories</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="245"/>
        <source>Where are the images you want to analyze?</source>
        <translation>Where are the images you want to analyze?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="286"/>
        <source>Where do you want ADIAT to store the output files?</source>
        <translation>Where do you want ADIAT to store the output files?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="348"/>
        <source>Image Capture Information</source>
        <translation>Image Capture Information</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="370"/>
        <source>What drone/camera was used to capture images?</source>
        <translation>What drone/camera was used to capture images?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="400"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>At what above ground level (AGL) altitude was the drone flying?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="413"/>
        <source>Height above the ground being flown over - what the image scale depends on. Over flat terrain this equals the drone&apos;s above-takeoff (ATO) reading; over rising ground it is less.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="468"/>
        <source>ft</source>
        <translation>ft</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="473"/>
        <source>m</source>
        <translation>m</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="511"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation>Estimated Ground Sampling Distance (GSD):</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="532"/>
        <source>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="542"/>
        <source>--</source>
        <translation>--</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="581"/>
        <source>Search Target Size</source>
        <translation>Search Target Size</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="606"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Approximately how large are the objects you&apos;re wanting to identify?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="637"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="676"/>
        <source>ALGORITHM SELECTION GUIDE</source>
        <translation>ALGORITHM SELECTION GUIDE</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="698"/>
        <source>Are you using thermal images?</source>
        <translation>Are you using thermal images?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="743"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1130"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="774"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1115"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="847"/>
        <source>Reset</source>
        <translation>Reset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="147"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="904"/>
        <source>Algorithm Parameters</source>
        <translation>Algorithm Parameters</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="934"/>
        <source>General Settings</source>
        <translation>General Settings</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="956"/>
        <source>What color should be used to highlight Areas of Interest (AOIs)?</source>
        <translation>What color should be used to highlight Areas of Interest (AOIs)?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="976"/>
        <source>Select Color</source>
        <translation>Select Color</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1025"/>
        <source>How many images should be processed at the same time?</source>
        <translation>How many images should be processed at the same time?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1049"/>
        <source>Run Benchmark</source>
        <translation>Run Benchmark</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1072"/>
        <source>What resolution should images be processed at?</source>
        <translation>What resolution should images be processed at?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1100"/>
        <source>Were the images captured in different lighting conditions?</source>
        <translation>Were the images captured in different lighting conditions?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1193"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1205"/>
        <source>Skip this wizard in the future</source>
        <translation>Skip this wizard in the future</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1233"/>
        <source>Back</source>
        <translation>Back</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="261"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="266"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="272"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1245"/>
        <source>Continue</source>
        <translation>Continue</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="102"/>
        <source>ADIAT Image Analysis Guide</source>
        <translation>ADIAT Image Analysis Guide</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="256"/>
        <source>Load Results</source>
        <translation>Load Results</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="269"/>
        <source>Start Processing</source>
        <translation>Start Processing</translation>
    </message>
</context>
<context>
    <name>ImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="78"/>
        <source>Select Drone/Camera</source>
        <translation>Select Drone/Camera</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="82"/>
        <source>No drones available</source>
        <translation>No drones available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="126"/>
        <source>Other</source>
        <translation>Other</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="162"/>
        <source>Error loading drone data</source>
        <translation>Error loading drone data</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="240"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Invalid camera data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="473"/>
        <source>{sensor_name}: Focal length not found in image EXIF</source>
        <translation>{sensor_name}: Focal length not found in image EXIF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="475"/>
        <source>{sensor_name}: Select input directory to extract focal length from images</source>
        <translation>{sensor_name}: Select input directory to extract focal length from images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="482"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Missing camera data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="483"/>
        <source>Unable to calculate GSD. Sensor dimensions found, but:</source>
        <translation>Unable to calculate GSD. Sensor dimensions found, but:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="484"/>
        <source>• Focal length is required (available from image EXIF data)</source>
        <translation>• Focal length is required (available from image EXIF data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="485"/>
        <source>GSD calculation requires an actual image file to extract focal length.</source>
        <translation>GSD calculation requires an actual image file to extract focal length.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="491"/>
        <source>-- (Error)</source>
        <translation>-- (Error)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="523"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="525"/>
        <source>Primary</source>
        <translation>Primary</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="527"/>
        <source>Sensor</source>
        <translation>Sensor</translation>
    </message>
</context>
<context>
    <name>ImageLoadController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="119"/>
        <source>(Image {current} of {total})</source>
        <translation>(Image {current} of {total})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="503"/>
        <source>Error Loading Image</source>
        <translation>Error Loading Image</translation>
    </message>
</context>
<context>
    <name>InputProcessingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="31"/>
        <source>Processing Resolution</source>
        <translation>Processing Resolution</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="36"/>
        <source>Resolution:</source>
        <translation>Resolution:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="41"/>
        <source>Original</source>
        <translation>Original</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="52"/>
        <source>Custom</source>
        <translation>Custom</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="61"/>
        <source>Select a preset resolution for processing. Lower resolutions are faster but less detailed.
&apos;Original&apos; uses the video&apos;s native resolution (no downsampling).
720P (1280x720) provides excellent balance between speed and detection accuracy.
Select &apos;Custom&apos; to manually set width and height.</source>
        <translation>Select a preset resolution for processing. Lower resolutions are faster but less detailed.
&apos;Original&apos; uses the video&apos;s native resolution (no downsampling).
720P (1280x720) provides excellent balance between speed and detection accuracy.
Select &apos;Custom&apos; to manually set width and height.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="71"/>
        <source>Width:</source>
        <translation>Width:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="78"/>
        <source>Custom processing width in pixels (320-3840).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Custom processing width in pixels (320-3840).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="84"/>
        <source>Height:</source>
        <translation>Height:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="91"/>
        <source>Custom processing height in pixels (240-2160).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Custom processing height in pixels (240-2160).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="107"/>
        <source>Performance Options</source>
        <translation>Performance Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="112"/>
        <source>Frame Rate:</source>
        <translation>Frame Rate:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="118"/>
        <source>Source FPS</source>
        <translation>Source FPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="133"/>
        <source>Limit the frame rate for processing.

• Source FPS - Follow the source cadence (live sources may apply a safety cap)
• 30 FPS - Good balance of smoothness and performance
• 25 FPS - Standard for PAL video
• 20 FPS - Reduced CPU usage
• 15 FPS - Lower CPU usage
• 10 FPS - Significant CPU savings
• 5 FPS - Maximum CPU savings, may miss fast objects

Lower frame rates reduce CPU usage but may miss fast-moving objects.
Detections persist between skipped frames for visual continuity.</source>
        <translation>Limit the frame rate for processing.

• Source FPS - Follow the source cadence (live sources may apply a safety cap)
• 30 FPS - Good balance of smoothness and performance
• 25 FPS - Standard for PAL video
• 20 FPS - Reduced CPU usage
• 15 FPS - Lower CPU usage
• 10 FPS - Significant CPU savings
• 5 FPS - Maximum CPU savings, may miss fast objects

Lower frame rates reduce CPU usage but may miss fast-moving objects.
Detections persist between skipped frames for visual continuity.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="148"/>
        <source>Render at Processing Resolution (faster for high-res)</source>
        <translation>Render at Processing Resolution (faster for high-res)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="151"/>
        <source>Renders detection overlays at processing resolution instead of original video resolution.
Significantly faster for high-resolution videos (1080p+) with minimal visual impact.
Example: Processing at 720p but video is 4K - renders at 720p then upscales.
Recommended: ON for high-res videos, OFF for native 720p or lower.</source>
        <translation>Renders detection overlays at processing resolution instead of original video resolution.
Significantly faster for high-resolution videos (1080p+) with minimal visual impact.
Example: Processing at 720p but video is 4K - renders at 720p then upscales.
Recommended: ON for high-res videos, OFF for native 720p or lower.</translation>
    </message>
</context>
<context>
    <name>LoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="12"/>
        <source>Generating Report</source>
        <translation>Generating Report</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="29"/>
        <source>Report generation in progress...</source>
        <translation>Report generation in progress...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="33"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>MRMap</name>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
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
        <translation>Number of segments to divide each image into for MR Map analysis.
Each segment is processed independently for multi-resolution feature detection.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in images with varying features.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Image Segments:</translation>
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
        <translation>Select the number of segments to divide each image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The MR Map (Multi-Resolution Map) algorithm analyzes features at multiple scales:
• 1 segment: Process whole image (best for small images or uniform content)
• More segments: Analyze local regions independently (better for large images)
Higher segment counts improve detection in images with varying features across the scene.
Recommended: 4-9 segments for typical drone imagery.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="67"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="72"/>
        <source>2</source>
        <translation>2</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="77"/>
        <source>4</source>
        <translation>4</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="82"/>
        <source>6</source>
        <translation>6</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="87"/>
        <source>9</source>
        <translation>9</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="92"/>
        <source>16</source>
        <translation>16</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="97"/>
        <source>25</source>
        <translation>25</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="102"/>
        <source>36</source>
        <translation>36</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="131"/>
        <source>Color Space:</source>
        <translation>Color Space:</translation>
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
        <translation>Select the color space for MR Map analysis.
The MR Map algorithm analyzes features in different color representations:
• LAB: Perceptually uniform color space (default, better for color difference analysis)
• RGB: Standard red-green-blue color space (good for general use)
• HSV: Hue-Saturation-Value color space (better for color-based feature detection)
Different color spaces can improve detection depending on the image content.
Recommended: LAB for most cases, HSV for color-rich imagery.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="159"/>
        <source>LAB</source>
        <translation>LAB</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="164"/>
        <source>RGB</source>
        <translation>RGB</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="169"/>
        <source>HSV</source>
        <translation>HSV</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="198"/>
        <source>Window size for multi-resolution analysis.
Determines the spatial scale of features to detect.</source>
        <translation>Window size for multi-resolution analysis.
Determines the spatial scale of features to detect.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="202"/>
        <source>Window Size:</source>
        <translation>Window Size:</translation>
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
        <translation>Set the window size for multi-resolution analysis.
• Range: 1 to 10
• Default: 5
The MR Map algorithm analyzes features at multiple spatial scales using sliding windows:
• Smaller values (1-3): Detect fine details and small features
• Medium values (4-6): Balanced detection (recommended for most cases)
• Larger values (7-10): Detect larger features and patterns
Window size affects the spatial resolution of feature detection.
Larger windows provide more context but may miss small objects.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="254"/>
        <source>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</source>
        <translation>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="258"/>
        <source>Threshold:</source>
        <translation>Threshold:</translation>
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
        <translation>Adjust the detection threshold for MR Map algorithm.
• Range: 1 to 200
• Default: 100
• Slider is inverted: LEFT = higher threshold, RIGHT = lower threshold
The MR Map algorithm detects features at multiple spatial resolutions:
• Lower values (1-50): Very sensitive, detects many features (may include noise)
• Medium values (51-150): Balanced detection (recommended for most cases)
• Higher values (151-200): Less sensitive, only detects prominent features
Threshold controls how distinct a feature must be to be detected.
Note: Slider appearance is inverted - move left for stricter, right for more lenient.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="326"/>
        <source>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</source>
        <translation>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="331"/>
        <source>100</source>
        <translation>100</translation>
    </message>
</context>
<context>
    <name>MRMapController</name>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="40"/>
        <source>Detection Expansion (optional)</source>
        <translation>Detection Expansion (optional)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="48"/>
        <source>Threshold Expansion</source>
        <translation>Threshold Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="50"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="57"/>
        <source>Hue Expansion</source>
        <translation>Hue Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="59"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</translation>
    </message>
</context>
<context>
    <name>MRMapWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="21"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="41"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="56"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="92"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>How aggressively should ADIAT be searching for anomalies?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="105"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Note: A higher setting will find more potential anomalies but may also increase false positives.</translation>
    </message>
</context>
<context>
    <name>MRMapWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="39"/>
        <source>Very 
Conservative</source>
        <translation>Very
Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="40"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="41"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="42"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="43"/>
        <source>Very 
Aggressive</source>
        <translation>Very
Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="60"/>
        <source>Detection Expansion (optional)</source>
        <translation>Detection Expansion (optional)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="67"/>
        <source>Threshold Expansion</source>
        <translation>Threshold Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="69"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="76"/>
        <source>Hue Expansion</source>
        <translation>Hue Expansion</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="78"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="22"/>
        <source>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</source>
        <translation>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="52"/>
        <source>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</source>
        <translation>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="57"/>
        <location filename="../resources/views/images/MainWindow.ui" line="133"/>
        <location filename="../resources/views/images/MainWindow.ui" line="597"/>
        <source> Select</source>
        <translation> Select</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="64"/>
        <location filename="../resources/views/images/MainWindow.ui" line="140"/>
        <source>folder.png</source>
        <translation>folder.png</translation>
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
        <translation>Path to the output folder for saving analysis results.
Click the Select button to browse for a destination folder.
Results include:
• Processed images with detected objects marked
• CSV file with detection coordinates and metadata
• KML file for viewing results in mapping applications
• Additional algorithm-specific output files</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="97"/>
        <source>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</source>
        <translation>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="101"/>
        <source>Input Folder:</source>
        <translation>Input Folder:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="113"/>
        <source>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</source>
        <translation>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="117"/>
        <source>Output Folder:</source>
        <translation>Output Folder:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="129"/>
        <source>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</source>
        <translation>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="152"/>
        <source>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</source>
        <translation>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="209"/>
        <source>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</source>
        <translation>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="213"/>
        <source>Min Object Area (px):</source>
        <translation>Min Object Area (px):</translation>
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
        <translation>Set the minimum object area in pixels for detection filtering.
• Range: 1 to 999 pixels
• Default: 10 pixels
Objects smaller than this threshold will be filtered out and not detected.
• Lower values: Detect smaller objects (may increase false positives)
• Higher values: Only detect larger objects (reduces noise)
Use to filter out small artifacts and noise in detection results.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="269"/>
        <source>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</source>
        <translation>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="273"/>
        <source>Max Object Area (px):</source>
        <translation>Max Object Area (px):</translation>
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
        <translation>Set the maximum object area in pixels for detection filtering.
• Range: 0 to 99999 pixels
• Default: 0 (None - no maximum filter applied)
• Special value: 0 displays as &quot;None&quot;
Objects larger than this threshold will be filtered out and not detected.
• Lower values: Only detect smaller objects
• Higher values: Allow detection of larger objects
• Set to 0 (None): No maximum size filtering
Use to exclude very large false positive detections like shadows or terrain features.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="299"/>
        <source>None</source>
        <translation>None</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="323"/>
        <source>Disable the maximum size filter and allow detections of any size.</source>
        <translation>Disable the maximum size filter and allow detections of any size.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="326"/>
        <source>No max limit</source>
        <translation>No max limit</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="359"/>
        <source>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</source>
        <translation>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="363"/>
        <source>Object Identifer Color:</source>
        <translation>Object Identifer Color:</translation>
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
        <translation>Select the color used to mark detected objects in output images.
• Default: Green (RGB: 0, 255, 0)
Click to open a color picker dialog and choose a different marker color.
The selected color will be used for:
• Drawing circles/rectangles around detected objects
• Highlighting AOI locations on output images
• Creating visual markers in the results viewer
Choose a color that contrasts well with your image content for best visibility.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="395"/>
        <source>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</source>
        <translation>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="399"/>
        <source>Max Processes: </source>
        <translation>Max Processes: </translation>
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
        <translation>Set the maximum number of parallel processes for image analysis.
• Range: 1 to 20 processes
• Default: 10 processes
The application uses multiprocessing to analyze multiple images simultaneously:
• Higher values: Faster processing (uses more CPU cores and memory)
• Lower values: Slower processing (uses fewer system resources)
• Recommended: Set to number of CPU cores or slightly higher
• For systems with limited RAM, reduce this value to prevent memory issues
Each process analyzes one image at a time, so more processes = more parallel image processing.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="446"/>
        <source>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</source>
        <translation>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="450"/>
        <source>Processing Resolution:</source>
        <translation>Processing Resolution:</translation>
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
        <translation>Select processing resolution as percentage of original image size:
• 100%: Original resolution (no scaling, highest quality, slowest)
• 75%: High quality (~56% of pixels, ~1.8x faster)
• 50%: Balanced quality (25% of pixels, ~4x faster) - RECOMMENDED
• 33%: Fast processing (~11% of pixels, ~9x faster)
• 25%: Very fast (6% of pixels, ~16x faster)
• 10%: Ultra fast (1% of pixels, ~100x faster)

Percentage scaling preserves original aspect ratio.
Works with any image size, orientation, or aspect ratio.

Min/Max Area values are always specified in original resolution.
All results are returned in original resolution coordinates.</translation>
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
        <translation>Enable histogram normalization preprocessing on images before detection.
Histogram normalization adjusts image colors to match a reference image:
• Equalizes lighting and color differences across images
• Corrects for varying sun angles, shadows, and atmospheric conditions
• Standardizes color appearance across image set
• Improves consistency of detection results
When enabled, select a reference image with ideal lighting/color conditions.
Useful when processing images taken at different times or under varying conditions.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="540"/>
        <source>Normalize Histograms</source>
        <translation>Normalize Histograms</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="555"/>
        <source>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</source>
        <translation>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="559"/>
        <source>Reference Image:</source>
        <translation>Reference Image:</translation>
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
        <translation>Path to the reference image for histogram normalization.
Click the Select button to choose an image.
Choose an image with ideal lighting and color conditions:
• Clear, well-lit image from your dataset
• Representative of the desired appearance
• Typical lighting conditions for your mission
All other images will be color-adjusted to match this reference.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="592"/>
        <source>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</source>
        <translation>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="604"/>
        <source>image.png</source>
        <translation>image.png</translation>
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
        <translation>Select the detection algorithm to use for image analysis.

Each algorithm has specific strengths and use cases:

• HSV Color Range: Best for detecting specific colored objects
• Color Range (RGB): Alternative color detection using RGB color space
• RX Anomaly: Statistical detection for unusual/anomalous objects
• Thermal Anomaly: Detects temperature anomalies in thermal imagery
• Thermal Range: Temperature-based detection in thermal images
• Matched Filter: Target-based detection using spectral matching
• MR Map: Multi-resolution feature detection at various scales
• AI Person Detector: Machine learning for detecting people

Hover over the algorithm dropdown for detailed descriptions of each algorithm.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="658"/>
        <source>Algorithm:</source>
        <translation>Algorithm:</translation>
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
        <translation>Select the detection algorithm for your image analysis task.
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
• For most accurate people detection: AI Person Detector</translation>
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
        <translation>Start processing images with the selected algorithm.
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
Click Cancel during processing to stop the analysis.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="918"/>
        <source>Start</source>
        <translation>Start</translation>
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
        <translation>Cancel the currently running image analysis process.
Stops processing immediately and safely terminates all worker processes.
Effects of canceling:
• All running analysis processes are stopped
• Partial results are saved up to the cancellation point
• Images already processed will have output files in the output folder
• Processing can be restarted after cancellation
• Returns to the ready state
Use when you need to stop processing to adjust settings or fix issues.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="963"/>
        <source> Cancel</source>
        <translation> Cancel</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="970"/>
        <source>cancel.png</source>
        <translation>cancel.png</translation>
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
        <translation>Open the Results Viewer to review detection results.
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
Use to review, verify, and export analysis results.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1782"/>
        <location filename="../resources/views/images/MainWindow.ui" line="1018"/>
        <source> View Results</source>
        <translation> View Results</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1028"/>
        <source>search</source>
        <translation>search</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1085"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1098"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1111"/>
        <source>Image Analysis Wizard</source>
        <translation>Image Analysis Wizard</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1114"/>
        <source>Launch the Image Analysis Guide wizard to configure analysis settings.
Opens a step-by-step wizard to:
• Select input and output directories
• Configure image capture settings (drone, altitude, GSD)
• Set target object size
• Choose detection algorithm
• Configure algorithm-specific parameters
• Set general processing options
The wizard will close this window and open with all settings pre-populated.</source>
        <translation>Launch the Image Analysis Guide wizard to configure analysis settings.
Opens a step-by-step wizard to:
• Select input and output directories
• Configure image capture settings (drone, altitude, GSD)
• Set target object size
• Choose detection algorithm
• Configure algorithm-specific parameters
• Set general processing options
The wizard will close this window and open with all settings pre-populated.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1132"/>
        <source>Load Results File</source>
        <translation>Load Results File</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1135"/>
        <source>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</source>
        <translation>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1148"/>
        <source>Load Results Folder</source>
        <translation>Load Results Folder</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1151"/>
        <source>Scan a folder recursively for ADIAT_DATA.XML files.
Displays all found results in a dialog for easy browsing.
Use this to quickly find and open results from multiple analysis sessions.</source>
        <translation>Scan a folder recursively for ADIAT_DATA.XML files.
Displays all found results in a dialog for easy browsing.
Use this to quickly find and open results from multiple analysis sessions.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1163"/>
        <source>Preferences</source>
        <translation>Preferences</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1166"/>
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
        <translation>Open the Preferences dialog to configure application settings.
Adjust global settings including:
• Application theme (Light/Dark)
• Max AOI warning threshold
• AOI circle radius for clustering
• Coordinate system format (Lat/Long, UTM)
• Temperature unit (Fahrenheit/Celsius)
• Distance unit (Meters/Feet)
• Drone sensor configuration file
All changes are saved automatically.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1185"/>
        <source>Video Parser</source>
        <translation>Video Parser</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1188"/>
        <source>Open the Video Parser utility to extract frames from video files.
Convert video footage into individual frame images for analysis.
Features:
• Extract frames at specified time intervals
• Optional SRT file support for GPS metadata
• Supports common video formats (MP4, AVI, MOV, etc.)
• Embeds location data into extracted frames
Use to prepare video footage for image-based analysis.</source>
        <translation>Open the Video Parser utility to extract frames from video files.
Convert video footage into individual frame images for analysis.
Features:
• Extract frames at specified time intervals
• Optional SRT file support for GPS metadata
• Supports common video formats (MP4, AVI, MOV, etc.)
• Embeds location data into extracted frames
Use to prepare video footage for image-based analysis.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1205"/>
        <source>Streaming Detector</source>
        <translation>Streaming Detector</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1208"/>
        <source>Switch to the Streaming Detector</source>
        <translation>Switch to the Streaming Detector</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1218"/>
        <source>Flight Viewer</source>
        <translation>Flight Viewer</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1221"/>
        <source>Open the Flight Viewer to pair with ADIAT Mobile drone controllers and watch their live feeds.</source>
        <translation>Open the Flight Viewer to pair with ADIAT Mobile drone controllers and watch their live feeds.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1231"/>
        <source>Real-Time Anomaly Detection</source>
        <translation>Real-Time Anomaly Detection</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1234"/>
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
        <translation>Open the Real-Time Anomaly Detection window for advanced live analysis.
Combines multiple detection algorithms for comprehensive real-time anomaly detection.
Features:
• Motion detection with background subtraction
• Color quantization anomaly detection
• Advanced streaming video processing
• Detection fusion and temporal filtering
• Real-time performance optimization
• Multi-threaded processing for better performance
• Enhanced detection accuracy through algorithm combination
Designed for detecting unusual objects, movement, and colors in real-time video streams.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1254"/>
        <source>Search Coordinator</source>
        <translation>Search Coordinator</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1257"/>
        <source>Open the Search Coordinator window for managing multi-batch review projects.
Features:
• Create and manage search projects with multiple batches
• Track reviewer progress across multiple image sets
• Consolidate review results from multiple reviewers
• View dashboard with search status and metrics
• Export consolidated results
• Manage batch assignments and reviewer coordination
Ideal for large-scale searches with multiple reviewers and image batches.</source>
        <translation>Open the Search Coordinator window for managing multi-batch review projects.
Features:
• Create and manage search projects with multiple batches
• Track reviewer progress across multiple image sets
• Consolidate review results from multiple reviewers
• View dashboard with search status and metrics
• Export consolidated results
• Manage batch assignments and reviewer coordination
Ideal for large-scale searches with multiple reviewers and image batches.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1273"/>
        <source>Ctrl+Shift+C</source>
        <translation>Ctrl+Shift+C</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1278"/>
        <source>Manual</source>
        <translation>Manual</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1281"/>
        <source>Open the online help documentation in your web browser.
Access comprehensive documentation, tutorials, and user guides.
Provides detailed information on all features and algorithms.</source>
        <translation>Open the online help documentation in your web browser.
Access comprehensive documentation, tutorials, and user guides.
Provides detailed information on all features and algorithms.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1293"/>
        <source>Check for Updates</source>
        <translation>Check for Updates</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1296"/>
        <source>Check the update feed for a newer ADIAT installer.
If an update is available, you can download and launch the installer from here.</source>
        <translation>Check the update feed for a newer ADIAT installer.
If an update is available, you can download and launch the installer from here.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1307"/>
        <source>Community Forum</source>
        <translation>Community Forum</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1310"/>
        <source>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</source>
        <translation>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1322"/>
        <source>YouTube Channel</source>
        <translation>YouTube Channel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="89"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="288"/>
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

TEMPERATURE RESIDUAL ANOMALY: Detects local delta-T outliers using radiometric residuals
  • Best for: Isolating rare hot/cold thermal signatures in mixed backgrounds
  • Limitation: Requires radiometric thermal data, can be sensitive to threshold choice

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
        <translation>Select the detection algorithm for your image analysis task:

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

TEMPERATURE RESIDUAL ANOMALY: Detects local delta-T outliers using radiometric residuals
  • Best for: Isolating rare hot/cold thermal signatures in mixed backgrounds
  • Limitation: Requires radiometric thermal data, can be sensitive to threshold choice

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
  • Limitation: Only detects people, slower processing</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="384"/>
        <source>Select AOI Highlight Color</source>
        <translation>Select AOI Highlight Color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="398"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="416"/>
        <source>Select Directory</source>
        <translation>Select Directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="433"/>
        <source>Select a Reference Image</source>
        <translation>Select a Reference Image</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="435"/>
        <source>Images (*.png *.jpg)</source>
        <translation>Images (*.png *.jpg)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="496"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="528"/>
        <source>Value Adjusted</source>
        <translation>Value Adjusted</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="498"/>
        <source>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</source>
        <translation>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="530"/>
        <source>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</source>
        <translation>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="644"/>
        <source>Please set the input and output directories.</source>
        <translation>Please set the input and output directories.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="651"/>
        <source>--- Starting image processing ---</source>
        <translation>--- Starting image processing ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="885"/>
        <source>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</source>
        <translation>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="908"/>
        <source>Area of Interest Limit ({limit}) exceeded. Continue?</source>
        <translation>Area of Interest Limit ({limit}) exceeded. Continue?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="911"/>
        <source>Area of Interest Limit Exceeded</source>
        <translation>Area of Interest Limit Exceeded</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="963"/>
        <source>--- Image Processing Completed ---</source>
        <translation>--- Image Processing Completed ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="964"/>
        <source>Image processing complete</source>
        <translation>Image processing complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="967"/>
        <source>{count} images with areas of interest identified</source>
        <translation>{count} images with areas of interest identified</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="973"/>
        <source>No areas of interest identified</source>
        <translation>No areas of interest identified</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1057"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1599"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1622"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1652"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1668"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1684"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1700"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1077"/>
        <source>Open Recent Results</source>
        <translation>Open Recent Results</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1121"/>
        <source>(no results opened yet)</source>
        <translation>(no results opened yet)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1137"/>
        <source>This results file no longer exists:
{path}</source>
        <translation>This results file no longer exists:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1154"/>
        <source>Select File</source>
        <translation>Select File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1154"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>XML Files (*.xml);;All Files (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1175"/>
        <source>Select Results Folder</source>
        <translation>Select Results Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1208"/>
        <source>Failed to scan folder: {error}</source>
        <translation>Failed to scan folder: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1230"/>
        <source>No Results Found</source>
        <translation>No Results Found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1231"/>
        <source>No ADIAT_DATA.XML files were found in the selected folder.</source>
        <translation>No ADIAT_DATA.XML files were found in the selected folder.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1248"/>
        <source>Failed to display results: {error}</source>
        <translation>Failed to display results: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1259"/>
        <source>Scan failed: {error}</source>
        <translation>Scan failed: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1302"/>
        <source>Failed to open viewer: {error}</source>
        <translation>Failed to open viewer: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1333"/>
        <source>The selected file is not a valid XML file: {path}</source>
        <translation>The selected file is not a valid XML file: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1545"/>
        <source>Error Loading Results</source>
        <translation>Error Loading Results</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1546"/>
        <source>Failed to load results file:
{error}</source>
        <translation>Failed to load results file:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1600"/>
        <source>Failed to open Streaming Detector:
{error}</source>
        <translation>Failed to open Streaming Detector:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1623"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Failed to open Flight Viewer:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1653"/>
        <source>Failed to open Search Coordinator:
{error}</source>
        <translation>Failed to open Search Coordinator:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1669"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Failed to open Help documentation:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1685"/>
        <source>Failed to open Community Help:
{error}</source>
        <translation>Failed to open Community Help:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1701"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Failed to open YouTube Channel:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1776"/>
        <source> Open Search Coordinator</source>
        <translation> Open Search Coordinator</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1778"/>
        <source>Open the Search Coordinator to review every batch in this run.</source>
        <translation>Open the Search Coordinator to review every batch in this run.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1784"/>
        <source>Open the Results Viewer to review detection results.</source>
        <translation>Open the Results Viewer to review detection results.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1871"/>
        <source>Invalid Value</source>
        <translation>Invalid Value</translation>
    </message>
</context>
<context>
    <name>MapDock</name>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="54"/>
        <source>Map</source>
        <translation>Map</translation>
    </message>
</context>
<context>
    <name>MapExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="34"/>
        <source>Map Export Options</source>
        <translation>Map Export Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="45"/>
        <source>Configure Map Export</source>
        <translation>Configure Map Export</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="53"/>
        <source>Export Type</source>
        <translation>Export Type</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="56"/>
        <source>KML File</source>
        <translation>KML File</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="58"/>
        <source>Export to a KML file for use in Google Earth, etc.</source>
        <translation>Export to a KML file for use in Google Earth, etc.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="60"/>
        <source>CalTopo</source>
        <translation>CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="61"/>
        <source>Export directly to a CalTopo map</source>
        <translation>Export directly to a CalTopo map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="73"/>
        <source>Data to Include</source>
        <translation>Data to Include</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="76"/>
        <source>Drone/Image Locations</source>
        <translation>Drone/Image Locations</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="78"/>
        <source>Include markers for each drone image location</source>
        <translation>Include markers for each drone image location</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="80"/>
        <source>Flagged Areas of Interest</source>
        <translation>Flagged Areas of Interest</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="82"/>
        <source>Include markers for flagged AOIs</source>
        <translation>Include markers for flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="84"/>
        <source>Coverage Area</source>
        <translation>Coverage Area</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="86"/>
        <source>Include polygon(s) showing the geographic coverage extent</source>
        <translation>Include polygon(s) showing the geographic coverage extent</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="88"/>
        <source>Include images without flagged AOIs</source>
        <translation>Include images without flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="90"/>
        <source>If unchecked, only export locations for images that have flagged AOIs</source>
        <translation>If unchecked, only export locations for images that have flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="101"/>
        <source>Probability of Detection (POD)</source>
        <translation>Probability of Detection (POD)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="104"/>
        <source>POD coverage heatmap (terrain-aware)</source>
        <translation>POD coverage heatmap (terrain-aware)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="107"/>
        <source>Compute a terrain and canopy aware probability-of-detection raster for the whole mission (all non-hidden images, independent of the selections above). KML exports embed the heatmap in the KML/KMZ as an image overlay; the GeoTIFF products (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) are also written — the GeoTIFF can be imported into CalTopo Map Sheets. May take several minutes.</source>
        <translation>Compute a terrain and canopy aware probability-of-detection raster for the whole mission (all non-hidden images, independent of the selections above). KML exports embed the heatmap in the KML/KMZ as an image overlay; the GeoTIFF products (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) are also written — the GeoTIFF can be imported into CalTopo Map Sheets. May take several minutes.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="114"/>
        <source>Show on map when complete</source>
        <translation>Show on map when complete</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="125"/>
        <source>CalTopo Options</source>
        <translation>CalTopo Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="128"/>
        <source>Include Images</source>
        <translation>Include Images</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="130"/>
        <source>Upload photos to CalTopo markers (CalTopo only)</source>
        <translation>Upload photos to CalTopo markers (CalTopo only)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="135"/>
        <source>Photo for flagged AOIs:</source>
        <translation>Photo for flagged AOIs:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="137"/>
        <source>Large Image (with zoom insets)</source>
        <translation>Large Image (with zoom insets)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="138"/>
        <source>AOI Thumbnail Only</source>
        <translation>AOI Thumbnail Only</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="139"/>
        <source>Both</source>
        <translation>Both</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="142"/>
        <source>Large Image uploads the same multi-zoom composite used in the PDF report
(full image with 3x and 6x insets). AOI Thumbnail uploads a zoomed crop
centered on the detection. Both uploads each.</source>
        <translation>Large Image uploads the same multi-zoom composite used in the PDF report
(full image with 3x and 6x insets). AOI Thumbnail uploads a zoomed crop
centered on the detection. Both uploads each.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="173"/>
        <source>Export</source>
        <translation>Export</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="177"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>MatchedFilter</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="42"/>
        <source>Add a new color signature for matched filter detection. Each color can have its own threshold value.</source>
        <translation>Add a new color signature for matched filter detection. Each color can have its own threshold value.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="45"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="52"/>
        <source>color.png</source>
        <translation>color.png</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="83"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the thresholds before processing.</source>
        <translation>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the thresholds before processing.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="88"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="95"/>
        <source>eye.png</source>
        <translation>eye.png</translation>
    </message>
</context>
<context>
    <name>MatchedFilterController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="42"/>
        <source>No Colors Selected</source>
        <translation>No Colors Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="299"/>
        <source>Please add at least one color to detect.</source>
        <translation>Please add at least one color to detect.</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilterWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Add Color</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="47"/>
        <source>No Targets Selected</source>
        <translation>No Targets Selected</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="57"/>
        <source>View Range</source>
        <translation>View Range</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="218"/>
        <source>Please add at least one target color to detect.</source>
        <translation>Please add at least one target color to detect.</translation>
    </message>
</context>
<context>
    <name>MeasureDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="71"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Distance</source>
        <translation>Measure Distance</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="85"/>
        <source>Measure Shadow</source>
        <translation>Measure Shadow</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="87"/>
        <source>When checked, the two clicks estimate the height of a vertical object from its shadow. Click the base of the object first, then the tip of its shadow.</source>
        <translation>When checked, the two clicks estimate the height of a vertical object from its shadow. Click the base of the object first, then the tip of its shadow.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="94"/>
        <source>Ground Sample Distance</source>
        <translation>Ground Sample Distance</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="97"/>
        <source>GSD:</source>
        <translation>GSD:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="99"/>
        <source>Enter GSD value</source>
        <translation>Enter GSD value</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="103"/>
        <source>cm/px</source>
        <translation>cm/px</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="111"/>
        <source>Measurement</source>
        <translation>Measurement</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="114"/>
        <source>Distance:</source>
        <translation>Distance:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="115"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="126"/>
        <source>--</source>
        <translation>--</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="124"/>
        <source>Shadow Height Estimate</source>
        <translation>Shadow Height Estimate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="135"/>
        <source>Use Anyway</source>
        <translation>Use Anyway</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="137"/>
        <source>Force the estimate with the current base/tip clicks even though the drawn line doesn&apos;t match the expected shadow direction. Use only when you&apos;re confident the geometry is correct.</source>
        <translation>Force the estimate with the current base/tip clicks even though the drawn line doesn&apos;t match the expected shadow direction. Use only when you&apos;re confident the geometry is correct.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="181"/>
        <source>Click the BASE of the object first, then the TIP of its shadow.</source>
        <translation>Click the BASE of the object first, then the TIP of its shadow.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="185"/>
        <source>Click on the image to place the first point,
then click again to place the second point.</source>
        <translation>Click on the image to place the first point,
then click again to place the second point.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="158"/>
        <source>Clear</source>
        <translation>Clear</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="160"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Shadow Height</source>
        <translation>Measure Shadow Height</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="415"/>
        <source>Image metadata unavailable</source>
        <translation>Image metadata unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="553"/>
        <source>Rejected</source>
        <translation>Rejected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="577"/>
        <source>No GSD value</source>
        <translation>No GSD value</translation>
    </message>
</context>
<context>
    <name>MediaSelector</name>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool (ADIAT)</source>
        <translation>Automated Drone Image Analysis Tool (ADIAT)</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="31"/>
        <source>What would you like to do?</source>
        <translation>What would you like to do?</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="169"/>
        <source>Image Analysis</source>
        <translation>Image Analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="83"/>
        <source>Open a completed analysis for review: scan a folder for results or reopen a recent one.</source>
        <translation>Open a completed analysis for review: scan a folder for results or reopen a recent one.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="89"/>
        <source>Review Results</source>
        <translation>Review Results</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="252"/>
        <source>Stream Analysis</source>
        <translation>Stream Analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="329"/>
        <source>Pair with ADIAT Mobile drone controllers to receive their live camera feeds with detections.</source>
        <translation>Pair with ADIAT Mobile drone controllers to receive their live camera feeds with detections.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="246"/>
        <source>RTMP, Video Files, HDMI Capture</source>
        <translation>RTMP, Video Files, HDMI Capture</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="335"/>
        <source>Flight Viewer</source>
        <translation>Flight Viewer</translation>
    </message>
</context>
<context>
    <name>MissionGalleryContents</name>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="32"/>
        <source>Filters</source>
        <translation>Filters</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="38"/>
        <source>Feed</source>
        <translation>Feed</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="48"/>
        <source>Detector</source>
        <translation>Detector</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="58"/>
        <source>Min score</source>
        <translation>Min score</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="99"/>
        <source>0 detections</source>
        <translation>0 detections</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="119"/>
        <source>Export</source>
        <translation>Export</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="122"/>
        <source>Export filtered detections to the standard ADIAT image-mode gallery format.</source>
        <translation>Export filtered detections to the standard ADIAT image-mode gallery format.</translation>
    </message>
</context>
<context>
    <name>MissionGalleryDock</name>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="28"/>
        <source>Mission Gallery</source>
        <translation>Mission Gallery</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="53"/>
        <source>All feeds</source>
        <translation>All feeds</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="59"/>
        <source>All detectors</source>
        <translation>All detectors</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="126"/>
        <source>0 detections</source>
        <translation>0 detections</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="151"/>
        <source>{n} detections</source>
        <translation>{n} detections</translation>
    </message>
</context>
<context>
    <name>NeighborGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="172"/>
        <source>Unknown</source>
        <translation type="unfinished">Unknown</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="175"/>
        <source> (Current)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>NeighborSearchWorker</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="68"/>
        <source>Locating the selected AOI...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PDFExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="151"/>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="160"/>
        <source>No Images to Export</source>
        <translation>No Images to Export</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="153"/>
        <source>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</source>
        <translation>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="162"/>
        <source>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</source>
        <translation>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="172"/>
        <source>Save PDF File</source>
        <translation>Save PDF File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="174"/>
        <source>PDF files (*.pdf)</source>
        <translation>PDF files (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="216"/>
        <source>Generating PDF Report</source>
        <translation>Generating PDF Report</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="219"/>
        <source>Generating PDF Report...</source>
        <translation>Generating PDF Report...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="260"/>
        <source>Failed to generate PDF file: {error}</source>
        <translation>Failed to generate PDF file: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="276"/>
        <source>Success</source>
        <translation>Success</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="277"/>
        <source>PDF report generated successfully!</source>
        <translation>PDF report generated successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="294"/>
        <source>PDF generation failed: {error}</source>
        <translation>PDF generation failed: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="308"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
</context>
<context>
    <name>PDFExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="27"/>
        <source>PDF Export Settings</source>
        <translation>PDF Export Settings</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="35"/>
        <source>Enter the following information for the PDF report:</source>
        <translation>Enter the following information for the PDF report:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="44"/>
        <source>Enter organization name</source>
        <translation>Enter organization name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="45"/>
        <source>Organization:</source>
        <translation>Organization:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="49"/>
        <source>Enter search name</source>
        <translation>Enter search name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="50"/>
        <source>Search Name:</source>
        <translation>Search Name:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="55"/>
        <source>Export Options:</source>
        <translation>Export Options:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="60"/>
        <source>Include images without flagged AOIs</source>
        <translation>Include images without flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="62"/>
        <source>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</source>
        <translation>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="69"/>
        <source>Map Tiles:</source>
        <translation>Map Tiles:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="71"/>
        <source>Map</source>
        <translation>Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="72"/>
        <source>Satellite</source>
        <translation>Satellite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="73"/>
        <source>Choose the background tiles for the PDF overview map.</source>
        <translation>Choose the background tiles for the PDF overview map.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="80"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="82"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>PathValidationController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="515"/>
        <source>
  ... and {count} more</source>
        <translation>
  ... and {count} more</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="131"/>
        <source>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</source>
        <translation>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="129"/>
        <source>Source Images Not Found</source>
        <translation>Source Images Not Found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="135"/>
        <source>Select Source Images Folder</source>
        <translation>Select Source Images Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="136"/>
        <source>Some Images Still Missing</source>
        <translation>Some Images Still Missing</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="165"/>
        <source>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</source>
        <translation>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="163"/>
        <source>Detection Masks Not Found</source>
        <translation>Detection Masks Not Found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="138"/>
        <source>Found {found} of {total} images.

Still missing:
{missing}</source>
        <translation>Found {found} of {total} images.

Still missing:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="142"/>
        <source>None of the {total} missing images were found in that folder (including its subfolders).

Expected to find files named:
{missing}</source>
        <translation>None of the {total} missing images were found in that folder (including its subfolders).

Expected to find files named:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="169"/>
        <source>Select Masks Folder</source>
        <translation>Select Masks Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="170"/>
        <source>Some Masks Still Missing</source>
        <translation>Some Masks Still Missing</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="172"/>
        <source>Found {found} of {total} masks.

Still missing:
{missing}</source>
        <translation>Found {found} of {total} masks.

Still missing:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="176"/>
        <source>None of the {total} missing masks were found in that folder (including its subfolders).

Expected to find files named:
{missing}</source>
        <translation>None of the {total} missing masks were found in that folder (including its subfolders).

Expected to find files named:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="421"/>
        <source>Choose Another Folder</source>
        <translation>Choose Another Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="428"/>
        <source>Continue Anyway</source>
        <translation>Continue Anyway</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="410"/>
        <source>

{count} of these appear more than once in that folder, so which capture they belong to cannot be determined:
{files}

Choose the specific flight/sortie folder rather than a folder containing several of them.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PersonReferenceDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="312"/>
        <source>Person Size Reference</source>
        <translation>Person Size Reference</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="319"/>
        <source>Reference Person</source>
        <translation>Reference Person</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="338"/>
        <source>Standing</source>
        <translation>Standing</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="340"/>
        <source>Lying down</source>
        <translation>Lying down</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="342"/>
        <source>Sitting</source>
        <translation>Sitting</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="351"/>
        <source>Show shadows (from capture time)</source>
        <translation>Show shadows (from capture time)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="354"/>
        <source>Use terrain elevation (DEM)</source>
        <translation>Use terrain elevation (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="363"/>
        <source>Rotate the person on the ground to line it up with an object</source>
        <translation>Rotate the person on the ground to line it up with an object</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="368"/>
        <source>Click to choose overlay color</source>
        <translation>Click to choose overlay color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="376"/>
        <source>Size:</source>
        <translation>Size:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="377"/>
        <source>Show:</source>
        <translation>Show:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="378"/>
        <source>Rotation:</source>
        <translation>Rotation:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="381"/>
        <source>Color:</source>
        <translation>Color:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="397"/>
        <source>Adjust camera clock...</source>
        <translation>Adjust camera clock...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="402"/>
        <source>Flight track log...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="404"/>
        <source>Attach a ForeFlight track log CSV to stamp true aircraft attitude (bank/pitch) and GPS-accurate capture times onto these images.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="411"/>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1364"/>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1371"/>
        <source>Trace shadow...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="413"/>
        <source>Derive the time of day from a real shadow: click the base of an object casting a shadow (rock, tree, post), then the tip of its shadow. The solved time drives the rendered shadows.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="419"/>
        <source>Drag the white handle to position the reference person. Silhouettes are drawn at true ground scale for this image&apos;s altitude and camera angle.</source>
        <translation>Drag the white handle to position the reference person. Silhouettes are drawn at true ground scale for this image&apos;s altitude and camera angle.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="427"/>
        <source>Recenter</source>
        <translation>Recenter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="429"/>
        <source>Bring the reference person to the center of the current view</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="430"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="497"/>
        <source>No camera clock fault or applied correction was found for this folder.</source>
        <translation>No camera clock fault or applied correction was found for this folder.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="596"/>
        <source>Select ForeFlight track log</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="598"/>
        <source>Track logs (*.csv);;All files (*.*)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="653"/>
        <source>Perspective overlay unavailable: this image is missing the altitude or lens metadata needed to project a person.</source>
        <translation>Perspective overlay unavailable: this image is missing the altitude or lens metadata needed to project a person.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="709"/>
        <source>Zoomed to the reference person: at this altitude a person spans only a few pixels.</source>
        <translation>Zoomed to the reference person: at this altitude a person spans only a few pixels.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="753"/>
        <source>no image loaded</source>
        <translation>no image loaded</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="758"/>
        <source>image metadata could not be read</source>
        <translation>image metadata could not be read</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="762"/>
        <source>image has no GPS coordinates</source>
        <translation>image has no GPS coordinates</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="774"/>
        <source>capture time / timezone not in metadata</source>
        <translation>capture time / timezone not in metadata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="785"/>
        <source>sun position could not be computed</source>
        <translation>sun position could not be computed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="799"/>
        <source>Sun at capture: {elev:.0f}° above horizon, azimuth {az:.0f}°.</source>
        <translation>Sun at capture: {elev:.0f}° above horizon, azimuth {az:.0f}°.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="804"/>
        <source>Capture time zone estimated from GPS location.</source>
        <translation>Capture time zone estimated from GPS location.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="807"/>
        <source>Using repaired capture time (camera clock fault).</source>
        <translation>Using repaired capture time (camera clock fault).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="810"/>
        <source>Time of day derived from the traced shadow.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="815"/>
        <source>the sun was below the horizon at capture</source>
        <translation>the sun was below the horizon at capture</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="817"/>
        <source>sun position unavailable</source>
        <translation>sun position unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="818"/>
        <source>Shadow unavailable: {reason}.</source>
        <translation>Shadow unavailable: {reason}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="917"/>
        <source>Place the person and shadow on the DEM terrain surface</source>
        <translation>Place the person and shadow on the DEM terrain surface</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="921"/>
        <source>Terrain (DEM) data is not available for this image</source>
        <translation>Terrain (DEM) data is not available for this image</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1181"/>
        <source>Choose Overlay Color</source>
        <translation>Choose Overlay Color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1339"/>
        <source>Cancel trace</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1341"/>
        <source>Shadow trace: on the image, click the BASE of an object casting a shadow (rock, tree, post), then click the TIP of its shadow.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1382"/>
        <source>Shadow trace: now click the TIP of the shadow.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1467"/>
        <source>Shadow trace: the traced points could not be projected to the ground - try two points further apart.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1473"/>
        <source>Shadow trace: the image is missing the capture date or GPS position needed to solve the time.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1488"/>
        <source>Shadow trace: no daylight sun position matches that direction on the capture date. Check the traced direction (base first, then shadow tip).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1493"/>
        <source>Clear traced time</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1495"/>
        <source>Time solved from the traced shadow: {time} (sun azimuth {az:.0f}°, {elev:.0f}° above horizon).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1502"/>
        <source>The traced direction looked reversed and was interpreted tip-to-base.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="1506"/>
        <source>Note: another time of day matches this direction almost as well.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>PlaybackControlBar</name>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="58"/>
        <source>Play/Pause (Space)</source>
        <translation>Play/Pause (Space)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="71"/>
        <source>Seek through video</source>
        <translation>Seek through video</translation>
    </message>
</context>
<context>
    <name>Preferences</name>
    <message>
        <location filename="../resources/views/Preferences.ui" line="14"/>
        <source>Preferences</source>
        <translation>Preferences</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="55"/>
        <source>Select the application theme appearance.
Changes the overall color scheme and visual style.</source>
        <translation>Select the application theme appearance.
Changes the overall color scheme and visual style.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="59"/>
        <source>Theme:</source>
        <translation>Theme:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="71"/>
        <source>Choose the application theme:
• Light: Bright theme with light backgrounds and dark text
• Dark: Dark theme with dark backgrounds and light text
Changes apply immediately to all windows.</source>
        <translation>Choose the application theme:
• Light: Bright theme with light backgrounds and dark text
• Dark: Dark theme with dark backgrounds and light text
Changes apply immediately to all windows.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="78"/>
        <source>Light</source>
        <translation>Light</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="83"/>
        <source>Dark</source>
        <translation>Dark</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="114"/>
        <source>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</source>
        <translation>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="118"/>
        <source>Max Areas of Interest: </source>
        <translation>Max Areas of Interest: </translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="130"/>
        <source>Set the warning threshold for total AOIs detected during processing.
• Range: 0 to 1000
• Default: 100
When this number of AOIs is detected across all images:
• UI displays a warning message
• User can cancel processing, adjust settings, and rerun
• If no action taken, detection continues automatically
Use lower values to catch high detection counts early.</source>
        <translation>Set the warning threshold for total AOIs detected during processing.
• Range: 0 to 1000
• Default: 100
When this number of AOIs is detected across all images:
• UI displays a warning message
• User can cancel processing, adjust settings, and rerun
• If no action taken, detection continues automatically
Use lower values to catch high detection counts early.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="161"/>
        <source>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</source>
        <translation>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="165"/>
        <source>Area of Interest Circle Radius(px):</source>
        <translation>Area of Interest Circle Radius(px):</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="177"/>
        <source>Set the radius for combining nearby AOIs during detection.
• Range: 0 to 100 pixels
• Default: 25 pixels
When AOIs are within this radius of each other:
• They are combined into a single AOI
• Process repeats until no neighbors remain within radius
• Larger values: Combines more distant detections (fewer total AOIs)
• Smaller values: Keeps detections separate (more individual AOIs)
Use to consolidate clustered detections into single objects.</source>
        <translation>Set the radius for combining nearby AOIs during detection.
• Range: 0 to 100 pixels
• Default: 25 pixels
When AOIs are within this radius of each other:
• They are combined into a single AOI
• Process repeats until no neighbors remain within radius
• Larger values: Combines more distant detections (fewer total AOIs)
• Smaller values: Keeps detections separate (more individual AOIs)
Use to consolidate clustered detections into single objects.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="209"/>
        <source>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</source>
        <translation>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="213"/>
        <source>Coordinate System:</source>
        <translation>Coordinate System:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="225"/>
        <source>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</source>
        <translation>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="233"/>
        <source>Lat/Long - Decimal Degrees</source>
        <translation>Lat/Long - Decimal Degrees</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="238"/>
        <source>Lat/Long - Degrees, Minutes, Seconds</source>
        <translation>Lat/Long - Degrees, Minutes, Seconds</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="243"/>
        <source>UTM</source>
        <translation>UTM</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="262"/>
        <source>Unit for displaying temperature measurements from thermal imagery.
Used when analyzing thermal images from thermal cameras.</source>
        <translation>Unit for displaying temperature measurements from thermal imagery.
Used when analyzing thermal images from thermal cameras.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="266"/>
        <source>Temperature Unit:</source>
        <translation>Temperature Unit:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="278"/>
        <source>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</source>
        <translation>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="287"/>
        <source>Fahrenheit</source>
        <translation>Fahrenheit</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="292"/>
        <source>Celsius</source>
        <translation>Celsius</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="311"/>
        <source>Unit for displaying distance and altitude measurements.
Used for drone altitude, object distances, and spatial calculations.</source>
        <translation>Unit for displaying distance and altitude measurements.
Used for drone altitude, object distances, and spatial calculations.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="315"/>
        <source>Distance Unit:</source>
        <translation>Distance Unit:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="327"/>
        <source>Select the distance unit for measurements:
• Meters (m): Metric distance unit (international standard)
  - 1 meter = 3.281 feet
  - Used for altitude, GSD, and distance calculations
• Feet (ft): Imperial distance unit (US standard)
  - 1 foot = 0.3048 meters
  - Common in US aviation and surveying
Applies to altitude displays, GSD calculations, and distance measurements.</source>
        <translation>Select the distance unit for measurements:
• Meters (m): Metric distance unit (international standard)
  - 1 meter = 3.281 feet
  - Used for altitude, GSD, and distance calculations
• Feet (ft): Imperial distance unit (US standard)
  - 1 foot = 0.3048 meters
  - Common in US aviation and surveying
Applies to altitude displays, GSD calculations, and distance measurements.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="338"/>
        <source>Meters</source>
        <translation>Meters</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="343"/>
        <source>Feet</source>
        <translation>Feet</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="362"/>
        <source>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</source>
        <translation>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="366"/>
        <source>Offline Only Mode:</source>
        <translation>Offline Only Mode:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="378"/>
        <source>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</source>
        <translation>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="381"/>
        <location filename="../resources/views/Preferences.ui" line="422"/>
        <location filename="../resources/views/Preferences.ui" line="463"/>
        <source>Enable</source>
        <translation>Enable</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="399"/>
        <source>Use terrain elevation data (DEM/DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online or local elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</source>
        <translation>Use terrain elevation data (DEM/DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online or local elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="416"/>
        <source>Enable terrain-corrected AOI positioning using DEM/DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</source>
        <translation>Enable terrain-corrected AOI positioning using DEM/DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="440"/>
        <source>Keep elevation data for the search area on hand, for whichever elevation source is selected above.
Downloads run while an analysis is working, when a results viewer opens and before an export - whichever comes first - so the data is already local by the time AOI coordinates are calculated.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="444"/>
        <source>Auto-Download Elevation Data:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="456"/>
        <source>Fetch elevation data for the area the images cover, before it is needed.
• AWS Terrain Tiles (the default source): a few tiles, well under a megabyte
• USGS 3DEP: about 4 MB per square kilometre, United States only
• Skipped, with a note, above the size limit, in Offline Only mode, with no connectivity, or when the area is already covered
• Never required: Download Coverage Data in Preferences and on the GPS Map still does it on demand, including for offline import</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="404"/>
        <source>Use Terrain Elevation:</source>
        <translation>Use Terrain Elevation:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="475"/>
        <source>Size limit (MB):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="487"/>
        <source>An automatic download larger than this is skipped and noted in the message pane, so an unexpectedly large search area never consumes a field connection unannounced.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="530"/>
        <source>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</source>
        <translation>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="534"/>
        <source>Terrain Cache:</source>
        <translation>Terrain Cache:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="546"/>
        <source>0 tiles (0 MB)</source>
        <translation>0 tiles (0 MB)</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="571"/>
        <source>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="575"/>
        <source>Clear Cache</source>
        <translation>Clear Cache</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="607"/>
        <source>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</source>
        <translation>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="611"/>
        <source>Drone Sensor File Version:</source>
        <translation>Drone Sensor File Version:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="636"/>
        <source>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</source>
        <translation>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="640"/>
        <source>TextLabel</source>
        <translation>TextLabel</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="668"/>
        <source>Replace the current drone sensor configuration file.
Allows updating to a newer version or custom sensor specifications.
Required file format: JSON with drone models, sensors, focal lengths, and dimensions.
Use this when:
• New drone models are available
• Sensor specifications need updating
• Custom camera configurations are needed
Backup existing file before replacing.</source>
        <translation>Replace the current drone sensor configuration file.
Allows updating to a newer version or custom sensor specifications.
Required file format: JSON with drone models, sensors, focal lengths, and dimensions.
Use this when:
• New drone models are available
• Sensor specifications need updating
• Custom camera configurations are needed
Backup existing file before replacing.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="678"/>
        <source>Replace</source>
        <translation>Replace</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="699"/>
        <source>Close the Preferences window.
All changes are saved automatically when modified.</source>
        <translation>Close the Preferences window.
All changes are saved automatically when modified.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="72"/>
        <source>Language:</source>
        <translation>Language:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="104"/>
        <source>AWS Terrain Tiles (online, ~30 m) is always available as the baseline; local USGS 3DEP adds 1 m detail where downloaded.</source>
        <translation>AWS Terrain Tiles (online, ~30 m) is always available as the baseline; local USGS 3DEP adds 1 m detail where downloaded.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="112"/>
        <source>Elevation Source:</source>
        <translation>Elevation Source:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="122"/>
        <location filename="../app/core/controllers/Preferences.py" line="207"/>
        <source>Manifest CSV:</source>
        <translation>Manifest CSV:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="124"/>
        <source>Path to dem_manifest.csv</source>
        <translation>Path to dem_manifest.csv</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="125"/>
        <location filename="../app/core/controllers/Preferences.py" line="136"/>
        <location filename="../app/core/controllers/Preferences.py" line="210"/>
        <location filename="../app/core/controllers/Preferences.py" line="220"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="133"/>
        <location filename="../app/core/controllers/Preferences.py" line="217"/>
        <source>Tiles directory:</source>
        <translation>Tiles directory:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="135"/>
        <location filename="../app/core/controllers/Preferences.py" line="219"/>
        <source>Folder containing the GeoTIFF tiles</source>
        <translation>Folder containing the GeoTIFF tiles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="145"/>
        <location filename="../app/core/controllers/Preferences.py" line="399"/>
        <source>3DEP is inactive until both paths are set — the AWS Terrain Tiles baseline is used. Use Download tiles… or Browse.</source>
        <translation>3DEP is inactive until both paths are set — the AWS Terrain Tiles baseline is used. Use Download tiles… or Browse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="177"/>
        <source>Terrain</source>
        <translation>Terrain</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="194"/>
        <source>Canopy Data Source</source>
        <translation>Canopy Data Source</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="198"/>
        <source>Source:</source>
        <translation>Source:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="209"/>
        <source>Path to the canopy manifest CSV</source>
        <translation>Path to the canopy manifest CSV</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="229"/>
        <location filename="../app/core/controllers/Preferences.py" line="479"/>
        <source>Canopy is disabled until both paths are set — use Download tiles… or Browse.</source>
        <translation>Canopy is disabled until both paths are set — use Download tiles… or Browse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="239"/>
        <source>Download tiles...</source>
        <translation>Download tiles...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="241"/>
        <source>Download DEM and/or canopy tiles for an area of interest and register them here. Note: the canopy download uses Meta/WRI data and registers it as the canopy source.</source>
        <translation>Download DEM and/or canopy tiles for an area of interest and register them here. Note: the canopy download uses Meta/WRI data and registers it as the canopy source.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="321"/>
        <location filename="../app/core/controllers/Preferences.py" line="672"/>
        <source>{version}_{date}</source>
        <translation>{version}_{date}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="405"/>
        <source>The registered 3DEP files no longer exist on disk — the AWS Terrain Tiles baseline is used. Re-download or fix the paths.</source>
        <translation>The registered 3DEP files no longer exist on disk — the AWS Terrain Tiles baseline is used. Re-download or fix the paths.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="444"/>
        <source>Select 3DEP manifest CSV</source>
        <translation>Select 3DEP manifest CSV</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="446"/>
        <location filename="../app/core/controllers/Preferences.py" line="510"/>
        <source>CSV files (*.csv);;All files (*)</source>
        <translation>CSV files (*.csv);;All files (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="456"/>
        <source>Select 3DEP tiles directory</source>
        <translation>Select 3DEP tiles directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="485"/>
        <source>The registered canopy files no longer exist on disk — canopy is disabled. Re-download or fix the paths.</source>
        <translation>The registered canopy files no longer exist on disk — canopy is disabled. Re-download or fix the paths.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="509"/>
        <source>Select canopy manifest CSV</source>
        <translation>Select canopy manifest CSV</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="518"/>
        <source>Select canopy tiles directory</source>
        <translation>Select canopy tiles directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="529"/>
        <source>Download Tiles</source>
        <translation>Download Tiles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="530"/>
        <source>The tile downloader is unavailable:
{error}</source>
        <translation>The tile downloader is unavailable:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="603"/>
        <source>{tiles} tiles ({size_mb:.1f} MB)</source>
        <translation>{tiles} tiles ({size_mb:.1f} MB)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="595"/>
        <source>Not available</source>
        <translation>Not available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="612"/>
        <source>N/A (local tiles)</source>
        <translation>N/A (local tiles)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="615"/>
        <location filename="../app/core/controllers/Preferences.py" line="623"/>
        <location filename="../app/core/controllers/Preferences.py" line="651"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="624"/>
        <source>Terrain service not available.</source>
        <translation>Terrain service not available.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="630"/>
        <source>Clear Terrain Cache</source>
        <translation>Clear Terrain Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="632"/>
        <source>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="645"/>
        <source>Cache Cleared</source>
        <translation>Cache Cleared</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="646"/>
        <source>Cleared {count} cached terrain tiles.</source>
        <translation>Cleared {count} cached terrain tiles.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="652"/>
        <source>Failed to clear cache: {error}</source>
        <translation>Failed to clear cache: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="659"/>
        <source>Select a Drone Sensor File</source>
        <translation>Select a Drone Sensor File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="661"/>
        <source>CSV Files (*.csv)</source>
        <translation>CSV Files (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="687"/>
        <source>Restart Required</source>
        <translation>Restart Required</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="688"/>
        <source>Please restart the application for language changes to take effect.</source>
        <translation>Please restart the application for language changes to take effect.</translation>
    </message>
</context>
<context>
    <name>QtImageViewer</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/QtImageViewer.py" line="390"/>
        <source>Open image</source>
        <translation>Open image</translation>
    </message>
</context>
<context>
    <name>RXAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
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
        <translation>Number of segments to divide each image into for analysis.
The RX algorithm analyzes each segment independently to detect local anomalies.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in images with varying backgrounds.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Image Segments:</translation>
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
        <translation>Select the number of segments to divide each image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The RX Anomaly algorithm uses statistical analysis to detect unusual pixels:
• 1 segment: Analyzes the whole image at once (best for small images)
• More segments: Analyzes local regions independently (better for large images)
Higher segment counts improve detection in images with varying backgrounds.
Recommended: 4-9 segments for typical drone imagery.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="73"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="78"/>
        <source>2</source>
        <translation>2</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="83"/>
        <source>4</source>
        <translation>4</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="88"/>
        <source>6</source>
        <translation>6</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="93"/>
        <source>9</source>
        <translation>9</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="98"/>
        <source>16</source>
        <translation>16</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="103"/>
        <source>25</source>
        <translation>25</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="108"/>
        <source>36</source>
        <translation>36</translation>
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
        <translation>Detection sensitivity for anomaly detection.
• Range: 1 to 10
• Default: 5
Controls how statistically different a pixel must be from the background to be detected:
• Lower values (1-3): DECREASE detections - less sensitive, only detects strong anomalies
• Higher values (7-10): INCREASE detections - more sensitive, detects subtle anomalies
Higher sensitivity finds more potential targets but may include noise/false positives.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="146"/>
        <source>Sensitivity:</source>
        <translation>Sensitivity:</translation>
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
        <translation>Adjust the detection sensitivity for anomaly detection.
• Range: 1 to 10
• Default: 5
The RX algorithm uses statistical analysis to find pixels that differ from the background:
• Lower values (1-3): Less sensitive, only detects strong anomalies (fewer false positives)
• Medium values (4-6): Balanced detection (recommended for most cases)
• Higher values (7-10): More sensitive, detects subtle anomalies (more detections, may include noise)
Anomalies are pixels that are statistically different from the surrounding background.
Use lower sensitivity for clean images, higher for finding subtle targets.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="205"/>
        <source>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</source>
        <translation>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="209"/>
        <source>5</source>
        <translation>5</translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizard</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="29"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="49"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="64"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="100"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>How aggressively should ADIAT be searching for anomalies?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="113"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Note: A higher setting will find more potential anomalies but may also increase false positives.</translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="50"/>
        <source>Very 
Conservative</source>
        <translation>Very
Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="51"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="52"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="53"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="54"/>
        <source>Very 
Aggressive</source>
        <translation>Very
Aggressive</translation>
    </message>
</context>
<context>
    <name>RecentColorWidget</name>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="68"/>
        <source>&lt;b&gt;RGB:&lt;/b&gt; ({r}, {g}, {b})</source>
        <translation>&lt;b&gt;RGB:&lt;/b&gt; ({r}, {g}, {b})</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="97"/>
        <source>&lt;br&gt;&lt;b&gt;H (°):&lt;/b&gt; {min}-{max}</source>
        <translation>&lt;br&gt;&lt;b&gt;H (°):&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="100"/>
        <source> &lt;b&gt;S (%):&lt;/b&gt; {min}-{max}</source>
        <translation> &lt;b&gt;S (%):&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="103"/>
        <source> &lt;b&gt;V (%):&lt;/b&gt; {min}-{max}</source>
        <translation> &lt;b&gt;V (%):&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="112"/>
        <source>&lt;br&gt;&lt;b&gt;R:&lt;/b&gt; {min}-{max}</source>
        <translation>&lt;br&gt;&lt;b&gt;R:&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="115"/>
        <source> &lt;b&gt;G:&lt;/b&gt; {min}-{max}</source>
        <translation> &lt;b&gt;G:&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="118"/>
        <source> &lt;b&gt;B:&lt;/b&gt; {min}-{max}</source>
        <translation> &lt;b&gt;B:&lt;/b&gt; {min}-{max}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="124"/>
        <source>&lt;br&gt;&lt;b&gt;Threshold:&lt;/b&gt; {value}</source>
        <translation>&lt;br&gt;&lt;b&gt;Threshold:&lt;/b&gt; {value}</translation>
    </message>
</context>
<context>
    <name>RecentColorsDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="151"/>
        <source>Recent Colors</source>
        <translation>Recent Colors</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="162"/>
        <source>Select a recently used color:</source>
        <translation>Select a recently used color:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="178"/>
        <source>No recent colors found</source>
        <translation>No recent colors found</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="204"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>RecordingsDialog</name>
    <message>
        <location filename="../app/core/views/streaming/RecordingsDialog.py" line="36"/>
        <source>{title} — {when} · {count} detections</source>
        <extracomment>Absolute path of the chosen recording&apos;s video, set on accept.</extracomment>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/RecordingsDialog.py" line="37"/>
        <source>Recording</source>
        <translation type="unfinished">Recording</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/RecordingsDialog.py" line="74"/>
        <source>Open recording video</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/RecordingsDialog.py" line="76"/>
        <source>Videos (*.mp4)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="14"/>
        <source>Recordings</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="20"/>
        <source>Choose a recording to replay. Double-click plays it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="34"/>
        <source>No recordings yet. Recordings appear here automatically when you stop one, or use Browse to open a recording folder from another machine.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="46"/>
        <source>Browse…</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="49"/>
        <source>Open a recording video that is not in this list.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="69"/>
        <source>Replay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/RecordingsDialog.ui" line="82"/>
        <source>Cancel</source>
        <translation type="unfinished">Cancel</translation>
    </message>
</context>
<context>
    <name>RenderingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="44"/>
        <source>Shape Options</source>
        <translation>Shape Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="47"/>
        <source>Shape Mode:</source>
        <translation>Shape Mode:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="49"/>
        <source>Box</source>
        <translation>Box</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="50"/>
        <source>Circle</source>
        <translation>Circle</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="51"/>
        <source>Dot</source>
        <translation>Dot</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="52"/>
        <source>Off</source>
        <translation>Off</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="55"/>
        <source>Shape to draw around detections:

• Box: Rectangle around detection bounding box.
  Use for: Precise boundaries, technical visualization.

• Circle: Circle encompassing detection (150% of contour radius).
  Use for: General use, cleaner look (default).

• Dot: Small dot at detection centroid.
  Use for: Minimal overlay, fast rendering.

• Off: No shape overlay (only thumbnails/text if enabled).
  Use for: Clean video with minimal overlays.</source>
        <translation>Shape to draw around detections:

• Box: Rectangle around detection bounding box.
  Use for: Precise boundaries, technical visualization.

• Circle: Circle encompassing detection (150% of contour radius).
  Use for: General use, cleaner look (default).

• Dot: Small dot at detection centroid.
  Use for: Minimal overlay, fast rendering.

• Off: No shape overlay (only thumbnails/text if enabled).
  Use for: Clean video with minimal overlays.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="70"/>
        <source>Visual Options</source>
        <translation>Visual Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="73"/>
        <source>Show Text Labels (slower)</source>
        <translation>Show Text Labels (slower)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="75"/>
        <source>Displays text labels near detections showing detection information.
Adds ~5-15ms processing overhead depending on detection count.
Labels show: detection type, confidence, area.
Recommended: OFF for speed, ON for debugging/analysis.</source>
        <translation>Displays text labels near detections showing detection information.
Adds ~5-15ms processing overhead depending on detection count.
Labels show: detection type, confidence, area.
Recommended: OFF for speed, ON for debugging/analysis.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="82"/>
        <source>Show Contours (slowest)</source>
        <translation>Show Contours (slowest)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="84"/>
        <source>Draws exact detection contours (pixel-precise boundaries).
Adds ~10-20ms processing overhead (very expensive).
Shows exact shape detected by algorithm.
Recommended: OFF for speed, ON only for detailed analysis.</source>
        <translation>Draws exact detection contours (pixel-precise boundaries).
Adds ~10-20ms processing overhead (very expensive).
Shows exact shape detected by algorithm.
Recommended: OFF for speed, ON only for detailed analysis.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="92"/>
        <source>Use Detection Color (hue @ 100% sat/val for color anomalies)</source>
        <translation>Use Detection Color (hue @ 100% sat/val for color anomalies)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="95"/>
        <source>Color the detection overlay based on detected color.
For color anomalies: Uses the detected hue at 100% saturation/value.
For motion detections: Uses default color (green/blue).
Helps visually identify what color was detected.
Recommended: ON for color detection, OFF for motion-only.</source>
        <translation>Color the detection overlay based on detected color.
For color anomalies: Uses the detected hue at 100% saturation/value.
For motion detections: Uses default color (green/blue).
Helps visually identify what color was detected.
Recommended: ON for color detection, OFF for motion-only.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="106"/>
        <source>Performance Limits</source>
        <translation>Performance Limits</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="109"/>
        <source>Max Detections:</source>
        <translation>Max Detections:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="115"/>
        <source>Maximum number of detections to render on screen (0-1000).
Prevents rendering slowdown when hundreds of detections occur.
Shows highest confidence detections first.
0 = Unlimited (may cause lag with many detections).
Recommended: 10 for general use, 50 for complex rendering (text+contours).</source>
        <translation>Maximum number of detections to render on screen (0-1000).
Prevents rendering slowdown when hundreds of detections occur.
Shows highest confidence detections first.
0 = Unlimited (may cause lag with many detections).
Recommended: 10 for general use, 50 for complex rendering (text+contours).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="126"/>
        <source>Temporal Voting</source>
        <translation>Temporal Voting</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="129"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Enable Temporal Voting (reduce flicker)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="132"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="142"/>
        <source>Window Frames (M):</source>
        <translation>Window Frames (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="147"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="155"/>
        <source>Threshold (N of M):</source>
        <translation>Threshold (N of M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="160"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be ≤ Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be ≤ Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="173"/>
        <source>Detection Cleanup</source>
        <translation>Detection Cleanup</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="177"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Enable Aspect Ratio Filtering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="180"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="189"/>
        <source>Min Ratio:</source>
        <translation>Min Ratio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="195"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 ≈ reject if height is more than 5× width.</source>
        <translation>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 ≈ reject if height is more than 5× width.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="202"/>
        <source>Max Ratio:</source>
        <translation>Max Ratio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="208"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="217"/>
        <source>Detection Clustering</source>
        <translation>Detection Clustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="220"/>
        <source>Enable Detection Clustering</source>
        <translation>Enable Detection Clustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="223"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="232"/>
        <source>Clustering Distance (px):</source>
        <translation>Clustering Distance (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="237"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</translation>
    </message>
</context>
<context>
    <name>ReplayWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/ReplayWindow.py" line="160"/>
        <source>Could not open {name}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/ReplayWindow.py" line="253"/>
        <source>{title} — {when} · {count} detections</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/ReplayWindow.py" line="257"/>
        <source>Recording Replay — {title}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/ReplayWindow.py" line="363"/>
        <source>Export finished with problems - see the log</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/ReplayWindow.py" line="367"/>
        <source>Exported {count} files to the recording folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="14"/>
        <source>Recording Replay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="23"/>
        <source>No recording loaded</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="46"/>
        <source>Export…</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="49"/>
        <source>Write this recording&apos;s shareable files: results for the Image Analysis window, CSV tables, an offline map page and a KML.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="59"/>
        <source>Open Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="90"/>
        <source>Video</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="97"/>
        <source>Playback</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="109"/>
        <source>Detections</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/ReplayWindow.ui" line="114"/>
        <source>Map</source>
        <translation type="unfinished">Map</translation>
    </message>
</context>
<context>
    <name>ResultsFolderDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="115"/>
        <source>Load Results Folder</source>
        <translation>Load Results Folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="124"/>
        <source>Found {count} result(s)</source>
        <translation>Found {count} result(s)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Folder</source>
        <translation>Folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Algorithm</source>
        <translation>Algorithm</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Images</source>
        <translation>Images</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Missing</source>
        <translation>Missing</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>AOIs</source>
        <translation>AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Map</source>
        <translation>Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>View</source>
        <translation>View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="170"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="216"/>
        <source>Open in Google Maps</source>
        <translation>Open in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="226"/>
        <source>No images available - cannot get GPS location</source>
        <translation>No images available - cannot get GPS location</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="228"/>
        <source>No GPS coordinates found in images</source>
        <translation>No GPS coordinates found in images</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="248"/>
        <source>Open in Results Viewer</source>
        <translation>Open in Results Viewer</translation>
    </message>
</context>
<context>
    <name>ResultsLoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="29"/>
        <source>Loading Results</source>
        <translation>Loading Results</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="43"/>
        <source>Opening results...</source>
        <translation>Opening results...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="55"/>
        <source>Preparing...</source>
        <translation>Preparing...</translation>
    </message>
</context>
<context>
    <name>ReviewOrNewPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="70"/>
        <source>No file selected</source>
        <translation>No file selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="114"/>
        <source>Select ADIAT Results File</source>
        <translation>Select ADIAT Results File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>XML Files (*.xml);;All Files (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="126"/>
        <source>File Name Warning</source>
        <translation>File Name Warning</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="128"/>
        <source>The selected file does not appear to be an ADIAT_Data.xml result or an ADIAT_Search project file.

Do you want to continue with this file?</source>
        <translation>The selected file does not appear to be an ADIAT_Data.xml result or an ADIAT_Search project file.

Do you want to continue with this file?</translation>
    </message>
</context>
<context>
    <name>ReviewerNameDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="25"/>
        <source>Reviewer Name</source>
        <translation>Reviewer Name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="45"/>
        <source>Review Tracking</source>
        <translation>Review Tracking</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="51"/>
        <source>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</source>
        <translation>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="60"/>
        <source>Your Name:</source>
        <translation>Your Name:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="64"/>
        <source>Enter your name</source>
        <translation>Enter your name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="65"/>
        <source>Enter your full name or identifier for review tracking</source>
        <translation>Enter your full name or identifier for review tracking</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="71"/>
        <source>Remember my name</source>
        <translation>Remember my name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="74"/>
        <source>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</source>
        <translation>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="86"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="91"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="123"/>
        <source>Name Required</source>
        <translation>Name Required</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="124"/>
        <source>Please enter your name to continue.</source>
        <translation>Please enter your name to continue.</translation>
    </message>
</context>
<context>
    <name>ScanProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="51"/>
        <source>Scanning for Results</source>
        <translation>Scanning for Results</translation>
    </message>
</context>
<context>
    <name>SimilarityGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="172"/>
        <source>Reference</source>
        <translation>Reference</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="181"/>
        <source>Unknown</source>
        <translation>Unknown</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="190"/>
        <source>AOI #{number}</source>
        <translation>AOI #{number}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="192"/>
        <source>AOI {index}</source>
        <translation>AOI {index}</translation>
    </message>
</context>
<context>
    <name>StatusController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="45"/>
        <source>GPS Coordinates</source>
        <translation>GPS Coordinates</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="48"/>
        <source>Altitude</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="49"/>
        <source>Gimbal Orientation</source>
        <translation>Gimbal Orientation</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="50"/>
        <source>Estimated Average GSD</source>
        <translation>Estimated Average GSD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="51"/>
        <source>Temperature</source>
        <translation>Temperature</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="52"/>
        <source>Color Values</source>
        <translation>Color Values</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="53"/>
        <source>Drone Orientation</source>
        <translation>Drone Orientation</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="54"/>
        <source>Grid Review</source>
        <translation>Grid Review</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="127"/>
        <source>Error Loading Images</source>
        <translation>Error Loading Images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="133"/>
        <source>No active images available.</source>
        <translation>No active images available.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="137"/>
        <source>No other images available.</source>
        <translation>No other images available.</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="90"/>
        <source>Are you primarily looking for a person?</source>
        <translation>Are you primarily looking for a person?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="156"/>
        <source>Do you know a distinctive target color?</source>
        <translation>Do you know a distinctive target color?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Color Detection</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Color Anomaly &amp; Motion Detection</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>AI Person Detector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="186"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Selected Algorithm: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="191"/>
        <source>{result}
Secondary Recommendation: {secondary}</source>
        <translation>{result}
Secondary Recommendation: {secondary}</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="180"/>
        <source>Color Detection</source>
        <translation>Color Detection</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="181"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Color Anomaly &amp; Motion Detection</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="182"/>
        <source>AI Person Detector</source>
        <translation>AI Person Detector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="189"/>
        <source>Algorithm</source>
        <translation>Algorithm</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="191"/>
        <source>{algorithm} Parameters</source>
        <translation>{algorithm} Parameters</translation>
    </message>
</context>
<context>
    <name>StreamConnectionPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="105"/>
        <source>Click Scan to find devices...</source>
        <translation>Click Scan to find devices...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="121"/>
        <source>480p</source>
        <translation>480p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="122"/>
        <source>720p</source>
        <translation>720p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="123"/>
        <source>1080p</source>
        <translation>1080p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="124"/>
        <source>4K</source>
        <translation>4K</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="333"/>
        <source>Video File:</source>
        <translation>Video File:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="334"/>
        <source>Click Browse to select a video file...</source>
        <translation>Click Browse to select a video file...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="340"/>
        <source>Click Scan to detect available capture devices, then select one from the dropdown.</source>
        <translation>Click Scan to detect available capture devices, then select one from the dropdown.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="342"/>
        <source>Device:</source>
        <translation>Device:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="343"/>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="366"/>
        <source></source>
        <translation></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="377"/>
        <source>OpenCV not available</source>
        <translation>OpenCV not available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="423"/>
        <source>Device {index} ({backend})</source>
        <translation>Device {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="416"/>
        <source>No capture devices found</source>
        <translation>No capture devices found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="327"/>
        <source>Choose the video file you want to analyze. Use Browse to pick a file from disk.

Location data is optional and usually detected automatically — ADIAT reads an .SRT sitting next to the video, or telemetry embedded in the video, on its own. Set it only to override that, or to supply location data the video does not have: a DJI .SRT or a .CSV flight log.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="349"/>
        <source>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</source>
        <translation>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="351"/>
        <source>Stream URL:</source>
        <translation>Stream URL:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="352"/>
        <source>rtmp://server:port/app/streamKey</source>
        <translation>rtmp://server:port/app/streamKey</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="358"/>
        <source>You&apos;ll be prompted for the pairing code when you connect — pairing codes expire about 30 seconds after ADIAT Flight shows them, so don&apos;t generate one until you&apos;re ready.

Finish this setup first, then start sharing in ADIAT Flight and enter the code. Detections reported by ADIAT Flight are ignored — this desktop runs its own analysis on the video.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="365"/>
        <source>Pairing Code:</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="383"/>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="386"/>
        <source>Scanning...</source>
        <translation>Scanning...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="410"/>
        <source>Scan</source>
        <translation>Scan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="490"/>
        <source>Select Video File</source>
        <translation>Select Video File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="493"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</source>
        <translation>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="512"/>
        <source>Select a Metadata File</source>
        <translation type="unfinished">Select a Metadata File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="515"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv);;All Files (*)</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamControlWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="862"/>
        <source>Stream Connection</source>
        <translation>Stream Connection</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="872"/>
        <source>Stream Type:</source>
        <translation>Stream Type:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="874"/>
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="875"/>
        <source>HDMI Capture</source>
        <translation>HDMI Capture</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="876"/>
        <source>RTMP Stream</source>
        <translation>RTMP Stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="879"/>
        <source>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</source>
        <translation>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="896"/>
        <source>Stream URL/Path:</source>
        <translation>Stream URL/Path:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="903"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1152"/>
        <source>Click to browse for video file...</source>
        <translation>Click to browse for video file...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="917"/>
        <source>Select HDMI capture device</source>
        <translation>Select HDMI capture device</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="919"/>
        <source>Scanning for devices...</source>
        <translation>Scanning for devices...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="923"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="978"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1101"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="927"/>
        <source>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</source>
        <translation>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="934"/>
        <source>Scan...</source>
        <translation>Scan...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="936"/>
        <source>Scan for available HDMI capture devices</source>
        <translation>Scan for available HDMI capture devices</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="957"/>
        <source>Optional. ADIAT already finds location data on its own, from:
• an .SRT file sitting next to the video
• telemetry embedded in the video (newer DJI aircraft)

Choose a file here only to override that, or to supply location data the video does not have. Supports DJI .SRT and .CSV flight logs (Skydio and similar).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="966"/>
        <source>Location Data (optional):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="973"/>
        <source>Optional - usually detected automatically</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="980"/>
        <source>Browse for an SRT or CSV file with the flight&apos;s location data.
Not needed for most videos, which already carry it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="989"/>
        <source>Connect</source>
        <translation>Connect</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="992"/>
        <source>Connect to the specified video source and begin processing.</source>
        <translation>Connect to the specified video source and begin processing.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="994"/>
        <source>Disconnect</source>
        <translation>Disconnect</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="998"/>
        <source>Disconnect from the current video source and stop processing.</source>
        <translation>Disconnect from the current video source and stop processing.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1005"/>
        <source>Status: Disconnected</source>
        <translation>Status: Disconnected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1007"/>
        <source>Current connection status</source>
        <translation>Current connection status</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1010"/>
        <source>Performance</source>
        <translation>Performance</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1011"/>
        <source>Real-time performance metrics</source>
        <translation>Real-time performance metrics</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1015"/>
        <source>Video: --</source>
        <translation>Video: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1016"/>
        <source>Original video resolution</source>
        <translation>Original video resolution</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1017"/>
        <source>Processing: --</source>
        <translation>Processing: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1019"/>
        <source>Resolution used for detection processing</source>
        <translation>Resolution used for detection processing</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1023"/>
        <source>Source FPS: --</source>
        <translation>Source FPS: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1024"/>
        <source>Source frame rate and the applied processing cadence</source>
        <translation>Source frame rate and the applied processing cadence</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1025"/>
        <source>Proc FPS: --</source>
        <translation>Proc FPS: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1027"/>
        <source>Actual frames per second being processed</source>
        <translation>Actual frames per second being processed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1031"/>
        <source>Time: -- ms</source>
        <translation>Time: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1033"/>
        <source>Time in milliseconds to process each frame</source>
        <translation>Time in milliseconds to process each frame</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1035"/>
        <source>Latency: -- ms</source>
        <translation>Latency: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1037"/>
        <source>End-to-end latency from frame capture to display</source>
        <translation>End-to-end latency from frame capture to display</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1041"/>
        <source>Frames: --</source>
        <translation>Frames: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1042"/>
        <source>Total number of frames processed</source>
        <translation>Total number of frames processed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1043"/>
        <source>Detections: --</source>
        <translation>Detections: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1044"/>
        <source>Number of detections in current frame</source>
        <translation>Number of detections in current frame</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1058"/>
        <source>Recording</source>
        <translation>Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1063"/>
        <source>Start Recording</source>
        <translation>Start Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1066"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Start recording the video stream with detection overlays.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1068"/>
        <source>Stop Recording</source>
        <translation>Stop Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1071"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Stop the current recording and save to file.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1078"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1303"/>
        <source>Status: Not Recording</source>
        <translation>Status: Not Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1081"/>
        <source>Current recording status and output file path</source>
        <translation>Current recording status and output file path</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1085"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1310"/>
        <source>Duration: --</source>
        <translation>Duration: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1087"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Recording statistics: Duration, FPS, Frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1096"/>
        <source>Save to:</source>
        <translation>Save to:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1099"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Directory where video recordings will be saved.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1103"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Choose a folder to store recordings.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1160"/>
        <source>rtmp://server:port/app/stream</source>
        <translation>rtmp://server:port/app/stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1173"/>
        <source>Click Connect to enter your pairing code</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1194"/>
        <source>Invalid Device</source>
        <translation>Invalid Device</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1195"/>
        <source>Please select a valid HDMI capture device.</source>
        <translation>Please select a valid HDMI capture device.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1215"/>
        <source>Invalid URL</source>
        <translation>Invalid URL</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1216"/>
        <source>Please enter a valid stream URL.</source>
        <translation>Please enter a valid stream URL.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1227"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1250"/>
        <source>Status: {message}</source>
        <translation>Status: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1290"/>
        <source>Status: Recording</source>
        <translation>Status: Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1294"/>
        <source>Output: {value}</source>
        <translation>Output: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1307"/>
        <source>Duration: {value}</source>
        <translation>Duration: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1336"/>
        <source>Select Recording Directory</source>
        <translation>Select Recording Directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1347"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1350"/>
        <source>Scanning...</source>
        <translation>Scanning...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1374"/>
        <source>Scan</source>
        <translation>Scan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1440"/>
        <source>Source FPS: {source:.1f} (Applied {applied:.1f})</source>
        <translation>Source FPS: {source:.1f} (Applied {applied:.1f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1447"/>
        <source>Source FPS: {fps:.1f}</source>
        <translation>Source FPS: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1500"/>
        <source>Select a Metadata File</source>
        <translation type="unfinished">Select a Metadata File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1503"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv);;All Files (*)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1387"/>
        <source>Device {index} ({backend})</source>
        <translation>Device {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="865"/>
        <source>Configure and connect to video source (file, HDMI capture, RTMP stream, or ADIAT Flight)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="888"/>
        <source>ADIAT Flight</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="890"/>
        <source>• ADIAT Flight: Live feed paired with the ADIAT Flight app</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="907"/>
        <source>Enter or browse for the video source:
• File: Click to browse for video file (MP4, AVI, MOV, etc.)
• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)
• ADIAT Flight: Enter the 6-character pairing code shown in the app</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1380"/>
        <source>No capture devices found</source>
        <translation>No capture devices found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1417"/>
        <source>Video: {width}x{height}</source>
        <translation>Video: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1424"/>
        <source>Processing: {width}x{height}</source>
        <translation>Processing: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1450"/>
        <source>Proc FPS: {fps:.1f}</source>
        <translation>Proc FPS: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1458"/>
        <source>Time: {time:.1f} ms</source>
        <translation>Time: {time:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1461"/>
        <source>Latency: {latency:.1f} ms</source>
        <translation>Latency: {latency:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1469"/>
        <source>Frames: {count}</source>
        <translation>Frames: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1472"/>
        <source>Detections: {count}</source>
        <translation>Detections: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1479"/>
        <source>Select Video File</source>
        <translation>Select Video File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1482"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</source>
        <translation>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</translation>
    </message>
</context>
<context>
    <name>StreamImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="181"/>
        <source>Select Drone/Camera</source>
        <translation>Select Drone/Camera</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="185"/>
        <source>No drones available</source>
        <translation>No drones available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="227"/>
        <source>Other</source>
        <translation>Other</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="263"/>
        <source>Error loading drone data</source>
        <translation>Error loading drone data</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="337"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Invalid camera data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="538"/>
        <source>{sensor_name}: Sensor dimensions not available</source>
        <translation>{sensor_name}: Sensor dimensions not available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="545"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Missing camera data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="546"/>
        <source>Unable to calculate GSD. Sensor dimensions are required.</source>
        <translation>Unable to calculate GSD. Sensor dimensions are required.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="552"/>
        <source>-- (Error)</source>
        <translation>-- (Error)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="583"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="585"/>
        <source>Primary</source>
        <translation>Primary</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="587"/>
        <source>Sensor</source>
        <translation>Sensor</translation>
    </message>
</context>
<context>
    <name>StreamTargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Hat, Helmet, Plastic Bag</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Cat, Daypack</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Large Pack, Medium Dog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Sleeping Bag, Large Dog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Small Boat, 2-Person Tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Car/SUV, Small Pickup Truck, Large Tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>House</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>More Examples:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>sqm</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>sqft</translation>
    </message>
</context>
<context>
    <name>StreamTelemetryCoordinator</name>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="100"/>
        <source>Waiting for telemetry from ADIAT Flight...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="112"/>
        <source>Could not read location data from video</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="122"/>
        <source>Could not use the selected metadata file: {reason}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="127"/>
        <source>No location data in this video</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="135"/>
        <source>Location data embedded in video ({count} fixes)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="141"/>
        <source>Location data from SRT file ({count} fixes)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="147"/>
        <source>Location data from {name} ({count} fixes)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="154"/>
        <source>Location data loaded ({count} fixes)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/components/StreamTelemetryCoordinator.py" line="207"/>
        <source>Receiving telemetry from ADIAT Flight</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>StreamViewerWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="129"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="268"/>
        <source>Live View</source>
        <translation>Live View</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="273"/>
        <source>Gallery</source>
        <translation>Gallery</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="336"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="337"/>
        <source>Open Recording…</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="338"/>
        <source>Streaming Analysis Wizard</source>
        <translation>Streaming Analysis Wizard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="339"/>
        <source>Image Analysis</source>
        <translation>Image Analysis</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="340"/>
        <source>Flight Viewer</source>
        <translation>Flight Viewer</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="341"/>
        <source>Preferences</source>
        <translation>Preferences</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="352"/>
        <source>Help</source>
        <translation>Help</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="353"/>
        <source>Check for Updates</source>
        <translation>Check for Updates</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="354"/>
        <source>Manual</source>
        <translation>Manual</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="355"/>
        <source>Community Forum</source>
        <translation>Community Forum</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="356"/>
        <source>YouTube Channel</source>
        <translation>YouTube Channel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="388"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2409"/>
        <source>Status: Not Recording</source>
        <translation>Status: Not Recording</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="391"/>
        <source>Current recording status and output file path</source>
        <translation>Current recording status and output file path</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="395"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2411"/>
        <source>Duration: --</source>
        <translation>Duration: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="397"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Recording statistics: Duration, FPS, Frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="402"/>
        <source>Save to:</source>
        <translation>Save to:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="406"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Directory where video recordings will be saved.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="408"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="410"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Choose a folder to store recordings.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="420"/>
        <source>Save detections</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="423"/>
        <source>Save each confirmed detection with the recording: a thumbnail, its position, and a results file that opens in the Image Analysis window.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="427"/>
        <source>Save flight map</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="430"/>
        <source>Save the flight path and detection locations as a map and a KML file. Requires location data from the video or a live ADIAT Flight feed.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="438"/>
        <source>Replay</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="441"/>
        <source>Watch this recording: video, detections, telemetry and map.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="443"/>
        <source>Open Recording Folder</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="446"/>
        <source>Open the folder holding the last recording and its detections.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="576"/>
        <source>Could not open replay: {error}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="587"/>
        <source>Select Recording Directory</source>
        <translation>Select Recording Directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="607"/>
        <source>Algorithm:</source>
        <translation>Algorithm:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="609"/>
        <source>Select which streaming detection algorithm to use</source>
        <translation>Select which streaming detection algorithm to use</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="615"/>
        <source>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</source>
        <translation>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="650"/>
        <source>Gallery Threshold:</source>
        <translation>Gallery Threshold:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="653"/>
        <source>Number of frames a detection must be seen before appearing in the Gallery tab</source>
        <translation>Number of frames a detection must be seen before appearing in the Gallery tab</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="660"/>
        <source> frames</source>
        <translation> frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="663"/>
        <source>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</source>
        <translation>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="746"/>
        <source>Device {index}</source>
        <translation>Device {index}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="955"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="974"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="988"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1011"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1025"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1039"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1053"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2445"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="956"/>
        <source>Failed to open Streaming Analysis Guide:
{error}</source>
        <translation>Failed to open Streaming Analysis Guide:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="975"/>
        <source>Failed to open Image Analysis:
{error}</source>
        <translation>Failed to open Image Analysis:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="989"/>
        <source>Failed to open Preferences:
{error}</source>
        <translation>Failed to open Preferences:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1012"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Failed to open Flight Viewer:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1026"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Failed to open Help documentation:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1040"/>
        <source>Failed to open Community Forum:
{error}</source>
        <translation>Failed to open Community Forum:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1054"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Failed to open YouTube Channel:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1164"/>
        <source>Loaded: {algorithm}</source>
        <translation>Loaded: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1180"/>
        <source>Error loading algorithm: {error}</source>
        <translation>Error loading algorithm: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1184"/>
        <source>Algorithm Load Error</source>
        <translation>Algorithm Load Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1695"/>
        <source>Algorithm switched to {label}</source>
        <translation>Algorithm switched to {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1778"/>
        <source>Connecting to {code}...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1866"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2006"/>
        <source>No Stream Connected</source>
        <translation>No Stream Connected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1917"/>
        <source>{state} - {message}</source>
        <translation>{state} - {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1912"/>
        <source>Connected</source>
        <translation>Connected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="534"/>
        <source>Save the flight path and detection locations as a map and a KML file. Location data is available for this source.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="541"/>
        <source>Save the flight path and detection locations as a map and a KML file. Nothing is saved unless location data arrives while recording.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1914"/>
        <source>Disconnected</source>
        <translation>Disconnected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1916"/>
        <source>Connecting</source>
        <translation type="unfinished">Connecting</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1935"/>
        <source>✓ Connected: {message}</source>
        <translation>✓ Connected: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1983"/>
        <source>… {message}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1988"/>
        <source>✗ Disconnected: {message}</source>
        <translation>✗ Disconnected: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2222"/>
        <source>No detections found.</source>
        <translation>No detections found.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2226"/>
        <source>Detection Results ({count} found):</source>
        <translation>Detection Results ({count} found):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2238"/>
        <source>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</source>
        <translation>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2248"/>
        <source>#{index}: Type({cls})</source>
        <translation>#{index}: Type({cls})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2253"/>
        <source> Conf({confidence:.2f})</source>
        <translation> Conf({confidence:.2f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2322"/>
        <source>Recording saved to {folder}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2325"/>
        <source>Stored {detections} detections and {fixes} location fixes.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2332"/>
        <source>Flight map saved as {name}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2339"/>
        <source>Could not save part of the recording: {reason}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2380"/>
        <source>Recording started: {path}</source>
        <translation>Recording started: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2387"/>
        <source>Recording stopped</source>
        <translation>Recording stopped</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2405"/>
        <source>Status: Recording to {path}</source>
        <translation>Status: Recording to {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2425"/>
        <source>Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}</source>
        <translation>Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2443"/>
        <source>✗ Error: {error}</source>
        <translation>✗ Error: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2510"/>
        <source>Live Stream</source>
        <translation>Live Stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2512"/>
        <source>Cannot seek in live stream.

Detection was first seen at frame {frame}.</source>
        <translation>Cannot seek in live stream.

Detection was first seen at frame {frame}.</translation>
    </message>
</context>
<context>
    <name>StreamingGuide</name>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="14"/>
        <source>Streaming Setup Guide</source>
        <translation>Streaming Setup Guide</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="51"/>
        <source>Connect to Your Stream</source>
        <translation>Connect to Your Stream</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="115"/>
        <source>Pre-recorded video file with playback controls</source>
        <translation>Pre-recorded video file with playback controls</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="122"/>
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="161"/>
        <source>Live HDMI capture device (enter device index)</source>
        <translation>Live HDMI capture device (enter device index)</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="168"/>
        <source>HDMI</source>
        <translation>HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="204"/>
        <source>Network stream via RTMP URL</source>
        <translation>Network stream via RTMP URL</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="211"/>
        <source>RTMP</source>
        <translation>RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="247"/>
        <source>Live feed from the ADIAT Flight app (enter pairing code)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="254"/>
        <source>ADIAT Flight</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="297"/>
        <source>File: Use local video files (MP4, MOV, etc.) with timeline controls.</source>
        <translation>File: Use local video files (MP4, MOV, etc.) with timeline controls.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="312"/>
        <source>HDMI: Connect to a live HDMI capture device.</source>
        <translation>HDMI: Connect to a live HDMI capture device.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="327"/>
        <source>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</source>
        <translation>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="342"/>
        <source>ADIAT Flight: Pair with the ADIAT Flight app using the 6-character code it displays.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="386"/>
        <source>Connection Details</source>
        <translation>Connection Details</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="405"/>
        <source>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</source>
        <translation>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="422"/>
        <source>Stream URL/Path:</source>
        <translation>Stream URL/Path:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="431"/>
        <source>Click Browse to select a file or enter a URL...</source>
        <translation>Click Browse to select a file or enter a URL...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="443"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="496"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="457"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="473"/>
        <source>Optional. ADIAT already finds location data on its own, from:
• an .SRT file sitting next to the video
• telemetry embedded in the video (newer DJI aircraft)

Choose a file here only to override that, or to supply location data the video does not have. Supports DJI .SRT and .CSV flight logs (Skydio and similar).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="464"/>
        <source>Location Data (optional):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="480"/>
        <source>Optional - usually detected automatically</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="492"/>
        <source>Browse for an SRT or CSV file with the flight&apos;s location data.
Not needed for most videos, which already carry it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="510"/>
        <source>Auto Connect:</source>
        <translation>Auto Connect:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="522"/>
        <source>Connect as soon as the guide finishes</source>
        <translation>Connect as soon as the guide finishes</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="534"/>
        <source>Capture Devices:</source>
        <translation>Capture Devices:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="555"/>
        <source>Scan...</source>
        <translation>Scan...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="595"/>
        <source>Processing Resolution:</source>
        <translation>Processing Resolution:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="643"/>
        <source>Video Capture Information</source>
        <translation>Video Capture Information</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="665"/>
        <source>What drone/camera was used to capture the video?</source>
        <translation>What drone/camera was used to capture the video?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="695"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>At what above ground level (AGL) altitude was the drone flying?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="708"/>
        <source>Height above the ground being flown over - what the image scale depends on. Over flat terrain this equals the drone&apos;s above-takeoff (ATO) reading. Any value detected from a video log is that ATO reading, so check it if the terrain rises or falls.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="763"/>
        <source>ft</source>
        <translation>ft</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="768"/>
        <source>m</source>
        <translation>m</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="806"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation>Estimated Ground Sampling Distance (GSD):</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="827"/>
        <source>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.0//EN&quot; &quot;http://www.w3.org/TR/REC-html40/strict.dtd&quot;&gt;
&lt;html&gt;&lt;head&gt;&lt;meta name=&quot;qrichtext&quot; content=&quot;1&quot; /&gt;&lt;meta charset=&quot;utf-8&quot; /&gt;&lt;style type=&quot;text/css&quot;&gt;
p, li { white-space: pre-wrap; }
hr { height: 1px; border-width: 0; }
li.unchecked::marker { content: &quot;\2610&quot;; }
li.checked::marker { content: &quot;\2612&quot;; }
&lt;/style&gt;&lt;/head&gt;&lt;body style=&quot; font-family:&apos;Segoe UI&apos;; font-size:11pt; font-weight:400; font-style:normal;&quot;&gt;
&lt;p style=&quot;-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:&apos;MS Shell Dlg 2&apos;; font-size:9pt;&quot;&gt;&lt;br /&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="837"/>
        <source>--</source>
        <translation>--</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="876"/>
        <source>Search Target Size</source>
        <translation>Search Target Size</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="901"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Approximately how large are the objects you&apos;re wanting to identify?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="932"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="974"/>
        <source>Detection &amp; Processing</source>
        <translation>Detection &amp; Processing</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="996"/>
        <source>Are you looking for specific colors?</source>
        <translation>Are you looking for specific colors?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1041"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1072"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1145"/>
        <source>Reset</source>
        <translation>Reset</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1218"/>
        <source>Algorithm Parameters</source>
        <translation>Algorithm Parameters</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1253"/>
        <source>Close</source>
        <translation>Close</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1265"/>
        <source>Skip this streaming guide next time</source>
        <translation>Skip this streaming guide next time</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1293"/>
        <source>Back</source>
        <translation>Back</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="140"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1305"/>
        <source>Continue</source>
        <translation>Continue</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="86"/>
        <source>ADIAT Streaming Setup Guide</source>
        <translation>ADIAT Streaming Setup Guide</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="138"/>
        <source>Open Stream Viewer</source>
        <translation>Open Stream Viewer</translation>
    </message>
</context>
<context>
    <name>StreamingVideoDisplay</name>
    <message>
        <location filename="../app/core/views/streaming/components/StreamingVideoDisplay.py" line="66"/>
        <source>No Stream Connected</source>
        <translation>No Stream Connected</translation>
    </message>
</context>
<context>
    <name>TargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Hat, Helmet, Plastic Bag</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Cat, Daypack</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Large Pack, Medium Dog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Sleeping Bag, Large Dog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Small Boat, 2-Person Tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Car/SUV, Small Pickup Truck, Large Tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>House</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>More Examples:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>sqm</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>sqft</translation>
    </message>
</context>
<context>
    <name>TeamPlanningController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="47"/>
        <source>No Flagged AOIs</source>
        <translation>No Flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="49"/>
        <source>There are no flagged AOIs to assign.

Flag at least one AOI in the viewer before using Plan Verification.</source>
        <translation>There are no flagged AOIs to assign.

Flag at least one AOI in the viewer before using Plan Verification.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="210"/>
        <source>No Team Selected</source>
        <translation>No Team Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="211"/>
        <source>Select a target team (or &apos;Unassigned&apos;) in the list first.</source>
        <translation>Select a target team (or &apos;Unassigned&apos;) in the list first.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="219"/>
        <source>No AOIs Selected</source>
        <translation>No AOIs Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="221"/>
        <source>Select one or more AOIs on the map first.
Click on markers, or use Rectangle Select for area selection.</source>
        <translation>Select one or more AOIs on the map first.
Click on markers, or use Rectangle Select for area selection.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="300"/>
        <source>No AOIs</source>
        <translation>No AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="301"/>
        <source>Team &apos;{name}&apos; has no assigned AOIs.</source>
        <translation>Team &apos;{name}&apos; has no assigned AOIs.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="312"/>
        <source>Save Team PDF</source>
        <translation>Save Team PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="314"/>
        <source>PDF files (*.pdf)</source>
        <translation>PDF files (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="326"/>
        <source>Select Export Folder</source>
        <translation>Select Export Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="336"/>
        <source>Exporting Team PDFs</source>
        <translation>Exporting Team PDFs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="354"/>
        <source>Generating PDF for {name}...</source>
        <translation>Generating PDF for {name}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="365"/>
        <source>Generating master summary...</source>
        <translation>Generating master summary...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="373"/>
        <source>Export complete</source>
        <translation>Export complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="406"/>
        <source>Generating PDF Report</source>
        <translation>Generating PDF Report</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="414"/>
        <source>Done</source>
        <translation>Done</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="418"/>
        <source>Success</source>
        <translation>Success</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="419"/>
        <source>PDF report generated successfully!</source>
        <translation>PDF report generated successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="380"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="426"/>
        <source>Export Error</source>
        <translation>Export Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="381"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="427"/>
        <source>PDF generation failed: {error}</source>
        <translation>PDF generation failed: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="389"/>
        <source>Export Complete</source>
        <translation>Export Complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="390"/>
        <source>Team PDFs saved to:
{folder}</source>
        <translation>Team PDFs saved to:
{folder}</translation>
    </message>
</context>
<context>
    <name>TeamPlanningDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="55"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="65"/>
        <source>Plan Verification</source>
        <translation>Plan Verification</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="122"/>
        <source>Teams</source>
        <translation>Teams</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="124"/>
        <source>+ New</source>
        <translation>+ New</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="125"/>
        <source>Create a new field team</source>
        <translation>Create a new field team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="127"/>
        <source>✕ Remove</source>
        <translation>✕ Remove</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="128"/>
        <source>Remove the selected team</source>
        <translation>Remove the selected team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="143"/>
        <source>Assign Selection ▶</source>
        <translation>Assign Selection ▶</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="145"/>
        <source>Assign the selected AOIs on the map to the chosen team</source>
        <translation>Assign the selected AOIs on the map to the chosen team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="158"/>
        <source>Team AOIs</source>
        <translation>Team AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="172"/>
        <source>Export Team PDF</source>
        <translation>Export Team PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="174"/>
        <source>Generate a PDF report for the selected team only</source>
        <translation>Generate a PDF report for the selected team only</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="179"/>
        <source>Export All PDFs</source>
        <translation>Export All PDFs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="181"/>
        <source>Generate one PDF per team plus a master summary PDF</source>
        <translation>Generate one PDF per team plus a master summary PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="86"/>
        <source>Zoom In (+)</source>
        <translation>Zoom In (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="88"/>
        <source>Zoom Out (-)</source>
        <translation>Zoom Out (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="90"/>
        <source>Fit All (F)</source>
        <translation>Fit All (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="93"/>
        <source>Rectangle Select</source>
        <translation>Rectangle Select</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="96"/>
        <source>Draw a rectangle on the map to select multiple AOIs</source>
        <translation>Draw a rectangle on the map to select multiple AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="316"/>
        <source>Satellite View</source>
        <translation>Satellite View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="313"/>
        <source>Map View</source>
        <translation>Map View</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="195"/>
        <source>Click to select AOI • Ctrl+Click to multi-select • Use Rectangle Select for area selection • Scroll to zoom</source>
        <translation>Click to select AOI • Ctrl+Click to multi-select • Use Rectangle Select for area selection • Scroll to zoom</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="222"/>
        <source>Team</source>
        <translation>Team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>New Team</source>
        <translation>New Team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>Team name:</source>
        <translation>Team name:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="246"/>
        <source>Duplicate Name</source>
        <translation>Duplicate Name</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="247"/>
        <source>A team named &apos;{name}&apos; already exists.</source>
        <translation>A team named &apos;{name}&apos; already exists.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="265"/>
        <source>Unassigned</source>
        <translation>Unassigned</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="298"/>
        <source>No Team Selected</source>
        <translation>No Team Selected</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="299"/>
        <source>Please select a team to export.</source>
        <translation>Please select a team to export.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="305"/>
        <source>No Teams</source>
        <translation>No Teams</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="306"/>
        <source>Create at least one team before exporting.</source>
        <translation>Create at least one team before exporting.</translation>
    </message>
</context>
<context>
    <name>TelemetryHud</name>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="136"/>
        <source>LAT {value}</source>
        <translation>LAT {value}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="139"/>
        <source>LON {value}</source>
        <translation>LON {value}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="189"/>
        <source>FLY</source>
        <extracomment>Mode strings the publisher sends when it does not know the mode. Printing them verbatim put the word &quot;Unknown&quot; on the HUD next to the battery chip, where it read as a battery reading rather than as &quot;the aircraft did not report a flight mode&quot;. An em dash says that, and says it the same way every other absent field does.</extracomment>
        <translation>FLY</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="226"/>
        <source>stale {age}s</source>
        <translation>stale {age}s</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="264"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="57"/>
        <source>ALT —</source>
        <translation>ALT —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="297"/>
        <source>no AGL yet - ADIAT Flight found no terrain source here</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="300"/>
        <source>no terrain-referenced AGL available</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="302"/>
        <source>AGL source: {origin}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="310"/>
        <source>MSL — above mean sea level</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="271"/>
        <source>ALT AGL {agl} / ATO {ato} / MSL {msl} {unit}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="306"/>
        <source>AGL — above the terrain beneath the aircraft; what clearance and image scale depend on</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="308"/>
        <source>ATO — above the takeoff point (the drone&apos;s own reading); equal to AGL only over flat ground</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="324"/>
        <source>ADIAT Flight (fused)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="326"/>
        <source>laser rangefinder (ADIAT Flight)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="328"/>
        <source>downward sensor (ADIAT Flight)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="330"/>
        <source>terrain DEM (ADIAT Flight)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="332"/>
        <source>desktop DEM</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="334"/>
        <source>no terrain source — this is the takeoff-relative reading</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="339"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="91"/>
        <source>HDG —</source>
        <translation>HDG —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="343"/>
        <source>HDG {bearing:03d}° {cardinal}</source>
        <translation>HDG {bearing:03d}° {cardinal}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="349"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="98"/>
        <source>SPD —</source>
        <translation>SPD —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="355"/>
        <source>SPD {value} mph</source>
        <translation>SPD {value} mph</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="358"/>
        <source>SPD {value} m/s</source>
        <translation>SPD {value} m/s</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="43"/>
        <source>LAT —</source>
        <translation>LAT —</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="50"/>
        <source>LON —</source>
        <translation>LON —</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="105"/>
        <source>↕ —</source>
        <translation>↕ —</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="112"/>
        <source>BAT</source>
        <translation>BAT</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="119"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="133"/>
        <source>—</source>
        <translation>—</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="126"/>
        <source>MODE</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>TextLabeledSlider</name>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="259"/>
        <source>Very Conservative</source>
        <translation>Very Conservative</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="260"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="261"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="262"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="263"/>
        <source>Very Aggressive</source>
        <translation>Very Aggressive</translation>
    </message>
</context>
<context>
    <name>ThermalAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="29"/>
        <source>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</source>
        <translation>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Anomaly Type:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="45"/>
        <source>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</source>
        <translation>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="54"/>
        <source>Above or Below Mean</source>
        <translation>Above or Below Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="59"/>
        <source>Above Mean</source>
        <translation>Above Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="64"/>
        <source>Below Mean</source>
        <translation>Below Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="77"/>
        <source>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</source>
        <translation>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="81"/>
        <source>Anomaly Threshold:</source>
        <translation>Anomaly Threshold:</translation>
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
        <translation>Set the anomaly detection threshold in standard deviations.
• Range: 0 to 7 standard deviations
• Default: 4
Defines how different a temperature must be from the mean to be detected:
• Lower values (1-2): Very sensitive, detects subtle temperature differences (more detections)
• Medium values (3-5): Balanced detection (recommended for most cases)
• Higher values (6-7): Only detects extreme temperature differences (fewer detections)
Example: Value of 4 detects pixels 4 standard deviations above/below mean temperature.</translation>
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
        <translation>Number of segments to divide each thermal image into for analysis.
Each segment is analyzed independently for local thermal anomalies.
Performance impact:
• Higher number of segments: INCREASES processing time (more segments to analyze)
• Lower number of segments: DECREASES processing time (fewer segments to analyze)
• 1 segment: Fastest processing (analyzes whole image once)
Higher segment counts improve detection in scenes with temperature gradients.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="122"/>
        <source>Image Segments:</source>
        <translation>Image Segments:</translation>
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
        <translation>Select the number of segments to divide each thermal image into.
• Options: 1, 2, 4, 6, 9, 16, 25, 36 segments
• Default: 1 (analyze entire image as one segment)
The algorithm calculates mean temperature for each segment independently:
• 1 segment: Global temperature analysis (best for uniform scenes)
• More segments: Local temperature analysis (better for varying backgrounds)
Higher segment counts improve detection in scenes with temperature gradients.
Recommended: 4-9 segments for typical thermal drone imagery.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="157"/>
        <source>1</source>
        <translation>1</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="162"/>
        <source>2</source>
        <translation>2</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="167"/>
        <source>4</source>
        <translation>4</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="172"/>
        <source>6</source>
        <translation>6</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="177"/>
        <source>9</source>
        <translation>9</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="182"/>
        <source>16</source>
        <translation>16</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="187"/>
        <source>25</source>
        <translation>25</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="192"/>
        <source>36</source>
        <translation>36</translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="37"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="57"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="72"/>
        <source>Yes</source>
        <translation>Yes</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="105"/>
        <source>What type of anomalies are you looking for?</source>
        <translation>What type of anomalies are you looking for?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="122"/>
        <source>Warmer than surroundings</source>
        <translation>Warmer than surroundings</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="134"/>
        <source>Cooler than surroundings</source>
        <translation>Cooler than surroundings</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="146"/>
        <source>Both</source>
        <translation>Both</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="185"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>How aggressively should ADIAT be searching for anomalies?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="198"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Note: A higher setting will find more potential anomalies but may also increase false positives.</translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="45"/>
        <source>Very 
Conservative</source>
        <translation>Very
Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="46"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="47"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="48"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="49"/>
        <source>Very 
Aggressive</source>
        <translation>Very
Aggressive</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramChart</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="98"/>
        <source>No histogram data available</source>
        <translation>No histogram data available</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="434"/>
        <source>All Pixels</source>
        <translation>All Pixels</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="445"/>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="456"/>
        <source>AOI Pixels</source>
        <translation>AOI Pixels</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="32"/>
        <source>Thermal Histogram Unavailable</source>
        <translation>Thermal Histogram Unavailable</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="33"/>
        <source>No thermal temperature data is available for the current image.</source>
        <translation>No thermal temperature data is available for the current image.</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="14"/>
        <source>Thermal Histogram</source>
        <translation>Thermal Histogram</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="23"/>
        <source>Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.</source>
        <translation>Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="32"/>
        <source>Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Reset Zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="64"/>
        <source>Visible Temperature Range</source>
        <translation>Visible Temperature Range</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="59"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="75"/>
        <source>Minimum: --</source>
        <translation>Minimum: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="60"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="82"/>
        <source>Maximum: --</source>
        <translation>Maximum: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="105"/>
        <source>Reset Range</source>
        <translation>Reset Range</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="61"/>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="126"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="117"/>
        <source>Hover over the histogram to inspect a temperature band.</source>
        <translation>Hover over the histogram to inspect a temperature band.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="30"/>
        <source>No thermal histogram data available</source>
        <translation>No thermal histogram data available</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="131"/>
        <source>Hover band: {lower:.1f} to {upper:.1f} °{unit}</source>
        <translation>Hover band: {lower:.1f} to {upper:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="141"/>
        <source>Minimum: {minimum:.1f} °{unit}</source>
        <translation>Minimum: {minimum:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="147"/>
        <source>Maximum: {maximum:.1f} °{unit}</source>
        <translation>Maximum: {maximum:.1f} °{unit}</translation>
    </message>
</context>
<context>
    <name>ThermalRange</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
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
        <translation>Minimum temperature threshold for detection in thermal images.
• Range: -30°C to 50°C
• Default: 35°C
Defines the lower bound of the temperature detection range:
• Lower values: INCREASE detections - accepts cooler objects
• Higher values: DECREASE detections - only warmer objects detected
Combined with Maximum Temp to create a detection range (e.g., 35-40°C for human body temperature).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="38"/>
        <source>Minimum Temp (°C)</source>
        <translation>Minimum Temp (°C)</translation>
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
        <translation>Set the minimum temperature for detection in Celsius.
• Range: -30°C to 50°C
• Default: 35°C
Pixels with temperatures at or above this threshold will be detected.
• Lower values: Detect cooler objects (more detections)
• Higher values: Only detect warmer objects (fewer detections)
Note: Temperature displayed in Celsius, converted based on Preferences setting.
Use for finding objects within a specific temperature range (e.g., people 35-40°C).</translation>
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
        <translation>Maximum temperature threshold for detection in thermal images.
• Range: -30°C to 93°C
• Default: 40°C
Defines the upper bound of the temperature detection range:
• Lower values: DECREASE detections - only cooler objects detected
• Higher values: INCREASE detections - accepts warmer objects
Combined with Minimum Temp to create a detection range (e.g., 35-40°C for human body temperature).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="103"/>
        <source>Maximum Temp (°C)</source>
        <translation>Maximum Temp (°C)</translation>
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
        <translation>Set the maximum temperature for detection in Celsius.
• Range: -30°C to 93°C
• Default: 40°C
Pixels with temperatures at or below this threshold will be detected.
• Lower values: Only detect cooler objects (fewer detections)
• Higher values: Detect warmer objects (more detections)
Note: Temperature displayed in Celsius, converted based on Preferences setting.
Detection occurs for pixels between minimum and maximum temperatures (inclusive).</translation>
    </message>
</context>
<context>
    <name>ThermalRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="108"/>
        <source>Minimum Temp ({degree} F)</source>
        <translation>Minimum Temp ({degree} F)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="114"/>
        <source>Maximum Temp ({degree} F)</source>
        <translation>Maximum Temp ({degree} F)</translation>
    </message>
</context>
<context>
    <name>ThermalRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRangeWizard.ui" line="34"/>
        <source>What range of temperatures should ADIAT look for?</source>
        <translation>What range of temperatures should ADIAT look for?</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Form</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="29"/>
        <source>Type of local thermal residual anomaly to detect in radiometric imagery.
Determines whether to find warm anomalies, cool anomalies, or both.</source>
        <translation>Type of local thermal residual anomaly to detect in radiometric imagery.
Determines whether to find warm anomalies, cool anomalies, or both.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Anomaly Type:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="45"/>
        <source>Select the type of thermal residual anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to its local background estimate.</source>
        <translation>Select the type of thermal residual anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to its local background estimate.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="53"/>
        <source>Above or Below Mean</source>
        <translation>Above or Below Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="58"/>
        <source>Above Mean</source>
        <translation>Above Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="63"/>
        <source>Below Mean</source>
        <translation>Below Mean</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="92"/>
        <source>Detection sensitivity for thermal residual anomalies.
• Range: 1 to 10
• Default: 5
Lower values are more conservative (fewer detections).
Higher values are more aggressive (more detections).</source>
        <translation>Detection sensitivity for thermal residual anomalies.
• Range: 1 to 10
• Default: 5
Lower values are more conservative (fewer detections).
Higher values are more aggressive (more detections).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="99"/>
        <source>Sensitivity:</source>
        <translation>Sensitivity:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="112"/>
        <source>Adjust detection sensitivity for local thermal residual anomalies.
• 1-3: Conservative
• 4-6: Moderate
• 7-10: Aggressive</source>
        <translation>Adjust detection sensitivity for local thermal residual anomalies.
• 1-3: Conservative
• 4-6: Moderate
• 7-10: Aggressive</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="153"/>
        <source>Current sensitivity level for residual anomaly detection.</source>
        <translation>Current sensitivity level for residual anomaly detection.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="156"/>
        <source>5</source>
        <translation>5</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomalyWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="37"/>
        <source>What type of anomalies are you looking for?</source>
        <translation>What type of anomalies are you looking for?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="54"/>
        <source>Warmer than surroundings</source>
        <translation>Warmer than surroundings</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="66"/>
        <source>Cooler than surroundings</source>
        <translation>Cooler than surroundings</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="78"/>
        <source>Both</source>
        <translation>Both</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="117"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>How aggressively should ADIAT be searching for anomalies?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="130"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Note: A higher setting will find more potential anomalies but may also increase false positives.</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="33"/>
        <source>Very 
Conservative</source>
        <translation>Very
Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="34"/>
        <source>Conservative</source>
        <translation>Conservative</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="35"/>
        <source>Moderate</source>
        <translation>Moderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="36"/>
        <source>Aggressive</source>
        <translation>Aggressive</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="37"/>
        <source>Very 
Aggressive</source>
        <translation>Very
Aggressive</translation>
    </message>
</context>
<context>
    <name>TileFetchController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="150"/>
        <source>Invalid Area</source>
        <translation>Invalid Area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="151"/>
        <source>Please enter a valid bounding box.</source>
        <translation>Please enter a valid bounding box.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="154"/>
        <source>No Output Folder</source>
        <translation>No Output Folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="155"/>
        <source>Please choose an output folder.</source>
        <translation>Please choose an output folder.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="158"/>
        <source>No Dataset</source>
        <translation>No Dataset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="159"/>
        <source>Please select at least one dataset.</source>
        <translation>Please select at least one dataset.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="286"/>
        <source>No GPS Found</source>
        <translation>No GPS Found</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="287"/>
        <source>No GPS positions were found in the {source} images.</source>
        <translation>No GPS positions were found in the {source} images.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="302"/>
        <source>Select image folder</source>
        <translation>Select image folder</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="311"/>
        <source>No Images</source>
        <translation>No Images</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="312"/>
        <source>No images were found in the selected folder.</source>
        <translation>No images were found in the selected folder.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="358"/>
        <source>Replace Canopy Source?</source>
        <translation>Replace Canopy Source?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="359"/>
        <source>A LANDFIRE canopy source is currently configured.

Register the downloaded Meta/WRI canopy tiles instead? (Your LANDFIRE files stay on disk; only the selected source changes.)</source>
        <translation>A LANDFIRE canopy source is currently configured.

Register the downloaded Meta/WRI canopy tiles instead? (Your LANDFIRE files stay on disk; only the selected source changes.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Elevation (DEM)</source>
        <translation>Elevation (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Canopy height</source>
        <translation>Canopy height</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="385"/>
        <source>{product}: cancelled before completion.</source>
        <translation>{product}: cancelled before completion.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="387"/>
        <source>{product}: {failed} tile(s) failed to download.</source>
        <translation>{product}: {failed} tile(s) failed to download.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="390"/>
        <source>{product}: no data covers this area.</source>
        <translation>{product}: no data covers this area.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="392"/>
        <source>{product}: nothing was downloaded.</source>
        <translation>{product}: nothing was downloaded.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="399"/>
        <source>{product}: registered as the active source.</source>
        <translation>{product}: registered as the active source.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="402"/>
        <source>{product}: NOT registered (no usable tiles).</source>
        <translation>{product}: NOT registered (no usable tiles).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="411"/>
        <source>Download Finished with Problems</source>
        <translation>Download Finished with Problems</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="417"/>
        <source>Download Complete</source>
        <translation>Download Complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="406"/>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="413"/>
        <source>Downloaded {count} tiles.</source>
        <translation>Downloaded {count} tiles.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="428"/>
        <source>Download Cancelled</source>
        <translation>Download Cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="429"/>
        <source>The download was cancelled. No tiles were registered.</source>
        <translation>The download was cancelled. No tiles were registered.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="436"/>
        <source>Download Error</source>
        <translation>Download Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="437"/>
        <source>Tile download failed:
{error}</source>
        <translation>Tile download failed:
{error}</translation>
    </message>
</context>
<context>
    <name>TileFetchDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="48"/>
        <source>Download Coverage Data</source>
        <translation>Download Coverage Data</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="58"/>
        <source>Area of Interest (WGS84)</source>
        <translation>Area of Interest (WGS84)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="68"/>
        <source>Fill area from</source>
        <translation>Fill area from</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="73"/>
        <source>Fill the area from the loaded mission&apos;s image GPS, or from an image folder.</source>
        <translation>Fill the area from the loaded mission&apos;s image GPS, or from an image folder.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="70"/>
        <source>Loaded mission extent</source>
        <translation>Loaded mission extent</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="71"/>
        <source>Image folder...</source>
        <translation>Image folder...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="93"/>
        <source>Min longitude:</source>
        <translation>Min longitude:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="95"/>
        <source>Min latitude:</source>
        <translation>Min latitude:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="97"/>
        <source>Max longitude:</source>
        <translation>Max longitude:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="99"/>
        <source>Max latitude:</source>
        <translation>Max latitude:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="104"/>
        <source>Footprint buffer (m):</source>
        <translation>Footprint buffer (m):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="109"/>
        <source>Padding added around the camera positions so downloaded tiles cover the image footprints. Auto-sized from the mission; edit and re-fill to change.</source>
        <translation>Padding added around the camera positions so downloaded tiles cover the image footprints. Auto-sized from the mission; edit and re-fill to change.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="118"/>
        <source>Datasets</source>
        <translation>Datasets</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="120"/>
        <source>USGS 3DEP DEM</source>
        <translation>USGS 3DEP DEM</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="123"/>
        <source>USGS 3DEP provides 1 m local elevation. Optional when you already have a terrain source configured (AWS Terrain Tiles online, or downloaded 3DEP) — enable it to download higher-resolution data.</source>
        <translation>USGS 3DEP provides 1 m local elevation. Optional when you already have a terrain source configured (AWS Terrain Tiles online, or downloaded 3DEP) — enable it to download higher-resolution data.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="127"/>
        <source>Meta/WRI Canopy Height</source>
        <translation>Meta/WRI Canopy Height</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="142"/>
        <source>Store in:</source>
        <translation>Store in:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="144"/>
        <source>Central tile library (recommended)</source>
        <translation>Central tile library (recommended)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="146"/>
        <source>Mission results folder</source>
        <translation>Mission results folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="147"/>
        <source>Custom folder...</source>
        <translation>Custom folder...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="149"/>
        <source>The central library collects tiles from all missions in one place (they merge, nothing gets replaced) and registers automatically. Choose the results folder or a custom folder to keep tiles beside a specific mission instead.</source>
        <translation>The central library collects tiles from all missions in one place (they merge, nothing gets replaced) and registers automatically. Choose the results folder or a custom folder to keep tiles beside a specific mission instead.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="158"/>
        <source>Output folder:</source>
        <translation>Output folder:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="162"/>
        <source>Browse...</source>
        <translation>Browse...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="168"/>
        <source>Register in Preferences when complete</source>
        <translation>Register in Preferences when complete</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="177"/>
        <source>Download</source>
        <translation>Download</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="180"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="206"/>
        <source>This area is already covered by your registered tiles.</source>
        <translation>This area is already covered by your registered tiles.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="208"/>
        <source>Partially covered by your registered tiles — downloading fills the gaps.</source>
        <translation>Partially covered by your registered tiles — downloading fills the gaps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="214"/>
        <source>Your downloaded 1 m tiles don&apos;t include this area — without this download, online AWS Terrain Tiles (~30 m) are used here instead.</source>
        <translation>Your downloaded 1 m tiles don&apos;t include this area — without this download, online AWS Terrain Tiles (~30 m) are used here instead.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="217"/>
        <source>Your downloaded canopy tiles don&apos;t include this area — without this download, POD runs with no canopy attenuation here.</source>
        <translation>Your downloaded canopy tiles don&apos;t include this area — without this download, POD runs with no canopy attenuation here.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="222"/>
        <source>No local elevation tiles registered — online AWS Terrain Tiles (~30 m) serve as the baseline.</source>
        <translation>No local elevation tiles registered — online AWS Terrain Tiles (~30 m) serve as the baseline.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="224"/>
        <source>No canopy source is configured yet.</source>
        <translation>No canopy source is configured yet.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="276"/>
        <source>Select output folder</source>
        <translation>Select output folder</translation>
    </message>
</context>
<context>
    <name>TrackGalleryWidget</name>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="41"/>
        <source>Detection Gallery</source>
        <translation>Detection Gallery</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="82"/>
        <source>0 detections</source>
        <translation>0 detections</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="149"/>
        <source>1 detection</source>
        <translation>1 detection</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="151"/>
        <source>{count} detections</source>
        <translation>{count} detections</translation>
    </message>
</context>
<context>
    <name>UnifiedMapExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="439"/>
        <source>No Data Selected</source>
        <translation>No Data Selected</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="440"/>
        <source>Please select at least one type of data to export.</source>
        <translation>Please select at least one type of data to export.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="470"/>
        <source>Select folder for POD coverage files</source>
        <translation>Select folder for POD coverage files</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="478"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="585"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="886"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="924"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="969"/>
        <source>Export Error</source>
        <translation>Export Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="479"/>
        <source>An error occurred during export:
{error}</source>
        <translation>An error occurred during export:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="497"/>
        <source>Save Map Export</source>
        <translation>Save Map Export</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="499"/>
        <source>KML files (*.kml);;KMZ files (*.kmz)</source>
        <translation>KML files (*.kml);;KMZ files (*.kmz)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="586"/>
        <source>Failed to export to KML:
{error}</source>
        <translation>Failed to export to KML:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="653"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="845"/>
        <source>POD Error</source>
        <translation>POD Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="654"/>
        <source>Could not start the POD calculation:
{error}</source>
        <translation>Could not start the POD calculation:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="704"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="716"/>
        <source>POD coverage complete</source>
        <translation>POD coverage complete</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="713"/>
        <source>POD coverage complete — {count} frame(s) used online elevation (outside local DEM)</source>
        <translation>POD coverage complete — {count} frame(s) used online elevation (outside local DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="721"/>
        <source>POD complete — {skipped} of {total} frames skipped</source>
        <translation>POD complete — {skipped} of {total} frames skipped</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="724"/>
        <source>({count} without elevation data)</source>
        <translation>({count} without elevation data)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="732"/>
        <source>(canopy data covered {pct}% of the searched area)</source>
        <translation>(canopy data covered {pct}% of the searched area)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="808"/>
        <source>Terrain and canopy aware probability-of-detection heatmap.</source>
        <translation>Terrain and canopy aware probability-of-detection heatmap.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="812"/>
        <source>Mean POD over covered area: {pod}%</source>
        <translation>Mean POD over covered area: {pod}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="815"/>
        <source>POD Coverage</source>
        <translation>POD Coverage</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="823"/>
        <source>POD Overlay</source>
        <translation>POD Overlay</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="824"/>
        <source>The POD coverage was computed, but embedding it into the exported file failed:
{error}

The POD GeoTIFF products were still written next to the export.</source>
        <translation>The POD coverage was computed, but embedding it into the exported file failed:
{error}

The POD GeoTIFF products were still written next to the export.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="837"/>
        <source>POD calculation cancelled</source>
        <translation>POD calculation cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="846"/>
        <source>POD calculation failed:
{error}</source>
        <translation>POD calculation failed:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="887"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="925"/>
        <source>Failed to export to CalTopo:
{error}</source>
        <translation>Failed to export to CalTopo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="941"/>
        <source>Map export completed successfully!</source>
        <translation>Map export completed successfully!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="956"/>
        <source>Map export cancelled</source>
        <translation>Map export cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="970"/>
        <source>Map export failed:
{error}</source>
        <translation>Map export failed:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="743"/>
        <source>(takeoff elevation {elev})</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="747"/>
        <source>(no takeoff elevation — POD is approximate over changing terrain)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="754"/>
        <source>{value} ft</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="755"/>
        <source>{value} m</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>UpdateController</name>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="52"/>
        <source>Disabled while Offline Only mode is enabled.</source>
        <translation>Disabled while Offline Only mode is enabled.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="56"/>
        <source>Check the update feed for a newer ADIAT installer.</source>
        <translation>Check the update feed for a newer ADIAT installer.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="85"/>
        <source>Updates Disabled</source>
        <translation>Updates Disabled</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="87"/>
        <source>Update checks are disabled while Offline Only mode is enabled.</source>
        <translation>Update checks are disabled while Offline Only mode is enabled.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="101"/>
        <source>Update Check Failed</source>
        <translation>Update Check Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="102"/>
        <source>Unable to check for updates:
{error}</source>
        <translation>Unable to check for updates:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="110"/>
        <source>No Updates Available</source>
        <translation>No Updates Available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="112"/>
        <source>You are already running the latest available version of ADIAT.</source>
        <translation>You are already running the latest available version of ADIAT.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="130"/>
        <source>Installer Launch Failed</source>
        <translation>Installer Launch Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="131"/>
        <source>The installer was downloaded but could not be launched:
{error}</source>
        <translation>The installer was downloaded but could not be launched:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="137"/>
        <source>Installer Started</source>
        <translation>Installer Started</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="139"/>
        <source>The installer has been launched. Close ADIAT when you are ready to continue the update.</source>
        <translation>The installer has been launched. Close ADIAT when you are ready to continue the update.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="148"/>
        <source>Update Available</source>
        <translation>Update Available</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="150"/>
        <source>ADIAT {new_version} is available. You are running {current_version}.</source>
        <translation>ADIAT {new_version} is available. You are running {current_version}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="156"/>
        <source>Do you want to download and launch the installer now?</source>
        <translation>Do you want to download and launch the installer now?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="159"/>
        <source>Download and Install</source>
        <translation>Download and Install</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="168"/>
        <source>Downloading ADIAT {version}...</source>
        <translation>Downloading ADIAT {version}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="169"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="174"/>
        <source>Downloading Update</source>
        <translation>Downloading Update</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="190"/>
        <location filename="../app/core/controllers/UpdateController.py" line="192"/>
        <source>{value} MB</source>
        <translation>{value} MB</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="193"/>
        <source>unknown</source>
        <translation>unknown</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="196"/>
        <source>Downloading ADIAT {version}...
{downloaded} of {total}</source>
        <translation>Downloading ADIAT {version}...
{downloaded} of {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="204"/>
        <location filename="../app/core/controllers/UpdateController.py" line="210"/>
        <source>Update download canceled.</source>
        <translation>Update download canceled.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="215"/>
        <source>Download Failed</source>
        <translation>Download Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="216"/>
        <source>Unable to download the update installer:
{error}</source>
        <translation>Unable to download the update installer:
{error}</translation>
    </message>
</context>
<context>
    <name>UpscaleDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="187"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="367"/>
        <source>Upscaled View - {level}x</source>
        <translation>Upscaled View - {level}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="229"/>
        <source>Upscale Method:</source>
        <translation>Upscale Method:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="233"/>
        <source>Auto (Recommended)</source>
        <translation>Auto (Recommended)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="234"/>
        <source>Fast (Lanczos)</source>
        <translation>Fast (Lanczos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="236"/>
        <source>Balanced (OpenCV EDSR)</source>
        <translation>Balanced (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="264"/>
        <source>Upres Again</source>
        <translation>Upres Again</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="267"/>
        <source>Upscale the currently visible portion by {factor}x</source>
        <translation>Upscale the currently visible portion by {factor}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="271"/>
        <source>Quit</source>
        <translation>Quit</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="274"/>
        <source>Close this upscale window</source>
        <translation>Close this upscale window</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="302"/>
        <source>Resolution: {width} × {height} pixels | Original: {orig_w} × {orig_h} pixels | Upscale: {level}x | Use mouse wheel to zoom, right-click to pan</source>
        <translation>Resolution: {width} × {height} pixels | Original: {orig_w} × {orig_h} pixels | Upscale: {level}x | Use mouse wheel to zoom, right-click to pan</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="375"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="387"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="532"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="564"/>
        <source>Upscale Error</source>
        <translation>Upscale Error</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="376"/>
        <source>Error during initial upscale: {error}</source>
        <translation>Error during initial upscale: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="388"/>
        <source>Unable to extract visible image portion.</source>
        <translation>Unable to extract visible image portion.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="397"/>
        <source>Maximum Upscale Reached</source>
        <translation>Maximum Upscale Reached</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="399"/>
        <source>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</source>
        <translation>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="413"/>
        <source>Image Too Large</source>
        <translation>Image Too Large</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="415"/>
        <source>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</source>
        <translation>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="426"/>
        <source>Image Too Small</source>
        <translation>Image Too Small</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="428"/>
        <source>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</source>
        <translation>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="468"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="565"/>
        <source>An error occurred during upscaling:
{error}</source>
        <translation>An error occurred during upscaling:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="487"/>
        <source>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</source>
        <translation>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="760"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="504"/>
        <source>Upscaling (OpenCV EDSR)</source>
        <translation>Upscaling (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="533"/>
        <source>Failed to start upscaling:
{error}</source>
        <translation>Failed to start upscaling:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="603"/>
        <source>Method Not Available</source>
        <translation>Method Not Available</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="605"/>
        <source>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</source>
        <translation>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="759"/>
        <source>Downloading {model_name} model...</source>
        <translation>Downloading {model_name} model...</translation>
    </message>
</context>
<context>
    <name>VideoParser</name>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="14"/>
        <source>Video Parser</source>
        <translation>Video Parser</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="45"/>
        <source>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</source>
        <translation>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="62"/>
        <location filename="../resources/views/images/VideoParser.ui" line="178"/>
        <source>Optional. ADIAT already finds location data on its own, from:
• an .SRT file sitting next to the video
• telemetry embedded in the video (newer DJI aircraft)

Choose a file here only to override that, or to supply location data the video does not have. Supports DJI .SRT and .CSV flight logs (Skydio and similar).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="69"/>
        <source>Optional. ADIAT automatically uses an .SRT file sitting next to the video, or telemetry embedded inside the video (as newer DJI aircraft record it). Choose a file here only to override that, or to supply location data the video does not have. Supports DJI .SRT and .CSV flight logs (Skydio and similar).</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="72"/>
        <source>Location Data (optional):</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="84"/>
        <source>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</source>
        <translation>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="88"/>
        <source>Output Folder:</source>
        <translation>Output Folder:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="100"/>
        <source>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</source>
        <translation>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="117"/>
        <source>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</source>
        <translation>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="121"/>
        <location filename="../resources/views/images/VideoParser.ui" line="163"/>
        <location filename="../resources/views/images/VideoParser.ui" line="204"/>
        <source>Select</source>
        <translation>Select</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="131"/>
        <source>folder.png</source>
        <translation>folder.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="143"/>
        <source>Select the source video file to parse.
Video will be split into individual frame images.</source>
        <translation>Select the source video file to parse.
Video will be split into individual frame images.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="147"/>
        <source>Video File:</source>
        <translation>Video File:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="159"/>
        <source>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</source>
        <translation>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="185"/>
        <source>Optional - usually detected automatically</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="200"/>
        <source>Browse for an SRT or CSV file with the flight&apos;s location data.
Not needed for most videos, which already carry it.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="305"/>
        <source>Start extracting frames from the video file.
Requirements:
• Video file must be selected
• Output folder must be selected
• Time interval must be set (default: 5 seconds)
The process will extract frames at the specified interval and save them as images.
If a metadata file (SRT or CSV) is provided, GPS metadata will be embedded in the extracted frames.</source>
        <translation>Start extracting frames from the video file.
Requirements:
• Video file must be selected
• Output folder must be selected
• Time interval must be set (default: 5 seconds)
The process will extract frames at the specified interval and save them as images.
If a metadata file (SRT or CSV) is provided, GPS metadata will be embedded in the extracted frames.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="223"/>
        <source>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</source>
        <translation>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="228"/>
        <source>Time Interval (seconds):</source>
        <translation>Time Interval (seconds):</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="240"/>
        <source>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</source>
        <translation>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="324"/>
        <source>Start</source>
        <translation>Start</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="355"/>
        <source>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</source>
        <translation>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="364"/>
        <source> Cancel</source>
        <translation> Cancel</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="371"/>
        <source>cancel.png</source>
        <translation>cancel.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="401"/>
        <source>Progress and status output window.
Displays real-time information during frame extraction:
• Current frame being processed
• Frame timestamps and numbers
• GPS coordinates (if SRT file is provided)
• Progress percentage and completion status
• Any errors or warnings encountered
Shows total frames extracted when complete.</source>
        <translation>Progress and status output window.
Displays real-time information during frame extraction:
• Current frame being processed
• Frame timestamps and numbers
• GPS coordinates (if SRT file is provided)
• Progress percentage and completion status
• Any errors or warnings encountered
Shows total frames extracted when complete.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="57"/>
        <source>Select a Video File</source>
        <translation>Select a Video File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="72"/>
        <source>Select a Metadata File</source>
        <translation>Select a Metadata File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="73"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv)</source>
        <translation>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="90"/>
        <source>Select Directory</source>
        <translation>Select Directory</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="110"/>
        <source>Please set the video file and output directory.</source>
        <translation>Please set the video file and output directory.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="115"/>
        <source>--- Starting video processing ---</source>
        <translation>--- Starting video processing ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="164"/>
        <source>Confirmation</source>
        <translation>Confirmation</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="165"/>
        <source>Are you sure you want to cancel the video processing in progress?</source>
        <translation>Are you sure you want to cancel the video processing in progress?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="201"/>
        <source>--- Video Processing Completed ---</source>
        <translation>--- Video Processing Completed ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="203"/>
        <source>{count} images created</source>
        <translation>{count} images created</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="256"/>
        <source>Error Starting Processing</source>
        <translation>Error Starting Processing</translation>
    </message>
</context>
<context>
    <name>Viewer</name>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</source>
        <translation>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="112"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="133"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="994"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1165"/>
        <source>TextLabel</source>
        <translation>TextLabel</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="161"/>
        <source>View keyboard shortcuts and help</source>
        <translation>View keyboard shortcuts and help</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="199"/>
        <source>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</source>
        <translation>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="501"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="205"/>
        <source>Show Overlay</source>
        <translation>Show Overlay</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1343"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="225"/>
        <source>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</source>
        <translation>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="255"/>
        <source>Highlight Pixels of Interest(H)</source>
        <translation>Highlight Pixels of Interest(H)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="277"/>
        <source>Show AOIs</source>
        <translation>Show AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1363"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="328"/>
        <source>Open Histogram</source>
        <translation>Open Histogram</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="344"/>
        <source>Map with Image Locations (M)</source>
        <translation>Map with Image Locations (M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="360"/>
        <source>North-Oriented View of Image (R)</source>
        <translation>North-Oriented View of Image (R)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="376"/>
        <source>Adjust Image (Ctrl+H)</source>
        <translation>Adjust Image (Ctrl+H)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="379"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="407"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="430"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="449"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="485"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="529"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="566"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="608"/>
        <source>...</source>
        <translation>...</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="392"/>
        <source>adjustments.png</source>
        <translation>adjustments.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="404"/>
        <source>Measure Distance (Ctrl+M)</source>
        <translation>Measure Distance (Ctrl+M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="420"/>
        <source>ruler.png</source>
        <translation>ruler.png</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2157"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="427"/>
        <source>Person Size Reference (Ctrl+P)</source>
        <translation>Person Size Reference (Ctrl+P)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="299"/>
        <source>Toggle the measurement ruler drawn over the selected AOI</source>
        <translation>Toggle the measurement ruler drawn over the selected AOI</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="439"/>
        <source>person.png</source>
        <translation>person.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="446"/>
        <source>Toggle Grid Review Mode (S) — sweep the image cell by cell; Shift+S for grid settings</source>
        <translation>Toggle Grid Review Mode (S) — sweep the image cell by cell; Shift+S for grid settings</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="461"/>
        <source>grid.png</source>
        <translation>grid.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="468"/>
        <source>Toggle Magnifying Glass (Middle Mouse)</source>
        <translation>Toggle Magnifying Glass (Middle Mouse)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="498"/>
        <source>magnify.png</source>
        <translation>magnify.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="512"/>
        <source>Map Export (KML / CalTopo)</source>
        <translation>Map Export (KML / CalTopo)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="542"/>
        <source>map.png</source>
        <translation>map.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="549"/>
        <source>Generate PDF Report</source>
        <translation>Generate PDF Report</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="579"/>
        <source>pdf.png</source>
        <translation>pdf.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="591"/>
        <source>Generate Zip Bundle</source>
        <translation>Generate Zip Bundle</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="621"/>
        <source>zip.png</source>
        <translation>zip.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="646"/>
        <source>Skip hidden images when navigating.
When enabled, Previous/Next buttons will skip over images marked as hidden.
Use to focus on images that haven&apos;t been reviewed or marked for exclusion.
Keyboard shortcut: H to hide/unhide current image</source>
        <translation>Skip hidden images when navigating.
When enabled, Previous/Next buttons will skip over images marked as hidden.
Use to focus on images that haven&apos;t been reviewed or marked for exclusion.
Keyboard shortcut: H to hide/unhide current image</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="652"/>
        <source>Skip Hidden</source>
        <translation>Skip Hidden</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="691"/>
        <source>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</source>
        <translation>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="698"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="718"/>
        <source>Hide Image</source>
        <translation>Hide Image</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="710"/>
        <source>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</source>
        <translation>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="746"/>
        <source>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</source>
        <translation>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="751"/>
        <source>Jump To:</source>
        <translation>Jump To:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="776"/>
        <source>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</source>
        <translation>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="790"/>
        <source>Jump to a specific AOI by its run-wide number.
Enter an AOI number and press Enter to select and scroll to it.</source>
        <translation>Jump to a specific AOI by its run-wide number.
Enter an AOI number and press Enter to select and scroll to it.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="794"/>
        <source>Go to AOI #:</source>
        <translation>Go to AOI #:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="819"/>
        <source>Enter an AOI number and press Enter.
Selects that AOI and scrolls it into view in the gallery or single-image list.</source>
        <translation>Enter an AOI number and press Enter.
Selects that AOI and scrolls it into view in the gallery or single-image list.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="832"/>
        <source>Previous Image</source>
        <translation>Previous Image</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="839"/>
        <source>previous.png</source>
        <translation>previous.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="854"/>
        <source>Next Image</source>
        <translation>Next Image</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="861"/>
        <source>next.png</source>
        <translation>next.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1004"/>
        <source>Filter AOIs by color and pixel area</source>
        <translation>Filter AOIs by color and pixel area</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1076"/>
        <source>Sort By</source>
        <translation>Sort By</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1088"/>
        <source>Sort Areas of Interest (AOIs) in the list.
Choose how to order the detected objects:
• Pixel Area: Sort by size (largest to smallest)
• Distance: Sort by distance from image center or reference point
• Color: Group by similar colors
• Detection Order: Original order from analysis
Sorting helps prioritize review of larger or closer objects.</source>
        <translation>Sort Areas of Interest (AOIs) in the list.
Choose how to order the detected objects:
• Pixel Area: Sort by size (largest to smallest)
• Distance: Sort by distance from image center or reference point
• Color: Group by similar colors
• Detection Order: Original order from analysis
Sorting helps prioritize review of larger or closer objects.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1176"/>
        <source>Open</source>
        <translation>Open</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="138"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="150"/>
        <source>Reading result file...</source>
        <translation>Reading result file...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="167"/>
        <source>Checking image dimensions ({n} images)...</source>
        <translation>Checking image dimensions ({n} images)...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="177"/>
        <source>Validating image paths...</source>
        <translation>Validating image paths...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="184"/>
        <source>Load Results Failed</source>
        <translation>Load Results Failed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="186"/>
        <source>Cannot load results without valid image and mask locations.

The viewer will now close.</source>
        <translation>Cannot load results without valid image and mask locations.

The viewer will now close.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="193"/>
        <source>Scanning source folder for full flight...</source>
        <translation>Scanning source folder for full flight...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="209"/>
        <source>Initialising controllers...</source>
        <translation>Initialising controllers...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="220"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1606"/>
        <source>Skip Hidden ({count}) </source>
        <translation>Skip Hidden ({count}) </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="252"/>
        <source>Loading detection results from {n} images...</source>
        <translation>Loading detection results from {n} images...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="304"/>
        <source>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</source>
        <translation>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="344"/>
        <source>Loading first image...</source>
        <translation>Loading first image...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="359"/>
        <source>Preparing thumbnails...</source>
        <translation>Preparing thumbnails...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="719"/>
        <source>No Dataset</source>
        <translation>No Dataset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="720"/>
        <source>No dataset is currently loaded.</source>
        <translation>No dataset is currently loaded.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="727"/>
        <source>Generate Cache</source>
        <translation>Generate Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="729"/>
        <source>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</source>
        <translation>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="742"/>
        <source>Initializing cache generation...</source>
        <translation>Initializing cache generation...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="743"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="748"/>
        <source>Generating Cache</source>
        <translation>Generating Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="785"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="786"/>
        <source>Failed to start cache generation:
{error}</source>
        <translation>Failed to start cache generation:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="804"/>
        <source>Cache Generated</source>
        <translation>Cache Generated</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="806"/>
        <source>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</source>
        <translation>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="837"/>
        <source>Cache Generation Error</source>
        <translation>Cache Generation Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="839"/>
        <source>An error occurred during cache generation:

{error}</source>
        <translation>An error occurred during cache generation:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1026"/>
        <source>AOI Not Visible</source>
        <translation>AOI Not Visible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1028"/>
        <source>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</source>
        <translation>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1222"/>
        <source>Update Image Dimensions</source>
        <translation>Update Image Dimensions</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1224"/>
        <source>This dataset is missing image dimensions needed for heatmap filtering ({count} images).

Would you like to read dimensions from the image files and update the results file?</source>
        <translation>This dataset is missing image dimensions needed for heatmap filtering ({count} images).

Would you like to read dimensions from the image files and update the results file?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1263"/>
        <source>Reading image dimensions ({done}/{total})...</source>
        <translation>Reading image dimensions ({done}/{total})...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1354"/>
        <source>Show Pixels of Interest (H or Ctrl+I)</source>
        <translation>Show Pixels of Interest (H or Ctrl+I)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1369"/>
        <source>Toggle AOI Circles</source>
        <translation>Toggle AOI Circles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1376"/>
        <source>Toggle AOI Ruler</source>
        <translation>Toggle AOI Ruler</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1792"/>
        <source>Missing Dependency</source>
        <translation>Missing Dependency</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1794"/>
        <source>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</source>
        <translation>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1803"/>
        <source>Upscale Error</source>
        <translation>Upscale Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1805"/>
        <source>An error occurred while opening the upscale dialog:
{error}</source>
        <translation>An error occurred while opening the upscale dialog:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2161"/>
        <source>Person Size Reference is unavailable: no GSD for this image</source>
        <translation>Person Size Reference is unavailable: no GSD for this image</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2258"/>
        <source>Unknown Reviewer</source>
        <translation>Unknown Reviewer</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2321"/>
        <source>Loading gallery...</source>
        <translation>Loading gallery...</translation>
    </message>
</context>
<context>
    <name>WaldoClockCorrectionDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="77"/>
        <source>WALDO Camera Clock Correction</source>
        <translation>WALDO Camera Clock Correction</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="99"/>
        <source>The camera clock on these images appears to be misconfigured:</source>
        <translation>The camera clock on these images appears to be misconfigured:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="108"/>
        <source>ADIAT can stamp a corrected capture time into the image metadata. This is non-destructive: the original EXIF fields are not changed, and sun/shadow calculations will use the corrected time. Check the preview against when the flight actually flew - if it is off by 12 hours, adjust the clock face error.</source>
        <translation>ADIAT can stamp a corrected capture time into the image metadata. This is non-destructive: the original EXIF fields are not changed, and sun/shadow calculations will use the corrected time. Check the preview against when the flight actually flew - if it is off by 12 hours, adjust the clock face error.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="120"/>
        <source> hours</source>
        <translation> hours</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="121"/>
        <source>Clock face error to remove:</source>
        <translation>Clock face error to remove:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="128"/>
        <source>IANA time zone name (e.g. America/Los_Angeles) or a fixed UTC offset in hours (e.g. -7)</source>
        <translation>IANA time zone name (e.g. America/Los_Angeles) or a fixed UTC offset in hours (e.g. -7)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="130"/>
        <source>True camera time zone:</source>
        <translation>True camera time zone:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="139"/>
        <source>Remember my choice for this folder</source>
        <translation>Remember my choice for this folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="159"/>
        <source>Apply Correction</source>
        <translation>Apply Correction</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="163"/>
        <source>Not Now</source>
        <translation>Not Now</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="166"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="170"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="231"/>
        <source>Enter a valid time zone (IANA name or UTC offset in hours).</source>
        <translation>Enter a valid time zone (IANA name or UTC offset in hours).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="239"/>
        <source>{name}: camera says {before}  →  corrected {after}</source>
        <translation>{name}: camera says {before}  →  corrected {after}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="245"/>
        <source>Correction preview unavailable.</source>
        <translation>Correction preview unavailable.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="272"/>
        <source>Stamping corrected capture times...</source>
        <translation>Stamping corrected capture times...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="292"/>
        <source>Cancelling...</source>
        <translation>Cancelling...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="308"/>
        <source>Corrected:        {n}</source>
        <translation>Corrected:        {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="309"/>
        <source>Already corrected: {n}</source>
        <translation>Already corrected: {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="310"/>
        <source>Errors:           {n}</source>
        <translation>Errors:           {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="313"/>
        <source>Cancelled - remaining images are uncorrected.</source>
        <translation>Cancelled - remaining images are uncorrected.</translation>
    </message>
</context>
<context>
    <name>WaldoFlightLogDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="126"/>
        <source>WALDO Flight Track Log</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="150"/>
        <source>An aircraft track log can supply the true per-image camera attitude (bank and pitch) and a GPS-accurate capture time, making image footprints and AOI positions substantially more accurate.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="162"/>
        <source>Remember my choice for this folder</source>
        <translation type="unfinished">Remember my choice for this folder</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="171"/>
        <source>Reading image metadata...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="182"/>
        <source>Apply Flight Log</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="186"/>
        <source>Not Now</source>
        <translation type="unfinished">Not Now</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="190"/>
        <source>Cancel</source>
        <translation type="unfinished">Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="193"/>
        <source>OK</source>
        <translation type="unfinished">OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="246"/>
        <source>The track log does not match these images: {reason}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="258"/>
        <source>Camera clock is {n:.1f} s {direction} of GPS time</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="259"/>
        <source>ahead</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="259"/>
        <source>behind</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="261"/>
        <source>Track log: {name}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="263"/>
        <source>Images sit {d:.0f} m from the flight track on average ({p:.0%} matched)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="269"/>
        <source>Attitude channel verified against turn physics (correlation {c:.2f}, recorded {lag:+.0f} s late)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="273"/>
        <source>Bank during capture: {lo:+.1f}° to {hi:+.1f}°</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="277"/>
        <source>Attitude channel is NOT reliable (correlation {c:.2f}) - only the capture-time refinement will be stamped</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="305"/>
        <source>Stamping flight-log attitude...</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="324"/>
        <source>Cancelling...</source>
        <translation type="unfinished">Cancelling...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="347"/>
        <source>Stamped:          {n}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="348"/>
        <source>Already current:  {n}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="349"/>
        <source>Errors:           {n}</source>
        <translation type="unfinished">Errors:           {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="355"/>
        <source>Cancelled - remaining images are unstamped.</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>WaldoPrePassDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="58"/>
        <source>Preparing WALDO Images</source>
        <translation>Preparing WALDO Images</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="70"/>
        <source>Synthesising WALDO metadata...</source>
        <translation>Synthesising WALDO metadata...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="82"/>
        <source>Initialising...</source>
        <translation>Initialising...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="93"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="96"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="146"/>
        <source>WALDO Pre-Pass Complete</source>
        <translation>WALDO Pre-Pass Complete</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="147"/>
        <source>WALDO Pre-Pass Cancelled</source>
        <translation>WALDO Pre-Pass Cancelled</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="154"/>
        <source>Processed:        {n}</source>
        <translation>Processed:        {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="155"/>
        <source>Already up-to-date: {n}</source>
        <translation>Already up-to-date: {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="156"/>
        <source>Skipped (non-WALDO): {n}</source>
        <translation>Skipped (non-WALDO): {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="157"/>
        <source>Errors:           {n}</source>
        <translation>Errors:           {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="164"/>
        <source>⚠ Metadata warnings:</source>
        <translation>⚠ Metadata warnings:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="169"/>
        <source>Per-image errors:</source>
        <translation>Per-image errors:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="183"/>
        <source>Cancelling...</source>
        <translation>Cancelling...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="184"/>
        <source>Cancellation requested...</source>
        <translation>Cancellation requested...</translation>
    </message>
</context>
<context>
    <name>WingtraDataDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="44"/>
        <source>Wingtra Data Import</source>
        <translation>Wingtra Data Import</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="54"/>
        <source>Import Summary</source>
        <translation>Import Summary</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="58"/>
        <source>&lt;b&gt;Matched images:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV entries without match:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Result images without CSV data:&lt;/b&gt; {unmatched_images}</source>
        <translation>&lt;b&gt;Matched images:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV entries without match:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Result images without CSV data:&lt;/b&gt; {unmatched_images}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="73"/>
        <source>Altitude &amp; GSD</source>
        <translation>Altitude &amp; GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="78"/>
        <source>&lt;b&gt;AGL computed from terrain:&lt;/b&gt; {agl_count} of {matched_count} images&lt;br&gt;&lt;br&gt;Per-image AGL is derived from the CSV altitude (ASL) minus terrain elevation at each GPS location. GSD will be calculated automatically using the camera sensor data and focal length.</source>
        <translation>&lt;b&gt;AGL computed from terrain:&lt;/b&gt; {agl_count} of {matched_count} images&lt;br&gt;&lt;br&gt;Per-image AGL is derived from the CSV altitude (ASL) minus terrain elevation at each GPS location. GSD will be calculated automatically using the camera sensor data and focal length.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="89"/>
        <source>&lt;b&gt;Terrain data unavailable&lt;/b&gt; - AGL could not be computed.&lt;br&gt;&lt;br&gt;Orientation (yaw/pitch/roll) will still be applied from the CSV. GSD and altitude displays require terrain data or a manual altitude override (Shift+O) after import.</source>
        <translation>&lt;b&gt;Terrain data unavailable&lt;/b&gt; - AGL could not be computed.&lt;br&gt;&lt;br&gt;Orientation (yaw/pitch/roll) will still be applied from the CSV. GSD and altitude displays require terrain data or a manual altitude override (Shift+O) after import.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="106"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="110"/>
        <source>Apply Wingtra Data</source>
        <translation>Apply Wingtra Data</translation>
    </message>
</context>
<context>
    <name>ZipExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="130"/>
        <source>Save Zip File</source>
        <translation>Save Zip File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="132"/>
        <source>Zip files (*.zip)</source>
        <translation>Zip files (*.zip)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="163"/>
        <source>No images to export</source>
        <translation>No images to export</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="397"/>
        <source>ZIP file created</source>
        <translation>ZIP file created</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="403"/>
        <source>Failed to generate Zip file: {error}</source>
        <translation>Failed to generate Zip file: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="424"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
</context>
<context>
    <name>ZipExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="18"/>
        <source>ZIP Export Options</source>
        <translation>ZIP Export Options</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="26"/>
        <source>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</source>
        <translation>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="34"/>
        <source>Export Native data (original files + XML)</source>
        <translation>Export Native data (original files + XML)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="35"/>
        <source>Export Augmented images (viewer overlays + metadata)</source>
        <translation>Export Augmented images (viewer overlays + metadata)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="50"/>
        <source>Include images without flagged AOIs</source>
        <translation>Include images without flagged AOIs</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="53"/>
        <source>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</source>
        <translation>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="59"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="60"/>
        <source>Cancel</source>
        <translation>Cancel</translation>
    </message>
</context>
<context>
    <name>_CalibrateWorker</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="66"/>
        <source>No images with resolvable GPS + capture time.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="68"/>
        <source>No ForeFlight track log found for this folder.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoFlightLogDialog.py" line="73"/>
        <source>Calibrating {name}...</source>
        <translation type="unfinished"></translation>
    </message>
</context>
<context>
    <name>controller</name>
    <message>
        <location filename="../app/tests/core/controllers/images/test_status_controller_altitude.py" line="56"/>
        <source>Altitude</source>
        <translation type="unfinished"></translation>
    </message>
</context>
</TS>
