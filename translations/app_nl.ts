<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="nl_NL">
<context>
    <name>AIPersonDetector</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="27"/>
        <source>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</source>
        <translation>Betrouwbaarheidsdrempel voor AI-persoonsdetectie.
Bepaalt het minimale betrouwbaarheidsniveau dat vereist is om een persoonsdetectie te melden.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="31"/>
        <source>Confidence Threshold</source>
        <translation>Betrouwbaarheidsdrempel</translation>
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
        <translation>Pas de betrouwbaarheidsdrempel voor persoonsdetectie aan.
• Bereik: 0% tot 100% (schuifregelaar -1 tot 100, -1 wordt weergegeven als 0%)
• Standaard: 50%
Het AI-model kent aan elke persoonsdetectie een betrouwbaarheidsscore toe:
• Lagere waarden (0-30%): accepteer detecties met lage betrouwbaarheid (meer detecties, meer valse positieven)
• Gemiddelde waarden (31-60%): gebalanceerde detectie (aanbevolen voor de meeste gevallen)
• Hogere waarden (61-100%): accepteer alleen detecties met hoge betrouwbaarheid (minder detecties, minder valse positieven)
De betrouwbaarheid vertegenwoordigt de zekerheid van het AI-model dat een gedetecteerd object een persoon is.
Begin met 50% en pas aan op basis van uw nauwkeurigheidsvereisten.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="81"/>
        <source>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</source>
        <translation>Huidig percentage van de betrouwbaarheidsdrempel.
Toont de waarde die is geselecteerd op de betrouwbaarheidsschuifregelaar (0-100%).
Detecties onder dit betrouwbaarheidsniveau worden uitgefilterd.</translation>
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
        <translation>GPU-status en beschikbaarheidsinformatie.
Toont of GPU-versnelling beschikbaar is voor AI-persoonsdetectie.
• GPU beschikbaar: AI-detectie gebruikt de GPU voor snellere verwerking
• Alleen CPU: AI-detectie gebruikt de CPU (langzamer maar nog steeds functioneel)
GPU-versnelling verbetert de verwerkingssnelheid van AI-modellen aanzienlijk.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="107"/>
        <source>GPU Label</source>
        <translation>GPU-label</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="54"/>
        <source>Person Detection</source>
        <translation>Persoonsdetectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="55"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Invoer &amp;&amp; Verwerking</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="56"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="57"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Opschoning</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="78"/>
        <source>Model</source>
        <translation>Model</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="80"/>
        <source>Force CPU (disable DirectML)</source>
        <translation>CPU forceren (DirectML uitschakelen)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="81"/>
        <source>Use 1024 model (higher quality, slower)</source>
        <translation>1024-model gebruiken (hogere kwaliteit, langzamer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="86"/>
        <source>Detection</source>
        <translation>Detectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="91"/>
        <source>Confidence Threshold:</source>
        <translation>Betrouwbaarheidsdrempel:</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="81"/>
        <source>GPU Not Available</source>
        <translation>GPU niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="87"/>
        <source>GPU Available</source>
        <translation>GPU beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="91"/>
        <source>FPS: {fps} | Processing: {ms}ms</source>
        <translation>FPS: {fps} | Verwerking: {ms}ms</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="96"/>
        <source>{status} | Tile fallback active</source>
        <translation>{status} | Tegelfallback actief</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizard</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="40"/>
        <source>How confident should ADIAT be before marking something as a person?</source>
        <translation>Hoe zeker moet ADIAT zijn voordat iets als persoon wordt gemarkeerd?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="56"/>
        <source>Note: A higher setting may increase false positives.</source>
        <translation>Opmerking: een hogere instelling kan het aantal valse positieven vergroten.</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizardController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="33"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="52"/>
        <source>Very 
Confident</source>
        <translation>Zeer 
zeker</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="34"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="53"/>
        <source>Confident</source>
        <translation>Zeker</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="35"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="54"/>
        <source>Balanced</source>
        <translation>Gebalanceerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="36"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="55"/>
        <source>Permissive</source>
        <translation>Toegeeflijk</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="37"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="56"/>
        <source>Very 
Permissive</source>
        <translation>Zeer 
toegeeflijk</translation>
    </message>
</context>
<context>
    <name>AOICommentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="27"/>
        <source>AOI Comment</source>
        <translation>AOI-opmerking</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="37"/>
        <source>Add a comment for this flagged AOI (max 256 characters):</source>
        <translation>Voeg een opmerking toe voor deze gemarkeerde AOI (max. 256 tekens):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="44"/>
        <source>Enter your comment here...</source>
        <translation>Voer hier uw opmerking in...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="57"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="59"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>AOIController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="366"/>
        <source>No AOI #{number} in this analysis.</source>
        <translation>Geen AOI #{number} in deze analyse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="379"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="389"/>
        <source>AOI #{number} is hidden by the current filter.</source>
        <translation>AOI #{number} is verborgen door het huidige filter.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="685"/>
        <source>Comment saved</source>
        <translation>Opmerking opgeslagen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="687"/>
        <source>Comment cleared</source>
        <translation>Opmerking gewist</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="776"/>
        <source>Copy Data</source>
        <translation>Gegevens kopiëren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="782"/>
        <source>Find Similar AOIs</source>
        <translation>Vergelijkbare AOI&apos;s zoeken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="885"/>
        <source>AOI data copied</source>
        <translation>AOI-gegevens gekopieerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="972"/>
        <source>Invalid image index</source>
        <translation>Ongeldige afbeeldingsindex</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="977"/>
        <source>Invalid AOI index</source>
        <translation>Ongeldige AOI-index</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1040"/>
        <source>Could not calculate AOI location. Diagnostic info copied to clipboard!</source>
        <translation>Kan AOI-locatie niet berekenen. Diagnostische informatie naar klembord gekopieerd!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1046"/>
        <source>Could not calculate AOI location</source>
        <translation>Kan AOI-locatie niet berekenen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1503"/>
        <source>Temperature sorting unavailable (no thermal data)</source>
        <translation>Sorteren op temperatuur niet beschikbaar (geen thermische gegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1855"/>
        <source>Cannot Delete AOI</source>
        <translation>Kan AOI niet verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1857"/>
        <source>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</source>
        <translation>Alleen handmatig gemaakte AOI&apos;s kunnen worden verwijderd. Door algoritmen gedetecteerde AOI&apos;s kunnen niet worden verwijderd.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1866"/>
        <source>Delete AOI</source>
        <translation>AOI verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1868"/>
        <source>Are you sure you want to delete this AOI? This action cannot be undone.</source>
        <translation>Weet u zeker dat u deze AOI wilt verwijderen? Deze actie kan niet ongedaan worden gemaakt.</translation>
    </message>
</context>
<context>
    <name>AOICreationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="23"/>
        <source>Create AOI</source>
        <translation>AOI aanmaken</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="31"/>
        <source>Create AOI?</source>
        <translation>AOI aanmaken?</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="39"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="43"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>AOIFilterDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="74"/>
        <source>Filter AOIs</source>
        <translation>AOI&apos;s filteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="91"/>
        <source>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</source>
        <translation>Interessegebieden filteren op gemarkeerde status, opmerkingen, kleur en/of pixelgebied:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="96"/>
        <source>Flagged AOIs</source>
        <translation>Gemarkeerde AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="99"/>
        <source>Show Only Flagged AOIs</source>
        <translation>Alleen gemarkeerde AOI&apos;s tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="103"/>
        <source>Only AOIs marked with a flag will be displayed</source>
        <translation>Alleen AOI&apos;s met een markering worden weergegeven</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="111"/>
        <source>Comment Filter</source>
        <translation>Opmerkingenfilter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="115"/>
        <source>Enable Comment Filter</source>
        <translation>Opmerkingenfilter inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="122"/>
        <source>Pattern:</source>
        <translation>Patroon:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="125"/>
        <source>e.g., damage or crack</source>
        <translation>bijv. schade of scheur</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="133"/>
        <source>Case-insensitive substring match (e.g. &quot;blue&quot; matches &quot;blueface&quot;)</source>
        <translation>Hoofdletterongevoelige subtekenreeks-match (bijv. &quot;blauw&quot; matcht met &quot;blauwgezicht&quot;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="137"/>
        <source>Only AOIs with non-empty comments matching the pattern will be shown</source>
        <translation>Alleen AOI&apos;s met niet-lege opmerkingen die overeenkomen met het patroon worden getoond</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="145"/>
        <source>Color Filter</source>
        <translation>Kleurfilter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="149"/>
        <source>Enable Color Filter</source>
        <translation>Kleurfilter inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="156"/>
        <source>Show Only This Color</source>
        <translation>Alleen deze kleur tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="157"/>
        <source>Exclude This Color</source>
        <translation>Deze kleur uitsluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="174"/>
        <source>Target Hue:</source>
        <translation>Doeltint:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="176"/>
        <source>Select Color</source>
        <translation>Kleur selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="188"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="556"/>
        <source>No color selected</source>
        <translation>Geen kleur geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="196"/>
        <source>Hue Range (±):</source>
        <translation>Tintbereik (±):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="214"/>
        <source>AOIs with hue within ±range of target will be shown</source>
        <translation>AOI&apos;s met tint binnen ±bereik van doel worden getoond</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="222"/>
        <source>Pixel Area Filter</source>
        <translation>Pixelgebiedfilter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="226"/>
        <source>Enable Pixel Area Filter</source>
        <translation>Pixelgebiedfilter inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="233"/>
        <source>Minimum Area (px):</source>
        <translation>Minimaal gebied (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="247"/>
        <source>Maximum Area (px):</source>
        <translation>Maximaal gebied (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="263"/>
        <source>Temperature Filter</source>
        <translation>Temperatuurfilter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="267"/>
        <source>Enable Temperature Filter</source>
        <translation>Temperatuurfilter inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="321"/>
        <source>Temperature filtering unavailable (no thermal data)</source>
        <translation>Temperatuurfiltering niet beschikbaar (geen thermische gegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="336"/>
        <source>Spatial Filters</source>
        <translation>Ruimtelijke filters</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="341"/>
        <source>Detection Density Heatmap</source>
        <translation>Detectiedichtheid-heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="347"/>
        <source>Off</source>
        <translation>Uit</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="348"/>
        <source>Filter Hot Zones</source>
        <translation>Hot zones filteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="349"/>
        <source>Show Hot Zones Only</source>
        <translation>Alleen hot zones tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="374"/>
        <source>Threshold:</source>
        <translation>Drempel:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="392"/>
        <source>View Heatmap</source>
        <translation>Heatmap bekijken</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="405"/>
        <source>Heatmap filtering unavailable (image dimensions not in dataset)</source>
        <translation>Heatmap-filtering niet beschikbaar (afbeeldingsafmetingen niet in dataset)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="418"/>
        <source>Image Mask Filter</source>
        <translation>Afbeeldingsmaskerfilter</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="422"/>
        <source>Enable Image Mask Filter</source>
        <translation>Afbeeldingsmaskerfilter inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="429"/>
        <source>Show Only Detections in Mask</source>
        <translation>Alleen detecties in masker tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="430"/>
        <source>Exclude Detections in Mask</source>
        <translation>Detecties in masker uitsluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="449"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="630"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="690"/>
        <source>No mask image selected</source>
        <translation>Geen maskerafbeelding geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="454"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="458"/>
        <source>Clear</source>
        <translation>Wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="465"/>
        <source>White regions = areas of interest. Mask is scaled to each image&apos;s dimensions.</source>
        <translation>Witte gebieden = interessegebieden. Het masker wordt geschaald naar de afmetingen van elke afbeelding.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="483"/>
        <source>Clear All Filters</source>
        <translation>Alle filters wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="489"/>
        <source>Apply</source>
        <translation>Toepassen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="494"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="531"/>
        <source>Select Target Hue</source>
        <translation>Doeltint selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="607"/>
        <source>Select Mask Image</source>
        <translation>Maskerafbeelding selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="609"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)</source>
        <translation>Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.tiff);;Alle bestanden (*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="618"/>
        <source>Invalid Image</source>
        <translation>Ongeldige afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="619"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Kan de geselecteerde afbeelding niet laden. Kies een geldig afbeeldingsbestand.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="637"/>
        <source>AOIs in high-density zones (above threshold) will be hidden</source>
        <translation>AOI&apos;s in hogedichtheidszones (boven drempel) worden verborgen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="640"/>
        <source>Only AOIs in high-density zones (above threshold) will be shown</source>
        <translation>Alleen AOI&apos;s in hogedichtheidszones (boven drempel) worden getoond</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="643"/>
        <source>Heatmap spatial filtering is disabled</source>
        <translation>Ruimtelijke heatmap-filtering is uitgeschakeld</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="649"/>
        <source>Heatmap</source>
        <translation>Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="650"/>
        <source>No heatmap data available. Ensure image dimensions are present in the dataset.</source>
        <translation>Geen heatmap-gegevens beschikbaar. Zorg dat afbeeldingsafmetingen aanwezig zijn in de dataset.</translation>
    </message>
</context>
<context>
    <name>AOINeighborGalleryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="338"/>
        <source>AOI in Neighboring Images</source>
        <translation>AOI in naburige afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="389"/>
        <source>Reset View</source>
        <translation>Weergave resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="392"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Zoom resetten en alle miniaturen in beeld passen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="399"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
</context>
<context>
    <name>AOINeighborTrackingController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="120"/>
        <source>No AOI Selected</source>
        <translation>Geen AOI geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="121"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Selecteer eerst een AOI door erop te klikken in het miniaturenpaneel.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="155"/>
        <source>Cannot Calculate GPS</source>
        <translation>Kan GPS niet berekenen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="157"/>
        <source>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</source>
        <translation>Kan GPS-coördinaten voor deze AOI niet berekenen.

Dit kan komen door ontbrekende afbeeldingsmetagegevens (GPS, hoogte of camera-informatie).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="167"/>
        <source>Searching for AOI in neighboring images...</source>
        <translation>AOI zoeken in naburige afbeeldingen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="168"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="172"/>
        <source>Tracking AOI</source>
        <translation>AOI volgen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="208"/>
        <source>Tracking Error</source>
        <translation>Volgfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="209"/>
        <source>An error occurred while tracking the AOI:
{error}</source>
        <translation>Er is een fout opgetreden bij het volgen van de AOI:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="234"/>
        <source>No Neighbors Found</source>
        <translation>Geen buren gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="235"/>
        <source>The AOI was not found in any neighboring images.</source>
        <translation>De AOI is niet gevonden in naburige afbeeldingen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="260"/>
        <source>Search Error</source>
        <translation>Zoekfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="261"/>
        <source>An error occurred during the search:
{error}</source>
        <translation>Er is een fout opgetreden tijdens het zoeken:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="312"/>
        <source>Display Error</source>
        <translation>Weergavefout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="313"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Er is een fout opgetreden bij het weergeven van de resultaten:
{error}</translation>
    </message>
</context>
<context>
    <name>AOISimilarityController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="134"/>
        <source>No AOI Selected</source>
        <translation>Geen AOI geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="135"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Selecteer eerst een AOI door erop te klikken in het miniaturenpaneel.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="152"/>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="246"/>
        <source>Similarity Search Error</source>
        <translation>Fout bij zoeken naar vergelijkbare AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="153"/>
        <source>An error occurred while starting the similarity search:
{error}</source>
        <translation>Er is een fout opgetreden bij het starten van de zoekactie naar vergelijkbare AOI&apos;s:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="164"/>
        <source>Analyzing AOIs for visual similarity...</source>
        <translation>AOI&apos;s analyseren op visuele overeenkomst...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="165"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="169"/>
        <source>Find Similar AOIs</source>
        <translation>Vergelijkbare AOI&apos;s zoeken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="200"/>
        <source>Analyzing AOI {done} of {total}...</source>
        <translation>AOI {done} van {total} analyseren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="215"/>
        <source>No Similar AOIs</source>
        <translation>Geen vergelijkbare AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="216"/>
        <source>No other AOIs could be analyzed for similarity.</source>
        <translation>Er konden geen andere AOI&apos;s op overeenkomst worden geanalyseerd.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="247"/>
        <source>The similarity search could not be completed:
{error}</source>
        <translation>De zoekactie naar vergelijkbare AOI&apos;s kon niet worden voltooid:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="314"/>
        <source>Display Error</source>
        <translation>Weergavefout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="315"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Er is een fout opgetreden bij het weergeven van de resultaten:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="367"/>
        <source>Flagged {count} AOI(s)</source>
        <translation>{count} AOI&apos;s gemarkeerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="370"/>
        <source>Removed flag from {count} AOI(s)</source>
        <translation>Markering verwijderd van {count} AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="402"/>
        <source>Comment saved on {count} AOI(s)</source>
        <translation>Opmerking opgeslagen bij {count} AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="405"/>
        <source>Comment cleared on {count} AOI(s)</source>
        <translation>Opmerking gewist bij {count} AOI&apos;s</translation>
    </message>
</context>
<context>
    <name>AOISimilarityResultsDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="442"/>
        <source>Similar AOIs</source>
        <translation>Vergelijkbare AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="470"/>
        <source>Top {shown} of {total} AOIs ranked by similarity to {reference}. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to jump to that AOI.</source>
        <translation>Top {shown} van {total} AOI&apos;s gerangschikt op overeenkomst met {reference}. Gebruik het muiswiel om te zoomen, sleep met de rechtermuisknop om te pannen. Klik op een miniatuur om naar die AOI te gaan.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="491"/>
        <source>Select All</source>
        <translation>Alles selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="495"/>
        <source>Clear Selection</source>
        <translation>Selectie wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="547"/>
        <source>{count} selected</source>
        <translation>{count} geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="505"/>
        <source>Flag</source>
        <translation>Markeren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="506"/>
        <source>Flag all checked AOIs</source>
        <translation>Alle aangevinkte AOI&apos;s markeren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="511"/>
        <source>Unflag</source>
        <translation>Markering verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="512"/>
        <source>Remove the flag from all checked AOIs</source>
        <translation>De markering verwijderen van alle aangevinkte AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="517"/>
        <source>Comment...</source>
        <translation>Opmerking...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="518"/>
        <source>Add or edit the comment on all checked AOIs</source>
        <translation>De opmerking toevoegen of bewerken voor alle aangevinkte AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="529"/>
        <source>Reset View</source>
        <translation>Weergave resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="532"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Zoom resetten en alle miniaturen in beeld passen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="537"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="572"/>
        <source>AOI #{number}</source>
        <translation>AOI #{number}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="573"/>
        <source>the selected AOI</source>
        <translation>de geselecteerde AOI</translation>
    </message>
</context>
<context>
    <name>AOIUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="250"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="346"/>
        <source>AOI Information
Right-click to copy data to clipboard</source>
        <translation>AOI-informatie
Rechtsklik om gegevens naar klembord te kopiëren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="256"/>
        <source>

Score Type: {type}
Raw Score: {score} ({method})</source>
        <translation>

Scoretype: {type}
Ruwe score: {score} ({method})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="320"/>
        <source>Confidence Score: {score:.1f}%</source>
        <translation>Betrouwbaarheidsscore: {score:.1f}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Unflag AOI</source>
        <translation>Markering AOI verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Flag AOI</source>
        <translation>AOI markeren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="403"/>
        <source>Comment:
{comment}

Click to edit comment</source>
        <translation>Opmerking:
{comment}

Klik om opmerking te bewerken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="411"/>
        <source>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</source>
        <translation>Nog geen opmerking.
Klik om een opmerking toe te voegen voor deze AOI.

Gebruik opmerkingen om belangrijke details, waarnemingen
of benodigde acties voor deze detectie vast te leggen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="428"/>
        <source>Calculate and show GPS location for this AOI</source>
        <translation>GPS-locatie voor deze AOI berekenen en tonen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="446"/>
        <source>Delete this AOI</source>
        <translation>Deze AOI verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Area</source>
        <translation>Gebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Areas</source>
        <translation>Gebieden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="486"/>
        <source>{filtered} of {total} {label}</source>
        <translation>{filtered} van {total} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="495"/>
        <source>Area of Interest</source>
        <translation>Interessegebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="497"/>
        <source>Areas of Interest</source>
        <translation>Interessegebieden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="500"/>
        <source>{count} {label}</source>
        <translation>{count} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="643"/>
        <source>Loading AOIs...</source>
        <translation>AOI&apos;s laden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="684"/>
        <source>Loading AOIs... ({current}/{total})</source>
        <translation>AOI&apos;s laden... ({current}/{total})</translation>
    </message>
</context>
<context>
    <name>AlertManager</name>
    <message>
        <location filename="../app/core/services/AlertService.py" line="294"/>
        <source>ADIAT - Color Detection Alerts</source>
        <translation>ADIAT - Kleurdetectiewaarschuwingen</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="569"/>
        <source>ADIAT - Color Detection Alert</source>
        <translation>ADIAT - Kleurdetectiewaarschuwing</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="610"/>
        <source>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</source>
        <translation>{count} object(en) gedetecteerd
Gemiddelde betrouwbaarheid: {avg_confidence:.2f}
Totale oppervlakte: {area:.0f} pixels
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
        <translation>  #{index}: ({x},{y}) {w}x{h} betr:{confidence:.2f}
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="644"/>
        <source>ADIAT - Detection Alert</source>
        <translation>ADIAT - Detectiewaarschuwing</translation>
    </message>
</context>
<context>
    <name>AlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmParametersPage.py" line="166"/>
        <source>{algorithm} Algorithm Settings</source>
        <translation>Instellingen voor {algorithm}-algoritme</translation>
    </message>
</context>
<context>
    <name>AlgorithmSelectionPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="92"/>
        <source>Are you using thermal images?</source>
        <translation>Gebruikt u thermische afbeeldingen?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="156"/>
        <source>Are you looking for anomalies within a specific temperature range?</source>
        <translation>Zoekt u afwijkingen binnen een specifiek temperatuurbereik?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="159"/>
        <source>Do you specifically want to detect people?</source>
        <translation>Wilt u specifiek personen detecteren?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="168"/>
        <source>Do you want to detect anomalies relative to local surroundings?</source>
        <translation>Wilt u afwijkingen ten opzichte van de lokale omgeving detecteren?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="185"/>
        <source>Are you trying to find a specific color?</source>
        <translation>Probeert u een specifieke kleur te vinden?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="190"/>
        <source>Do you want to manually adjust the color range?</source>
        <translation>Wilt u het kleurbereik handmatig aanpassen?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="193"/>
        <source>Do your images contain complex backgrounds or structures?</source>
        <translation>Bevatten uw afbeeldingen complexe achtergronden of structuren?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="200"/>
        <source>Do your images include shadows or areas with uneven lighting?</source>
        <translation>Bevatten uw afbeeldingen schaduwen of gebieden met ongelijkmatige verlichting?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="226"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Geselecteerd algoritme: {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlignImageController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="46"/>
        <source>No image available to align</source>
        <translation>Geen afbeelding beschikbaar om uit te lijnen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="52"/>
        <source>This image has no GPS data and cannot be aligned</source>
        <translation>Deze afbeelding bevat geen GPS-gegevens en kan niet worden uitgelijnd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="84"/>
        <source>Could not save the alignment</source>
        <translation>Kan de uitlijning niet opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="95"/>
        <source>Image alignment saved</source>
        <translation>Afbeeldingsuitlijning opgeslagen</translation>
    </message>
</context>
<context>
    <name>AlignImageDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="53"/>
        <source>This saved alignment looks mirrored - re-place each corner handle on its matching photo corner (coloured squares).</source>
        <translation>Deze opgeslagen uitlijning lijkt gespiegeld: plaats elke hoekgreep opnieuw op de bijbehorende fotohoek (gekleurde vierkantjes).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="60"/>
        <source>Align Image</source>
        <translation>Afbeelding uitlijnen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="130"/>
        <source>Rotate the drone image to line it up with the map. The small coloured squares mark the photo&apos;s corners - drag each corner handle onto the map where its matching-coloured photo corner belongs. For extra accuracy, add tie points: put the IMAGE end on a feature in the drone photo and the MAP end on the same feature on the map.</source>
        <translation>Draai de drone-afbeelding zodat deze op de kaart aansluit. De kleine gekleurde vierkantjes markeren de hoeken van de foto: sleep elke hoekgreep op de kaart naar de plek waar de fotohoek met dezelfde kleur hoort. Voeg voor extra nauwkeurigheid verbindingspunten toe: plaats het AFBEELDING-uiteinde op een herkenbaar punt in de dronefoto en het KAART-uiteinde op hetzelfde punt op de kaart.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="137"/>
        <source>Rotation:</source>
        <translation>Rotatie:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="138"/>
        <source>Map opacity:</source>
        <translation>Kaartopaciteit:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="139"/>
        <source>FOV overlay opacity:</source>
        <translation>Opaciteit FOV-overlay:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="140"/>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="192"/>
        <source>Show Street Map</source>
        <translation>Stratenkaart tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="141"/>
        <source>Add Tie Point</source>
        <translation>Verbindingspunt toevoegen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="142"/>
        <source>Reset</source>
        <translation>Resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="195"/>
        <source>Show Satellite</source>
        <translation>Satelliet tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="218"/>
        <source>Corners look mirrored</source>
        <translation>Hoeken lijken gespiegeld</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="220"/>
        <source>The four corners appear mirrored - the drone image would map to the ground flipped.

Each corner handle is colour-matched to a corner of the drone photo (the small coloured squares). Make sure every handle sits where its matching photo corner belongs.</source>
        <translation>De vier hoeken lijken gespiegeld: de drone-afbeelding zou omgekeerd op de grond worden geprojecteerd.

Elke hoekgreep is op kleur gekoppeld aan een hoek van de dronefoto (de kleine gekleurde vierkantjes). Zorg dat elke greep op de plek staat waar de bijbehorende fotohoek hoort.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="230"/>
        <source>Go Back and Fix</source>
        <translation>Teruggaan en corrigeren</translation>
    </message>
</context>
<context>
    <name>AlignImageView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="425"/>
        <source>IMAGE</source>
        <translation>AFBEELDING</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="427"/>
        <source>MAP</source>
        <translation>KAART</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="672"/>
        <source>Remove Tie Point</source>
        <translation>Verbindingspunt verwijderen</translation>
    </message>
</context>
<context>
    <name>AltitudeController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>meters</source>
        <translation>meter</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>feet</source>
        <translation>voet</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="109"/>
        <source>Negative Altitude Detected</source>
        <translation>Negatieve hoogte gedetecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="111"/>
        <source>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</source>
        <translation>WAARSCHUWING! De relatieve hoogte is negatief. Voer een AGL-hoogte in voor GSD-berekeningen (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="130"/>
        <source>Override Altitude</source>
        <translation>Hoogte overschrijven</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="132"/>
        <source>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</source>
        <translation>Voer een aangepaste AGL-hoogte in voor GSD-berekeningen voor alle afbeeldingen (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="180"/>
        <source>Custom AGL set to {value:.1f} {unit}</source>
        <translation>Aangepaste AGL ingesteld op {value:.1f} {unit}</translation>
    </message>
</context>
<context>
    <name>AnalyzeService</name>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="161"/>
        <source>Processing {count} files</source>
        <translation>{count} bestanden verwerken</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="205"/>
        <source>Skipping {file} :: File is not an image</source>
        <translation>{file} overslaan :: Bestand is geen afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="210"/>
        <source>All {count} images queued, processing started...</source>
        <translation>Alle {count} afbeeldingen in wachtrij, verwerking gestart...</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="268"/>
        <source>{images} images with {aois} areas of interest identified</source>
        <translation>{images} afbeeldingen met {aois} interessegebieden geïdentificeerd</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="274"/>
        <source>Total Processing Time: {seconds} seconds</source>
        <translation>Totale verwerkingstijd: {seconds} seconden</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="277"/>
        <source>Total Images Processed: {count}</source>
        <translation>Totaal aantal verwerkte afbeeldingen: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="495"/>
        <source>Unable to process {file} :: {error} ({percent}%)</source>
        <translation>Kan {file} niet verwerken :: {error} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="518"/>
        <source>{count} areas of interest identified in {file} ({percent}%)</source>
        <translation>{count} interessegebieden geïdentificeerd in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="535"/>
        <source>No areas of interest identified in {file} ({percent}%)</source>
        <translation>Geen interessegebieden geïdentificeerd in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="617"/>
        <source>--- Cancelling Image Processing ---</source>
        <translation>--- Beeldverwerking annuleren ---</translation>
    </message>
</context>
<context>
    <name>BearingRecoveryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="124"/>
        <source>Missing Bearings Detected</source>
        <translation>Ontbrekende koersen gedetecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="132"/>
        <source>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</source>
        <translation>Sommige afbeeldingen missen koers-/richtingsinformatie. We kunnen koersen schatten uit een vluchtspoorbestand (KML/GPX/CSV) of ze automatisch berekenen op basis van GPS-coördinaten van de afbeeldingen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="150"/>
        <source>📁 Load Track File (KML/GPX/CSV)</source>
        <translation>📁 Spoorbestand laden (KML/GPX/CSV)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="156"/>
        <source>🧭 Auto-Calculate from Image GPS</source>
        <translation>🧭 Automatisch berekenen vanuit afbeeldings-GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="174"/>
        <source>Preparing...</source>
        <translation>Voorbereiden...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="190"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="195"/>
        <source>Skip</source>
        <translation>Overslaan</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="259"/>
        <source>Select Track File</source>
        <translation>Spoorbestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="261"/>
        <source>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</source>
        <translation>Spoorbestanden (*.kml *.gpx *.csv);;KML-bestanden (*.kml);;GPX-bestanden (*.gpx);;CSV-bestanden (*.csv);;Alle bestanden (*.*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="345"/>
        <source>Bearings set for {count} images ({source})</source>
        <translation>Koersen ingesteld voor {count} afbeeldingen ({source})</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="350"/>
        <source>, {count} flagged near turns</source>
        <translation>, {count} gemarkeerd nabij bochten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="352"/>
        <source>, {count} hover estimates</source>
        <translation>, {count} hover-schattingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="354"/>
        <source>, {count} time gaps</source>
        <translation>, {count} tijdsleemtes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="361"/>
        <source>Bearing Calculation Complete</source>
        <translation>Koersberekening voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="362"/>
        <source>{summary}.</source>
        <translation>{summary}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="389"/>
        <source>Bearing Calculation Failed</source>
        <translation>Koersberekening mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="391"/>
        <source>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</source>
        <translation>Er is een fout opgetreden tijdens de koersberekening:

{error}

Controleer uw invoerbestanden en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="411"/>
        <source>Cancelled</source>
        <translation>Geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="422"/>
        <source>Cancelling...</source>
        <translation>Annuleren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="435"/>
        <source>Bearing Recovery Not Needed</source>
        <translation>Koersherstel niet nodig</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="437"/>
        <source>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</source>
        <translation>Koersherstel vereist meerdere afbeeldingen om de bewegingsrichting te berekenen.

Met slechts één afbeelding kan koersherstel niet worden uitgevoerd.</translation>
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
&lt;h3&gt;Wat is koersherstel?&lt;/h3&gt;

&lt;p&gt;&lt;b&gt;Koers&lt;/b&gt; (ook wel heading, yaw of course genoemd) is de richting waarin de drone/camera
wees toen een afbeelding werd vastgelegd, gemeten in graden met de klok mee vanaf het noorden (0-360°).&lt;/p&gt;

&lt;h4&gt;Waarom is het belangrijk?&lt;/h4&gt;
&lt;p&gt;Koersen zijn essentieel voor:&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;Nauwkeurige georeferentie en mapping&lt;/li&gt;
&lt;li&gt;Correcte uitlijning en stitching van afbeeldingen&lt;/li&gt;
&lt;li&gt;Begrip van het cameragezichtsveld&lt;/li&gt;
&lt;li&gt;Analyse van gedetecteerde objecten in geografische context&lt;/li&gt;
&lt;/ul&gt;

&lt;h4&gt;Herstelmethoden:&lt;/h4&gt;

&lt;p&gt;&lt;b&gt;Spoorbestand laden (KML/GPX/CSV)&lt;/b&gt;&lt;br/&gt;
Gebruikt een extern GPS-spoorlogboek van uw drone of vluchtcontroller. Het spoor bevat
posities met tijdstempel die nauwkeurige koersinterpolatie mogelijk maken. Meest nauwkeurige methode.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Automatisch berekenen vanuit afbeeldings-GPS&lt;/b&gt;&lt;br/&gt;
Schat koersen alleen op basis van de in uw afbeeldingen ingebedde GPS-coördinaten. Analyseert het
vluchtpatroon om de bewegingsrichting te bepalen. Werkt goed voor systematische vluchtpatronen
zoals rastervluchten.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Overslaan&lt;/b&gt;&lt;br/&gt;
Doorgaan zonder koersherstel. Sommige functies werken mogelijk niet correct.&lt;/p&gt;
        </translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="483"/>
        <source>About Bearing Recovery</source>
        <translation>Over koersherstel</translation>
    </message>
</context>
<context>
    <name>CacheLocationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="35"/>
        <source>Cache Not Found</source>
        <translation>Cache niet gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="47"/>
        <source>Cached Data Not Found</source>
        <translation>Gecachete gegevens niet gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="56"/>
        <source>The following cached items were not found:
</source>
        <translation>De volgende gecachete items zijn niet gevonden:
</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="66"/>
        <source>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</source>
        <translation>Zonder gecachete gegevens worden miniaturen en kleuren op aanvraag gegenereerd, wat vertragingen kan veroorzaken bij het bekijken van resultaten.

Als u deze dataset eerder hebt verwerkt en een ADIAT_Results-map met gecachete gegevens hebt, kunt u deze nu lokaliseren om de prestaties te verbeteren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="80"/>
        <source>Locate Cache Folder...</source>
        <translation>Cachemap lokaliseren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="85"/>
        <source>Skip (Generate On-Demand)</source>
        <translation>Overslaan (op aanvraag genereren)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="122"/>
        <source>Select ADIAT_Results Folder</source>
        <translation>ADIAT_Results-map selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="136"/>
        <source>Invalid Cache Folder</source>
        <translation>Ongeldige cachemap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="138"/>
        <source>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</source>
        <translation>De geselecteerde map bevat geen map met miniaturencache.

Verwacht te vinden:
  • .thumbnails/

Selecteer een geldige ADIAT_Results-map.</translation>
    </message>
</context>
<context>
    <name>CalTopoAPIMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="42"/>
        <source>Select CalTopo Map</source>
        <translation>CalTopo-kaart selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="68"/>
        <source>Select a CalTopo map:</source>
        <translation>Selecteer een CalTopo-kaart:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="77"/>
        <source>Search:</source>
        <translation>Zoeken:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="79"/>
        <source>Filter maps by name...</source>
        <translation>Kaarten filteren op naam...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="111"/>
        <source>Update Credentials</source>
        <translation>Inloggegevens bijwerken</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="117"/>
        <source>Select Map</source>
        <translation>Kaart selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="121"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="150"/>
        <source>No account data available.</source>
        <translation>Geen accountgegevens beschikbaar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="515"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="540"/>
        <source>Credentials Updated</source>
        <translation>Inloggegevens bijgewerkt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="516"/>
        <source>Credentials have been updated and the map list has been refreshed.</source>
        <translation>De inloggegevens zijn bijgewerkt en de kaartlijst is vernieuwd.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="521"/>
        <source>Update Failed</source>
        <translation>Bijwerken mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="523"/>
        <source>Failed to refresh account data with new credentials.

Please check your credentials and try again.</source>
        <translation>Kan accountgegevens niet vernieuwen met nieuwe inloggegevens.

Controleer uw inloggegevens en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="530"/>
        <source>Update Error</source>
        <translation>Bijwerkfout</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="531"/>
        <source>An error occurred while updating credentials:

{error}</source>
        <translation>Er is een fout opgetreden bij het bijwerken van de inloggegevens:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="542"/>
        <source>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</source>
        <translation>De inloggegevens zijn bijgewerkt. Sluit en open dit dialoogvenster opnieuw om de kaartlijst te vernieuwen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="559"/>
        <source>No Map Selected</source>
        <translation>Geen kaart geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="560"/>
        <source>Please select a map from the list.</source>
        <translation>Selecteer een kaart uit de lijst.</translation>
    </message>
</context>
<context>
    <name>CalTopoAuthDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="96"/>
        <source>CalTopo Login &amp; Map Selection</source>
        <translation>CalTopo aanmelden &amp; kaartselectie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="173"/>
        <source>Current map: Not selected</source>
        <translation>Huidige kaart: niet geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="177"/>
        <source>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</source>
        <translation>(Aanmelden → navigeer naar uw kaart → klik op &apos;Ik ben aangemeld&apos;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="191"/>
        <source>I&apos;m Logged In - Export Data</source>
        <translation>Ik ben aangemeld - Gegevens exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="193"/>
        <source>Click this after logging in and navigating to your map</source>
        <translation>Klik hierop na het aanmelden en navigeren naar uw kaart</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="196"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="264"/>
        <source>Initialization Error</source>
        <translation>Initialisatiefout</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="265"/>
        <source>Failed to initialize CalTopo browser:
{error}</source>
        <translation>Kan CalTopo-browser niet initialiseren:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="308"/>
        <source>Failed to Load</source>
        <translation>Laden mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="310"/>
        <source>Failed to load CalTopo. Please check your internet connection and try again.</source>
        <translation>Kan CalTopo niet laden. Controleer uw internetverbinding en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="341"/>
        <source>Current map: {map_id}</source>
        <translation>Huidige kaart: {map_id}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="358"/>
        <source>No Map Selected</source>
        <translation>Geen kaart geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="360"/>
        <source>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</source>
        <translation>Navigeer naar een CalTopo-kaart voordat u de sessie vastlegt.

De kaart-URL moet een kaart-ID bevatten (bijv. /m/ABC123 of #id=ABC123).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="369"/>
        <source>Browser Not Ready</source>
        <translation>Browser niet gereed</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="370"/>
        <source>The CalTopo browser is still loading. Please wait a moment and try again.</source>
        <translation>De CalTopo-browser laadt nog. Wacht even en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="376"/>
        <source>Starting export...</source>
        <translation>Export starten...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="394"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="557"/>
        <source>Authentication Failed</source>
        <translation>Authenticatie mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="395"/>
        <source>Browser not initialized. Please try again.</source>
        <translation>Browser niet geïnitialiseerd. Probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="559"/>
        <source>Could not capture session cookies. Please ensure you are logged in to CalTopo.

Try:
1. Make sure you&apos;re logged in
2. Navigate to a map
3. Wait a few seconds for cookies to be set
4. Click &apos;I&apos;m Logged In&apos; again</source>
        <translation>Kan sessiecookies niet vastleggen. Zorg dat u bent aangemeld bij CalTopo.

Probeer:
1. Zorg dat u bent aangemeld
2. Navigeer naar een kaart
3. Wacht enkele seconden tot cookies zijn ingesteld
4. Klik nogmaals op &apos;Ik ben aangemeld&apos;</translation>
    </message>
</context>
<context>
    <name>CalTopoCredentialDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="33"/>
        <source>CalTopo API Credentials</source>
        <translation>CalTopo API-inloggegevens</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="54"/>
        <source>Enter new credential secret...</source>
        <translation>Voer nieuwe inloggegeven-sleutel in...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="76"/>
        <source>CalTopo Team API Credentials</source>
        <translation>CalTopo Team API-inloggegevens</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="85"/>
        <source>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</source>
        <translation>Voer uw CalTopo Team API-inloggegevens in.
Deze zijn te vinden op de Team Admin-pagina onder Service Accounts.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="97"/>
        <source>How to get your API credentials</source>
        <translation>Hoe u uw API-inloggegevens krijgt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="101"/>
        <source>Opens CalTopo API documentation in your browser</source>
        <translation>Opent de CalTopo API-documentatie in uw browser</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="107"/>
        <source>Change credentials</source>
        <translation>Inloggegevens wijzigen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="114"/>
        <source>Team ID:</source>
        <translation>Team-ID:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="116"/>
        <source>6-digit alphanumeric Team ID</source>
        <translation>Alfanumeriek Team-ID van 6 tekens</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="123"/>
        <source>Credential ID:</source>
        <translation>Inloggegeven-ID:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="125"/>
        <source>Credential ID</source>
        <translation>Inloggegeven-ID</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="132"/>
        <source>Credential Secret:</source>
        <translation>Inloggegeven-sleutel:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="134"/>
        <source>Credential Secret (will be encrypted)</source>
        <translation>Inloggegeven-sleutel (wordt versleuteld)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="146"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="309"/>
        <source>Test Credentials</source>
        <translation>Inloggegevens testen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="148"/>
        <source>Test the credentials by calling the CalTopo API</source>
        <translation>Inloggegevens testen door de CalTopo API aan te roepen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="150"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="204"/>
        <source>Enter credential secret...</source>
        <translation>Voer inloggegeven-sleutel in...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Invalid Input</source>
        <translation>Ongeldige invoer</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <source>Please enter a Team ID.</source>
        <translation>Voer een Team-ID in.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <source>Please enter a Credential ID.</source>
        <translation>Voer een inloggegeven-ID in.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Please enter a Credential Secret.</source>
        <translation>Voer een inloggegeven-sleutel in.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="267"/>
        <source>Testing...</source>
        <translation>Testen...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="282"/>
        <source>Credentials Valid</source>
        <translation>Inloggegevens geldig</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="283"/>
        <source>The credentials are valid and successfully authenticated with CalTopo API.</source>
        <translation>De inloggegevens zijn geldig en authenticatie met de CalTopo API is geslaagd.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="288"/>
        <source>Credentials Invalid</source>
        <translation>Inloggegevens ongeldig</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <source>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</source>
        <translation>Authenticatie met de CalTopo API met de inloggegevens is mislukt.

Controleer:
• Team-ID is correct
• Inloggegeven-ID is correct
• Inloggegeven-sleutel is correct (kopieer deze exact zoals getoond)
• Uw serviceaccount heeft de vereiste machtigingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="301"/>
        <source>Test Error</source>
        <translation>Testfout</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="302"/>
        <source>An error occurred while testing credentials:

{error}</source>
        <translation>Er is een fout opgetreden bij het testen van de inloggegevens:

{error}</translation>
    </message>
</context>
<context>
    <name>CalTopoExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="441"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1508"/>
        <source>Offline Mode Enabled</source>
        <translation>Offline-modus ingeschakeld</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="443"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1510"/>
        <source>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</source>
        <translation>Alleen offline is ingeschakeld in Voorkeuren:

• Kaarttegels worden niet opgehaald.
• CalTopo-integratie is uitgeschakeld.

Schakel Alleen offline uit om naar CalTopo te exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="454"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1521"/>
        <source>Nothing Selected</source>
        <translation>Niets geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="456"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1523"/>
        <source>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</source>
        <translation>Selecteer ten minste één gegevenstype (gemarkeerde AOI&apos;s, drone-/afbeeldingslocaties of dekkingsgebied) om te exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="464"/>
        <source>Preparing Export Data</source>
        <translation>Exportgegevens voorbereiden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="467"/>
        <source>Preparing data for export...</source>
        <translation>Gegevens voorbereiden voor export...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="468"/>
        <source>Processing images and AOIs...</source>
        <translation>Afbeeldingen en AOI&apos;s verwerken...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="512"/>
        <source>Preparation Error</source>
        <translation>Voorbereidingsfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="514"/>
        <source>An error occurred while preparing export data:

{error}</source>
        <translation>Er is een fout opgetreden bij het voorbereiden van exportgegevens:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="523"/>
        <source>flagged AOIs</source>
        <translation>gemarkeerde AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="525"/>
        <source>image locations</source>
        <translation>afbeeldingslocaties</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="527"/>
        <source>coverage area</source>
        <translation>dekkingsgebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="531"/>
        <source>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</source>
        <translation>Geen gemarkeerde AOI&apos;s, geotagde afbeeldingslocaties of dekkingsgebieden beschikbaar.
Markeer enkele AOI&apos;s met de &apos;F&apos;-toets of zorg dat uw afbeeldingen GPS-metagegevens hebben.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="537"/>
        <source>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</source>
        <translation>{count} gemarkeerde AOI(&apos;s) gevonden, maar kan GPS-coördinaten niet extraheren.

Dit betekent meestal:
• De afbeeldingen hebben geen GPS-gegevens in hun EXIF-metagegevens
• De afbeeldingsbestanden zijn verplaatst of hernoemd

Zorg dat uw afbeeldingen GPS-coördinaten bevatten.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="545"/>
        <source>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</source>
        <translation>Geen geotagde drone-/afbeeldingslocaties gevonden.
Zorg dat uw afbeeldingen GPS-metagegevens bevatten en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="550"/>
        <source>No coverage area polygons could be calculated.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The images are not nadir (gimbal pitch must be between -85° and -95°)
• GSD (ground sample distance) could not be calculated

Please ensure your images have GPS coordinates and are nadir shots.</source>
        <translation>Er konden geen polygonen voor het dekkingsgebied worden berekend.

Dit betekent meestal:
• De afbeeldingen hebben geen GPS-gegevens in hun EXIF-metagegevens
• De afbeeldingen zijn niet nadir (gimbal-pitch moet tussen -85° en -95° zijn)
• GSD (ground sample distance) kon niet worden berekend

Zorg dat uw afbeeldingen GPS-coördinaten hebben en nadirale opnamen zijn.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="559"/>
        <source>No {types} are available to export.</source>
        <translation>Er zijn geen {types} beschikbaar om te exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="564"/>
        <source>Nothing to Export</source>
        <translation>Niets te exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="585"/>
        <source>No Map Selected</source>
        <translation>Geen kaart geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="587"/>
        <source>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</source>
        <translation>Navigeer naar een CalTopo-kaart voordat u op &apos;Ik ben aangemeld&apos; klikt.

De kaart-URL moet er zo uitzien:
https://caltopo.com/map.html#...&amp;id=ABC123</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="649"/>
        <source>{count} marker(s)</source>
        <translation>{count} markering(en)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="653"/>
        <source>{count} polygon(s)</source>
        <translation>{count} polygoon(en)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="656"/>
        <source> and </source>
        <translation> en </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="661"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1717"/>
        <source>Export Successful</source>
        <translation>Export geslaagd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="663"/>
        <source>Successfully exported all {items} to CalTopo map {map_id}.

The items should now be visible on your map.</source>
        <translation>Alle {items} succesvol geëxporteerd naar CalTopo-kaart {map_id}.

De items moeten nu zichtbaar zijn op uw kaart.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="670"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1726"/>
        <source>Partial Success</source>
        <translation>Gedeeltelijk geslaagd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="672"/>
        <source>Exported {success} of {total} item(s) ({items}) to CalTopo map {map_id}.

{failed} item(s) failed. Check console for details.</source>
        <translation>{success} van {total} item(s) ({items}) geëxporteerd naar CalTopo-kaart {map_id}.

{failed} item(s) mislukt. Controleer de console voor details.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="686"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1739"/>
        <source>Export Failed</source>
        <translation>Export mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="688"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1741"/>
        <source>Failed to export items to CalTopo.

Please check the console output for error details.</source>
        <translation>Kan items niet exporteren naar CalTopo.

Controleer de console-uitvoer voor foutdetails.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="698"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1647"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1752"/>
        <source>Export Error</source>
        <translation>Exportfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="700"/>
        <source>An error occurred during CalTopo export:

{error}</source>
        <translation>Er is een fout opgetreden tijdens de CalTopo-export:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1002"/>
        <source>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</source>
        <translation>Dekkingsgebied: {sqkm:.3f} km² ({acres:.2f} acres)
Gebied in vierkante meter: {sqm:.0f} m²
Aantal hoeken: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1046"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1330"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1678"/>
        <source>Exporting to CalTopo</source>
        <translation>Exporteren naar CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1049"/>
        <source>Exporting markers to CalTopo...</source>
        <translation>Markeringen exporteren naar CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1051"/>
        <source>Preparing to export {count} marker(s)...</source>
        <translation>Voorbereiden om {count} markering(en) te exporteren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1296"/>
        <source>Export complete: {success} of {total} marker(s) exported</source>
        <translation>Export voltooid: {success} van {total} markering(en) geëxporteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1333"/>
        <source>Exporting polygons to CalTopo...</source>
        <translation>Polygonen exporteren naar CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1335"/>
        <source>Preparing to export {count} polygon(s)...</source>
        <translation>Voorbereiden om {count} polygoon(en) te exporteren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1462"/>
        <source>Export complete: {success} of {total} polygon(s) exported</source>
        <translation>Export voltooid: {success} van {total} polygoon(en) geëxporteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1480"/>
        <source>Logged Out</source>
        <translation>Afgemeld</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1481"/>
        <source>Successfully logged out from CalTopo.</source>
        <translation>Succesvol afgemeld bij CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1546"/>
        <source>Loading CalTopo Maps</source>
        <translation>CalTopo-kaarten laden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1549"/>
        <source>Connecting to CalTopo...</source>
        <translation>Verbinden met CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1550"/>
        <source>Fetching account data and maps...</source>
        <translation>Accountgegevens en kaarten ophalen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1588"/>
        <source>Connection Error</source>
        <translation>Verbindingsfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1590"/>
        <source>An error occurred while connecting to CalTopo API:

{error}</source>
        <translation>Er is een fout opgetreden bij het verbinden met de CalTopo API:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1598"/>
        <source>Authentication Failed</source>
        <translation>Authenticatie mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1600"/>
        <source>Failed to authenticate with CalTopo API.

Please check your credentials and try again.</source>
        <translation>Authenticatie met de CalTopo API mislukt.

Controleer uw inloggegevens en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1649"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1754"/>
        <source>An error occurred during CalTopo API export:

{error}</source>
        <translation>Er is een fout opgetreden tijdens de CalTopo API-export:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1681"/>
        <source>Exporting to CalTopo...</source>
        <translation>Exporteren naar CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1682"/>
        <source>Preparing data and exporting...</source>
        <translation>Gegevens voorbereiden en exporteren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1719"/>
        <source>Successfully exported all {total} item(s) to CalTopo map.

The items should now be visible on your map.</source>
        <translation>Alle {total} item(s) succesvol geëxporteerd naar CalTopo-kaart.

De items moeten nu zichtbaar zijn op uw kaart.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1728"/>
        <source>Exported {success} of {total} item(s) to CalTopo map.

{failed} item(s) failed. Check console for details.</source>
        <translation>{success} van {total} item(s) geëxporteerd naar CalTopo-kaart.

{failed} item(s) mislukt. Controleer de console voor details.</translation>
    </message>
</context>
<context>
    <name>CalTopoMethodDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="34"/>
        <source>CalTopo Export Method</source>
        <translation>CalTopo-exportmethode</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="52"/>
        <source>Select CalTopo Export Method</source>
        <translation>CalTopo-exportmethode selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="61"/>
        <source>Choose how you want to authenticate with CalTopo:</source>
        <translation>Kies hoe u zich bij CalTopo wilt authenticeren:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="68"/>
        <source>Export Method</source>
        <translation>Exportmethode</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="72"/>
        <source>API (Recommended for CalTopo Team Account)</source>
        <translation>API (aanbevolen voor CalTopo Team-account)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="75"/>
        <source>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</source>
        <translation>Gebruik de CalTopo Team API met serviceaccount-inloggegevens.
Ideaal voor Team-accounts met geconfigureerde serviceaccounts.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="79"/>
        <source>Browser Login</source>
        <translation>Aanmelden via browser</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="81"/>
        <source>Use browser-based authentication.
Log in through an embedded browser window.</source>
        <translation>Gebruik browsergebaseerde authenticatie.
Meld u aan via een ingebed browservenster.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="96"/>
        <source>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</source>
        <translation>De API-methode vereist een Team-ID en inloggegeven-sleutel van uw
CalTopo Team Admin-pagina. De browsermethode gebruikt uw normale aanmelding.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="109"/>
        <source>Continue</source>
        <translation>Doorgaan</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="113"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>CleanupTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="32"/>
        <source>Temporal Voting</source>
        <translation>Temporeel stemmen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="35"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Temporeel stemmen inschakelen (flikker verminderen)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="38"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Verzacht detecties over frames met temporele consistentie.
Detecties moeten verschijnen in N van M opeenvolgende frames om te worden bevestigd.
Vermindert flikkerende valse positieven aanzienlijk.
Aanbevolen: AAN voor alle gebruikssituaties (standaard).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="48"/>
        <source>Window Frames (M):</source>
        <translation>Vensterframes (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="53"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Grootte van temporeel stemvenster (2-30 frames).
Detecties moeten verschijnen in N van M opeenvolgende frames.
Grotere waarden = langer geheugen, stabieler, langzamere reactie op nieuwe objecten.
Kleinere waarden = korter geheugen, snellere reactie, minder stabiel.
Aanbevolen: 5 voor 30fps (~167ms venster), 7 voor 60fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="61"/>
        <source>Threshold (N of M):</source>
        <translation>Drempel (N van M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="66"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be &lt;= Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Aantal frames binnen het venster waarin detectie moet verschijnen (N van M).
Hogere waarden = strenger, filtert vluchtige valse positieven.
Lagere waarden = toleranter, snellere reactie op nieuwe objecten.
Moet &lt;= vensterframes zijn.
Aanbevolen: 3 van 5 (detectie in 60% van de frames).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="78"/>
        <source>Detection Cleanup</source>
        <translation>Detectie-opschoning</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="82"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Filtering van beeldverhouding inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="85"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filter zeer dunne of uitgerekte detecties uit op basis van breedte/hoogte.
Nuttig voor het verwijderen van draden, lange schaduwen of andere niet-object-vormen.
De meeste gebruikers kunnen dit UIT laten, tenzij u veel lange, smalle valse detecties ziet.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="94"/>
        <source>Min Ratio:</source>
        <translation>Min. verhouding:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="100"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 = reject if height is more than 5x width.</source>
        <translation>Minimale breedte/hoogte-verhouding om te behouden (0,1-10,0).
Lagere waarden = sta hogere, dunnere detecties toe.
Hogere waarden = vereisen vierkanter detecties.
Voorbeeld: 0,2 = wijs af als hoogte meer dan 5x breedte is.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="107"/>
        <source>Max Ratio:</source>
        <translation>Max. verhouding:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="113"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Maximale breedte/hoogte-verhouding om te behouden (0,1-20,0).
Lagere waarden = wijs zeer brede, dunne detecties af.
Hogere waarden = sta bredere objecten toe zoals voertuigen of lange uitrusting.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="122"/>
        <source>Detection Clustering</source>
        <translation>Detectieclustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="125"/>
        <source>Enable Detection Clustering</source>
        <translation>Detectieclustering inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="128"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Voeg desgewenst nabije detecties samen tot één grotere detectie.
Nuttig wanneer één object verschijnt als vele kleine aangrenzende detecties.
De meeste gebruikers kunnen dit UIT laten, tenzij objecten gefragmenteerd lijken.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="137"/>
        <source>Clustering Distance (px):</source>
        <translation>Clusterafstand (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="142"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Maximale afstand tussen detectiemiddens om ze samen te voegen (0-500 pixels).
Lagere waarden = voeg alleen zeer nabije detecties samen.
Hogere waarden = voeg verder uit elkaar liggende detecties samen (kan oversamenvoegen).</translation>
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
Klik om kleur te wijzigen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="71"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="71"/>
        <source>HSV: ({h}, {s}, {v})
Click to change color</source>
        <translation>HSV: ({h}, {s}, {v})
Klik om kleur te wijzigen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="78"/>
        <source>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Klik om kleur te wijzigen</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="67"/>
        <source>Color Anomaly</source>
        <translation>Kleurafwijking</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="68"/>
        <source>Motion Detection</source>
        <translation>Bewegingsdetectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="69"/>
        <source>Fusion</source>
        <translation>Fusie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="77"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Invoer &amp;&amp; Verwerking</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="78"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="79"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Opschoning</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="146"/>
        <source>Enable Motion Detection</source>
        <translation>Bewegingsdetectie inschakelen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="149"/>
        <source>Turn ON to highlight moving objects in the scene.
Most users can leave all other settings at their defaults.
Works best for stationary or slow-moving cameras and can be combined
with Color-Based Anomaly Detection for more robust results.</source>
        <translation>Schakel AAN om bewegende objecten in de scène te markeren.
De meeste gebruikers kunnen alle andere instellingen op hun standaardwaarden laten.
Werkt het beste voor stationaire of langzaam bewegende camera&apos;s en kan worden gecombineerd
met kleurgebaseerde afwijkingsdetectie voor robuustere resultaten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="162"/>
        <source>Algorithm</source>
        <translation>Algoritme</translation>
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
        <translation>Bewegingsdetectie-algoritme (geavanceerde instelling):

• FRAME_DIFF – snel en eenvoudig; zeer gevoelig voor elke beweging.
• MOG2 – gebalanceerd en adaptief (aanbevolen voor de meeste scènes).
• KNN – robuuster tegen ruis en complexe achtergronden.

Weet u het niet zeker, laat dit op MOG2 staan.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="185"/>
        <source>Detection Parameters</source>
        <translation>Detectieparameters</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="191"/>
        <source>Motion Threshold:</source>
        <translation>Bewegingsdrempel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="196"/>
        <source>Minimum pixel intensity change to consider as motion (1-255).
Lower values = more sensitive, detects subtle motion, more false positives.
Higher values = less sensitive, only strong motion, fewer false positives.
Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.</source>
        <translation>Minimale pixelintensiteitsverandering om als beweging te beschouwen (1-255).
Lagere waarden = gevoeliger, detecteert subtiele beweging, meer valse positieven.
Hogere waarden = minder gevoelig, alleen sterke beweging, minder valse positieven.
Aanbevolen: 10 voor algemeen gebruik, 5 voor subtiele beweging, 15-20 voor scènes met hoog contrast.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="204"/>
        <source>Blur Kernel (odd):</source>
        <translation>Blur-kernel (oneven):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="210"/>
        <source>Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).
Smooths the frame before motion detection to reduce noise.
Larger values = more smoothing, less noise, less detail.
Smaller values = less smoothing, more detail, more noise.
Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.</source>
        <translation>Gaussiaanse blur-kernel-grootte (moet oneven zijn: 1, 3, 5, 7, enz.).
Verzacht het frame vóór bewegingsdetectie om ruis te verminderen.
Grotere waarden = meer verzachting, minder ruis, minder detail.
Kleinere waarden = minder verzachting, meer detail, meer ruis.
Aanbevolen: 5 voor algemeen gebruik, 1 voor geen blur, 7-9 voor ruisachtige video&apos;s.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="219"/>
        <source>Morphology Kernel:</source>
        <translation>Morfologie-kernel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="225"/>
        <source>Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).
Removes small noise and fills holes in detections.
Larger values = remove more noise, merge nearby detections.
Smaller values = preserve detail, keep detections separate.
Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.</source>
        <translation>Morfologische bewerking kernel-grootte (oneven getallen: 1, 3, 5, enz.).
Verwijdert kleine ruis en vult gaten in detecties.
Grotere waarden = verwijder meer ruis, voeg nabije detecties samen.
Kleinere waarden = behoud detail, houd detecties gescheiden.
Aanbevolen: 3 voor algemeen gebruik, 1 voor precieze randen, 5-7 voor ruisachtige video&apos;s.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="236"/>
        <source>Persistence Filter</source>
        <translation>Persistentiefilter</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="241"/>
        <source>Window Frames (M):</source>
        <translation>Vensterframes (M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="246"/>
        <source>Size of temporal window for persistence filtering (2-30 frames).
Motion must appear in N out of M consecutive frames to be confirmed.
Larger values = longer memory, more stable, slower response.
Smaller values = shorter memory, faster response, more flicker.
Recommended: 3 for 30fps video (100ms window), 5 for 60fps.</source>
        <translation>Grootte van temporeel venster voor persistentiefiltering (2-30 frames).
Beweging moet verschijnen in N van M opeenvolgende frames om te worden bevestigd.
Grotere waarden = langer geheugen, stabieler, langzamere reactie.
Kleinere waarden = korter geheugen, snellere reactie, meer flikker.
Aanbevolen: 3 voor 30fps-video (100ms venster), 5 voor 60fps.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="254"/>
        <source>Threshold (N of M):</source>
        <translation>Drempel (N van M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="259"/>
        <source>Number of frames within window where motion must appear (N of M).
Higher values = more stringent, filters flickering false positives.
Lower values = more lenient, detects brief/intermittent motion.
Must be ≤ Window Frames.
Recommended: 2 (motion in 2 of last 3 frames).</source>
        <translation>Aantal frames binnen het venster waarin beweging moet verschijnen (N van M).
Hogere waarden = strenger, filtert flikkerende valse positieven.
Lagere waarden = toleranter, detecteert korte/intermitterende beweging.
Moet ≤ vensterframes zijn.
Aanbevolen: 2 (beweging in 2 van de laatste 3 frames).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="270"/>
        <source>Background Subtraction (MOG2/KNN)</source>
        <translation>Achtergrondsubtractie (MOG2/KNN)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="275"/>
        <source>History Frames:</source>
        <translation>Historieframes:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="280"/>
        <source>Number of frames to learn background model (10-500).
Only applies to MOG2 and KNN algorithms.
Longer history = adapts slower to lighting changes, more stable.
Shorter history = adapts faster, less stable.
Recommended: 50 (~1.7 sec at 30fps) for general use.</source>
        <translation>Aantal frames om het achtergrondmodel te leren (10-500).
Geldt alleen voor MOG2- en KNN-algoritmen.
Langere historie = past zich langzamer aan aan lichtveranderingen, stabieler.
Kortere historie = past zich sneller aan, minder stabiel.
Aanbevolen: 50 (~1,7 sec bij 30fps) voor algemeen gebruik.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="288"/>
        <source>Variance Threshold:</source>
        <translation>Variantiedrempel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="293"/>
        <source>Variance threshold for background/foreground classification (1.0-100.0).
Only applies to MOG2 and KNN algorithms.
Lower values = more sensitive, detects subtle changes, more false positives.
Higher values = less sensitive, only strong foreground objects.
Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.</source>
        <translation>Variantiedrempel voor achtergrond-/voorgrondclassificatie (1,0-100,0).
Geldt alleen voor MOG2- en KNN-algoritmen.
Lagere waarden = gevoeliger, detecteert subtiele veranderingen, meer valse positieven.
Hogere waarden = minder gevoelig, alleen sterke voorgrondobjecten.
Aanbevolen: 10,0 voor binnen, 15-20 voor buiten met variërende verlichting.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="301"/>
        <source>Detect Shadows (slower)</source>
        <translation>Schaduwen detecteren (langzamer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="303"/>
        <source>Enables shadow detection in MOG2 background subtractor.
Helps distinguish shadows from actual objects (reduces false positives).
Adds ~10-20% processing overhead.
Recommended: ON for outdoor scenes with strong shadows, OFF for speed.</source>
        <translation>Schakelt schaduwdetectie in de MOG2-achtergrondsubtractor in.
Helpt schaduwen te onderscheiden van werkelijke objecten (vermindert valse positieven).
Voegt ~10-20% verwerkingsoverhead toe.
Aanbevolen: AAN voor buitenscènes met sterke schaduwen, UIT voor snelheid.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="313"/>
        <source>Object Size Filter</source>
        <translation>Filter objectgrootte</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="318"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="454"/>
        <source>Min Object Area (px):</source>
        <translation>Min. objectgebied (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="323"/>
        <source>Minimum detection area in pixels (1-100000).
Filters out very small detections such as noise, insects, or raindrops.
Lower values = detect smaller objects (more noise).
Higher values = only larger objects (less noise).
Recommended: 5-10 for person-sized motion, 50-100 for vehicles.</source>
        <translation>Minimaal detectiegebied in pixels (1-100000).
Filtert zeer kleine detecties uit zoals ruis, insecten of regendruppels.
Lagere waarden = detecteer kleinere objecten (meer ruis).
Hogere waarden = alleen grotere objecten (minder ruis).
Aanbevolen: 5-10 voor beweging ter grootte van een persoon, 50-100 voor voertuigen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="331"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="467"/>
        <source>Max Object Area (px):</source>
        <translation>Max. objectgebied (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="336"/>
        <source>Maximum detection area in pixels (10-1000000).
Filters out very large regions such as full-frame lighting changes or giant shadows.
Lower values = only small/medium objects.
Higher values = allow large objects.
Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.</source>
        <translation>Maximaal detectiegebied in pixels (10-1000000).
Filtert zeer grote gebieden uit zoals lichtveranderingen op het hele frame of gigantische schaduwen.
Lagere waarden = alleen kleine/middelgrote objecten.
Hogere waarden = sta grote objecten toe.
Aanbevolen: 1000 voor personen, 10000 voor voertuigen, hoger voor zeer grote objecten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="347"/>
        <source>Camera Movement Detection</source>
        <translation>Camerabewegingsdetectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="350"/>
        <source>Pause on Camera Movement</source>
        <translation>Pauzeren bij camerabeweging</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="353"/>
        <source>Automatically pauses motion detection when camera is moving/panning.
Prevents false positives caused by camera movement (entire scene appears to move).
Detects camera movement by measuring percentage of frame with motion.
Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.</source>
        <translation>Pauzeert bewegingsdetectie automatisch wanneer de camera beweegt/pant.
Voorkomt valse positieven veroorzaakt door camerabeweging (de hele scène lijkt te bewegen).
Detecteert camerabeweging door het percentage frame met beweging te meten.
Aanbevolen: AAN voor handheld/drone-beelden, UIT voor stationaire statiefcamera&apos;s.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="361"/>
        <source>Threshold:</source>
        <translation>Drempel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="366"/>
        <source>Percentage of frame with motion to consider as camera movement (1-100%).
If more than this % of pixels show motion, pause detection.
Lower values = detect camera movement sooner (more pauses).
Higher values = tolerate more motion before pausing (fewer pauses).
Recommended: 15% for drone/handheld, 30% for shaky tripod.</source>
        <translation>Percentage frame met beweging om als camerabeweging te beschouwen (1-100%).
Als meer dan dit % van de pixels beweging vertoont, pauzeer dan de detectie.
Lagere waarden = detecteer camerabeweging eerder (meer pauzes).
Hogere waarden = tolereer meer beweging vóór pauzeren (minder pauzes).
Aanbevolen: 15% voor drone/handheld, 30% voor schokkerig statief.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="380"/>
        <source>Show Advanced Motion Settings</source>
        <translation>Geavanceerde bewegingsinstellingen tonen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="383"/>
        <source>Advanced users can expand this to adjust the motion algorithm
and detailed thresholds (sensitivity, filters, background model).
If you are unsure, leave this unchecked and use the defaults.</source>
        <translation>Geavanceerde gebruikers kunnen dit uitvouwen om het bewegings-algoritme
en gedetailleerde drempels (gevoeligheid, filters, achtergrondmodel) aan te passen.
Weet u het niet zeker, laat dit uitgevinkt en gebruik de standaardinstellingen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="402"/>
        <source>Enable Color-Based Anomaly Detection</source>
        <translation>Kleurgebaseerde afwijkingsdetectie inschakelen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="405"/>
        <source>Detects pixels whose colors are statistically rare in the frame.
Conceptually similar to MRMap&apos;s rarity-based detection for images.
Works well for: bright colored clothing, vehicles, equipment in natural scenes.
Can be combined with Motion Detection for more robust detection.</source>
        <translation>Detecteert pixels waarvan de kleuren statistisch zeldzaam zijn in het frame.
Conceptueel vergelijkbaar met MRMap&apos;s zeldzaamheidsgebaseerde detectie voor afbeeldingen.
Werkt goed voor: felgekleurde kleding, voertuigen, uitrusting in natuurlijke scènes.
Kan worden gecombineerd met bewegingsdetectie voor robuustere detectie.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="413"/>
        <source>Color Rarity Settings</source>
        <translation>Instellingen kleurzeldzaamheid</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="418"/>
        <source>Color Resolution (bins):</source>
        <translation>Kleurresolutie (bins):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="424"/>
        <source>Controls how finely colors are grouped into histogram bins (3-8 bits).
Analogous to MRMap&apos;s color binning.
Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.
Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.
Recommended: 4-5 for a balanced number of detections; use lower for very clean results,
and higher only when you need to pull out very subtle color differences.</source>
        <translation>Bepaalt hoe fijn kleuren worden gegroepeerd in histogram-bins (3-8 bits).
Analoog aan kleurbinning in MRMap.
Lagere waarden (3-4) = minder bins → sneller, meer groepering, minder maar sterkere detecties.
Hogere waarden (6-8) = meer bins → langzamer, minder groepering, meer maar zwakkere/kleinere detecties.
Aanbevolen: 4-5 voor een gebalanceerd aantal detecties; gebruik lager voor zeer schone resultaten,
en hoger alleen wanneer u zeer subtiele kleurverschillen wilt vinden.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="432"/>
        <source>4 bits</source>
        <translation>4 bits</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="436"/>
        <source>Rarity Threshold (% of colors):</source>
        <translation>Zeldzaamheidsdrempel (% van kleuren):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="442"/>
        <source>Sensitivity threshold for how rare a color must be to be flagged (0-100%).
Computed from the distribution of color-bin counts in the frame, similar in role
to MRMap&apos;s detection threshold.
Lower values (10-20%) = stricter: only very rare colors (fewer detections).
Medium values (25-40%) = balanced (recommended for general use).
Higher values (40-60%) = more sensitive: includes more common colors (more detections).</source>
        <translation>Gevoeligheidsdrempel voor hoe zeldzaam een kleur moet zijn om te worden gemarkeerd (0-100%).
Berekend uit de verdeling van kleur-bin-aantallen in het frame, vergelijkbaar in rol
met MRMap&apos;s detectiedrempel.
Lagere waarden (10-20%) = strenger: alleen zeer zeldzame kleuren (minder detecties).
Gemiddelde waarden (25-40%) = gebalanceerd (aanbevolen voor algemeen gebruik).
Hogere waarden (40-60%) = gevoeliger: omvat meer voorkomende kleuren (meer detecties).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="459"/>
        <source>Minimum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s minimum AOI area.
Lower values = detect smaller colored objects (more noise).
Higher values = only larger colored regions (less noise).
Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.</source>
        <translation>Minimaal gebied in pixels voor een kleurafwijking om als interessant object te worden behandeld.
Komt conceptueel overeen met MRMap&apos;s minimale AOI-gebied.
Lagere waarden = detecteer kleinere gekleurde objecten (meer ruis).
Hogere waarden = alleen grotere gekleurde gebieden (minder ruis).
Aanbevolen: 15 voor doelen ter grootte van een persoon, 50+ voor voertuigen of grote objecten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="472"/>
        <source>Maximum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s maximum AOI area.
Lower values = only detect smaller colored objects.
Higher values = allow larger colored regions.
Recommended: 50000 for general use, 10000 for small-object-only searches.</source>
        <translation>Maximaal gebied in pixels voor een kleurafwijking om als interessant object te worden behandeld.
Komt conceptueel overeen met MRMap&apos;s maximale AOI-gebied.
Lagere waarden = detecteer alleen kleinere gekleurde objecten.
Hogere waarden = sta grotere gekleurde gebieden toe.
Aanbevolen: 50000 voor algemeen gebruik, 10000 voor zoekacties met alleen kleine objecten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="480"/>
        <source>Blob Detection Method:</source>
        <translation>Blob-detectiemethode:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="482"/>
        <source>Find Contours</source>
        <translation>Contouren vinden</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="483"/>
        <source>Connected Components</source>
        <translation>Verbonden componenten</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="486"/>
        <source>Method for extracting blob regions from the detection mask:

Find Contours: Traditional OpenCV contour detection (default).
  Better for irregular shapes, provides detailed contour outlines.

Connected Components: Uses cv2.connectedComponentsWithStats.
  Provides direct blob statistics in a single pass.</source>
        <translation>Methode voor het extraheren van blob-gebieden uit het detectiemasker:

Contouren vinden: traditionele OpenCV-contourdetectie (standaard).
  Beter voor onregelmatige vormen, biedt gedetailleerde contour-omlijningen.

Verbonden componenten: gebruikt cv2.connectedComponentsWithStats.
  Levert directe blob-statistieken in één doorgang.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="497"/>
        <source>Color Space (Lighting Invariance)</source>
        <translation>Kleurruimte (lichtinvariantie)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="502"/>
        <source>Color Space:</source>
        <translation>Kleurruimte:</translation>
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
        <translation>Kleurruimte voor histogramgebaseerde afwijkingsdetectie:

RGB: gebruikt alle 3 kleurkanalen. Snel, maar gevoelig voor licht.
  Een rood shirt in de schaduw komt mogelijk niet overeen met een rood shirt in zonlicht.

HSV (tintgebaseerd): gebruikt alleen het tintkanaal - lichtinvariant.
  Rood blijft rood, ongeacht de helderheid. Goed voor gekleurde objecten.
  Filtert grijzen/witten uit waar tint ongedefinieerd is.

LAB (a,b chromaticiteit): gebruikt a,b-kanalen - lichtinvariant, perceptueel uniform.
  Geen discontinuïteit bij rood (in tegenstelling tot HSV). Het beste voor SAR.
  Filtert neutrale grijzen uit waar a,b bijna nul zijn.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="522"/>
        <source>HSV Min Saturation:</source>
        <translation>HSV min. verzadiging:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="529"/>
        <source>Minimum saturation for HSV mode (0-255).
Pixels below this saturation are ignored (grays, whites, blacks).
These have undefined/noisy hue values.
Lower = include more desaturated colors (may add noise).
Higher = only vivid colors (may miss faded/shadowed objects).
Recommended: 30-50 for general use.</source>
        <translation>Minimale verzadiging voor HSV-modus (0-255).
Pixels onder deze verzadiging worden genegeerd (grijzen, witten, zwarten).
Deze hebben ongedefinieerde/ruisachtige tintwaarden.
Lager = neem meer ontzadigde kleuren mee (kan ruis toevoegen).
Hoger = alleen levendige kleuren (kan vervaagde/in schaduw liggende objecten missen).
Aanbevolen: 30-50 voor algemeen gebruik.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="542"/>
        <source>LAB Min Chroma:</source>
        <translation>LAB min. chroma:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="549"/>
        <source>Minimum chroma (color intensity) for LAB mode (0-128).
Chroma = distance from neutral gray in a,b plane.
Pixels below this are ignored (near-neutral grays).
Lower = include more muted colors.
Higher = only vivid, saturated colors.
Recommended: 10-20 for general use.</source>
        <translation>Minimale chroma (kleurintensiteit) voor LAB-modus (0-128).
Chroma = afstand van neutraal grijs in het a,b-vlak.
Pixels eronder worden genegeerd (bijna-neutrale grijzen).
Lager = neem meer gedempte kleuren mee.
Hoger = alleen levendige, verzadigde kleuren.
Aanbevolen: 10-20 voor algemeen gebruik.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="567"/>
        <source>Color Match Expansion</source>
        <translation>Kleurovereenkomst-uitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="570"/>
        <source>Allow Similar Colors (Hue Expansion)</source>
        <translation>Vergelijkbare kleuren toestaan (tintuitbreiding)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="573"/>
        <source>Lets the detector treat similar colors as the same object.
For example, a red jacket that looks slightly orange in some frames will still be grouped together.
Turn this OFF if you only care about one very specific color shade.
Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).</source>
        <translation>Laat de detector vergelijkbare kleuren als hetzelfde object behandelen.
Bijvoorbeeld, een rode jas die er in sommige frames iets oranje uitziet, wordt nog steeds gegroepeerd.
Zet dit UIT als u alleen om één zeer specifieke kleurschakering geeft.
Zet dit AAN als u een hele familie kleuren wilt (bijv. alle warme rood/oranje-tinten).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="581"/>
        <source>Color Match Range:</source>
        <translation>Kleurovereenkomst-bereik:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="586"/>
        <source>How wide to stretch the color match around each detected color.
Smaller values = stay very close to the original color (more specific).
Larger values = include a wider range of similar colors (more forgiving).
Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.</source>
        <translation>Hoe breed de kleurovereenkomst rond elke gedetecteerde kleur uit te rekken.
Kleinere waarden = blijf zeer dicht bij de originele kleur (specifieker).
Grotere waarden = neem een breder scala aan vergelijkbare kleuren mee (toleranter).
Aanbevolen: lage waarden voor nauwkeurige kleuren, hogere waarden wanneer licht of camerakleur sterk verschuift.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="592"/>
        <source>±5 (~10°)</source>
        <translation>±5 (~10°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="599"/>
        <source>Color Exclusion</source>
        <translation>Kleuruitsluiting</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="602"/>
        <source>Enable Color Exclusion</source>
        <translation>Kleuruitsluiting inschakelen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="605"/>
        <source>Exclude specific background colors from color anomaly detection.
Useful for ignoring dominant scene colors such as grass, sky, or buildings.
Click on the color wheel below to choose colors to ignore.
Selected colors are highlighted with a dark border.</source>
        <translation>Sluit specifieke achtergrondkleuren uit van kleurafwijkingsdetectie.
Nuttig voor het negeren van dominante scène-kleuren zoals gras, lucht of gebouwen.
Klik op het onderstaande kleurwiel om kleuren te kiezen die genegeerd moeten worden.
Geselecteerde kleuren worden gemarkeerd met een donkere rand.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="613"/>
        <source>Click on color wheel to exclude colors (20° steps, 0-360°):</source>
        <translation>Klik op het kleurwiel om kleuren uit te sluiten (stappen van 20°, 0-360°):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="618"/>
        <source>Click on any color segment to toggle exclusion on/off.
Segments represent broad color ranges (e.g., blues, greens, reds).
Use this to teach the system which background colors to ignore.</source>
        <translation>Klik op een kleursegment om uitsluiting in/uit te schakelen.
Segmenten vertegenwoordigen brede kleurbereiken (bijv. blauwen, groenen, roden).
Gebruik dit om het systeem te leren welke achtergrondkleuren genegeerd moeten worden.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="635"/>
        <source>Detection Fusion</source>
        <translation>Detectiefusie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="638"/>
        <source>Enable Fusion (when both motion and color enabled)</source>
        <translation>Fusie inschakelen (wanneer zowel beweging als kleur zijn ingeschakeld)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="641"/>
        <source>Combines motion and color detections when both are enabled.
Only active when both Motion and Color detection are ON.
Different modes control how detections are merged.
Recommended: ON for robust multi-modal detection.</source>
        <translation>Combineert bewegings- en kleurdetecties wanneer beide zijn ingeschakeld.
Alleen actief wanneer zowel bewegings- als kleurdetectie AAN staan.
Verschillende modi bepalen hoe detecties worden samengevoegd.
Aanbevolen: AAN voor robuuste multimodale detectie.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="649"/>
        <source>Fusion Mode:</source>
        <translation>Fusiemodus:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="651"/>
        <source>UNION</source>
        <translation>UNIE</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="652"/>
        <source>INTERSECTION</source>
        <translation>DOORSNEDE</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="653"/>
        <source>COLOR_PRIORITY</source>
        <translation>KLEUR_PRIORITEIT</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="654"/>
        <source>MOTION_PRIORITY</source>
        <translation>BEWEGINGS_PRIORITEIT</translation>
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
        <translation>Hoe bewegings- en kleurdetecties te combineren:

• UNIE: toon alle detecties van beide (meeste detecties).
  Gebruik voor: maximale dekking, niets missen.

• DOORSNEDE: toon alleen detecties gevonden door beide (minste valse positieven).
  Gebruik voor: hoge betrouwbaarheid, valse positieven verminderen.

• KLEUR_PRIORITEIT: toon kleurdetecties + bewegingsdetecties die overeenkomen met kleur.
  Gebruik voor: meer vertrouwen op kleur (bijv. felgekleurde objecten).

• BEWEGINGS_PRIORITEIT: toon bewegingsdetecties + kleurdetecties die overeenkomen met beweging.
  Gebruik voor: meer vertrouwen op beweging (bijv. bewegende gecamoufleerde objecten).</translation>
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
        <translation>FPS: {fps} | Verwerking: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="12"/>
        <source>Color Anomaly Detection</source>
        <translation>Kleurafwijkingsdetectie</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="16"/>
        <source>Enable Color Anomaly Detection</source>
        <translation>Kleurafwijkingsdetectie inschakelen</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="27"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Hoe agressief moet ADIAT naar afwijkingen zoeken?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="38"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Opmerking: een hogere instelling vindt meer potentiële afwijkingen, maar kan ook het aantal valse positieven vergroten.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="56"/>
        <source>Motion Detection</source>
        <translation>Bewegingsdetectie</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="65"/>
        <source>Do you want to enable motion detection?</source>
        <translation>Wilt u bewegingsdetectie inschakelen?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="73"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="79"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="48"/>
        <source>Very 
Conservative</source>
        <translation>Zeer 
conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="49"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="50"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="51"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="52"/>
        <source>Very 
Aggressive</source>
        <translation>Zeer 
agressief</translation>
    </message>
</context>
<context>
    <name>ColorDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="76"/>
        <source>Color Selection</source>
        <translation>Kleurselectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="77"/>
        <source>Detection</source>
        <translation>Detectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="78"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Invoer &amp;&amp; Verwerking</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="79"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="80"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Opschoning</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="108"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="111"/>
        <source>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</source>
        <translation>Een nieuw kleurbereik toevoegen om te detecteren.
Kies uit HSV-kleurkiezer, afbeelding, lijst of recente kleuren.
U kunt meerdere kleurbereiken toevoegen om verschillende kleuren tegelijk te detecteren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="131"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="134"/>
        <source>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</source>
        <translation>HSV-kleurbereiken bekijken voor alle geconfigureerde kleuren.
Opent een weergavevenster voor elk kleurbereik met
de tint-, verzadigings- en waardebereiken die zullen worden gedetecteerd.
Handig om meerkleurendetectie te begrijpen en fijn af te stemmen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="157"/>
        <source>No colors configured. Add at least one color to start detection.</source>
        <translation>Geen kleuren geconfigureerd. Voeg ten minste één kleur toe om de detectie te starten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="178"/>
        <source>Min Object Area (px):</source>
        <translation>Min. objectgebied (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="184"/>
        <source>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</source>
        <translation>Minimaal detectiegebied in pixels (10-50000).
Filtert zeer kleine detecties uit (ruis, kleine objecten, fragmenten).
Lagere waarden = kleinere objecten detecteren, meer detecties, meer ruis.
Hogere waarden = alleen grote objecten, minder detecties, minder ruis.
Aanbevolen: 100 voor algemeen gebruik, 50 voor kleine objecten, 200-500 voor grote objecten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="193"/>
        <source>Max Object Area (px):</source>
        <translation>Max. objectgebied (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="199"/>
        <source>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</source>
        <translation>Maximaal detectiegebied in pixels (100-500000).
Filtert zeer grote detecties uit (schaduwen, lichtveranderingen, hele scène).
Lagere waarden = alleen kleine/middelgrote objecten.
Hogere waarden = staat grote objecten toe, kan ongewenste grote gebieden bevatten.
Aanbevolen: 100000 voor algemeen gebruik, 50000 voor kleine objecten, 200000+ voor grote objecten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="208"/>
        <source>Confidence Threshold:</source>
        <translation>Betrouwbaarheidsdrempel:</translation>
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
        <translation>Minimale betrouwbaarheidsscore om een detectie te accepteren (0-100%).
De betrouwbaarheid wordt berekend uit:
• Groottescore: gebied ten opzichte van max. gebied
• Vormscore: stevigheid (hoe compact/regelmatig de vorm is)
• Eind: gemiddelde van beide scores

Lagere waarden (0-30%) = accepteer meer detecties, inclusief zwakke/gefragmenteerde.
Hogere waarden (70-100%) = alleen detecties van hoge kwaliteit, goedgevormde vormen.
Aanbevolen: 50% voor gebalanceerde filtering, 30% voor meer detecties, 70% voor strenge kwaliteit.</translation>
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
        <translation>Kleur_{index}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="513"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Kleurbereiken: {count} kleuren</translation>
    </message>
</context>
<context>
    <name>ColorDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionController.py" line="134"/>
        <source>FPS: {fps} | Processing: {time}ms</source>
        <translation>FPS: {fps} | Verwerking: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorDetectionWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="52"/>
        <source>No Colors Selected</source>
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="62"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="244"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Kleurbereiken: {count} kleuren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="329"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="57"/>
        <source>Hue Histogram Unavailable</source>
        <translation>Tinthistogram niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="59"/>
        <source>No color image data is available for the current image.</source>
        <translation>Er zijn geen kleurafbeeldingsgegevens beschikbaar voor de huidige afbeelding.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="14"/>
        <source>Hue Histogram</source>
        <translation>Tinthistogram</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="23"/>
        <source>Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.</source>
        <translation>Tintverdeling van alle pixels versus AOI-pixels. Wanneer u over het diagram beweegt, worden overeenkomende pixels in de afbeelding gemarkeerd.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="32"/>
        <source>AOIs Only</source>
        <translation>Alleen AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Zoom resetten</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="61"/>
        <source>Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Sleep op het histogram of gebruik het muiswiel om te zoomen. Dubbelklik of gebruik Zoom resetten om terug te keren naar het volledige bereik.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="74"/>
        <source>Visible Hue Range</source>
        <translation>Zichtbaar tintbereik</translation>
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
        <translation>Bereik resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="64"/>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="174"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="127"/>
        <source>Hover over the histogram to inspect a hue band.</source>
        <translation>Beweeg over het histogram om een tintband te inspecteren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="30"/>
        <source>No hue histogram data available</source>
        <translation>Geen tinthistogramgegevens beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="180"/>
        <source>Hover hue: {value}°</source>
        <translation>Tint onder cursor: {value}°</translation>
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
        <translation>Kleur uit lijst selecteren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="42"/>
        <source>Search:</source>
        <translation>Zoeken:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="44"/>
        <source>Filter by name or uses…</source>
        <translation>Filter op naam of toepassingen…</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Name</source>
        <translation>Naam</translation>
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
        <translation>Toepassingen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="73"/>
        <source>Use Color</source>
        <translation>Kleur gebruiken</translation>
    </message>
</context>
<context>
    <name>ColorPickerDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="35"/>
        <source>Select Color from Image</source>
        <translation>Kleur uit afbeelding selecteren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="55"/>
        <source>Use Color</source>
        <translation>Kleur gebruiken</translation>
    </message>
</context>
<context>
    <name>ColorPickerImageViewer</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <source>Load Image</source>
        <translation>Afbeelding laden</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <source>Color Selector</source>
        <translation>Kleurkiezer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <source>Select Image</source>
        <translation>Afbeelding selecteren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="173"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="230"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="588"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="174"/>
        <source>Could not load image: {path}</source>
        <translation>Kan afbeelding niet laden: {path}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <source>Error loading image: {error}</source>
        <translation>Fout bij het laden van afbeelding: {error}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (onder cursor)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <source>Error setting image: {error}</source>
        <translation>Fout bij het instellen van afbeelding: {error}</translation>
    </message>
</context>
<context>
    <name>ColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="42"/>
        <source>Add a new color range to detect. Each color can have its own RGB range tolerances.</source>
        <translation>Een nieuw kleurbereik toevoegen om te detecteren. Elke kleur kan eigen RGB-bereiktoleranties hebben.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="45"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
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
        <translation>Opent het Bereikweergavevenster om:
- Het bereik van kleuren te zien dat tijdens de beeldanalyse wordt gezocht.
Gebruik dit om te zien welke kleuren worden gedetecteerd en om de kleurbereiken te optimaliseren vóór de verwerking.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="88"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
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
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="324"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
    </message>
</context>
<context>
    <name>ColorRangeDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="39"/>
        <source>HSV Color Range Selection</source>
        <translation>HSV-kleurbereikselectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="122"/>
        <source>Color Range Selection</source>
        <translation>Kleurbereikselectie</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="206"/>
        <source>Preview</source>
        <translation>Voorvertoning</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="210"/>
        <source>Original Image</source>
        <translation>Originele afbeelding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="216"/>
        <source>Original image preview.
Shows the unmodified input image for reference.
Use this to compare with the filtered result below.</source>
        <translation>Voorvertoning originele afbeelding.
Toont de ongewijzigde invoerafbeelding ter referentie.
Gebruik dit om te vergelijken met het gefilterde resultaat hieronder.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="222"/>
        <source>Filtered Result</source>
        <translation>Gefilterd resultaat</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="228"/>
        <source>Filtered result preview.
Shows pixels that match your current HSV color range settings.
Updates in real-time as you adjust the color and range values.
Matching pixels are shown, non-matching pixels appear black.</source>
        <translation>Voorvertoning gefilterd resultaat.
Toont pixels die overeenkomen met uw huidige HSV-kleurbereikinstellingen.
Wordt in realtime bijgewerkt terwijl u de kleur- en bereikwaarden aanpast.
Overeenkomende pixels worden getoond, niet-overeenkomende pixels verschijnen zwart.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="235"/>
        <source>Show mask only</source>
        <translation>Alleen masker tonen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="237"/>
        <source>Toggle between masked color result and grayscale mask.
• Unchecked (default): Shows the original image with matching colors visible
• Checked: Shows a black and white mask where white = matching pixels
Use the mask view to clearly see which pixels are being detected.</source>
        <translation>Schakel tussen gemaskeerd kleurresultaat en grijswaarden-masker.
• Uitgevinkt (standaard): toont de originele afbeelding met overeenkomende kleuren zichtbaar
• Aangevinkt: toont een zwart-wit masker waarin wit = overeenkomende pixels
Gebruik de maskerweergave om duidelijk te zien welke pixels worden gedetecteerd.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="244"/>
        <source>Original:</source>
        <translation>Origineel:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="246"/>
        <source>Result:</source>
        <translation>Resultaat:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="262"/>
        <source>Pick from Image...</source>
        <translation>Kiezen uit afbeelding...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="268"/>
        <source>Test on Image</source>
        <translation>Testen op afbeelding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="270"/>
        <source>Test current HSV range settings on the loaded image.
Manually triggers a preview update to see detection results.
Preview updates automatically as you adjust settings.</source>
        <translation>Test huidige HSV-bereikinstellingen op de geladen afbeelding.
Activeert handmatig een voorvertoningsupdate om detectieresultaten te zien.
Voorvertoning werkt automatisch bij wanneer u instellingen aanpast.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="280"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="282"/>
        <source>Cancel color selection.
Discards all changes and closes the dialog without applying the color range.</source>
        <translation>Annuleer kleurselectie.
Gooit alle wijzigingen weg en sluit het dialoogvenster zonder het kleurbereik toe te passen.</translation>
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
        <translation>Pas kleurselectie toe.
Slaat de huidige HSV-kleurbereikinstellingen op en sluit het dialoogvenster.
Het geselecteerde kleurbereik wordt gebruikt voor beeldanalyse.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="309"/>
        <source>Custom Colors</source>
        <translation>Aangepaste kleuren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="312"/>
        <source>Standard Dialog...</source>
        <translation>Standaarddialoog...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="318"/>
        <source>Add Current</source>
        <translation>Huidige toevoegen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="381"/>
        <source>Select Color</source>
        <translation>Kleur selecteren</translation>
    </message>
</context>
<context>
    <name>ColorRangeViewer</name>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="14"/>
        <source>Color Range Viewer</source>
        <translation>Kleurbereikweergave</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="37"/>
        <source>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</source>
        <translation>Geselecteerde afbeeldingen om te bekijken.
Toont de afbeeldingen die u hebt gekozen om te bekijken in de bereikweergave.
Klik op afbeeldingen hieronder om ze toe te voegen aan of te verwijderen uit deze sectie.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="42"/>
        <source>Selected</source>
        <translation>Geselecteerd</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="76"/>
        <source>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</source>
        <translation>Beschikbare afbeeldingen om te bekijken.
Toont alle afbeeldingen uit de invoermap die beschikbaar zijn om te selecteren.
Klik op afbeeldingen om ze naar de sectie Geselecteerd hierboven te verplaatsen.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="81"/>
        <source>Unselected</source>
        <translation>Niet geselecteerd</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="69"/>
        <source>No Colors Selected</source>
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="79"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="258"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
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
        <translation>Leeg slot - voeg een aangepaste kleur toe</translation>
    </message>
</context>
<context>
    <name>CoordinateController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="122"/>
        <source>GPS Coordinates: {coords}</source>
        <translation>GPS-coördinaten: {coords}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="148"/>
        <source>📋 Copy coordinates</source>
        <translation>📋 Coördinaten kopiëren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="152"/>
        <source>🗺️ Open in Google Maps</source>
        <translation>🗺️ Openen in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="156"/>
        <source>🌍 View in Google Earth</source>
        <translation>🌍 Bekijken in Google Earth</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="160"/>
        <source>📱 Send via WhatsApp</source>
        <translation>📱 Verzenden via WhatsApp</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="164"/>
        <source>📨 Send via Telegram</source>
        <translation>📨 Verzenden via Telegram</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="236"/>
        <source>Coordinates copied</source>
        <translation>Coördinaten gekopieerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="246"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="260"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="323"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="343"/>
        <source>Coordinates unavailable</source>
        <translation>Coördinaten niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="330"/>
        <source>Coordinate: {lat}, {lon} — {maps}</source>
        <translation>Coördinaat: {lat}, {lon} — {maps}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="350"/>
        <source>Coordinates: {lat}, {lon}</source>
        <translation>Coördinaten: {lat}, {lon}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="390"/>
        <source>No bearing info available</source>
        <translation>Geen koersinformatie beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="412"/>
        <source>North-Oriented View (Rotated {angle:.1f}°)</source>
        <translation>Noord-georiënteerde weergave (gedraaid {angle:.1f}°)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="444"/>
        <source>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</source>
        <translation>Oorspronkelijke koers: {bearing:.1f}° | Toegepaste rotatie: {rotation:.1f}°</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="454"/>
        <source>↑ NORTH</source>
        <translation>↑ NOORD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="463"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="474"/>
        <source>Error: {error}</source>
        <translation>Fout: {error}</translation>
    </message>
</context>
<context>
    <name>CoordinatorWindow</name>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="39"/>
        <source>Search Coordinator</source>
        <translation>Zoekcoördinator</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="58"/>
        <source>Create New Search</source>
        <translation>Nieuwe zoekopdracht maken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="63"/>
        <source>Open Existing Search</source>
        <translation>Bestaande zoekopdracht openen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="68"/>
        <source>Save Search</source>
        <translation>Zoekopdracht opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="74"/>
        <source>Add Batches to Search</source>
        <translation>Batches aan zoekopdracht toevoegen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="78"/>
        <source>Add more batch XML files to the current search project</source>
        <translation>Meer batch-XML-bestanden toevoegen aan het huidige zoekproject</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="96"/>
        <source>Dashboard</source>
        <translation>Dashboard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="100"/>
        <source>Batch Status</source>
        <translation>Batchstatus</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="104"/>
        <source>AOI Analysis</source>
        <translation>AOI-analyse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="112"/>
        <source>Review Selected Batch</source>
        <translation>Geselecteerde batch beoordelen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="116"/>
        <source>Open the selected batch&apos;s results in the Viewer to review (same as double-clicking the batch).</source>
        <translation>Open de resultaten van de geselecteerde batch in de Viewer om ze te beoordelen (hetzelfde als dubbelklikken op de batch).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="122"/>
        <source>Load Review XML</source>
        <translation>Beoordelings-XML laden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="128"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="658"/>
        <source>Export Consolidated Results</source>
        <translation>Geconsolideerde resultaten exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="140"/>
        <source>Project Information</source>
        <translation>Projectinformatie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="145"/>
        <source>No project loaded</source>
        <translation>Geen project geladen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="147"/>
        <source>Project:</source>
        <translation>Project:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="152"/>
        <source>Created by:</source>
        <translation>Gemaakt door:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="157"/>
        <source>Date:</source>
        <translation>Datum:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="176"/>
        <source>Total Batches</source>
        <translation>Totaal batches</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="177"/>
        <source>Total Images</source>
        <translation>Totaal afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="178"/>
        <source>Total Reviews</source>
        <translation>Totaal beoordelingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="179"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="327"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="361"/>
        <source>Reviewers</source>
        <translation>Beoordelaars</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="189"/>
        <source>Review Progress</source>
        <translation>Beoordelingsvoortgang</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="194"/>
        <source>Overall Completion:</source>
        <translation>Totale voltooiing:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="199"/>
        <source>0%</source>
        <translation>0%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="213"/>
        <source>Not Reviewed</source>
        <translation>Niet beoordeeld</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="222"/>
        <source>In Progress</source>
        <translation>Bezig</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="231"/>
        <source>Complete</source>
        <translation>Voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="239"/>
        <source>AOI Summary</source>
        <translation>AOI-overzicht</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="247"/>
        <source>Total AOIs</source>
        <translation>Totaal AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="255"/>
        <source>Flagged AOIs</source>
        <translation>Gemarkeerde AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="262"/>
        <source>Active Reviewers</source>
        <translation>Actieve beoordelaars</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="264"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="714"/>
        <source>No reviewers yet</source>
        <translation>Nog geen beoordelaars</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="312"/>
        <source>Batch review status and assignments. Load reviewer XMLs to update progress. Double-click a batch to open its results in the Viewer.</source>
        <translation>Status en toewijzingen voor batchcontrole. Laad XML-bestanden van reviewers om de voortgang bij te werken. Dubbelklik op een batch om de resultaten in de Viewer te openen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="323"/>
        <source>Batch ID</source>
        <translation>Batch-ID</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="324"/>
        <source>Algorithm</source>
        <translation>Algoritme</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="325"/>
        <source>Images</source>
        <translation>Afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="326"/>
        <source>Reviews</source>
        <translation>Beoordelingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="328"/>
        <source>Status</source>
        <translation>Status</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="349"/>
        <source>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</source>
        <translation>Geconsolideerde AOI-gegevens uit alle beoordelingen. Toont aantallen markeringen en opmerkingen van beoordelaars.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="358"/>
        <source>Image</source>
        <translation>Afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="359"/>
        <source>Location</source>
        <translation>Locatie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="360"/>
        <source>Flag Count</source>
        <translation>Aantal markeringen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="362"/>
        <source>Comments</source>
        <translation>Opmerkingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="379"/>
        <source>New Search Project</source>
        <translation>Nieuw zoekproject</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="380"/>
        <source>Enter project name:</source>
        <translation>Voer projectnaam in:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="389"/>
        <source>Coordinator Information</source>
        <translation>Coördinatorinformatie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="390"/>
        <source>Enter your name:</source>
        <translation>Voer uw naam in:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="399"/>
        <source>Select Batch Files</source>
        <translation>Batchbestanden selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="400"/>
        <source>Select Initial Batch XML Files</source>
        <translation>Initiële batch-XML-bestanden selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="403"/>
        <source>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</source>
        <translation>U kunt meerdere ADIAT_Data.xml-bestanden uit verschillende mappen selecteren.

Tips:
• Houd Ctrl (Windows/Linux) of Cmd (Mac) ingedrukt om meerdere bestanden te selecteren
• U kunt later meer batches toevoegen via de knop &apos;Batches aan zoekopdracht toevoegen&apos;
• Elke batch moet een verwerkt ADIAT_Data.xml-bestand zijn</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="417"/>
        <source>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</source>
        <translation>Batch ADIAT_Data.xml-bestanden selecteren (houd Ctrl ingedrukt voor meerdere)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="419"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="434"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="558"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="605"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="660"/>
        <source>XML Files (*.xml)</source>
        <translation>XML-bestanden (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <source>Save Search Project</source>
        <translation>Zoekproject opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="444"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="517"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="577"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="641"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="667"/>
        <source>Success</source>
        <translation>Geslaagd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="445"/>
        <source>Search project &apos;{project}&apos; created successfully!</source>
        <translation>Zoekproject &apos;{project}&apos; succesvol aangemaakt!</translation>
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
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="453"/>
        <source>Failed to save project file.</source>
        <translation>Kan projectbestand niet opslaan.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="456"/>
        <source>Failed to create project.</source>
        <translation>Kan project niet aanmaken.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="462"/>
        <source>Open Search Project</source>
        <translation>Zoekproject openen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="464"/>
        <source>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</source>
        <translation>Zoekprojectbestanden (ADIAT_Search_*.xml);;Alle XML-bestanden (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="474"/>
        <source>Project loaded successfully!</source>
        <translation>Project succesvol geladen!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="493"/>
        <source>Search project file not found:
{path}</source>
        <translation>Zoekprojectbestand niet gevonden:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="507"/>
        <source>Failed to load project file.</source>
        <translation>Kan projectbestand niet laden.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="518"/>
        <source>Project saved successfully!</source>
        <translation>Project succesvol opgeslagen!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="521"/>
        <source>Failed to save project.</source>
        <translation>Kan project niet opslaan.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="528"/>
        <source>No Project</source>
        <translation>Geen project</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="529"/>
        <source>Please create or open a project first.</source>
        <translation>Maak of open eerst een project.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="536"/>
        <source>Add Batches</source>
        <translation>Batches toevoegen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="537"/>
        <source>Add More Batch XML Files</source>
        <translation>Meer batch-XML-bestanden toevoegen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="540"/>
        <source>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</source>
        <translation>Selecteer aanvullende ADIAT_Data.xml batchbestanden om aan deze zoekopdracht toe te voegen.

Tips:
• Houd Ctrl (Windows/Linux) of Cmd (Mac) ingedrukt om meerdere bestanden te selecteren
• Bestanden mogen in verschillende mappen staan
• Elke batch moet een verwerkt ADIAT_Data.xml-bestand zijn
• Nieuwe batches worden opeenvolgend genummerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="556"/>
        <source>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</source>
        <translation>Toe te voegen Batch ADIAT_Data.xml-bestanden selecteren (houd Ctrl ingedrukt voor meerdere)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="579"/>
        <source>Successfully added {count} batch(es) to the project!
Total batches: {total}</source>
        <translation>{count} batch(es) succesvol toegevoegd aan het project!
Totaal aantal batches: {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="589"/>
        <source>No Batches Added</source>
        <translation>Geen batches toegevoegd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="591"/>
        <source>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</source>
        <translation>Er zijn geen batches toegevoegd. Controleer of de XML-bestanden geldige ADIAT_Data.xml-bestanden zijn.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="603"/>
        <source>Select Reviewer&apos;s ADIAT_Data.xml File</source>
        <translation>ADIAT_Data.xml-bestand van beoordelaar selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="616"/>
        <source>No Batches</source>
        <translation>Geen batches</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="617"/>
        <source>No batches found in project.</source>
        <translation>Geen batches gevonden in het project.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="625"/>
        <source>Select Batch</source>
        <translation>Batch selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="626"/>
        <source>Which batch does this review belong to?</source>
        <translation>Tot welke batch behoort deze beoordeling?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="642"/>
        <source>Review data loaded and merged successfully!</source>
        <translation>Beoordelingsgegevens succesvol geladen en samengevoegd!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="648"/>
        <source>Failed to load review data.</source>
        <translation>Kan beoordelingsgegevens niet laden.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="668"/>
        <source>Consolidated results exported to:
{path}</source>
        <translation>Geconsolideerde resultaten geëxporteerd naar:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="671"/>
        <source>Failed to export results.</source>
        <translation>Kan resultaten niet exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="697"/>
        <source>{value}%</source>
        <translation>{value}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="758"/>
        <source>No Batch Selected</source>
        <translation>Geen batch geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="759"/>
        <source>Select a batch in the table, then click Review Selected Batch.</source>
        <translation>Selecteer een batch in de tabel en klik vervolgens op Geselecteerde batch beoordelen.</translation>
    </message>
</context>
<context>
    <name>CoverageExtentExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="129"/>
        <source>Generate Coverage Extent KML</source>
        <translation>KML van dekkingsomvang genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="131"/>
        <source>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</source>
        <translation>Een KML-bestand genereren met de geografische dekkingsomvang van alle afbeeldingen?

Hiermee worden polygonen gemaakt die het gebied vertegenwoordigen dat door alle afbeeldingen wordt gedekt. Overlappende afbeeldingsgebieden worden samengevoegd tot één polygoon.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="145"/>
        <source>Save Coverage Extent KML</source>
        <translation>KML van dekkingsomvang opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="147"/>
        <source>KML files (*.kml)</source>
        <translation>KML-bestanden (*.kml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="160"/>
        <source>Generating Coverage Extent KML</source>
        <translation>KML van dekkingsomvang genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="163"/>
        <source>Calculating coverage extent...</source>
        <translation>Dekkingsomvang berekenen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="209"/>
        <source>Error generating coverage extent KML</source>
        <translation>Fout bij genereren van KML van dekkingsomvang</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="215"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="263"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="216"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="264"/>
        <source>Failed to generate coverage extent KML:
{error}</source>
        <translation>Kan KML van dekkingsomvang niet genereren:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="246"/>
        <source>Coverage extent generation cancelled</source>
        <translation>Genereren van dekkingsomvang geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="257"/>
        <source>Error generating coverage extent</source>
        <translation>Fout bij genereren van dekkingsomvang</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="270"/>
        <source>No valid images found for coverage extent calculation</source>
        <translation>Geen geldige afbeeldingen gevonden voor berekening van dekkingsomvang</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="276"/>
        <source>Coverage Extent</source>
        <translation>Dekkingsomvang</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="278"/>
        <source>Could not calculate coverage extent.

Images processed: {processed}
Images skipped: {skipped}

Images may be skipped for the following reasons:
  • Missing GPS data in EXIF
  • No valid GSD (missing altitude/focal length)
  • Gimbal not nadir (must be -85° to -95°)</source>
        <translation>Kan dekkingsomvang niet berekenen.

Verwerkte afbeeldingen: {processed}
Overgeslagen afbeeldingen: {skipped}

Afbeeldingen kunnen om de volgende redenen worden overgeslagen:
  • Ontbrekende GPS-gegevens in EXIF
  • Geen geldige GSD (ontbrekende hoogte/brandpuntsafstand)
  • Gimbal niet nadir (moet tussen -85° en -95° zijn)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="300"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="301"/>
        <source>{value:.2f} acres</source>
        <translation>{value:.2f} acres</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="305"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="306"/>
        <source>{value:.3f} km²</source>
        <translation>{value:.3f} km²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="309"/>
        <source>Coverage extent KML saved: {area}</source>
        <translation>KML van dekkingsomvang opgeslagen: {area}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="318"/>
        <source>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</source>
        <translation>

Afbeeldingen kunnen worden overgeslagen vanwege:
  • Ontbrekende GPS-gegevens
  • Geen geldige GSD
  • Gimbal niet nadir</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="326"/>
        <source>Coverage Extent KML Generated</source>
        <translation>KML van dekkingsomvang gegenereerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="328"/>
        <source>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</source>
        <translation>KML-bestand van dekkingsomvang succesvol gemaakt!

Bestand: {file}
Verwerkte afbeeldingen: {processed}
Overgeslagen afbeeldingen: {skipped}
Dekkingsgebieden: {areas}
Totaal gebied: {area}{skip_info}</translation>
    </message>
</context>
<context>
    <name>DetectionRowWidget</name>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="62"/>
        <source>CLASS</source>
        <translation>KLASSE</translation>
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
        <translation>Videofeed: --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="109"/>
        <source>View</source>
        <translation>Weergeven</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="112"/>
        <source>Open the full-size thumbnail and metadata.</source>
        <translation>Open de miniatuur op volledige grootte en de metadata.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="119"/>
        <source>Copy GPS</source>
        <translation>GPS kopiëren</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="122"/>
        <source>Copy the detection&apos;s coordinates to the clipboard in the operator-preferred format.</source>
        <translation>Kopieer de coördinaten van de detectie naar het klembord in de door de operator gewenste indeling.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="115"/>
        <source>{name} ({code})</source>
        <translation>{name} ({code})</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="124"/>
        <source>Feed: {feed}</source>
        <translation>Videofeed: {feed}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="132"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Serienummer drone: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="150"/>
        <source>no
thumb</source>
        <translation>geen
miniatuur</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="156"/>
        <source>bad
thumb</source>
        <translation>ongeldige
miniatuur</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="224"/>
        <source>Detection</source>
        <translation>Detectie</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="283"/>
        <source>No image available.</source>
        <translation>Geen afbeelding beschikbaar.</translation>
    </message>
</context>
<context>
    <name>DirectoriesPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="55"/>
        <source>Select Input Directory</source>
        <translation>Invoermap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="72"/>
        <source>Select Output Directory</source>
        <translation>Uitvoermap selecteren</translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="58"/>
        <source>Processing...</source>
        <translation>Verwerken...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="72"/>
        <source>Starting...</source>
        <translation>Starten...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="76"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="103"/>
        <source>Cancelling...</source>
        <translation>Annuleren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="104"/>
        <source>Cancellation requested...</source>
        <translation>Annulering aangevraagd...</translation>
    </message>
</context>
<context>
    <name>FlightPairingDialog</name>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="14"/>
        <source>Add Flight Feed</source>
        <translation>Vluchtfeed toevoegen</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="27"/>
        <source>Ask the drone operator to read out the 6-character pairing code shown on their controller.</source>
        <translation>Vraag de drone-operator de koppelcode van 6 tekens op de controller voor te lezen.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="40"/>
        <source>e.g. K3F7PM</source>
        <translation>bijv. K3F7PM</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="85"/>
        <source>Pairing…</source>
        <translation>Koppelen…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="98"/>
        <source>Looking up code, exchanging keys, gathering ICE candidates.</source>
        <translation>Code opzoeken, sleutels uitwisselen en ICE-kandidaten verzamelen.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="135"/>
        <source>Pairing failed</source>
        <translation>Koppelen mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="69"/>
        <location filename="../resources/views/flight/flight_pairing.ui" line="200"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="207"/>
        <source>Connect</source>
        <translation>Verbinden</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="67"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="85"/>
        <source>drone has {current}/{limit} viewers</source>
        <translation>drone heeft {current}/{limit} kijkers</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="98"/>
        <source>known device — same fingerprint as last pair</source>
        <translation>bekend apparaat — zelfde vingerafdruk als bij vorige koppeling</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="101"/>
        <source>new device</source>
        <translation>nieuw apparaat</translation>
    </message>
</context>
<context>
    <name>FlightTile</name>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="460"/>
        <source>Feed {code}</source>
        <translation>Videofeed {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="298"/>
        <source>Choose recording directory</source>
        <translation>Opnamemap kiezen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="328"/>
        <source>REC ● {filename}</source>
        <translation>REC ● {filename}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="333"/>
        <source>REC error: {msg}</source>
        <translation>REC-fout: {msg}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="341"/>
        <source>REC failed to start</source>
        <translation>Opname kon niet starten</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="355"/>
        <source>Recording saved</source>
        <translation>Opname opgeslagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="364"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="383"/>
        <source>Network: {state}</source>
        <translation>Netwerk: {state}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="377"/>
        <source>latency: {ms:.0f}ms</source>
        <translation>latentie: {ms:.0f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="379"/>
        <source>latency: --</source>
        <translation>latentie: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="457"/>
        <source>{name} · {code}</source>
        <translation>{name} · {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="482"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Serienummer drone: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="520"/>
        <source>Rename Feed</source>
        <translation>Feed hernoemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="522"/>
        <source>Nickname for this drone (persists across new pairing codes via the aircraft serial number). Leave blank to clear.</source>
        <translation>Bijnaam voor deze drone (blijft behouden bij nieuwe koppelcodes via het serienummer van de drone). Laat leeg om te wissen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="554"/>
        <source>Initializing</source>
        <translation>Initialiseren</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="555"/>
        <source>Connecting</source>
        <translation>Verbinden</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="556"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="557"/>
        <source>Connected</source>
        <translation>Verbonden</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="558"/>
        <source>Disconnected</source>
        <translation>Verbinding verbroken</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="559"/>
        <source>Failed</source>
        <translation>Mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="560"/>
        <source>Closed</source>
        <translation>Gesloten</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="574"/>
        <source>Rename Feed...</source>
        <translation>Feed hernoemen...</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="591"/>
        <source>Restore</source>
        <translation>Herstellen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="595"/>
        <source>Maximize</source>
        <translation>Maximaliseren</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="580"/>
        <source>Full Screen</source>
        <translation>Volledig scherm</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="601"/>
        <source>Mute Detections in Gallery</source>
        <translation>Detecties in galerij verbergen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="617"/>
        <source>Stop Recording</source>
        <translation>Opname stoppen</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="621"/>
        <source>Start Recording…</source>
        <translation>Opname starten…</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="625"/>
        <source>Reconnect</source>
        <translation>Opnieuw verbinden</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="631"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
</context>
<context>
    <name>FlightTileContents</name>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="44"/>
        <source>Waiting for video…</source>
        <translation>Wachten op video…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="90"/>
        <source>Network: new</source>
        <translation>Netwerk: nieuw</translation>
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
        <translation>latentie: --</translation>
    </message>
</context>
<context>
    <name>FlightTileController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="191"/>
        <source>Looking up code {code} and connecting to the drone.</source>
        <translation>Code {code} opzoeken en verbinding maken met de drone.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="266"/>
        <source>Name this device</source>
        <translation>Geef dit apparaat een naam</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="268"/>
        <source>Give this publisher a name so you can recognise it next time (e.g. &apos;Operator A&apos;s M4E&apos;).</source>
        <translation>Geef deze zender een naam zodat u hem de volgende keer herkent (bijv. &apos;M4E van operator A&apos;).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="286"/>
        <source>Device &apos;{label}&apos; presented a different DTLS fingerprint than the last time you paired with it. This could mean the controller was reset, a different controller is using the label, or somebody is impersonating it.

Reject if you weren&apos;t expecting this.</source>
        <translation>Apparaat &apos;{label}&apos; presenteerde een andere DTLS-vingerafdruk dan de vorige keer dat u ermee koppelde. Dit kan betekenen dat de controller is gereset, dat een andere controller dit label gebruikt of dat iemand zich ervoor uitgeeft.

Wijs af als u dit niet verwachtte.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="453"/>
        <source>Pairing ended before video could start. Ask the operator to generate a new code and try again.</source>
        <translation>De koppeling eindigde voordat de video kon starten. Vraag de operator een nieuwe code te genereren en probeer het opnieuw.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="294"/>
        <source>Fingerprint mismatch — &apos;{label}&apos;</source>
        <translation>Vingerafdruk komt niet overeen — &apos;{label}&apos;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="303"/>
        <source>Fingerprint changed on {ts}; previous identity was overwritten after operator review.</source>
        <translation>Vingerafdruk gewijzigd op {ts}; de vorige identiteit is overschreven na controle door de operator.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="395"/>
        <source>This drone already has {current} viewers connected (maximum {limit}). Ask one to disconnect, or try again later.</source>
        <translation>Deze drone heeft al {current} kijkers verbonden (maximum {limit}). Vraag iemand de verbinding te verbreken of probeer het later opnieuw.</translation>
    </message>
</context>
<context>
    <name>FlightViewerController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="499"/>
        <source>New flight session</source>
        <translation>Nieuwe vluchtsessie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="501"/>
        <source>Mobile started a new flight under code {code}. The previous session&apos;s detections are still saved on this computer. Discard them, or keep them archived?</source>
        <translation>Mobile is een nieuwe vlucht gestart met code {code}. De detecties van de vorige sessie staan nog op deze computer. Wilt u ze verwijderen of gearchiveerd bewaren?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="627"/>
        <source>Image Analysis</source>
        <translation>Beeldanalyse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="650"/>
        <source>Streaming Detector</source>
        <translation>Streamingdetector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="667"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="668"/>
        <source>Failed to open {target}:
{error}</source>
        <translation>Kan {target} niet openen:
{error}</translation>
    </message>
</context>
<context>
    <name>FlightViewerWindow</name>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="14"/>
        <source>ADIAT Flight Viewer</source>
        <translation>ADIAT-vluchtviewer</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="21"/>
        <source>Add a feed to begin.  Use Add Feed in the toolbar.</source>
        <translation>Voeg een feed toe om te beginnen. Gebruik Feed toevoegen in de werkbalk.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="76"/>
        <source>Main Toolbar</source>
        <translation>Hoofdwerkbalk</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="97"/>
        <source>+ Add Feed</source>
        <translation>+ Feed toevoegen</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="49"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="66"/>
        <source>Help</source>
        <translation>Hulp</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="100"/>
        <source>Pair with an ADIAT Mobile drone controller using a 6-character code.</source>
        <translation>Koppel met een ADIAT Mobile-dronecontroller via een code van 6 tekens.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="105"/>
        <source>Mission Gallery</source>
        <translation>Missiegalerij</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="114"/>
        <source>Show or hide the aggregate Mission Gallery panel.</source>
        <translation>Toon of verberg het samengevoegde paneel Missiegalerij.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="119"/>
        <source>Save Layout</source>
        <translation>Indeling opslaan</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="122"/>
        <source>Save the current dock arrangement for next session.</source>
        <translation>Sla de huidige dockindeling op voor de volgende sessie.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="127"/>
        <source>Restore Layout</source>
        <translation>Indeling herstellen</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="130"/>
        <source>Apply the last saved dock arrangement.</source>
        <translation>Pas de laatst opgeslagen dockindeling toe.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="135"/>
        <source>Close Viewer</source>
        <translation>Viewer sluiten</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="140"/>
        <source>Map</source>
        <translation>Kaart</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="149"/>
        <source>Show or hide the detection map dock.</source>
        <translation>Toon of verberg het kaartdock met detecties.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="154"/>
        <source>Open Image Analysis</source>
        <translation>Beeldanalyse openen</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="157"/>
        <source>Switch to the Image Analysis window for post-flight image review.</source>
        <translation>Schakel naar het venster Beeldanalyse voor controle van beelden na de vlucht.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="162"/>
        <source>Open Streaming Detector</source>
        <translation>Streamingdetector openen</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="165"/>
        <source>Switch to the Streaming Detector window for RTMP / HDMI capture sessions.</source>
        <translation>Schakel naar het venster Streamingdetector voor RTMP- / HDMI-opnamesessies.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="170"/>
        <source>ADIAT Help</source>
        <translation>ADIAT-help</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="173"/>
        <source>Open the ADIAT documentation in your browser.</source>
        <translation>Open de ADIAT-documentatie in uw browser.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightViewerWindow.py" line="274"/>
        <source>Rename Feed...</source>
        <translation>Feed hernoemen...</translation>
    </message>
</context>
<context>
    <name>FrameTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="52"/>
        <source>Enable Processing Region Mask</source>
        <translation>Verwerkingsgebiedmasker inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="55"/>
        <source>Enable to restrict detection processing to a specific region of the video.
Useful for excluding edges, UI overlays, or focusing on specific areas.
Improves performance by not processing masked regions.</source>
        <translation>Inschakelen om detectieverwerking te beperken tot een specifiek gebied van de video.
Nuttig voor het uitsluiten van randen, UI-overlays of het focussen op specifieke gebieden.
Verbetert de prestaties door gemaskeerde gebieden niet te verwerken.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="67"/>
        <source>Enable Frame Buffer</source>
        <translation>Framebuffer inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="69"/>
        <source>Exclude a uniform border from all edges of the video.
Enter the number of pixels to exclude from each edge.
The inner area will be processed for detections.</source>
        <translation>Sluit een uniforme rand uit aan alle randen van de video.
Voer het aantal pixels in dat van elke rand moet worden uitgesloten.
Het binnengebied wordt verwerkt voor detecties.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="77"/>
        <source>Frame Buffer Settings</source>
        <translation>Framebuffer-instellingen</translation>
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
        <translation>Aantal pixels om uit te sluiten van alle randen (0-1000).
Een waarde van 50 sluit 50 pixels uit van boven, onder, links en rechts.
Nuttig voor het verwijderen van UI-overlays of cameralens-vervorming aan de randen.
Deze waarde is gebaseerd op de oorspronkelijke videoresolutie.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="97"/>
        <source>Enable Image Mask</source>
        <translation>Afbeeldingsmasker inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="99"/>
        <source>Load a black/white image as a custom mask.
White areas will be processed, black areas excluded.
The mask will be scaled to match the video resolution.</source>
        <translation>Laad een zwart-witafbeelding als aangepast masker.
Witte gebieden worden verwerkt, zwarte gebieden uitgesloten.
Het masker wordt geschaald om overeen te komen met de videoresolutie.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="107"/>
        <source>Image Mask Settings</source>
        <translation>Maskerinstellingen afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="114"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="211"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="332"/>
        <source>No mask image selected</source>
        <translation>Geen maskerafbeelding geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="117"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="118"/>
        <source>Select a black/white image file to use as mask</source>
        <translation>Selecteer een zwart-witafbeeldingsbestand om als masker te gebruiken</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="121"/>
        <source>Clear</source>
        <translation>Wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="122"/>
        <source>Clear the selected mask image</source>
        <translation>De geselecteerde maskerafbeelding wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="128"/>
        <source>White = Process, Black = Exclude</source>
        <translation>Wit = verwerken, zwart = uitsluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="136"/>
        <source>Visualization</source>
        <translation>Visualisatie</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="139"/>
        <source>Show mask overlay on video</source>
        <translation>Maskeroverlay op video tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="142"/>
        <source>Display the processing region on the rendered video.
Frame mode: Shows a cyan rectangle outline of the processed area.
Image mask: Shows a semi-transparent overlay of excluded regions.</source>
        <translation>Toon het verwerkingsgebied op de gerenderde video.
Framemodus: toont een cyaankleurige rechthoek-omlijning van het verwerkte gebied.
Afbeeldingsmasker: toont een semi-transparante overlay van uitgesloten gebieden.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="226"/>
        <source>Invalid Image</source>
        <translation>Ongeldige afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="227"/>
        <source>{error}</source>
        <translation>{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="229"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Kan de geselecteerde afbeelding niet laden. Kies een geldig afbeeldingsbestand.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="238"/>
        <source>Aspect Ratio Mismatch</source>
        <translation>Onjuiste beeldverhouding</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="240"/>
        <source>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</source>
        <translation>{error}

Het masker wordt geschaald om te passen, wat vervorming kan veroorzaken.

Wilt u doorgaan?</translation>
    </message>
</context>
<context>
    <name>GPSMapController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="104"/>
        <source>No GPS data found in images</source>
        <translation>Geen GPS-gegevens gevonden in afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="189"/>
        <source>POD overlay cleared — the elevation/canopy source changed. Recalculate to refresh it.</source>
        <translation>POD-overlay gewist — de hoogte-/bladerdakbron is gewijzigd. Herbereken om te vernieuwen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="200"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Tegels downloaden is uitgeschakeld in de modus alleen offline</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="231"/>
        <source>Calculate POD Coverage?</source>
        <translation>POD-dekking berekenen?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="232"/>
        <source>Coverage data is ready. Calculate the probability-of-detection heatmap for this mission now? (May take several minutes.)</source>
        <translation>De dekkingsgegevens zijn gereed. Nu de detectiekans-heatmap voor deze missie berekenen? (Kan enkele minuten duren.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="291"/>
        <source>Your local USGS 3DEP tiles only partially cover this mission.</source>
        <translation>Uw lokale USGS 3DEP-tegels dekken deze missie slechts gedeeltelijk.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="294"/>
        <source>Your local USGS 3DEP tiles do not cover this mission.</source>
        <translation>Uw lokale USGS 3DEP-tegels dekken deze missie niet.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="298"/>
        <source>Local Elevation Coverage</source>
        <translation>Dekking lokale hoogtegegevens</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="300"/>
        <source>Frames outside the local tiles will use online AWS Terrain Tiles (~30 m) elevation instead. You can download 1 m tiles for this area first, or continue with the fallback.</source>
        <translation>Frames buiten de lokale tegels gebruiken in plaats daarvan online AWS Terrain Tiles-hoogte (~30 m). U kunt eerst 1 m-tegels voor dit gebied downloaden of doorgaan met de fallback.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="303"/>
        <source>Download Tiles...</source>
        <translation>Tegels downloaden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="305"/>
        <source>Continue</source>
        <translation>Doorgaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="334"/>
        <source>POD calculation is unavailable</source>
        <translation>POD-berekening is niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="353"/>
        <source>The tile downloader is unavailable</source>
        <translation>De tegeldownloader is niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="383"/>
        <source>Download Canopy Data?</source>
        <translation>Kroongegevens downloaden?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="384"/>
        <source>No canopy-height data is configured for this mission.

Download elevation and canopy tiles for this area now so the canopy overlay and terrain-aware detection coverage can use them?

This downloads Meta/WRI canopy height (1 m) and sets it as the canopy source, replacing any LANDFIRE selection (LANDFIRE tiles must be added manually).</source>
        <translation>Er zijn geen kroonhoogtegegevens geconfigureerd voor deze missie.

Nu hoogte- en kroontegels voor dit gebied downloaden zodat de kroonoverlay en de terreinbewuste detectiedekking ze kunnen gebruiken?

Hiermee wordt Meta/WRI-kroonhoogte (1 m) gedownload en ingesteld als bron voor kroongegevens, waarbij een eventuele LANDFIRE-selectie wordt vervangen (LANDFIRE-tegels moeten handmatig worden toegevoegd).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="579"/>
        <source>Not covered — no looks</source>
        <translation>Niet gedekt — geen waarnemingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="580"/>
        <source>Terrain occlusion</source>
        <translation>Terreinocclusie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="581"/>
        <source>Canopy</source>
        <translation>Boomkroon</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="582"/>
        <source>Image resolution (GSD)</source>
        <translation>Beeldresolutie (GSD)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="583"/>
        <source>None</source>
        <translation>Geen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="585"/>
        <source>Unknown</source>
        <translation>Onbekend</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="765"/>
        <source>Building canopy overlay...</source>
        <translation>Kroonoverlay wordt gemaakt...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="791"/>
        <source>No canopy data covers this area</source>
        <translation>Geen kroongegevens dekken dit gebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="851"/>
        <source>POD: {pod}% (beta)   Looks: {looks}</source>
        <translation>POD: {pod}% (beta)   Waarnemingen: {looks}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="854"/>
        <source>Limiting factor: {factor}</source>
        <translation>Beperkende factor: {factor}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="889"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="902"/>
        <source>Image {n}</source>
        <translation>Afbeelding {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="890"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="905"/>
        <source>View {name}</source>
        <translation>Weergave {name}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="862"/>
        <source>Find location in images</source>
        <translation>Locatie in afbeeldingen zoeken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="909"/>
        <source>{name} (no flagged AOIs)</source>
        <translation>{name} (geen gemarkeerde AOI&apos;s)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1044"/>
        <source>GPS coordinate not in any images</source>
        <translation>GPS-coördinaat in geen enkele afbeelding</translation>
    </message>
</context>
<context>
    <name>GPSMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="54"/>
        <source>GPS Map View</source>
        <translation>GPS-kaartweergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="108"/>
        <source>Zoom In (+)</source>
        <translation>Inzoomen (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="112"/>
        <source>Zoom Out (-)</source>
        <translation>Uitzoomen (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="116"/>
        <source>Fit All (F)</source>
        <translation>Alles passend maken (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="120"/>
        <source>Rotate (R)</source>
        <translation>Roteren (R)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="128"/>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="338"/>
        <source>Satellite View</source>
        <translation>Satellietweergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="135"/>
        <source>POD Overlay</source>
        <translation>POD-overlay</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="139"/>
        <source>Run a map export with the POD option to generate this overlay</source>
        <translation>Voer een kaartexport uit met de POD-optie om deze overlay te genereren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="144"/>
        <source>POD (beta)</source>
        <translation>POD (beta)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="145"/>
        <source>Look count</source>
        <translation>Aantal waarnemingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="146"/>
        <source>Canopy height</source>
        <translation>Kroonhoogte</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="156"/>
        <source>POD overlay opacity</source>
        <translation>Dekking van POD-overlay</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="162"/>
        <source>Download Canopy Tiles</source>
        <translation>Kroontegels downloaden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="169"/>
        <source>Calculate POD</source>
        <translation>POD berekenen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="171"/>
        <source>Compute the terrain-aware probability-of-detection heatmap for this mission (may take several minutes)</source>
        <translation>Bereken de terreinbewuste detectiekans-heatmap voor deze missie (kan enkele minuten duren)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="179"/>
        <source>Click point to select • Drag to pan • Scroll to zoom</source>
        <translation>Klik op punt om te selecteren • Sleep om te verplaatsen • Scrol om te zoomen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="263"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Tegels downloaden is uitgeschakeld in de modus alleen offline</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="265"/>
        <source>Download elevation and canopy-height tiles for this mission&apos;s area</source>
        <translation>Hoogte- en kroonhoogtetegels voor het gebied van deze missie downloaden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="335"/>
        <source>Map View</source>
        <translation>Kaartweergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="372"/>
        <source>⚠ {error}</source>
        <translation>⚠ {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="382"/>
        <source>Map Tile Loading Issue</source>
        <translation>Probleem met laden van kaarttegels</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="384"/>
        <source>{error}

The map will continue to work with cached tiles where available.</source>
        <translation>{error}

De kaart blijft werken met gecachete tegels waar beschikbaar.</translation>
    </message>
</context>
<context>
    <name>GPSMapView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1216"/>
        <source>Copy Data</source>
        <translation>Gegevens kopiëren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1770"/>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1878"/>
        <source>Zoom FOV</source>
        <translation>Zoom-gezichtsveld</translation>
    </message>
</context>
<context>
    <name>GalleryUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="369"/>
        <source>0 AOIs</source>
        <translation>0 AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOI</source>
        <translation>AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOIs</source>
        <translation>AOI&apos;s</translation>
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
        <translation>Interessegebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="432"/>
        <source>Areas of Interest</source>
        <translation>Interessegebieden</translation>
    </message>
</context>
<context>
    <name>GeneralSettingsPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="121"/>
        <source>Select AOI Highlight Color</source>
        <translation>AOI-markeerkleur selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="159"/>
        <source>Benchmark Complete</source>
        <translation>Benchmark voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="161"/>
        <source>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</source>
        <translation>{count} CPU-core(s) gedetecteerd.

Aanbevolen aantal processen: {recommended}

De schuifregelaar is ingesteld op {recommended} processen.</translation>
    </message>
</context>
<context>
    <name>GridReviewController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="151"/>
        <source>Grid review works in single-image mode — exit the gallery first.</source>
        <translation>Rasterbeoordeling werkt in de modus voor één afbeelding; verlaat eerst de galerie.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="273"/>
        <source>This image keeps its existing grid — the new size applies to unstarted images.</source>
        <translation>Deze afbeelding behoudt het bestaande raster; de nieuwe grootte geldt voor afbeeldingen waarvan de beoordeling nog niet is gestart.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="320"/>
        <source>Apply Grid to All Images</source>
        <translation>Raster toepassen op alle afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="322"/>
        <source>{n} image(s) already have review progress recorded at a different grid size.

Reset their progress and apply {rows}×{cols} to them too?

Yes resets them; No keeps them at their current size.</source>
        <translation>{n} afbeelding(en) hebben al beoordelingsvoortgang met een andere rastergrootte.

Hun voortgang resetten en {rows}×{cols} ook op deze afbeeldingen toepassen?

Ja reset ze; Nee houdt ze op hun huidige grootte.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="391"/>
        <source>Image fully reviewed — advancing</source>
        <translation>Afbeelding volledig beoordeeld; doorgaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="628"/>
        <source>cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed</source>
        <translation>cel {cell}/{cells} — afbeelding {image}/{images} — reeks {percent}% beoordeeld</translation>
    </message>
</context>
<context>
    <name>GridReviewDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="52"/>
        <source>Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)</source>
        <translation>Voorstel: {rows}×{cols} (persoon ≈ {px} px op scherm bij celzoom)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="55"/>
        <source>Suggested: {rows}×{cols}</source>
        <translation>Voorstel: {rows}×{cols}</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="14"/>
        <source>Grid Review Settings</source>
        <translation>Instellingen voor rasterbeoordeling</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="23"/>
        <source>Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.</source>
        <translation>Kies in hoeveel cellen het beoordelingsraster elke afbeelding verdeelt. Kleinere cellen betekenen meer zoom per cel.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="32"/>
        <source>Rows</source>
        <translation>Rijen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="52"/>
        <source>Columns</source>
        <translation>Kolommen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="74"/>
        <source>Mark cells reviewed when advancing (Space)</source>
        <translation>Cellen als beoordeeld markeren bij doorgaan (Spatie)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="84"/>
        <source>Draw a 3×3 guide inside the active cell to focus your scan. Visual only — it does not change what gets reviewed.</source>
        <translation>Tekent een 3×3-hulplijn in de actieve cel om uw scan te focussen. Alleen visueel; dit verandert niet wat wordt beoordeeld.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="87"/>
        <source>Show 3×3 focus guide inside each cell</source>
        <translation>3×3-scanhulp binnen elke cel tonen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="97"/>
        <source>Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.</source>
        <translation>Pas de gekozen rijen en kolommen toe op elke afbeelding in deze dataset, niet alleen op de huidige. Afbeeldingen waarvan u de beoordeling al bent gestart, behouden hun voortgang tenzij u een reset bevestigt.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="100"/>
        <source>Apply this grid size to all images</source>
        <translation>Deze rastergrootte toepassen op alle afbeeldingen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="112"/>
        <source>No grid suggestion available (image GSD unknown).</source>
        <translation>Geen rastervoorstel beschikbaar (GSD van afbeelding onbekend).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="119"/>
        <source>Use Suggestion</source>
        <translation>Voorstel gebruiken</translation>
    </message>
</context>
<context>
    <name>HSVColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
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
        <translation>Selecteer een doelkleur in een afbeelding om te detecteren.
Opent een kleurkiezer waarmee u kunt:
• Een afbeelding laden uit de invoermap
• Op pixels klikken om kleuren te bemonsteren
• HSV-waarden automatisch berekenen
• Tint-, verzadigings- en waardebereiken instellen
De geselecteerde kleur wordt het midden van uw HSV-detectiebereik.
Pas de +/- bereikwaarden aan om kleurvariaties vast te leggen.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="37"/>
        <source> Pick Color</source>
        <translation> Kleur kiezen</translation>
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
        <translation>Visuele voorvertoning van de momenteel geselecteerde doelkleur.
Toont de middenkleur van uw HSV-detectiebereik.
De werkelijke detectie zal overeenkomen met kleuren binnen de opgegeven +/- bereiken rond deze kleur.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="92"/>
        <source>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</source>
        <translation>Tolerantie van het tintbereik voor kleurdetectie.
De tint vertegenwoordigt de werkelijke kleur (rood, groen, blauw, enz.) op een schaal van 0-179.
Pas de -/+ waarden aan om variatie in de kleurtint toe te staan.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="97"/>
        <source>Hue Range</source>
        <translation>Tintbereik</translation>
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
        <translation>Onderste tolerantie van het tintbereik.
• Bereik: 0 tot 179
• Standaard: 20
Wordt afgetrokken van de doeltintwaarde om de ondergrens te bepalen.
Lagere waarden = strengere kleurovereenkomst, hogere waarden = meer kleurvariatie geaccepteerd.
Voorbeeld: doeltint 100, minus 20 = detecteert tinten van 80-100.</translation>
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
        <translation>Bovenste tolerantie van het tintbereik.
• Bereik: 0 tot 179
• Standaard: 20
Wordt opgeteld bij de doeltintwaarde om de bovengrens te bepalen.
Lagere waarden = strengere kleurovereenkomst, hogere waarden = meer kleurvariatie geaccepteerd.
Voorbeeld: doeltint 100, plus 20 = detecteert tinten van 100-120.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="198"/>
        <source>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</source>
        <translation>Tolerantie van het verzadigingsbereik voor kleurdetectie.
Verzadiging vertegenwoordigt de kleurintensiteit (0=grijs, 255=volledig verzadigd) op een schaal van 0-255.
Pas de -/+ waarden aan om variatie in kleurintensiteit toe te staan.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="203"/>
        <source>Saturation Range</source>
        <translation>Verzadigingsbereik</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="227"/>
        <source>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</source>
        <translation>Onderste tolerantie van het verzadigingsbereik.
• Bereik: 0 tot 255
• Standaard: 50
Wordt afgetrokken van de doelverzadigingswaarde om de ondergrens te bepalen.
Lagere waarden = vereist levendige kleuren, hogere waarden = accepteert vervaagde/uitgewassen kleuren.
Voorbeeld: doelverzadiging 150, minus 50 = detecteert verzadigingen van 100-150.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="262"/>
        <source>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</source>
        <translation>Bovenste tolerantie van het verzadigingsbereik.
• Bereik: 0 tot 255
• Standaard: 50
Wordt opgeteld bij de doelverzadigingswaarde om de bovengrens te bepalen.
Lagere waarden = vereist exacte verzadiging, hogere waarden = accepteert meer verzadigde kleuren.
Voorbeeld: doelverzadiging 150, plus 50 = detecteert verzadigingen van 150-200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="298"/>
        <source>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</source>
        <translation>Tolerantie van het waardebereik (helderheid) voor kleurdetectie.
De waarde vertegenwoordigt de helderheid (0=zwart, 255=helder) op een schaal van 0-255.
Pas de -/+ waarden aan om variatie in helderheid toe te staan.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="303"/>
        <source>Value Range</source>
        <translation>Waardebereik</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="327"/>
        <source>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</source>
        <translation>Onderste tolerantie van het waardebereik (helderheid).
• Bereik: 0 tot 255
• Standaard: 50
Wordt afgetrokken van de doelhelderheidswaarde om de ondergrens te bepalen.
Lagere waarden = vereist heldere pixels, hogere waarden = accepteert donkerdere pixels.
Voorbeeld: doelwaarde 200, minus 50 = detecteert helderheid van 150-200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="362"/>
        <source>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</source>
        <translation>Bovenste tolerantie van het waardebereik (helderheid).
• Bereik: 0 tot 255
• Standaard: 50
Wordt opgeteld bij de doelhelderheidswaarde om de bovengrens te bepalen.
Lagere waarden = vereist exacte helderheid, hogere waarden = accepteert helderdere pixels.
Voorbeeld: doelwaarde 200, plus 50 = detecteert helderheid van 200-250.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="410"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation>Opent het Bereikweergavevenster om:
- Het bereik van kleuren te zien dat tijdens de beeldanalyse wordt gezocht.
Gebruik dit om te zien welke kleuren worden gedetecteerd en om de kleurbereiken te optimaliseren vóór de verwerking.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="415"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
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
        <translation>HSV-kleurbereikassistent - Klikselectie</translation>
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
        <translation>Interactieve afbeeldingsviewer met kleurselectie.

NAVIGATIE:
• Muiswiel: in/uitzoomen
• Linkermuisknop slepen: pannen door afbeelding
• Dubbelklik: afbeelding aan venster aanpassen

KLEURSELECTIE:
• CTRL + linkermuisknop ingedrukt houden: vergelijkbare kleuren selecteren
• CTRL+SHIFT + linkermuisknop ingedrukt houden: selectie verwijderen/wissen
• [ ]-toetsen: selectiestraal aanpassen
• CTRL+Z: laatste selectie ongedaan maken
• CTRL+SHIFT+Z: opnieuw uitvoeren

WEERGAVE:
• Witte overlay = geselecteerde pixels
• Gele tekst = HSV-waarden op cursorpositie
• Cirkelvormige cursor verschijnt wanneer CTRL ingedrukt is</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="741"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="743"/>
        <source>Browse for an image file to load.
Opens a file dialog to select an image from your computer.
• Supported formats: PNG, JPG, JPEG, BMP
• Load an image to start selecting colors
The image will be displayed in the main viewer on the left.</source>
        <translation>Bladeren naar een te laden afbeeldingsbestand.
Opent een bestandsdialoog om een afbeelding van uw computer te selecteren.
• Ondersteunde formaten: PNG, JPG, JPEG, BMP
• Laad een afbeelding om kleuren te selecteren
De afbeelding wordt weergegeven in de hoofdviewer aan de linkerkant.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="753"/>
        <source>Reset</source>
        <translation>Resetten</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="755"/>
        <source>Reset all selections and start over.
• Clears all selected pixels (white overlay)
• Resets HSV ranges to defaults
• Clears the mask preview
• Undoable with CTRL+Z
Use this to start fresh without reloading the image.</source>
        <translation>Reset alle selecties en begin opnieuw.
• Wist alle geselecteerde pixels (witte overlay)
• Reset HSV-bereiken naar standaardinstellingen
• Wist de maskervoorvertoning
• Ongedaan te maken met CTRL+Z
Gebruik dit om opnieuw te beginnen zonder de afbeelding opnieuw te laden.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="766"/>
        <source>Selection Radius:</source>
        <translation>Selectiestraal:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="768"/>
        <source>Size of the circular selection cursor.
Determines how many pixels are sampled when you CTRL+Click.</source>
        <translation>Grootte van de cirkelvormige selectiecursor.
Bepaalt hoeveel pixels worden bemonsterd wanneer u CTRL+klikt.</translation>
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
        <translation>Stel de straal van de selectiecursor in pixels in.
• Bereik: 1-50 pixels
• Standaard: 1 pixel (selectie van enkele pixel)
Grotere straal:
• Bemonstert meer pixels bij klikken
• Middelt kleuren binnen de cirkel
• Goed voor het selecteren van gradiënten of getextureerde gebieden
Kleinere straal:
• Nauwkeurigere selectie
• Beter voor effen kleuren
Sneltoetsen: [ verlaag, ] verhoog met 2 pixels</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="793"/>
        <source>Color Tolerance:</source>
        <translation>Kleurtolerantie:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="795"/>
        <source>HSV color matching tolerance.
Controls how similar colors must be to get selected.</source>
        <translation>HSV-kleurovereenkomst-tolerantie.
Bepaalt hoe vergelijkbaar kleuren moeten zijn om geselecteerd te worden.</translation>
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
        <translation>Stel kleurtolerantie in voor detectie van vergelijkbare pixels.
• Bereik: 0-50
• Standaard: 2
Wanneer u CTRL+klikt, worden pixels geselecteerd als hun HSV-waarden binnen deze tolerantie liggen:
• 0: alleen exacte overeenkomst (zeer streng)
• 2-5: kleine variaties (aanbevolen voor de meeste gevallen)
• 10+: grote variaties (kan te veel kleuren selecteren)
Hogere tolerantie:
• Selecteert meer vergelijkbare kleuren
• Goed voor afbeeldingen met lichtvariatie
• Kan ongewenste kleuren bevatten
Lagere tolerantie:
• Nauwkeurigere kleurovereenkomst
• Kan sommige pixels van de doelkleur missen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="825"/>
        <source>CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius</source>
        <translation>CTRL+klik: vergelijkbare kleuren selecteren | CTRL+SHIFT+klik: verwijderen | [ ] : straal</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="831"/>
        <source>Help</source>
        <translation>Hulp</translation>
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
        <translation>Toon gedetailleerde hulp en instructies.
Opent een dialoogvenster met:
• Stapsgewijze gebruiksinstructies
• Uitleg van navigatieknoppen
• Kleurselectietechnieken
• Referentie van sneltoetsen
Klik hier als u niet zeker weet hoe u dit hulpmiddel moet gebruiken.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="859"/>
        <source>Selected Color</source>
        <translation>Geselecteerde kleur</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="861"/>
        <source>Average color of all selected pixels.
Shows the center/mean color that will be used for HSV range detection.</source>
        <translation>Gemiddelde kleur van alle geselecteerde pixels.
Toont de midden-/gemiddelde kleur die wordt gebruikt voor HSV-bereikdetectie.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="866"/>
        <source>Color:</source>
        <translation>Kleur:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="868"/>
        <source>Visual preview of the average selected color.
This is the center color calculated from all selected pixels.</source>
        <translation>Visuele voorvertoning van de gemiddeld geselecteerde kleur.
Dit is de middenkleur berekend uit alle geselecteerde pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="876"/>
        <source>Color swatch showing the average of all selected pixels.
This becomes the center color for HSV range detection.</source>
        <translation>Kleurstaal met het gemiddelde van alle geselecteerde pixels.
Dit wordt de middenkleur voor HSV-bereikdetectie.</translation>
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
        <translation>Hexadecimale weergave van de geselecteerde kleur.
Formaat: #RRGGBB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="889"/>
        <source>Hex color code of the average selected color.
Can be used to identify the exact RGB color value.</source>
        <translation>Hex-kleurcode van de gemiddeld geselecteerde kleur.
Kan worden gebruikt om de exacte RGB-kleurwaarde te identificeren.</translation>
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
        <translation>HSV-waarden van de geselecteerde kleur.
H = tint (0-360°), S = verzadiging (0-100%), V = waarde (0-100%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="902"/>
        <source>HSV color values of the average selected color.
This is the center point of your color range.</source>
        <translation>HSV-kleurwaarden van de gemiddeld geselecteerde kleur.
Dit is het middenpunt van uw kleurbereik.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="910"/>
        <source>HSV Ranges</source>
        <translation>HSV-bereiken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="912"/>
        <source>HSV color range configuration.
Defines the detection range for each HSV channel.
Center values are calculated from selected pixels.
Buffer values add extra tolerance to catch color variations.</source>
        <translation>HSV-kleurbereikconfiguratie.
Definieert het detectiebereik voor elk HSV-kanaal.
Middenwaarden worden berekend uit geselecteerde pixels.
Bufferwaarden voegen extra tolerantie toe om kleurvariaties te vangen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="920"/>
        <source>Channel</source>
        <translation>Kanaal</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="921"/>
        <source>HSV color channel (Hue, Saturation, Value)</source>
        <translation>HSV-kleurkanaal (tint, verzadiging, waarde)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="924"/>
        <source>Center</source>
        <translation>Midden</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="925"/>
        <source>Average value of selected pixels for this channel</source>
        <translation>Gemiddelde waarde van geselecteerde pixels voor dit kanaal</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="928"/>
        <source>- Buffer</source>
        <translation>- Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="929"/>
        <source>Extra tolerance below center value (lower bound buffer)</source>
        <translation>Extra tolerantie onder middenwaarde (ondergrens-buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="932"/>
        <source>+ Buffer</source>
        <translation>+ Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="933"/>
        <source>Extra tolerance above center value (upper bound buffer)</source>
        <translation>Extra tolerantie boven middenwaarde (bovengrens-buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="936"/>
        <source>Final Range</source>
        <translation>Eindbereik</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="937"/>
        <source>Complete detection range (min-max) after applying buffers</source>
        <translation>Volledig detectiebereik (min-max) na toepassing van buffers</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="941"/>
        <source>Hue:</source>
        <translation>Tint:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="942"/>
        <source>Hue channel (color type): 0-360 degrees on color wheel</source>
        <translation>Tintkanaal (kleurtype): 0-360 graden op kleurwiel</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="947"/>
        <source>Center hue value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-360° (red=0°, green=120°, blue=240°)</source>
        <translation>Midden-tintwaarde (gemiddelde van geselecteerde pixels).
Automatisch berekend uit uw selectie.
Bereik: 0-360° (rood=0°, groen=120°, blauw=240°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="957"/>
        <source>Hue lower bound buffer (subtract from center).
• Range: 0-360°
• Adds tolerance below the center hue
• Larger values detect more hues in the minus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Tint-ondergrens-buffer (aftrekken van midden).
• Bereik: 0-360°
• Voegt tolerantie toe onder de midden-tint
• Grotere waarden detecteren meer tinten in de min-richting
• Houd smal om ongewenste kleuren niet te detecteren
WAARSCHUWING: totaal tintbereik (min + plus) &gt; 60° kan valse positieven veroorzaken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="971"/>
        <source>Hue upper bound buffer (add to center).
• Range: 0-360°
• Adds tolerance above the center hue
• Larger values detect more hues in the plus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Tint-bovengrens-buffer (optellen bij midden).
• Bereik: 0-360°
• Voegt tolerantie toe boven de midden-tint
• Grotere waarden detecteren meer tinten in de plus-richting
• Houd smal om ongewenste kleuren niet te detecteren
WAARSCHUWING: totaal tintbereik (min + plus) &gt; 60° kan valse positieven veroorzaken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="983"/>
        <source>Final hue detection range.
Shows the complete min-max hue range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Eind-tintdetectiebereik.
Toont het volledige min-max tintbereik dat zal worden gedetecteerd.
Berekend als: (midden - min-buffer) tot (midden + plus-buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="990"/>
        <source>WARNING: Too wide of a Hue range can result in false positives!</source>
        <translation>WAARSCHUWING: een te breed tintbereik kan leiden tot valse positieven!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="994"/>
        <source>Hue range warning.
Your total hue range exceeds 60°.
Wide hue ranges may detect many different colors.
Consider narrowing the buffers for more accurate detection.</source>
        <translation>Waarschuwing tintbereik.
Uw totale tintbereik overschrijdt 60°.
Brede tintbereiken kunnen veel verschillende kleuren detecteren.
Overweeg de buffers te versmallen voor nauwkeurigere detectie.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1002"/>
        <source>Sat:</source>
        <translation>Verz:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1003"/>
        <source>Saturation channel (color intensity): 0-100%</source>
        <translation>Verzadigingskanaal (kleurintensiteit): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1008"/>
        <source>Center saturation value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=gray, 100%=vivid color)</source>
        <translation>Midden-verzadigingswaarde (gemiddelde van geselecteerde pixels).
Automatisch berekend uit uw selectie.
Bereik: 0-100% (0%=grijs, 100%=levendige kleur)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1018"/>
        <source>Saturation lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center saturation
• Larger values detect more desaturated/grayish colors
• Be careful: very low saturation includes gray colors
WARNING: Lower bound &lt; 25% may include unwanted gray/desaturated colors</source>
        <translation>Verzadiging-ondergrens-buffer (aftrekken van midden).
• Bereik: 0-100%
• Voegt tolerantie toe onder de midden-verzadiging
• Grotere waarden detecteren meer ontzadigde/grijsachtige kleuren
• Wees voorzichtig: zeer lage verzadiging omvat grijze kleuren
WAARSCHUWING: ondergrens &lt; 25% kan ongewenste grijze/ontzadigde kleuren bevatten</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1032"/>
        <source>Saturation upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center saturation
• Larger values detect more saturated/vivid colors
• Higher saturation generally safe to increase</source>
        <translation>Verzadiging-bovengrens-buffer (optellen bij midden).
• Bereik: 0-100%
• Voegt tolerantie toe boven de midden-verzadiging
• Grotere waarden detecteren meer verzadigde/levendige kleuren
• Hogere verzadiging is over het algemeen veilig om te verhogen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1043"/>
        <source>Final saturation detection range.
Shows the complete min-max saturation range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Eind-verzadigingsdetectiebereik.
Toont het volledige min-max verzadigingsbereik dat zal worden gedetecteerd.
Berekend als: (midden - min-buffer) tot (midden + plus-buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1050"/>
        <source>WARNING: Too low of a Saturation level can result in false positives!</source>
        <translation>WAARSCHUWING: een te laag verzadigingsniveau kan leiden tot valse positieven!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1054"/>
        <source>Saturation range warning.
Your lower saturation bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unwanted gray or desaturated objects.</source>
        <translation>Waarschuwing verzadigingsbereik.
Uw ondergrens van de verzadiging ligt onder 25%.
Lage verzadiging omvat grijsachtige/uitgewassen kleuren.
Kan ongewenste grijze of ontzadigde objecten detecteren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1062"/>
        <source>Val:</source>
        <translation>Waarde:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1063"/>
        <source>Value channel (brightness): 0-100%</source>
        <translation>Waardekanaal (helderheid): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1068"/>
        <source>Center value/brightness (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=black, 100%=bright)</source>
        <translation>Midden-waarde/helderheid (gemiddelde van geselecteerde pixels).
Automatisch berekend uit uw selectie.
Bereik: 0-100% (0%=zwart, 100%=helder)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1078"/>
        <source>Value lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center brightness
• Larger values detect darker versions of the color
• Be careful: very low value includes very dark/black colors
WARNING: Lower bound &lt; 25% may include unwanted shadows or dark objects</source>
        <translation>Waarde-ondergrens-buffer (aftrekken van midden).
• Bereik: 0-100%
• Voegt tolerantie toe onder de midden-helderheid
• Grotere waarden detecteren donkerdere versies van de kleur
• Wees voorzichtig: zeer lage waarde omvat zeer donkere/zwarte kleuren
WAARSCHUWING: ondergrens &lt; 25% kan ongewenste schaduwen of donkere objecten bevatten</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1092"/>
        <source>Value upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center brightness
• Larger values detect brighter versions of the color
• Higher brightness generally safe to increase</source>
        <translation>Waarde-bovengrens-buffer (optellen bij midden).
• Bereik: 0-100%
• Voegt tolerantie toe boven de midden-helderheid
• Grotere waarden detecteren helderere versies van de kleur
• Hogere helderheid is over het algemeen veilig om te verhogen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1103"/>
        <source>Final value/brightness detection range.
Shows the complete min-max brightness range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Eind-waarde/helderheidsdetectiebereik.
Toont het volledige min-max helderheidsbereik dat zal worden gedetecteerd.
Berekend als: (midden - min-buffer) tot (midden + plus-buffer)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1110"/>
        <source>WARNING: Too low of a Value level can result in false positives!</source>
        <translation>WAARSCHUWING: een te laag waardeniveau kan leiden tot valse positieven!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1114"/>
        <source>Value range warning.
Your lower value bound is below 25%.
Low value includes very dark colors.
May detect unwanted shadows or dark objects.</source>
        <translation>Waarschuwing waardebereik.
Uw ondergrens van de waarde ligt onder 25%.
Lage waarde omvat zeer donkere kleuren.
Kan ongewenste schaduwen of donkere objecten detecteren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1124"/>
        <source>Statistics</source>
        <translation>Statistieken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1126"/>
        <source>Statistics about your current selection.
Shows how many pixels are selected and what percentage of the image they represent.</source>
        <translation>Statistieken over uw huidige selectie.
Toont hoeveel pixels zijn geselecteerd en welk percentage van de afbeelding ze vertegenwoordigen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1130"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1225"/>
        <source>Selected Pixels: 0</source>
        <translation>Geselecteerde pixels: 0</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1132"/>
        <source>Number of pixels currently selected.
Shows the total count of white-highlighted pixels in the main viewer.
Updates in real-time as you select colors.</source>
        <translation>Aantal momenteel geselecteerde pixels.
Toont het totale aantal wit-gemarkeerde pixels in de hoofdviewer.
Wordt in realtime bijgewerkt terwijl u kleuren selecteert.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1137"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1226"/>
        <source>Coverage: 0%</source>
        <translation>Dekking: 0%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1139"/>
        <source>Percentage of image covered by selection.
Shows what portion of the total image is selected.
• Low %: Precise selection, may miss some target pixels
• High %: Broad selection, may include unwanted areas</source>
        <translation>Percentage afbeelding gedekt door selectie.
Toont welk deel van de totale afbeelding is geselecteerd.
• Laag %: nauwkeurige selectie, kan sommige doelpixels missen
• Hoog %: brede selectie, kan ongewenste gebieden bevatten</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1148"/>
        <source>Mask Preview</source>
        <translation>Maskervoorbeeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1150"/>
        <source>Black and white preview of the detection mask.
Shows what pixels will be detected with current HSV ranges and buffers.</source>
        <translation>Zwart-witvoorvertoning van het detectiemasker.
Toont welke pixels worden gedetecteerd met de huidige HSV-bereiken en buffers.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1161"/>
        <source>Grayscale mask preview.
• White pixels: Will be detected with current settings
• Black pixels: Will NOT be detected
Updates automatically when you adjust buffers.
Use this to verify your HSV range captures the target without false positives.</source>
        <translation>Grijswaarden-maskervoorvertoning.
• Witte pixels: worden gedetecteerd met huidige instellingen
• Zwarte pixels: worden NIET gedetecteerd
Wordt automatisch bijgewerkt wanneer u buffers aanpast.
Gebruik dit om te verifiëren dat uw HSV-bereik het doel vastlegt zonder valse positieven.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1179"/>
        <source>Select Image</source>
        <translation>Afbeelding selecteren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1180"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp)</source>
        <translation>Afbeeldingen (*.png *.jpg *.jpeg *.bmp)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1237"/>
        <source>Selected Pixels: {0:,}</source>
        <translation>Geselecteerde pixels: {0:,}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1238"/>
        <source>Coverage: {0:.1f}%</source>
        <translation>Dekking: {0:.1f}%</translation>
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
&lt;h2&gt;HSV-kleurbereikassistent - Hulp&lt;/h2&gt;

&lt;p&gt;Met dit hulpmiddel kunt u het HSV-kleurbereik van een specifieke kleur in een foto kiezen.
Klik op de knop BLADEREN om een afbeelding te openen.&lt;/p&gt;

&lt;h3&gt;Navigatie:&lt;/h3&gt;
&lt;p&gt;• Gebruik het muiswiel om in/uit te zoomen op de afbeelding&lt;br&gt;
• Gebruik de linkermuisknop om de afbeelding te slepen en te pannen&lt;/p&gt;

&lt;h3&gt;Kleurselectie:&lt;/h3&gt;
&lt;p&gt;• Houd de &lt;b&gt;CTRL-/OPTION-toets&lt;/b&gt; ingedrukt terwijl u met de linkermuisknop op een kleur in de afbeelding klikt die u wilt selecteren&lt;br&gt;
• Alle pixels in de afbeelding die die HSV-kleurwaarde delen, worden geselecteerd en in het wit gemarkeerd&lt;/p&gt;

&lt;h3&gt;Selectiestraal:&lt;/h3&gt;
        &lt;p&gt;U kunt de selectiestraal van de muisaanwijzer groter of kleiner maken.
        Wanneer u CTRL+klikt, worden alle kleuren binnen die straal van de muisaanwijzer geselecteerd.&lt;/p&gt;

&lt;h3&gt;Correcties:&lt;/h3&gt;
&lt;p&gt;Als u een fout maakt, kunt u de laatste selectie ONGEDAAN MAKEN of op de knop RESETTEN drukken om opnieuw te beginnen.&lt;/p&gt;

&lt;h3&gt;Maskervoorbeeld:&lt;/h3&gt;
        &lt;p&gt;Aan de rechterkant toont de sectie Maskervoorbeeld u welke pixels in de afbeelding zijn geselecteerd.
        Als u pixels ziet buiten uw doelobject die u selecteert, betekent dit mogelijk dat u
        de kleurtolerantie moet aanpassen of voorzichtiger moet zijn met uw selecties.&lt;/p&gt;
</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1504"/>
        <source>HSV Color Range Assistant - Help</source>
        <translation>HSV-kleurbereikassistent - Hulp</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="97"/>
        <source>No Colors Selected</source>
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="120"/>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="125"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="176"/>
        <source>Hue Expansion</source>
        <translation>Tintuitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="178"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid via buren waarvan de tint binnen +/- {0}
(OpenCV-eenheden) van de gemiddelde tint van de oorspronkelijk gedetecteerde pixels valt.
Pixels met verzadiging onder {1}% of waarde onder {2}% worden uitgesloten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="468"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="53"/>
        <source>No Colors Selected</source>
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="63"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="99"/>
        <source>Hue Expansion</source>
        <translation>Tintuitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="101"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid via buren waarvan de tint binnen +/- {0}
(OpenCV-eenheden) van de gemiddelde tint van de oorspronkelijk gedetecteerde pixels valt.
Pixels met verzadiging onder {1}% of waarde onder {2}% worden uitgesloten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="408"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
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
        <translation>Overeenkomst
tolerantie:</translation>
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
        <translation>Invoer van hexadecimale kleurcode.
Voer kleuren in als hex-codes (bijv. #FF0000 voor rood).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="102"/>
        <source>Enter a hexadecimal color code.
• Format: #RRGGBB (e.g., #FF0000 for red, #00FF00 for green)
• Also accepts short format: #RGB (e.g., #F00 for red)
Type or paste a hex code to quickly set a specific color.
The color will be converted to HSV automatically.</source>
        <translation>Voer een hexadecimale kleurcode in.
• Formaat: #RRGGBB (bijv. #FF0000 voor rood, #00FF00 voor groen)
• Accepteert ook kort formaat: #RGB (bijv. #F00 voor rood)
Typ of plak een hex-code om snel een specifieke kleur in te stellen.
De kleur wordt automatisch geconverteerd naar HSV.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="111"/>
        <source>Reset to Default</source>
        <translation>Terugzetten naar standaard</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="114"/>
        <source>Reset to default color and ranges.
• Color: Pure red (H:0°, S:100%, V:100%)
• Hue range: ±20° (total 40° range)
• Saturation range: ±20%
• Value range: ±20%
Use this to start over with standard settings.</source>
        <translation>Terugzetten naar standaard kleur en bereiken.
• Kleur: zuiver rood (H:0°, S:100%, V:100%)
• Tintbereik: ±20° (totaal 40° bereik)
• Verzadigingsbereik: ±20%
• Waardebereik: ±20%
Gebruik dit om opnieuw te beginnen met standaardinstellingen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="137"/>
        <source>Saturation / Value</source>
        <translation>Verzadiging / waarde</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="141"/>
        <source>Saturation and Value (brightness) selector.
Saturation controls color intensity (left=gray, right=vivid).
Value controls brightness (bottom=dark, top=bright).</source>
        <translation>Verzadiging- en waarde- (helderheid)-selector.
Verzadiging bepaalt de kleurintensiteit (links=grijs, rechts=levendig).
Waarde bepaalt de helderheid (onder=donker, boven=helder).</translation>
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
        <translation>Interactieve verzadiging/waarde-selector.
• Klik ergens om de verzadiging en helderheid van de middenkleur in te stellen
• Witte cirkel = huidige positie van middenkleur
• Witte rechthoek = detectiebereik (aanpasbaar)
• Sleep witte hoekhandvatten om verzadigings-/waardebereiken aan te passen
• Horizontaal bereik = verzadigingstolerantie
• Verticaal bereik = waarde/helderheidstolerantie
Grotere bereiken detecteren meer kleurvariaties, maar kunnen ongewenste kleuren bevatten.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="165"/>
        <source>Hue</source>
        <translation>Tint</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="169"/>
        <source>Hue (color type) selector.
Hue represents the actual color: red, orange, yellow, green, cyan, blue, purple, magenta.</source>
        <translation>Tint (kleurtype)-selector.
Tint vertegenwoordigt de werkelijke kleur: rood, oranje, geel, groen, cyaan, blauw, paars, magenta.</translation>
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
        <translation>Interactieve tint-kleurring-selector.
• Klik op de ring om een tint (kleurtype) te selecteren
• Witte lijn = huidige midden-tint
• Grijze bogen en lijnen = tintdetectiebereik (aanpasbaar)
• Sleep witte cirkelhandvatten om het tintbereik aan te passen
• Linker handvat = ondergrens (min-bereik)
• Rechter handvat = bovengrens (plus-bereik)
Waarschuwing: tintbereiken breder dan 60° kunnen te veel kleuren detecteren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="205"/>
        <source>Use Image</source>
        <translation>Afbeelding gebruiken</translation>
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
        <translation>Open HSV-kleurbereikassistent.
Geavanceerd hulpmiddel voor het selecteren van kleuren uit een afbeelding:
• Laad een afbeelding uit uw invoermap
• Klik op pixels om kleuren te bemonsteren
• Berekent automatisch optimale HSV-bereiken
• Zie realtime voorvertoning van detectieresultaten
Aanbevolen voor het vinden van het beste kleurbereik voor uw doel.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="219"/>
        <source>Pick Screen Color</source>
        <translation>Schermkleur kiezen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="222"/>
        <source>Pick a color from anywhere on your screen.
Opens a color picker that lets you:
• Click anywhere on your screen to sample a color
• Sample from other applications or images
The picked color will be set as the center color.
Ranges remain unchanged - adjust manually after picking.</source>
        <translation>Kies een kleur ergens op uw scherm.
Opent een kleurkiezer waarmee u kunt:
• Ergens op uw scherm klikken om een kleur te bemonsteren
• Bemonsteren van andere applicaties of afbeeldingen
De gekozen kleur wordt ingesteld als middenkleur.
Bereiken blijven ongewijzigd - pas handmatig aan na het kiezen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="232"/>
        <source>Add to Custom Colors</source>
        <translation>Toevoegen aan aangepaste kleuren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="235"/>
        <source>Save current color to Custom Colors palette.
Adds the current center color to the first empty slot in Custom Colors.
• Only saves the color, not the ranges
• Click saved colors to quickly reuse them
• Custom colors persist across sessions
Useful for building a palette of frequently used colors.</source>
        <translation>Sla huidige kleur op in palet Aangepaste kleuren.
Voegt de huidige middenkleur toe aan het eerste lege slot in Aangepaste kleuren.
• Slaat alleen de kleur op, niet de bereiken
• Klik op opgeslagen kleuren om ze snel opnieuw te gebruiken
• Aangepaste kleuren blijven behouden tussen sessies
Nuttig voor het opbouwen van een palet van veelgebruikte kleuren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="253"/>
        <source>Basic Colors:</source>
        <translation>Basiskleuren:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="256"/>
        <source>Preset basic color palette.
Quick access to common colors like red, orange, yellow, green, cyan, blue, purple, and grayscale.
Click any color swatch to set it as the center color.</source>
        <translation>Vooraf ingesteld basis-kleurenpalet.
Snelle toegang tot veelvoorkomende kleuren zoals rood, oranje, geel, groen, cyaan, blauw, paars en grijswaarden.
Klik op een kleurstaal om deze als middenkleur in te stellen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="264"/>
        <source>Basic color swatches.
Click any color to quickly set it as your center color.
• Top row: Primary colors and tints
• Bottom row: Grayscale and darker shades
Useful for quickly selecting standard colors.</source>
        <translation>Basis-kleurstalen.
Klik op een kleur om deze snel als uw middenkleur in te stellen.
• Bovenste rij: primaire kleuren en tinten
• Onderste rij: grijswaarden en donkere tinten
Nuttig voor het snel selecteren van standaardkleuren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="274"/>
        <source>Custom Colors:</source>
        <translation>Aangepaste kleuren:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="277"/>
        <source>Your saved custom color palette.
Colors you&apos;ve saved using &apos;Add to Custom Colors&apos; button.
Click any saved color to reuse it.</source>
        <translation>Uw opgeslagen aangepaste kleurenpalet.
Kleuren die u hebt opgeslagen met de knop &apos;Toevoegen aan aangepaste kleuren&apos;.
Klik op een opgeslagen kleur om deze opnieuw te gebruiken.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="285"/>
        <source>Custom color swatches.
Click any color to set it as your center color.
• Empty slots shown as gray
• Use &apos;Add to Custom Colors&apos; button to save current color
• Custom colors persist across sessions
Build your own palette of frequently used colors.</source>
        <translation>Aangepaste kleurstalen.
Klik op een kleur om deze als uw middenkleur in te stellen.
• Lege slots worden grijs weergegeven
• Gebruik de knop &apos;Toevoegen aan aangepaste kleuren&apos; om de huidige kleur op te slaan
• Aangepaste kleuren blijven behouden tussen sessies
Bouw uw eigen palet van veelgebruikte kleuren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="461"/>
        <source>Current HSV color range summary.
Shows the center color and detection ranges in real-time.
Warning indicators appear when ranges may cause detection issues.</source>
        <translation>Samenvatting van het huidige HSV-kleurbereik.
Toont de middenkleur en detectiebereiken in realtime.
Waarschuwingen verschijnen wanneer bereiken detectieproblemen kunnen veroorzaken.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Center HSV:</source>
        <translation>Midden-HSV:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Hue Range:</source>
        <translation>Tintbereik:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Sat Range:</source>
        <translation>Verz.-bereik:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Val Range:</source>
        <translation>Waardebereik:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="472"/>
        <source>Current center HSV color values.
H = Hue (0-360°), S = Saturation (0-100%), V = Value/brightness (0-100%).</source>
        <translation>Huidige midden-HSV-kleurwaarden.
H = tint (0-360°), S = verzadiging (0-100%), V = waarde/helderheid (0-100%).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="473"/>
        <source>Hue detection range (minus/plus from center).
Total range = minus + plus. Warning shown if total &gt; 60°.</source>
        <translation>Tintdetectiebereik (min/plus vanaf midden).
Totaal bereik = min + plus. Waarschuwing getoond als totaal &gt; 60°.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="474"/>
        <source>Saturation detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Verzadigingsdetectiebereik (min/plus vanaf midden).
Waarschuwing getoond als ondergrens &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="475"/>
        <source>Value detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Waardedetectiebereik (min/plus vanaf midden).
Waarschuwing getoond als ondergrens &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="497"/>
        <source>⚠ Too wide!</source>
        <translation>⚠ Te breed!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="502"/>
        <source>Hue range warning.
Your hue range is wider than 60° total.
Wide hue ranges may detect too many different colors.
Consider narrowing the range for more accurate detection.</source>
        <translation>Waarschuwing tintbereik.
Uw tintbereik is breder dan in totaal 60°.
Brede tintbereiken kunnen te veel verschillende kleuren detecteren.
Overweeg het bereik te versmallen voor nauwkeurigere detectie.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="510"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="523"/>
        <source>⚠ Too low!</source>
        <translation>⚠ Te laag!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="515"/>
        <source>Saturation range warning.
Your saturation lower bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unintended gray or desaturated colors.</source>
        <translation>Waarschuwing verzadigingsbereik.
Uw ondergrens van de verzadiging ligt onder 25%.
Lage verzadiging omvat grijsachtige/uitgewassen kleuren.
Kan onbedoelde grijze of ontzadigde kleuren detecteren.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="528"/>
        <source>Value range warning.
Your value lower bound is below 25%.
Low value includes very dark colors.
May detect shadows or dark unintended objects.</source>
        <translation>Waarschuwing waardebereik.
Uw ondergrens van de waarde ligt onder 25%.
Lage waarde omvat zeer donkere kleuren.
Kan schaduwen of donkere onbedoelde objecten detecteren.</translation>
    </message>
</context>
<context>
    <name>HeatmapViewerDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="34"/>
        <source>AOI Detection Heatmap</source>
        <translation>AOI-detectieheatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="59"/>
        <source>Threshold</source>
        <translation>Drempel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="62"/>
        <source>Percentile:</source>
        <translation>Percentiel:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="81"/>
        <source>Grid Resolution</source>
        <translation>Rasterresolutie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="86"/>
        <source>Low (100)</source>
        <translation>Laag (100)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="87"/>
        <source>Medium (200)</source>
        <translation>Gemiddeld (200)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="88"/>
        <source>High (400)</source>
        <translation>Hoog (400)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="114"/>
        <source>Hot zones (colored) show high-density detection areas. Gray zones are below the threshold. Adjust the threshold to control what counts as a hot zone.</source>
        <translation>Hot zones (gekleurd) tonen detectiegebieden met hoge dichtheid. Grijze zones liggen onder de drempel. Pas de drempel aan om te bepalen wat als hot zone telt.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="126"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="150"/>
        <source>No heatmap data available</source>
        <translation>Geen heatmap-gegevens beschikbaar</translation>
    </message>
</context>
<context>
    <name>HelpDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="25"/>
        <source>Viewer Help</source>
        <translation>Hulp bij weergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="60"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
</context>
<context>
    <name>ImageAdjustmentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="83"/>
        <source>Image Adjustment</source>
        <translation>Beeldaanpassing</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="96"/>
        <source>Adjustments</source>
        <translation>Aanpassingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="124"/>
        <source>Exposure:</source>
        <translation>Belichting:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="127"/>
        <source>Highlights:</source>
        <translation>Hooglichten:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="130"/>
        <source>Shadows:</source>
        <translation>Schaduwen:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="133"/>
        <source>Clarity:</source>
        <translation>Detailcontrast:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="136"/>
        <source>Radius:</source>
        <translation>Straal:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="146"/>
        <source>Reset</source>
        <translation>Resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="147"/>
        <source>Apply</source>
        <translation>Toepassen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="148"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
</context>
<context>
    <name>ImageAnalysisGuide</name>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="14"/>
        <source>Image Analysis Guide</source>
        <translation>Beeldanalysegids</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="39"/>
        <source>Welcome to ADIAT</source>
        <translation>Welkom bij ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="67"/>
        <source>Select a results file from a previous analysis: an ADIAT_Data.xml result, or a batch&apos;s Search Coordinator project (ADIAT_Search_*.xml).</source>
        <translation>Selecteer een resultatenbestand van een eerdere analyse: een ADIAT_Data.xml-resultaat of een project voor batchcontrole van de Zoekcoördinator (ADIAT_Search_*.xml).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="79"/>
        <source>No file selected</source>
        <translation>Geen bestand geselecteerd</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="94"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="266"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="307"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="123"/>
        <source>What would you like to do?</source>
        <translation>Wat wilt u doen?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="160"/>
        <source>Start New Image Analysis</source>
        <translation>Nieuwe beeldanalyse starten</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="178"/>
        <source>Review Existing Image Analysis</source>
        <translation>Bestaande beeldanalyse beoordelen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="223"/>
        <source>Select Directories</source>
        <translation>Mappen selecteren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="245"/>
        <source>Where are the images you want to analyze?</source>
        <translation>Waar bevinden zich de afbeeldingen die u wilt analyseren?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="286"/>
        <source>Where do you want ADIAT to store the output files?</source>
        <translation>Waar moet ADIAT de uitvoerbestanden opslaan?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="348"/>
        <source>Image Capture Information</source>
        <translation>Informatie over beeldopname</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="370"/>
        <source>What drone/camera was used to capture images?</source>
        <translation>Welke drone/camera is gebruikt om de afbeeldingen vast te leggen?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="400"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>Op welke hoogte boven de grond (AGL) vloog de drone?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="452"/>
        <source>ft</source>
        <translation>ft</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="457"/>
        <source>m</source>
        <translation>m</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="495"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation>Geschatte grondbemonsteringsafstand (GSD):</translation>
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
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="526"/>
        <source>--</source>
        <translation>--</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="565"/>
        <source>Search Target Size</source>
        <translation>Grootte van zoekdoel</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="590"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Ongeveer hoe groot zijn de objecten die u wilt identificeren?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="621"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Meer voorbeelden:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 ft² – Hoed, helm, plastic zak &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 ft² – Kat, dagrugzak &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 ft² – Grote rugzak, middelgrote hond &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 ft² – Slaapzak, grote hond &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 ft² – Kleine boot, 2-persoonstent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 ft² – Auto/SUV, kleine pick-up, grote tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 ft² – Huis &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="660"/>
        <source>ALGORITHM SELECTION GUIDE</source>
        <translation>GIDS VOOR ALGORITMESELECTIE</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="682"/>
        <source>Are you using thermal images?</source>
        <translation>Gebruikt u thermische afbeeldingen?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="727"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1114"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="758"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1099"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="831"/>
        <source>Reset</source>
        <translation>Resetten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="147"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="888"/>
        <source>Algorithm Parameters</source>
        <translation>Algoritmeparameters</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="918"/>
        <source>General Settings</source>
        <translation>Algemene instellingen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="940"/>
        <source>What color should be used to highlight Areas of Interest (AOIs)?</source>
        <translation>Welke kleur moet worden gebruikt om interessegebieden (AOI&apos;s) te markeren?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="960"/>
        <source>Select Color</source>
        <translation>Kleur selecteren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1009"/>
        <source>How many images should be processed at the same time?</source>
        <translation>Hoeveel afbeeldingen moeten tegelijkertijd worden verwerkt?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1033"/>
        <source>Run Benchmark</source>
        <translation>Benchmark uitvoeren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1056"/>
        <source>What resolution should images be processed at?</source>
        <translation>Op welke resolutie moeten afbeeldingen worden verwerkt?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1084"/>
        <source>Were the images captured in different lighting conditions?</source>
        <translation>Zijn de afbeeldingen vastgelegd onder verschillende lichtomstandigheden?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1177"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1189"/>
        <source>Skip this wizard in the future</source>
        <translation>Deze wizard in de toekomst overslaan</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1217"/>
        <source>Back</source>
        <translation>Terug</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="261"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="266"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="272"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1229"/>
        <source>Continue</source>
        <translation>Doorgaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="102"/>
        <source>ADIAT Image Analysis Guide</source>
        <translation>ADIAT-beeldanalysegids</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="256"/>
        <source>Load Results</source>
        <translation>Resultaten laden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="269"/>
        <source>Start Processing</source>
        <translation>Verwerking starten</translation>
    </message>
</context>
<context>
    <name>ImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="78"/>
        <source>Select Drone/Camera</source>
        <translation>Drone/camera selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="82"/>
        <source>No drones available</source>
        <translation>Geen drones beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="126"/>
        <source>Other</source>
        <translation>Overig</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="162"/>
        <source>Error loading drone data</source>
        <translation>Fout bij laden van dronegegevens</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="240"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Ongeldige cameragegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="473"/>
        <source>{sensor_name}: Focal length not found in image EXIF</source>
        <translation>{sensor_name}: brandpuntsafstand niet gevonden in afbeeldings-EXIF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="475"/>
        <source>{sensor_name}: Select input directory to extract focal length from images</source>
        <translation>{sensor_name}: selecteer invoermap om brandpuntsafstand uit afbeeldingen te extraheren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="482"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Ontbrekende cameragegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="483"/>
        <source>Unable to calculate GSD. Sensor dimensions found, but:</source>
        <translation>Kan GSD niet berekenen. Sensorafmetingen gevonden, maar:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="484"/>
        <source>• Focal length is required (available from image EXIF data)</source>
        <translation>• Brandpuntsafstand is vereist (beschikbaar uit EXIF-gegevens van afbeelding)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="485"/>
        <source>GSD calculation requires an actual image file to extract focal length.</source>
        <translation>GSD-berekening vereist een werkelijk afbeeldingsbestand om de brandpuntsafstand te extraheren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="491"/>
        <source>-- (Error)</source>
        <translation>-- (Fout)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="523"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="525"/>
        <source>Primary</source>
        <translation>Primair</translation>
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
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="118"/>
        <source>(Image {current} of {total})</source>
        <translation>(Afbeelding {current} van {total})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="447"/>
        <source>Error Loading Image</source>
        <translation>Fout bij laden van afbeelding</translation>
    </message>
</context>
<context>
    <name>InputProcessingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="31"/>
        <source>Processing Resolution</source>
        <translation>Verwerkingsresolutie</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="36"/>
        <source>Resolution:</source>
        <translation>Resolutie:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="41"/>
        <source>Original</source>
        <translation>Origineel</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="52"/>
        <source>Custom</source>
        <translation>Aangepast</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="61"/>
        <source>Select a preset resolution for processing. Lower resolutions are faster but less detailed.
&apos;Original&apos; uses the video&apos;s native resolution (no downsampling).
720P (1280x720) provides excellent balance between speed and detection accuracy.
Select &apos;Custom&apos; to manually set width and height.</source>
        <translation>Selecteer een vooraf ingestelde resolutie voor verwerking. Lagere resoluties zijn sneller maar minder gedetailleerd.
&apos;Origineel&apos; gebruikt de native resolutie van de video (geen downsampling).
720P (1280x720) biedt een uitstekende balans tussen snelheid en detectienauwkeurigheid.
Selecteer &apos;Aangepast&apos; om breedte en hoogte handmatig in te stellen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="71"/>
        <source>Width:</source>
        <translation>Breedte:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="78"/>
        <source>Custom processing width in pixels (320-3840).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Aangepaste verwerkingsbreedte in pixels (320-3840).
Alleen ingeschakeld wanneer de resolutie &apos;Aangepast&apos; is geselecteerd.
Lagere waarden = snellere verwerking, minder detail.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="84"/>
        <source>Height:</source>
        <translation>Hoogte:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="91"/>
        <source>Custom processing height in pixels (240-2160).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Aangepaste verwerkingshoogte in pixels (240-2160).
Alleen ingeschakeld wanneer de resolutie &apos;Aangepast&apos; is geselecteerd.
Lagere waarden = snellere verwerking, minder detail.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="107"/>
        <source>Performance Options</source>
        <translation>Prestatieopties</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="112"/>
        <source>Frame Rate:</source>
        <translation>Framerate:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="118"/>
        <source>Source FPS</source>
        <translation>Bron-FPS</translation>
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
        <translation>Beperk de framerate voor verwerking.

• Bron-FPS - volg het brontempo (live-bronnen kunnen een veiligheidsplafond toepassen)
• 30 FPS - goede balans tussen vloeiendheid en prestaties
• 25 FPS - standaard voor PAL-video
• 20 FPS - verlaagd CPU-gebruik
• 15 FPS - lager CPU-gebruik
• 10 FPS - aanzienlijke CPU-besparingen
• 5 FPS - maximale CPU-besparingen, kan snelle objecten missen

Lagere framerates verlagen het CPU-gebruik, maar kunnen snel bewegende objecten missen.
Detecties blijven behouden tussen overgeslagen frames voor visuele continuïteit.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="148"/>
        <source>Render at Processing Resolution (faster for high-res)</source>
        <translation>Renderen op verwerkingsresolutie (sneller voor hoge resolutie)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="151"/>
        <source>Renders detection overlays at processing resolution instead of original video resolution.
Significantly faster for high-resolution videos (1080p+) with minimal visual impact.
Example: Processing at 720p but video is 4K - renders at 720p then upscales.
Recommended: ON for high-res videos, OFF for native 720p or lower.</source>
        <translation>Rendert detectie-overlays op verwerkingsresolutie in plaats van oorspronkelijke videoresolutie.
Aanzienlijk sneller voor video&apos;s met hoge resolutie (1080p+) met minimale visuele impact.
Voorbeeld: verwerking op 720p maar video is 4K - rendert op 720p en schaalt vervolgens op.
Aanbevolen: AAN voor hoge-resolutie video&apos;s, UIT voor native 720p of lager.</translation>
    </message>
</context>
<context>
    <name>LoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="12"/>
        <source>Generating Report</source>
        <translation>Rapport genereren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="29"/>
        <source>Report generation in progress...</source>
        <translation>Rapportgeneratie bezig...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="33"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>MRMap</name>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
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
        <translation>Aantal segmenten waarin elke afbeelding wordt verdeeld voor MR Map-analyse.
Elk segment wordt onafhankelijk verwerkt voor multiresolutie-kenmerkdetectie.
Prestatie-impact:
• Hoger aantal segmenten: VERHOOGT de verwerkingstijd (meer segmenten te analyseren)
• Lager aantal segmenten: VERLAAGT de verwerkingstijd (minder segmenten te analyseren)
• 1 segment: snelste verwerking (analyseert de hele afbeelding in één keer)
Meer segmenten verbeteren de detectie in afbeeldingen met variërende kenmerken.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Beeldsegmenten:</translation>
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
        <translation>Selecteer het aantal segmenten waarin elke afbeelding wordt verdeeld.
• Opties: 1, 2, 4, 6, 9, 16, 25, 36 segmenten
• Standaard: 1 (analyseer de hele afbeelding als één segment)
Het MR Map-algoritme (Multi-Resolution Map) analyseert kenmerken op meerdere schalen:
• 1 segment: verwerk de hele afbeelding (het beste voor kleine afbeeldingen of uniforme inhoud)
• Meer segmenten: analyseer lokale gebieden onafhankelijk (beter voor grote afbeeldingen)
Meer segmenten verbeteren de detectie in afbeeldingen met variërende kenmerken in de scène.
Aanbevolen: 4-9 segmenten voor typische dronebeelden.</translation>
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
        <translation>Kleurruimte:</translation>
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
        <translation>Selecteer de kleurruimte voor MR Map-analyse.
Het MR Map-algoritme analyseert kenmerken in verschillende kleurrepresentaties:
• LAB: perceptueel uniforme kleurruimte (standaard, beter voor analyse van kleurverschillen)
• RGB: standaard rood-groen-blauw kleurruimte (goed voor algemeen gebruik)
• HSV: tint-verzadiging-waarde kleurruimte (beter voor kleurgebaseerde kenmerkdetectie)
Verschillende kleurruimten kunnen de detectie verbeteren afhankelijk van de afbeeldingsinhoud.
Aanbevolen: LAB voor de meeste gevallen, HSV voor kleurrijke beelden.</translation>
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
        <translation>Venstergrootte voor multiresolutie-analyse.
Bepaalt de ruimtelijke schaal van te detecteren kenmerken.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="202"/>
        <source>Window Size:</source>
        <translation>Venstergrootte:</translation>
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
        <translation>Stel de venstergrootte in voor multiresolutie-analyse.
• Bereik: 1 tot 10
• Standaard: 5
Het MR Map-algoritme analyseert kenmerken op meerdere ruimtelijke schalen met schuifvensters:
• Kleinere waarden (1-3): detecteer fijne details en kleine kenmerken
• Gemiddelde waarden (4-6): gebalanceerde detectie (aanbevolen voor de meeste gevallen)
• Grotere waarden (7-10): detecteer grotere kenmerken en patronen
De venstergrootte beïnvloedt de ruimtelijke resolutie van kenmerkdetectie.
Grotere vensters bieden meer context, maar kunnen kleine objecten missen.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="254"/>
        <source>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</source>
        <translation>Detectiedrempel voor MR Map-kenmerkdetectie.
Bepaalt de gevoeligheid van kenmerkdetectie over meerdere resoluties.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="258"/>
        <source>Threshold:</source>
        <translation>Drempel:</translation>
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
        <translation>Pas de detectiedrempel voor het MR Map-algoritme aan.
• Bereik: 1 tot 200
• Standaard: 100
• Schuifregelaar is omgekeerd: LINKS = hogere drempel, RECHTS = lagere drempel
Het MR Map-algoritme detecteert kenmerken op meerdere ruimtelijke resoluties:
• Lagere waarden (1-50): zeer gevoelig, detecteert veel kenmerken (kan ruis bevatten)
• Gemiddelde waarden (51-150): gebalanceerde detectie (aanbevolen voor de meeste gevallen)
• Hogere waarden (151-200): minder gevoelig, detecteert alleen prominente kenmerken
De drempel bepaalt hoe onderscheidend een kenmerk moet zijn om te worden gedetecteerd.
Opmerking: het uiterlijk van de schuifregelaar is omgekeerd - schuif naar links voor strenger, naar rechts voor toegeeflijker.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="326"/>
        <source>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</source>
        <translation>Huidige drempelwaarde voor MR Map-kenmerkdetectie.
Toont de waarde die is geselecteerd op de drempelschuifregelaar (1-200).
Lagere waarden = gevoeliger detectie.</translation>
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
        <translation>Detectie-uitbreiding (optioneel)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="48"/>
        <source>Threshold Expansion</source>
        <translation>Drempeluitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="50"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid met pixels waarvan de histogramtellingen
onder (drempel + {0}) liggen. Pixels binnen de clusterrechthoek worden onvoorwaardelijk toegevoegd;
pixels erbuiten worden toegevoegd als ze verbonden zijn via andere geschikte pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="57"/>
        <source>Hue Expansion</source>
        <translation>Tintuitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="59"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid via buren waarvan de tint binnen +/- {0}
(OpenCV-eenheden) van de gemiddelde tint van de oorspronkelijk gedetecteerde pixels valt.
Pixels met verzadiging onder {1}% of waarde onder {2}% worden uitgesloten.</translation>
    </message>
</context>
<context>
    <name>MRMapWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="21"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>Bevatten uw afbeeldingen complexe scènes met gebouwen, voertuigen of gemengde door mensen gemaakte bedekking?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="41"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="56"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="92"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Hoe agressief moet ADIAT naar afwijkingen zoeken?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="105"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Opmerking: een hogere instelling vindt meer potentiële afwijkingen, maar kan ook het aantal valse positieven vergroten.</translation>
    </message>
</context>
<context>
    <name>MRMapWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="39"/>
        <source>Very 
Conservative</source>
        <translation>Zeer 
conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="40"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="41"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="42"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="43"/>
        <source>Very 
Aggressive</source>
        <translation>Zeer 
agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="60"/>
        <source>Detection Expansion (optional)</source>
        <translation>Detectie-uitbreiding (optioneel)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="67"/>
        <source>Threshold Expansion</source>
        <translation>Drempeluitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="69"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid met pixels waarvan de histogramtellingen
onder (drempel + {0}) liggen. Pixels binnen de clusterrechthoek worden onvoorwaardelijk toegevoegd;
pixels erbuiten worden toegevoegd als ze verbonden zijn via andere geschikte pixels.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="76"/>
        <source>Hue Expansion</source>
        <translation>Tintuitbreiding</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="78"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Indien ingeschakeld, wordt elke AOI uitgebreid via buren waarvan de tint binnen +/- {0}
(OpenCV-eenheden) van de gemiddelde tint van de oorspronkelijk gedetecteerde pixels valt.
Pixels met verzadiging onder {1}% of waarde onder {2}% worden uitgesloten.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="22"/>
        <source>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument v1.2 - Gesponsord door TEXSAR</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="52"/>
        <source>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</source>
        <translation>Bladeren naar de uitvoermap om analyseresultaten op te slaan.
Opent een map-selectievenster.
Kies een lege map of maak een nieuwe aan om overschrijven van bestaande bestanden te voorkomen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="57"/>
        <location filename="../resources/views/images/MainWindow.ui" line="133"/>
        <location filename="../resources/views/images/MainWindow.ui" line="597"/>
        <source> Select</source>
        <translation> Selecteren</translation>
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
        <translation>Pad naar de uitvoermap voor het opslaan van analyseresultaten.
Klik op de knop Selecteren om naar een doelmap te bladeren.
Resultaten omvatten:
• Verwerkte afbeeldingen met gemarkeerde gedetecteerde objecten
• CSV-bestand met detectiecoördinaten en metagegevens
• KML-bestand om resultaten in kaarttoepassingen te bekijken
• Aanvullende algoritme-specifieke uitvoerbestanden</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="97"/>
        <source>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</source>
        <translation>Selecteer de map met de te analyseren afbeeldingen.
Ondersteunde formaten: JPG, PNG, TIFF en andere veelvoorkomende afbeeldingsformaten.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="101"/>
        <source>Input Folder:</source>
        <translation>Invoermap:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="113"/>
        <source>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</source>
        <translation>Selecteer de doelmap voor analyseresultaten.
De uitvoer omvat verwerkte afbeeldingen met gemarkeerde detecties en CSV-gegevensbestanden.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="117"/>
        <source>Output Folder:</source>
        <translation>Uitvoermap:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="129"/>
        <source>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</source>
        <translation>Bladeren naar de invoermap met de te analyseren afbeeldingen.
Opent een map-selectievenster.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="152"/>
        <source>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</source>
        <translation>Pad naar de invoermap met afbeeldingen voor analyse.
Klik op de knop Selecteren om naar een map te bladeren.
Alle ondersteunde afbeeldingsbestanden in deze map worden verwerkt.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="209"/>
        <source>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</source>
        <translation>Minimale objectgrootte in pixels voor detectiefiltering.
Objecten kleiner dan dit worden genegeerd.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="213"/>
        <source>Min Object Area (px):</source>
        <translation>Min. objectgebied (px):</translation>
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
        <translation>Stel het minimale objectgebied in pixels in voor detectiefiltering.
• Bereik: 1 tot 999 pixels
• Standaard: 10 pixels
Objecten kleiner dan deze drempel worden uitgefilterd en niet gedetecteerd.
• Lagere waarden: detecteer kleinere objecten (kan valse positieven verhogen)
• Hogere waarden: detecteer alleen grotere objecten (vermindert ruis)
Gebruik om kleine artefacten en ruis in detectieresultaten uit te filteren.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="269"/>
        <source>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</source>
        <translation>Maximale objectgrootte in pixels voor detectiefiltering.
Objecten groter dan dit worden genegeerd.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="273"/>
        <source>Max Object Area (px):</source>
        <translation>Max. objectgebied (px):</translation>
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
        <translation>Stel het maximale objectgebied in pixels in voor detectiefiltering.
• Bereik: 0 tot 99999 pixels
• Standaard: 0 (Geen - geen maximumfilter toegepast)
• Speciale waarde: 0 wordt weergegeven als &quot;Geen&quot;
Objecten groter dan deze drempel worden uitgefilterd en niet gedetecteerd.
• Lagere waarden: detecteer alleen kleinere objecten
• Hogere waarden: sta detectie van grotere objecten toe
• Op 0 (Geen) zetten: geen maximumgroottefiltering
Gebruik om zeer grote valse positieven uit te sluiten, zoals schaduwen of terreinkenmerken.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="299"/>
        <source>None</source>
        <translation>Geen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="323"/>
        <source>Disable the maximum size filter and allow detections of any size.</source>
        <translation>Schakel het filter voor maximale grootte uit en sta detecties van elke grootte toe.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="326"/>
        <source>No max limit</source>
        <translation>Geen maximumlimiet</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="359"/>
        <source>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</source>
        <translation>Kleur die wordt gebruikt om gedetecteerde objecten in uitvoerafbeeldingen te markeren en identificeren.
Klik op de kleurknop om een andere kleur te selecteren.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="363"/>
        <source>Object Identifer Color:</source>
        <translation>Kleur object-identificatie:</translation>
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
        <translation>Selecteer de kleur die wordt gebruikt om gedetecteerde objecten in uitvoerafbeeldingen te markeren.
• Standaard: groen (RGB: 0, 255, 0)
Klik om een kleurkiezerdialoogvenster te openen en een andere markeerkleur te kiezen.
De geselecteerde kleur wordt gebruikt voor:
• Het tekenen van cirkels/rechthoeken rond gedetecteerde objecten
• Het markeren van AOI-locaties op uitvoerafbeeldingen
• Het maken van visuele markeringen in de resultatenviewer
Kies een kleur die goed contrasteert met uw afbeeldingsinhoud voor de beste zichtbaarheid.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="395"/>
        <source>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</source>
        <translation>Maximaal aantal parallelle processen voor beeldanalyse.
Meer processen = snellere verwerking, maar hoger CPU-/geheugengebruik.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="399"/>
        <source>Max Processes: </source>
        <translation>Max. processen: </translation>
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
        <translation>Stel het maximumaantal parallelle processen in voor beeldanalyse.
• Bereik: 1 tot 20 processen
• Standaard: 10 processen
De applicatie gebruikt multiprocessing om meerdere afbeeldingen tegelijk te analyseren:
• Hogere waarden: snellere verwerking (gebruikt meer CPU-cores en geheugen)
• Lagere waarden: langzamere verwerking (gebruikt minder systeembronnen)
• Aanbevolen: stel in op het aantal CPU-cores of iets hoger
• Voor systemen met beperkt RAM: verlaag deze waarde om geheugenproblemen te voorkomen
Elk proces analyseert één afbeelding tegelijk, dus meer processen = meer parallelle beeldverwerking.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="446"/>
        <source>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</source>
        <translation>Resolutie waarop afbeeldingen worden verwerkt.
Lagere resoluties = snellere verwerking, maar kunnen kleine objecten missen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="450"/>
        <source>Processing Resolution:</source>
        <translation>Verwerkingsresolutie:</translation>
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
        <translation>Selecteer de verwerkingsresolutie als percentage van de oorspronkelijke afbeeldingsgrootte:
• 100%: oorspronkelijke resolutie (geen schaling, hoogste kwaliteit, langzaamst)
• 75%: hoge kwaliteit (~56% van de pixels, ~1,8x sneller)
• 50%: gebalanceerde kwaliteit (25% van de pixels, ~4x sneller) - AANBEVOLEN
• 33%: snelle verwerking (~11% van de pixels, ~9x sneller)
• 25%: zeer snel (6% van de pixels, ~16x sneller)
• 10%: ultrasnel (1% van de pixels, ~100x sneller)

Percentageschaling behoudt de oorspronkelijke beeldverhouding.
Werkt met elke afbeeldingsgrootte, oriëntatie of beeldverhouding.

Waarden voor Min./Max. gebied worden altijd opgegeven in de oorspronkelijke resolutie.
Alle resultaten worden teruggegeven in coördinaten van de oorspronkelijke resolutie.</translation>
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
        <translation>Schakel histogramnormalisatie-voorbewerking op afbeeldingen in vóór detectie.
Histogramnormalisatie past afbeeldingskleuren aan om overeen te komen met een referentieafbeelding:
• Egaliseert verschillen in licht en kleur tussen afbeeldingen
• Corrigeert voor variërende zonshoeken, schaduwen en atmosferische omstandigheden
• Standaardiseert het kleuruiterlijk over de afbeeldingsset
• Verbetert de consistentie van detectieresultaten
Wanneer ingeschakeld, selecteer een referentieafbeelding met ideale licht-/kleuromstandigheden.
Nuttig bij het verwerken van afbeeldingen die op verschillende tijden of onder variërende omstandigheden zijn genomen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="540"/>
        <source>Normalize Histograms</source>
        <translation>Histogrammen normaliseren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="555"/>
        <source>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</source>
        <translation>Selecteer de referentieafbeelding voor histogramnormalisatie.
Alle afbeeldingen worden aangepast om overeen te komen met de kleurverdeling van deze afbeelding.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="559"/>
        <source>Reference Image:</source>
        <translation>Referentie-afbeelding:</translation>
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
        <translation>Pad naar de referentieafbeelding voor histogramnormalisatie.
Klik op de knop Selecteren om een afbeelding te kiezen.
Kies een afbeelding met ideale licht- en kleuromstandigheden:
• Heldere, goed verlichte afbeelding uit uw dataset
• Representatief voor het gewenste uiterlijk
• Typische lichtomstandigheden voor uw missie
Alle andere afbeeldingen worden in kleur aangepast om overeen te komen met deze referentie.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="592"/>
        <source>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</source>
        <translation>Bladeren naar een referentieafbeelding voor histogramnormalisatie.
Opent een afbeeldingsbestand-selectievenster.
Selecteer een representatieve afbeelding met goed licht en typische kleuromstandigheden.</translation>
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
        <translation>Selecteer het detectie-algoritme dat moet worden gebruikt voor beeldanalyse.

Elk algoritme heeft specifieke sterke punten en gebruikssituaties:

• HSV-kleurbereik: het beste voor het detecteren van specifieke gekleurde objecten
• Kleurbereik (RGB): alternatieve kleurdetectie met RGB-kleurruimte
• RX-afwijking: statistische detectie voor ongewone/afwijkende objecten
• Thermische afwijking: detecteert temperatuurafwijkingen in thermische beelden
• Thermisch bereik: temperatuurgebaseerde detectie in thermische afbeeldingen
• Matched Filter: doelgebaseerde detectie met spectrale matching
• MR Map: multiresolutie-kenmerkdetectie op verschillende schalen
• AI-persoonsdetector: machine learning voor het detecteren van personen

Beweeg over de algoritme-vervolgkeuzelijst voor gedetailleerde beschrijvingen van elk algoritme.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="658"/>
        <source>Algorithm:</source>
        <translation>Algoritme:</translation>
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
        <translation>Selecteer het detectie-algoritme voor uw beeldanalysetaak.
Elk algoritme heeft unieke sterke punten en optimale gebruikssituaties:

═══════════════════════════════════════════════════
HSV-KLEURBEREIK
═══════════════════════════════════════════════════
Wat het doet: detecteert objecten via specifieke kleurbereiken in HSV-kleurruimte
Sterke punten:
• Het beste voor het detecteren van fel gekleurde objecten (oranje, gele, rode kleding)
• Robuust tegen lichtvariaties (HSV scheidt kleur van helderheid)
• Zeer aanpasbaar met bereiken per kanaal
• Interactieve kleurselectiehulpmiddelen beschikbaar
Zwakke punten:
• Vereist zorgvuldige afstemming van het kleurbereik voor optimale resultaten
• Kan moeite hebben met kleurvariaties in schaduwen
• Niet effectief voor kleurloze of gecamoufleerde objecten
Het beste voor: SAR (gekleurde kleding, uitrusting), gekleurde voertuigen, tenten, gekleurde dekzeilen

═══════════════════════════════════════════════════
KLEURBEREIK (RGB)
═══════════════════════════════════════════════════
Wat het doet: detecteert objecten via RGB-kleurbereiken
Sterke punten:
• Eenvoudige en intuïtieve RGB-kleurspecificatie
• Snelle verwerkingssnelheid
• Goed voor basis kleurgebaseerde detectie
Zwakke punten:
• Gevoeliger voor lichtveranderingen dan HSV
• RGB-kanalen mengen kleur- en helderheidsinformatie
• Minder flexibel dan HSV voor complexe kleurvariaties
Het beste voor: gecontroleerde lichtsituaties, snelle basis kleurdetectie, eenvoudige scenario&apos;s

═══════════════════════════════════════════════════
RX-AFWIJKING
═══════════════════════════════════════════════════
Wat het doet: statistische afwijkingsdetectie - vindt pixels die ongewoon zijn ten opzichte van de achtergrond
Sterke punten:
• Detecteert objecten die niet bij de achtergrond passen (geen doelmonster nodig)
• Uitstekend voor het vinden van gecamoufleerde of gedeeltelijk verborgen objecten
• Werkt op alle beeldtypen (RGB, thermisch, multispectraal)
• Past zich automatisch aan scènekenmerken aan
• Goed voor het detecteren van subtiele verschillen
Zwakke punten:
• Kan natuurlijke afwijkingen detecteren (stenen, vegetatieveranderingen)
• Vereist afstemming van gevoeligheid om detectie vs. valse positieven te balanceren
• Hogere aantallen segmenten verhogen de verwerkingstijd aanzienlijk
• Minder effectief in zeer gevarieerde/rommelige achtergronden
Het beste voor: zoekacties naar vermisten (mens tussen vegetatie), gecamoufleerde objecten, onbekende doelen, alles ongewoons in de scène

═══════════════════════════════════════════════════
THERMISCHE AFWIJKING
═══════════════════════════════════════════════════
Wat het doet: detecteert temperatuurafwijkingen in thermische beelden (warme/koude plekken)
Sterke punten:
• Vindt temperatuuruitbijters automatisch (geen specifieke temp. nodig)
• Uitstekend voor het detecteren van warmtebronnen (mensen, dieren, branden)
• Werkt overdag of &apos;s nachts met thermische camera&apos;s
• Detecteert door lichte vegetatie heen
• Aanpasbaar voor warme, koude of beide soorten afwijkingen
Zwakke punten:
• Vereist thermische (FLIR) beelden
• Kan door zon verwarmde objecten detecteren (stenen, voertuigen)
• Temperatuurgradiënten kunnen valse positieven veroorzaken
• Beïnvloed door omgevingstemperatuur en weer
Het beste voor: nachtelijke zoekacties, detecteren van mensen/dieren via lichaamswarmte, vinden van warmtebronnen, koude-plekdetectie

═══════════════════════════════════════════════════
THERMISCH BEREIK
═══════════════════════════════════════════════════
Wat het doet: temperatuurgebaseerde detectie binnen een specifiek temperatuurbereik
Sterke punten:
• Nauwkeurige temperatuurgebaseerde detectie
• Uitstekend voor het vinden van mensen (lichaamstemp. ~35-40°C / 95-104°F)
• Filtert niet-doel-temperaturen effectief uit
• Werkt overdag of &apos;s nachts met thermische camera&apos;s
• Zeer betrouwbaar wanneer de doeltemperatuur bekend is
Zwakke punten:
• Vereist thermische (FLIR) beelden met temperatuurgegevens
• Doel-temperatuurbereik moet vooraf bekend zijn
• Omgevingsomstandigheden beïnvloeden de doeltemperatuur
• Kan doelen missen bij extreem weer (gevallen van onderkoeling)
Het beste voor: persoonsdetectie (bekende lichaamstemp.), specifieke temperatuurdoelen, branddetectie (hoog temp.bereik)

═══════════════════════════════════════════════════
MATCHED FILTER
═══════════════════════════════════════════════════
Wat het doet: doelgebaseerde detectie via spectrale signatuur-matching
Sterke punten:
• Zeer nauwkeurig wanneer u een doelmonster hebt
• Gebruikt spectrale/kleur-&quot;signatuur&quot; van doel voor matching
• Vermindert valse positieven door matching met bekende doelkenmerken
• Goed voor het detecteren van specifieke objecttypen
Zwakke punten:
• Vereist een referentieafbeelding of kleurmonster van het doel
• Minder effectief als het uiterlijk van het doel sterk varieert
• Lichtverschillen kunnen de matching-nauwkeurigheid beïnvloeden
• Niet geschikt voor onbekende doelen
Het beste voor: het vinden van specifieke bekende objecten (specifieke voertuigkleur, specifieke kleding), wanneer u een doelmonster hebt om mee te matchen

═══════════════════════════════════════════════════
MR MAP (Multi-Resolution Map)
═══════════════════════════════════════════════════
Wat het doet: multiresolutie-kenmerkdetectie op verschillende ruimtelijke schalen
Sterke punten:
• Detecteert kenmerken op meerdere schalen tegelijk
• Goed voor het vinden van objecten van wisselende grootte
• Effectief voor complexe scène-analyse
• Kan zowel grote als kleine kenmerken in één keer detecteren
Zwakke punten:
• Rekenintensiever
• Vereist zorgvuldige parameterafstemming
• Hogere aantallen segmenten verhogen de verwerkingstijd aanzienlijk
• Kan meer valse positieven produceren die filtering vereisen
Het beste voor: complexe scènes met variërende objectgroottes, wanneer de doelgrootte onbekend is, algemene kenmerkmapping

═══════════════════════════════════════════════════
AI-PERSOONSDETECTOR
═══════════════════════════════════════════════════
Wat het doet: deep-learning AI-model dat specifiek is getraind om personen te detecteren
Sterke punten:
• Zeer nauwkeurig voor het detecteren van personen in verschillende houdingen
• Werkt bij gedeeltelijke zichtbaarheid en verschillende kleding
• Geen kleur-/temperatuurvereisten - werkt op normale RGB-afbeeldingen
• Getraind op miljoenen afbeeldingen voor robuuste detectie
• Detecteert personen in complexe achtergronden
• Minimale parameterafstemming nodig
Zwakke punten:
• Detecteert alleen personen (geen voertuigen, uitrusting, enz.)
• Rekenintensief - langzamere verwerking
• Vereist voldoende afbeeldingsresolutie
• Kan moeite hebben met zeer verre/kleine personen
• Minder effectief bij zware afdekking
Het beste voor: SAR-operaties (vermiste personen), personen tellen, situaties waarin alleen menselijke detectie nodig is

═══════════════════════════════════════════════════
GIDS VOOR ALGORITMESELECTIE
═══════════════════════════════════════════════════
• Voor kleurrijke objecten (felgekleurde kleding, uitrusting): HSV-kleurbereik
• Voor thermische camera&apos;s die naar personen zoeken: thermisch bereik of thermische afwijking
• Voor gecamoufleerde of verborgen subjecten: RX-afwijking
• Voor het specifiek detecteren van personen: AI-persoonsdetector
• Wanneer u een doelmonster hebt: Matched Filter
• Voor onbekende doelen die opvallen: RX-afwijking of thermische afwijking
• Voor de snelste verwerking: kleurbereik (RGB) of HSV-kleurbereik
• Voor de meest nauwkeurige persoonsdetectie: AI-persoonsdetector</translation>
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
        <translation>Start de verwerking van afbeeldingen met het geselecteerde algoritme.
Vereisten vóór het starten:
• Invoermap moet geselecteerd zijn met geldige afbeeldingen
• Uitvoermap moet geselecteerd zijn
• Algoritme moet geselecteerd zijn
• Alle vereiste algoritmeparameters moeten geconfigureerd zijn
De verwerking zal:
• Alle afbeeldingen in de invoermap analyseren met het geselecteerde algoritme
• Globale filters toepassen (min./max. gebied, K-Means, histogramnormalisatie)
• Resultaten opslaan in de uitvoermap (gemarkeerde afbeeldingen, CSV-, KML-bestanden)
• Voortgang en resultaten weergeven in het uitvoervenster
Klik op Annuleren tijdens de verwerking om de analyse te stoppen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="918"/>
        <source>Start</source>
        <translation>Starten</translation>
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
        <translation>Annuleer het momenteel actieve beeldanalyseproces.
Stopt de verwerking onmiddellijk en beëindigt alle werkprocessen veilig.
Effecten van annuleren:
• Alle lopende analyseprocessen worden gestopt
• Gedeeltelijke resultaten worden opgeslagen tot het annuleringspunt
• Reeds verwerkte afbeeldingen krijgen uitvoerbestanden in de uitvoermap
• Verwerking kan na annulering opnieuw worden gestart
• Keert terug naar de gereed-toestand
Gebruik wanneer u de verwerking moet stoppen om instellingen aan te passen of problemen op te lossen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="963"/>
        <source> Cancel</source>
        <translation> Annuleren</translation>
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
        <translation>Open de resultatenviewer om detectieresultaten te bekijken.
Beschikbaar nadat de verwerking succesvol is voltooid.
De resultatenviewer biedt:
• Interactief bladeren door afbeeldingen met gemarkeerde gedetecteerde objecten
• Naast-elkaar-vergelijking van originele en verwerkte afbeeldingen
• Navigatie door alle verwerkte afbeeldingen
• AOI-details (interessegebied) en metagegevens
• GPS-coördinaten voor gedetecteerde objecten
• Exportopties voor geselecteerde detecties
• Zoom- en panmogelijkheden
• Filteren en sorteren van detectieresultaten
Gebruik om analyseresultaten te bekijken, verifiëren en exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1594"/>
        <location filename="../resources/views/images/MainWindow.ui" line="1018"/>
        <source> View Results</source>
        <translation> Resultaten bekijken</translation>
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
        <translation>Hulp</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1111"/>
        <source>Image Analysis Wizard</source>
        <translation>Beeldanalysewizard</translation>
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
        <translation>Start de wizard Beeldanalysegids om analyse-instellingen te configureren.
Opent een stapsgewijze wizard om:
• Invoer- en uitvoermappen te selecteren
• Beeldopname-instellingen te configureren (drone, hoogte, GSD)
• Doelobjectgrootte in te stellen
• Detectie-algoritme te kiezen
• Algoritme-specifieke parameters te configureren
• Algemene verwerkingsopties in te stellen
De wizard sluit dit venster en opent met alle instellingen vooraf ingevuld.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1132"/>
        <source>Load Results File</source>
        <translation>Resultatenbestand laden</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1135"/>
        <source>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</source>
        <translation>Laad een eerder opgeslagen resultatenbestand om te bekijken.
Opent een bestandsdialoogvenster om een resultatenbestand te selecteren (.pkl-formaat).
Laadt de analyseresultaten en opent de resultatenviewer.
Gebruik dit om resultaten van eerdere analysesessies te bekijken zonder opnieuw te verwerken.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1148"/>
        <source>Load Results Folder</source>
        <translation>Resultatenmap laden</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1151"/>
        <source>Scan a folder recursively for ADIAT_DATA.XML files.
Displays all found results in a dialog for easy browsing.
Use this to quickly find and open results from multiple analysis sessions.</source>
        <translation>Scan een map recursief naar ADIAT_DATA.XML-bestanden.
Toont alle gevonden resultaten in een dialoogvenster voor eenvoudig bladeren.
Gebruik dit om snel resultaten van meerdere analysesessies te vinden en te openen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1163"/>
        <source>Preferences</source>
        <translation>Voorkeuren</translation>
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
        <translation>Open het dialoogvenster Voorkeuren om applicatie-instellingen te configureren.
Pas globale instellingen aan, waaronder:
• Applicatie-thema (licht/donker)
• Max. AOI-waarschuwingsdrempel
• AOI-cirkelstraal voor clustering
• Coördinatensysteem-indeling (Lat/Long, UTM)
• Temperatuureenheid (Fahrenheit/Celsius)
• Afstandseenheid (meter/voet)
• Configuratiebestand dronesensor
Alle wijzigingen worden automatisch opgeslagen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1185"/>
        <source>Video Parser</source>
        <translation>Videoparser</translation>
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
        <translation>Open het hulpprogramma Videoparser om frames uit videobestanden te halen.
Zet videobeelden om in individuele frame-afbeeldingen voor analyse.
Functies:
• Frames op opgegeven tijdsintervallen extraheren
• Optionele SRT-bestandsondersteuning voor GPS-metagegevens
• Ondersteunt gangbare videoformaten (MP4, AVI, MOV, enz.)
• Sluit locatiegegevens in geëxtraheerde frames in
Gebruik om videobeelden voor te bereiden op beeldgebaseerde analyse.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1205"/>
        <source>Streaming Detector</source>
        <translation>Streamingdetector</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1208"/>
        <source>Switch to the Streaming Detector</source>
        <translation>Overschakelen naar de streamingdetector</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1218"/>
        <source>Flight Viewer</source>
        <translation>Vluchtviewer</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1221"/>
        <source>Open the Flight Viewer to pair with ADIAT Mobile drone controllers and watch their live feeds.</source>
        <translation>Open de Vluchtviewer om te koppelen met ADIAT Mobile-dronecontrollers en hun livefeeds te bekijken.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1231"/>
        <source>Real-Time Anomaly Detection</source>
        <translation>Realtime afwijkingsdetectie</translation>
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
        <translation>Open het venster Realtime afwijkingsdetectie voor geavanceerde live-analyse.
Combineert meerdere detectie-algoritmen voor uitgebreide realtime afwijkingsdetectie.
Functies:
• Bewegingsdetectie met achtergrondsubtractie
• Detectie van kleurkwantisatie-afwijkingen
• Geavanceerde streaming videoverwerking
• Detectiefusie en temporele filtering
• Realtime prestatieoptimalisatie
• Multithreaded verwerking voor betere prestaties
• Verhoogde detectienauwkeurigheid door algoritmecombinatie
Ontworpen voor het detecteren van ongewone objecten, beweging en kleuren in realtime videostreams.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1254"/>
        <source>Search Coordinator</source>
        <translation>Zoekcoördinator</translation>
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
        <translation>Open het venster Zoekcoördinator voor het beheren van beoordelingsprojecten met meerdere batches.
Functies:
• Zoekprojecten met meerdere batches maken en beheren
• Beoordelaarsvoortgang volgen over meerdere afbeeldingssets
• Beoordelingsresultaten van meerdere beoordelaars consolideren
• Dashboard met zoekstatus en metingen bekijken
• Geconsolideerde resultaten exporteren
• Batchtoewijzingen en coördinatie van beoordelaars beheren
Ideaal voor grootschalige zoekopdrachten met meerdere beoordelaars en afbeeldingsbatches.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1273"/>
        <source>Ctrl+Shift+C</source>
        <translation>Ctrl+Shift+C</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1278"/>
        <source>Manual</source>
        <translation>Handleiding</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1281"/>
        <source>Open the online help documentation in your web browser.
Access comprehensive documentation, tutorials, and user guides.
Provides detailed information on all features and algorithms.</source>
        <translation>Open de online hulpdocumentatie in uw webbrowser.
Krijg toegang tot uitgebreide documentatie, tutorials en gebruikershandleidingen.
Biedt gedetailleerde informatie over alle functies en algoritmen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1293"/>
        <source>Check for Updates</source>
        <translation>Controleren op updates</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1296"/>
        <source>Check the update feed for a newer ADIAT installer.
If an update is available, you can download and launch the installer from here.</source>
        <translation>Controleer de update-feed op een nieuwer ADIAT-installatieprogramma.
Als er een update beschikbaar is, kunt u het installatieprogramma vanaf hier downloaden en starten.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1307"/>
        <source>Community Forum</source>
        <translation>Communityforum</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1310"/>
        <source>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</source>
        <translation>Word lid van de Discord-server van de community voor ondersteuning en discussies.
Maak contact met andere gebruikers, deel ervaringen en vraag hulp.
Stel vragen, meld problemen en stel nieuwe functies voor.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1322"/>
        <source>YouTube Channel</source>
        <translation>YouTube-kanaal</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="80"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument v{version} - Gesponsord door TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="265"/>
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
        <translation>Selecteer het detectie-algoritme voor uw beeldanalysetaak:

HSV-KLEURBEREIK: detecteert fel gekleurde objecten (kleding, voertuigen, tenten)
  • Het beste voor: gekleurde objecten in variërende lichtomstandigheden
  • Beperking: vereist kleurafstemming, niet voor gecamoufleerde objecten

KLEURBEREIK (RGB): eenvoudige RGB-kleurdetectie, snelle verwerking
  • Het beste voor: basis kleurdetectie bij gecontroleerd licht
  • Beperking: gevoelig voor lichtveranderingen

RX-AFWIJKING: vindt objecten die niet bij de achtergrond passen (geen monster nodig)
  • Het beste voor: gecamoufleerde/verborgen subjecten, onbekende doelen
  • Beperking: kan natuurlijke afwijkingen detecteren, langzamer met meer segmenten

THERMISCHE AFWIJKING: detecteert warme/koude plekken in thermische beelden
  • Het beste voor: nachtelijke zoekacties, detecteren van mensen/dieren via lichaamswarmte
  • Beperking: vereist thermische camera, kan door zon verwarmde objecten detecteren

RESIDUELE TEMPERATUURAFWIJKING: detecteert lokale delta-T-uitbijters via radiometrische residuen
  • Het beste voor: isoleren van zeldzame warme/koude thermische signaturen in gemengde achtergronden
  • Beperking: vereist radiometrische thermische gegevens, gevoelig voor drempelkeuze

THERMISCH BEREIK: temperatuurgebaseerde detectie (bijv. 35-40°C voor mensen)
  • Het beste voor: persoonsdetectie met thermische camera (bekende lichaamstemp.)
  • Beperking: vereist thermische camera, doeltemperatuur moet bekend zijn

MATCHED FILTER: matcht doelen via kleursignatuur uit monster
  • Het beste voor: specifieke bekende objecten wanneer u een doelmonster hebt
  • Beperking: vereist referentieafbeelding, niet voor onbekende doelen

MR MAP: multiresolutie-detectie voor objecten van wisselende grootte
  • Het beste voor: complexe scènes met onbekende doelgroottes
  • Beperking: langzamere verwerking, meer valse positieven

AI-PERSOONSDETECTOR: deep-learning model voor nauwkeurige persoonsdetectie
  • Het beste voor: SAR, het vinden van mensen in elke kleding/houding
  • Beperking: detecteert alleen personen, langzamere verwerking</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="344"/>
        <source>Select AOI Highlight Color</source>
        <translation>AOI-markeerkleur selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="358"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="376"/>
        <source>Select Directory</source>
        <translation>Map selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="393"/>
        <source>Select a Reference Image</source>
        <translation>Een referentie-afbeelding selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="395"/>
        <source>Images (*.png *.jpg)</source>
        <translation>Afbeeldingen (*.png *.jpg)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="443"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="475"/>
        <source>Value Adjusted</source>
        <translation>Waarde aangepast</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="445"/>
        <source>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</source>
        <translation>Het maximale gebied is aangepast naar {value} pixels om een geldig bereik te behouden.
(Minimumgebied moet kleiner zijn dan maximumgebied)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="477"/>
        <source>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</source>
        <translation>Het minimale gebied is aangepast naar {value} pixels om een geldig bereik te behouden.
(Maximumgebied moet groter zijn dan minimumgebied)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="591"/>
        <source>Please set the input and output directories.</source>
        <translation>Stel de invoer- en uitvoermappen in.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="598"/>
        <source>--- Starting image processing ---</source>
        <translation>--- Beeldverwerking starten ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="794"/>
        <source>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</source>
        <translation>Kan XML-bestand niet parseren. Controleer bestandspaden in &quot;{file_name}&quot;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="817"/>
        <source>Area of Interest Limit ({limit}) exceeded. Continue?</source>
        <translation>Limiet voor interessegebieden ({limit}) overschreden. Doorgaan?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="820"/>
        <source>Area of Interest Limit Exceeded</source>
        <translation>Limiet voor interessegebieden overschreden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="872"/>
        <source>--- Image Processing Completed ---</source>
        <translation>--- Beeldverwerking voltooid ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="873"/>
        <source>Image processing complete</source>
        <translation>Beeldverwerking voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="876"/>
        <source>{count} images with areas of interest identified</source>
        <translation>{count} afbeeldingen met interessegebieden geïdentificeerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="882"/>
        <source>No areas of interest identified</source>
        <translation>Geen interessegebieden geïdentificeerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="966"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1411"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1434"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1464"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1480"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1496"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1512"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="976"/>
        <source>Select File</source>
        <translation>Bestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="976"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>XML-bestanden (*.xml);;Alle bestanden (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="997"/>
        <source>Select Results Folder</source>
        <translation>Resultatenmap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1030"/>
        <source>Failed to scan folder: {error}</source>
        <translation>Map scannen mislukt: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1052"/>
        <source>No Results Found</source>
        <translation>Geen resultaten gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1053"/>
        <source>No ADIAT_DATA.XML files were found in the selected folder.</source>
        <translation>Er zijn geen ADIAT_DATA.XML-bestanden gevonden in de geselecteerde map.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1070"/>
        <source>Failed to display results: {error}</source>
        <translation>Kan resultaten niet weergeven: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1081"/>
        <source>Scan failed: {error}</source>
        <translation>Scannen mislukt: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1124"/>
        <source>Failed to open viewer: {error}</source>
        <translation>Kan viewer niet openen: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1153"/>
        <source>The selected file is not a valid XML file: {path}</source>
        <translation>Het geselecteerde bestand is geen geldig XML-bestand: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1357"/>
        <source>Error Loading Results</source>
        <translation>Fout bij laden van resultaten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1358"/>
        <source>Failed to load results file:
{error}</source>
        <translation>Kan resultatenbestand niet laden:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1412"/>
        <source>Failed to open Streaming Detector:
{error}</source>
        <translation>Kan streamingdetector niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1435"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Kan Vluchtviewer niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1465"/>
        <source>Failed to open Search Coordinator:
{error}</source>
        <translation>Kan zoekcoördinator niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1481"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Kan hulpdocumentatie niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1497"/>
        <source>Failed to open Community Help:
{error}</source>
        <translation>Kan communityhulp niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1513"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Kan YouTube-kanaal niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1588"/>
        <source> Open Search Coordinator</source>
        <translation> Zoekcoördinator openen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1590"/>
        <source>Open the Search Coordinator to review every batch in this run.</source>
        <translation>Open de Zoekcoördinator om elke batch in deze run te beoordelen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1596"/>
        <source>Open the Results Viewer to review detection results.</source>
        <translation>Open de resultatenviewer om detectieresultaten te beoordelen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1681"/>
        <source>Invalid Value</source>
        <translation>Ongeldige waarde</translation>
    </message>
</context>
<context>
    <name>MapDock</name>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="263"/>
        <source>Map</source>
        <translation>Kaart</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="360"/>
        <source>QtWebEngine not available — install PySide6-Addons for the interactive map. Showing list view instead.</source>
        <translation>QtWebEngine is niet beschikbaar — installeer PySide6-Addons voor de interactieve kaart. De lijstweergave wordt getoond.</translation>
    </message>
</context>
<context>
    <name>MapExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="34"/>
        <source>Map Export Options</source>
        <translation>Kaartexportopties</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="45"/>
        <source>Configure Map Export</source>
        <translation>Kaartexport configureren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="53"/>
        <source>Export Type</source>
        <translation>Exporttype</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="56"/>
        <source>KML File</source>
        <translation>KML-bestand</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="58"/>
        <source>Export to a KML file for use in Google Earth, etc.</source>
        <translation>Exporteren naar een KML-bestand voor gebruik in Google Earth, enz.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="60"/>
        <source>CalTopo</source>
        <translation>CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="61"/>
        <source>Export directly to a CalTopo map</source>
        <translation>Direct exporteren naar een CalTopo-kaart</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="73"/>
        <source>Data to Include</source>
        <translation>Op te nemen gegevens</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="76"/>
        <source>Drone/Image Locations</source>
        <translation>Drone-/afbeeldingslocaties</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="78"/>
        <source>Include markers for each drone image location</source>
        <translation>Markeringen voor elke drone-afbeeldingslocatie opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="80"/>
        <source>Flagged Areas of Interest</source>
        <translation>Gemarkeerde interessegebieden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="82"/>
        <source>Include markers for flagged AOIs</source>
        <translation>Markeringen voor gemarkeerde AOI&apos;s opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="84"/>
        <source>Coverage Area</source>
        <translation>Dekkingsgebied</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="86"/>
        <source>Include polygon(s) showing the geographic coverage extent</source>
        <translation>Polygonen opnemen die de geografische dekkingsomvang tonen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="88"/>
        <source>Include images without flagged AOIs</source>
        <translation>Afbeeldingen zonder gemarkeerde AOI&apos;s opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="90"/>
        <source>If unchecked, only export locations for images that have flagged AOIs</source>
        <translation>Indien uitgeschakeld, alleen locaties exporteren voor afbeeldingen die gemarkeerde AOI&apos;s hebben</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="101"/>
        <source>Probability of Detection (POD)</source>
        <translation>Detectiekans (POD)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="104"/>
        <source>POD coverage heatmap (terrain-aware)</source>
        <translation>POD-dekkingsheatmap (terreinbewust)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="107"/>
        <source>Compute a terrain and canopy aware probability-of-detection raster for the whole mission (all non-hidden images, independent of the selections above). KML exports embed the heatmap in the KML/KMZ as an image overlay; the GeoTIFF products (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) are also written — the GeoTIFF can be imported into CalTopo Map Sheets. May take several minutes.</source>
        <translation>Berekent een terrein- en bladerdakbewust detectiekans-raster voor de hele missie (alle niet-verborgen afbeeldingen, onafhankelijk van de selecties hierboven). KML-exports sluiten de heatmap als afbeeldingsoverlay in het KML/KMZ-bestand in; de GeoTIFF-producten (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) worden ook geschreven — de GeoTIFF kan in CalTopo Map Sheets worden geïmporteerd. Kan enkele minuten duren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="114"/>
        <source>Show on map when complete</source>
        <translation>Op kaart tonen na voltooiing</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="125"/>
        <source>CalTopo Options</source>
        <translation>CalTopo-opties</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="128"/>
        <source>Include Images</source>
        <translation>Afbeeldingen opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="130"/>
        <source>Upload photos to CalTopo markers (CalTopo only)</source>
        <translation>Foto&apos;s uploaden naar CalTopo-markeringen (alleen CalTopo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="150"/>
        <source>Export</source>
        <translation>Exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>MatchedFilter</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="42"/>
        <source>Add a new color signature for matched filter detection. Each color can have its own threshold value.</source>
        <translation>Een nieuwe kleurkenmerk toevoegen voor matched-filterdetectie. Elke kleur kan zijn eigen drempelwaarde hebben.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="45"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
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
        <translation>Opent het Bereikweergavevenster om:
- Het bereik van kleuren te zien dat tijdens de beeldanalyse wordt gezocht.
Gebruik dit om te zien welke kleuren worden gedetecteerd en om de drempels te optimaliseren vóór de verwerking.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="88"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
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
        <translation>Geen kleuren geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="299"/>
        <source>Please add at least one color to detect.</source>
        <translation>Voeg ten minste één kleur toe om te detecteren.</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilterWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Kleur toevoegen</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="47"/>
        <source>No Targets Selected</source>
        <translation>Geen doelen geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="57"/>
        <source>View Range</source>
        <translation>Bereik bekijken</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="218"/>
        <source>Please add at least one target color to detect.</source>
        <translation>Voeg ten minste één doelkleur toe om te detecteren.</translation>
    </message>
</context>
<context>
    <name>MeasureDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="71"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Distance</source>
        <translation>Afstand meten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="85"/>
        <source>Measure Shadow</source>
        <translation>Schaduw meten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="87"/>
        <source>When checked, the two clicks estimate the height of a vertical object from its shadow. Click the base of the object first, then the tip of its shadow.</source>
        <translation>Indien ingeschakeld schatten de twee klikken de hoogte van een verticaal object op basis van de schaduw. Klik eerst op de basis van het object en daarna op de punt van de schaduw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="94"/>
        <source>Ground Sample Distance</source>
        <translation>Grondbemonsteringsafstand</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="97"/>
        <source>GSD:</source>
        <translation>GSD:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="99"/>
        <source>Enter GSD value</source>
        <translation>Voer GSD-waarde in</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="103"/>
        <source>cm/px</source>
        <translation>cm/px</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="111"/>
        <source>Measurement</source>
        <translation>Meting</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="114"/>
        <source>Distance:</source>
        <translation>Afstand:</translation>
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
        <translation>Schatting hoogte uit schaduw</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="135"/>
        <source>Use Anyway</source>
        <translation>Toch gebruiken</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="137"/>
        <source>Force the estimate with the current base/tip clicks even though the drawn line doesn&apos;t match the expected shadow direction. Use only when you&apos;re confident the geometry is correct.</source>
        <translation>Forceer de schatting met de huidige basis-/puntklikken, ook al komt de getekende lijn niet overeen met de verwachte schaduwrichting. Gebruik dit alleen als u zeker weet dat de geometrie klopt.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="181"/>
        <source>Click the BASE of the object first, then the TIP of its shadow.</source>
        <translation>Klik eerst op de BASIS van het object en daarna op de PUNT van de schaduw.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="185"/>
        <source>Click on the image to place the first point,
then click again to place the second point.</source>
        <translation>Klik op de afbeelding om het eerste punt te plaatsen,
klik daarna nogmaals om het tweede punt te plaatsen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="158"/>
        <source>Clear</source>
        <translation>Wissen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="160"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Shadow Height</source>
        <translation>Hoogte uit schaduw meten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="415"/>
        <source>Image metadata unavailable</source>
        <translation>Afbeeldingsmetadata niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="553"/>
        <source>Rejected</source>
        <translation>Afgewezen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="577"/>
        <source>No GSD value</source>
        <translation>Geen GSD-waarde</translation>
    </message>
</context>
<context>
    <name>MediaSelector</name>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool (ADIAT)</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument (ADIAT)</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="31"/>
        <source>What would you like to do?</source>
        <translation>Wat wilt u doen?</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="86"/>
        <source>Image Analysis</source>
        <translation>Beeldanalyse</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="169"/>
        <source>Stream Analysis</source>
        <translation>Streamanalyse</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="246"/>
        <source>Pair with ADIAT Mobile drone controllers to receive their live camera feeds with detections.</source>
        <translation>Koppel met ADIAT Mobile-dronecontrollers om hun live camerafeeds met detecties te ontvangen.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="163"/>
        <source>RTMP, Video Files, HDMI Capture</source>
        <translation>RTMP, videobestanden, HDMI-opname</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="252"/>
        <source>Flight Viewer</source>
        <translation>Vluchtviewer</translation>
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
        <translation>Min. score</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="99"/>
        <source>0 detections</source>
        <translation>0 detecties</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="119"/>
        <source>Export</source>
        <translation>Exporteren</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="122"/>
        <source>Export filtered detections to the standard ADIAT image-mode gallery format.</source>
        <translation>Exporteer gefilterde detecties naar de standaard ADIAT-galerijindeling voor beeldmodus.</translation>
    </message>
</context>
<context>
    <name>MissionGalleryDock</name>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="28"/>
        <source>Mission Gallery</source>
        <translation>Missiegalerij</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="53"/>
        <source>All feeds</source>
        <translation>Alle feeds</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="59"/>
        <source>All detectors</source>
        <translation>Alle detectors</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="126"/>
        <source>0 detections</source>
        <translation>0 detecties</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="151"/>
        <source>{n} detections</source>
        <translation>{n} detecties</translation>
    </message>
</context>
<context>
    <name>PDFExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="151"/>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="160"/>
        <source>No Images to Export</source>
        <translation>Geen afbeeldingen om te exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="153"/>
        <source>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</source>
        <translation>Er zijn geen afbeeldingen beschikbaar om in het PDF-rapport op te nemen.

Mogelijk zijn alle afbeeldingen verborgen of bevat de dataset geen afbeeldingen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="162"/>
        <source>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</source>
        <translation>Er zijn geen afbeeldingen met gemarkeerde AOI&apos;s om in het PDF-rapport op te nemen.

Markeer ten minste één AOI of vink &apos;Afbeeldingen zonder gemarkeerde AOI&apos;s opnemen&apos; aan om alle afbeeldingen in het rapport op te nemen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="172"/>
        <source>Save PDF File</source>
        <translation>PDF-bestand opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="174"/>
        <source>PDF files (*.pdf)</source>
        <translation>PDF-bestanden (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="216"/>
        <source>Generating PDF Report</source>
        <translation>PDF-rapport genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="219"/>
        <source>Generating PDF Report...</source>
        <translation>PDF-rapport genereren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="260"/>
        <source>Failed to generate PDF file: {error}</source>
        <translation>Kan PDF-bestand niet genereren: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="276"/>
        <source>Success</source>
        <translation>Geslaagd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="277"/>
        <source>PDF report generated successfully!</source>
        <translation>PDF-rapport succesvol gegenereerd!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="294"/>
        <source>PDF generation failed: {error}</source>
        <translation>PDF-generatie mislukt: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="308"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
</context>
<context>
    <name>PDFExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="27"/>
        <source>PDF Export Settings</source>
        <translation>PDF-exportinstellingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="35"/>
        <source>Enter the following information for the PDF report:</source>
        <translation>Voer de volgende informatie in voor het PDF-rapport:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="44"/>
        <source>Enter organization name</source>
        <translation>Voer organisatienaam in</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="45"/>
        <source>Organization:</source>
        <translation>Organisatie:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="49"/>
        <source>Enter search name</source>
        <translation>Voer zoeknaam in</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="50"/>
        <source>Search Name:</source>
        <translation>Zoeknaam:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="55"/>
        <source>Export Options:</source>
        <translation>Exportopties:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="60"/>
        <source>Include images without flagged AOIs</source>
        <translation>Afbeeldingen zonder gemarkeerde AOI&apos;s opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="62"/>
        <source>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</source>
        <translation>Indien aangevinkt, worden alle afbeeldingen opgenomen in het PDF-rapport, ook als ze geen gemarkeerde AOI&apos;s hebben. Indien uitgevinkt, worden alleen afbeeldingen met gemarkeerde AOI&apos;s opgenomen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="69"/>
        <source>Map Tiles:</source>
        <translation>Kaarttegels:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="71"/>
        <source>Map</source>
        <translation>Kaart</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="72"/>
        <source>Satellite</source>
        <translation>Satelliet</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="73"/>
        <source>Choose the background tiles for the PDF overview map.</source>
        <translation>Kies de achtergrondtegels voor de PDF-overzichtskaart.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="80"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="82"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
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
        <translation>
  ... en nog {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="92"/>
        <source>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</source>
        <translation>{count} bronafbeelding(en) niet gevonden op verwachte locaties:

{files}

Selecteer de map die de bronafbeeldingen bevat.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="100"/>
        <source>Source Images Not Found</source>
        <translation>Bronafbeeldingen niet gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="111"/>
        <source>Select Source Images Folder</source>
        <translation>Map met bronafbeeldingen selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="143"/>
        <source>Some Images Still Missing</source>
        <translation>Sommige afbeeldingen ontbreken nog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="145"/>
        <source>Found {found} of {total} images.

Still missing:
{missing}</source>
        <translation>{found} van {total} afbeeldingen gevonden.

Nog ontbrekend:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="175"/>
        <source>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</source>
        <translation>{count} detectiemasker(s) niet gevonden op verwachte locaties:

{files}

Selecteer de map die de maskerbestanden bevat.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="183"/>
        <source>Detection Masks Not Found</source>
        <translation>Detectiemaskers niet gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="194"/>
        <source>Select Masks Folder</source>
        <translation>Maskermap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="226"/>
        <source>Some Masks Still Missing</source>
        <translation>Sommige maskers ontbreken nog</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="228"/>
        <source>Found {found} of {total} masks.

Still missing:
{missing}</source>
        <translation>{found} van {total} maskers gevonden.

Nog ontbrekend:
{missing}</translation>
    </message>
</context>
<context>
    <name>PersonReferenceDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="277"/>
        <source>Person Size Reference</source>
        <translation>Referentie voor persoonsgrootte</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="284"/>
        <source>Reference Person</source>
        <translation>Referentiepersoon</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="303"/>
        <source>Standing</source>
        <translation>Staand</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="305"/>
        <source>Lying down</source>
        <translation>Liggend</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="307"/>
        <source>Sitting</source>
        <translation>Zittend</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="316"/>
        <source>Show shadows (from capture time)</source>
        <translation>Schaduwen tonen (opnametijd)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="319"/>
        <source>Use terrain elevation (DEM)</source>
        <translation>Terreinhoogte gebruiken (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="328"/>
        <source>Rotate the person on the ground to line it up with an object</source>
        <translation>Draai de persoon op de grond om deze met een object uit te lijnen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="333"/>
        <source>Click to choose overlay color</source>
        <translation>Klik om de overlaykleur te kiezen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="341"/>
        <source>Size:</source>
        <translation>Grootte:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="342"/>
        <source>Show:</source>
        <translation>Tonen:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="343"/>
        <source>Rotation:</source>
        <translation>Rotatie:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="346"/>
        <source>Color:</source>
        <translation>Kleur:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="359"/>
        <source>Drag the white handle to position the reference person. Silhouettes are drawn at true ground scale for this image&apos;s altitude and camera angle.</source>
        <translation>Sleep de witte greep om de referentiepersoon te plaatsen. Silhouetten worden op ware terreinschaal getekend voor de hoogte en camerahoek van deze afbeelding.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="367"/>
        <source>Recenter</source>
        <translation>Centreren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="368"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="423"/>
        <source>Perspective overlay unavailable: this image is missing the altitude or lens metadata needed to project a person.</source>
        <translation>Perspectiefoverlay niet beschikbaar: deze afbeelding mist de hoogte- of lensmetadata die nodig zijn om een persoon te projecteren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="441"/>
        <source>no image loaded</source>
        <translation>geen afbeelding geladen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="446"/>
        <source>image metadata could not be read</source>
        <translation>afbeeldingsmetadata konden niet worden gelezen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="450"/>
        <source>image has no GPS coordinates</source>
        <translation>afbeelding heeft geen GPS-coördinaten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="462"/>
        <source>capture time / timezone not in metadata</source>
        <translation>opnametijd / tijdzone ontbreekt in metadata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="468"/>
        <source>sun position could not be computed</source>
        <translation>zonnestand kon niet worden berekend</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="477"/>
        <source>Sun at capture: {elev:.0f}° above horizon, azimuth {az:.0f}°.</source>
        <translation>Zon bij opname: {elev:.0f}° boven de horizon, azimut {az:.0f}°.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="482"/>
        <source>Capture time zone estimated from GPS location.</source>
        <translation>Tijdzone van opname geschat op basis van GPS-locatie.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="487"/>
        <source>the sun was below the horizon at capture</source>
        <translation>de zon stond tijdens de opname onder de horizon</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="489"/>
        <source>sun position unavailable</source>
        <translation>zonnestand niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="490"/>
        <source>Shadow unavailable: {reason}.</source>
        <translation>Schaduw niet beschikbaar: {reason}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="589"/>
        <source>Place the person and shadow on the DEM terrain surface</source>
        <translation>Plaats de persoon en schaduw op het DEM-terreinoppervlak</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="593"/>
        <source>Terrain (DEM) data is not available for this image</source>
        <translation>Terreingegevens (DEM) zijn niet beschikbaar voor deze afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="853"/>
        <source>Choose Overlay Color</source>
        <translation>Overlaykleur kiezen</translation>
    </message>
</context>
<context>
    <name>PlaybackControlBar</name>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="54"/>
        <source>Play/Pause (Space)</source>
        <translation>Afspelen/pauzeren (spatie)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="67"/>
        <source>Seek through video</source>
        <translation>Door video zoeken</translation>
    </message>
</context>
<context>
    <name>Preferences</name>
    <message>
        <location filename="../resources/views/Preferences.ui" line="14"/>
        <source>Preferences</source>
        <translation>Voorkeuren</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="55"/>
        <source>Select the application theme appearance.
Changes the overall color scheme and visual style.</source>
        <translation>Selecteer het uiterlijk van het applicatie-thema.
Wijzigt het algehele kleurenschema en de visuele stijl.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="59"/>
        <source>Theme:</source>
        <translation>Thema:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="71"/>
        <source>Choose the application theme:
• Light: Bright theme with light backgrounds and dark text
• Dark: Dark theme with dark backgrounds and light text
Changes apply immediately to all windows.</source>
        <translation>Kies het applicatie-thema:
• Licht: licht thema met lichte achtergronden en donkere tekst
• Donker: donker thema met donkere achtergronden en lichte tekst
Wijzigingen worden onmiddellijk toegepast op alle vensters.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="78"/>
        <source>Light</source>
        <translation>Licht</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="83"/>
        <source>Dark</source>
        <translation>Donker</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="114"/>
        <source>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</source>
        <translation>Waarschuwingsdrempel voor totaal aantal gedetecteerde AOI&apos;s over alle afbeeldingen.
Waarschuwt de gebruiker wanneer deze limiet tijdens de verwerking wordt bereikt.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="118"/>
        <source>Max Areas of Interest: </source>
        <translation>Max. interessegebieden: </translation>
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
        <translation>Stel de waarschuwingsdrempel in voor het totaal aantal AOI&apos;s dat tijdens de verwerking wordt gedetecteerd.
• Bereik: 0 tot 1000
• Standaard: 100
Wanneer dit aantal AOI&apos;s over alle afbeeldingen wordt gedetecteerd:
• De UI toont een waarschuwingsbericht
• De gebruiker kan de verwerking annuleren, instellingen aanpassen en opnieuw uitvoeren
• Als er geen actie wordt ondernomen, gaat de detectie automatisch verder
Gebruik lagere waarden om hoge detectie-aantallen vroeg te onderscheppen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="161"/>
        <source>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</source>
        <translation>Straal voor het samenvoegen van aangrenzende AOI&apos;s tot enkele detecties.
AOI&apos;s binnen deze afstand worden samengevoegd.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="165"/>
        <source>Area of Interest Circle Radius(px):</source>
        <translation>Cirkelstraal interessegebied (px):</translation>
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
        <translation>Stel de straal in voor het samenvoegen van nabije AOI&apos;s tijdens detectie.
• Bereik: 0 tot 100 pixels
• Standaard: 25 pixels
Wanneer AOI&apos;s binnen deze straal van elkaar liggen:
• Worden ze gecombineerd tot één AOI
• Het proces herhaalt zich totdat er geen buren binnen de straal overblijven
• Grotere waarden: combineren verder gelegen detecties (minder totale AOI&apos;s)
• Kleinere waarden: houden detecties gescheiden (meer individuele AOI&apos;s)
Gebruik om geclusterde detecties tot enkele objecten te consolideren.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="209"/>
        <source>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</source>
        <translation>Indeling voor het weergeven van geografische coördinaten in de applicatie.
Beïnvloedt hoe GPS-locaties in de viewer en exports worden getoond.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="213"/>
        <source>Coordinate System:</source>
        <translation>Coördinatensysteem:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="225"/>
        <source>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</source>
        <translation>Selecteer de weergave-indeling voor geografische coördinaten:
• Lat/Long - decimale graden: 34.123456, -118.987654 (meest gebruikelijk, makkelijk te gebruiken)
• Lat/Long - graden, minuten, seconden: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditionele navigatie)
• UTM: Universal Transverse Mercator-rastersysteem met zone, easting, northing (militair, landmeten)
Deze instelling beïnvloedt de coördinatenweergave in de viewer, exports en overlays.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="233"/>
        <source>Lat/Long - Decimal Degrees</source>
        <translation>Lat/Long - decimale graden</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="238"/>
        <source>Lat/Long - Degrees, Minutes, Seconds</source>
        <translation>Lat/Long - graden, minuten, seconden</translation>
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
        <translation>Eenheid voor het weergeven van temperatuurmetingen uit thermische beelden.
Gebruikt bij het analyseren van thermische afbeeldingen van thermische camera&apos;s.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="266"/>
        <source>Temperature Unit:</source>
        <translation>Temperatuureenheid:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="278"/>
        <source>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</source>
        <translation>Selecteer de temperatuureenheid voor thermische beeldanalyse:
• Fahrenheit (°F): imperiale temperatuurschaal (US-standaard)
  - Water bevriest bij 32°F, kookt bij 212°F
• Celsius (°C): metrische temperatuurschaal (internationale standaard)
  - Water bevriest bij 0°C, kookt bij 100°C
Geldt voor weergave van gegevens van thermische camera&apos;s en analyseresultaten.</translation>
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
        <translation>Eenheid voor het weergeven van afstands- en hoogtemetingen.
Gebruikt voor dronehoogte, objectafstanden en ruimtelijke berekeningen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="315"/>
        <source>Distance Unit:</source>
        <translation>Afstandseenheid:</translation>
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
        <translation>Selecteer de afstandseenheid voor metingen:
• Meter (m): metrische afstandseenheid (internationale standaard)
  - 1 meter = 3,281 voet
  - Gebruikt voor hoogte-, GSD- en afstandsberekeningen
• Voet (ft): imperiale afstandseenheid (US-standaard)
  - 1 voet = 0,3048 meter
  - Gebruikelijk in de Amerikaanse luchtvaart en landmeten
Geldt voor hoogteweergaven, GSD-berekeningen en afstandsmetingen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="338"/>
        <source>Meters</source>
        <translation>Meter</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="343"/>
        <source>Feet</source>
        <translation>Voet</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="362"/>
        <source>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</source>
        <translation>Modus Alleen offline in-/uitschakelen.
Indien ingeschakeld, slaat de app netwerkaanroepen over (kaarttegels, CalTopo-exports) en werkt alleen met gecachete gegevens.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="366"/>
        <source>Offline Only Mode:</source>
        <translation>Modus alleen offline:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="378"/>
        <source>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</source>
        <translation>Schakel onlinefunctionaliteit uit (tegeldownloads, CalTopo-integratie) en werk volledig offline.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="381"/>
        <location filename="../resources/views/Preferences.ui" line="422"/>
        <source>Enable</source>
        <translation>Inschakelen</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="399"/>
        <source>Use terrain elevation data (DEM/DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online or local elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</source>
        <translation>Gebruik terreinhoogtegegevens (DEM/DTM/DSM) voor nauwkeurigere berekeningen van AOI-GPS-coördinaten.
Indien ingeschakeld, worden online of lokale hoogtegegevens gebruikt om rekening te houden met terreinvariaties.
Indien uitgeschakeld, wordt vlak terrein op opstijghoogte aangenomen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="416"/>
        <source>Enable terrain-corrected AOI positioning using DEM/DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</source>
        <translation>Schakel terrein-gecorrigeerde AOI-positionering in met DEM-/DTM-/DSM-hoogtegegevens.
• Indien ingeschakeld: downloadt en cachet hoogtetegels voor nauwkeurige positionering
• Indien uitgeschakeld: gebruikt aanname van vlak terrein (sneller, werkt offline)
Terreingegevens worden lokaal in cache opgeslagen en werken offline na de eerste download.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="404"/>
        <source>Use Terrain Elevation:</source>
        <translation>Terreinhoogte gebruiken:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="440"/>
        <source>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</source>
        <translation>Beheer de cache van terreinhoogtegegevens.
Terreintegels worden lokaal gedownload en opgeslagen voor offlinegebruik.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="444"/>
        <source>Terrain Cache:</source>
        <translation>Terreincache:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="456"/>
        <source>0 tiles (0 MB)</source>
        <translation>0 tegels (0 MB)</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="481"/>
        <source>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Wis alle gecachete terreinhoogtetegels.
Hierdoor moeten tegels opnieuw worden gedownload wanneer terreinhoogte wordt gebruikt.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="485"/>
        <source>Clear Cache</source>
        <translation>Cache wissen</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="517"/>
        <source>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</source>
        <translation>Versie van het huidige configuratiebestand voor dronesensor.
Bevat cameraspecificaties, sensorafmetingen en gegevens over brandpuntsafstanden voor verschillende dronemodellen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="521"/>
        <source>Drone Sensor File Version:</source>
        <translation>Versie van dronesensorbestand:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="546"/>
        <source>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</source>
        <translation>Versienummer van het momenteel geladen dronesensorbestand.
Het sensorbestand definieert cameraparameters voor nauwkeurige GSD- en AOI-berekeningen.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="550"/>
        <source>TextLabel</source>
        <translation>TextLabel</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="578"/>
        <source>Replace the current drone sensor configuration file.
Allows updating to a newer version or custom sensor specifications.
Required file format: JSON with drone models, sensors, focal lengths, and dimensions.
Use this when:
• New drone models are available
• Sensor specifications need updating
• Custom camera configurations are needed
Backup existing file before replacing.</source>
        <translation>Vervang het huidige configuratiebestand voor dronesensor.
Maakt het mogelijk te updaten naar een nieuwere versie of aangepaste sensorspecificaties.
Vereist bestandsformaat: JSON met dronemodellen, sensoren, brandpuntsafstanden en afmetingen.
Gebruik dit wanneer:
• Nieuwe dronemodellen beschikbaar zijn
• Sensorspecificaties moeten worden bijgewerkt
• Aangepaste cameraconfiguraties nodig zijn
Maak een back-up van het bestaande bestand voordat u vervangt.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="588"/>
        <source>Replace</source>
        <translation>Vervangen</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="609"/>
        <source>Close the Preferences window.
All changes are saved automatically when modified.</source>
        <translation>Sluit het venster Voorkeuren.
Alle wijzigingen worden automatisch opgeslagen wanneer ze worden gewijzigd.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="69"/>
        <source>Language:</source>
        <translation>Taal:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="101"/>
        <source>AWS Terrain Tiles (online, ~30 m) is always available as the baseline; local USGS 3DEP adds 1 m detail where downloaded.</source>
        <translation>AWS Terrain Tiles (online, ~30 m) is altijd beschikbaar als basis; lokale USGS 3DEP voegt 1 m detail toe waar gedownload.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="109"/>
        <source>Elevation Source:</source>
        <translation>Hoogtebron:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="119"/>
        <location filename="../app/core/controllers/Preferences.py" line="204"/>
        <source>Manifest CSV:</source>
        <translation>Manifest-CSV:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="121"/>
        <source>Path to dem_manifest.csv</source>
        <translation>Pad naar dem_manifest.csv</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="122"/>
        <location filename="../app/core/controllers/Preferences.py" line="133"/>
        <location filename="../app/core/controllers/Preferences.py" line="207"/>
        <location filename="../app/core/controllers/Preferences.py" line="217"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="130"/>
        <location filename="../app/core/controllers/Preferences.py" line="214"/>
        <source>Tiles directory:</source>
        <translation>Tegelmap:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="132"/>
        <location filename="../app/core/controllers/Preferences.py" line="216"/>
        <source>Folder containing the GeoTIFF tiles</source>
        <translation>Map met de GeoTIFF-tegels</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="142"/>
        <location filename="../app/core/controllers/Preferences.py" line="378"/>
        <source>3DEP is inactive until both paths are set — the AWS Terrain Tiles baseline is used. Use Download tiles… or Browse.</source>
        <translation>3DEP is inactief totdat beide paden zijn ingesteld — de AWS Terrain Tiles-basis wordt gebruikt. Gebruik Tegels downloaden… of Bladeren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="174"/>
        <source>Terrain</source>
        <translation>Terrein</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="191"/>
        <source>Canopy Data Source</source>
        <translation>Bron kroongegevens</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="195"/>
        <source>Source:</source>
        <translation>Bron:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="206"/>
        <source>Path to the canopy manifest CSV</source>
        <translation>Pad naar de kroon-manifest-CSV</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="226"/>
        <location filename="../app/core/controllers/Preferences.py" line="451"/>
        <source>Canopy is disabled until both paths are set — use Download tiles… or Browse.</source>
        <translation>Kroon is uitgeschakeld totdat beide paden zijn ingesteld — gebruik Tegels downloaden… of Bladeren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="236"/>
        <source>Download tiles...</source>
        <translation>Tegels downloaden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="238"/>
        <source>Download DEM and/or canopy tiles for an area of interest and register them here. Note: the canopy download uses Meta/WRI data and registers it as the canopy source.</source>
        <translation>Download DEM- en/of kroontegels voor een interessegebied en registreer ze hier. Let op: de kroondownload gebruikt Meta/WRI-gegevens en registreert die als kroonbron.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="300"/>
        <location filename="../app/core/controllers/Preferences.py" line="644"/>
        <source>{version}_{date}</source>
        <translation>{version}_{date}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="384"/>
        <source>The registered 3DEP files no longer exist on disk — the AWS Terrain Tiles baseline is used. Re-download or fix the paths.</source>
        <translation>De geregistreerde 3DEP-bestanden bestaan niet meer op schijf — de AWS Terrain Tiles-basis wordt gebruikt. Download opnieuw of corrigeer de paden.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="416"/>
        <source>Select 3DEP manifest CSV</source>
        <translation>3DEP-manifest-CSV selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="418"/>
        <location filename="../app/core/controllers/Preferences.py" line="482"/>
        <source>CSV files (*.csv);;All files (*)</source>
        <translation>CSV-bestanden (*.csv);;Alle bestanden (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="428"/>
        <source>Select 3DEP tiles directory</source>
        <translation>Map met 3DEP-tegels selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="457"/>
        <source>The registered canopy files no longer exist on disk — canopy is disabled. Re-download or fix the paths.</source>
        <translation>De geregistreerde bladerdakbestanden bestaan niet meer op schijf — bladerdak is uitgeschakeld. Download opnieuw of corrigeer de paden.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="481"/>
        <source>Select canopy manifest CSV</source>
        <translation>Kroon-manifest-CSV selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="490"/>
        <source>Select canopy tiles directory</source>
        <translation>Map met kroontegels selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="501"/>
        <source>Download Tiles</source>
        <translation>Tegels downloaden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="502"/>
        <source>The tile downloader is unavailable:
{error}</source>
        <translation>De tegel-downloader is niet beschikbaar:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="575"/>
        <source>{tiles} tiles ({size_mb:.1f} MB)</source>
        <translation>{tiles} tegels ({size_mb:.1f} MB)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="567"/>
        <source>Not available</source>
        <translation>Niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="584"/>
        <source>N/A (local tiles)</source>
        <translation>N.v.t. (lokale tegels)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="587"/>
        <location filename="../app/core/controllers/Preferences.py" line="595"/>
        <location filename="../app/core/controllers/Preferences.py" line="623"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="596"/>
        <source>Terrain service not available.</source>
        <translation>Terreinservice niet beschikbaar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="602"/>
        <source>Clear Terrain Cache</source>
        <translation>Terreincache wissen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="604"/>
        <source>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Weet u zeker dat u alle gecachete terreinhoogtegegevens wilt wissen?

Hierdoor moeten tegels opnieuw worden gedownload wanneer terreinhoogte wordt gebruikt.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="617"/>
        <source>Cache Cleared</source>
        <translation>Cache gewist</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="618"/>
        <source>Cleared {count} cached terrain tiles.</source>
        <translation>{count} gecachete terreintegels gewist.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="624"/>
        <source>Failed to clear cache: {error}</source>
        <translation>Kan cache niet wissen: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="631"/>
        <source>Select a Drone Sensor File</source>
        <translation>Een dronesensorbestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="633"/>
        <source>CSV Files (*.csv)</source>
        <translation>CSV-bestanden (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="659"/>
        <source>Restart Required</source>
        <translation>Herstart vereist</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="660"/>
        <source>Please restart the application for language changes to take effect.</source>
        <translation>Start de applicatie opnieuw om taalwijzigingen door te voeren.</translation>
    </message>
</context>
<context>
    <name>QtImageViewer</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/QtImageViewer.py" line="384"/>
        <source>Open image</source>
        <translation>Afbeelding openen</translation>
    </message>
</context>
<context>
    <name>RXAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
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
        <translation>Aantal segmenten waarin elke afbeelding wordt verdeeld voor analyse.
Het RX-algoritme analyseert elk segment onafhankelijk om lokale afwijkingen te detecteren.
Prestatie-impact:
• Hoger aantal segmenten: VERHOOGT de verwerkingstijd (meer segmenten te analyseren)
• Lager aantal segmenten: VERLAAGT de verwerkingstijd (minder segmenten te analyseren)
• 1 segment: snelste verwerking (analyseert de hele afbeelding in één keer)
Meer segmenten verbeteren de detectie in afbeeldingen met variërende achtergronden.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Beeldsegmenten:</translation>
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
        <translation>Selecteer het aantal segmenten waarin elke afbeelding wordt verdeeld.
• Opties: 1, 2, 4, 6, 9, 16, 25, 36 segmenten
• Standaard: 1 (analyseer de hele afbeelding als één segment)
Het RX-afwijkingsalgoritme gebruikt statistische analyse om ongewone pixels te detecteren:
• 1 segment: analyseert de hele afbeelding tegelijk (het beste voor kleine afbeeldingen)
• Meer segmenten: analyseert lokale gebieden onafhankelijk (beter voor grote afbeeldingen)
Meer segmenten verbeteren de detectie in afbeeldingen met variërende achtergronden.
Aanbevolen: 4-9 segmenten voor typische dronebeelden.</translation>
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
        <translation>Detectiegevoeligheid voor afwijkingsdetectie.
• Bereik: 1 tot 10
• Standaard: 5
Bepaalt hoe statistisch verschillend een pixel moet zijn van de achtergrond om te worden gedetecteerd:
• Lagere waarden (1-3): VERMINDEREN detecties - minder gevoelig, detecteert alleen sterke afwijkingen
• Hogere waarden (7-10): VERHOGEN detecties - gevoeliger, detecteert subtiele afwijkingen
Hogere gevoeligheid vindt meer potentiële doelen, maar kan ruis/valse positieven bevatten.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="146"/>
        <source>Sensitivity:</source>
        <translation>Gevoeligheid:</translation>
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
        <translation>Pas de detectiegevoeligheid voor afwijkingsdetectie aan.
• Bereik: 1 tot 10
• Standaard: 5
Het RX-algoritme gebruikt statistische analyse om pixels te vinden die afwijken van de achtergrond:
• Lagere waarden (1-3): minder gevoelig, detecteert alleen sterke afwijkingen (minder valse positieven)
• Gemiddelde waarden (4-6): gebalanceerde detectie (aanbevolen voor de meeste gevallen)
• Hogere waarden (7-10): gevoeliger, detecteert subtiele afwijkingen (meer detecties, kan ruis bevatten)
Afwijkingen zijn pixels die statistisch verschillen van de omringende achtergrond.
Gebruik lagere gevoeligheid voor schone afbeeldingen, hogere voor het vinden van subtiele doelen.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="205"/>
        <source>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</source>
        <translation>Huidig gevoeligheidsniveau voor afwijkingsdetectie.
Toont de waarde die is geselecteerd op de gevoeligheidsschuifregelaar (1-10).</translation>
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
        <translation>Bevatten uw afbeeldingen complexe scènes met gebouwen, voertuigen of gemengde door mensen gemaakte bedekking?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="49"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="64"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="100"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Hoe agressief moet ADIAT naar afwijkingen zoeken?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="113"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Opmerking: een hogere instelling vindt meer potentiële afwijkingen, maar kan ook het aantal valse positieven vergroten.</translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="50"/>
        <source>Very 
Conservative</source>
        <translation>Zeer 
conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="51"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="52"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="53"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="54"/>
        <source>Very 
Aggressive</source>
        <translation>Zeer 
agressief</translation>
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
        <translation>&lt;br&gt;&lt;b&gt;Drempel:&lt;/b&gt; {value}</translation>
    </message>
</context>
<context>
    <name>RecentColorsDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="151"/>
        <source>Recent Colors</source>
        <translation>Recente kleuren</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="162"/>
        <source>Select a recently used color:</source>
        <translation>Selecteer een recent gebruikte kleur:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="178"/>
        <source>No recent colors found</source>
        <translation>Geen recente kleuren gevonden</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="204"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
<context>
    <name>RenderingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="44"/>
        <source>Shape Options</source>
        <translation>Vormopties</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="47"/>
        <source>Shape Mode:</source>
        <translation>Vormmodus:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="49"/>
        <source>Box</source>
        <translation>Rechthoek</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="50"/>
        <source>Circle</source>
        <translation>Cirkel</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="51"/>
        <source>Dot</source>
        <translation>Stip</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="52"/>
        <source>Off</source>
        <translation>Uit</translation>
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
        <translation>Vorm om rond detecties te tekenen:

• Vak: rechthoek rond het begrenzingsvak van de detectie.
  Gebruik voor: nauwkeurige grenzen, technische visualisatie.

• Cirkel: cirkel die de detectie omvat (150% van de contourstraal).
  Gebruik voor: algemeen gebruik, schonere uitstraling (standaard).

• Stip: kleine stip in het zwaartepunt van de detectie.
  Gebruik voor: minimale overlay, snel renderen.

• Uit: geen vormoverlay (alleen miniaturen/tekst indien ingeschakeld).
  Gebruik voor: schone video met minimale overlays.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="70"/>
        <source>Visual Options</source>
        <translation>Visuele opties</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="73"/>
        <source>Show Text Labels (slower)</source>
        <translation>Tekstlabels tonen (langzamer)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="75"/>
        <source>Displays text labels near detections showing detection information.
Adds ~5-15ms processing overhead depending on detection count.
Labels show: detection type, confidence, area.
Recommended: OFF for speed, ON for debugging/analysis.</source>
        <translation>Geeft tekstlabels weer naast detecties met detectie-informatie.
Voegt ~5-15ms verwerkingsoverhead toe afhankelijk van het aantal detecties.
Labels tonen: detectietype, betrouwbaarheid, gebied.
Aanbevolen: UIT voor snelheid, AAN voor debugging/analyse.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="82"/>
        <source>Show Contours (slowest)</source>
        <translation>Contouren tonen (langzaamst)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="84"/>
        <source>Draws exact detection contours (pixel-precise boundaries).
Adds ~10-20ms processing overhead (very expensive).
Shows exact shape detected by algorithm.
Recommended: OFF for speed, ON only for detailed analysis.</source>
        <translation>Tekent exacte detectiecontouren (pixel-nauwkeurige grenzen).
Voegt ~10-20ms verwerkingsoverhead toe (zeer duur).
Toont exacte vorm zoals gedetecteerd door het algoritme.
Aanbevolen: UIT voor snelheid, AAN alleen voor gedetailleerde analyse.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="92"/>
        <source>Use Detection Color (hue @ 100% sat/val for color anomalies)</source>
        <translation>Detectiekleur gebruiken (tint bij 100% verz./waarde voor kleurafwijkingen)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="95"/>
        <source>Color the detection overlay based on detected color.
For color anomalies: Uses the detected hue at 100% saturation/value.
For motion detections: Uses default color (green/blue).
Helps visually identify what color was detected.
Recommended: ON for color detection, OFF for motion-only.</source>
        <translation>Kleur de detectie-overlay op basis van de gedetecteerde kleur.
Voor kleurafwijkingen: gebruikt de gedetecteerde tint bij 100% verzadiging/waarde.
Voor bewegingsdetecties: gebruikt de standaardkleur (groen/blauw).
Helpt visueel te identificeren welke kleur is gedetecteerd.
Aanbevolen: AAN voor kleurdetectie, UIT voor alleen beweging.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="106"/>
        <source>Performance Limits</source>
        <translation>Prestatielimieten</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="109"/>
        <source>Max Detections:</source>
        <translation>Max. detecties:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="115"/>
        <source>Maximum number of detections to render on screen (0-1000).
Prevents rendering slowdown when hundreds of detections occur.
Shows highest confidence detections first.
0 = Unlimited (may cause lag with many detections).
Recommended: 10 for general use, 50 for complex rendering (text+contours).</source>
        <translation>Maximaal aantal detecties om op het scherm te renderen (0-1000).
Voorkomt vertraging in renderen wanneer honderden detecties plaatsvinden.
Toont eerst detecties met de hoogste betrouwbaarheid.
0 = onbeperkt (kan vertraging veroorzaken bij veel detecties).
Aanbevolen: 10 voor algemeen gebruik, 50 voor complex renderen (tekst+contouren).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="126"/>
        <source>Temporal Voting</source>
        <translation>Temporeel stemmen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="129"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Temporeel stemmen inschakelen (flikker verminderen)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="132"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Verzacht detecties over frames met temporele consistentie.
Detecties moeten verschijnen in N van M opeenvolgende frames om te worden bevestigd.
Vermindert flikkerende valse positieven aanzienlijk.
Aanbevolen: AAN voor alle gebruikssituaties (standaard).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="142"/>
        <source>Window Frames (M):</source>
        <translation>Vensterframes (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="147"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Grootte van temporeel stemvenster (2-30 frames).
Detecties moeten verschijnen in N van M opeenvolgende frames.
Grotere waarden = langer geheugen, stabieler, langzamere reactie op nieuwe objecten.
Kleinere waarden = korter geheugen, snellere reactie, minder stabiel.
Aanbevolen: 5 voor 30fps (~167ms venster), 7 voor 60fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="155"/>
        <source>Threshold (N of M):</source>
        <translation>Drempel (N van M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="160"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be ≤ Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Aantal frames binnen het venster waarin detectie moet verschijnen (N van M).
Hogere waarden = strenger, filtert vluchtige valse positieven.
Lagere waarden = toleranter, snellere reactie op nieuwe objecten.
Moet ≤ vensterframes zijn.
Aanbevolen: 3 van 5 (detectie in 60% van de frames).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="173"/>
        <source>Detection Cleanup</source>
        <translation>Detectie-opschoning</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="177"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Filtering van beeldverhouding inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="180"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filter zeer dunne of uitgerekte detecties uit op basis van breedte/hoogte.
Nuttig voor het verwijderen van draden, lange schaduwen of andere niet-object-vormen.
De meeste gebruikers kunnen dit UIT laten, tenzij u veel lange, smalle valse detecties ziet.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="189"/>
        <source>Min Ratio:</source>
        <translation>Min. verhouding:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="195"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 ≈ reject if height is more than 5× width.</source>
        <translation>Minimale breedte/hoogte-verhouding om te behouden (0,1-10,0).
Lagere waarden = sta hogere, dunnere detecties toe.
Hogere waarden = vereisen vierkanter detecties.
Voorbeeld: 0,2 ≈ wijs af als hoogte meer dan 5× breedte is.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="202"/>
        <source>Max Ratio:</source>
        <translation>Max. verhouding:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="208"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Maximale breedte/hoogte-verhouding om te behouden (0,1-20,0).
Lagere waarden = wijs zeer brede, dunne detecties af.
Hogere waarden = sta bredere objecten toe zoals voertuigen of lange uitrusting.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="217"/>
        <source>Detection Clustering</source>
        <translation>Detectieclustering</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="220"/>
        <source>Enable Detection Clustering</source>
        <translation>Detectieclustering inschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="223"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Voeg desgewenst nabije detecties samen tot één grotere detectie.
Nuttig wanneer één object verschijnt als vele kleine aangrenzende detecties.
De meeste gebruikers kunnen dit UIT laten, tenzij objecten gefragmenteerd lijken.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="232"/>
        <source>Clustering Distance (px):</source>
        <translation>Clusterafstand (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="237"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Maximale afstand tussen detectiemiddens om ze samen te voegen (0-500 pixels).
Lagere waarden = voeg alleen zeer nabije detecties samen.
Hogere waarden = voeg verder uit elkaar liggende detecties samen (kan oversamenvoegen).</translation>
    </message>
</context>
<context>
    <name>ResultsFolderDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="115"/>
        <source>Load Results Folder</source>
        <translation>Resultatenmap laden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="124"/>
        <source>Found {count} result(s)</source>
        <translation>{count} resultaten gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Folder</source>
        <translation>Map</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Algorithm</source>
        <translation>Algoritme</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Images</source>
        <translation>Afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Missing</source>
        <translation>Ontbrekend</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>AOIs</source>
        <translation>AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Map</source>
        <translation>Kaart</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>View</source>
        <translation>Weergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="170"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="216"/>
        <source>Open in Google Maps</source>
        <translation>Openen in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="226"/>
        <source>No images available - cannot get GPS location</source>
        <translation>Geen afbeeldingen beschikbaar - kan GPS-locatie niet ophalen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="228"/>
        <source>No GPS coordinates found in images</source>
        <translation>Geen GPS-coördinaten gevonden in afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="248"/>
        <source>Open in Results Viewer</source>
        <translation>Openen in resultatenviewer</translation>
    </message>
</context>
<context>
    <name>ResultsLoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="29"/>
        <source>Loading Results</source>
        <translation>Resultaten laden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="43"/>
        <source>Opening results...</source>
        <translation>Resultaten openen...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="55"/>
        <source>Preparing...</source>
        <translation>Voorbereiden...</translation>
    </message>
</context>
<context>
    <name>ReviewOrNewPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="70"/>
        <source>No file selected</source>
        <translation>Geen bestand geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="114"/>
        <source>Select ADIAT Results File</source>
        <translation>ADIAT-resultatenbestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>XML-bestanden (*.xml);;Alle bestanden (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="126"/>
        <source>File Name Warning</source>
        <translation>Waarschuwing bestandsnaam</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="128"/>
        <source>The selected file does not appear to be an ADIAT_Data.xml result or an ADIAT_Search project file.

Do you want to continue with this file?</source>
        <translation>Het geselecteerde bestand lijkt geen ADIAT_Data.xml-resultaat of ADIAT_Search-projectbestand te zijn.

Wilt u doorgaan met dit bestand?</translation>
    </message>
</context>
<context>
    <name>ReviewerNameDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="25"/>
        <source>Reviewer Name</source>
        <translation>Beoordelaarsnaam</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="45"/>
        <source>Review Tracking</source>
        <translation>Beoordelingstracering</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="51"/>
        <source>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</source>
        <translation>Voer uw naam in om uw beoordelingsactiviteit te volgen.
Dit helpt bij de coördinatie van beoordelingen door meerdere beoordelaars.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="60"/>
        <source>Your Name:</source>
        <translation>Uw naam:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="64"/>
        <source>Enter your name</source>
        <translation>Voer uw naam in</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="65"/>
        <source>Enter your full name or identifier for review tracking</source>
        <translation>Voer uw volledige naam of identificatie in voor beoordelingstracering</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="71"/>
        <source>Remember my name</source>
        <translation>Mijn naam onthouden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="74"/>
        <source>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</source>
        <translation>Sla uw naam op voor toekomstige beoordelingssessies.
U kunt deze later wijzigen in Voorkeuren of door op de beoordelaarsnaam in de viewer te klikken.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="86"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="91"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="123"/>
        <source>Name Required</source>
        <translation>Naam vereist</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="124"/>
        <source>Please enter your name to continue.</source>
        <translation>Voer uw naam in om door te gaan.</translation>
    </message>
</context>
<context>
    <name>ScanProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="51"/>
        <source>Scanning for Results</source>
        <translation>Resultaten scannen</translation>
    </message>
</context>
<context>
    <name>SimilarityGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="172"/>
        <source>Reference</source>
        <translation>Referentie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="181"/>
        <source>Unknown</source>
        <translation>Onbekend</translation>
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
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="44"/>
        <source>GPS Coordinates</source>
        <translation>GPS-coördinaten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="45"/>
        <source>Relative Altitude</source>
        <translation>Relatieve hoogte</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="46"/>
        <source>Gimbal Orientation</source>
        <translation>Gimbal-oriëntatie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="47"/>
        <source>Estimated Average GSD</source>
        <translation>Geschatte gemiddelde GSD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="48"/>
        <source>Temperature</source>
        <translation>Temperatuur</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="49"/>
        <source>Color Values</source>
        <translation>Kleurwaarden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="50"/>
        <source>Drone Orientation</source>
        <translation>Drone-oriëntatie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="51"/>
        <source>Grid Review</source>
        <translation>Rasterbeoordeling</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="116"/>
        <source>Error Loading Images</source>
        <translation>Fout bij laden van afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="122"/>
        <source>No active images available.</source>
        <translation>Geen actieve afbeeldingen beschikbaar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="126"/>
        <source>No other images available.</source>
        <translation>Geen andere afbeeldingen beschikbaar.</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="90"/>
        <source>Are you primarily looking for a person?</source>
        <translation>Zoekt u voornamelijk naar een persoon?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="156"/>
        <source>Do you know a distinctive target color?</source>
        <translation>Kent u een onderscheidende doelkleur?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Kleurdetectie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Kleurafwijkings- &amp; bewegingsdetectie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>AI-persoonsdetector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="186"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Geselecteerd algoritme: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="191"/>
        <source>{result}
Secondary Recommendation: {secondary}</source>
        <translation>{result}
Secundaire aanbeveling: {secondary}</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Kleurdetectie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Kleurafwijkings- &amp; bewegingsdetectie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>AI-persoonsdetector</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="190"/>
        <source>Algorithm</source>
        <translation>Algoritme</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="192"/>
        <source>{algorithm} Parameters</source>
        <translation>{algorithm}-parameters</translation>
    </message>
</context>
<context>
    <name>StreamConnectionPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="92"/>
        <source>Click Scan to find devices...</source>
        <translation>Klik op Scannen om apparaten te vinden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="108"/>
        <source>480p</source>
        <translation>480p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="109"/>
        <source>720p</source>
        <translation>720p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="110"/>
        <source>1080p</source>
        <translation>1080p</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="111"/>
        <source>4K</source>
        <translation>4K</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="266"/>
        <source>Choose the video file you want to analyze. Use Browse to pick a file from disk.</source>
        <translation>Kies het videobestand dat u wilt analyseren. Gebruik Bladeren om een bestand van schijf te kiezen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="268"/>
        <source>Video File:</source>
        <translation>Videobestand:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="269"/>
        <source>Click Browse to select a video file...</source>
        <translation>Klik op Bladeren om een videobestand te selecteren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="275"/>
        <source>Click Scan to detect available capture devices, then select one from the dropdown.</source>
        <translation>Klik op Scannen om beschikbare opnameapparaten te detecteren en selecteer er een uit de keuzelijst.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="277"/>
        <source>Device:</source>
        <translation>Apparaat:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="278"/>
        <source></source>
        <translation></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="284"/>
        <source>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</source>
        <translation>Voer de RTMP-URL in die door uw streamingserver wordt verstrekt (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="286"/>
        <source>Stream URL:</source>
        <translation>Stream-URL:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="287"/>
        <source>rtmp://server:port/app/streamKey</source>
        <translation>rtmp://server:port/app/streamKey</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="298"/>
        <source>OpenCV not available</source>
        <translation>OpenCV niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="304"/>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="307"/>
        <source>Scanning...</source>
        <translation>Scannen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="331"/>
        <source>Scan</source>
        <translation>Scannen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="337"/>
        <source>No capture devices found</source>
        <translation>Geen opnameapparaten gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="344"/>
        <source>Device {index} ({backend})</source>
        <translation>Apparaat {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="383"/>
        <source>Select Video File</source>
        <translation>Videobestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="386"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</source>
        <translation>Videobestanden (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;Alle bestanden (*)</translation>
    </message>
</context>
<context>
    <name>StreamControlWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="827"/>
        <source>Stream Connection</source>
        <translation>Streamverbinding</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="829"/>
        <source>Configure and connect to video source (file, HDMI capture, or RTMP stream)</source>
        <translation>Videobron configureren en verbinden (bestand, HDMI-opname of RTMP-stream)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="834"/>
        <source>Stream Type:</source>
        <translation>Streamtype:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="836"/>
        <source>File</source>
        <translation>Bestand</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="837"/>
        <source>HDMI Capture</source>
        <translation>HDMI-opname</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="838"/>
        <source>RTMP Stream</source>
        <translation>RTMP-stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="841"/>
        <source>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</source>
        <translation>Selecteer het type videobron:
• Bestand: vooraf opgenomen videobestand met tijdlijnbediening
• HDMI-opname: live-opname van HDMI-opnameapparaat
• RTMP-stream: realtime streamen vanaf RTMP/HTTP-bron</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="850"/>
        <source>Stream URL/Path:</source>
        <translation>Stream-URL/-pad:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="857"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1056"/>
        <source>Click to browse for video file...</source>
        <translation>Klik om naar videobestand te bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="861"/>
        <source>Enter or browse for the video source:
• File: Click to browse for video file (MP4, AVI, MOV, etc.)
• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)</source>
        <translation>Voer de videobron in of blader ernaar:
• Bestand: klik om naar een videobestand te bladeren (MP4, AVI, MOV, enz.)
• RTMP-stream: voer RTMP-URL in (rtmp://server:port/app/stream)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="870"/>
        <source>Select HDMI capture device</source>
        <translation>HDMI-opnameapparaat selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="872"/>
        <source>Scanning for devices...</source>
        <translation>Apparaten scannen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="876"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1008"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="880"/>
        <source>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</source>
        <translation>Open de bestandsbrowser om een videobestand voor analyse te selecteren.
Ondersteunde formaten: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="887"/>
        <source>Scan...</source>
        <translation>Scannen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="889"/>
        <source>Scan for available HDMI capture devices</source>
        <translation>Scannen op beschikbare HDMI-opnameapparaten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="896"/>
        <source>Connect</source>
        <translation>Verbinden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="899"/>
        <source>Connect to the specified video source and begin processing.</source>
        <translation>Verbind met de opgegeven videobron en start de verwerking.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="901"/>
        <source>Disconnect</source>
        <translation>Verbinding verbreken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="905"/>
        <source>Disconnect from the current video source and stop processing.</source>
        <translation>Verbreek de verbinding met de huidige videobron en stop de verwerking.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="912"/>
        <source>Status: Disconnected</source>
        <translation>Status: verbinding verbroken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="914"/>
        <source>Current connection status</source>
        <translation>Huidige verbindingsstatus</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="917"/>
        <source>Performance</source>
        <translation>Prestaties</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="918"/>
        <source>Real-time performance metrics</source>
        <translation>Realtime prestatiemetingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="922"/>
        <source>Video: --</source>
        <translation>Video: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="923"/>
        <source>Original video resolution</source>
        <translation>Oorspronkelijke videoresolutie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="924"/>
        <source>Processing: --</source>
        <translation>Verwerking: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="926"/>
        <source>Resolution used for detection processing</source>
        <translation>Resolutie gebruikt voor detectieverwerking</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="930"/>
        <source>Source FPS: --</source>
        <translation>Bron-FPS: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="931"/>
        <source>Source frame rate and the applied processing cadence</source>
        <translation>Bron-framerate en het toegepaste verwerkingsritme</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="932"/>
        <source>Proc FPS: --</source>
        <translation>Verw.-FPS: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="934"/>
        <source>Actual frames per second being processed</source>
        <translation>Werkelijk verwerkte frames per seconde</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="938"/>
        <source>Time: -- ms</source>
        <translation>Tijd: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="940"/>
        <source>Time in milliseconds to process each frame</source>
        <translation>Tijd in milliseconden om elk frame te verwerken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="942"/>
        <source>Latency: -- ms</source>
        <translation>Latentie: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="944"/>
        <source>End-to-end latency from frame capture to display</source>
        <translation>End-to-end-latentie van frame-opname tot weergave</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="948"/>
        <source>Frames: --</source>
        <translation>Frames: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="949"/>
        <source>Total number of frames processed</source>
        <translation>Totaal aantal verwerkte frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="950"/>
        <source>Detections: --</source>
        <translation>Detecties: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="951"/>
        <source>Number of detections in current frame</source>
        <translation>Aantal detecties in het huidige frame</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="965"/>
        <source>Recording</source>
        <translation>Opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="970"/>
        <source>Start Recording</source>
        <translation>Opname starten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="973"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Start opname van de videostream met detectie-overlays.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="975"/>
        <source>Stop Recording</source>
        <translation>Opname stoppen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="978"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Stop de huidige opname en sla op in een bestand.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="985"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1173"/>
        <source>Status: Not Recording</source>
        <translation>Status: niet aan het opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="988"/>
        <source>Current recording status and output file path</source>
        <translation>Huidige opnamestatus en pad naar uitvoerbestand</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="992"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1180"/>
        <source>Duration: --</source>
        <translation>Duur: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="994"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Opnamestatistieken: duur, FPS, frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1003"/>
        <source>Save to:</source>
        <translation>Opslaan naar:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1006"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Map waarin video-opnamen worden opgeslagen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1010"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Kies een map om opnamen op te slaan.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1064"/>
        <source>rtmp://server:port/app/stream</source>
        <translation>rtmp://server:port/app/stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1081"/>
        <source>Invalid Device</source>
        <translation>Ongeldig apparaat</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1082"/>
        <source>Please select a valid HDMI capture device.</source>
        <translation>Selecteer een geldig HDMI-opnameapparaat.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1094"/>
        <source>Invalid URL</source>
        <translation>Ongeldige URL</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1095"/>
        <source>Please enter a valid stream URL.</source>
        <translation>Voer een geldige stream-URL in.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1112"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1125"/>
        <source>Status: {message}</source>
        <translation>Status: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1161"/>
        <source>Status: Recording</source>
        <translation>Status: opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1165"/>
        <source>Output: {value}</source>
        <translation>Uitvoer: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1177"/>
        <source>Duration: {value}</source>
        <translation>Duur: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1206"/>
        <source>Select Recording Directory</source>
        <translation>Opnamemap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1217"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1220"/>
        <source>Scanning...</source>
        <translation>Scannen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1244"/>
        <source>Scan</source>
        <translation>Scannen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1250"/>
        <source>No capture devices found</source>
        <translation>Geen opnameapparaten gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1257"/>
        <source>Device {index} ({backend})</source>
        <translation>Apparaat {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1287"/>
        <source>Video: {width}x{height}</source>
        <translation>Video: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1294"/>
        <source>Processing: {width}x{height}</source>
        <translation>Verwerking: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1310"/>
        <source>Source FPS: {source:.1f} (Applied {applied:.1f})</source>
        <translation>Bron-FPS: {source:.1f} (toegepast {applied:.1f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1317"/>
        <source>Source FPS: {fps:.1f}</source>
        <translation>Bron-FPS: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1320"/>
        <source>Proc FPS: {fps:.1f}</source>
        <translation>Verw.-FPS: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1328"/>
        <source>Time: {time:.1f} ms</source>
        <translation>Tijd: {time:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1331"/>
        <source>Latency: {latency:.1f} ms</source>
        <translation>Latentie: {latency:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1339"/>
        <source>Frames: {count}</source>
        <translation>Frames: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1342"/>
        <source>Detections: {count}</source>
        <translation>Detecties: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1349"/>
        <source>Select Video File</source>
        <translation>Videobestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1352"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</source>
        <translation>Videobestanden (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;Alle bestanden (*)</translation>
    </message>
</context>
<context>
    <name>StreamImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="66"/>
        <source>Select Drone/Camera</source>
        <translation>Drone/camera selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="70"/>
        <source>No drones available</source>
        <translation>Geen drones beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="112"/>
        <source>Other</source>
        <translation>Overig</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="148"/>
        <source>Error loading drone data</source>
        <translation>Fout bij laden van dronegegevens</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="222"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Ongeldige cameragegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="423"/>
        <source>{sensor_name}: Sensor dimensions not available</source>
        <translation>{sensor_name}: sensorafmetingen niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="430"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Ontbrekende cameragegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="431"/>
        <source>Unable to calculate GSD. Sensor dimensions are required.</source>
        <translation>Kan GSD niet berekenen. Sensorafmetingen zijn vereist.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="437"/>
        <source>-- (Error)</source>
        <translation>-- (Fout)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="468"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="470"/>
        <source>Primary</source>
        <translation>Primair</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="472"/>
        <source>Sensor</source>
        <translation>Sensor</translation>
    </message>
</context>
<context>
    <name>StreamTargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Hoed, helm, plastic zak</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Kat, dagrugzak</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Grote rugzak, middelgrote hond</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Slaapzak, grote hond</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Kleine boot, 2-persoonstent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Auto/SUV, kleine pick-up, grote tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Huis</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Meer voorbeelden:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>m²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>ft²</translation>
    </message>
</context>
<context>
    <name>StreamViewerWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="102"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument v{version} - Gesponsord door TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="214"/>
        <source>Live View</source>
        <translation>Live-weergave</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="219"/>
        <source>Gallery</source>
        <translation>Galerij</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="260"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="261"/>
        <source>Streaming Analysis Wizard</source>
        <translation>Streaminganalyse-wizard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="262"/>
        <source>Image Analysis</source>
        <translation>Beeldanalyse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="263"/>
        <source>Flight Viewer</source>
        <translation>Vluchtviewer</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="264"/>
        <source>Preferences</source>
        <translation>Voorkeuren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="274"/>
        <source>Help</source>
        <translation>Hulp</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="275"/>
        <source>Check for Updates</source>
        <translation>Controleren op updates</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="276"/>
        <source>Manual</source>
        <translation>Handleiding</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="277"/>
        <source>Community Forum</source>
        <translation>Communityforum</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="278"/>
        <source>YouTube Channel</source>
        <translation>YouTube-kanaal</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="305"/>
        <source>Start Recording</source>
        <translation>Opname starten</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="308"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Start opname van de videostream met detectie-overlays.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="310"/>
        <source>Stop Recording</source>
        <translation>Opname stoppen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="313"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Stop de huidige opname en sla op in een bestand.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="320"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1881"/>
        <source>Status: Not Recording</source>
        <translation>Status: niet aan het opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="323"/>
        <source>Current recording status and output file path</source>
        <translation>Huidige opnamestatus en pad naar uitvoerbestand</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="327"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1883"/>
        <source>Duration: --</source>
        <translation>Duur: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="329"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Opnamestatistieken: duur, FPS, frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="334"/>
        <source>Save to:</source>
        <translation>Opslaan naar:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="338"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Map waarin video-opnamen worden opgeslagen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="340"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="342"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Kies een map om opnamen op te slaan.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="393"/>
        <source>Select Recording Directory</source>
        <translation>Opnamemap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="413"/>
        <source>Algorithm:</source>
        <translation>Algoritme:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="415"/>
        <source>Select which streaming detection algorithm to use</source>
        <translation>Selecteer welk streamingdetectie-algoritme moet worden gebruikt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="421"/>
        <source>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</source>
        <translation>Kies welk streamingdetectie-algoritme moet worden uitgevoerd.
• Kleurafwijkings- &amp; bewegingsdetectie: gefuseerde afwijkingsdetectoren
• Kleurdetectie: kleurgebaseerde markering</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="456"/>
        <source>Gallery Threshold:</source>
        <translation>Galerijdrempel:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="459"/>
        <source>Number of frames a detection must be seen before appearing in the Gallery tab</source>
        <translation>Aantal frames waarin een detectie moet worden gezien voordat deze in het tabblad Galerij verschijnt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="466"/>
        <source> frames</source>
        <translation> frames</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="469"/>
        <source>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</source>
        <translation>Detecties moeten gedurende dit aantal opeenvolgende frames worden gezien
voordat ze in de Galerij verschijnen. Hogere waarden verminderen
valse positieven, maar vertragen het verschijnen van detecties.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="530"/>
        <source>Device {index}</source>
        <translation>Apparaat {index}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="724"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="743"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="757"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="780"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="794"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="808"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="822"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1917"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="725"/>
        <source>Failed to open Streaming Analysis Guide:
{error}</source>
        <translation>Kan de streaminganalyse-gids niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="744"/>
        <source>Failed to open Image Analysis:
{error}</source>
        <translation>Kan beeldanalyse niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="758"/>
        <source>Failed to open Preferences:
{error}</source>
        <translation>Kan voorkeuren niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="781"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Kan Vluchtviewer niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="795"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Kan hulpdocumentatie niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="809"/>
        <source>Failed to open Community Forum:
{error}</source>
        <translation>Kan communityforum niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="823"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Kan YouTube-kanaal niet openen:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="934"/>
        <source>Loaded: {algorithm}</source>
        <translation>Geladen: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="950"/>
        <source>Error loading algorithm: {error}</source>
        <translation>Fout bij laden van algoritme: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="954"/>
        <source>Algorithm Load Error</source>
        <translation>Fout bij laden algoritme</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1462"/>
        <source>Algorithm switched to {label}</source>
        <translation>Algoritme overgeschakeld naar {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1512"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1589"/>
        <source>No Stream Connected</source>
        <translation>Geen stream verbonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1529"/>
        <source>{state} - {message}</source>
        <translation>{state} - {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1530"/>
        <source>Connected</source>
        <translation>Verbonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1530"/>
        <source>Disconnected</source>
        <translation>Verbinding verbroken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1542"/>
        <source>✓ Connected: {message}</source>
        <translation>✓ Verbonden: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1571"/>
        <source>✗ Disconnected: {message}</source>
        <translation>✗ Verbinding verbroken: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1780"/>
        <source>No detections found.</source>
        <translation>Geen detecties gevonden.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1784"/>
        <source>Detection Results ({count} found):</source>
        <translation>Detectieresultaten ({count} gevonden):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1796"/>
        <source>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</source>
        <translation>#{index}: type({cls}) pos({x},{y}) grootte({w}x{h})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1806"/>
        <source>#{index}: Type({cls})</source>
        <translation>#{index}: type({cls})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1811"/>
        <source> Conf({confidence:.2f})</source>
        <translation> betr({confidence:.2f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1856"/>
        <source>Recording started: {path}</source>
        <translation>Opname gestart: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1863"/>
        <source>Recording stopped</source>
        <translation>Opname gestopt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1877"/>
        <source>Status: Recording to {path}</source>
        <translation>Status: opnemen naar {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1897"/>
        <source>Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}</source>
        <translation>Duur: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Wachtrij: {queue}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1915"/>
        <source>✗ Error: {error}</source>
        <translation>✗ Fout: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1982"/>
        <source>Live Stream</source>
        <translation>Live-stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1984"/>
        <source>Cannot seek in live stream.

Detection was first seen at frame {frame}.</source>
        <translation>Kan niet zoeken in live-stream.

Detectie werd voor het eerst gezien bij frame {frame}.</translation>
    </message>
</context>
<context>
    <name>StreamingGuide</name>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="14"/>
        <source>Streaming Setup Guide</source>
        <translation>Streaminginstallatiegids</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="51"/>
        <source>Connect to Your Stream</source>
        <translation>Verbinden met uw stream</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="115"/>
        <source>Pre-recorded video file with playback controls</source>
        <translation>Vooraf opgenomen videobestand met afspeelbediening</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="122"/>
        <source>File</source>
        <translation>Bestand</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="161"/>
        <source>Live HDMI capture device (enter device index)</source>
        <translation>Live HDMI-opnameapparaat (voer apparaatindex in)</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="168"/>
        <source>HDMI</source>
        <translation>HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="204"/>
        <source>Network stream via RTMP URL</source>
        <translation>Netwerkstream via RTMP-URL</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="211"/>
        <source>RTMP</source>
        <translation>RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="254"/>
        <source>File: Use local video files (MP4, MOV, etc.) with timeline controls.</source>
        <translation>Bestand: gebruik lokale videobestanden (MP4, MOV, enz.) met tijdlijnbediening.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="269"/>
        <source>HDMI: Connect to a live HDMI capture device.</source>
        <translation>HDMI: maak verbinding met een live HDMI-opnameapparaat.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="284"/>
        <source>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</source>
        <translation>RTMP: maak verbinding met een live-netwerkstream (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="328"/>
        <source>Connection Details</source>
        <translation>Verbindingsdetails</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="347"/>
        <source>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</source>
        <translation>Geef het pad of de URL op voor het geselecteerde streamtype. U kunt optioneel automatisch verbinden wanneer de gids is voltooid.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="364"/>
        <source>Stream URL/Path:</source>
        <translation>Stream-URL/-pad:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="373"/>
        <source>Click Browse to select a file or enter a URL...</source>
        <translation>Klik op Bladeren om een bestand te selecteren of voer een URL in...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="385"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="399"/>
        <source>Auto Connect:</source>
        <translation>Automatisch verbinden:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="411"/>
        <source>Connect as soon as the guide finishes</source>
        <translation>Verbinden zodra de gids is voltooid</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="423"/>
        <source>Capture Devices:</source>
        <translation>Opnameapparaten:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="444"/>
        <source>Scan...</source>
        <translation>Scannen...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="484"/>
        <source>Processing Resolution:</source>
        <translation>Verwerkingsresolutie:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="532"/>
        <source>Video Capture Information</source>
        <translation>Informatie over video-opname</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="554"/>
        <source>What drone/camera was used to capture the video?</source>
        <translation>Welke drone/camera is gebruikt om de video vast te leggen?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="584"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>Op welke hoogte boven de grond (AGL) vloog de drone?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="636"/>
        <source>ft</source>
        <translation>ft</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="641"/>
        <source>m</source>
        <translation>m</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="679"/>
        <source>Estimated Ground Sampling Distance (GSD):</source>
        <translation>Geschatte grondbemonsteringsafstand (GSD):</translation>
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
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="710"/>
        <source>--</source>
        <translation>--</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="749"/>
        <source>Search Target Size</source>
        <translation>Grootte van zoekdoel</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="774"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Ongeveer hoe groot zijn de objecten die u wilt identificeren?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="805"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Meer voorbeelden:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 ft² – Hoed, helm, plastic zak &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 ft² – Kat, dagrugzak &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 ft² – Grote rugzak, middelgrote hond &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 ft² – Slaapzak, grote hond &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 ft² – Kleine boot, 2-persoonstent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 ft² – Auto/SUV, kleine pick-up, grote tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 ft² – Huis &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="847"/>
        <source>Detection &amp; Processing</source>
        <translation>Detectie &amp; verwerking</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="869"/>
        <source>Are you looking for specific colors?</source>
        <translation>Zoekt u specifieke kleuren?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="914"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="945"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1018"/>
        <source>Reset</source>
        <translation>Resetten</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1091"/>
        <source>Algorithm Parameters</source>
        <translation>Algoritmeparameters</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1126"/>
        <source>Close</source>
        <translation>Sluiten</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1138"/>
        <source>Skip this streaming guide next time</source>
        <translation>Deze streaminggids de volgende keer overslaan</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1166"/>
        <source>Back</source>
        <translation>Terug</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="138"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1178"/>
        <source>Continue</source>
        <translation>Doorgaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="84"/>
        <source>ADIAT Streaming Setup Guide</source>
        <translation>ADIAT-streaminginstallatiegids</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="136"/>
        <source>Open Stream Viewer</source>
        <translation>Streamviewer openen</translation>
    </message>
</context>
<context>
    <name>StreamingVideoDisplay</name>
    <message>
        <location filename="../app/core/views/streaming/components/StreamingVideoDisplay.py" line="66"/>
        <source>No Stream Connected</source>
        <translation>Geen stream verbonden</translation>
    </message>
</context>
<context>
    <name>TargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Hoed, helm, plastic zak</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Kat, dagrugzak</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Grote rugzak, middelgrote hond</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Slaapzak, grote hond</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Kleine boot, 2-persoonstent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Auto/SUV, kleine pick-up, grote tent</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Huis</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Meer voorbeelden:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>m²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>ft²</translation>
    </message>
</context>
<context>
    <name>TeamPlanningController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="47"/>
        <source>No Flagged AOIs</source>
        <translation>Geen gemarkeerde AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="49"/>
        <source>There are no flagged AOIs to assign.

Flag at least one AOI in the viewer before using Plan Verification.</source>
        <translation>Er zijn geen gemarkeerde AOI&apos;s om toe te wijzen.

Markeer ten minste één AOI in de viewer voordat u Plan-verificatie gebruikt.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="210"/>
        <source>No Team Selected</source>
        <translation>Geen team geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="211"/>
        <source>Select a target team (or &apos;Unassigned&apos;) in the list first.</source>
        <translation>Selecteer eerst een doelteam (of &apos;Niet toegewezen&apos;) in de lijst.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="219"/>
        <source>No AOIs Selected</source>
        <translation>Geen AOI&apos;s geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="221"/>
        <source>Select one or more AOIs on the map first.
Click on markers, or use Rectangle Select for area selection.</source>
        <translation>Selecteer eerst een of meer AOI&apos;s op de kaart.
Klik op markeringen of gebruik Rechthoek selecteren voor gebiedsselectie.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="300"/>
        <source>No AOIs</source>
        <translation>Geen AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="301"/>
        <source>Team &apos;{name}&apos; has no assigned AOIs.</source>
        <translation>Team &apos;{name}&apos; heeft geen toegewezen AOI&apos;s.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="312"/>
        <source>Save Team PDF</source>
        <translation>Team-PDF opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="314"/>
        <source>PDF files (*.pdf)</source>
        <translation>PDF-bestanden (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="326"/>
        <source>Select Export Folder</source>
        <translation>Exportmap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="336"/>
        <source>Exporting Team PDFs</source>
        <translation>Team-PDF&apos;s exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="354"/>
        <source>Generating PDF for {name}...</source>
        <translation>PDF genereren voor {name}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="365"/>
        <source>Generating master summary...</source>
        <translation>Hoofdsamenvatting genereren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="373"/>
        <source>Export complete</source>
        <translation>Export voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="380"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="426"/>
        <source>Export Error</source>
        <translation>Exportfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="381"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="427"/>
        <source>PDF generation failed: {error}</source>
        <translation>PDF-generatie mislukt: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="389"/>
        <source>Export Complete</source>
        <translation>Export voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="390"/>
        <source>Team PDFs saved to:
{folder}</source>
        <translation>Team-PDF&apos;s opgeslagen in:
{folder}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="406"/>
        <source>Generating PDF Report</source>
        <translation>PDF-rapport genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="414"/>
        <source>Done</source>
        <translation>Gereed</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="418"/>
        <source>Success</source>
        <translation>Geslaagd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="419"/>
        <source>PDF report generated successfully!</source>
        <translation>PDF-rapport succesvol gegenereerd!</translation>
    </message>
</context>
<context>
    <name>TeamPlanningDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="55"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="65"/>
        <source>Plan Verification</source>
        <translation>Plan-verificatie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="86"/>
        <source>Zoom In (+)</source>
        <translation>Inzoomen (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="88"/>
        <source>Zoom Out (-)</source>
        <translation>Uitzoomen (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="90"/>
        <source>Fit All (F)</source>
        <translation>Alles passend maken (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="93"/>
        <source>Rectangle Select</source>
        <translation>Rechthoek selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="96"/>
        <source>Draw a rectangle on the map to select multiple AOIs</source>
        <translation>Teken een rechthoek op de kaart om meerdere AOI&apos;s te selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="316"/>
        <source>Satellite View</source>
        <translation>Satellietweergave</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="122"/>
        <source>Teams</source>
        <translation>Teams</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="124"/>
        <source>+ New</source>
        <translation>+ Nieuw</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="125"/>
        <source>Create a new field team</source>
        <translation>Een nieuw veldteam maken</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="127"/>
        <source>✕ Remove</source>
        <translation>✕ Verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="128"/>
        <source>Remove the selected team</source>
        <translation>Het geselecteerde team verwijderen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="143"/>
        <source>Assign Selection ▶</source>
        <translation>Selectie toewijzen ▶</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="145"/>
        <source>Assign the selected AOIs on the map to the chosen team</source>
        <translation>De geselecteerde AOI&apos;s op de kaart toewijzen aan het gekozen team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="158"/>
        <source>Team AOIs</source>
        <translation>Team-AOI&apos;s</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="172"/>
        <source>Export Team PDF</source>
        <translation>Team-PDF exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="174"/>
        <source>Generate a PDF report for the selected team only</source>
        <translation>Een PDF-rapport genereren voor alleen het geselecteerde team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="179"/>
        <source>Export All PDFs</source>
        <translation>Alle PDF&apos;s exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="181"/>
        <source>Generate one PDF per team plus a master summary PDF</source>
        <translation>Een PDF per team plus een hoofdsamenvattings-PDF genereren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="195"/>
        <source>Click to select AOI • Ctrl+Click to multi-select • Use Rectangle Select for area selection • Scroll to zoom</source>
        <translation>Klik om AOI te selecteren • Ctrl+klik voor meervoudige selectie • Gebruik Rechthoek selecteren voor gebiedsselectie • Scrol om te zoomen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="222"/>
        <source>Team</source>
        <translation>Team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>New Team</source>
        <translation>Nieuw team</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>Team name:</source>
        <translation>Teamnaam:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="246"/>
        <source>Duplicate Name</source>
        <translation>Dubbele naam</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="247"/>
        <source>A team named &apos;{name}&apos; already exists.</source>
        <translation>Er bestaat al een team met de naam &apos;{name}&apos;.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="265"/>
        <source>Unassigned</source>
        <translation>Niet toegewezen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="298"/>
        <source>No Team Selected</source>
        <translation>Geen team geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="299"/>
        <source>Please select a team to export.</source>
        <translation>Selecteer een team om te exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="305"/>
        <source>No Teams</source>
        <translation>Geen teams</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="306"/>
        <source>Create at least one team before exporting.</source>
        <translation>Maak ten minste één team aan voordat u exporteert.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="313"/>
        <source>Map View</source>
        <translation>Kaartweergave</translation>
    </message>
</context>
<context>
    <name>TelemetryHud</name>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="83"/>
        <source>LAT {value}</source>
        <translation>LAT {value}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="86"/>
        <source>LON {value}</source>
        <translation>LON {value}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="122"/>
        <source>FLY</source>
        <translation>FLY</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="147"/>
        <source>stale {age}s</source>
        <translation>verouderd {age}s</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="167"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="57"/>
        <source>ALT —</source>
        <translation>ALT —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="178"/>
        <source>ALT {msl} {msl_unit} / {agl} {agl_unit}</source>
        <translation>ALT {msl} {msl_unit} / {agl} {agl_unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="184"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="91"/>
        <source>HDG —</source>
        <translation>HDG —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="188"/>
        <source>HDG {bearing:03d}° {cardinal}</source>
        <translation>HDG {bearing:03d}° {cardinal}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="194"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="98"/>
        <source>SPD —</source>
        <translation>SPD —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="200"/>
        <source>SPD {value} mph</source>
        <translation>SPD {value} mph</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="203"/>
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
        <location filename="../resources/views/flight/telemetry_hud.ui" line="126"/>
        <source>—</source>
        <translation>—</translation>
    </message>
</context>
<context>
    <name>TextLabeledSlider</name>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="238"/>
        <source>Very Conservative</source>
        <translation>Zeer conservatief</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="239"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="240"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="241"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="242"/>
        <source>Very Aggressive</source>
        <translation>Zeer agressief</translation>
    </message>
</context>
<context>
    <name>ThermalAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="29"/>
        <source>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</source>
        <translation>Type thermische afwijking om te detecteren in thermische beelden.
Bepaalt of u warme plekken, koude plekken of beide wilt vinden.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Afwijkingstype:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="45"/>
        <source>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</source>
        <translation>Selecteer het type thermische afwijking om te detecteren:
• Boven of onder het gemiddelde: detecteert zowel warme als koude afwijkingen (standaard)
• Boven het gemiddelde: detecteert alleen warme plekken (temperaturen boven het gemiddelde)
• Onder het gemiddelde: detecteert alleen koude plekken (temperaturen onder het gemiddelde)
Het algoritme vergelijkt de temperatuur van elke pixel met de gemiddelde temperatuur van zijn segment.
Gebruik &quot;Boven het gemiddelde&quot; om warmtebronnen te vinden, &quot;Onder het gemiddelde&quot; voor koude objecten.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="54"/>
        <source>Above or Below Mean</source>
        <translation>Boven of onder het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="59"/>
        <source>Above Mean</source>
        <translation>Boven het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="64"/>
        <source>Below Mean</source>
        <translation>Onder het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="77"/>
        <source>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</source>
        <translation>Temperatuurdrempel voor het detecteren van thermische afwijkingen.
Gemeten in standaarddeviaties vanaf de gemiddelde temperatuur.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="81"/>
        <source>Anomaly Threshold:</source>
        <translation>Afwijkingsdrempel:</translation>
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
        <translation>Stel de drempel voor afwijkingsdetectie in standaarddeviaties in.
• Bereik: 0 tot 7 standaarddeviaties
• Standaard: 4
Definieert hoeveel een temperatuur moet afwijken van het gemiddelde om gedetecteerd te worden:
• Lagere waarden (1-2): zeer gevoelig, detecteert subtiele temperatuurverschillen (meer detecties)
• Gemiddelde waarden (3-5): gebalanceerde detectie (aanbevolen voor de meeste gevallen)
• Hogere waarden (6-7): detecteert alleen extreme temperatuurverschillen (minder detecties)
Voorbeeld: waarde van 4 detecteert pixels die 4 standaarddeviaties boven/onder de gemiddelde temperatuur liggen.</translation>
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
        <translation>Aantal segmenten waarin elke thermische afbeelding wordt verdeeld voor analyse.
Elk segment wordt onafhankelijk geanalyseerd op lokale thermische afwijkingen.
Prestatie-impact:
• Hoger aantal segmenten: VERHOOGT de verwerkingstijd (meer segmenten te analyseren)
• Lager aantal segmenten: VERLAAGT de verwerkingstijd (minder segmenten te analyseren)
• 1 segment: snelste verwerking (analyseert de hele afbeelding in één keer)
Meer segmenten verbeteren de detectie in scènes met temperatuurgradiënten.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="122"/>
        <source>Image Segments:</source>
        <translation>Beeldsegmenten:</translation>
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
        <translation>Selecteer het aantal segmenten waarin elke thermische afbeelding wordt verdeeld.
• Opties: 1, 2, 4, 6, 9, 16, 25, 36 segmenten
• Standaard: 1 (analyseer de hele afbeelding als één segment)
Het algoritme berekent de gemiddelde temperatuur voor elk segment onafhankelijk:
• 1 segment: globale temperatuuranalyse (het beste voor uniforme scènes)
• Meer segmenten: lokale temperatuuranalyse (beter voor variërende achtergronden)
Meer segmenten verbeteren de detectie in scènes met temperatuurgradiënten.
Aanbevolen: 4-9 segmenten voor typische thermische dronebeelden.</translation>
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
        <translation>Bevatten uw afbeeldingen complexe scènes met gebouwen, voertuigen of gemengde door mensen gemaakte bedekking?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="57"/>
        <source>No</source>
        <translation>Nee</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="72"/>
        <source>Yes</source>
        <translation>Ja</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="105"/>
        <source>What type of anomalies are you looking for?</source>
        <translation>Naar welk type afwijkingen zoekt u?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="122"/>
        <source>Warmer than surroundings</source>
        <translation>Warmer dan de omgeving</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="134"/>
        <source>Cooler than surroundings</source>
        <translation>Koeler dan de omgeving</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="146"/>
        <source>Both</source>
        <translation>Beide</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="185"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Hoe agressief moet ADIAT naar afwijkingen zoeken?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="198"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Opmerking: een hogere instelling vindt meer potentiële afwijkingen, maar kan ook het aantal valse positieven vergroten.</translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="45"/>
        <source>Very 
Conservative</source>
        <translation>Zeer 
conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="46"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="47"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="48"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="49"/>
        <source>Very 
Aggressive</source>
        <translation>Zeer 
agressief</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramChart</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="98"/>
        <source>No histogram data available</source>
        <translation>Geen histogramgegevens beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="434"/>
        <source>All Pixels</source>
        <translation>Alle pixels</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="445"/>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="456"/>
        <source>AOI Pixels</source>
        <translation>AOI-pixels</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="32"/>
        <source>Thermal Histogram Unavailable</source>
        <translation>Thermisch histogram niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="33"/>
        <source>No thermal temperature data is available for the current image.</source>
        <translation>Er zijn geen thermische temperatuurgegevens beschikbaar voor de huidige afbeelding.</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="14"/>
        <source>Thermal Histogram</source>
        <translation>Thermisch histogram</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="23"/>
        <source>Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.</source>
        <translation>Grijze balken tonen de volledige temperatuurverdeling, oranje balken markeren AOI-/afwijkingsbins, en wanneer u over het diagram beweegt, worden overeenkomende pixels in de afbeelding gemarkeerd.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="32"/>
        <source>Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Sleep op het histogram om te zoomen. Dubbelklik of gebruik Zoom resetten om terug te keren naar het volledige bereik.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Zoom resetten</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="64"/>
        <source>Visible Temperature Range</source>
        <translation>Zichtbaar temperatuurbereik</translation>
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
        <translation>Bereik resetten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="61"/>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="126"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="117"/>
        <source>Hover over the histogram to inspect a temperature band.</source>
        <translation>Beweeg over het histogram om een temperatuurband te inspecteren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="30"/>
        <source>No thermal histogram data available</source>
        <translation>Geen thermische histogramgegevens beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="131"/>
        <source>Hover band: {lower:.1f} to {upper:.1f} °{unit}</source>
        <translation>Band onder cursor: {lower:.1f} tot {upper:.1f} °{unit}</translation>
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
        <translation>Formulier</translation>
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
        <translation>Minimumtemperatuurdrempel voor detectie in thermische afbeeldingen.
• Bereik: -30°C tot 50°C
• Standaard: 35°C
Definieert de ondergrens van het temperatuurdetectiebereik:
• Lagere waarden: VERHOGEN detecties - accepteert koelere objecten
• Hogere waarden: VERMINDEREN detecties - alleen warmere objecten worden gedetecteerd
Gecombineerd met Max. temp. om een detectiebereik te maken (bijv. 35-40°C voor menselijke lichaamstemperatuur).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="38"/>
        <source>Minimum Temp (°C)</source>
        <translation>Min. temp. (°C)</translation>
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
        <translation>Stel de minimumtemperatuur voor detectie in Celsius in.
• Bereik: -30°C tot 50°C
• Standaard: 35°C
Pixels met temperaturen op of boven deze drempel worden gedetecteerd.
• Lagere waarden: detecteer koelere objecten (meer detecties)
• Hogere waarden: detecteer alleen warmere objecten (minder detecties)
Opmerking: temperatuur weergegeven in Celsius, geconverteerd op basis van de instelling in Voorkeuren.
Gebruik voor het vinden van objecten binnen een specifiek temperatuurbereik (bijv. mensen 35-40°C).</translation>
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
        <translation>Maximumtemperatuurdrempel voor detectie in thermische afbeeldingen.
• Bereik: -30°C tot 93°C
• Standaard: 40°C
Definieert de bovengrens van het temperatuurdetectiebereik:
• Lagere waarden: VERMINDEREN detecties - alleen koelere objecten gedetecteerd
• Hogere waarden: VERHOGEN detecties - accepteert warmere objecten
Gecombineerd met Min. temp. om een detectiebereik te maken (bijv. 35-40°C voor menselijke lichaamstemperatuur).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="103"/>
        <source>Maximum Temp (°C)</source>
        <translation>Max. temp. (°C)</translation>
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
        <translation>Stel de maximumtemperatuur voor detectie in Celsius in.
• Bereik: -30°C tot 93°C
• Standaard: 40°C
Pixels met temperaturen op of onder deze drempel worden gedetecteerd.
• Lagere waarden: detecteer alleen koelere objecten (minder detecties)
• Hogere waarden: detecteer warmere objecten (meer detecties)
Opmerking: temperatuur weergegeven in Celsius, geconverteerd op basis van de instelling in Voorkeuren.
Detectie vindt plaats voor pixels tussen minimum- en maximumtemperaturen (inclusief).</translation>
    </message>
</context>
<context>
    <name>ThermalRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="108"/>
        <source>Minimum Temp ({degree} F)</source>
        <translation>Min. temp. ({degree} F)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="114"/>
        <source>Maximum Temp ({degree} F)</source>
        <translation>Max. temp. ({degree} F)</translation>
    </message>
</context>
<context>
    <name>ThermalRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRangeWizard.ui" line="34"/>
        <source>What range of temperatures should ADIAT look for?</source>
        <translation>Naar welk temperatuurbereik moet ADIAT zoeken?</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulier</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="29"/>
        <source>Type of local thermal residual anomaly to detect in radiometric imagery.
Determines whether to find warm anomalies, cool anomalies, or both.</source>
        <translation>Type lokale thermische residuele afwijking om te detecteren in radiometrische beelden.
Bepaalt of u warme afwijkingen, koele afwijkingen of beide wilt vinden.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Afwijkingstype:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="45"/>
        <source>Select the type of thermal residual anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to its local background estimate.</source>
        <translation>Selecteer het type thermische residuele afwijking om te detecteren:
• Boven of onder het gemiddelde: detecteert zowel warme als koude afwijkingen (standaard)
• Boven het gemiddelde: detecteert alleen warme plekken (temperaturen boven het gemiddelde)
• Onder het gemiddelde: detecteert alleen koude plekken (temperaturen onder het gemiddelde)
Het algoritme vergelijkt de temperatuur van elke pixel met zijn lokale achtergrondschatting.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="53"/>
        <source>Above or Below Mean</source>
        <translation>Boven of onder het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="58"/>
        <source>Above Mean</source>
        <translation>Boven het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="63"/>
        <source>Below Mean</source>
        <translation>Onder het gemiddelde</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="92"/>
        <source>Detection sensitivity for thermal residual anomalies.
• Range: 1 to 10
• Default: 5
Lower values are more conservative (fewer detections).
Higher values are more aggressive (more detections).</source>
        <translation>Detectiegevoeligheid voor thermische residuele afwijkingen.
• Bereik: 1 tot 10
• Standaard: 5
Lagere waarden zijn conservatiever (minder detecties).
Hogere waarden zijn agressiever (meer detecties).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="99"/>
        <source>Sensitivity:</source>
        <translation>Gevoeligheid:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="112"/>
        <source>Adjust detection sensitivity for local thermal residual anomalies.
• 1-3: Conservative
• 4-6: Moderate
• 7-10: Aggressive</source>
        <translation>Pas de detectiegevoeligheid aan voor lokale thermische residuele afwijkingen.
• 1-3: conservatief
• 4-6: gematigd
• 7-10: agressief</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="153"/>
        <source>Current sensitivity level for residual anomaly detection.</source>
        <translation>Huidig gevoeligheidsniveau voor detectie van residuele afwijkingen.</translation>
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
        <translation>Naar welk type afwijkingen zoekt u?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="54"/>
        <source>Warmer than surroundings</source>
        <translation>Warmer dan de omgeving</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="66"/>
        <source>Cooler than surroundings</source>
        <translation>Koeler dan de omgeving</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="78"/>
        <source>Both</source>
        <translation>Beide</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="117"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Hoe agressief moet ADIAT naar afwijkingen zoeken?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="130"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Opmerking: een hogere instelling vindt meer potentiële afwijkingen, maar kan ook het aantal valse positieven vergroten.</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="33"/>
        <source>Very 
Conservative</source>
        <translation>Zeer 
conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="34"/>
        <source>Conservative</source>
        <translation>Conservatief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="35"/>
        <source>Moderate</source>
        <translation>Gemiddeld</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="36"/>
        <source>Aggressive</source>
        <translation>Agressief</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="37"/>
        <source>Very 
Aggressive</source>
        <translation>Zeer 
agressief</translation>
    </message>
</context>
<context>
    <name>TileFetchController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="150"/>
        <source>Invalid Area</source>
        <translation>Ongeldig gebied</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="151"/>
        <source>Please enter a valid bounding box.</source>
        <translation>Voer een geldig begrenzingsvak in.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="154"/>
        <source>No Output Folder</source>
        <translation>Geen uitvoermap</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="155"/>
        <source>Please choose an output folder.</source>
        <translation>Kies een uitvoermap.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="158"/>
        <source>No Dataset</source>
        <translation>Geen dataset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="159"/>
        <source>Please select at least one dataset.</source>
        <translation>Selecteer minstens één dataset.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="286"/>
        <source>No GPS Found</source>
        <translation>Geen GPS gevonden</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="287"/>
        <source>No GPS positions were found in the {source} images.</source>
        <translation>Er zijn geen GPS-posities gevonden in de {source}-afbeeldingen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="302"/>
        <source>Select image folder</source>
        <translation>Afbeeldingenmap selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="311"/>
        <source>No Images</source>
        <translation>Geen afbeeldingen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="312"/>
        <source>No images were found in the selected folder.</source>
        <translation>Er zijn geen afbeeldingen gevonden in de geselecteerde map.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="358"/>
        <source>Replace Canopy Source?</source>
        <translation>Kroonbron vervangen?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="359"/>
        <source>A LANDFIRE canopy source is currently configured.

Register the downloaded Meta/WRI canopy tiles instead? (Your LANDFIRE files stay on disk; only the selected source changes.)</source>
        <translation>Er is momenteel een LANDFIRE-kroonbron geconfigureerd.

In plaats daarvan de gedownloade Meta/WRI-kroontegels registreren? (Uw LANDFIRE-bestanden blijven op schijf; alleen de geselecteerde bron verandert.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Elevation (DEM)</source>
        <translation>Hoogte (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Canopy height</source>
        <translation>Kroonhoogte</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="385"/>
        <source>{product}: cancelled before completion.</source>
        <translation>{product}: geannuleerd vóór voltooiing.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="387"/>
        <source>{product}: {failed} tile(s) failed to download.</source>
        <translation>{product}: {failed} tegel(s) konden niet worden gedownload.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="390"/>
        <source>{product}: no data covers this area.</source>
        <translation>{product}: geen gegevens dekken dit gebied.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="392"/>
        <source>{product}: nothing was downloaded.</source>
        <translation>{product}: er is niets gedownload.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="399"/>
        <source>{product}: registered as the active source.</source>
        <translation>{product}: geregistreerd als actieve bron.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="402"/>
        <source>{product}: NOT registered (no usable tiles).</source>
        <translation>{product}: NIET geregistreerd (geen bruikbare tegels).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="411"/>
        <source>Download Finished with Problems</source>
        <translation>Download voltooid met problemen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="417"/>
        <source>Download Complete</source>
        <translation>Download voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="406"/>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="413"/>
        <source>Downloaded {count} tiles.</source>
        <translation>{count} tegels gedownload.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="428"/>
        <source>Download Cancelled</source>
        <translation>Download geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="429"/>
        <source>The download was cancelled. No tiles were registered.</source>
        <translation>De download is geannuleerd. Er zijn geen tegels geregistreerd.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="436"/>
        <source>Download Error</source>
        <translation>Downloadfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="437"/>
        <source>Tile download failed:
{error}</source>
        <translation>Downloaden van tegels mislukt:
{error}</translation>
    </message>
</context>
<context>
    <name>TileFetchDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="48"/>
        <source>Download Coverage Data</source>
        <translation>Dekkingsgegevens downloaden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="58"/>
        <source>Area of Interest (WGS84)</source>
        <translation>Interessegebied (WGS84)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="68"/>
        <source>Fill area from</source>
        <translation>Gebied invullen uit</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="73"/>
        <source>Fill the area from the loaded mission&apos;s image GPS, or from an image folder.</source>
        <translation>Vul het gebied in op basis van de GPS van de afbeeldingen van de geladen missie, of uit een afbeeldingenmap.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="70"/>
        <source>Loaded mission extent</source>
        <translation>Bereik van geladen missie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="71"/>
        <source>Image folder...</source>
        <translation>Afbeeldingenmap...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="93"/>
        <source>Min longitude:</source>
        <translation>Min. lengtegraad:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="95"/>
        <source>Min latitude:</source>
        <translation>Min. breedtegraad:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="97"/>
        <source>Max longitude:</source>
        <translation>Max. lengtegraad:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="99"/>
        <source>Max latitude:</source>
        <translation>Max. breedtegraad:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="104"/>
        <source>Footprint buffer (m):</source>
        <translation>Voetafdrukbuffer (m):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="109"/>
        <source>Padding added around the camera positions so downloaded tiles cover the image footprints. Auto-sized from the mission; edit and re-fill to change.</source>
        <translation>Marge rond de cameraposities zodat de gedownloade tegels de beeldvoetafdrukken dekken. Automatisch bepaald op basis van de missie; bewerk en vul opnieuw om te wijzigen.</translation>
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
        <translation>USGS 3DEP levert lokale hoogtegegevens van 1 m. Optioneel wanneer u al een terreinbron hebt geconfigureerd (AWS Terrain Tiles online of gedownloade 3DEP) — schakel dit in om gegevens met hogere resolutie te downloaden.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="127"/>
        <source>Meta/WRI Canopy Height</source>
        <translation>Meta/WRI-kroonhoogte</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="142"/>
        <source>Store in:</source>
        <translation>Opslaan in:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="144"/>
        <source>Central tile library (recommended)</source>
        <translation>Centrale tegelbibliotheek (aanbevolen)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="146"/>
        <source>Mission results folder</source>
        <translation>Map met missieresultaten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="147"/>
        <source>Custom folder...</source>
        <translation>Aangepaste map...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="149"/>
        <source>The central library collects tiles from all missions in one place (they merge, nothing gets replaced) and registers automatically. Choose the results folder or a custom folder to keep tiles beside a specific mission instead.</source>
        <translation>De centrale bibliotheek verzamelt tegels van alle missies op één plek (ze worden samengevoegd, niets wordt vervangen) en registreert automatisch. Kies de resultatenmap of een aangepaste map om tegels bij een specifieke missie te bewaren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="158"/>
        <source>Output folder:</source>
        <translation>Uitvoermap:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="162"/>
        <source>Browse...</source>
        <translation>Bladeren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="168"/>
        <source>Register in Preferences when complete</source>
        <translation>Registreren in Voorkeuren na voltooiing</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="177"/>
        <source>Download</source>
        <translation>Downloaden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="180"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="206"/>
        <source>This area is already covered by your registered tiles.</source>
        <translation>Dit gebied wordt al gedekt door uw geregistreerde tegels.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="208"/>
        <source>Partially covered by your registered tiles — downloading fills the gaps.</source>
        <translation>Gedeeltelijk gedekt door uw geregistreerde tegels — downloaden vult de gaten.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="214"/>
        <source>Your downloaded 1 m tiles don&apos;t include this area — without this download, online AWS Terrain Tiles (~30 m) are used here instead.</source>
        <translation>Uw gedownloade 1 m-tegels omvatten dit gebied niet — zonder deze download worden hier online AWS Terrain Tiles (~30 m) gebruikt.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="217"/>
        <source>Your downloaded canopy tiles don&apos;t include this area — without this download, POD runs with no canopy attenuation here.</source>
        <translation>Uw gedownloade bladerdaktegels omvatten dit gebied niet — zonder deze download draait POD hier zonder bladerdakdemping.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="222"/>
        <source>No local elevation tiles registered — online AWS Terrain Tiles (~30 m) serve as the baseline.</source>
        <translation>Geen lokale hoogtetegels geregistreerd — online AWS Terrain Tiles (~30 m) dienen als basis.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="224"/>
        <source>No canopy source is configured yet.</source>
        <translation>Er is nog geen bladerdakbron geconfigureerd.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="276"/>
        <source>Select output folder</source>
        <translation>Uitvoermap selecteren</translation>
    </message>
</context>
<context>
    <name>TrackGalleryWidget</name>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="41"/>
        <source>Detection Gallery</source>
        <translation>Detectiegalerij</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="82"/>
        <source>0 detections</source>
        <translation>0 detecties</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="149"/>
        <source>1 detection</source>
        <translation>1 detectie</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="151"/>
        <source>{count} detections</source>
        <translation>{count} detecties</translation>
    </message>
</context>
<context>
    <name>UnifiedMapExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="438"/>
        <source>No Data Selected</source>
        <translation>Geen gegevens geselecteerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="439"/>
        <source>Please select at least one type of data to export.</source>
        <translation>Selecteer ten minste één type gegevens om te exporteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="468"/>
        <source>Select folder for POD coverage files</source>
        <translation>Map voor POD-dekkingsbestanden selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="476"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="583"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="855"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="889"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="934"/>
        <source>Export Error</source>
        <translation>Exportfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="477"/>
        <source>An error occurred during export:
{error}</source>
        <translation>Er is een fout opgetreden tijdens de export:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="495"/>
        <source>Save Map Export</source>
        <translation>Kaartexport opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="497"/>
        <source>KML files (*.kml);;KMZ files (*.kmz)</source>
        <translation>KML-bestanden (*.kml);;KMZ-bestanden (*.kmz)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="584"/>
        <source>Failed to export to KML:
{error}</source>
        <translation>Exporteren naar KML mislukt:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="651"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="822"/>
        <source>POD Error</source>
        <translation>POD-fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="652"/>
        <source>Could not start the POD calculation:
{error}</source>
        <translation>Kan de POD-berekening niet starten:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="702"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="714"/>
        <source>POD coverage complete</source>
        <translation>POD-dekking voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="711"/>
        <source>POD coverage complete — {count} frame(s) used online elevation (outside local DEM)</source>
        <translation>POD-dekking voltooid — {count} frame(s) gebruikten online hoogte (buiten lokale DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="719"/>
        <source>POD complete — {skipped} of {total} frames skipped</source>
        <translation>POD voltooid — {skipped} van {total} frames overgeslagen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="722"/>
        <source>({count} without elevation data)</source>
        <translation>({count} zonder hoogtegegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="730"/>
        <source>(canopy data covered {pct}% of the searched area)</source>
        <translation>(bladerdakgegevens dekten {pct}% van het doorzochte gebied)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="785"/>
        <source>Terrain and canopy aware probability-of-detection heatmap.</source>
        <translation>Terrein- en bladerdakbewuste detectiekans-heatmap.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="789"/>
        <source>Mean POD over covered area: {pod}%</source>
        <translation>Gemiddelde POD over gedekt gebied: {pod}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="792"/>
        <source>POD Coverage</source>
        <translation>POD-dekking</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="800"/>
        <source>POD Overlay</source>
        <translation>POD-overlay</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="801"/>
        <source>The POD coverage was computed, but embedding it into the exported file failed:
{error}

The POD GeoTIFF products were still written next to the export.</source>
        <translation>De POD-dekking is berekend, maar het insluiten in het geëxporteerde bestand is mislukt:
{error}

De POD GeoTIFF-producten zijn wel naast de export geschreven.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="814"/>
        <source>POD calculation cancelled</source>
        <translation>POD-berekening geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="823"/>
        <source>POD calculation failed:
{error}</source>
        <translation>POD-berekening mislukt:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="856"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="890"/>
        <source>Failed to export to CalTopo:
{error}</source>
        <translation>Exporteren naar CalTopo mislukt:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="906"/>
        <source>Map export completed successfully!</source>
        <translation>Kaartexport succesvol voltooid!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="921"/>
        <source>Map export cancelled</source>
        <translation>Kaartexport geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="935"/>
        <source>Map export failed:
{error}</source>
        <translation>Kaartexport mislukt:
{error}</translation>
    </message>
</context>
<context>
    <name>UpdateController</name>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="52"/>
        <source>Disabled while Offline Only mode is enabled.</source>
        <translation>Uitgeschakeld terwijl de modus Alleen offline is ingeschakeld.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="56"/>
        <source>Check the update feed for a newer ADIAT installer.</source>
        <translation>Controleer de update-feed op een nieuwer ADIAT-installatieprogramma.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="85"/>
        <source>Updates Disabled</source>
        <translation>Updates uitgeschakeld</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="87"/>
        <source>Update checks are disabled while Offline Only mode is enabled.</source>
        <translation>Updatecontroles zijn uitgeschakeld terwijl de modus Alleen offline is ingeschakeld.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="101"/>
        <source>Update Check Failed</source>
        <translation>Updatecontrole mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="102"/>
        <source>Unable to check for updates:
{error}</source>
        <translation>Kan niet controleren op updates:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="110"/>
        <source>No Updates Available</source>
        <translation>Geen updates beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="112"/>
        <source>You are already running the latest available version of ADIAT.</source>
        <translation>U gebruikt al de nieuwste beschikbare versie van ADIAT.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="130"/>
        <source>Installer Launch Failed</source>
        <translation>Starten van installatieprogramma mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="131"/>
        <source>The installer was downloaded but could not be launched:
{error}</source>
        <translation>Het installatieprogramma is gedownload, maar kon niet worden gestart:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="137"/>
        <source>Installer Started</source>
        <translation>Installatieprogramma gestart</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="139"/>
        <source>The installer has been launched. Close ADIAT when you are ready to continue the update.</source>
        <translation>Het installatieprogramma is gestart. Sluit ADIAT wanneer u klaar bent om de update voort te zetten.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="148"/>
        <source>Update Available</source>
        <translation>Update beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="150"/>
        <source>ADIAT {new_version} is available. You are running {current_version}.</source>
        <translation>ADIAT {new_version} is beschikbaar. U gebruikt {current_version}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="156"/>
        <source>Do you want to download and launch the installer now?</source>
        <translation>Wilt u het installatieprogramma nu downloaden en starten?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="159"/>
        <source>Download and Install</source>
        <translation>Downloaden en installeren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="168"/>
        <source>Downloading ADIAT {version}...</source>
        <translation>ADIAT {version} downloaden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="169"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="174"/>
        <source>Downloading Update</source>
        <translation>Update downloaden</translation>
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
        <translation>onbekend</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="196"/>
        <source>Downloading ADIAT {version}...
{downloaded} of {total}</source>
        <translation>ADIAT {version} downloaden...
{downloaded} van {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="204"/>
        <location filename="../app/core/controllers/UpdateController.py" line="210"/>
        <source>Update download canceled.</source>
        <translation>Update-download geannuleerd.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="215"/>
        <source>Download Failed</source>
        <translation>Download mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="216"/>
        <source>Unable to download the update installer:
{error}</source>
        <translation>Kan het update-installatieprogramma niet downloaden:
{error}</translation>
    </message>
</context>
<context>
    <name>UpscaleDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="187"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="367"/>
        <source>Upscaled View - {level}x</source>
        <translation>Opgeschaalde weergave - {level}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="229"/>
        <source>Upscale Method:</source>
        <translation>Opschaalmethode:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="233"/>
        <source>Auto (Recommended)</source>
        <translation>Automatisch (aanbevolen)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="234"/>
        <source>Fast (Lanczos)</source>
        <translation>Snel (Lanczos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="236"/>
        <source>Balanced (OpenCV EDSR)</source>
        <translation>Gebalanceerd (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="264"/>
        <source>Upres Again</source>
        <translation>Opnieuw opschalen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="267"/>
        <source>Upscale the currently visible portion by {factor}x</source>
        <translation>Het momenteel zichtbare gedeelte opschalen met {factor}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="271"/>
        <source>Quit</source>
        <translation>Afsluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="274"/>
        <source>Close this upscale window</source>
        <translation>Dit opschaalvenster sluiten</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="302"/>
        <source>Resolution: {width} × {height} pixels | Original: {orig_w} × {orig_h} pixels | Upscale: {level}x | Use mouse wheel to zoom, right-click to pan</source>
        <translation>Resolutie: {width} × {height} pixels | Origineel: {orig_w} × {orig_h} pixels | Opschaal: {level}x | Gebruik muiswiel om te zoomen, rechtsklik om te pannen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="375"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="387"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="532"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="564"/>
        <source>Upscale Error</source>
        <translation>Opschaalfout</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="376"/>
        <source>Error during initial upscale: {error}</source>
        <translation>Fout tijdens initiële opschaling: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="388"/>
        <source>Unable to extract visible image portion.</source>
        <translation>Kan zichtbaar afbeeldingsgedeelte niet extraheren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="397"/>
        <source>Maximum Upscale Reached</source>
        <translation>Maximale opschaling bereikt</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="399"/>
        <source>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</source>
        <translation>Maximaal opschaalniveau van {level}x is bereikt.
Verdere opschaling is niet toegestaan om geheugenproblemen te voorkomen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="413"/>
        <source>Image Too Large</source>
        <translation>Afbeelding te groot</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="415"/>
        <source>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</source>
        <translation>Opschaling zou resulteren in een afbeelding van {width}×{height} pixels.
Maximaal toegestane afmeting is {max_dim} pixels.

Probeer in te zoomen op een kleiner gebied voordat u opschaalt.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="426"/>
        <source>Image Too Small</source>
        <translation>Afbeelding te klein</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="428"/>
        <source>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</source>
        <translation>Zichtbaar gedeelte is te klein ({width}×{height} pixels).
Zoom in op een groter gebied voordat u opschaalt.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="468"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="565"/>
        <source>An error occurred during upscaling:
{error}</source>
        <translation>Er is een fout opgetreden tijdens de opschaling:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="487"/>
        <source>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</source>
        <translation>Afbeelding opschalen met AI-verbetering...
Van {width}×{height} naar {new_width}×{new_height} pixels
Dit kan enkele seconden duren.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="760"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="504"/>
        <source>Upscaling (OpenCV EDSR)</source>
        <translation>Opschalen (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="533"/>
        <source>Failed to start upscaling:
{error}</source>
        <translation>Kan opschaling niet starten:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="603"/>
        <source>Method Not Available</source>
        <translation>Methode niet beschikbaar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="605"/>
        <source>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</source>
        <translation>Real-ESRGAN is nog niet geïmplementeerd.
Terugvallen op Lanczos-interpolatie.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="759"/>
        <source>Downloading {model_name} model...</source>
        <translation>Model {model_name} downloaden...</translation>
    </message>
</context>
<context>
    <name>VideoParser</name>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="14"/>
        <source>Video Parser</source>
        <translation>Videoparser</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="45"/>
        <source>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</source>
        <translation>Pad naar het videobestand waaruit frames moeten worden geëxtraheerd.
Ondersteunde formaten: MP4, AVI, MOV, MKV en andere gangbare videoformaten.
Klik op de knop Selecteren om naar een videobestand te bladeren.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="62"/>
        <source>Metadata file containing GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Optional: Provides location information for extracted frames.
Without a metadata file, frames will have no GPS data.</source>
        <translation>Metagegevensbestand met GPS-telemetriegegevens.
Ondersteunt DJI SRT-ondertitelbestanden en Skydio CSV-vluchtlogboeken.
Optioneel: biedt locatie-informatie voor geëxtraheerde frames.
Zonder een metagegevensbestand hebben frames geen GPS-gegevens.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="68"/>
        <source>The metadata file contains timestamped GPS information for the video.  It is optional, but without it output images won&apos;t include location information.  Supports SRT (DJI) and CSV (Skydio) formats.</source>
        <translation>Het metagegevensbestand bevat GPS-informatie met tijdstempels voor de video. Het is optioneel, maar zonder dit bestand bevatten de uitvoer-afbeeldingen geen locatie-informatie. Ondersteunt SRT- (DJI) en CSV-formaten (Skydio).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="71"/>
        <source>Metadata File (optional): </source>
        <translation>Metagegevensbestand (optioneel): </translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="83"/>
        <source>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</source>
        <translation>Doelmap waar geëxtraheerde frameafbeeldingen worden opgeslagen.
Elk frame wordt opgeslagen als een afzonderlijk afbeeldingsbestand met tijdstempelinformatie.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="87"/>
        <source>Output Folder:</source>
        <translation>Uitvoermap:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="99"/>
        <source>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</source>
        <translation>Pad naar de uitvoermap voor geëxtraheerde frameafbeeldingen.
Alle frames worden in deze map opgeslagen met opeenvolgende naamgeving.
Klik op de knop Selecteren om een andere map te kiezen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="116"/>
        <source>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</source>
        <translation>Bladeren naar uitvoermap om geëxtraheerde frames op te slaan.
Opent een mapselectievenster.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="120"/>
        <location filename="../resources/views/images/VideoParser.ui" line="162"/>
        <location filename="../resources/views/images/VideoParser.ui" line="200"/>
        <source>Select</source>
        <translation>Selecteren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="130"/>
        <source>folder.png</source>
        <translation>folder.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="142"/>
        <source>Select the source video file to parse.
Video will be split into individual frame images.</source>
        <translation>Selecteer het bronvideobestand om te parseren.
De video wordt opgesplitst in afzonderlijke frame-afbeeldingen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="146"/>
        <source>Video File:</source>
        <translation>Videobestand:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="158"/>
        <source>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</source>
        <translation>Bladeren naar videobestand om frames uit te extraheren.
Opent een bestandsselectievenster voor videobestanden (MP4, AVI, MOV, enz.).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="177"/>
        <source>Path to the optional metadata file with GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
If provided, extracted frames will include GPS metadata (latitude, longitude, altitude).
Can be left empty if location data is not needed.</source>
        <translation>Pad naar het optionele metagegevensbestand met GPS-telemetriegegevens.
Ondersteunt DJI SRT-ondertitelbestanden en Skydio CSV-vluchtlogboeken.
Indien opgegeven, bevatten geëxtraheerde frames GPS-metagegevens (breedtegraad, lengtegraad, hoogte).
Kan leeg blijven als locatiegegevens niet nodig zijn.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="195"/>
        <source>Browse for optional metadata file containing GPS telemetry.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Opens a file selection dialog for SRT and CSV files.</source>
        <translation>Bladeren naar optioneel metagegevensbestand met GPS-telemetrie.
Ondersteunt DJI SRT-ondertitelbestanden en Skydio CSV-vluchtlogboeken.
Opent een bestandsselectievenster voor SRT- en CSV-bestanden.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="219"/>
        <source>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</source>
        <translation>Tijdsinterval tussen geëxtraheerde frames.
Bepaalt hoe vaak frames uit de video worden opgenomen.
Kleinere intervallen = meer frames geëxtraheerd (grotere uitvoer)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="224"/>
        <source>Time Interval (seconds):</source>
        <translation>Tijdsinterval (seconden):</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="236"/>
        <source>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</source>
        <translation>Stel het tijdsinterval in seconden in tussen frame-extracties.
• Bereik: 0,1 tot onbeperkt seconden
• Standaard: 5,0 seconden (extraheert 1 frame per 5 seconden)
• Lagere waarden: meer frames geëxtraheerd (bijv. 0,5s = 2 frames per seconde)
• Hogere waarden: minder frames geëxtraheerd (bijv. 10s = 1 frame per 10 seconden)
Aanbeveling: 3-5 seconden voor de meeste drone-beeldanalyses</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="301"/>
        <source>Start extracting frames from the video file.
Requirements:
• Video file must be selected
• Output folder must be selected
• Time interval must be set (default: 5 seconds)
The process will extract frames at the specified interval and save them as images.
If a metadata file (SRT or CSV) is provided, GPS metadata will be embedded in the extracted frames.</source>
        <translation>Begin met het extraheren van frames uit het videobestand.
Vereisten:
• Videobestand moet geselecteerd zijn
• Uitvoermap moet geselecteerd zijn
• Tijdsinterval moet zijn ingesteld (standaard: 5 seconden)
Het proces extraheert frames op het opgegeven interval en slaat ze op als afbeeldingen.
Als een metagegevensbestand (SRT of CSV) wordt opgegeven, worden GPS-metagegevens ingebed in de geëxtraheerde frames.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="320"/>
        <source>Start</source>
        <translation>Starten</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="351"/>
        <source>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</source>
        <translation>Annuleer het frame-extractieproces.
Stopt de bewerking onmiddellijk en keert terug naar de gereed-toestand.
Reeds geëxtraheerde frames worden opgeslagen in de uitvoermap.
Klik om de huidige parseerbewerking af te breken.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="360"/>
        <source> Cancel</source>
        <translation> Annuleren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="367"/>
        <source>cancel.png</source>
        <translation>cancel.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="397"/>
        <source>Progress and status output window.
Displays real-time information during frame extraction:
• Current frame being processed
• Frame timestamps and numbers
• GPS coordinates (if SRT file is provided)
• Progress percentage and completion status
• Any errors or warnings encountered
Shows total frames extracted when complete.</source>
        <translation>Voortgangs- en statusvenster.
Toont realtime informatie tijdens frame-extractie:
• Huidig frame dat wordt verwerkt
• Frametijdstempels en -nummers
• GPS-coördinaten (als SRT-bestand wordt opgegeven)
• Voortgangspercentage en voltooiingsstatus
• Eventuele fouten of waarschuwingen
Toont het totaal aantal geëxtraheerde frames bij voltooien.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="57"/>
        <source>Select a Video File</source>
        <translation>Een videobestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="72"/>
        <source>Select a Metadata File</source>
        <translation>Een metagegevensbestand selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="73"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv)</source>
        <translation>Metagegevensbestanden (*.srt *.csv);;SRT-bestanden (*.srt);;CSV-vluchtlogboeken (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="90"/>
        <source>Select Directory</source>
        <translation>Map selecteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="110"/>
        <source>Please set the video file and output directory.</source>
        <translation>Stel het videobestand en de uitvoermap in.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="115"/>
        <source>--- Starting video processing ---</source>
        <translation>--- Videoverwerking starten ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="164"/>
        <source>Confirmation</source>
        <translation>Bevestiging</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="165"/>
        <source>Are you sure you want to cancel the video processing in progress?</source>
        <translation>Weet u zeker dat u de lopende videoverwerking wilt annuleren?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="201"/>
        <source>--- Video Processing Completed ---</source>
        <translation>--- Videoverwerking voltooid ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="203"/>
        <source>{count} images created</source>
        <translation>{count} afbeeldingen gemaakt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="256"/>
        <source>Error Starting Processing</source>
        <translation>Fout bij starten van verwerking</translation>
    </message>
</context>
<context>
    <name>Viewer</name>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument :: Viewer - Gesponsord door TEXSAR</translation>
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
        <translation>Sneltoetsen en hulp bekijken</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="199"/>
        <source>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</source>
        <translation>Detectie-overlay op de afbeelding in-/uitschakelen.
Indien ingeschakeld, wordt de verwerkte afbeelding met gemarkeerde gedetecteerde objecten getoond.
Indien uitgeschakeld, wordt de originele onbewerkte afbeelding getoond.
Gebruik om de originele afbeelding met detectieresultaten te vergelijken.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="450"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="205"/>
        <source>Show Overlay</source>
        <translation>Overlay tonen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1242"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="225"/>
        <source>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</source>
        <translation>Galerijmodus in-/uitschakelen (G)
Toont alle AOI&apos;s van alle afbeeldingen in een rasterweergave</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="255"/>
        <source>Highlight Pixels of Interest(H)</source>
        <translation>Interessepixels markeren (H)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="277"/>
        <source>Show AOIs</source>
        <translation>AOI&apos;s tonen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1262"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="328"/>
        <source>Open Histogram</source>
        <translation>Histogram openen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="344"/>
        <source>Map with Image Locations (M)</source>
        <translation>Kaart met afbeeldingslocaties (M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="360"/>
        <source>North-Oriented View of Image (R)</source>
        <translation>Noord-georiënteerde weergave van afbeelding (R)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="376"/>
        <source>Adjust Image (Ctrl+H)</source>
        <translation>Afbeelding aanpassen (Ctrl+H)</translation>
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
        <translation>Afstand meten (Ctrl+M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="420"/>
        <source>ruler.png</source>
        <translation>ruler.png</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1981"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="427"/>
        <source>Person Size Reference (Ctrl+P)</source>
        <translation>Referentie voor persoonsgrootte (Ctrl+P)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="299"/>
        <source>Toggle the measurement ruler drawn over the selected AOI</source>
        <translation>Schakel de meetliniaal boven de geselecteerde AOI in of uit</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="439"/>
        <source>person.png</source>
        <translation>person.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="446"/>
        <source>Toggle Grid Review Mode (S) — sweep the image cell by cell; Shift+S for grid settings</source>
        <translation>Rasterbeoordelingsmodus in-/uitschakelen (S) — de afbeelding cel voor cel doorlopen; Shift+S voor rasterinstellingen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="461"/>
        <source>grid.png</source>
        <translation>grid.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="468"/>
        <source>Toggle Magnifying Glass (Middle Mouse)</source>
        <translation>Vergrootglas in-/uitschakelen (middelste muisknop)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="498"/>
        <source>magnify.png</source>
        <translation>magnify.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="512"/>
        <source>Map Export (KML / CalTopo)</source>
        <translation>Kaartexport (KML / CalTopo)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="542"/>
        <source>map.png</source>
        <translation>map.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="549"/>
        <source>Generate PDF Report</source>
        <translation>PDF-rapport genereren</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="579"/>
        <source>pdf.png</source>
        <translation>pdf.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="591"/>
        <source>Generate Zip Bundle</source>
        <translation>Zip-bundel genereren</translation>
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
        <translation>Verborgen afbeeldingen overslaan bij navigeren.
Indien ingeschakeld, slaan de knoppen Vorige/Volgende afbeeldingen over die als verborgen zijn gemarkeerd.
Gebruik om u te concentreren op afbeeldingen die niet zijn beoordeeld of voor uitsluiting zijn gemarkeerd.
Sneltoets: H om de huidige afbeelding te verbergen/te tonen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="652"/>
        <source>Skip Hidden</source>
        <translation>Verborgen overslaan</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="691"/>
        <source>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</source>
        <translation>Markeer huidige afbeelding als verborgen.
Verborgen afbeeldingen kunnen worden uitgesloten van rapporten, exports en navigatie.
Gebruik dit om afbeeldingen met valse positieven of zonder relevante detecties uit de weergave te halen.
Wanneer &quot;Verborgen overslaan&quot; is ingeschakeld, worden verborgen afbeeldingen tijdens navigatie overgeslagen.
Sneltoets: H</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="698"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="718"/>
        <source>Hide Image</source>
        <translation>Afbeelding verbergen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="710"/>
        <source>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</source>
        <translation>Toont de naam van de momenteel verborgen afbeelding.
Wanneer een afbeelding als verborgen is gemarkeerd, verschijnt hier de bestandsnaam.
Verborgen afbeeldingen worden uitgesloten van navigatie wanneer &quot;Verborgen overslaan&quot; is ingeschakeld.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="746"/>
        <source>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</source>
        <translation>Spring direct naar een specifiek afbeeldingsnummer.
Voer een afbeeldingsnummer in en druk op Enter om direct te navigeren.
Nuttig voor het beoordelen van specifieke afbeeldingen of het terugkeren naar een genoteerde locatie.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="751"/>
        <source>Jump To:</source>
        <translation>Springen naar:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="776"/>
        <source>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</source>
        <translation>Voer een afbeeldingsnummer in (1 tot totaal) en druk op Enter.
Navigeer snel naar elke afbeelding in de analyseresultaten.
Voorbeeld: typ &quot;25&quot; en druk op Enter om naar afbeelding #25 te springen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="790"/>
        <source>Jump to a specific AOI by its run-wide number.
Enter an AOI number and press Enter to select and scroll to it.</source>
        <translation>Spring naar een specifieke AOI via het nummer binnen de hele run.
Voer een AOI-nummer in en druk op Enter om deze te selecteren en ernaartoe te scrollen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="794"/>
        <source>Go to AOI #:</source>
        <translation>Ga naar AOI-nr.:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="819"/>
        <source>Enter an AOI number and press Enter.
Selects that AOI and scrolls it into view in the gallery or single-image list.</source>
        <translation>Voer een AOI-nummer in en druk op Enter.
Selecteert die AOI en scrollt ernaartoe in de galerij of de lijst voor één afbeelding.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="832"/>
        <source>Previous Image</source>
        <translation>Vorige afbeelding</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="839"/>
        <source>previous.png</source>
        <translation>previous.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="854"/>
        <source>Next Image</source>
        <translation>Volgende afbeelding</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="861"/>
        <source>next.png</source>
        <translation>next.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1004"/>
        <source>Filter AOIs by color and pixel area</source>
        <translation>AOI&apos;s filteren op kleur en pixelgebied</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1076"/>
        <source>Sort By</source>
        <translation>Sorteren op</translation>
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
        <translation>Sorteer interessegebieden (AOI&apos;s) in de lijst.
Kies hoe gedetecteerde objecten te ordenen:
• Pixelgebied: sorteren op grootte (grootste tot kleinste)
• Afstand: sorteren op afstand vanaf het midden van de afbeelding of een referentiepunt
• Kleur: groeperen op vergelijkbare kleuren
• Detectievolgorde: oorspronkelijke volgorde uit de analyse
Sorteren helpt bij het prioriteren van de beoordeling van grotere of nabije objecten.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1176"/>
        <source>Open</source>
        <translation>Openen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="132"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Geautomatiseerd drone-beeldanalyse-instrument v{version} - Gesponsord door TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="144"/>
        <source>Reading result file...</source>
        <translation>Resultaatbestand lezen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="161"/>
        <source>Checking image dimensions ({n} images)...</source>
        <translation>Afbeeldingsafmetingen controleren ({n} afbeeldingen)...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="171"/>
        <source>Validating image paths...</source>
        <translation>Afbeeldingspaden valideren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="178"/>
        <source>Load Results Failed</source>
        <translation>Laden van resultaten mislukt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="180"/>
        <source>Cannot load results without valid image and mask locations.

The viewer will now close.</source>
        <translation>Kan resultaten niet laden zonder geldige afbeeldings- en maskerlocaties.

De viewer wordt nu gesloten.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="187"/>
        <source>Scanning source folder for full flight...</source>
        <translation>Bronmap scannen op volledige vlucht...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="203"/>
        <source>Initialising controllers...</source>
        <translation>Controllers initialiseren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="214"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1455"/>
        <source>Skip Hidden ({count}) </source>
        <translation>Verborgen overslaan ({count}) </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="246"/>
        <source>Loading detection results from {n} images...</source>
        <translation>Detectieresultaten van {n} afbeeldingen laden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="285"/>
        <source>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</source>
        <translation>Afbeeldingsmetagegevens en -informatie.
Klik op GPS-coördinaten om te kopiëren, delen of te openen in kaarttoepassingen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="317"/>
        <source>Loading first image...</source>
        <translation>Eerste afbeelding laden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="332"/>
        <source>Preparing thumbnails...</source>
        <translation>Miniaturen voorbereiden...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="648"/>
        <source>No Dataset</source>
        <translation>Geen dataset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="649"/>
        <source>No dataset is currently loaded.</source>
        <translation>Er is momenteel geen dataset geladen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="656"/>
        <source>Generate Cache</source>
        <translation>Cache genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="658"/>
        <source>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</source>
        <translation>Hiermee worden miniaturen- en kleurcaches voor alle AOI&apos;s in deze dataset opnieuw gegenereerd.

Dit kan enkele minuten duren, afhankelijk van de grootte van de dataset.

Doorgaan?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="671"/>
        <source>Initializing cache generation...</source>
        <translation>Cachegeneratie initialiseren...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="672"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="677"/>
        <source>Generating Cache</source>
        <translation>Cache genereren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="714"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="715"/>
        <source>Failed to start cache generation:
{error}</source>
        <translation>Kan cachegeneratie niet starten:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="733"/>
        <source>Cache Generated</source>
        <translation>Cache gegenereerd</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="735"/>
        <source>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</source>
        <translation>Cachegeneratie voltooid!

{images} afbeeldingen verwerkt met {aois} AOI&apos;s.

De viewer laadt nu miniaturen en kleuren veel sneller.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="766"/>
        <source>Cache Generation Error</source>
        <translation>Fout bij cachegeneratie</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="768"/>
        <source>An error occurred during cache generation:

{error}</source>
        <translation>Er is een fout opgetreden tijdens de cachegeneratie:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="954"/>
        <source>AOI Not Visible</source>
        <translation>AOI niet zichtbaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="956"/>
        <source>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</source>
        <translation>De AOI op de cursorpositie kan niet worden geselecteerd omdat deze momenteel verborgen is vanwege actieve filters.

Wis of pas uw filters aan om deze AOI te selecteren.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1121"/>
        <source>Update Image Dimensions</source>
        <translation>Afbeeldingsafmetingen bijwerken</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1123"/>
        <source>This dataset is missing image dimensions needed for heatmap filtering ({count} images).

Would you like to read dimensions from the image files and update the results file?</source>
        <translation>Deze dataset mist afbeeldingsafmetingen die nodig zijn voor heatmap-filtering ({count} afbeeldingen).

Wilt u de afmetingen uit de afbeeldingsbestanden lezen en het resultatenbestand bijwerken?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1162"/>
        <source>Reading image dimensions ({done}/{total})...</source>
        <translation>Afbeeldingsafmetingen lezen ({done}/{total})...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1253"/>
        <source>Show Pixels of Interest (H or Ctrl+I)</source>
        <translation>Interessepixels tonen (H of Ctrl+I)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1268"/>
        <source>Toggle AOI Circles</source>
        <translation>AOI-cirkels in-/uitschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1275"/>
        <source>Toggle AOI Ruler</source>
        <translation>AOI-liniaal in-/uitschakelen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1641"/>
        <source>Missing Dependency</source>
        <translation>Ontbrekende afhankelijkheid</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1643"/>
        <source>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</source>
        <translation>De qimage2ndarray-module is vereist voor de opschaalfunctie.
Installeer deze met: pip install qimage2ndarray</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1652"/>
        <source>Upscale Error</source>
        <translation>Opschaalfout</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1654"/>
        <source>An error occurred while opening the upscale dialog:
{error}</source>
        <translation>Er is een fout opgetreden bij het openen van het opschaaldialoogvenster:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1985"/>
        <source>Person Size Reference is unavailable: no GSD for this image</source>
        <translation>Referentie voor persoonsgrootte is niet beschikbaar: geen GSD voor deze afbeelding</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2082"/>
        <source>Unknown Reviewer</source>
        <translation>Onbekende beoordelaar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2145"/>
        <source>Loading gallery...</source>
        <translation>Galerij laden...</translation>
    </message>
</context>
<context>
    <name>WaldoPrePassDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="58"/>
        <source>Preparing WALDO Images</source>
        <translation>WALDO-afbeeldingen voorbereiden</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="70"/>
        <source>Synthesising WALDO metadata...</source>
        <translation>WALDO-metadata genereren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="82"/>
        <source>Initialising...</source>
        <translation>Initialiseren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="93"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="96"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="146"/>
        <source>WALDO Pre-Pass Complete</source>
        <translation>WALDO-prepass voltooid</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="147"/>
        <source>WALDO Pre-Pass Cancelled</source>
        <translation>WALDO-prepass geannuleerd</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="154"/>
        <source>Processed:        {n}</source>
        <translation>Verwerkt:        {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="155"/>
        <source>Already up-to-date: {n}</source>
        <translation>Al bijgewerkt: {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="156"/>
        <source>Skipped (non-WALDO): {n}</source>
        <translation>Overgeslagen (niet-WALDO): {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="157"/>
        <source>Errors:           {n}</source>
        <translation>Fouten:          {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="160"/>
        <source>Per-image errors:</source>
        <translation>Fouten per afbeelding:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="174"/>
        <source>Cancelling...</source>
        <translation>Annuleren...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="175"/>
        <source>Cancellation requested...</source>
        <translation>Annulering aangevraagd...</translation>
    </message>
</context>
<context>
    <name>WingtraDataDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="44"/>
        <source>Wingtra Data Import</source>
        <translation>Wingtra-gegevensimport</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="54"/>
        <source>Import Summary</source>
        <translation>Importsamenvatting</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="58"/>
        <source>&lt;b&gt;Matched images:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV entries without match:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Result images without CSV data:&lt;/b&gt; {unmatched_images}</source>
        <translation>&lt;b&gt;Overeenkomende afbeeldingen:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV-records zonder overeenkomst:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Resultaatafbeeldingen zonder CSV-gegevens:&lt;/b&gt; {unmatched_images}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="73"/>
        <source>Altitude &amp; GSD</source>
        <translation>Hoogte &amp; GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="78"/>
        <source>&lt;b&gt;AGL computed from terrain:&lt;/b&gt; {agl_count} of {matched_count} images&lt;br&gt;&lt;br&gt;Per-image AGL is derived from the CSV altitude (ASL) minus terrain elevation at each GPS location. GSD will be calculated automatically using the camera sensor data and focal length.</source>
        <translation>&lt;b&gt;AGL berekend uit terrein:&lt;/b&gt; {agl_count} van {matched_count} afbeeldingen&lt;br&gt;&lt;br&gt;De AGL per afbeelding is afgeleid van de CSV-hoogte (ASL) min de terreinhoogte op elke GPS-locatie. GSD wordt automatisch berekend met behulp van de camerasensorgegevens en de brandpuntsafstand.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="89"/>
        <source>&lt;b&gt;Terrain data unavailable&lt;/b&gt; - AGL could not be computed.&lt;br&gt;&lt;br&gt;Orientation (yaw/pitch/roll) will still be applied from the CSV. GSD and altitude displays require terrain data or a manual altitude override (Shift+O) after import.</source>
        <translation>&lt;b&gt;Terreingegevens niet beschikbaar&lt;/b&gt; - AGL kon niet worden berekend.&lt;br&gt;&lt;br&gt;Oriëntatie (yaw/pitch/roll) wordt nog steeds toegepast vanuit het CSV-bestand. GSD- en hoogteweergaven vereisen terreingegevens of een handmatige hoogteoverschrijving (Shift+O) na import.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="106"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="110"/>
        <source>Apply Wingtra Data</source>
        <translation>Wingtra-gegevens toepassen</translation>
    </message>
</context>
<context>
    <name>ZipExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="130"/>
        <source>Save Zip File</source>
        <translation>Zip-bestand opslaan</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="132"/>
        <source>Zip files (*.zip)</source>
        <translation>Zip-bestanden (*.zip)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="163"/>
        <source>No images to export</source>
        <translation>Geen afbeeldingen om te exporteren</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="397"/>
        <source>ZIP file created</source>
        <translation>Zip-bestand gemaakt</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="403"/>
        <source>Failed to generate Zip file: {error}</source>
        <translation>Kan zip-bestand niet genereren: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="424"/>
        <source>Error</source>
        <translation>Fout</translation>
    </message>
</context>
<context>
    <name>ZipExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="18"/>
        <source>ZIP Export Options</source>
        <translation>Zip-exportopties</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="26"/>
        <source>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</source>
        <translation>Kies wat u wilt exporteren:

- Native: oorspronkelijke afbeeldingen, TIFF-maskers en XML (paden draagbaar gemaakt).
- Augmented: wat u in de viewer ziet (AOI&apos;s/POI&apos;s), met behoud van EXIF/XMP.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="34"/>
        <source>Export Native data (original files + XML)</source>
        <translation>Native gegevens exporteren (originele bestanden + XML)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="35"/>
        <source>Export Augmented images (viewer overlays + metadata)</source>
        <translation>Augmented afbeeldingen exporteren (viewer-overlays + metagegevens)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="50"/>
        <source>Include images without flagged AOIs</source>
        <translation>Afbeeldingen zonder gemarkeerde AOI&apos;s opnemen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="53"/>
        <source>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</source>
        <translation>Indien uitgevinkt, worden alleen afbeeldingen met ten minste één gemarkeerde AOI geëxporteerd.
Indien aangevinkt, worden alle afbeeldingen geëxporteerd, ongeacht de status van gemarkeerde AOI&apos;s.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="59"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="60"/>
        <source>Cancel</source>
        <translation>Annuleren</translation>
    </message>
</context>
</TS>
