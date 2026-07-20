<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="it_IT">
<context>
    <name>AIPersonDetector</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="27"/>
        <source>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</source>
        <translation>Soglia di confidenza per il rilevamento persone AI.
Controlla il livello minimo di confidenza richiesto per segnalare il rilevamento di una persona.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="31"/>
        <source>Confidence Threshold</source>
        <translation>Soglia di Confidenza</translation>
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
        <translation>Regola la soglia di confidenza per il rilevamento delle persone.
• Intervallo: da 0% a 100% (cursore da -1 a 100, -1 visualizzato come 0%)
• Predefinito: 50%
Il modello AI assegna un punteggio di confidenza a ogni rilevamento di persona:
• Valori bassi (0-30%): accetta rilevamenti a bassa confidenza (più rilevamenti, più falsi positivi)
• Valori medi (31-60%): rilevamento bilanciato (consigliato per la maggior parte dei casi)
• Valori alti (61-100%): accetta solo rilevamenti ad alta confidenza (meno rilevamenti, meno falsi positivi)
La confidenza rappresenta la certezza del modello AI che un oggetto rilevato sia una persona.
Inizia con il 50% e regola in base ai tuoi requisiti di precisione.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="81"/>
        <source>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</source>
        <translation>Percentuale della soglia di confidenza attuale.
Visualizza il valore selezionato sul cursore della confidenza (0-100%).
I rilevamenti al di sotto di questo livello di confidenza verranno filtrati.</translation>
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
        <translation>Informazioni sullo stato e sulla disponibilità della GPU.
Mostra se l&apos;accelerazione GPU è disponibile per il rilevamento persone AI.
• GPU disponibile: il rilevamento AI utilizzerà la GPU per un&apos;elaborazione più rapida
• Solo CPU: il rilevamento AI utilizzerà la CPU (più lento ma comunque funzionale)
L&apos;accelerazione GPU migliora significativamente la velocità di elaborazione per i modelli AI.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="107"/>
        <source>GPU Label</source>
        <translation>Etichetta GPU</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="54"/>
        <source>Person Detection</source>
        <translation>Rilevamento Persone</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="55"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Elaborazione</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="56"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="57"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Pulizia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="78"/>
        <source>Model</source>
        <translation>Modello</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="80"/>
        <source>Force CPU (disable DirectML)</source>
        <translation>Forza CPU (disattiva DirectML)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="81"/>
        <source>Use 1024 model (higher quality, slower)</source>
        <translation>Usa modello 1024 (qualità superiore, più lento)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="86"/>
        <source>Detection</source>
        <translation>Rilevamento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="91"/>
        <source>Confidence Threshold:</source>
        <translation>Soglia di Confidenza:</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="81"/>
        <source>GPU Not Available</source>
        <translation>GPU non disponibile</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="87"/>
        <source>GPU Available</source>
        <translation>GPU disponibile</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="91"/>
        <source>FPS: {fps} | Processing: {ms}ms</source>
        <translation>FPS: {fps} | Elaborazione: {ms} ms</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="96"/>
        <source>{status} | Tile fallback active</source>
        <translation>{status} | Fallback tile attivo</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizard</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="40"/>
        <source>How confident should ADIAT be before marking something as a person?</source>
        <translation>Quanto dovrebbe essere sicura ADIAT prima di contrassegnare qualcosa come persona?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="56"/>
        <source>Note: A higher setting may increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta può aumentare i falsi positivi.</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizardController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="33"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="52"/>
        <source>Very 
Confident</source>
        <translation>Molto 
Sicuro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="34"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="53"/>
        <source>Confident</source>
        <translation>Sicuro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="35"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="54"/>
        <source>Balanced</source>
        <translation>Bilanciato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="36"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="55"/>
        <source>Permissive</source>
        <translation>Permissivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="37"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="56"/>
        <source>Very 
Permissive</source>
        <translation>Molto 
Permissivo</translation>
    </message>
</context>
<context>
    <name>AOICommentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="27"/>
        <source>AOI Comment</source>
        <translation>Commento AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="37"/>
        <source>Add a comment for this flagged AOI (max 256 characters):</source>
        <translation>Aggiungi un commento per questa AOI contrassegnata (max 256 caratteri):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="44"/>
        <source>Enter your comment here...</source>
        <translation>Inserisci qui il tuo commento...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="57"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="59"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>AOIController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="366"/>
        <source>No AOI #{number} in this analysis.</source>
        <translation>Nessuna AOI #{number} in questa analisi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="379"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="389"/>
        <source>AOI #{number} is hidden by the current filter.</source>
        <translation>L&apos;AOI #{number} è nascosta dal filtro corrente.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="685"/>
        <source>Comment saved</source>
        <translation>Commento salvato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="687"/>
        <source>Comment cleared</source>
        <translation>Commento cancellato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="776"/>
        <source>Copy Data</source>
        <translation>Copia Dati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="782"/>
        <source>Find Similar AOIs</source>
        <translation>Trova AOI simili</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="885"/>
        <source>AOI data copied</source>
        <translation>Dati AOI copiati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="972"/>
        <source>Invalid image index</source>
        <translation>Indice immagine non valido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="977"/>
        <source>Invalid AOI index</source>
        <translation>Indice AOI non valido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1040"/>
        <source>Could not calculate AOI location. Diagnostic info copied to clipboard!</source>
        <translation>Impossibile calcolare la posizione dell&apos;AOI. Informazioni diagnostiche copiate negli appunti!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1046"/>
        <source>Could not calculate AOI location</source>
        <translation>Impossibile calcolare la posizione dell&apos;AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1503"/>
        <source>Temperature sorting unavailable (no thermal data)</source>
        <translation>Ordinamento per temperatura non disponibile (nessun dato termico)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1855"/>
        <source>Cannot Delete AOI</source>
        <translation>Impossibile eliminare l&apos;AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1857"/>
        <source>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</source>
        <translation>Solo le AOI create manualmente possono essere eliminate. Le AOI rilevate dagli algoritmi non possono essere eliminate.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1866"/>
        <source>Delete AOI</source>
        <translation>Elimina AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1868"/>
        <source>Are you sure you want to delete this AOI? This action cannot be undone.</source>
        <translation>Sei sicuro di voler eliminare questa AOI? Questa azione non può essere annullata.</translation>
    </message>
</context>
<context>
    <name>AOICreationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="23"/>
        <source>Create AOI</source>
        <translation>Crea AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="31"/>
        <source>Create AOI?</source>
        <translation>Creare AOI?</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="39"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="43"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>AOIFilterDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="74"/>
        <source>Filter AOIs</source>
        <translation>Filtra AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="91"/>
        <source>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</source>
        <translation>Filtra le Aree di Interesse per stato contrassegnato, commenti, colore e/o area in pixel:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="96"/>
        <source>Flagged AOIs</source>
        <translation>AOI Contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="99"/>
        <source>Show Only Flagged AOIs</source>
        <translation>Mostra solo AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="103"/>
        <source>Only AOIs marked with a flag will be displayed</source>
        <translation>Verranno visualizzate solo le AOI contrassegnate con una bandierina</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="111"/>
        <source>Comment Filter</source>
        <translation>Filtro Commenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="115"/>
        <source>Enable Comment Filter</source>
        <translation>Abilita Filtro Commenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="122"/>
        <source>Pattern:</source>
        <translation>Modello:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="125"/>
        <source>e.g., damage or crack</source>
        <translation>es. danno o crepa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="133"/>
        <source>Case-insensitive substring match (e.g. &quot;blue&quot; matches &quot;blueface&quot;)</source>
        <translation>Corrispondenza di sottostringa, ignora maiuscole/minuscole (es. &quot;blue&quot; corrisponde a &quot;blueface&quot;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="137"/>
        <source>Only AOIs with non-empty comments matching the pattern will be shown</source>
        <translation>Verranno mostrate solo le AOI con commenti non vuoti che corrispondono al modello</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="145"/>
        <source>Color Filter</source>
        <translation>Filtro Colore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="149"/>
        <source>Enable Color Filter</source>
        <translation>Abilita Filtro Colore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="156"/>
        <source>Show Only This Color</source>
        <translation>Mostra Solo Questo Colore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="157"/>
        <source>Exclude This Color</source>
        <translation>Escludi Questo Colore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="174"/>
        <source>Target Hue:</source>
        <translation>Tonalità Obiettivo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="176"/>
        <source>Select Color</source>
        <translation>Seleziona Colore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="188"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="556"/>
        <source>No color selected</source>
        <translation>Nessun colore selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="196"/>
        <source>Hue Range (±):</source>
        <translation>Intervallo Tonalità (±):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="214"/>
        <source>AOIs with hue within ±range of target will be shown</source>
        <translation>Verranno mostrate le AOI con tonalità entro l&apos;intervallo ± dell&apos;obiettivo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="222"/>
        <source>Pixel Area Filter</source>
        <translation>Filtro Area Pixel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="226"/>
        <source>Enable Pixel Area Filter</source>
        <translation>Abilita Filtro Area Pixel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="233"/>
        <source>Minimum Area (px):</source>
        <translation>Area Minima (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="247"/>
        <source>Maximum Area (px):</source>
        <translation>Area Massima (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="263"/>
        <source>Temperature Filter</source>
        <translation>Filtro Temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="267"/>
        <source>Enable Temperature Filter</source>
        <translation>Abilita Filtro Temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="321"/>
        <source>Temperature filtering unavailable (no thermal data)</source>
        <translation>Filtro temperatura non disponibile (nessun dato termico)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="336"/>
        <source>Spatial Filters</source>
        <translation>Filtri Spaziali</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="341"/>
        <source>Detection Density Heatmap</source>
        <translation>Heatmap della Densità dei Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="347"/>
        <source>Off</source>
        <translation>Off</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="348"/>
        <source>Filter Hot Zones</source>
        <translation>Filtra Zone Critiche</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="349"/>
        <source>Show Hot Zones Only</source>
        <translation>Mostra Solo le Zone Critiche</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="374"/>
        <source>Threshold:</source>
        <translation>Soglia:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="392"/>
        <source>View Heatmap</source>
        <translation>Visualizza Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="405"/>
        <source>Heatmap filtering unavailable (image dimensions not in dataset)</source>
        <translation>Filtraggio per heatmap non disponibile (dimensioni immagine non presenti nel dataset)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="418"/>
        <source>Image Mask Filter</source>
        <translation>Filtro Maschera Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="422"/>
        <source>Enable Image Mask Filter</source>
        <translation>Abilita Filtro Maschera Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="429"/>
        <source>Show Only Detections in Mask</source>
        <translation>Mostra Solo i Rilevamenti nella Maschera</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="430"/>
        <source>Exclude Detections in Mask</source>
        <translation>Escludi i Rilevamenti nella Maschera</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="449"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="630"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="690"/>
        <source>No mask image selected</source>
        <translation>Nessuna maschera immagine selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="454"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="458"/>
        <source>Clear</source>
        <translation>Cancella</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="465"/>
        <source>White regions = areas of interest. Mask is scaled to each image&apos;s dimensions.</source>
        <translation>Le aree bianche = aree di interesse. La maschera viene scalata in base alle dimensioni di ciascuna immagine.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="483"/>
        <source>Clear All Filters</source>
        <translation>Cancella Tutti i Filtri</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="489"/>
        <source>Apply</source>
        <translation>Applica</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="494"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="531"/>
        <source>Select Target Hue</source>
        <translation>Seleziona Tonalità Obiettivo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="607"/>
        <source>Select Mask Image</source>
        <translation>Seleziona Maschera Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="609"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)</source>
        <translation>Immagini (*.png *.jpg *.jpeg *.bmp *.tiff);;Tutti i file (*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="618"/>
        <source>Invalid Image</source>
        <translation>Immagine Non Valida</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="619"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Impossibile caricare l&apos;immagine selezionata. Scegli un file immagine valido.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="637"/>
        <source>AOIs in high-density zones (above threshold) will be hidden</source>
        <translation>Le AOI nelle zone ad alta densità (oltre la soglia) verranno nascoste</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="640"/>
        <source>Only AOIs in high-density zones (above threshold) will be shown</source>
        <translation>Verranno mostrate solo le AOI nelle zone ad alta densità (oltre la soglia)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="643"/>
        <source>Heatmap spatial filtering is disabled</source>
        <translation>Il filtraggio spaziale tramite heatmap è disabilitato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="649"/>
        <source>Heatmap</source>
        <translation>Heatmap</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="650"/>
        <source>No heatmap data available. Ensure image dimensions are present in the dataset.</source>
        <translation>Nessun dato heatmap disponibile. Assicurati che le dimensioni delle immagini siano presenti nel dataset.</translation>
    </message>
</context>
<context>
    <name>AOINeighborGalleryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="338"/>
        <source>AOI in Neighboring Images</source>
        <translation>AOI nelle immagini vicine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="389"/>
        <source>Reset View</source>
        <translation>Ripristina Vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="392"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Ripristina lo zoom e adatta tutte le miniature alla vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="399"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
</context>
<context>
    <name>AOINeighborTrackingController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="120"/>
        <source>No AOI Selected</source>
        <translation>Nessuna AOI selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="121"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Seleziona prima un&apos;AOI cliccandoci sopra nel pannello delle miniature.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="155"/>
        <source>Cannot Calculate GPS</source>
        <translation>Impossibile calcolare il GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="157"/>
        <source>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</source>
        <translation>Impossibile calcolare le coordinate GPS per questa AOI.

Ciò potrebbe essere dovuto alla mancanza di metadati dell&apos;immagine (GPS, altitudine o informazioni sulla telecamera).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="167"/>
        <source>Searching for AOI in neighboring images...</source>
        <translation>Ricerca dell&apos;AOI nelle immagini vicine...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="168"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="172"/>
        <source>Tracking AOI</source>
        <translation>Tracciamento AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="208"/>
        <source>Tracking Error</source>
        <translation>Errore di tracciamento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="209"/>
        <source>An error occurred while tracking the AOI:
{error}</source>
        <translation>Si è verificato un errore durante il tracciamento dell&apos;AOI:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="234"/>
        <source>No Neighbors Found</source>
        <translation>Nessuna immagine vicina trovata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="235"/>
        <source>The AOI was not found in any neighboring images.</source>
        <translation>L&apos;AOI non è stata trovata in nessuna delle immagini vicine.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="260"/>
        <source>Search Error</source>
        <translation>Errore di ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="261"/>
        <source>An error occurred during the search:
{error}</source>
        <translation>Si è verificato un errore durante la ricerca:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="312"/>
        <source>Display Error</source>
        <translation>Errore di visualizzazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="313"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Si è verificato un errore durante la visualizzazione dei risultati:
{error}</translation>
    </message>
</context>
<context>
    <name>AOISimilarityController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="134"/>
        <source>No AOI Selected</source>
        <translation>Nessuna AOI selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="135"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Seleziona prima un&apos;AOI cliccandoci sopra nel pannello delle miniature.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="152"/>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="246"/>
        <source>Similarity Search Error</source>
        <translation>Errore nella ricerca di similarità</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="153"/>
        <source>An error occurred while starting the similarity search:
{error}</source>
        <translation>Si è verificato un errore durante l&apos;avvio della ricerca di similarità:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="164"/>
        <source>Analyzing AOIs for visual similarity...</source>
        <translation>Analisi delle AOI per similarità visiva...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="165"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="169"/>
        <source>Find Similar AOIs</source>
        <translation>Trova AOI simili</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="200"/>
        <source>Analyzing AOI {done} of {total}...</source>
        <translation>Analisi AOI {done} di {total}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="215"/>
        <source>No Similar AOIs</source>
        <translation>Nessuna AOI simile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="216"/>
        <source>No other AOIs could be analyzed for similarity.</source>
        <translation>Non è stato possibile analizzare altre AOI per la similarità.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="247"/>
        <source>The similarity search could not be completed:
{error}</source>
        <translation>Non è stato possibile completare la ricerca di similarità:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="314"/>
        <source>Display Error</source>
        <translation>Errore di visualizzazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="315"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Si è verificato un errore durante la visualizzazione dei risultati:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="367"/>
        <source>Flagged {count} AOI(s)</source>
        <translation>{count} AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="370"/>
        <source>Removed flag from {count} AOI(s)</source>
        <translation>Contrassegno rimosso da {count} AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="402"/>
        <source>Comment saved on {count} AOI(s)</source>
        <translation>Commento salvato su {count} AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="405"/>
        <source>Comment cleared on {count} AOI(s)</source>
        <translation>Commento cancellato su {count} AOI</translation>
    </message>
</context>
<context>
    <name>AOISimilarityResultsDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="442"/>
        <source>Similar AOIs</source>
        <translation>AOI simili</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="470"/>
        <source>Top {shown} of {total} AOIs ranked by similarity to {reference}. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to jump to that AOI.</source>
        <translation>Le prime {shown} di {total} AOI ordinate per similarità con {reference}. Usa la rotellina del mouse per lo zoom, trascina con il tasto destro per la panoramica. Fai clic su una miniatura per passare a quell&apos;AOI.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="491"/>
        <source>Select All</source>
        <translation>Seleziona tutto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="495"/>
        <source>Clear Selection</source>
        <translation>Cancella selezione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="547"/>
        <source>{count} selected</source>
        <translation>{count} selezionate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="505"/>
        <source>Flag</source>
        <translation>Contrassegna</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="506"/>
        <source>Flag all checked AOIs</source>
        <translation>Contrassegna tutte le AOI spuntate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="511"/>
        <source>Unflag</source>
        <translation>Rimuovi contrassegno</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="512"/>
        <source>Remove the flag from all checked AOIs</source>
        <translation>Rimuovi il contrassegno da tutte le AOI spuntate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="517"/>
        <source>Comment...</source>
        <translation>Commento...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="518"/>
        <source>Add or edit the comment on all checked AOIs</source>
        <translation>Aggiungi o modifica il commento su tutte le AOI spuntate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="529"/>
        <source>Reset View</source>
        <translation>Ripristina Vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="532"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Ripristina lo zoom e adatta tutte le miniature alla vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="537"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="572"/>
        <source>AOI #{number}</source>
        <translation>AOI #{number}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="573"/>
        <source>the selected AOI</source>
        <translation>l&apos;AOI selezionata</translation>
    </message>
</context>
<context>
    <name>AOIUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="250"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="346"/>
        <source>AOI Information
Right-click to copy data to clipboard</source>
        <translation>Informazioni AOI
Fai clic destro per copiare i dati negli appunti</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="256"/>
        <source>

Score Type: {type}
Raw Score: {score} ({method})</source>
        <translation>

Tipo Punteggio: {type}
Punteggio Grezzo: {score} ({method})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="320"/>
        <source>Confidence Score: {score:.1f}%</source>
        <translation>Punteggio di Confidenza: {score:.1f}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Unflag AOI</source>
        <translation>Rimuovi contrassegno AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Flag AOI</source>
        <translation>Contrassegna AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="403"/>
        <source>Comment:
{comment}

Click to edit comment</source>
        <translation>Commento:
{comment}

Clicca per modificare il commento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="411"/>
        <source>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</source>
        <translation>Ancora nessun commento.
Clicca per aggiungere un commento per questa AOI.

Usa i commenti per annotare dettagli importanti, osservazioni,
o azioni necessarie per questo rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="428"/>
        <source>Calculate and show GPS location for this AOI</source>
        <translation>Calcola e mostra la posizione GPS per questa AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="446"/>
        <source>Delete this AOI</source>
        <translation>Elimina questa AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Area</source>
        <translation>Area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Areas</source>
        <translation>Aree</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="486"/>
        <source>{filtered} of {total} {label}</source>
        <translation>{filtered} di {total} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="495"/>
        <source>Area of Interest</source>
        <translation>Area di Interesse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="497"/>
        <source>Areas of Interest</source>
        <translation>Aree di Interesse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="500"/>
        <source>{count} {label}</source>
        <translation>{count} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="643"/>
        <source>Loading AOIs...</source>
        <translation>Caricamento AOI...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="684"/>
        <source>Loading AOIs... ({current}/{total})</source>
        <translation>Caricamento AOI... ({current}/{total})</translation>
    </message>
</context>
<context>
    <name>AlertManager</name>
    <message>
        <location filename="../app/core/services/AlertService.py" line="294"/>
        <source>ADIAT - Color Detection Alerts</source>
        <translation>ADIAT - Avvisi Rilevamento Colore</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="569"/>
        <source>ADIAT - Color Detection Alert</source>
        <translation>ADIAT - Avviso Rilevamento Colore</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="610"/>
        <source>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</source>
        <translation>Rilevati {count} oggetti
Confidenza media: {avg_confidence:.2f}
Area totale: {area:.0f} pixel
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="620"/>
        <source>
Details:
</source>
        <translation>
Dettagli:
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
        <translation>ADIAT - Avviso Rilevamento</translation>
    </message>
</context>
<context>
    <name>AlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmParametersPage.py" line="166"/>
        <source>{algorithm} Algorithm Settings</source>
        <translation>Impostazioni Algoritmo {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlgorithmSelectionPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="92"/>
        <source>Are you using thermal images?</source>
        <translation>Stai usando immagini termiche?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="156"/>
        <source>Are you looking for anomalies within a specific temperature range?</source>
        <translation>Stai cercando anomalie entro un intervallo di temperatura specifico?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="159"/>
        <source>Do you specifically want to detect people?</source>
        <translation>Vuoi rilevare specificamente persone?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="168"/>
        <source>Do you want to detect anomalies relative to local surroundings?</source>
        <translation>Vuoi rilevare anomalie rispetto alle aree circostanti locali?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="185"/>
        <source>Are you trying to find a specific color?</source>
        <translation>Stai cercando un colore specifico?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="190"/>
        <source>Do you want to manually adjust the color range?</source>
        <translation>Vuoi regolare manualmente l&apos;intervallo di colore?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="193"/>
        <source>Do your images contain complex backgrounds or structures?</source>
        <translation>Le tue immagini contengono sfondi o strutture complesse?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="200"/>
        <source>Do your images include shadows or areas with uneven lighting?</source>
        <translation>Le tue immagini includono ombre o aree con illuminazione non uniforme?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="226"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Algoritmo selezionato: {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlignImageController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="46"/>
        <source>No image available to align</source>
        <translation>Nessuna immagine disponibile per l&apos;allineamento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="52"/>
        <source>This image has no GPS data and cannot be aligned</source>
        <translation>Questa immagine non contiene dati GPS e non può essere allineata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="84"/>
        <source>Could not save the alignment</source>
        <translation>Impossibile salvare l&apos;allineamento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="95"/>
        <source>Image alignment saved</source>
        <translation>Allineamento immagine salvato</translation>
    </message>
</context>
<context>
    <name>AlignImageDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="53"/>
        <source>This saved alignment looks mirrored - re-place each corner handle on its matching photo corner (coloured squares).</source>
        <translation>Questo allineamento salvato sembra speculare: riposiziona ogni maniglia d&apos;angolo sull&apos;angolo corrispondente della foto (quadrati colorati).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="60"/>
        <source>Align Image</source>
        <translation>Allinea immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="130"/>
        <source>Rotate the drone image to line it up with the map. The small coloured squares mark the photo&apos;s corners - drag each corner handle onto the map where its matching-coloured photo corner belongs. For extra accuracy, add tie points: put the IMAGE end on a feature in the drone photo and the MAP end on the same feature on the map.</source>
        <translation>Ruota l&apos;immagine del drone per allinearla alla mappa. I piccoli quadrati colorati segnano gli angoli della foto: trascina ogni maniglia d&apos;angolo sulla mappa nel punto in cui deve trovarsi l&apos;angolo della foto dello stesso colore. Per maggiore precisione, aggiungi punti di collegamento: metti l&apos;estremità IMMAGINE su un elemento nella foto del drone e l&apos;estremità MAPPA sullo stesso elemento sulla mappa.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="137"/>
        <source>Rotation:</source>
        <translation>Rotazione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="138"/>
        <source>Map opacity:</source>
        <translation>Opacità mappa:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="139"/>
        <source>FOV overlay opacity:</source>
        <translation>Opacità sovrapposizione FOV:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="140"/>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="192"/>
        <source>Show Street Map</source>
        <translation>Mostra mappa stradale</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="141"/>
        <source>Add Tie Point</source>
        <translation>Aggiungi punto di collegamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="142"/>
        <source>Reset</source>
        <translation>Reimposta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="195"/>
        <source>Show Satellite</source>
        <translation>Mostra satellite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="218"/>
        <source>Corners look mirrored</source>
        <translation>Gli angoli sembrano speculari</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="220"/>
        <source>The four corners appear mirrored - the drone image would map to the ground flipped.

Each corner handle is colour-matched to a corner of the drone photo (the small coloured squares). Make sure every handle sits where its matching photo corner belongs.</source>
        <translation>I quattro angoli sembrano speculari: l&apos;immagine del drone verrebbe proiettata sul terreno capovolta.

Ogni maniglia d&apos;angolo è abbinata per colore a un angolo della foto del drone (i piccoli quadrati colorati). Assicurati che ogni maniglia si trovi nel punto in cui deve stare l&apos;angolo corrispondente della foto.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="230"/>
        <source>Go Back and Fix</source>
        <translation>Torna indietro e correggi</translation>
    </message>
</context>
<context>
    <name>AlignImageView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="425"/>
        <source>IMAGE</source>
        <translation>IMMAGINE</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="427"/>
        <source>MAP</source>
        <translation>MAPPA</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="672"/>
        <source>Remove Tie Point</source>
        <translation>Rimuovi punto di collegamento</translation>
    </message>
</context>
<context>
    <name>AltitudeController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>meters</source>
        <translation>metri</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>feet</source>
        <translation>piedi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="109"/>
        <source>Negative Altitude Detected</source>
        <translation>Rilevata altitudine negativa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="111"/>
        <source>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</source>
        <translation>ATTENZIONE! L&apos;altitudine relativa è negativa. Inserisci un&apos;altitudine AGL da utilizzare per i calcoli GSD (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="130"/>
        <source>Override Altitude</source>
        <translation>Forza Altitudine</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="132"/>
        <source>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</source>
        <translation>Inserisci un&apos;altitudine AGL personalizzata da utilizzare per i calcoli GSD per tutte le immagini (in {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="180"/>
        <source>Custom AGL set to {value:.1f} {unit}</source>
        <translation>AGL personalizzata impostata su {value:.1f} {unit}</translation>
    </message>
</context>
<context>
    <name>AnalyzeService</name>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="161"/>
        <source>Processing {count} files</source>
        <translation>Elaborazione di {count} file</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="205"/>
        <source>Skipping {file} :: File is not an image</source>
        <translation>Saltato {file} :: Il file non è un&apos;immagine</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="210"/>
        <source>All {count} images queued, processing started...</source>
        <translation>Tutte le {count} immagini in coda, elaborazione avviata...</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="268"/>
        <source>{images} images with {aois} areas of interest identified</source>
        <translation>{images} immagini con {aois} aree di interesse identificate</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="274"/>
        <source>Total Processing Time: {seconds} seconds</source>
        <translation>Tempo totale di elaborazione: {seconds} secondi</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="277"/>
        <source>Total Images Processed: {count}</source>
        <translation>Totale immagini elaborate: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="495"/>
        <source>Unable to process {file} :: {error} ({percent}%)</source>
        <translation>Impossibile elaborare {file} :: {error} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="518"/>
        <source>{count} areas of interest identified in {file} ({percent}%)</source>
        <translation>{count} aree di interesse identificate in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="535"/>
        <source>No areas of interest identified in {file} ({percent}%)</source>
        <translation>Nessuna area di interesse identificata in {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="617"/>
        <source>--- Cancelling Image Processing ---</source>
        <translation>--- Annullamento elaborazione immagini ---</translation>
    </message>
</context>
<context>
    <name>BearingRecoveryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="124"/>
        <source>Missing Bearings Detected</source>
        <translation>Rilevati Orientamenti Mancanti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="132"/>
        <source>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</source>
        <translation>Alcune immagini mancano di informazioni sull&apos;orientamento/prua. Possiamo stimare gli orientamenti da un file di traccia di volo (KML/GPX/CSV) o calcolarli automaticamente dalle coordinate GPS dell&apos;immagine.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="150"/>
        <source>📁 Load Track File (KML/GPX/CSV)</source>
        <translation>📁 Carica File Traccia (KML/GPX/CSV)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="156"/>
        <source>🧭 Auto-Calculate from Image GPS</source>
        <translation>🧭 Calcolo Automatico da GPS Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="174"/>
        <source>Preparing...</source>
        <translation>Preparazione...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="190"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="195"/>
        <source>Skip</source>
        <translation>Salta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="259"/>
        <source>Select Track File</source>
        <translation>Seleziona File Traccia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="261"/>
        <source>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</source>
        <translation>File Traccia (*.kml *.gpx *.csv);;File KML (*.kml);;File GPX (*.gpx);;File CSV (*.csv);;Tutti i File (*.*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="345"/>
        <source>Bearings set for {count} images ({source})</source>
        <translation>Orientamenti impostati per {count} immagini ({source})</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="350"/>
        <source>, {count} flagged near turns</source>
        <translation>, {count} segnalati vicino alle virate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="352"/>
        <source>, {count} hover estimates</source>
        <translation>, {count} stime di stazionamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="354"/>
        <source>, {count} time gaps</source>
        <translation>, {count} intervalli di tempo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="361"/>
        <source>Bearing Calculation Complete</source>
        <translation>Calcolo Orientamento Completato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="362"/>
        <source>{summary}.</source>
        <translation>{summary}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="389"/>
        <source>Bearing Calculation Failed</source>
        <translation>Calcolo Orientamento Fallito</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="391"/>
        <source>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</source>
        <translation>Si è verificato un errore durante il calcolo dell&apos;orientamento:

{error}

Controlla i file di input e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="411"/>
        <source>Cancelled</source>
        <translation>Annullato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="422"/>
        <source>Cancelling...</source>
        <translation>Annullamento in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="435"/>
        <source>Bearing Recovery Not Needed</source>
        <translation>Recupero Orientamento Non Necessario</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="437"/>
        <source>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</source>
        <translation>Il recupero dell&apos;orientamento richiede più immagini per calcolare la direzione di viaggio.

Con una sola immagine, il recupero dell&apos;orientamento non può essere eseguito.</translation>
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
&lt;h3&gt;Cos&apos;è il Recupero dell&apos;Orientamento?&lt;/h3&gt;

&lt;p&gt;L&apos;&lt;b&gt;Orientamento&lt;/b&gt; (chiamato anche prua, imbardata o rotta) è la direzione in cui il drone/telecamera
era puntato quando è stata acquisita un&apos;immagine, misurata in gradi in senso orario dal Nord (0-360°).&lt;/p&gt;

&lt;h4&gt;Perché è importante?&lt;/h4&gt;
&lt;p&gt;Gli orientamenti sono essenziali per:&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;Georeferenziazione e mappatura accurate&lt;/li&gt;
&lt;li&gt;Corretto allineamento e cucitura delle immagini&lt;/li&gt;
&lt;li&gt;Comprensione del campo visivo della telecamera&lt;/li&gt;
&lt;li&gt;Analisi degli oggetti rilevati nel contesto geografico&lt;/li&gt;
&lt;/ul&gt;

&lt;h4&gt;Metodi di Recupero:&lt;/h4&gt;

&lt;p&gt;&lt;b&gt;Carica File Traccia (KML/GPX/CSV)&lt;/b&gt;&lt;br/&gt;
Utilizza un log di traccia GPS esterno dal drone o dal controller di volo. La traccia contiene
posizioni con timestamp che consentono un&apos;interpolazione precisa dell&apos;orientamento. Metodo più accurato.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Calcolo Automatico da GPS Immagine&lt;/b&gt;&lt;br/&gt;
Stima gli orientamenti utilizzando solo le coordinate GPS incorporate nelle immagini. Analizza lo
schema di volo per determinare la direzione di viaggio. Funziona bene per schemi di volo sistematici
come i rilievi a &quot;tagliaerba&quot;.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Salta&lt;/b&gt;&lt;br/&gt;
Procedi senza il recupero dell&apos;orientamento. Alcune funzioni potrebbero non funzionare correttamente.&lt;/p&gt;
        </translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="483"/>
        <source>About Bearing Recovery</source>
        <translation>Informazioni sul Recupero dell&apos;Orientamento</translation>
    </message>
</context>
<context>
    <name>CacheLocationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="35"/>
        <source>Cache Not Found</source>
        <translation>Cache non trovata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="47"/>
        <source>Cached Data Not Found</source>
        <translation>Dati memorizzati nella cache non trovati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="56"/>
        <source>The following cached items were not found:
</source>
        <translation>I seguenti elementi memorizzati nella cache non sono stati trovati:
</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="66"/>
        <source>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</source>
        <translation>Senza i dati memorizzati nella cache, le miniature e i colori verranno generati su richiesta, il che potrebbe causare ritardi durante la visualizzazione dei risultati.

Se hai precedentemente elaborato questo set di dati e hai una cartella ADIAT_Results con i dati memorizzati nella cache, puoi individuarla ora per migliorare le prestazioni.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="80"/>
        <source>Locate Cache Folder...</source>
        <translation>Individua Cartella Cache...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="85"/>
        <source>Skip (Generate On-Demand)</source>
        <translation>Salta (Genera su Richiesta)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="122"/>
        <source>Select ADIAT_Results Folder</source>
        <translation>Seleziona Cartella ADIAT_Results</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="136"/>
        <source>Invalid Cache Folder</source>
        <translation>Cartella Cache Non Valida</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="138"/>
        <source>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</source>
        <translation>La cartella selezionata non contiene la directory della cache delle miniature.

Atteso:
  • .thumbnails/

Seleziona una cartella ADIAT_Results valida.</translation>
    </message>
</context>
<context>
    <name>CalTopoAPIMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="42"/>
        <source>Select CalTopo Map</source>
        <translation>Seleziona Mappa CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="68"/>
        <source>Select a CalTopo map:</source>
        <translation>Seleziona una mappa CalTopo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="77"/>
        <source>Search:</source>
        <translation>Cerca:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="79"/>
        <source>Filter maps by name...</source>
        <translation>Filtra mappe per nome...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="111"/>
        <source>Update Credentials</source>
        <translation>Aggiorna Credenziali</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="117"/>
        <source>Select Map</source>
        <translation>Seleziona Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="121"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="150"/>
        <source>No account data available.</source>
        <translation>Nessun dato dell&apos;account disponibile.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="515"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="540"/>
        <source>Credentials Updated</source>
        <translation>Credenziali Aggiornate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="516"/>
        <source>Credentials have been updated and the map list has been refreshed.</source>
        <translation>Le credenziali sono state aggiornate e l&apos;elenco delle mappe è stato aggiornato.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="521"/>
        <source>Update Failed</source>
        <translation>Aggiornamento Fallito</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="523"/>
        <source>Failed to refresh account data with new credentials.

Please check your credentials and try again.</source>
        <translation>Impossibile aggiornare i dati dell&apos;account con le nuove credenziali.

Controlla le tue credenziali e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="530"/>
        <source>Update Error</source>
        <translation>Errore di Aggiornamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="531"/>
        <source>An error occurred while updating credentials:

{error}</source>
        <translation>Si è verificato un errore durante l&apos;aggiornamento delle credenziali:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="542"/>
        <source>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</source>
        <translation>Le credenziali sono state aggiornate. Chiudi e riapri questa finestra per aggiornare l&apos;elenco delle mappe.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="559"/>
        <source>No Map Selected</source>
        <translation>Nessuna Mappa Selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="560"/>
        <source>Please select a map from the list.</source>
        <translation>Seleziona una mappa dall&apos;elenco.</translation>
    </message>
</context>
<context>
    <name>CalTopoAuthDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="96"/>
        <source>CalTopo Login &amp; Map Selection</source>
        <translation>Accesso CalTopo &amp; Selezione Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="173"/>
        <source>Current map: Not selected</source>
        <translation>Mappa corrente: Non selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="177"/>
        <source>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</source>
        <translation>(Accedi → Naviga verso la tua mappa → Clicca &apos;Sono connesso&apos;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="191"/>
        <source>I&apos;m Logged In - Export Data</source>
        <translation>Sono connesso - Esporta Dati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="193"/>
        <source>Click this after logging in and navigating to your map</source>
        <translation>Clicca qui dopo aver effettuato l&apos;accesso e aver navigato verso la tua mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="196"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="264"/>
        <source>Initialization Error</source>
        <translation>Errore di Inizializzazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="265"/>
        <source>Failed to initialize CalTopo browser:
{error}</source>
        <translation>Impossibile inizializzare il browser CalTopo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="308"/>
        <source>Failed to Load</source>
        <translation>Caricamento Fallito</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="310"/>
        <source>Failed to load CalTopo. Please check your internet connection and try again.</source>
        <translation>Impossibile caricare CalTopo. Controlla la tua connessione internet e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="341"/>
        <source>Current map: {map_id}</source>
        <translation>Mappa corrente: {map_id}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="358"/>
        <source>No Map Selected</source>
        <translation>Nessuna Mappa Selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="360"/>
        <source>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</source>
        <translation>Naviga verso una mappa CalTopo prima di acquisire la sessione.

L&apos;URL della mappa deve contenere un ID mappa (es., /m/ABC123 o #id=ABC123).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="369"/>
        <source>Browser Not Ready</source>
        <translation>Browser non pronto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="370"/>
        <source>The CalTopo browser is still loading. Please wait a moment and try again.</source>
        <translation>Il browser CalTopo è ancora in fase di caricamento. Attendi un momento e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="376"/>
        <source>Starting export...</source>
        <translation>Inizio esportazione...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="394"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="557"/>
        <source>Authentication Failed</source>
        <translation>Autenticazione Fallita</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="395"/>
        <source>Browser not initialized. Please try again.</source>
        <translation>Browser non inizializzato. Riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="559"/>
        <source>Could not capture session cookies. Please ensure you are logged in to CalTopo.

Try:
1. Make sure you&apos;re logged in
2. Navigate to a map
3. Wait a few seconds for cookies to be set
4. Click &apos;I&apos;m Logged In&apos; again</source>
        <translation>Impossibile acquisire i cookie della sessione. Assicurati di aver effettuato l&apos;accesso a CalTopo.

Prova:
1. Assicurati di aver effettuato l&apos;accesso
2. Naviga verso una mappa
3. Attendi qualche secondo affinché i cookie vengano impostati
4. Clicca di nuovo su &apos;Sono connesso&apos;</translation>
    </message>
</context>
<context>
    <name>CalTopoCredentialDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="33"/>
        <source>CalTopo API Credentials</source>
        <translation>Credenziali API CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="54"/>
        <source>Enter new credential secret...</source>
        <translation>Inserisci la nuova parola segreta delle credenziali...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="76"/>
        <source>CalTopo Team API Credentials</source>
        <translation>Credenziali API Team CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="85"/>
        <source>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</source>
        <translation>Inserisci le tue credenziali API Team CalTopo.
Queste possono essere trovate nella pagina Team Admin sotto Service Accounts.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="97"/>
        <source>How to get your API credentials</source>
        <translation>Come ottenere le credenziali API</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="101"/>
        <source>Opens CalTopo API documentation in your browser</source>
        <translation>Apre la documentazione API CalTopo nel browser</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="107"/>
        <source>Change credentials</source>
        <translation>Cambia credenziali</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="114"/>
        <source>Team ID:</source>
        <translation>Team ID:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="116"/>
        <source>6-digit alphanumeric Team ID</source>
        <translation>Team ID alfanumerico di 6 cifre</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="123"/>
        <source>Credential ID:</source>
        <translation>ID Credenziale:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="125"/>
        <source>Credential ID</source>
        <translation>ID Credenziale</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="132"/>
        <source>Credential Secret:</source>
        <translation>Segreto Credenziale:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="134"/>
        <source>Credential Secret (will be encrypted)</source>
        <translation>Segreto Credenziale (sarà crittografato)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="146"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="309"/>
        <source>Test Credentials</source>
        <translation>Testa Credenziali</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="148"/>
        <source>Test the credentials by calling the CalTopo API</source>
        <translation>Testa le credenziali chiamando l&apos;API CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="150"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="204"/>
        <source>Enter credential secret...</source>
        <translation>Inserisci la parola segreta delle credenziali...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Invalid Input</source>
        <translation>Input Non Valido</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="254"/>
        <source>Please enter a Team ID.</source>
        <translation>Inserisci un ID Team.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="258"/>
        <source>Please enter a Credential ID.</source>
        <translation>Inserisci un ID Credenziale.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="262"/>
        <source>Please enter a Credential Secret.</source>
        <translation>Inserisci un Segreto Credenziale.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="267"/>
        <source>Testing...</source>
        <translation>Test in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="282"/>
        <source>Credentials Valid</source>
        <translation>Credenziali Valide</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="283"/>
        <source>The credentials are valid and successfully authenticated with CalTopo API.</source>
        <translation>Le credenziali sono valide e l&apos;autenticazione con l&apos;API CalTopo è riuscita.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="288"/>
        <source>Credentials Invalid</source>
        <translation>Credenziali Non Valide</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <source>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</source>
        <translation>Impossibile autenticare le credenziali con l&apos;API CalTopo.

Controlla:
• L&apos;ID Team è corretto
• L&apos;ID Credenziale è corretto
• Il Segreto Credenziale è corretto (copialo esattamente come mostrato)
• Il tuo account di servizio ha i permessi richiesti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="301"/>
        <source>Test Error</source>
        <translation>Errore Test</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="302"/>
        <source>An error occurred while testing credentials:

{error}</source>
        <translation>Si è verificato un errore durante il test delle credenziali:

{error}</translation>
    </message>
</context>
<context>
    <name>CalTopoExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="441"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1508"/>
        <source>Offline Mode Enabled</source>
        <translation>Modalità Offline Abilitata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="443"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1510"/>
        <source>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</source>
        <translation>La modalità Solo Offline è attiva nelle Preferenze:

• I tasselli della mappa non verranno recuperati.
• L&apos;integrazione CalTopo è disabilitata.

Disattiva Solo Offline per esportare su CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="454"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1521"/>
        <source>Nothing Selected</source>
        <translation>Nessuna Selezione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="456"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1523"/>
        <source>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</source>
        <translation>Seleziona almeno un tipo di dati (AOI contrassegnate, posizioni drone/immagini o area di copertura) da esportare.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="464"/>
        <source>Preparing Export Data</source>
        <translation>Preparazione Dati Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="467"/>
        <source>Preparing data for export...</source>
        <translation>Preparazione dei dati per l&apos;esportazione...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="468"/>
        <source>Processing images and AOIs...</source>
        <translation>Elaborazione immagini e AOI...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="512"/>
        <source>Preparation Error</source>
        <translation>Errore di Preparazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="514"/>
        <source>An error occurred while preparing export data:

{error}</source>
        <translation>Si è verificato un errore durante la preparazione dei dati di esportazione:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="523"/>
        <source>flagged AOIs</source>
        <translation>AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="525"/>
        <source>image locations</source>
        <translation>posizioni immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="527"/>
        <source>coverage area</source>
        <translation>area di copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="531"/>
        <source>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</source>
        <translation>Non sono disponibili AOI contrassegnate, posizioni di immagini georeferenziate o aree di copertura.
Contrassegna alcune AOI con il tasto &apos;F&apos; o assicurati che le tue immagini abbiano metadati GPS.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="537"/>
        <source>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</source>
        <translation>Trovate {count} AOI contrassegnate, ma non è stato possibile estrarre le coordinate GPS.

Questo di solito significa:
• Le immagini non hanno dati GPS nei loro metadati EXIF
• I file immagine sono stati spostati o rinominati

Assicurati che le tue immagini abbiano le coordinate GPS incorporate.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="545"/>
        <source>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</source>
        <translation>Non sono state trovate posizioni di droni/immagini georeferenziate.
Assicurati che le tue immagini contengano metadati GPS e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="550"/>
        <source>No coverage area polygons could be calculated.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The images are not nadir (gimbal pitch must be between -85° and -95°)
• GSD (ground sample distance) could not be calculated

Please ensure your images have GPS coordinates and are nadir shots.</source>
        <translation>Non è stato possibile calcolare alcun poligono dell&apos;area di copertura.

Questo di solito significa:
• Le immagini non hanno dati GPS nei loro metadati EXIF
• Le immagini non sono nadirali (l&apos;inclinazione del gimbal deve essere compresa tra -85° e -95°)
• Non è stato possibile calcolare la GSD (ground sample distance)

Assicurati che le tue immagini abbiano le coordinate GPS e siano scatti nadirali.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="559"/>
        <source>No {types} are available to export.</source>
        <translation>Nessun {types} disponibile per l&apos;esportazione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="564"/>
        <source>Nothing to Export</source>
        <translation>Nulla da Esportare</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="585"/>
        <source>No Map Selected</source>
        <translation>Nessuna Mappa Selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="587"/>
        <source>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</source>
        <translation>Naviga verso una mappa CalTopo prima di cliccare su &apos;Sono connesso&apos;.

L&apos;URL della mappa dovrebbe essere simile a:
https://caltopo.com/map.html#...&amp;id=ABC123</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="649"/>
        <source>{count} marker(s)</source>
        <translation>{count} marcatore/i</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="653"/>
        <source>{count} polygon(s)</source>
        <translation>{count} poligono/i</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="656"/>
        <source> and </source>
        <translation> e </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="661"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1717"/>
        <source>Export Successful</source>
        <translation>Esportazione Riuscita</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="663"/>
        <source>Successfully exported all {items} to CalTopo map {map_id}.

The items should now be visible on your map.</source>
        <translation>Esportati con successo tutti gli {items} sulla mappa CalTopo {map_id}.

Gli elementi dovrebbero ora essere visibili sulla tua mappa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="670"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1726"/>
        <source>Partial Success</source>
        <translation>Successo Parziale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="672"/>
        <source>Exported {success} of {total} item(s) ({items}) to CalTopo map {map_id}.

{failed} item(s) failed. Check console for details.</source>
        <translation>Esportati {success} di {total} elementi ({items}) sulla mappa CalTopo {map_id}.

{failed} elementi falliti. Controlla la console per i dettagli.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="686"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1739"/>
        <source>Export Failed</source>
        <translation>Esportazione Fallita</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="688"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1741"/>
        <source>Failed to export items to CalTopo.

Please check the console output for error details.</source>
        <translation>Impossibile esportare gli elementi su CalTopo.

Controlla l&apos;output della console per i dettagli dell&apos;errore.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="698"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1647"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1752"/>
        <source>Export Error</source>
        <translation>Errore di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="700"/>
        <source>An error occurred during CalTopo export:

{error}</source>
        <translation>Si è verificato un errore durante l&apos;esportazione su CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1002"/>
        <source>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</source>
        <translation>Area di copertura: {sqkm:.3f} km² ({acres:.2f} acri)
Area in metri quadrati: {sqm:.0f} m²
Numero di angoli: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1046"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1330"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1678"/>
        <source>Exporting to CalTopo</source>
        <translation>Esportazione su CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1049"/>
        <source>Exporting markers to CalTopo...</source>
        <translation>Esportazione marcatori su CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1051"/>
        <source>Preparing to export {count} marker(s)...</source>
        <translation>Preparazione all&apos;esportazione di {count} marcatore/i...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1296"/>
        <source>Export complete: {success} of {total} marker(s) exported</source>
        <translation>Esportazione completata: {success} di {total} marcatore/i esportati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1333"/>
        <source>Exporting polygons to CalTopo...</source>
        <translation>Esportazione poligoni su CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1335"/>
        <source>Preparing to export {count} polygon(s)...</source>
        <translation>Preparazione all&apos;esportazione di {count} poligono/i...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1462"/>
        <source>Export complete: {success} of {total} polygon(s) exported</source>
        <translation>Esportazione completata: {success} di {total} poligono/i esportati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1480"/>
        <source>Logged Out</source>
        <translation>Disconnesso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1481"/>
        <source>Successfully logged out from CalTopo.</source>
        <translation>Disconnessione da CalTopo riuscita.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1546"/>
        <source>Loading CalTopo Maps</source>
        <translation>Caricamento Mappe CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1549"/>
        <source>Connecting to CalTopo...</source>
        <translation>Connessione a CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1550"/>
        <source>Fetching account data and maps...</source>
        <translation>Recupero dati account e mappe...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1588"/>
        <source>Connection Error</source>
        <translation>Errore di Connessione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1590"/>
        <source>An error occurred while connecting to CalTopo API:

{error}</source>
        <translation>Si è verificato un errore durante la connessione all&apos;API CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1598"/>
        <source>Authentication Failed</source>
        <translation>Autenticazione Fallita</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1600"/>
        <source>Failed to authenticate with CalTopo API.

Please check your credentials and try again.</source>
        <translation>Impossibile autenticare con l&apos;API CalTopo.

Controlla le tue credenziali e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1649"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1754"/>
        <source>An error occurred during CalTopo API export:

{error}</source>
        <translation>Si è verificato un errore durante l&apos;esportazione tramite API CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1681"/>
        <source>Exporting to CalTopo...</source>
        <translation>Esportazione su CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1682"/>
        <source>Preparing data and exporting...</source>
        <translation>Preparazione dati ed esportazione...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1719"/>
        <source>Successfully exported all {total} item(s) to CalTopo map.

The items should now be visible on your map.</source>
        <translation>Esportati con successo tutti i {total} elementi sulla mappa CalTopo.

Gli elementi dovrebbero ora essere visibili sulla tua mappa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1728"/>
        <source>Exported {success} of {total} item(s) to CalTopo map.

{failed} item(s) failed. Check console for details.</source>
        <translation>Esportati {success} di {total} elementi sulla mappa CalTopo.

{failed} elementi falliti. Controlla la console per i dettagli.</translation>
    </message>
</context>
<context>
    <name>CalTopoMethodDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="34"/>
        <source>CalTopo Export Method</source>
        <translation>Metodo di Esportazione CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="52"/>
        <source>Select CalTopo Export Method</source>
        <translation>Seleziona Metodo di Esportazione CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="61"/>
        <source>Choose how you want to authenticate with CalTopo:</source>
        <translation>Scegli come vuoi autenticarti con CalTopo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="68"/>
        <source>Export Method</source>
        <translation>Metodo di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="72"/>
        <source>API (Recommended for CalTopo Team Account)</source>
        <translation>API (Consigliato per Account Team CalTopo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="75"/>
        <source>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</source>
        <translation>Usa l&apos;API Team CalTopo con le credenziali dell&apos;account di servizio.
Ideale per gli account Team con account di servizio configurati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="79"/>
        <source>Browser Login</source>
        <translation>Accesso tramite Browser</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="81"/>
        <source>Use browser-based authentication.
Log in through an embedded browser window.</source>
        <translation>Usa l&apos;autenticazione basata su browser.
Accedi tramite una finestra del browser integrata.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="96"/>
        <source>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</source>
        <translation>Il metodo API richiede l&apos;ID Team e il Segreto Credenziale dalla tua
pagina Admin Team CalTopo. Il metodo Browser utilizza il tuo normale accesso.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="109"/>
        <source>Continue</source>
        <translation>Continua</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="113"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>CleanupTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="32"/>
        <source>Temporal Voting</source>
        <translation>Voto Temporale</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="35"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Abilita Voto Temporale (riduce lo sfarfallio)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="38"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Smussa i rilevamenti tra i frame usando la consistenza temporale.
I rilevamenti devono comparire in N degli M frame consecutivi per essere confermati.
Riduce notevolmente i falsi positivi intermittenti.
Consigliato: ON in tutti i casi d&apos;uso (predefinito).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="48"/>
        <source>Window Frames (M):</source>
        <translation>Frame Finestra (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="53"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Dimensione della finestra di voto temporale (2-30 frame).
I rilevamenti devono comparire in N degli M frame consecutivi.
Valori più alti = memoria più lunga, più stabile, risposta più lenta ai nuovi oggetti.
Valori più bassi = memoria più breve, risposta più rapida, meno stabile.
Consigliato: 5 per 30 fps (finestra ~167 ms), 7 per 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="61"/>
        <source>Threshold (N of M):</source>
        <translation>Soglia (N su M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="66"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be &lt;= Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Numero di frame, all&apos;interno della finestra, in cui il rilevamento deve comparire (N su M).
Valori più alti = più rigoroso, filtra i falsi positivi transitori.
Valori più bassi = più permissivo, risposta più rapida ai nuovi oggetti.
Deve essere ≤ Frame Finestra.
Consigliato: 3 su 5 (rilevamento nel 60% dei frame).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="78"/>
        <source>Detection Cleanup</source>
        <translation>Pulizia Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="82"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Abilita Filtro Rapporto d&apos;Aspetto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="85"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filtra i rilevamenti molto sottili o allungati in base a larghezza/altezza.
Utile per rimuovere fili, ombre allungate o altre forme non corrispondenti a oggetti.
La maggior parte degli utenti può lasciarlo OFF, a meno di rilevare molti falsi positivi sottili e allungati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="94"/>
        <source>Min Ratio:</source>
        <translation>Rapporto Min:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="100"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 = reject if height is more than 5x width.</source>
        <translation>Rapporto larghezza/altezza minimo da mantenere (0,1-10,0).
Valori più bassi = consente rilevamenti più alti e sottili.
Valori più alti = richiede rilevamenti più simili a un quadrato.
Esempio: 0,2 = rifiuta se l&apos;altezza è più di 5x la larghezza.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="107"/>
        <source>Max Ratio:</source>
        <translation>Rapporto Max:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="113"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Rapporto larghezza/altezza massimo da mantenere (0,1-20,0).
Valori più bassi = rifiuta i rilevamenti molto larghi e sottili.
Valori più alti = consente oggetti più larghi come veicoli o attrezzature lunghe.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="122"/>
        <source>Detection Clustering</source>
        <translation>Clustering Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="125"/>
        <source>Enable Detection Clustering</source>
        <translation>Abilita Clustering Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="128"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Unisce facoltativamente i rilevamenti vicini in un unico rilevamento più grande.
Utile quando un oggetto compare come molti piccoli rilevamenti adiacenti.
La maggior parte degli utenti può lasciarlo OFF, a meno che gli oggetti non appaiano frammentati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="137"/>
        <source>Clustering Distance (px):</source>
        <translation>Distanza Clustering (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="142"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Distanza massima tra i centri di rilevamento per unirli (0-500 pixel).
Valori più bassi = unisce solo rilevamenti molto vicini.
Valori più alti = unisce rilevamenti più distanti (può unire troppo).</translation>
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
Clicca per cambiare colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="71"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="71"/>
        <source>HSV: ({h}, {s}, {v})
Click to change color</source>
        <translation>HSV: ({h}, {s}, {v})
Clicca per cambiare colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="78"/>
        <source>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Clicca per cambiare colore</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="67"/>
        <source>Color Anomaly</source>
        <translation>Anomalia Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="68"/>
        <source>Motion Detection</source>
        <translation>Rilevamento Movimento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="69"/>
        <source>Fusion</source>
        <translation>Fusione</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="77"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Elaborazione</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="78"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="79"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Pulizia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="146"/>
        <source>Enable Motion Detection</source>
        <translation>Abilita Rilevamento Movimento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="149"/>
        <source>Turn ON to highlight moving objects in the scene.
Most users can leave all other settings at their defaults.
Works best for stationary or slow-moving cameras and can be combined
with Color-Based Anomaly Detection for more robust results.</source>
        <translation>Attiva per evidenziare gli oggetti in movimento nella scena.
La maggior parte degli utenti può lasciare tutte le altre impostazioni sui valori predefiniti.
Funziona meglio con telecamere fisse o a movimento lento e può essere combinato
con il Rilevamento Anomalie Basato sul Colore per risultati più affidabili.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="162"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="167"/>
        <source>Type:</source>
        <translation>Tipo:</translation>
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
        <translation>Algoritmo di rilevamento movimento (impostazione avanzata):

• FRAME_DIFF – Veloce e semplice; molto sensibile a qualsiasi movimento.
• MOG2 – Bilanciato e adattivo (consigliato per la maggior parte delle scene).
• KNN – Più robusto al rumore e agli sfondi complessi.

In caso di dubbi, lascia impostato MOG2.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="185"/>
        <source>Detection Parameters</source>
        <translation>Parametri Rilevamento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="191"/>
        <source>Motion Threshold:</source>
        <translation>Soglia Movimento:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="196"/>
        <source>Minimum pixel intensity change to consider as motion (1-255).
Lower values = more sensitive, detects subtle motion, more false positives.
Higher values = less sensitive, only strong motion, fewer false positives.
Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.</source>
        <translation>Variazione minima di intensità dei pixel da considerare come movimento (1-255).
Valori più bassi = più sensibile, rileva movimenti sottili, più falsi positivi.
Valori più alti = meno sensibile, solo movimenti marcati, meno falsi positivi.
Consigliato: 10 per uso generale, 5 per movimenti sottili, 15-20 per scene ad alto contrasto.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="204"/>
        <source>Blur Kernel (odd):</source>
        <translation>Kernel Sfocatura (dispari):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="210"/>
        <source>Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).
Smooths the frame before motion detection to reduce noise.
Larger values = more smoothing, less noise, less detail.
Smaller values = less smoothing, more detail, more noise.
Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.</source>
        <translation>Dimensione del kernel di sfocatura gaussiana (deve essere dispari: 1, 3, 5, 7, ecc.).
Leviga il frame prima del rilevamento movimento per ridurre il rumore.
Valori più alti = più sfocatura, meno rumore, meno dettaglio.
Valori più bassi = meno sfocatura, più dettaglio, più rumore.
Consigliato: 5 per uso generale, 1 per nessuna sfocatura, 7-9 per video rumorosi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="219"/>
        <source>Morphology Kernel:</source>
        <translation>Kernel Morfologia:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="225"/>
        <source>Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).
Removes small noise and fills holes in detections.
Larger values = remove more noise, merge nearby detections.
Smaller values = preserve detail, keep detections separate.
Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.</source>
        <translation>Dimensione del kernel per operazioni morfologiche (numeri dispari: 1, 3, 5, ecc.).
Rimuove il rumore di piccola entità e riempie i fori nei rilevamenti.
Valori più alti = rimuove più rumore, unisce rilevamenti vicini.
Valori più bassi = preserva il dettaglio, mantiene separati i rilevamenti.
Consigliato: 3 per uso generale, 1 per bordi precisi, 5-7 per video rumorosi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="236"/>
        <source>Persistence Filter</source>
        <translation>Filtro Persistenza</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="241"/>
        <source>Window Frames (M):</source>
        <translation>Frame Finestra (M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="246"/>
        <source>Size of temporal window for persistence filtering (2-30 frames).
Motion must appear in N out of M consecutive frames to be confirmed.
Larger values = longer memory, more stable, slower response.
Smaller values = shorter memory, faster response, more flicker.
Recommended: 3 for 30fps video (100ms window), 5 for 60fps.</source>
        <translation>Dimensione della finestra temporale per il filtro di persistenza (2-30 frame).
Il movimento deve comparire in N degli M frame consecutivi per essere confermato.
Valori più alti = memoria più lunga, più stabile, risposta più lenta.
Valori più bassi = memoria più breve, risposta più rapida, più sfarfallio.
Consigliato: 3 per video a 30 fps (finestra di 100 ms), 5 per 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="254"/>
        <source>Threshold (N of M):</source>
        <translation>Soglia (N su M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="259"/>
        <source>Number of frames within window where motion must appear (N of M).
Higher values = more stringent, filters flickering false positives.
Lower values = more lenient, detects brief/intermittent motion.
Must be ≤ Window Frames.
Recommended: 2 (motion in 2 of last 3 frames).</source>
        <translation>Numero di frame, all&apos;interno della finestra, in cui il movimento deve comparire (N su M).
Valori più alti = più rigoroso, filtra i falsi positivi intermittenti.
Valori più bassi = più permissivo, rileva movimenti brevi o intermittenti.
Deve essere ≤ Frame Finestra.
Consigliato: 2 (movimento in 2 degli ultimi 3 frame).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="270"/>
        <source>Background Subtraction (MOG2/KNN)</source>
        <translation>Sottrazione Sfondo (MOG2/KNN)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="275"/>
        <source>History Frames:</source>
        <translation>Frame Cronologia:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="280"/>
        <source>Number of frames to learn background model (10-500).
Only applies to MOG2 and KNN algorithms.
Longer history = adapts slower to lighting changes, more stable.
Shorter history = adapts faster, less stable.
Recommended: 50 (~1.7 sec at 30fps) for general use.</source>
        <translation>Numero di frame utilizzati per apprendere il modello di sfondo (10-500).
Si applica solo agli algoritmi MOG2 e KNN.
Cronologia più lunga = si adatta più lentamente ai cambi di illuminazione, più stabile.
Cronologia più breve = si adatta più rapidamente, meno stabile.
Consigliato: 50 (~1,7 sec a 30 fps) per uso generale.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="288"/>
        <source>Variance Threshold:</source>
        <translation>Soglia Varianza:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="293"/>
        <source>Variance threshold for background/foreground classification (1.0-100.0).
Only applies to MOG2 and KNN algorithms.
Lower values = more sensitive, detects subtle changes, more false positives.
Higher values = less sensitive, only strong foreground objects.
Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.</source>
        <translation>Soglia di varianza per la classificazione sfondo/primo piano (1,0-100,0).
Si applica solo agli algoritmi MOG2 e KNN.
Valori più bassi = più sensibile, rileva variazioni sottili, più falsi positivi.
Valori più alti = meno sensibile, solo oggetti in primo piano marcati.
Consigliato: 10,0 per interni, 15-20 per esterni con illuminazione variabile.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="301"/>
        <source>Detect Shadows (slower)</source>
        <translation>Rileva Ombre (più lento)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="303"/>
        <source>Enables shadow detection in MOG2 background subtractor.
Helps distinguish shadows from actual objects (reduces false positives).
Adds ~10-20% processing overhead.
Recommended: ON for outdoor scenes with strong shadows, OFF for speed.</source>
        <translation>Abilita il rilevamento delle ombre nel sottrattore di sfondo MOG2.
Aiuta a distinguere le ombre dagli oggetti reali (riduce i falsi positivi).
Aumenta il carico di elaborazione del ~10-20%.
Consigliato: ON per scene esterne con ombre marcate, OFF per la velocità.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="313"/>
        <source>Object Size Filter</source>
        <translation>Filtro Dimensione Oggetti</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="318"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="454"/>
        <source>Min Object Area (px):</source>
        <translation>Area Min Oggetto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="323"/>
        <source>Minimum detection area in pixels (1-100000).
Filters out very small detections such as noise, insects, or raindrops.
Lower values = detect smaller objects (more noise).
Higher values = only larger objects (less noise).
Recommended: 5-10 for person-sized motion, 50-100 for vehicles.</source>
        <translation>Area minima di rilevamento in pixel (1-100000).
Esclude i rilevamenti molto piccoli come rumore, insetti o gocce di pioggia.
Valori più bassi = rileva oggetti più piccoli (più rumore).
Valori più alti = solo oggetti più grandi (meno rumore).
Consigliato: 5-10 per soggetti delle dimensioni di una persona, 50-100 per i veicoli.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="331"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="467"/>
        <source>Max Object Area (px):</source>
        <translation>Area Max Oggetto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="336"/>
        <source>Maximum detection area in pixels (10-1000000).
Filters out very large regions such as full-frame lighting changes or giant shadows.
Lower values = only small/medium objects.
Higher values = allow large objects.
Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.</source>
        <translation>Area massima di rilevamento in pixel (10-1000000).
Esclude regioni molto grandi come variazioni di luce a pieno campo o ombre estese.
Valori più bassi = solo oggetti piccoli/medi.
Valori più alti = consente oggetti grandi.
Consigliato: 1000 per le persone, 10000 per i veicoli, valori più alti per oggetti molto grandi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="347"/>
        <source>Camera Movement Detection</source>
        <translation>Rilevamento Movimento Telecamera</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="350"/>
        <source>Pause on Camera Movement</source>
        <translation>Metti in Pausa Durante il Movimento della Telecamera</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="353"/>
        <source>Automatically pauses motion detection when camera is moving/panning.
Prevents false positives caused by camera movement (entire scene appears to move).
Detects camera movement by measuring percentage of frame with motion.
Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.</source>
        <translation>Mette automaticamente in pausa il rilevamento movimento quando la telecamera si sposta o effettua una panoramica.
Evita i falsi positivi causati dal movimento della telecamera (l&apos;intera scena appare in movimento).
Il movimento della telecamera è rilevato misurando la percentuale di frame in movimento.
Consigliato: ON per riprese a mano libera o da drone, OFF per telecamere su treppiede fisso.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="361"/>
        <source>Threshold:</source>
        <translation>Soglia:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="366"/>
        <source>Percentage of frame with motion to consider as camera movement (1-100%).
If more than this % of pixels show motion, pause detection.
Lower values = detect camera movement sooner (more pauses).
Higher values = tolerate more motion before pausing (fewer pauses).
Recommended: 15% for drone/handheld, 30% for shaky tripod.</source>
        <translation>Percentuale di frame in movimento da considerare come movimento della telecamera (1-100%).
Se più di questa percentuale di pixel risulta in movimento, il rilevamento viene messo in pausa.
Valori più bassi = il movimento della telecamera viene rilevato prima (più pause).
Valori più alti = tollera più movimento prima di mettere in pausa (meno pause).
Consigliato: 15% per drone/mano libera, 30% per treppiedi instabili.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="380"/>
        <source>Show Advanced Motion Settings</source>
        <translation>Mostra Impostazioni Avanzate Movimento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="383"/>
        <source>Advanced users can expand this to adjust the motion algorithm
and detailed thresholds (sensitivity, filters, background model).
If you are unsure, leave this unchecked and use the defaults.</source>
        <translation>Gli utenti esperti possono espandere questa sezione per regolare l&apos;algoritmo di movimento
e le soglie di dettaglio (sensibilità, filtri, modello di sfondo).
In caso di dubbi, lascia disattivata questa opzione e usa le impostazioni predefinite.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="402"/>
        <source>Enable Color-Based Anomaly Detection</source>
        <translation>Abilita Rilevamento Anomalie Basato sul Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="405"/>
        <source>Detects pixels whose colors are statistically rare in the frame.
Conceptually similar to MRMap&apos;s rarity-based detection for images.
Works well for: bright colored clothing, vehicles, equipment in natural scenes.
Can be combined with Motion Detection for more robust detection.</source>
        <translation>Rileva i pixel i cui colori sono statisticamente rari nel frame.
Concettualmente simile al rilevamento basato sulla rarità di MRMap per le immagini.
Funziona bene con: abbigliamento dai colori vivaci, veicoli, attrezzature in scene naturali.
Può essere combinato con il Rilevamento Movimento per un rilevamento più robusto.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="413"/>
        <source>Color Rarity Settings</source>
        <translation>Impostazioni Rarità Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="418"/>
        <source>Color Resolution (bins):</source>
        <translation>Risoluzione Colore (bin):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="424"/>
        <source>Controls how finely colors are grouped into histogram bins (3-8 bits).
Analogous to MRMap&apos;s color binning.
Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.
Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.
Recommended: 4-5 for a balanced number of detections; use lower for very clean results,
and higher only when you need to pull out very subtle color differences.</source>
        <translation>Regola la granularità con cui i colori sono raggruppati nei bin dell&apos;istogramma (3-8 bit).
Analogo al binning dei colori di MRMap.
Valori più bassi (3-4) = meno bin → più veloce, più raggruppamento, rilevamenti meno numerosi ma più marcati.
Valori più alti (6-8) = più bin → più lento, meno raggruppamento, rilevamenti più numerosi ma più deboli/piccoli.
Consigliato: 4-5 per un numero bilanciato di rilevamenti; usa valori più bassi per risultati molto puliti,
e più alti solo quando devi cogliere differenze di colore molto sottili.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="432"/>
        <source>4 bits</source>
        <translation>4 bit</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="436"/>
        <source>Rarity Threshold (% of colors):</source>
        <translation>Soglia Rarità (% dei colori):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="442"/>
        <source>Sensitivity threshold for how rare a color must be to be flagged (0-100%).
Computed from the distribution of color-bin counts in the frame, similar in role
to MRMap&apos;s detection threshold.
Lower values (10-20%) = stricter: only very rare colors (fewer detections).
Medium values (25-40%) = balanced (recommended for general use).
Higher values (40-60%) = more sensitive: includes more common colors (more detections).</source>
        <translation>Soglia di sensibilità per stabilire quanto deve essere raro un colore per essere segnalato (0-100%).
Viene calcolata dalla distribuzione dei conteggi dei bin di colore nel frame, con un ruolo simile
alla soglia di rilevamento di MRMap.
Valori più bassi (10-20%) = più rigoroso: solo colori molto rari (meno rilevamenti).
Valori medi (25-40%) = bilanciato (consigliato per uso generale).
Valori più alti (40-60%) = più sensibile: include colori più comuni (più rilevamenti).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="459"/>
        <source>Minimum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s minimum AOI area.
Lower values = detect smaller colored objects (more noise).
Higher values = only larger colored regions (less noise).
Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.</source>
        <translation>Area minima in pixel affinché un&apos;anomalia di colore venga considerata un oggetto di interesse.
Corrisponde concettualmente all&apos;area minima dell&apos;AOI in MRMap.
Valori più bassi = rileva oggetti colorati più piccoli (più rumore).
Valori più alti = solo regioni colorate più grandi (meno rumore).
Consigliato: 15 per soggetti delle dimensioni di una persona, 50+ per veicoli o oggetti grandi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="472"/>
        <source>Maximum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s maximum AOI area.
Lower values = only detect smaller colored objects.
Higher values = allow larger colored regions.
Recommended: 50000 for general use, 10000 for small-object-only searches.</source>
        <translation>Area massima in pixel affinché un&apos;anomalia di colore venga considerata un oggetto di interesse.
Corrisponde concettualmente all&apos;area massima dell&apos;AOI in MRMap.
Valori più bassi = rileva solo oggetti colorati più piccoli.
Valori più alti = consente regioni colorate più grandi.
Consigliato: 50000 per uso generale, 10000 per ricerche di soli oggetti piccoli.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="480"/>
        <source>Blob Detection Method:</source>
        <translation>Metodo Rilevamento Blob:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="482"/>
        <source>Find Contours</source>
        <translation>Trova Contorni</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="483"/>
        <source>Connected Components</source>
        <translation>Componenti Connesse</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="486"/>
        <source>Method for extracting blob regions from the detection mask:

Find Contours: Traditional OpenCV contour detection (default).
  Better for irregular shapes, provides detailed contour outlines.

Connected Components: Uses cv2.connectedComponentsWithStats.
  Provides direct blob statistics in a single pass.</source>
        <translation>Metodo per estrarre le regioni blob dalla maschera di rilevamento:

Trova Contorni: rilevamento contorni OpenCV tradizionale (predefinito).
  Migliore per forme irregolari, fornisce contorni dettagliati.

Componenti Connesse: usa cv2.connectedComponentsWithStats.
  Fornisce statistiche dei blob in un&apos;unica passata.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="497"/>
        <source>Color Space (Lighting Invariance)</source>
        <translation>Spazio Colore (Invarianza Luminosa)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="502"/>
        <source>Color Space:</source>
        <translation>Spazio colore:</translation>
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
        <translation>Spazio colore per il rilevamento anomalie basato su istogramma:

RGB: usa tutti e 3 i canali colore. Veloce, ma sensibile alla luce.
  Una maglietta rossa in ombra potrebbe non corrispondere a una rossa al sole.

HSV (basato sulla tonalità): usa solo il canale Hue, invariante alla luce.
  Il rosso rimane rosso indipendentemente dalla luminosità. Adatto agli oggetti colorati.
  Esclude grigi/bianchi dove la tonalità è indefinita.

LAB (cromaticità a,b): usa i canali a,b, invariante alla luce, percettivamente uniforme.
  Nessuna discontinuità sul rosso (a differenza di HSV). Ideale per ricerca e soccorso.
  Esclude i grigi neutri dove a,b sono vicini a zero.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="522"/>
        <source>HSV Min Saturation:</source>
        <translation>Saturazione Min HSV:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="529"/>
        <source>Minimum saturation for HSV mode (0-255).
Pixels below this saturation are ignored (grays, whites, blacks).
These have undefined/noisy hue values.
Lower = include more desaturated colors (may add noise).
Higher = only vivid colors (may miss faded/shadowed objects).
Recommended: 30-50 for general use.</source>
        <translation>Saturazione minima per la modalità HSV (0-255).
I pixel sotto questa saturazione vengono ignorati (grigi, bianchi, neri).
Hanno valori di tonalità indefiniti o rumorosi.
Più basso = include più colori desaturati (può aggiungere rumore).
Più alto = solo colori vividi (può perdere oggetti sbiaditi o in ombra).
Consigliato: 30-50 per uso generale.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="542"/>
        <source>LAB Min Chroma:</source>
        <translation>Croma Min LAB:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="549"/>
        <source>Minimum chroma (color intensity) for LAB mode (0-128).
Chroma = distance from neutral gray in a,b plane.
Pixels below this are ignored (near-neutral grays).
Lower = include more muted colors.
Higher = only vivid, saturated colors.
Recommended: 10-20 for general use.</source>
        <translation>Croma minimo (intensità colore) per la modalità LAB (0-128).
Croma = distanza dal grigio neutro nel piano a,b.
I pixel sotto questo valore vengono ignorati (grigi quasi neutri).
Più basso = include più colori smorzati.
Più alto = solo colori vividi e saturi.
Consigliato: 10-20 per uso generale.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="567"/>
        <source>Color Match Expansion</source>
        <translation>Espansione Corrispondenza Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="570"/>
        <source>Allow Similar Colors (Hue Expansion)</source>
        <translation>Consenti Colori Simili (Espansione Tonalità)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="573"/>
        <source>Lets the detector treat similar colors as the same object.
For example, a red jacket that looks slightly orange in some frames will still be grouped together.
Turn this OFF if you only care about one very specific color shade.
Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).</source>
        <translation>Consente al rilevatore di trattare colori simili come lo stesso oggetto.
Ad esempio, una giacca rossa che in alcuni frame appare leggermente arancione verrà comunque raggruppata insieme.
Disattivalo se ti interessa una sola tonalità molto specifica.
Attivalo se vuoi un&apos;intera famiglia di colori (es. tutti i rossi/aranci caldi).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="581"/>
        <source>Color Match Range:</source>
        <translation>Intervallo Corrispondenza Colore:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="586"/>
        <source>How wide to stretch the color match around each detected color.
Smaller values = stay very close to the original color (more specific).
Larger values = include a wider range of similar colors (more forgiving).
Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.</source>
        <translation>Quanto ampliare la corrispondenza di colore attorno a ciascun colore rilevato.
Valori più bassi = restano molto vicini al colore originale (più specifico).
Valori più alti = includono una gamma più ampia di colori simili (più tollerante).
Consigliato: valori bassi per colori precisi, valori più alti quando la luce o il colore della telecamera variano molto.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="592"/>
        <source>±5 (~10°)</source>
        <translation>±5 (~10°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="599"/>
        <source>Color Exclusion</source>
        <translation>Esclusione Colori</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="602"/>
        <source>Enable Color Exclusion</source>
        <translation>Abilita Esclusione Colori</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="605"/>
        <source>Exclude specific background colors from color anomaly detection.
Useful for ignoring dominant scene colors such as grass, sky, or buildings.
Click on the color wheel below to choose colors to ignore.
Selected colors are highlighted with a dark border.</source>
        <translation>Esclude specifici colori di sfondo dal rilevamento anomalie di colore.
Utile per ignorare colori dominanti della scena come erba, cielo o edifici.
Clicca sulla ruota dei colori in basso per scegliere quali colori ignorare.
I colori selezionati sono evidenziati con un bordo scuro.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="613"/>
        <source>Click on color wheel to exclude colors (20° steps, 0-360°):</source>
        <translation>Clicca sulla ruota dei colori per escludere colori (passi di 20°, 0-360°):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="618"/>
        <source>Click on any color segment to toggle exclusion on/off.
Segments represent broad color ranges (e.g., blues, greens, reds).
Use this to teach the system which background colors to ignore.</source>
        <translation>Clicca su qualsiasi segmento di colore per attivare/disattivare l&apos;esclusione.
I segmenti rappresentano gamme cromatiche ampie (es. blu, verdi, rossi).
Usa questa funzione per indicare al sistema quali colori di sfondo ignorare.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="635"/>
        <source>Detection Fusion</source>
        <translation>Fusione Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="638"/>
        <source>Enable Fusion (when both motion and color enabled)</source>
        <translation>Abilita Fusione (quando movimento e colore sono entrambi attivi)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="641"/>
        <source>Combines motion and color detections when both are enabled.
Only active when both Motion and Color detection are ON.
Different modes control how detections are merged.
Recommended: ON for robust multi-modal detection.</source>
        <translation>Combina i rilevamenti di movimento e colore quando entrambi sono attivi.
Attivo solo quando sia il rilevamento Movimento sia quello Colore sono attivi.
Le diverse modalità controllano come vengono unite le rilevazioni.
Consigliato: ON per un rilevamento multi-modale affidabile.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="649"/>
        <source>Fusion Mode:</source>
        <translation>Modalità Fusione:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="651"/>
        <source>UNION</source>
        <translation>UNIONE</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="652"/>
        <source>INTERSECTION</source>
        <translation>INTERSEZIONE</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="653"/>
        <source>COLOR_PRIORITY</source>
        <translation>PRIORITÀ_COLORE</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="654"/>
        <source>MOTION_PRIORITY</source>
        <translation>PRIORITÀ_MOVIMENTO</translation>
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
        <translation>Come combinare i rilevamenti di movimento e colore:

• UNIONE: mostra tutti i rilevamenti di entrambi (massimo numero di rilevamenti).
  Da usare per: copertura massima, non perdere nulla.

• INTERSEZIONE: mostra solo i rilevamenti trovati da entrambi (minimo dei falsi positivi).
  Da usare per: alta affidabilità, riduzione dei falsi positivi.

• PRIORITÀ_COLORE: mostra i rilevamenti di colore + i rilevamenti di movimento che corrispondono al colore.
  Da usare per: dare maggior peso al colore (es. oggetti dai colori vivaci).

• PRIORITÀ_MOVIMENTO: mostra i rilevamenti di movimento + i rilevamenti di colore che corrispondono al movimento.
  Da usare per: dare maggior peso al movimento (es. oggetti mimetizzati in movimento).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="757"/>
        <source>{value} bits</source>
        <translation>{value} bit</translation>
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
        <translation>FPS: {fps} | Elaborazione: {time} ms</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="12"/>
        <source>Color Anomaly Detection</source>
        <translation>Rilevamento Anomalie Colore</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="16"/>
        <source>Enable Color Anomaly Detection</source>
        <translation>Abilita Rilevamento Anomalie Colore</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="27"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Quanto aggressivamente dovrebbe ADIAT cercare le anomalie?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="38"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta troverà più potenziali anomalie ma potrebbe anche aumentare i falsi positivi.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="56"/>
        <source>Motion Detection</source>
        <translation>Rilevamento Movimento</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="65"/>
        <source>Do you want to enable motion detection?</source>
        <translation>Vuoi abilitare il rilevamento del movimento?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="73"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="79"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="48"/>
        <source>Very 
Conservative</source>
        <translation>Molto 
Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="49"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="50"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="51"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="52"/>
        <source>Very 
Aggressive</source>
        <translation>Molto 
Aggressivo</translation>
    </message>
</context>
<context>
    <name>ColorDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="76"/>
        <source>Color Selection</source>
        <translation>Selezione Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="77"/>
        <source>Detection</source>
        <translation>Rilevamento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="78"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Input &amp;&amp; Elaborazione</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="79"/>
        <source>Frame</source>
        <translation>Frame</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="80"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Rendering &amp;&amp; Pulizia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="108"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="111"/>
        <source>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</source>
        <translation>Aggiungi un nuovo intervallo di colori da rilevare.
Scegli tra Selettore Colore HSV, Immagine, Elenco o Colori Recenti.
Puoi aggiungere più intervalli di colori per rilevare diversi colori contemporaneamente.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="131"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="134"/>
        <source>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</source>
        <translation>Visualizza gli intervalli di colore HSV per tutti i colori configurati.
Apre una finestra di visualizzazione per ogni intervallo di colore mostrando
gli intervalli di tonalità, saturazione e valore che verranno rilevati.
Utile per comprendere e perfezionare il rilevamento multicolore.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="157"/>
        <source>No colors configured. Add at least one color to start detection.</source>
        <translation>Nessun colore configurato. Aggiungi almeno un colore per avviare il rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="178"/>
        <source>Min Object Area (px):</source>
        <translation>Area Min Oggetto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="184"/>
        <source>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</source>
        <translation>Area di rilevamento minima in pixel (10-50000).
Filtra i rilevamenti molto piccoli (rumore, piccoli oggetti, frammenti).
Valori più bassi = rileva oggetti più piccoli, più rilevamenti, più rumore.
Valori più alti = solo oggetti grandi, meno rilevamenti, meno rumore.
Consigliato: 100 per uso generale, 50 per piccoli oggetti, 200-500 per grandi oggetti.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="193"/>
        <source>Max Object Area (px):</source>
        <translation>Area Max Oggetto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="199"/>
        <source>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</source>
        <translation>Area di rilevamento massima in pixel (100-500000).
Filtra i rilevamenti molto grandi (ombre, cambiamenti di luce, intera scena).
Valori più bassi = solo oggetti piccoli/medi.
Valori più alti = consente oggetti grandi, può includere grandi regioni indesiderate.
Consigliato: 100000 per uso generale, 50000 per piccoli oggetti, 200000+ per grandi oggetti.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="208"/>
        <source>Confidence Threshold:</source>
        <translation>Soglia di Confidenza:</translation>
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
        <translation>Punteggio di confidenza minimo per accettare un rilevamento (0-100%).
La confidenza è calcolata da:
• Punteggio dimensione: area relativa all&apos;area massima
• Punteggio forma: solidità (quanto è compatta/regolare la forma)
• Finale: media di entrambi i punteggi

Valori più bassi (0-30%) = accetta più rilevamenti, inclusi quelli deboli/frammentati.
Valori più alti (70-100%) = solo rilevamenti di alta qualità, forme ben formate.
Consigliato: 50% per un filtraggio bilanciato, 30% per più rilevamenti, 70% per qualità rigorosa.</translation>
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
        <translation>Colore_{index}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="513"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Intervalli Colore: {count} colori</translation>
    </message>
</context>
<context>
    <name>ColorDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionController.py" line="134"/>
        <source>FPS: {fps} | Processing: {time}ms</source>
        <translation>FPS: {fps} | Elaborazione: {time} ms</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorDetectionWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="52"/>
        <source>No Colors Selected</source>
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="62"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="244"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Intervalli Colore: {count} colori</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="329"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="57"/>
        <source>Hue Histogram Unavailable</source>
        <translation>Istogramma della tonalita non disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="59"/>
        <source>No color image data is available for the current image.</source>
        <translation>Nessun dato dell&apos;immagine a colori e disponibile per l&apos;immagine corrente.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="14"/>
        <source>Hue Histogram</source>
        <translation>Istogramma della tonalita</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="23"/>
        <source>Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.</source>
        <translation>Distribuzione della tonalita di tutti i pixel rispetto ai pixel AOI. Passando sul grafico vengono evidenziati nell&apos;immagine i pixel corrispondenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="32"/>
        <source>AOIs Only</source>
        <translation>Solo AOI</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Reimposta zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="61"/>
        <source>Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Trascina sull&apos;istogramma o usa la rotella del mouse per zoomare. Fai doppio clic oppure usa Reimposta zoom per tornare all&apos;intervallo completo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="74"/>
        <source>Visible Hue Range</source>
        <translation>Intervallo di tonalita visibile</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="64"/>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="174"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="127"/>
        <source>Hover over the histogram to inspect a hue band.</source>
        <translation>Passa sull&apos;istogramma per ispezionare una banda di tonalita.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="61"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="85"/>
        <source>Minimum: --</source>
        <translation>Minimo: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="62"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="92"/>
        <source>Maximum: --</source>
        <translation>Massimo: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="115"/>
        <source>Reset Range</source>
        <translation>Reimposta intervallo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="30"/>
        <source>No hue histogram data available</source>
        <translation>Nessun dato disponibile per l&apos;istogramma della tonalita</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="180"/>
        <source>Hover hue: {value}°</source>
        <translation>Tonalita al passaggio: {value}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="188"/>
        <source>Minimum: {minimum}°</source>
        <translation>Minimo: {minimum}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="193"/>
        <source>Maximum: {maximum}°</source>
        <translation>Massimo: {maximum}°</translation>
    </message>
</context>
<context>
    <name>ColorListDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="30"/>
        <source>Select Color from List</source>
        <translation>Seleziona Colore dall&apos;Elenco</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="42"/>
        <source>Search:</source>
        <translation>Cerca:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="44"/>
        <source>Filter by name or uses…</source>
        <translation>Filtra per nome o utilizzi…</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Name</source>
        <translation>Nome</translation>
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
        <translation>Utilizzi</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="73"/>
        <source>Use Color</source>
        <translation>Usa Colore</translation>
    </message>
</context>
<context>
    <name>ColorPickerDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="35"/>
        <source>Select Color from Image</source>
        <translation>Seleziona Colore dall&apos;Immagine</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="55"/>
        <source>Use Color</source>
        <translation>Usa Colore</translation>
    </message>
</context>
<context>
    <name>ColorPickerImageViewer</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <source>Load Image</source>
        <translation>Carica Immagine</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <source>Color Selector</source>
        <translation>Selettore Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <source>Select Image</source>
        <translation>Seleziona Immagine</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="173"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="230"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="588"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="174"/>
        <source>Could not load image: {path}</source>
        <translation>Impossibile caricare l&apos;immagine: {path}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <source>Error loading image: {error}</source>
        <translation>Errore durante il caricamento dell&apos;immagine: {error}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (passaggio mouse)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <source>Error setting image: {error}</source>
        <translation>Errore durante l&apos;impostazione dell&apos;immagine: {error}</translation>
    </message>
</context>
<context>
    <name>ColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="42"/>
        <source>Add a new color range to detect. Each color can have its own RGB range tolerances.</source>
        <translation>Aggiungi un nuovo intervallo di colori da rilevare. Ogni colore può avere le proprie tolleranze di intervallo RGB.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="45"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
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
        <translation>Apre la finestra Visualizzatore Intervallo per:
- Vedere l&apos;intervallo di colori che verranno cercati nell&apos;analisi dell&apos;immagine.
Usa questo per vedere quali colori verranno rilevati e ottimizzare gli intervalli di colore prima dell&apos;elaborazione.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="88"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
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
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="324"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
    </message>
</context>
<context>
    <name>ColorRangeDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="39"/>
        <source>HSV Color Range Selection</source>
        <translation>Selezione Intervallo Colore HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="122"/>
        <source>Color Range Selection</source>
        <translation>Selezione Intervallo Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="206"/>
        <source>Preview</source>
        <translation>Anteprima</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="210"/>
        <source>Original Image</source>
        <translation>Immagine Originale</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="216"/>
        <source>Original image preview.
Shows the unmodified input image for reference.
Use this to compare with the filtered result below.</source>
        <translation>Anteprima dell&apos;immagine originale.
Mostra l&apos;immagine di input non modificata per riferimento.
Usala per confrontarla con il risultato filtrato qui sotto.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="222"/>
        <source>Filtered Result</source>
        <translation>Risultato Filtrato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="228"/>
        <source>Filtered result preview.
Shows pixels that match your current HSV color range settings.
Updates in real-time as you adjust the color and range values.
Matching pixels are shown, non-matching pixels appear black.</source>
        <translation>Anteprima del risultato filtrato.
Mostra i pixel che corrispondono alle attuali impostazioni dell&apos;intervallo colore HSV.
Si aggiorna in tempo reale mentre regoli colore e valori di intervallo.
I pixel corrispondenti vengono mostrati, gli altri appaiono in nero.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="235"/>
        <source>Show mask only</source>
        <translation>Mostra solo la maschera</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="237"/>
        <source>Toggle between masked color result and grayscale mask.
• Unchecked (default): Shows the original image with matching colors visible
• Checked: Shows a black and white mask where white = matching pixels
Use the mask view to clearly see which pixels are being detected.</source>
        <translation>Alterna tra risultato a colori mascherato e maschera in scala di grigi.
• Non selezionato (predefinito): mostra l&apos;immagine originale con i colori corrispondenti visibili
• Selezionato: mostra una maschera in bianco e nero dove bianco = pixel corrispondenti
Usa la vista a maschera per vedere chiaramente quali pixel vengono rilevati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="244"/>
        <source>Original:</source>
        <translation>Originale:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="246"/>
        <source>Result:</source>
        <translation>Risultato:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="262"/>
        <source>Pick from Image...</source>
        <translation>Preleva dall&apos;Immagine...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="268"/>
        <source>Test on Image</source>
        <translation>Prova sull&apos;Immagine</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="270"/>
        <source>Test current HSV range settings on the loaded image.
Manually triggers a preview update to see detection results.
Preview updates automatically as you adjust settings.</source>
        <translation>Prova le impostazioni HSV correnti sull&apos;immagine caricata.
Forza manualmente l&apos;aggiornamento dell&apos;anteprima per vedere i risultati di rilevamento.
L&apos;anteprima si aggiorna automaticamente mentre modifichi le impostazioni.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="280"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="282"/>
        <source>Cancel color selection.
Discards all changes and closes the dialog without applying the color range.</source>
        <translation>Annulla la selezione del colore.
Scarta tutte le modifiche e chiude la finestra senza applicare l&apos;intervallo colore.</translation>
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
        <translation>Applica la selezione del colore.
Salva le impostazioni dell&apos;intervallo colore HSV correnti e chiude la finestra.
L&apos;intervallo selezionato verrà usato per l&apos;analisi delle immagini.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="309"/>
        <source>Custom Colors</source>
        <translation>Colori Personalizzati</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="312"/>
        <source>Standard Dialog...</source>
        <translation>Finestra Standard...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="318"/>
        <source>Add Current</source>
        <translation>Aggiungi Corrente</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="381"/>
        <source>Select Color</source>
        <translation>Seleziona Colore</translation>
    </message>
</context>
<context>
    <name>ColorRangeViewer</name>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="14"/>
        <source>Color Range Viewer</source>
        <translation>Visualizzatore Intervallo Colore</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="37"/>
        <source>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</source>
        <translation>Immagini selezionate per la visualizzazione.
Mostra le immagini che hai scelto di visualizzare nel visualizzatore di intervalli.
Fai clic sulle immagini sottostanti per aggiungerle o rimuoverle da questa sezione.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="42"/>
        <source>Selected</source>
        <translation>Selezionate</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="76"/>
        <source>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</source>
        <translation>Immagini disponibili per la visualizzazione.
Mostra tutte le immagini della cartella di input disponibili per la selezione.
Fai clic sulle immagini per spostarle nella sezione Selezionate in alto.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="81"/>
        <source>Unselected</source>
        <translation>Non Selezionate</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="69"/>
        <source>No Colors Selected</source>
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="79"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="258"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
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
        <translation>Slot vuoto - aggiungi un colore personalizzato</translation>
    </message>
</context>
<context>
    <name>CoordinateController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="122"/>
        <source>GPS Coordinates: {coords}</source>
        <translation>Coordinate GPS: {coords}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="148"/>
        <source>📋 Copy coordinates</source>
        <translation>📋 Copia coordinate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="152"/>
        <source>🗺️ Open in Google Maps</source>
        <translation>🗺️ Apri in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="156"/>
        <source>🌍 View in Google Earth</source>
        <translation>🌍 Visualizza in Google Earth</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="160"/>
        <source>📱 Send via WhatsApp</source>
        <translation>📱 Invia tramite WhatsApp</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="164"/>
        <source>📨 Send via Telegram</source>
        <translation>📨 Invia tramite Telegram</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="236"/>
        <source>Coordinates copied</source>
        <translation>Coordinate copiate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="246"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="260"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="323"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="343"/>
        <source>Coordinates unavailable</source>
        <translation>Coordinate non disponibili</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="330"/>
        <source>Coordinate: {lat}, {lon} — {maps}</source>
        <translation>Coordinata: {lat}, {lon} — {maps}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="350"/>
        <source>Coordinates: {lat}, {lon}</source>
        <translation>Coordinate: {lat}, {lon}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="390"/>
        <source>No bearing info available</source>
        <translation>Nessuna info sull&apos;orientamento disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="412"/>
        <source>North-Oriented View (Rotated {angle:.1f}°)</source>
        <translation>Vista orientata a Nord (Ruotata di {angle:.1f}°)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="444"/>
        <source>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</source>
        <translation>Orientamento originale: {bearing:.1f}° | Rotazione applicata: {rotation:.1f}°</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="454"/>
        <source>↑ NORTH</source>
        <translation>↑ NORD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="463"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="474"/>
        <source>Error: {error}</source>
        <translation>Errore: {error}</translation>
    </message>
</context>
<context>
    <name>CoordinatorWindow</name>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="39"/>
        <source>Search Coordinator</source>
        <translation>Coordinatore di Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="58"/>
        <source>Create New Search</source>
        <translation>Crea Nuova Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="63"/>
        <source>Open Existing Search</source>
        <translation>Apri Ricerca Esistente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="68"/>
        <source>Save Search</source>
        <translation>Salva Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="74"/>
        <source>Add Batches to Search</source>
        <translation>Aggiungi Batch alla Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="78"/>
        <source>Add more batch XML files to the current search project</source>
        <translation>Aggiungi altri file XML batch al progetto di ricerca corrente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="96"/>
        <source>Dashboard</source>
        <translation>Dashboard</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="100"/>
        <source>Batch Status</source>
        <translation>Stato Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="104"/>
        <source>AOI Analysis</source>
        <translation>Analisi AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="112"/>
        <source>Review Selected Batch</source>
        <translation>Esamina batch selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="116"/>
        <source>Open the selected batch&apos;s results in the Viewer to review (same as double-clicking the batch).</source>
        <translation>Apri i risultati del batch selezionato nel Visualizzatore per esaminarli (equivale a fare doppio clic sul batch).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="122"/>
        <source>Load Review XML</source>
        <translation>Carica XML di Revisione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="128"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="658"/>
        <source>Export Consolidated Results</source>
        <translation>Esporta Risultati Consolidati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="140"/>
        <source>Project Information</source>
        <translation>Informazioni Progetto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="145"/>
        <source>No project loaded</source>
        <translation>Nessun progetto caricato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="147"/>
        <source>Project:</source>
        <translation>Progetto:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="152"/>
        <source>Created by:</source>
        <translation>Creato da:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="157"/>
        <source>Date:</source>
        <translation>Data:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="176"/>
        <source>Total Batches</source>
        <translation>Batch Totali</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="177"/>
        <source>Total Images</source>
        <translation>Immagini Totali</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="178"/>
        <source>Total Reviews</source>
        <translation>Revisioni Totali</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="179"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="327"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="361"/>
        <source>Reviewers</source>
        <translation>Revisori</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="189"/>
        <source>Review Progress</source>
        <translation>Progresso Revisione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="194"/>
        <source>Overall Completion:</source>
        <translation>Completamento Totale:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="199"/>
        <source>0%</source>
        <translation>0%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="213"/>
        <source>Not Reviewed</source>
        <translation>Non Revisionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="222"/>
        <source>In Progress</source>
        <translation>In Corso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="231"/>
        <source>Complete</source>
        <translation>Completato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="239"/>
        <source>AOI Summary</source>
        <translation>Riepilogo AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="247"/>
        <source>Total AOIs</source>
        <translation>AOI Totali</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="255"/>
        <source>Flagged AOIs</source>
        <translation>AOI Contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="262"/>
        <source>Active Reviewers</source>
        <translation>Revisori Attivi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="264"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="714"/>
        <source>No reviewers yet</source>
        <translation>Ancora nessun revisore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="312"/>
        <source>Batch review status and assignments. Load reviewer XMLs to update progress. Double-click a batch to open its results in the Viewer.</source>
        <translation>Stato e assegnazioni della revisione batch. Carica gli XML dei revisori per aggiornare l&apos;avanzamento. Fai doppio clic su un batch per aprire i risultati nel Visualizzatore.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="323"/>
        <source>Batch ID</source>
        <translation>ID Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="324"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="325"/>
        <source>Images</source>
        <translation>Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="326"/>
        <source>Reviews</source>
        <translation>Revisioni</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="328"/>
        <source>Status</source>
        <translation>Stato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="349"/>
        <source>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</source>
        <translation>Dati AOI consolidati da tutte le revisioni. Mostra il numero di contrassegni e i commenti dei revisori.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="358"/>
        <source>Image</source>
        <translation>Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="359"/>
        <source>Location</source>
        <translation>Posizione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="360"/>
        <source>Flag Count</source>
        <translation>Conteggio Contrassegni</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="362"/>
        <source>Comments</source>
        <translation>Commenti</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="379"/>
        <source>New Search Project</source>
        <translation>Nuovo Progetto di Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="380"/>
        <source>Enter project name:</source>
        <translation>Inserisci il nome del progetto:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="389"/>
        <source>Coordinator Information</source>
        <translation>Informazioni Coordinatore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="390"/>
        <source>Enter your name:</source>
        <translation>Inserisci il tuo nome:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="399"/>
        <source>Select Batch Files</source>
        <translation>Seleziona File Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="400"/>
        <source>Select Initial Batch XML Files</source>
        <translation>Seleziona i File XML Batch Iniziali</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="403"/>
        <source>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</source>
        <translation>Puoi selezionare più file ADIAT_Data.xml da diverse cartelle.

Suggerimenti:
• Tieni premuto Ctrl (Windows/Linux) o Cmd (Mac) per selezionare più file
• Puoi aggiungere altri batch in seguito usando il pulsante &apos;Aggiungi Batch alla Ricerca&apos;
• Ogni batch deve essere un file ADIAT_Data.xml elaborato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="417"/>
        <source>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</source>
        <translation>Seleziona i File ADIAT_Data.xml Batch (Tieni premuto Ctrl per selezionarne più di uno)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="419"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="434"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="558"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="605"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="660"/>
        <source>XML Files (*.xml)</source>
        <translation>File XML (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <source>Save Search Project</source>
        <translation>Salva Progetto di Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="444"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="517"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="577"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="641"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="667"/>
        <source>Success</source>
        <translation>Successo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="445"/>
        <source>Search project &apos;{project}&apos; created successfully!</source>
        <translation>Progetto di ricerca &apos;{project}&apos; creato con successo!</translation>
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
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="453"/>
        <source>Failed to save project file.</source>
        <translation>Impossibile salvare il file di progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="456"/>
        <source>Failed to create project.</source>
        <translation>Impossibile creare il progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="462"/>
        <source>Open Search Project</source>
        <translation>Apri Progetto di Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="464"/>
        <source>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</source>
        <translation>File Progetto di Ricerca (ADIAT_Search_*.xml);;Tutti i File XML (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="474"/>
        <source>Project loaded successfully!</source>
        <translation>Progetto caricato con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="493"/>
        <source>Search project file not found:
{path}</source>
        <translation>File del progetto di ricerca non trovato:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="507"/>
        <source>Failed to load project file.</source>
        <translation>Impossibile caricare il file di progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="518"/>
        <source>Project saved successfully!</source>
        <translation>Progetto salvato con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="521"/>
        <source>Failed to save project.</source>
        <translation>Impossibile salvare il progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="528"/>
        <source>No Project</source>
        <translation>Nessun Progetto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="529"/>
        <source>Please create or open a project first.</source>
        <translation>Crea o apri prima un progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="536"/>
        <source>Add Batches</source>
        <translation>Aggiungi Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="537"/>
        <source>Add More Batch XML Files</source>
        <translation>Aggiungi Altri File XML Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="540"/>
        <source>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</source>
        <translation>Seleziona file batch ADIAT_Data.xml aggiuntivi da aggiungere a questa ricerca.

Suggerimenti:
• Tieni premuto Ctrl (Windows/Linux) o Cmd (Mac) per selezionare più file
• I file possono trovarsi in cartelle diverse
• Ogni batch deve essere un file ADIAT_Data.xml elaborato
• I nuovi batch verranno numerati sequenzialmente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="556"/>
        <source>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</source>
        <translation>Seleziona i File ADIAT_Data.xml Batch da Aggiungere (Tieni premuto Ctrl per selezionarne più di uno)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="579"/>
        <source>Successfully added {count} batch(es) to the project!
Total batches: {total}</source>
        <translation>Aggiunti con successo {count} batch al progetto!
Batch totali: {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="589"/>
        <source>No Batches Added</source>
        <translation>Nessun Batch Aggiunto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="591"/>
        <source>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</source>
        <translation>Nessun batch aggiunto. Controlla che i file XML siano file ADIAT_Data.xml validi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="603"/>
        <source>Select Reviewer&apos;s ADIAT_Data.xml File</source>
        <translation>Seleziona il file ADIAT_Data.xml del revisore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="616"/>
        <source>No Batches</source>
        <translation>Nessun Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="617"/>
        <source>No batches found in project.</source>
        <translation>Nessun batch trovato nel progetto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="625"/>
        <source>Select Batch</source>
        <translation>Seleziona Batch</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="626"/>
        <source>Which batch does this review belong to?</source>
        <translation>A quale batch appartiene questa revisione?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="642"/>
        <source>Review data loaded and merged successfully!</source>
        <translation>Dati di revisione caricati e uniti con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="648"/>
        <source>Failed to load review data.</source>
        <translation>Impossibile caricare i dati di revisione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="668"/>
        <source>Consolidated results exported to:
{path}</source>
        <translation>Risultati consolidati esportati in:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="671"/>
        <source>Failed to export results.</source>
        <translation>Impossibile esportare i risultati.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="697"/>
        <source>{value}%</source>
        <translation>{value}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="758"/>
        <source>No Batch Selected</source>
        <translation>Nessun batch selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="759"/>
        <source>Select a batch in the table, then click Review Selected Batch.</source>
        <translation>Seleziona un batch nella tabella, quindi fai clic su Esamina batch selezionato.</translation>
    </message>
</context>
<context>
    <name>CoverageExtentExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="129"/>
        <source>Generate Coverage Extent KML</source>
        <translation>Genera KML Estensione Copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="131"/>
        <source>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</source>
        <translation>Generare un file KML che mostri l&apos;estensione della copertura geografica di tutte le immagini?

Questo creerà dei poligoni che rappresentano l&apos;area coperta da tutte le immagini. Le aree delle immagini sovrapposte verranno unite in un unico poligono.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="145"/>
        <source>Save Coverage Extent KML</source>
        <translation>Salva KML Estensione Copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="147"/>
        <source>KML files (*.kml)</source>
        <translation>File KML (*.kml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="160"/>
        <source>Generating Coverage Extent KML</source>
        <translation>Generazione KML Estensione Copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="163"/>
        <source>Calculating coverage extent...</source>
        <translation>Calcolo dell&apos;estensione della copertura...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="209"/>
        <source>Error generating coverage extent KML</source>
        <translation>Errore durante la generazione del file KML dell&apos;estensione della copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="215"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="263"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="216"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="264"/>
        <source>Failed to generate coverage extent KML:
{error}</source>
        <translation>Impossibile generare il file KML dell&apos;estensione della copertura:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="246"/>
        <source>Coverage extent generation cancelled</source>
        <translation>Generazione dell&apos;estensione della copertura annullata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="257"/>
        <source>Error generating coverage extent</source>
        <translation>Errore durante la generazione dell&apos;estensione della copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="270"/>
        <source>No valid images found for coverage extent calculation</source>
        <translation>Nessuna immagine valida trovata per il calcolo dell&apos;estensione della copertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="276"/>
        <source>Coverage Extent</source>
        <translation>Estensione della Copertura</translation>
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
        <translation>Impossibile calcolare l&apos;estensione della copertura.

Immagini elaborate: {processed}
Immagini saltate: {skipped}

Le immagini possono essere saltate per i seguenti motivi:
  • Dati GPS mancanti negli EXIF
  • Nessun GSD valido (altitudine/lunghezza focale mancante)
  • Gimbal non nadirale (deve essere tra -85° e -95°)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="300"/>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="301"/>
        <source>{value:.2f} acres</source>
        <translation>{value:.2f} acri</translation>
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
        <translation>KML dell&apos;estensione della copertura salvato: {area}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="318"/>
        <source>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</source>
        <translation>

Le immagini possono essere saltate per:
  • Dati GPS mancanti
  • Nessun GSD valido
  • Gimbal non nadirale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="326"/>
        <source>Coverage Extent KML Generated</source>
        <translation>KML dell&apos;Estensione della Copertura Generato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="328"/>
        <source>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</source>
        <translation>File KML dell&apos;estensione della copertura creato con successo!

File: {file}
Immagini elaborate: {processed}
Immagini saltate: {skipped}
Aree di copertura: {areas}
Area totale: {area}{skip_info}</translation>
    </message>
</context>
<context>
    <name>DetectionRowWidget</name>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="62"/>
        <source>CLASS</source>
        <translation>CLASSE</translation>
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
        <translation>Flusso: --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="109"/>
        <source>View</source>
        <translation>Visualizza</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="112"/>
        <source>Open the full-size thumbnail and metadata.</source>
        <translation>Apri la miniatura a dimensione intera e i metadati.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="119"/>
        <source>Copy GPS</source>
        <translation>Copia GPS</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="122"/>
        <source>Copy the detection&apos;s coordinates to the clipboard in the operator-preferred format.</source>
        <translation>Copia le coordinate del rilevamento negli appunti nel formato preferito dall&apos;operatore.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="115"/>
        <source>{name} ({code})</source>
        <translation>{name} ({code})</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="124"/>
        <source>Feed: {feed}</source>
        <translation>Flusso: {feed}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="132"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Numero di serie del drone: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="150"/>
        <source>no
thumb</source>
        <translation>nessuna
miniatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="156"/>
        <source>bad
thumb</source>
        <translation>miniatura
non valida</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="224"/>
        <source>Detection</source>
        <translation>Rilevamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="283"/>
        <source>No image available.</source>
        <translation>Nessuna immagine disponibile.</translation>
    </message>
</context>
<context>
    <name>DirectoriesPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="55"/>
        <source>Select Input Directory</source>
        <translation>Seleziona Cartella di Input</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="72"/>
        <source>Select Output Directory</source>
        <translation>Seleziona Cartella di Output</translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="58"/>
        <source>Processing...</source>
        <translation>Elaborazione in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="72"/>
        <source>Starting...</source>
        <translation>Avvio in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="76"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="103"/>
        <source>Cancelling...</source>
        <translation>Annullamento in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="104"/>
        <source>Cancellation requested...</source>
        <translation>Annullamento richiesto...</translation>
    </message>
</context>
<context>
    <name>FlightPairingDialog</name>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="14"/>
        <source>Add Flight Feed</source>
        <translation>Aggiungi flusso di volo</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="27"/>
        <source>Ask the drone operator to read out the 6-character pairing code shown on their controller.</source>
        <translation>Chiedi all&apos;operatore del drone di leggere il codice di abbinamento a 6 caratteri mostrato sul controller.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="40"/>
        <source>e.g. K3F7PM</source>
        <translation>es. K3F7PM</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="85"/>
        <source>Pairing…</source>
        <translation>Abbinamento…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="98"/>
        <source>Looking up code, exchanging keys, gathering ICE candidates.</source>
        <translation>Ricerca del codice, scambio delle chiavi, raccolta dei candidati ICE.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="135"/>
        <source>Pairing failed</source>
        <translation>Abbinamento non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="69"/>
        <location filename="../resources/views/flight/flight_pairing.ui" line="200"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="207"/>
        <source>Connect</source>
        <translation>Connetti</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="67"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="85"/>
        <source>drone has {current}/{limit} viewers</source>
        <translation>il drone ha {current}/{limit} visualizzatori</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="98"/>
        <source>known device — same fingerprint as last pair</source>
        <translation>dispositivo noto — stessa impronta dell&apos;ultimo abbinamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="101"/>
        <source>new device</source>
        <translation>nuovo dispositivo</translation>
    </message>
</context>
<context>
    <name>FlightTile</name>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="460"/>
        <source>Feed {code}</source>
        <translation>Flusso {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="298"/>
        <source>Choose recording directory</source>
        <translation>Scegli cartella registrazioni</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="328"/>
        <source>REC ● {filename}</source>
        <translation>REC ● {filename}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="333"/>
        <source>REC error: {msg}</source>
        <translation>Errore REC: {msg}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="341"/>
        <source>REC failed to start</source>
        <translation>Avvio registrazione non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="355"/>
        <source>Recording saved</source>
        <translation>Registrazione salvata</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="364"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="383"/>
        <source>Network: {state}</source>
        <translation>Rete: {state}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="377"/>
        <source>latency: {ms:.0f}ms</source>
        <translation>latenza: {ms:.0f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="379"/>
        <source>latency: --</source>
        <translation>latenza: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="457"/>
        <source>{name} · {code}</source>
        <translation>{name} · {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="482"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Numero di serie del drone: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="520"/>
        <source>Rename Feed</source>
        <translation>Rinomina flusso</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="522"/>
        <source>Nickname for this drone (persists across new pairing codes via the aircraft serial number). Leave blank to clear.</source>
        <translation>Soprannome per questo drone (rimane valido tra nuovi codici di abbinamento tramite il numero di serie del drone). Lascia vuoto per cancellarlo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="554"/>
        <source>Initializing</source>
        <translation>Inizializzazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="555"/>
        <source>Connecting</source>
        <translation>Connessione</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="556"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="557"/>
        <source>Connected</source>
        <translation>Connesso</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="558"/>
        <source>Disconnected</source>
        <translation>Disconnesso</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="559"/>
        <source>Failed</source>
        <translation>Non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="560"/>
        <source>Closed</source>
        <translation>Chiuso</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="574"/>
        <source>Rename Feed...</source>
        <translation>Rinomina flusso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="591"/>
        <source>Restore</source>
        <translation>Ripristina</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="595"/>
        <source>Maximize</source>
        <translation>Massimizza</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="580"/>
        <source>Full Screen</source>
        <translation>Schermo intero</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="601"/>
        <source>Mute Detections in Gallery</source>
        <translation>Nascondi rilevamenti nella galleria</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="617"/>
        <source>Stop Recording</source>
        <translation>Interrompi registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="621"/>
        <source>Start Recording…</source>
        <translation>Avvia registrazione…</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="625"/>
        <source>Reconnect</source>
        <translation>Riconnetti</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="631"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
</context>
<context>
    <name>FlightTileContents</name>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="44"/>
        <source>Waiting for video…</source>
        <translation>In attesa del video…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="90"/>
        <source>Network: new</source>
        <translation>Rete: nuova</translation>
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
        <translation>latenza: --</translation>
    </message>
</context>
<context>
    <name>FlightTileController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="191"/>
        <source>Looking up code {code} and connecting to the drone.</source>
        <translation>Ricerca del codice {code} e connessione al drone.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="266"/>
        <source>Name this device</source>
        <translation>Assegna un nome a questo dispositivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="268"/>
        <source>Give this publisher a name so you can recognise it next time (e.g. &apos;Operator A&apos;s M4E&apos;).</source>
        <translation>Dai un nome a questo emittente per riconoscerlo la prossima volta (ad es. &apos;M4E operatore A&apos;).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="286"/>
        <source>Device &apos;{label}&apos; presented a different DTLS fingerprint than the last time you paired with it. This could mean the controller was reset, a different controller is using the label, or somebody is impersonating it.

Reject if you weren&apos;t expecting this.</source>
        <translation>Il dispositivo &apos;{label}&apos; ha presentato un&apos;impronta DTLS diversa rispetto all&apos;ultimo abbinamento. Potrebbe significare che il controller è stato reimpostato, che un controller diverso usa questa etichetta o che qualcuno sta tentando di impersonarlo.

Rifiuta se non te lo aspettavi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="453"/>
        <source>Pairing ended before video could start. Ask the operator to generate a new code and try again.</source>
        <translation>L&apos;abbinamento è terminato prima dell&apos;avvio del video. Chiedi all&apos;operatore di generare un nuovo codice e riprova.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="294"/>
        <source>Fingerprint mismatch — &apos;{label}&apos;</source>
        <translation>Impronta non corrispondente — &apos;{label}&apos;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="303"/>
        <source>Fingerprint changed on {ts}; previous identity was overwritten after operator review.</source>
        <translation>Impronta modificata il {ts}; l&apos;identità precedente è stata sovrascritta dopo la verifica dell&apos;operatore.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="395"/>
        <source>This drone already has {current} viewers connected (maximum {limit}). Ask one to disconnect, or try again later.</source>
        <translation>Questo drone ha già {current} visualizzatori connessi (massimo {limit}). Chiedi a uno di disconnettersi oppure riprova più tardi.</translation>
    </message>
</context>
<context>
    <name>FlightViewerController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="499"/>
        <source>New flight session</source>
        <translation>Nuova sessione di volo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="501"/>
        <source>Mobile started a new flight under code {code}. The previous session&apos;s detections are still saved on this computer. Discard them, or keep them archived?</source>
        <translation>Mobile ha avviato un nuovo volo con il codice {code}. I rilevamenti della sessione precedente sono ancora salvati su questo computer. Vuoi eliminarli o conservarli in archivio?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="627"/>
        <source>Image Analysis</source>
        <translation>Analisi immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="650"/>
        <source>Streaming Detector</source>
        <translation>Rilevatore streaming</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="667"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="668"/>
        <source>Failed to open {target}:
{error}</source>
        <translation>Impossibile aprire {target}:
{error}</translation>
    </message>
</context>
<context>
    <name>FlightViewerWindow</name>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="14"/>
        <source>ADIAT Flight Viewer</source>
        <translation>Visore voli ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="21"/>
        <source>Add a feed to begin.  Use Add Feed in the toolbar.</source>
        <translation>Aggiungi un flusso per iniziare. Usa Aggiungi flusso nella barra degli strumenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="76"/>
        <source>Main Toolbar</source>
        <translation>Barra degli strumenti principale</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="97"/>
        <source>+ Add Feed</source>
        <translation>+ Aggiungi flusso</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="49"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="66"/>
        <source>Help</source>
        <translation>Aiuto</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="100"/>
        <source>Pair with an ADIAT Mobile drone controller using a 6-character code.</source>
        <translation>Abbina un controller drone ADIAT Mobile usando un codice a 6 caratteri.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="105"/>
        <source>Mission Gallery</source>
        <translation>Galleria missione</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="114"/>
        <source>Show or hide the aggregate Mission Gallery panel.</source>
        <translation>Mostra o nascondi il pannello aggregato Galleria missione.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="119"/>
        <source>Save Layout</source>
        <translation>Salva layout</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="122"/>
        <source>Save the current dock arrangement for next session.</source>
        <translation>Salva la disposizione corrente dei pannelli per la prossima sessione.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="127"/>
        <source>Restore Layout</source>
        <translation>Ripristina layout</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="130"/>
        <source>Apply the last saved dock arrangement.</source>
        <translation>Applica l&apos;ultima disposizione dei pannelli salvata.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="135"/>
        <source>Close Viewer</source>
        <translation>Chiudi visore</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="140"/>
        <source>Map</source>
        <translation>Mappa</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="149"/>
        <source>Show or hide the detection map dock.</source>
        <translation>Mostra o nascondi il pannello mappa dei rilevamenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="154"/>
        <source>Open Image Analysis</source>
        <translation>Apri Analisi immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="157"/>
        <source>Switch to the Image Analysis window for post-flight image review.</source>
        <translation>Passa alla finestra Analisi immagini per la revisione delle immagini post-volo.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="162"/>
        <source>Open Streaming Detector</source>
        <translation>Apri Rilevatore streaming</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="165"/>
        <source>Switch to the Streaming Detector window for RTMP / HDMI capture sessions.</source>
        <translation>Passa alla finestra Rilevatore streaming per sessioni di acquisizione RTMP / HDMI.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="170"/>
        <source>ADIAT Help</source>
        <translation>Aiuto ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="173"/>
        <source>Open the ADIAT documentation in your browser.</source>
        <translation>Apri la documentazione ADIAT nel browser.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightViewerWindow.py" line="274"/>
        <source>Rename Feed...</source>
        <translation>Rinomina flusso...</translation>
    </message>
</context>
<context>
    <name>FrameTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="52"/>
        <source>Enable Processing Region Mask</source>
        <translation>Abilita Maschera Regione di Elaborazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="55"/>
        <source>Enable to restrict detection processing to a specific region of the video.
Useful for excluding edges, UI overlays, or focusing on specific areas.
Improves performance by not processing masked regions.</source>
        <translation>Attiva per limitare l&apos;elaborazione del rilevamento a una specifica area del video.
Utile per escludere i bordi, gli overlay dell&apos;interfaccia o concentrarsi su aree specifiche.
Migliora le prestazioni evitando di elaborare le aree mascherate.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="67"/>
        <source>Enable Frame Buffer</source>
        <translation>Abilita Frame Buffer</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="69"/>
        <source>Exclude a uniform border from all edges of the video.
Enter the number of pixels to exclude from each edge.
The inner area will be processed for detections.</source>
        <translation>Esclude un bordo uniforme su tutti i lati del video.
Inserisci il numero di pixel da escludere da ogni lato.
L&apos;area interna verrà elaborata per il rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="77"/>
        <source>Frame Buffer Settings</source>
        <translation>Impostazioni Frame Buffer</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="82"/>
        <source>Buffer (pixels):</source>
        <translation>Buffer (pixel):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="87"/>
        <source>Number of pixels to exclude from all edges (0-1000).
A value of 50 excludes 50 pixels from top, bottom, left, and right.
Useful for removing UI overlays or camera lens distortion at edges.
This value is based on the original video resolution.</source>
        <translation>Numero di pixel da escludere da tutti i bordi (0-1000).
Un valore di 50 esclude 50 pixel da alto, basso, sinistra e destra.
Utile per rimuovere overlay dell&apos;interfaccia o distorsioni di lente ai bordi.
Il valore è riferito alla risoluzione originale del video.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="97"/>
        <source>Enable Image Mask</source>
        <translation>Abilita Maschera Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="99"/>
        <source>Load a black/white image as a custom mask.
White areas will be processed, black areas excluded.
The mask will be scaled to match the video resolution.</source>
        <translation>Carica un&apos;immagine in bianco e nero come maschera personalizzata.
Le aree bianche verranno elaborate, le aree nere escluse.
La maschera verrà ridimensionata in base alla risoluzione del video.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="107"/>
        <source>Image Mask Settings</source>
        <translation>Impostazioni Maschera Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="114"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="211"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="332"/>
        <source>No mask image selected</source>
        <translation>Nessuna immagine maschera selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="117"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="118"/>
        <source>Select a black/white image file to use as mask</source>
        <translation>Seleziona un file immagine in bianco e nero da usare come maschera</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="121"/>
        <source>Clear</source>
        <translation>Cancella</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="122"/>
        <source>Clear the selected mask image</source>
        <translation>Cancella l&apos;immagine maschera selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="128"/>
        <source>White = Process, Black = Exclude</source>
        <translation>Bianco = Elabora, Nero = Escludi</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="136"/>
        <source>Visualization</source>
        <translation>Visualizzazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="139"/>
        <source>Show mask overlay on video</source>
        <translation>Mostra overlay della maschera sul video</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="142"/>
        <source>Display the processing region on the rendered video.
Frame mode: Shows a cyan rectangle outline of the processed area.
Image mask: Shows a semi-transparent overlay of excluded regions.</source>
        <translation>Mostra la regione di elaborazione sul video renderizzato.
Modalità frame: mostra un riquadro ciano del contorno dell&apos;area elaborata.
Maschera immagine: mostra un overlay semitrasparente delle aree escluse.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="226"/>
        <source>Invalid Image</source>
        <translation>Immagine Non Valida</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="227"/>
        <source>{error}</source>
        <translation>{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="229"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>Impossibile caricare l&apos;immagine selezionata. Scegli un file immagine valido.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="238"/>
        <source>Aspect Ratio Mismatch</source>
        <translation>Mancata Corrispondenza Proporzioni</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="240"/>
        <source>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</source>
        <translation>{error}

La maschera verrà scalata per adattarsi, il che potrebbe causare distorsioni.

Vuoi continuare?</translation>
    </message>
</context>
<context>
    <name>GPSMapController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="104"/>
        <source>No GPS data found in images</source>
        <translation>Nessun dato GPS trovato nelle immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="189"/>
        <source>POD overlay cleared — the elevation/canopy source changed. Recalculate to refresh it.</source>
        <translation>Sovrapposizione POD cancellata: la sorgente di elevazione/chioma è cambiata. Ricalcola per aggiornarla.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="200"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Il download delle tile è disabilitato nella modalità solo offline</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="231"/>
        <source>Calculate POD Coverage?</source>
        <translation>Calcolare la copertura POD?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="232"/>
        <source>Coverage data is ready. Calculate the probability-of-detection heatmap for this mission now? (May take several minutes.)</source>
        <translation>I dati di copertura sono pronti. Calcolare ora la heatmap della probabilità di rilevamento per questa missione? (Può richiedere diversi minuti.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="291"/>
        <source>Your local USGS 3DEP tiles only partially cover this mission.</source>
        <translation>I tile locali USGS 3DEP coprono solo parzialmente questa missione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="294"/>
        <source>Your local USGS 3DEP tiles do not cover this mission.</source>
        <translation>I tile locali USGS 3DEP non coprono questa missione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="298"/>
        <source>Local Elevation Coverage</source>
        <translation>Copertura dell&apos;elevazione locale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="300"/>
        <source>Frames outside the local tiles will use online AWS Terrain Tiles (~30 m) elevation instead. You can download 1 m tiles for this area first, or continue with the fallback.</source>
        <translation>I fotogrammi fuori dai tile locali useranno l&apos;elevazione online di AWS Terrain Tiles (~30 m). Puoi prima scaricare i tile a 1 m per quest&apos;area oppure continuare con il fallback.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="303"/>
        <source>Download Tiles...</source>
        <translation>Scarica tile...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="305"/>
        <source>Continue</source>
        <translation>Continua</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="334"/>
        <source>POD calculation is unavailable</source>
        <translation>Il calcolo POD non è disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="353"/>
        <source>The tile downloader is unavailable</source>
        <translation>Il downloader delle tile non è disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="383"/>
        <source>Download Canopy Data?</source>
        <translation>Scaricare i dati della chioma?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="384"/>
        <source>No canopy-height data is configured for this mission.

Download elevation and canopy tiles for this area now so the canopy overlay and terrain-aware detection coverage can use them?

This downloads Meta/WRI canopy height (1 m) and sets it as the canopy source, replacing any LANDFIRE selection (LANDFIRE tiles must be added manually).</source>
        <translation>Nessun dato di altezza della chioma è configurato per questa missione.

Scaricare ora le tile di elevazione e chioma per quest&apos;area affinché la sovrapposizione della chioma e la copertura di rilevamento con analisi del terreno possano utilizzarle?

Questo scarica l&apos;altezza chioma Meta/WRI (1 m) e la imposta come origine dati chioma, sostituendo qualsiasi selezione LANDFIRE (le tile LANDFIRE devono essere aggiunte manualmente).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="579"/>
        <source>Not covered — no looks</source>
        <translation>Non coperto — nessuna osservazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="580"/>
        <source>Terrain occlusion</source>
        <translation>Occlusione del terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="581"/>
        <source>Canopy</source>
        <translation>Chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="582"/>
        <source>Image resolution (GSD)</source>
        <translation>Risoluzione immagine (GSD)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="583"/>
        <source>None</source>
        <translation>Nessuno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="585"/>
        <source>Unknown</source>
        <translation>Sconosciuto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="765"/>
        <source>Building canopy overlay...</source>
        <translation>Creazione della sovrapposizione della chioma...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="791"/>
        <source>No canopy data covers this area</source>
        <translation>Nessun dato sulla chioma copre quest&apos;area</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="851"/>
        <source>POD: {pod}% (beta)   Looks: {looks}</source>
        <translation>POD: {pod}% (beta)   Osservazioni: {looks}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="854"/>
        <source>Limiting factor: {factor}</source>
        <translation>Fattore limitante: {factor}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="889"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="902"/>
        <source>Image {n}</source>
        <translation>Immagine {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="890"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="905"/>
        <source>View {name}</source>
        <translation>Vista {name}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="862"/>
        <source>Find location in images</source>
        <translation>Trova posizione nelle immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="909"/>
        <source>{name} (no flagged AOIs)</source>
        <translation>{name} (nessun AOI contrassegnato)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1044"/>
        <source>GPS coordinate not in any images</source>
        <translation>Coordinata GPS non presente in nessuna immagine</translation>
    </message>
</context>
<context>
    <name>GPSMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="54"/>
        <source>GPS Map View</source>
        <translation>Vista Mappa GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="108"/>
        <source>Zoom In (+)</source>
        <translation>Ingrandisci (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="112"/>
        <source>Zoom Out (-)</source>
        <translation>Rimpicciolisci (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="116"/>
        <source>Fit All (F)</source>
        <translation>Adatta Tutto (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="120"/>
        <source>Rotate (R)</source>
        <translation>Ruota (R)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="128"/>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="338"/>
        <source>Satellite View</source>
        <translation>Vista Satellitare</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="135"/>
        <source>POD Overlay</source>
        <translation>Sovrapposizione POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="139"/>
        <source>Run a map export with the POD option to generate this overlay</source>
        <translation>Esegui un&apos;esportazione mappa con l&apos;opzione POD per generare questa sovrapposizione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="144"/>
        <source>POD (beta)</source>
        <translation>POD (beta)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="145"/>
        <source>Look count</source>
        <translation>Numero di osservazioni</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="146"/>
        <source>Canopy height</source>
        <translation>Altezza della chioma</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="156"/>
        <source>POD overlay opacity</source>
        <translation>Opacità della sovrapposizione POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="162"/>
        <source>Download Canopy Tiles</source>
        <translation>Scarica tile chioma</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="169"/>
        <source>Calculate POD</source>
        <translation>Calcola POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="171"/>
        <source>Compute the terrain-aware probability-of-detection heatmap for this mission (may take several minutes)</source>
        <translation>Calcola la heatmap della probabilità di rilevamento con analisi del terreno per questa missione (può richiedere diversi minuti)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="179"/>
        <source>Click point to select • Drag to pan • Scroll to zoom</source>
        <translation>Clicca su un punto per selezionare • Trascina per scorrere • Scorri per lo zoom</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="263"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>Il download delle tile è disabilitato nella modalità solo offline</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="265"/>
        <source>Download elevation and canopy-height tiles for this mission&apos;s area</source>
        <translation>Scarica le tile di elevazione e altezza della chioma per l&apos;area di questa missione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="335"/>
        <source>Map View</source>
        <translation>Vista Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="372"/>
        <source>⚠ {error}</source>
        <translation>⚠ {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="382"/>
        <source>Map Tile Loading Issue</source>
        <translation>Problema di Caricamento Tasselli Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="384"/>
        <source>{error}

The map will continue to work with cached tiles where available.</source>
        <translation>{error}

La mappa continuerà a funzionare con i tasselli memorizzati nella cache, ove disponibili.</translation>
    </message>
</context>
<context>
    <name>GPSMapView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1216"/>
        <source>Copy Data</source>
        <translation>Copia Dati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1770"/>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1878"/>
        <source>Zoom FOV</source>
        <translation>Zoom FOV</translation>
    </message>
</context>
<context>
    <name>GalleryUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="369"/>
        <source>0 AOIs</source>
        <translation>0 AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOI</source>
        <translation>AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="410"/>
        <source>AOIs</source>
        <translation>AOI</translation>
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
        <translation>Area di Interesse</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="432"/>
        <source>Areas of Interest</source>
        <translation>Aree di Interesse</translation>
    </message>
</context>
<context>
    <name>GeneralSettingsPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="121"/>
        <source>Select AOI Highlight Color</source>
        <translation>Seleziona Colore Evidenziazione AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="159"/>
        <source>Benchmark Complete</source>
        <translation>Benchmark Completato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="161"/>
        <source>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</source>
        <translation>Rilevati {count} core CPU.

Numero consigliato di processi: {recommended}

Il cursore è stato impostato su {recommended} processi.</translation>
    </message>
</context>
<context>
    <name>GridReviewController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="151"/>
        <source>Grid review works in single-image mode — exit the gallery first.</source>
        <translation>La revisione a griglia funziona in modalità immagine singola; esci prima dalla galleria.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="273"/>
        <source>This image keeps its existing grid — the new size applies to unstarted images.</source>
        <translation>Questa immagine mantiene la griglia esistente; la nuova dimensione si applica alle immagini non ancora avviate.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="320"/>
        <source>Apply Grid to All Images</source>
        <translation>Applica griglia a tutte le immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="322"/>
        <source>{n} image(s) already have review progress recorded at a different grid size.

Reset their progress and apply {rows}×{cols} to them too?

Yes resets them; No keeps them at their current size.</source>
        <translation>{n} immagini hanno già progressi di revisione registrati con una dimensione della griglia diversa.

Reimpostare i loro progressi e applicare anche {rows}×{cols}?

Sì le reimposta; No le mantiene alla dimensione attuale.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="391"/>
        <source>Image fully reviewed — advancing</source>
        <translation>Immagine completamente revisionata; avanzamento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="628"/>
        <source>cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed</source>
        <translation>cella {cell}/{cells} — immagine {image}/{images} — sessione {percent}% revisionata</translation>
    </message>
</context>
<context>
    <name>GridReviewDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="52"/>
        <source>Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)</source>
        <translation>Suggerito: {rows}×{cols} (persona ≈ {px} px sullo schermo con zoom sulla cella)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="55"/>
        <source>Suggested: {rows}×{cols}</source>
        <translation>Suggerito: {rows}×{cols}</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="14"/>
        <source>Grid Review Settings</source>
        <translation>Impostazioni revisione a griglia</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="23"/>
        <source>Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.</source>
        <translation>Scegliere in quante celle la griglia di revisione divide ogni immagine. Celle più piccole significano uno zoom maggiore per cella.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="32"/>
        <source>Rows</source>
        <translation>Righe</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="52"/>
        <source>Columns</source>
        <translation>Colonne</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="74"/>
        <source>Mark cells reviewed when advancing (Space)</source>
        <translation>Segna le celle come revisionate quando si avanza (Spazio)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="84"/>
        <source>Draw a 3×3 guide inside the active cell to focus your scan. Visual only — it does not change what gets reviewed.</source>
        <translation>Disegna una guida 3×3 all&apos;interno della cella attiva per concentrare la scansione. Solo visuale; non cambia ciò che viene revisionato.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="87"/>
        <source>Show 3×3 focus guide inside each cell</source>
        <translation>Mostra la guida 3×3 dentro ogni cella</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="97"/>
        <source>Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.</source>
        <translation>Applica le righe e le colonne scelte a ogni immagine in questo set di dati, non solo a quella corrente. Le immagini di cui è già stata iniziata la revisione mantengono i progressi a meno che non si confermi un ripristino.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="100"/>
        <source>Apply this grid size to all images</source>
        <translation>Applica questa dimensione della griglia a tutte le immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="112"/>
        <source>No grid suggestion available (image GSD unknown).</source>
        <translation>Nessun suggerimento di griglia disponibile (GSD dell&apos;immagine sconosciuto).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="119"/>
        <source>Use Suggestion</source>
        <translation>Usa suggerimento</translation>
    </message>
</context>
<context>
    <name>HSVColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
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
        <translation>Seleziona un colore obiettivo da un&apos;immagine da rilevare.
Apre un selettore di colori che ti consente di:
• Caricare un&apos;immagine dalla cartella di input
• Cliccare sui pixel per campionare i colori
• Calcolare automaticamente i valori HSV
• Impostare gli intervalli di Tonalità, Saturazione e Valore
Il colore selezionato diventa il centro del tuo intervallo di rilevamento HSV.
Regola i valori dell&apos;intervallo +/- per catturare le variazioni di colore.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="37"/>
        <source> Pick Color</source>
        <translation> Scegli Colore</translation>
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
        <translation>Anteprima visiva del colore obiettivo attualmente selezionato.
Mostra il colore centrale del tuo intervallo di rilevamento HSV.
Il rilevamento effettivo corrisponderà ai colori entro gli intervalli +/- specificati attorno a questo colore.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="92"/>
        <source>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</source>
        <translation>Tolleranza dell&apos;intervallo di tonalità per il rilevamento del colore.
La tonalità rappresenta il colore effettivo (rosso, verde, blu, ecc.) su una scala 0-179.
Regola i valori -/+ per consentire variazioni nella tonalità del colore.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="97"/>
        <source>Hue Range</source>
        <translation>Intervallo Tonalità</translation>
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
        <translation>Tolleranza inferiore dell&apos;intervallo di tonalità.
• Intervallo: da 0 a 179
• Predefinito: 20
Sottrae dal valore della tonalità obiettivo per definire il limite inferiore.
Valori più bassi = corrispondenza del colore più rigorosa, valori più alti = maggiore variazione di colore accettata.
Esempio: Tonalità obiettivo 100, meno 20 = rileva tonalità da 80 a 100.</translation>
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
        <translation>Tolleranza superiore dell&apos;intervallo di tonalità.
• Intervallo: da 0 a 179
• Predefinito: 20
Aggiunge al valore della tonalità obiettivo per definire il limite superiore.
Valori più bassi = corrispondenza del colore più rigorosa, valori più alti = maggiore variazione di colore accettata.
Esempio: Tonalità obiettivo 100, più 20 = rileva tonalità da 100 a 120.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="198"/>
        <source>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</source>
        <translation>Tolleranza dell&apos;intervallo di saturazione per il rilevamento del colore.
La saturazione rappresenta l&apos;intensità del colore (0=grigio, 255=completamente saturo) su una scala 0-255.
Regola i valori -/+ per consentire variazioni nell&apos;intensità del colore.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="203"/>
        <source>Saturation Range</source>
        <translation>Intervallo Saturazione</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="227"/>
        <source>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</source>
        <translation>Tolleranza inferiore dell&apos;intervallo di saturazione.
• Intervallo: da 0 a 255
• Predefinito: 50
Sottrae dal valore di saturazione obiettivo per definire il limite inferiore.
Valori più bassi = richiede colori vivaci, valori più alti = accetta colori sbiaditi/lavati.
Esempio: Saturazione obiettivo 150, meno 50 = rileva saturazioni da 100 a 150.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="262"/>
        <source>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</source>
        <translation>Tolleranza superiore dell&apos;intervallo di saturazione.
• Intervallo: da 0 a 255
• Predefinito: 50
Aggiunge al valore di saturazione obiettivo per definire il limite superiore.
Valori più bassi = richiede saturazione esatta, valori più alti = accetta colori più saturi.
Esempio: Saturazione obiettivo 150, più 50 = rileva saturazioni da 150 a 200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="298"/>
        <source>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</source>
        <translation>Tolleranza dell&apos;intervallo di valore (luminosità) per il rilevamento del colore.
Il valore rappresenta la luminosità (0=nero, 255=luminoso) su una scala 0-255.
Regola i valori -/+ per consentire variazioni nella luminosità.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="303"/>
        <source>Value Range</source>
        <translation>Intervallo Valore</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="327"/>
        <source>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</source>
        <translation>Tolleranza inferiore dell&apos;intervallo di valore (luminosità).
• Intervallo: da 0 a 255
• Predefinito: 50
Sottrae dal valore di luminosità obiettivo per definire il limite inferiore.
Valori più bassi = richiede pixel luminosi, valori più alti = accetta pixel più scuri.
Esempio: Valore obiettivo 200, meno 50 = rileva luminosità da 150 a 200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="362"/>
        <source>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</source>
        <translation>Tolleranza superiore dell&apos;intervallo di valore (luminosità).
• Intervallo: da 0 a 255
• Predefinito: 50
Aggiunge al valore di luminosità obiettivo per definire il limite superiore.
Valori più bassi = richiede luminosità esatta, valori più alti = accetta pixel più luminosi.
Esempio: Valore obiettivo 200, più 20 = rileva luminosità da 200 a 220.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="410"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation>Apre la finestra Visualizzatore Intervallo per:
- Vedere l&apos;intervallo di colori che verranno cercati nell&apos;analisi dell&apos;immagine.
Usa questo per vedere quali colori verranno rilevati e ottimizzare gli intervalli di colore prima dell&apos;elaborazione.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="415"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
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
        <translation>Assistente Intervallo Colore HSV - Selezione con Clic</translation>
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
        <translation>Visualizzatore immagini interattivo con selezione del colore.

NAVIGAZIONE:
• Rotella del mouse: zoom avanti/indietro
• Trascina con tasto sinistro: spostati nell&apos;immagine
• Doppio clic: adatta l&apos;immagine alla vista

SELEZIONE COLORE:
• CTRL + clic sinistro: seleziona colori simili
• CTRL+MAIUSC + clic sinistro: rimuove/cancella la selezione
• Tasti [ ]: regola il raggio di selezione
• CTRL+Z: annulla l&apos;ultima selezione
• CTRL+MAIUSC+Z: ripeti

VISUALIZZAZIONE:
• Overlay bianco = pixel selezionati
• Testo giallo = valori HSV nella posizione del cursore
• Il cursore circolare appare tenendo premuto CTRL</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="741"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="743"/>
        <source>Browse for an image file to load.
Opens a file dialog to select an image from your computer.
• Supported formats: PNG, JPG, JPEG, BMP
• Load an image to start selecting colors
The image will be displayed in the main viewer on the left.</source>
        <translation>Sfoglia per scegliere un file immagine da caricare.
Apre una finestra di dialogo per selezionare un&apos;immagine dal computer.
• Formati supportati: PNG, JPG, JPEG, BMP
• Carica un&apos;immagine per iniziare a selezionare i colori
L&apos;immagine verrà mostrata nel visualizzatore principale a sinistra.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="753"/>
        <source>Reset</source>
        <translation>Reimposta</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="755"/>
        <source>Reset all selections and start over.
• Clears all selected pixels (white overlay)
• Resets HSV ranges to defaults
• Clears the mask preview
• Undoable with CTRL+Z
Use this to start fresh without reloading the image.</source>
        <translation>Reimposta tutte le selezioni e ricomincia da capo.
• Cancella tutti i pixel selezionati (overlay bianco)
• Ripristina gli intervalli HSV ai valori predefiniti
• Cancella l&apos;anteprima della maschera
• Annullabile con CTRL+Z
Utile per ripartire da zero senza ricaricare l&apos;immagine.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="766"/>
        <source>Selection Radius:</source>
        <translation>Raggio di Selezione:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="768"/>
        <source>Size of the circular selection cursor.
Determines how many pixels are sampled when you CTRL+Click.</source>
        <translation>Dimensione del cursore circolare di selezione.
Determina quanti pixel vengono campionati con CTRL+Clic.</translation>
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
        <translation>Imposta il raggio del cursore di selezione in pixel.
• Intervallo: 1-50 pixel
• Predefinito: 1 pixel (selezione singolo pixel)
Raggio più grande:
• Campiona più pixel a ogni clic
• Calcola la media dei colori all&apos;interno del cerchio
• Adatto per selezionare gradienti o aree con texture
Raggio più piccolo:
• Selezione più precisa
• Migliore per colori uniformi
Scorciatoie da tastiera: [ diminuisce, ] aumenta di 2 pixel.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="793"/>
        <source>Color Tolerance:</source>
        <translation>Tolleranza Colore:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="795"/>
        <source>HSV color matching tolerance.
Controls how similar colors must be to get selected.</source>
        <translation>Tolleranza di corrispondenza dei colori HSV.
Controlla quanto i colori devono essere simili per essere selezionati.</translation>
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
        <translation>Imposta la tolleranza colore per il rilevamento dei pixel simili.
• Intervallo: 0-50
• Predefinito: 2
Quando usi CTRL+Clic, i pixel vengono selezionati se i loro valori HSV rientrano in questa tolleranza:
• 0: solo corrispondenza esatta (molto rigoroso)
• 2-5: piccole variazioni (consigliato nella maggior parte dei casi)
• 10+: variazioni ampie (può selezionare troppi colori)
Tolleranza più alta:
• Seleziona più colori simili
• Adatta a immagini con variazioni di luce
• Può includere colori indesiderati
Tolleranza più bassa:
• Corrispondenza colore più precisa
• Può non rilevare alcuni pixel del colore target.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="825"/>
        <source>CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius</source>
        <translation>CTRL+Clic: seleziona colori simili | CTRL+MAIUSC+Clic: rimuovi | [ ] : raggio</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="831"/>
        <source>Help</source>
        <translation>Aiuto</translation>
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
        <translation>Mostra una guida dettagliata e le istruzioni.
Apre una finestra di dialogo con:
• Istruzioni d&apos;uso passo-passo
• Spiegazione dei comandi di navigazione
• Tecniche di selezione del colore
• Riferimento alle scorciatoie da tastiera
Clicca qui se non sei sicuro di come usare questo strumento.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="859"/>
        <source>Selected Color</source>
        <translation>Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="861"/>
        <source>Average color of all selected pixels.
Shows the center/mean color that will be used for HSV range detection.</source>
        <translation>Colore medio di tutti i pixel selezionati.
Mostra il colore centrale/medio che verrà usato per il rilevamento dell&apos;intervallo HSV.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="866"/>
        <source>Color:</source>
        <translation>Colore:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="868"/>
        <source>Visual preview of the average selected color.
This is the center color calculated from all selected pixels.</source>
        <translation>Anteprima visiva del colore medio selezionato.
È il colore centrale calcolato da tutti i pixel selezionati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="876"/>
        <source>Color swatch showing the average of all selected pixels.
This becomes the center color for HSV range detection.</source>
        <translation>Campione che mostra la media di tutti i pixel selezionati.
Diventa il colore centrale per il rilevamento dell&apos;intervallo HSV.</translation>
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
        <translation>Rappresentazione esadecimale del colore selezionato.
Formato: #RRGGBB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="889"/>
        <source>Hex color code of the average selected color.
Can be used to identify the exact RGB color value.</source>
        <translation>Codice esadecimale del colore medio selezionato.
Può essere usato per identificare l&apos;esatto valore RGB.</translation>
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
        <translation>Valori HSV del colore selezionato.
H = Tonalità (0-360°), S = Saturazione (0-100%), V = Valore (0-100%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="902"/>
        <source>HSV color values of the average selected color.
This is the center point of your color range.</source>
        <translation>Valori di colore HSV del colore medio selezionato.
È il punto centrale del tuo intervallo cromatico.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="910"/>
        <source>HSV Ranges</source>
        <translation>Intervalli HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="912"/>
        <source>HSV color range configuration.
Defines the detection range for each HSV channel.
Center values are calculated from selected pixels.
Buffer values add extra tolerance to catch color variations.</source>
        <translation>Configurazione dell&apos;intervallo cromatico HSV.
Definisce l&apos;intervallo di rilevamento per ciascun canale HSV.
I valori centrali sono calcolati dai pixel selezionati.
I valori di buffer aggiungono tolleranza per catturare le variazioni cromatiche.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="920"/>
        <source>Channel</source>
        <translation>Canale</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="921"/>
        <source>HSV color channel (Hue, Saturation, Value)</source>
        <translation>Canale colore HSV (Tonalità, Saturazione, Valore)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="924"/>
        <source>Center</source>
        <translation>Centro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="925"/>
        <source>Average value of selected pixels for this channel</source>
        <translation>Valore medio dei pixel selezionati per questo canale</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="928"/>
        <source>- Buffer</source>
        <translation>- Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="929"/>
        <source>Extra tolerance below center value (lower bound buffer)</source>
        <translation>Tolleranza extra sotto il valore centrale (buffer del limite inferiore)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="932"/>
        <source>+ Buffer</source>
        <translation>+ Buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="933"/>
        <source>Extra tolerance above center value (upper bound buffer)</source>
        <translation>Tolleranza extra sopra il valore centrale (buffer del limite superiore)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="936"/>
        <source>Final Range</source>
        <translation>Intervallo Finale</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="937"/>
        <source>Complete detection range (min-max) after applying buffers</source>
        <translation>Intervallo di rilevamento completo (min-max) dopo l&apos;applicazione dei buffer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="941"/>
        <source>Hue:</source>
        <translation>Tonalità:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="942"/>
        <source>Hue channel (color type): 0-360 degrees on color wheel</source>
        <translation>Canale Tonalità (tipo di colore): 0-360 gradi sulla ruota dei colori</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="947"/>
        <source>Center hue value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-360° (red=0°, green=120°, blue=240°)</source>
        <translation>Valore di tonalità centrale (media dei pixel selezionati).
Calcolato automaticamente dalla tua selezione.
Intervallo: 0-360° (rosso=0°, verde=120°, blu=240°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="957"/>
        <source>Hue lower bound buffer (subtract from center).
• Range: 0-360°
• Adds tolerance below the center hue
• Larger values detect more hues in the minus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Buffer del limite inferiore di tonalità (sottratto dal centro).
• Intervallo: 0-360°
• Aggiunge tolleranza sotto la tonalità centrale
• Valori più alti rilevano più tonalità in direzione meno
• Mantieni stretto per evitare di rilevare colori indesiderati
AVVISO: un intervallo totale di tonalità (meno + più) &gt; 60° può causare falsi positivi</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="971"/>
        <source>Hue upper bound buffer (add to center).
• Range: 0-360°
• Adds tolerance above the center hue
• Larger values detect more hues in the plus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Buffer del limite superiore di tonalità (sommato al centro).
• Intervallo: 0-360°
• Aggiunge tolleranza sopra la tonalità centrale
• Valori più alti rilevano più tonalità in direzione più
• Mantieni stretto per evitare di rilevare colori indesiderati
AVVISO: un intervallo totale di tonalità (meno + più) &gt; 60° può causare falsi positivi</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="983"/>
        <source>Final hue detection range.
Shows the complete min-max hue range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Intervallo finale di rilevamento della tonalità.
Mostra l&apos;intervallo completo min-max di tonalità che verrà rilevato.
Calcolato come: (centro - buffer meno) fino a (centro + buffer più).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="990"/>
        <source>WARNING: Too wide of a Hue range can result in false positives!</source>
        <translation>AVVISO: un intervallo di Tonalità troppo ampio può causare falsi positivi!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="994"/>
        <source>Hue range warning.
Your total hue range exceeds 60°.
Wide hue ranges may detect many different colors.
Consider narrowing the buffers for more accurate detection.</source>
        <translation>Avviso intervallo di tonalità.
L&apos;intervallo di tonalità totale supera i 60°.
Intervalli di tonalità ampi possono rilevare molti colori diversi.
Considera di restringere i buffer per un rilevamento più accurato.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1002"/>
        <source>Sat:</source>
        <translation>Sat:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1003"/>
        <source>Saturation channel (color intensity): 0-100%</source>
        <translation>Canale Saturazione (intensità del colore): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1008"/>
        <source>Center saturation value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=gray, 100%=vivid color)</source>
        <translation>Valore centrale di saturazione (media dei pixel selezionati).
Calcolato automaticamente dalla tua selezione.
Intervallo: 0-100% (0%=grigio, 100%=colore vivido)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1018"/>
        <source>Saturation lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center saturation
• Larger values detect more desaturated/grayish colors
• Be careful: very low saturation includes gray colors
WARNING: Lower bound &lt; 25% may include unwanted gray/desaturated colors</source>
        <translation>Buffer del limite inferiore di saturazione (sottratto dal centro).
• Intervallo: 0-100%
• Aggiunge tolleranza sotto la saturazione centrale
• Valori più alti rilevano colori più desaturati/grigiastri
• Attenzione: una saturazione molto bassa include i colori grigi
AVVISO: un limite inferiore &lt; 25% può includere colori grigi/desaturati indesiderati</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1032"/>
        <source>Saturation upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center saturation
• Larger values detect more saturated/vivid colors
• Higher saturation generally safe to increase</source>
        <translation>Buffer del limite superiore di saturazione (sommato al centro).
• Intervallo: 0-100%
• Aggiunge tolleranza sopra la saturazione centrale
• Valori più alti rilevano colori più saturi/vividi
• Aumentare la saturazione superiore è in genere sicuro.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1043"/>
        <source>Final saturation detection range.
Shows the complete min-max saturation range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Intervallo finale di rilevamento della saturazione.
Mostra l&apos;intervallo completo min-max di saturazione che verrà rilevato.
Calcolato come: (centro - buffer meno) fino a (centro + buffer più).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1050"/>
        <source>WARNING: Too low of a Saturation level can result in false positives!</source>
        <translation>AVVISO: un livello di Saturazione troppo basso può causare falsi positivi!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1054"/>
        <source>Saturation range warning.
Your lower saturation bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unwanted gray or desaturated objects.</source>
        <translation>Avviso intervallo di saturazione.
Il limite inferiore di saturazione è inferiore al 25%.
Una saturazione bassa include colori grigiastri/sbiaditi.
Potrebbe rilevare oggetti grigi o desaturati indesiderati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1062"/>
        <source>Val:</source>
        <translation>Val:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1063"/>
        <source>Value channel (brightness): 0-100%</source>
        <translation>Canale Valore (luminosità): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1068"/>
        <source>Center value/brightness (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=black, 100%=bright)</source>
        <translation>Valore/luminosità centrale (media dei pixel selezionati).
Calcolato automaticamente dalla tua selezione.
Intervallo: 0-100% (0%=nero, 100%=luminoso)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1078"/>
        <source>Value lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center brightness
• Larger values detect darker versions of the color
• Be careful: very low value includes very dark/black colors
WARNING: Lower bound &lt; 25% may include unwanted shadows or dark objects</source>
        <translation>Buffer del limite inferiore del valore (sottratto dal centro).
• Intervallo: 0-100%
• Aggiunge tolleranza sotto la luminosità centrale
• Valori più alti rilevano versioni più scure del colore
• Attenzione: un valore molto basso include colori molto scuri/neri
AVVISO: un limite inferiore &lt; 25% può includere ombre o oggetti scuri indesiderati</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1092"/>
        <source>Value upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center brightness
• Larger values detect brighter versions of the color
• Higher brightness generally safe to increase</source>
        <translation>Buffer del limite superiore del valore (sommato al centro).
• Intervallo: 0-100%
• Aggiunge tolleranza sopra la luminosità centrale
• Valori più alti rilevano versioni più luminose del colore
• Aumentare la luminosità è in genere sicuro.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1103"/>
        <source>Final value/brightness detection range.
Shows the complete min-max brightness range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Intervallo finale di rilevamento del valore/luminosità.
Mostra l&apos;intervallo completo min-max di luminosità che verrà rilevato.
Calcolato come: (centro - buffer meno) fino a (centro + buffer più).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1110"/>
        <source>WARNING: Too low of a Value level can result in false positives!</source>
        <translation>AVVISO: un livello di Valore troppo basso può causare falsi positivi!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1114"/>
        <source>Value range warning.
Your lower value bound is below 25%.
Low value includes very dark colors.
May detect unwanted shadows or dark objects.</source>
        <translation>Avviso intervallo del valore.
Il limite inferiore del valore è inferiore al 25%.
Un valore basso include colori molto scuri.
Potrebbe rilevare ombre o oggetti scuri indesiderati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1124"/>
        <source>Statistics</source>
        <translation>Statistiche</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1126"/>
        <source>Statistics about your current selection.
Shows how many pixels are selected and what percentage of the image they represent.</source>
        <translation>Statistiche sulla selezione corrente.
Mostra quanti pixel sono selezionati e quale percentuale dell&apos;immagine rappresentano.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1130"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1225"/>
        <source>Selected Pixels: 0</source>
        <translation>Pixel Selezionati: 0</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1132"/>
        <source>Number of pixels currently selected.
Shows the total count of white-highlighted pixels in the main viewer.
Updates in real-time as you select colors.</source>
        <translation>Numero di pixel attualmente selezionati.
Mostra il conteggio totale dei pixel evidenziati in bianco nel visualizzatore principale.
Si aggiorna in tempo reale mentre selezioni i colori.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1137"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1226"/>
        <source>Coverage: 0%</source>
        <translation>Copertura: 0%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1139"/>
        <source>Percentage of image covered by selection.
Shows what portion of the total image is selected.
• Low %: Precise selection, may miss some target pixels
• High %: Broad selection, may include unwanted areas</source>
        <translation>Percentuale di immagine coperta dalla selezione.
Mostra quale porzione dell&apos;immagine totale è selezionata.
• Percentuale bassa: selezione precisa, potrebbe perdere alcuni pixel target
• Percentuale alta: selezione ampia, potrebbe includere aree indesiderate</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1148"/>
        <source>Mask Preview</source>
        <translation>Anteprima Maschera</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1150"/>
        <source>Black and white preview of the detection mask.
Shows what pixels will be detected with current HSV ranges and buffers.</source>
        <translation>Anteprima in bianco e nero della maschera di rilevamento.
Mostra quali pixel verranno rilevati con gli attuali intervalli HSV e buffer.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1161"/>
        <source>Grayscale mask preview.
• White pixels: Will be detected with current settings
• Black pixels: Will NOT be detected
Updates automatically when you adjust buffers.
Use this to verify your HSV range captures the target without false positives.</source>
        <translation>Anteprima della maschera in scala di grigi.
• Pixel bianchi: verranno rilevati con le impostazioni correnti
• Pixel neri: NON verranno rilevati
Si aggiorna automaticamente quando regoli i buffer.
Usala per verificare che il tuo intervallo HSV catturi il target senza falsi positivi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1179"/>
        <source>Select Image</source>
        <translation>Seleziona Immagine</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1180"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp)</source>
        <translation>Immagini (*.png *.jpg *.jpeg *.bmp)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1237"/>
        <source>Selected Pixels: {0:,}</source>
        <translation>Pixel Selezionati: {0:,}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1238"/>
        <source>Coverage: {0:.1f}%</source>
        <translation>Copertura: {0:.1f}%</translation>
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
&lt;h2&gt;Assistente Intervallo Colore HSV - Aiuto&lt;/h2&gt;

&lt;p&gt;Questo strumento ti aiuta a scegliere l&apos;intervallo di colori HSV di un colore specifico in una foto.
Clicca sul pulsante SFOGLIA per aprire un&apos;immagine.&lt;/p&gt;

&lt;h3&gt;Navigazione:&lt;/h3&gt;
&lt;p&gt;• Usa la rotellina del mouse per ingrandire/rimpicciolire l&apos;immagine&lt;br&gt;
• Usa il tasto sinistro del mouse per trascinare l&apos;immagine e spostarla&lt;/p&gt;

&lt;h3&gt;Selezione Colore:&lt;/h3&gt;
&lt;p&gt;• Tieni premuto il tasto &lt;b&gt;CTRL/OPTION&lt;/b&gt; mentre fai clic con il tasto sinistro su un colore nell&apos;immagine che desideri selezionare&lt;br&gt;
• Tutti i pixel nell&apos;immagine che condividono quel valore di colore HSV verranno selezionati ed evidenziati in bianco&lt;/p&gt;

&lt;h3&gt;Raggio di Selezione:&lt;/h3&gt;
        &lt;p&gt;Puoi regolare il Raggio di Selezione del cursore del mouse per renderlo più grande o più piccolo.
        Quando fai clic con CTRL, verranno selezionati tutti i colori entro quel raggio dal cursore del mouse.&lt;/p&gt;

&lt;h3&gt;Correzioni:&lt;/h3&gt;
&lt;p&gt;Se commetti un errore, puoi ANNULLARE l&apos;ultima selezione o premere il pulsante RIPRISTINA per ricominciare.&lt;/p&gt;

&lt;h3&gt;Anteprima Maschera:&lt;/h3&gt;
        &lt;p&gt;Sul lato destro, la sezione Anteprima Maschera ti mostrerà quali pixel nell&apos;immagine sono stati selezionati.
        Se vedi pixel al di fuori del tuo oggetto target che stai selezionando, significa che potresti dover
        regolare la Tolleranza Colore o essere più attento con le tue selezioni.&lt;/p&gt;
</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1504"/>
        <source>HSV Color Range Assistant - Help</source>
        <translation>Assistente Intervallo Colore HSV - Aiuto</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="97"/>
        <source>No Colors Selected</source>
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="120"/>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="125"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="176"/>
        <source>Hue Expansion</source>
        <translation>Espansione per Tonalità</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="178"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Se abilitato, espande ogni AOI attraverso i pixel adiacenti la cui tonalità rientra in ± {0}
(unità OpenCV) rispetto alla tonalità media dei pixel originali rilevati.
I pixel con saturazione inferiore al {1}% o valore inferiore al {2}% vengono esclusi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="468"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="53"/>
        <source>No Colors Selected</source>
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="63"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="99"/>
        <source>Hue Expansion</source>
        <translation>Espansione per Tonalità</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="101"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Se abilitato, espande ogni AOI attraverso i pixel adiacenti la cui tonalità rientra in ± {0}
(unità OpenCV) rispetto alla tonalità media dei pixel originali rilevati.
I pixel con saturazione inferiore al {1}% o valore inferiore al {2}% vengono esclusi.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="408"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
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
        <translation>Tolleranza
Corrispondenza:</translation>
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
        <translation>Inserimento codice colore esadecimale.
Inserisci i colori come codici esadecimali (es. #FF0000 per il rosso).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="102"/>
        <source>Enter a hexadecimal color code.
• Format: #RRGGBB (e.g., #FF0000 for red, #00FF00 for green)
• Also accepts short format: #RGB (e.g., #F00 for red)
Type or paste a hex code to quickly set a specific color.
The color will be converted to HSV automatically.</source>
        <translation>Inserisci un codice colore esadecimale.
• Formato: #RRGGBB (es. #FF0000 per il rosso, #00FF00 per il verde)
• Accetta anche il formato breve: #RGB (es. #F00 per il rosso)
Digita o incolla un codice esadecimale per impostare rapidamente un colore specifico.
Il colore verrà convertito automaticamente in HSV.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="111"/>
        <source>Reset to Default</source>
        <translation>Ripristina Predefiniti</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="114"/>
        <source>Reset to default color and ranges.
• Color: Pure red (H:0°, S:100%, V:100%)
• Hue range: ±20° (total 40° range)
• Saturation range: ±20%
• Value range: ±20%
Use this to start over with standard settings.</source>
        <translation>Ripristina colore e intervalli predefiniti.
• Colore: rosso puro (H:0°, S:100%, V:100%)
• Intervallo tonalità: ±20° (totale 40°)
• Intervallo saturazione: ±20%
• Intervallo valore: ±20%
Usalo per ripartire dalle impostazioni standard.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="137"/>
        <source>Saturation / Value</source>
        <translation>Saturazione / Valore</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="141"/>
        <source>Saturation and Value (brightness) selector.
Saturation controls color intensity (left=gray, right=vivid).
Value controls brightness (bottom=dark, top=bright).</source>
        <translation>Selettore di Saturazione e Valore (luminosità).
La Saturazione controlla l&apos;intensità del colore (sinistra=grigio, destra=vivido).
Il Valore controlla la luminosità (basso=scuro, alto=luminoso).</translation>
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
        <translation>Selettore interattivo Saturazione/Valore.
• Clicca in qualsiasi punto per impostare saturazione e luminosità del colore centrale
• Cerchio bianco = posizione attuale del colore centrale
• Rettangolo bianco = intervallo di rilevamento (regolabile)
• Trascina le maniglie bianche agli angoli per regolare gli intervalli di saturazione/valore
• Intervallo orizzontale = tolleranza di saturazione
• Intervallo verticale = tolleranza di valore/luminosità
Intervalli più ampi rilevano più variazioni di colore ma possono includere colori indesiderati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="165"/>
        <source>Hue</source>
        <translation>Tonalità</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="169"/>
        <source>Hue (color type) selector.
Hue represents the actual color: red, orange, yellow, green, cyan, blue, purple, magenta.</source>
        <translation>Selettore di Tonalità (tipo di colore).
La Tonalità rappresenta il colore effettivo: rosso, arancione, giallo, verde, ciano, blu, viola, magenta.</translation>
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
        <translation>Selettore interattivo ad anello della Tonalità.
• Clicca sull&apos;anello per selezionare una tonalità (tipo di colore)
• Linea bianca = tonalità centrale attuale
• Archi e linee grigie = intervallo di rilevamento della tonalità (regolabile)
• Trascina le maniglie circolari bianche per regolare l&apos;intervallo di tonalità
• Maniglia sinistra = limite inferiore (intervallo meno)
• Maniglia destra = limite superiore (intervallo più)
Avviso: intervalli di tonalità superiori a 60° possono rilevare troppi colori.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="205"/>
        <source>Use Image</source>
        <translation>Usa Immagine</translation>
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
        <translation>Apri l&apos;Assistente Intervallo Colore HSV.
Strumento avanzato per selezionare colori da un&apos;immagine:
• Carica un&apos;immagine dalla tua cartella di input
• Clicca sui pixel per campionare i colori
• Calcola automaticamente gli intervalli HSV ottimali
• Visualizza un&apos;anteprima in tempo reale dei risultati di rilevamento
Consigliato per trovare l&apos;intervallo cromatico migliore per il tuo target.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="219"/>
        <source>Pick Screen Color</source>
        <translation>Preleva Colore dallo Schermo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="222"/>
        <source>Pick a color from anywhere on your screen.
Opens a color picker that lets you:
• Click anywhere on your screen to sample a color
• Sample from other applications or images
The picked color will be set as the center color.
Ranges remain unchanged - adjust manually after picking.</source>
        <translation>Preleva un colore da qualsiasi punto dello schermo.
Apre un selettore di colore che ti consente di:
• Cliccare ovunque sullo schermo per campionare un colore
• Campionare da altre applicazioni o immagini
Il colore prelevato verrà impostato come colore centrale.
Gli intervalli restano invariati: regolali manualmente dopo il prelievo.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="232"/>
        <source>Add to Custom Colors</source>
        <translation>Aggiungi ai Colori Personalizzati</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="235"/>
        <source>Save current color to Custom Colors palette.
Adds the current center color to the first empty slot in Custom Colors.
• Only saves the color, not the ranges
• Click saved colors to quickly reuse them
• Custom colors persist across sessions
Useful for building a palette of frequently used colors.</source>
        <translation>Salva il colore corrente nella tavolozza dei Colori Personalizzati.
Aggiunge il colore centrale corrente al primo slot libero in Colori Personalizzati.
• Salva solo il colore, non gli intervalli
• Clicca sui colori salvati per riutilizzarli rapidamente
• I colori personalizzati vengono mantenuti tra le sessioni
Utile per costruire una tavolozza dei colori usati di frequente.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="253"/>
        <source>Basic Colors:</source>
        <translation>Colori di Base:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="256"/>
        <source>Preset basic color palette.
Quick access to common colors like red, orange, yellow, green, cyan, blue, purple, and grayscale.
Click any color swatch to set it as the center color.</source>
        <translation>Tavolozza di colori di base predefiniti.
Accesso rapido ai colori comuni come rosso, arancione, giallo, verde, ciano, blu, viola e scala di grigi.
Clicca su un campione di colore per impostarlo come colore centrale.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="264"/>
        <source>Basic color swatches.
Click any color to quickly set it as your center color.
• Top row: Primary colors and tints
• Bottom row: Grayscale and darker shades
Useful for quickly selecting standard colors.</source>
        <translation>Campioni di colori di base.
Clicca su un colore per impostarlo rapidamente come colore centrale.
• Riga superiore: colori primari e tinte
• Riga inferiore: scala di grigi e tonalità più scure
Utile per selezionare velocemente i colori standard.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="274"/>
        <source>Custom Colors:</source>
        <translation>Colori Personalizzati:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="277"/>
        <source>Your saved custom color palette.
Colors you&apos;ve saved using &apos;Add to Custom Colors&apos; button.
Click any saved color to reuse it.</source>
        <translation>La tua tavolozza di colori personalizzati salvati.
Colori che hai salvato con il pulsante &quot;Aggiungi ai Colori Personalizzati&quot;.
Clicca su un colore salvato per riutilizzarlo.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="285"/>
        <source>Custom color swatches.
Click any color to set it as your center color.
• Empty slots shown as gray
• Use &apos;Add to Custom Colors&apos; button to save current color
• Custom colors persist across sessions
Build your own palette of frequently used colors.</source>
        <translation>Campioni di colori personalizzati.
Clicca su un colore per impostarlo come colore centrale.
• Gli slot vuoti sono mostrati in grigio
• Usa il pulsante &quot;Aggiungi ai Colori Personalizzati&quot; per salvare il colore corrente
• I colori personalizzati vengono mantenuti tra le sessioni
Costruisci la tua tavolozza di colori usati di frequente.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="461"/>
        <source>Current HSV color range summary.
Shows the center color and detection ranges in real-time.
Warning indicators appear when ranges may cause detection issues.</source>
        <translation>Riepilogo dell&apos;intervallo colore HSV corrente.
Mostra in tempo reale il colore centrale e gli intervalli di rilevamento.
Gli indicatori di avviso compaiono quando gli intervalli possono causare problemi di rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Center HSV:</source>
        <translation>HSV Centro:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Hue Range:</source>
        <translation>Intervallo Tonalità:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Sat Range:</source>
        <translation>Intervallo Sat:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Val Range:</source>
        <translation>Intervallo Val:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="472"/>
        <source>Current center HSV color values.
H = Hue (0-360°), S = Saturation (0-100%), V = Value/brightness (0-100%).</source>
        <translation>Valori HSV correnti del colore centrale.
H = Tonalità (0-360°), S = Saturazione (0-100%), V = Valore/luminosità (0-100%).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="473"/>
        <source>Hue detection range (minus/plus from center).
Total range = minus + plus. Warning shown if total &gt; 60°.</source>
        <translation>Intervallo di rilevamento tonalità (meno/più dal centro).
Intervallo totale = meno + più. L&apos;avviso appare se il totale &gt; 60°.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="474"/>
        <source>Saturation detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Intervallo di rilevamento saturazione (meno/più dal centro).
L&apos;avviso appare se il limite inferiore &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="475"/>
        <source>Value detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Intervallo di rilevamento valore (meno/più dal centro).
L&apos;avviso appare se il limite inferiore &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="497"/>
        <source>⚠ Too wide!</source>
        <translation>⚠ Troppo ampio!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="502"/>
        <source>Hue range warning.
Your hue range is wider than 60° total.
Wide hue ranges may detect too many different colors.
Consider narrowing the range for more accurate detection.</source>
        <translation>Avviso intervallo di tonalità.
Il tuo intervallo di tonalità totale è superiore a 60°.
Intervalli di tonalità ampi possono rilevare troppi colori diversi.
Considera di restringere l&apos;intervallo per un rilevamento più accurato.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="510"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="523"/>
        <source>⚠ Too low!</source>
        <translation>⚠ Troppo basso!</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="515"/>
        <source>Saturation range warning.
Your saturation lower bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unintended gray or desaturated colors.</source>
        <translation>Avviso intervallo di saturazione.
Il tuo limite inferiore di saturazione è inferiore al 25%.
Una saturazione bassa include colori grigiastri/sbiaditi.
Potrebbe rilevare colori grigi o desaturati indesiderati.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="528"/>
        <source>Value range warning.
Your value lower bound is below 25%.
Low value includes very dark colors.
May detect shadows or dark unintended objects.</source>
        <translation>Avviso intervallo del valore.
Il tuo limite inferiore del valore è inferiore al 25%.
Un valore basso include colori molto scuri.
Potrebbe rilevare ombre o oggetti scuri indesiderati.</translation>
    </message>
</context>
<context>
    <name>HeatmapViewerDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="34"/>
        <source>AOI Detection Heatmap</source>
        <translation>Heatmap dei Rilevamenti AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="59"/>
        <source>Threshold</source>
        <translation>Soglia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="62"/>
        <source>Percentile:</source>
        <translation>Percentile:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="81"/>
        <source>Grid Resolution</source>
        <translation>Risoluzione Griglia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="86"/>
        <source>Low (100)</source>
        <translation>Bassa (100)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="87"/>
        <source>Medium (200)</source>
        <translation>Media (200)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="88"/>
        <source>High (400)</source>
        <translation>Alta (400)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="114"/>
        <source>Hot zones (colored) show high-density detection areas. Gray zones are below the threshold. Adjust the threshold to control what counts as a hot zone.</source>
        <translation>Le zone calde (colorate) mostrano aree con alta densità di rilevamenti. Le zone grigie sono sotto la soglia. Regola la soglia per controllare cosa viene considerato una zona calda.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="126"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="150"/>
        <source>No heatmap data available</source>
        <translation>Nessun dato heatmap disponibile</translation>
    </message>
</context>
<context>
    <name>HelpDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="25"/>
        <source>Viewer Help</source>
        <translation>Aiuto Visualizzatore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="60"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
</context>
<context>
    <name>ImageAdjustmentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="83"/>
        <source>Image Adjustment</source>
        <translation>Regolazione Immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="96"/>
        <source>Adjustments</source>
        <translation>Regolazioni</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="124"/>
        <source>Exposure:</source>
        <translation>Esposizione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="127"/>
        <source>Highlights:</source>
        <translation>Luci:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="130"/>
        <source>Shadows:</source>
        <translation>Ombre:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="133"/>
        <source>Clarity:</source>
        <translation>Chiarezza:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="136"/>
        <source>Radius:</source>
        <translation>Raggio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="146"/>
        <source>Reset</source>
        <translation>Ripristina</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="147"/>
        <source>Apply</source>
        <translation>Applica</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="148"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
</context>
<context>
    <name>ImageAnalysisGuide</name>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="14"/>
        <source>Image Analysis Guide</source>
        <translation>Guida all&apos;Analisi delle Immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="39"/>
        <source>Welcome to ADIAT</source>
        <translation>Benvenuto in ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="67"/>
        <source>Select a results file from a previous analysis: an ADIAT_Data.xml result, or a batch&apos;s Search Coordinator project (ADIAT_Search_*.xml).</source>
        <translation>Seleziona un file di risultati da un&apos;analisi precedente: un risultato ADIAT_Data.xml oppure un progetto di revisione multi-batch del Coordinatore di Ricerca (ADIAT_Search_*.xml).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="79"/>
        <source>No file selected</source>
        <translation>Nessun file selezionato</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="94"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="266"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="307"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="123"/>
        <source>What would you like to do?</source>
        <translation>Cosa vorresti fare?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="160"/>
        <source>Start New Image Analysis</source>
        <translation>Inizia Nuova Analisi Immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="178"/>
        <source>Review Existing Image Analysis</source>
        <translation>Rivedi Analisi Immagini Esistente</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="223"/>
        <source>Select Directories</source>
        <translation>Seleziona Cartelle</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="245"/>
        <source>Where are the images you want to analyze?</source>
        <translation>Dove sono le immagini che vuoi analizzare?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="286"/>
        <source>Where do you want ADIAT to store the output files?</source>
        <translation>Dove vuoi che ADIAT memorizzi i file di output?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="348"/>
        <source>Image Capture Information</source>
        <translation>Informazioni Acquisizione Immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="370"/>
        <source>What drone/camera was used to capture images?</source>
        <translation>Quale drone/telecamera è stata utilizzata per acquisire le immagini?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="400"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>A quale altitudine dal livello del suolo (AGL) volava il drone?</translation>
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
        <translation>Distanza di campionamento al suolo (GSD) stimata:</translation>
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
        <translation>Dimensione target di ricerca</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="590"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Quanto sono approssimativamente grandi gli oggetti che vuoi identificare?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="621"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Altri esempi:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 ft² – Cappello, Casco, Sacchetto di plastica &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 ft² – Gatto, Zaino da giorno &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 ft² – Zaino grande, Cane medio &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 ft² – Sacco a pelo, Cane grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 ft² – Barca piccola, Tenda da 2 persone &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 ft² – Auto/SUV, Pickup piccolo, Tenda grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 ft² – Casa &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="660"/>
        <source>ALGORITHM SELECTION GUIDE</source>
        <translation>GUIDA ALLA SELEZIONE DELL&apos;ALGORITMO</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="682"/>
        <source>Are you using thermal images?</source>
        <translation>Stai usando immagini termiche?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="727"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1114"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="758"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1099"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="831"/>
        <source>Reset</source>
        <translation>Reimposta</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="147"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="888"/>
        <source>Algorithm Parameters</source>
        <translation>Parametri Algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="918"/>
        <source>General Settings</source>
        <translation>Impostazioni Generali</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="940"/>
        <source>What color should be used to highlight Areas of Interest (AOIs)?</source>
        <translation>Quale colore dovrebbe essere usato per evidenziare le Aree di Interesse (AOI)?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="960"/>
        <source>Select Color</source>
        <translation>Seleziona Colore</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1009"/>
        <source>How many images should be processed at the same time?</source>
        <translation>Quante immagini devono essere elaborate contemporaneamente?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1033"/>
        <source>Run Benchmark</source>
        <translation>Esegui Benchmark</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1056"/>
        <source>What resolution should images be processed at?</source>
        <translation>A quale risoluzione devono essere elaborate le immagini?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1084"/>
        <source>Were the images captured in different lighting conditions?</source>
        <translation>Le immagini sono state acquisite in condizioni di illuminazione diverse?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1177"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1189"/>
        <source>Skip this wizard in the future</source>
        <translation>Salta questa procedura guidata in futuro</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1217"/>
        <source>Back</source>
        <translation>Indietro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="261"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="266"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="272"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1229"/>
        <source>Continue</source>
        <translation>Continua</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="102"/>
        <source>ADIAT Image Analysis Guide</source>
        <translation>Guida all&apos;analisi immagini ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="256"/>
        <source>Load Results</source>
        <translation>Carica Risultati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="269"/>
        <source>Start Processing</source>
        <translation>Avvia Elaborazione</translation>
    </message>
</context>
<context>
    <name>ImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="78"/>
        <source>Select Drone/Camera</source>
        <translation>Seleziona Drone/Fotocamera</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="82"/>
        <source>No drones available</source>
        <translation>Nessun drone disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="126"/>
        <source>Other</source>
        <translation>Altro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="162"/>
        <source>Error loading drone data</source>
        <translation>Errore nel caricamento dei dati del drone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="240"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Dati fotocamera non validi)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="473"/>
        <source>{sensor_name}: Focal length not found in image EXIF</source>
        <translation>{sensor_name}: lunghezza focale non trovata nei metadati EXIF dell&apos;immagine</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="475"/>
        <source>{sensor_name}: Select input directory to extract focal length from images</source>
        <translation>{sensor_name}: seleziona la cartella di input per estrarre la lunghezza focale dalle immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="482"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Dati fotocamera mancanti)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="483"/>
        <source>Unable to calculate GSD. Sensor dimensions found, but:</source>
        <translation>Impossibile calcolare il GSD. Dimensioni del sensore trovate, ma:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="484"/>
        <source>• Focal length is required (available from image EXIF data)</source>
        <translation>• È richiesta la lunghezza focale (disponibile nei metadati EXIF delle immagini)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="485"/>
        <source>GSD calculation requires an actual image file to extract focal length.</source>
        <translation>Il calcolo del GSD richiede un file immagine reale da cui estrarre la lunghezza focale.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="491"/>
        <source>-- (Error)</source>
        <translation>-- (Errore)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="523"/>
        <source>Sensor {n}</source>
        <translation>Sensore {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="525"/>
        <source>Primary</source>
        <translation>Principale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="527"/>
        <source>Sensor</source>
        <translation>Sensore</translation>
    </message>
</context>
<context>
    <name>ImageLoadController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="118"/>
        <source>(Image {current} of {total})</source>
        <translation>(Immagine {current} di {total})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="447"/>
        <source>Error Loading Image</source>
        <translation>Errore durante il caricamento dell&apos;immagine</translation>
    </message>
</context>
<context>
    <name>InputProcessingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="31"/>
        <source>Processing Resolution</source>
        <translation>Risoluzione di Elaborazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="36"/>
        <source>Resolution:</source>
        <translation>Risoluzione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="41"/>
        <source>Original</source>
        <translation>Originale</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="52"/>
        <source>Custom</source>
        <translation>Personalizzata</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="61"/>
        <source>Select a preset resolution for processing. Lower resolutions are faster but less detailed.
&apos;Original&apos; uses the video&apos;s native resolution (no downsampling).
720P (1280x720) provides excellent balance between speed and detection accuracy.
Select &apos;Custom&apos; to manually set width and height.</source>
        <translation>Seleziona una risoluzione predefinita per l&apos;elaborazione. Risoluzioni più basse sono più veloci ma meno dettagliate.
&quot;Originale&quot; usa la risoluzione nativa del video (nessun sottocampionamento).
720P (1280x720) offre un ottimo equilibrio tra velocità e precisione di rilevamento.
Seleziona &quot;Personalizzata&quot; per impostare manualmente larghezza e altezza.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="71"/>
        <source>Width:</source>
        <translation>Larghezza:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="78"/>
        <source>Custom processing width in pixels (320-3840).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Larghezza di elaborazione personalizzata in pixel (320-3840).
Abilitata solo quando è selezionata la risoluzione &quot;Personalizzata&quot;.
Valori più bassi = elaborazione più rapida, meno dettaglio.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="84"/>
        <source>Height:</source>
        <translation>Altezza:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="91"/>
        <source>Custom processing height in pixels (240-2160).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Altezza di elaborazione personalizzata in pixel (240-2160).
Abilitata solo quando è selezionata la risoluzione &quot;Personalizzata&quot;.
Valori più bassi = elaborazione più rapida, meno dettaglio.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="107"/>
        <source>Performance Options</source>
        <translation>Opzioni Prestazioni</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="112"/>
        <source>Frame Rate:</source>
        <translation>Frame Rate:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="118"/>
        <source>Source FPS</source>
        <translation>FPS della Sorgente</translation>
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
        <translation>Limita il frame rate dell&apos;elaborazione.

• FPS della Sorgente – segue la cadenza della sorgente (le sorgenti live possono applicare un limite di sicurezza)
• 30 FPS – buon equilibrio tra fluidità e prestazioni
• 25 FPS – standard per video PAL
• 20 FPS – uso CPU ridotto
• 15 FPS – uso CPU più basso
• 10 FPS – risparmio CPU significativo
• 5 FPS – massimo risparmio CPU, può perdere oggetti veloci

Frame rate più bassi riducono l&apos;uso della CPU ma possono perdere oggetti in rapido movimento.
I rilevamenti persistono tra i frame saltati per garantire continuità visiva.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="148"/>
        <source>Render at Processing Resolution (faster for high-res)</source>
        <translation>Renderizza alla Risoluzione di Elaborazione (più veloce per alte risoluzioni)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="151"/>
        <source>Renders detection overlays at processing resolution instead of original video resolution.
Significantly faster for high-resolution videos (1080p+) with minimal visual impact.
Example: Processing at 720p but video is 4K - renders at 720p then upscales.
Recommended: ON for high-res videos, OFF for native 720p or lower.</source>
        <translation>Disegna gli overlay dei rilevamenti alla risoluzione di elaborazione anziché a quella originale del video.
Molto più rapido per video ad alta risoluzione (1080p+) con impatto visivo minimo.
Esempio: elaborazione a 720p ma video in 4K – il rendering avviene a 720p e poi viene scalato.
Consigliato: ON per video ad alta risoluzione, OFF per 720p nativo o inferiore.</translation>
    </message>
</context>
<context>
    <name>LoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="12"/>
        <source>Generating Report</source>
        <translation>Generazione report</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="29"/>
        <source>Report generation in progress...</source>
        <translation>Generazione del report in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="33"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>MRMap</name>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
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
        <translation>Numero di segmenti in cui dividere ogni immagine per l&apos;analisi MR Map.
Ogni segmento viene elaborato indipendentemente per il rilevamento di caratteristiche multi-risoluzione.
Impatto sulle prestazioni:
• Numero di segmenti più alto: AUMENTA il tempo di elaborazione (più segmenti da analizzare)
• Numero di segmenti più basso: DIMINUISCE il tempo di elaborazione (meno segmenti da analizzare)
• 1 segmento: elaborazione più veloce (analizza l&apos;immagine intera una sola volta)
Un numero più alto di segmenti migliora il rilevamento in immagini con caratteristiche variabili.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Segmenti Immagine:</translation>
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
        <translation>Seleziona il numero di segmenti in cui dividere ogni immagine.
• Opzioni: 1, 2, 4, 6, 9, 16, 25, 36 segmenti
• Predefinito: 1 (analizza l&apos;immagine intera come un singolo segmento)
L&apos;algoritmo MR Map (Multi-Resolution Map) analizza le caratteristiche a più scale:
• 1 segmento: elabora l&apos;immagine intera (ideale per immagini piccole o contenuto uniforme)
• Più segmenti: analizza regioni locali in modo indipendente (meglio per immagini grandi)
Un numero più alto di segmenti migliora il rilevamento in immagini con caratteristiche variabili nella scena.
Consigliato: 4-9 segmenti per immagini tipiche da drone.</translation>
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
        <translation>Spazio colore:</translation>
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
        <translation>Seleziona lo spazio colore per l&apos;analisi MR Map.
L&apos;algoritmo MR Map analizza le caratteristiche in diverse rappresentazioni del colore:
• LAB: spazio colore percettivamente uniforme (predefinito, migliore per l&apos;analisi delle differenze di colore)
• RGB: spazio colore standard rosso-verde-blu (buono per uso generale)
• HSV: spazio colore Tonalità-Saturazione-Valore (migliore per il rilevamento di caratteristiche basate sul colore)
Spazi colore diversi possono migliorare il rilevamento a seconda del contenuto dell&apos;immagine.
Consigliato: LAB per la maggior parte dei casi, HSV per immagini ricche di colore.</translation>
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
        <translation>Dimensione della finestra per l&apos;analisi multi-risoluzione.
Determina la scala spaziale delle caratteristiche da rilevare.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="202"/>
        <source>Window Size:</source>
        <translation>Dimensione Finestra:</translation>
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
        <translation>Imposta la dimensione della finestra per l&apos;analisi multi-risoluzione.
• Intervallo: da 1 a 10
• Predefinito: 5
L&apos;algoritmo MR Map analizza le caratteristiche a più scale spaziali usando finestre scorrevoli:
• Valori più piccoli (1-3): rilevano dettagli fini e caratteristiche piccole
• Valori medi (4-6): rilevamento bilanciato (consigliato per la maggior parte dei casi)
• Valori più grandi (7-10): rilevano caratteristiche e pattern più grandi
La dimensione della finestra influisce sulla risoluzione spaziale del rilevamento delle caratteristiche.
Finestre più grandi forniscono più contesto ma possono perdere oggetti piccoli.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="254"/>
        <source>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</source>
        <translation>Soglia di rilevamento per il rilevamento delle caratteristiche MR Map.
Controlla la sensibilità del rilevamento delle caratteristiche su più risoluzioni.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="258"/>
        <source>Threshold:</source>
        <translation>Soglia:</translation>
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
        <translation>Regola la soglia di rilevamento per l&apos;algoritmo MR Map.
• Intervallo: da 1 a 200
• Predefinito: 100
• Il cursore è invertito: SINISTRA = soglia più alta, DESTRA = soglia più bassa
L&apos;algoritmo MR Map rileva le caratteristiche a più risoluzioni spaziali:
• Valori più bassi (1-50): molto sensibile, rileva molte caratteristiche (può includere rumore)
• Valori medi (51-150): rilevamento bilanciato (consigliato per la maggior parte dei casi)
• Valori più alti (151-200): meno sensibile, rileva solo caratteristiche evidenti
La soglia controlla quanto una caratteristica deve essere distinta per essere rilevata.
Nota: l&apos;aspetto del cursore è invertito - sposta a sinistra per più rigoroso, a destra per più permissivo.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="326"/>
        <source>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</source>
        <translation>Valore soglia corrente per il rilevamento delle caratteristiche MR Map.
Visualizza il valore selezionato sul cursore della soglia (1-200).
Valori più bassi = rilevamento più sensibile.</translation>
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
        <translation>Espansione Rilevamento (opzionale)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="48"/>
        <source>Threshold Expansion</source>
        <translation>Espansione per Soglia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="50"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Se abilitato, espande ogni AOI includendo anche i pixel con conteggi nei bin dell&apos;istogramma
inferiori a (soglia + {0}). I pixel all&apos;interno del rettangolo del cluster vengono aggiunti senza condizioni;
quelli esterni vengono aggiunti se collegati tramite altri pixel idonei.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="57"/>
        <source>Hue Expansion</source>
        <translation>Espansione per Tonalità</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="59"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Se abilitato, espande ogni AOI attraverso i pixel adiacenti la cui tonalità rientra in ± {0}
(unità OpenCV) rispetto alla tonalità media dei pixel originali rilevati.
I pixel con saturazione inferiore al {1}% o valore inferiore al {2}% vengono esclusi.</translation>
    </message>
</context>
<context>
    <name>MRMapWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="21"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>Le tue immagini contengono scene complesse con edifici, veicoli o coperture del terreno artificiali miste?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="41"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="56"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="92"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Quanto aggressivamente dovrebbe ADIAT cercare le anomalie?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="105"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta troverà più potenziali anomalie ma potrebbe anche aumentare i falsi positivi.</translation>
    </message>
</context>
<context>
    <name>MRMapWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="39"/>
        <source>Very 
Conservative</source>
        <translation>Molto 
Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="40"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="41"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="42"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="43"/>
        <source>Very 
Aggressive</source>
        <translation>Molto 
Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="60"/>
        <source>Detection Expansion (optional)</source>
        <translation>Espansione Rilevamento (opzionale)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="67"/>
        <source>Threshold Expansion</source>
        <translation>Espansione per Soglia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="69"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Se abilitato, espande ogni AOI includendo anche i pixel con conteggi nei bin dell&apos;istogramma
inferiori a (soglia + {0}). I pixel all&apos;interno del rettangolo del cluster vengono aggiunti senza condizioni;
quelli esterni vengono aggiunti se collegati tramite altri pixel idonei.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="76"/>
        <source>Hue Expansion</source>
        <translation>Espansione per Tonalità</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="78"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Se abilitato, espande ogni AOI attraverso i pixel adiacenti la cui tonalità rientra in ± {0}
(unità OpenCV) rispetto alla tonalità media dei pixel originali rilevati.
I pixel con saturazione inferiore al {1}% o valore inferiore al {2}% vengono esclusi.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="22"/>
        <source>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</source>
        <translation>Strumento Automatico di Analisi Immagini Drone v1.2 - Sponsorizzato da TEXSAR</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1148"/>
        <source>Load Results Folder</source>
        <translation>Carica Cartella Risultati</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="52"/>
        <source>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</source>
        <translation>Sfoglia per la cartella di output dove salvare i risultati dell&apos;analisi.
Apre una finestra di selezione cartella.
Scegli una cartella vuota o creane una nuova per evitare di sovrascrivere file esistenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="57"/>
        <location filename="../resources/views/images/MainWindow.ui" line="133"/>
        <location filename="../resources/views/images/MainWindow.ui" line="597"/>
        <source> Select</source>
        <translation> Seleziona</translation>
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
        <translation>Percorso della cartella di output per salvare i risultati dell&apos;analisi.
Clicca il pulsante Seleziona per scegliere una cartella di destinazione.
I risultati includono:
• Immagini elaborate con oggetti rilevati evidenziati
• File CSV con coordinate di rilevamento e metadati
• File KML per visualizzare i risultati in applicazioni di mappatura
• Ulteriori file di output specifici dell&apos;algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="97"/>
        <source>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</source>
        <translation>Seleziona la cartella contenente le immagini da analizzare.
Formati supportati: JPG, PNG, TIFF e altri formati immagine comuni.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="101"/>
        <source>Input Folder:</source>
        <translation>Cartella Input:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="113"/>
        <source>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</source>
        <translation>Seleziona la cartella di destinazione per i risultati dell&apos;analisi.
L&apos;output include immagini elaborate con rilevamenti evidenziati e file di dati CSV.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="117"/>
        <source>Output Folder:</source>
        <translation>Cartella Output:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="129"/>
        <source>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</source>
        <translation>Sfoglia la cartella di input contenente le immagini da analizzare.
Apre una finestra di selezione cartella.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="152"/>
        <source>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</source>
        <translation>Percorso della cartella di input contenente le immagini per l&apos;analisi.
Clicca il pulsante Seleziona per scegliere una cartella.
Tutti i file immagine supportati in questa cartella verranno elaborati.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="209"/>
        <source>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</source>
        <translation>Dimensione minima dell&apos;oggetto in pixel per il filtro di rilevamento.
Gli oggetti più piccoli di questo valore verranno ignorati.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="213"/>
        <source>Min Object Area (px):</source>
        <translation>Area Min Oggetto (px):</translation>
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
        <translation>Imposta l&apos;area minima dell&apos;oggetto in pixel per il filtro di rilevamento.
• Intervallo: da 1 a 999 pixel
• Predefinito: 10 pixel
Gli oggetti più piccoli di questa soglia verranno filtrati e non rilevati.
• Valori più bassi: rilevano oggetti più piccoli (possono aumentare i falsi positivi)
• Valori più alti: rilevano solo oggetti più grandi (riduce il rumore)
Usa per filtrare piccoli artefatti e rumore nei risultati di rilevamento.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="269"/>
        <source>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</source>
        <translation>Dimensione massima dell&apos;oggetto in pixel per il filtro di rilevamento.
Gli oggetti più grandi di questo valore verranno ignorati.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="273"/>
        <source>Max Object Area (px):</source>
        <translation>Area Max Oggetto (px):</translation>
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
        <translation>Imposta l&apos;area massima dell&apos;oggetto in pixel per il filtro di rilevamento.
• Intervallo: da 0 a 99999 pixel
• Predefinito: 0 (Nessuno - nessun filtro massimo applicato)
• Valore speciale: 0 viene visualizzato come &quot;Nessuno&quot;
Gli oggetti più grandi di questa soglia verranno filtrati e non rilevati.
• Valori più bassi: rilevano solo oggetti più piccoli
• Valori più alti: consentono il rilevamento di oggetti più grandi
• Imposta su 0 (Nessuno): nessun filtro di dimensione massima
Usa per escludere falsi positivi molto grandi come ombre o caratteristiche del terreno.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="299"/>
        <source>None</source>
        <translation>Nessuno</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="323"/>
        <source>Disable the maximum size filter and allow detections of any size.</source>
        <translation>Disattiva il filtro di dimensione massima e consente rilevamenti di qualsiasi dimensione.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="326"/>
        <source>No max limit</source>
        <translation>Nessun limite max</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="359"/>
        <source>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</source>
        <translation>Colore usato per contrassegnare e identificare gli oggetti rilevati nelle immagini di output.
Clicca il pulsante colore per selezionare un colore diverso.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="363"/>
        <source>Object Identifer Color:</source>
        <translation>Colore Identificatore Oggetto:</translation>
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
        <translation>Seleziona il colore usato per contrassegnare gli oggetti rilevati nelle immagini di output.
• Predefinito: Verde (RGB: 0, 255, 0)
Clicca per aprire una finestra di selezione colore e scegliere un colore di marcatura diverso.
Il colore selezionato sarà usato per:
• Disegnare cerchi/rettangoli attorno agli oggetti rilevati
• Evidenziare le posizioni AOI nelle immagini di output
• Creare marcatori visivi nel visualizzatore risultati
Scegli un colore che contrasti bene con il contenuto dell&apos;immagine per una migliore visibilità.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="395"/>
        <source>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</source>
        <translation>Numero massimo di processi paralleli da usare per l&apos;analisi immagini.
Più processi = elaborazione più veloce ma maggiore uso di CPU/memoria.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="399"/>
        <source>Max Processes: </source>
        <translation>Processi Max: </translation>
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
        <translation>Imposta il numero massimo di processi paralleli per l&apos;analisi delle immagini.
• Intervallo: da 1 a 20 processi
• Predefinito: 10 processi
L&apos;applicazione usa il multiprocessing per analizzare più immagini simultaneamente:
• Valori più alti: elaborazione più veloce (usa più core CPU e memoria)
• Valori più bassi: elaborazione più lenta (usa meno risorse di sistema)
• Consigliato: imposta al numero di core CPU o leggermente superiore
• Per sistemi con RAM limitata, riduci questo valore per prevenire problemi di memoria
Ogni processo analizza un&apos;immagine alla volta, quindi più processi = più elaborazione parallela di immagini.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="446"/>
        <source>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</source>
        <translation>Risoluzione a cui vengono elaborate le immagini.
Risoluzioni più basse = elaborazione più veloce ma possono perdere oggetti piccoli.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="450"/>
        <source>Processing Resolution:</source>
        <translation>Risoluzione Elaborazione:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="80"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Strumento Automatico di Analisi Immagini Drone v{version} - Sponsorizzato da TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="591"/>
        <source>Please set the input and output directories.</source>
        <translation>Imposta le cartelle di input e output.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="598"/>
        <source>--- Starting image processing ---</source>
        <translation>--- Inizio elaborazione immagini ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="872"/>
        <source>--- Image Processing Completed ---</source>
        <translation>--- Elaborazione Immagini Completata ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="876"/>
        <source>{count} images with areas of interest identified</source>
        <translation>{count} immagini con aree di interesse identificate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="882"/>
        <source>No areas of interest identified</source>
        <translation>Nessuna area di interesse identificata</translation>
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
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1153"/>
        <source>The selected file is not a valid XML file: {path}</source>
        <translation>Il file selezionato non è un file XML valido: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1357"/>
        <source>Error Loading Results</source>
        <translation>Errore Caricamento Risultati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1358"/>
        <source>Failed to load results file:
{error}</source>
        <translation>Impossibile caricare il file dei risultati:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1412"/>
        <source>Failed to open Streaming Detector:
{error}</source>
        <translation>Impossibile aprire il Rilevatore Streaming:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1435"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Impossibile aprire il Visore voli:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1465"/>
        <source>Failed to open Search Coordinator:
{error}</source>
        <translation>Impossibile aprire il Coordinatore di Ricerca:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1481"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Impossibile aprire la documentazione di Aiuto:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1497"/>
        <source>Failed to open Community Help:
{error}</source>
        <translation>Impossibile aprire l&apos;Aiuto della Community:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1513"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Impossibile aprire il canale YouTube:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1588"/>
        <source> Open Search Coordinator</source>
        <translation> Apri Coordinatore di Ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1590"/>
        <source>Open the Search Coordinator to review every batch in this run.</source>
        <translation>Apri il Coordinatore di Ricerca per esaminare tutti i batch di questa esecuzione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1596"/>
        <source>Open the Results Viewer to review detection results.</source>
        <translation>Apri il Visualizzatore Risultati per esaminare i risultati dei rilevamenti.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1681"/>
        <source>Invalid Value</source>
        <translation>Valore Non Valido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="344"/>
        <source>Select AOI Highlight Color</source>
        <translation>Seleziona Colore Evidenziazione AOI</translation>
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
        <translation>Seleziona l&apos;algoritmo di rilevamento per la tua attività di analisi delle immagini:

HSV COLOR RANGE: rileva oggetti dai colori vivaci (abbigliamento, veicoli, tende)
  • Ideale per: oggetti colorati in condizioni di illuminazione variabile
  • Limite: richiede taratura dei colori, non adatto a oggetti mimetizzati

COLOR RANGE (RGB): semplice rilevamento colore RGB, elaborazione veloce
  • Ideale per: rilevamento base del colore in illuminazione controllata
  • Limite: sensibile alle variazioni di luce

RX ANOMALY: trova oggetti che non corrispondono allo sfondo (non serve un campione)
  • Ideale per: soggetti mimetizzati/nascosti, target sconosciuti
  • Limite: può rilevare anomalie naturali, più lento con molti segmenti

THERMAL ANOMALY: rileva punti caldi/freddi in immagini termiche
  • Ideale per: ricerche notturne, rilevamento di persone/animali dal calore corporeo
  • Limite: richiede una telecamera termica, può rilevare oggetti scaldati dal sole

TEMPERATURE RESIDUAL ANOMALY: rileva outlier locali di delta-T usando i residui radiometrici
  • Ideale per: isolare rare firme termiche calde/fredde su sfondi misti
  • Limite: richiede dati termici radiometrici, può essere sensibile alla scelta della soglia

THERMAL RANGE: rilevamento basato sulla temperatura (es. 35-40°C per gli umani)
  • Ideale per: rilevamento di persone con telecamera termica (temperatura corporea nota)
  • Limite: richiede una telecamera termica, è necessario conoscere la temperatura target

MATCHED FILTER: confronta i target con la firma cromatica di un campione
  • Ideale per: oggetti specifici conosciuti, quando si dispone di un campione
  • Limite: richiede un&apos;immagine di riferimento, non adatto a target sconosciuti

MR MAP: rilevamento multi-risoluzione per oggetti di dimensioni variabili
  • Ideale per: scene complesse con dimensioni del target sconosciute
  • Limite: elaborazione più lenta, più falsi positivi

AI PERSON DETECTOR: modello di deep learning per il rilevamento accurato di persone
  • Ideale per: ricerca e soccorso, individuazione di persone in qualsiasi abbigliamento/posa
  • Limite: rileva solo persone, elaborazione più lenta</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="358"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="376"/>
        <source>Select Directory</source>
        <translation>Seleziona Cartella</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="393"/>
        <source>Select a Reference Image</source>
        <translation>Seleziona un&apos;Immagine di Riferimento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="395"/>
        <source>Images (*.png *.jpg)</source>
        <translation>Immagini (*.png *.jpg)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="443"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="475"/>
        <source>Value Adjusted</source>
        <translation>Valore Regolato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="445"/>
        <source>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</source>
        <translation>L&apos;area massima è stata regolata a {value} pixel per mantenere un intervallo valido.
(L&apos;area minima deve essere inferiore all&apos;area massima)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="477"/>
        <source>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</source>
        <translation>L&apos;area minima è stata regolata a {value} pixel per mantenere un intervallo valido.
(L&apos;area massima deve essere maggiore dell&apos;area minima)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="817"/>
        <source>Area of Interest Limit ({limit}) exceeded. Continue?</source>
        <translation>Limite Area di Interesse ({limit}) superato. Continuare?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="820"/>
        <source>Area of Interest Limit Exceeded</source>
        <translation>Limite Area di Interesse Superato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="873"/>
        <source>Image processing complete</source>
        <translation>Elaborazione immagini completata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="976"/>
        <source>Select File</source>
        <translation>Seleziona File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="976"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>File XML (*.xml);;Tutti i File (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="997"/>
        <source>Select Results Folder</source>
        <translation>Seleziona Cartella Risultati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1030"/>
        <source>Failed to scan folder: {error}</source>
        <translation>Impossibile scansionare la cartella: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1052"/>
        <source>No Results Found</source>
        <translation>Nessun Risultato Trovato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1053"/>
        <source>No ADIAT_DATA.XML files were found in the selected folder.</source>
        <translation>Nessun file ADIAT_DATA.XML trovato nella cartella selezionata.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1070"/>
        <source>Failed to display results: {error}</source>
        <translation>Impossibile visualizzare i risultati: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1081"/>
        <source>Scan failed: {error}</source>
        <translation>Scansione fallita: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1124"/>
        <source>Failed to open viewer: {error}</source>
        <translation>Impossibile aprire il visualizzatore: {error}</translation>
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
        <translation>Seleziona la risoluzione di elaborazione come percentuale della dimensione originale dell&apos;immagine:
• 100%: Risoluzione originale (nessun ridimensionamento, massima qualità, più lenta)
• 75%: Alta qualità (~56% dei pixel, ~1,8x più veloce)
• 50%: Qualità bilanciata (25% dei pixel, ~4x più veloce) - CONSIGLIATO
• 33%: Elaborazione veloce (~11% dei pixel, ~9x più veloce)
• 25%: Molto veloce (6% dei pixel, ~16x più veloce)
• 10%: Ultra veloce (1% dei pixel, ~100x più veloce)

Il ridimensionamento percentuale preserva il rapporto d&apos;aspetto originale.
Funziona con qualsiasi dimensione, orientamento o rapporto d&apos;aspetto dell&apos;immagine.

I valori Min/Max Area sono sempre specificati alla risoluzione originale.
Tutti i risultati sono restituiti nelle coordinate della risoluzione originale.</translation>
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
        <translation>Abilita la pre-elaborazione di normalizzazione dell&apos;istogramma sulle immagini prima del rilevamento.
La normalizzazione dell&apos;istogramma regola i colori dell&apos;immagine per corrispondere a un&apos;immagine di riferimento:
• Uniforma le differenze di illuminazione e colore tra le immagini
• Corregge variazioni dovute a angoli del sole, ombre e condizioni atmosferiche
• Standardizza l&apos;aspetto dei colori nell&apos;insieme di immagini
• Migliora la coerenza dei risultati di rilevamento
Quando abilitata, seleziona un&apos;immagine di riferimento con condizioni di illuminazione/colore ideali.
Utile quando si elaborano immagini scattate in momenti diversi o in condizioni variabili.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="540"/>
        <source>Normalize Histograms</source>
        <translation>Normalizza Istogrammi</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="555"/>
        <source>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</source>
        <translation>Seleziona l&apos;immagine di riferimento per la normalizzazione dell&apos;istogramma.
Tutte le immagini verranno regolate per corrispondere alla distribuzione dei colori di questa immagine.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="559"/>
        <source>Reference Image:</source>
        <translation>Immagine di riferimento:</translation>
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
        <translation>Percorso dell&apos;immagine di riferimento per la normalizzazione dell&apos;istogramma.
Clicca il pulsante Seleziona per scegliere un&apos;immagine.
Scegli un&apos;immagine con condizioni ideali di illuminazione e colore:
• Immagine chiara e ben illuminata dal tuo dataset
• Rappresentativa dell&apos;aspetto desiderato
• Condizioni di illuminazione tipiche per la tua missione
Tutte le altre immagini verranno regolate nei colori per corrispondere a questo riferimento.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="592"/>
        <source>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</source>
        <translation>Sfoglia un&apos;immagine di riferimento per la normalizzazione dell&apos;istogramma.
Apre una finestra di selezione file immagine.
Seleziona un&apos;immagine rappresentativa con buona illuminazione e condizioni di colore tipiche.</translation>
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
        <translation>Seleziona l&apos;algoritmo di rilevamento da usare per l&apos;analisi delle immagini.

Ogni algoritmo ha punti di forza e casi d&apos;uso specifici:

• HSV Color Range: migliore per rilevare oggetti di un colore specifico
• Color Range (RGB): rilevamento colore alternativo usando lo spazio colore RGB
• RX Anomaly: rilevamento statistico di oggetti insoliti/anomali
• Thermal Anomaly: rileva anomalie di temperatura nelle immagini termiche
• Thermal Range: rilevamento basato sulla temperatura nelle immagini termiche
• Matched Filter: rilevamento basato su target usando corrispondenza spettrale
• MR Map: rilevamento di caratteristiche multi-risoluzione a diverse scale
• AI Person Detector: machine learning per rilevare persone

Passa il mouse sul menu a discesa degli algoritmi per descrizioni dettagliate di ciascun algoritmo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="658"/>
        <source>Algorithm:</source>
        <translation>Algoritmo:</translation>
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
        <translation>Seleziona l&apos;algoritmo di rilevamento per la tua attività di analisi immagini.
Ogni algoritmo ha punti di forza unici e casi d&apos;uso ottimali:

═══════════════════════════════════════════════════
HSV COLOR RANGE
═══════════════════════════════════════════════════
Cosa fa: rileva oggetti tramite intervalli di colore specifici usando lo spazio colore HSV
Punti di forza:
• Ideale per rilevare oggetti dai colori vivaci (arancione, giallo, abbigliamento rosso)
• Robusto alle variazioni di illuminazione (HSV separa colore da luminosità)
• Altamente personalizzabile con intervalli per canale
• Strumenti interattivi di selezione colore disponibili
Punti deboli:
• Richiede una regolazione accurata degli intervalli di colore per risultati ottimali
• Può faticare con le variazioni di colore nelle ombre
• Non efficace per oggetti senza colore o mimetizzati
Ideale per: Search &amp; Rescue (abbigliamento colorato, attrezzatura), veicoli colorati, tende, teloni colorati

═══════════════════════════════════════════════════
COLOR RANGE (RGB)
═══════════════════════════════════════════════════
Cosa fa: rileva oggetti tramite intervalli di colore RGB
Punti di forza:
• Specificazione del colore RGB semplice e intuitiva
• Velocità di elaborazione elevata
• Buono per il rilevamento di base basato sul colore
Punti deboli:
• Più sensibile ai cambiamenti di illuminazione rispetto a HSV
• I canali RGB mescolano informazioni di colore e luminosità
• Meno flessibile di HSV per variazioni di colore complesse
Ideale per: situazioni con illuminazione controllata, rilevamento rapido di base del colore, scenari semplici

═══════════════════════════════════════════════════
RX ANOMALY
═══════════════════════════════════════════════════
Cosa fa: rilevamento statistico di anomalie - trova pixel insoliti rispetto allo sfondo
Punti di forza:
• Rileva oggetti che non corrispondono allo sfondo (nessun campione target necessario)
• Eccellente per trovare oggetti mimetizzati o parzialmente nascosti
• Funziona con tutti i tipi di immagini (RGB, termiche, multispettrali)
• Si adatta automaticamente alle caratteristiche della scena
• Buono per rilevare differenze sottili
Punti deboli:
• Può rilevare anomalie naturali (rocce, cambiamenti della vegetazione)
• Richiede la regolazione della sensibilità per bilanciare rilevamento e falsi positivi
• Un numero più alto di segmenti aumenta significativamente il tempo di elaborazione
• Meno efficace in sfondi molto vari o affollati
Ideale per: ricerche di persone scomparse (umano tra la vegetazione), oggetti mimetizzati, target sconosciuti, qualsiasi cosa insolita nella scena

═══════════════════════════════════════════════════
THERMAL ANOMALY
═══════════════════════════════════════════════════
Cosa fa: rileva anomalie di temperatura nelle immagini termiche (punti caldi/freddi)
Punti di forza:
• Trova automaticamente valori di temperatura anomali (non serve una temperatura specifica)
• Eccellente per rilevare fonti di calore (persone, animali, incendi)
• Funziona giorno e notte con camere termiche
• Rileva attraverso vegetazione leggera
• Regolabile per anomalie calde, fredde o entrambe
Punti deboli:
• Richiede immagini termiche (FLIR)
• Può rilevare oggetti riscaldati dal sole (rocce, veicoli)
• I gradienti di temperatura possono causare falsi positivi
• Influenzato dalla temperatura ambiente e dalle condizioni meteo
Ideale per: ricerche notturne, rilevare persone/animali tramite calore corporeo, trovare fonti di calore, rilevamento di punti freddi

═══════════════════════════════════════════════════
THERMAL RANGE
═══════════════════════════════════════════════════
Cosa fa: rilevamento basato sulla temperatura entro un intervallo di temperatura specifico
Punti di forza:
• Rilevamento basato sulla temperatura preciso
• Eccellente per trovare persone (temp. corporea ~35-40°C / 95-104°F)
• Filtra efficacemente le temperature non target
• Funziona giorno e notte con camere termiche
• Molto affidabile quando la temperatura target è nota
Punti deboli:
• Richiede immagini termiche (FLIR) con dati di temperatura
• È necessario conoscere in anticipo l&apos;intervallo di temperatura target
• Le condizioni ambientali influenzano la temperatura target
• Può perdere target in condizioni meteo estreme (casi di ipotermia)
Ideale per: rilevamento persone (temp. corporea nota), target con temperatura specifica, rilevamento incendi (intervalli di temperatura alti)

═══════════════════════════════════════════════════
MATCHED FILTER
═══════════════════════════════════════════════════
Cosa fa: rilevamento basato su target usando la corrispondenza della firma spettrale
Punti di forza:
• Molto preciso quando si dispone di un campione target
• Usa la &quot;firma&quot; spettrale/colore del target per la corrispondenza
• Riduce i falsi positivi abbinando caratteristiche note del target
• Buono per rilevare tipi specifici di oggetti
Punti deboli:
• Richiede un&apos;immagine di riferimento o un campione di colore del target
• Meno efficace se l&apos;aspetto del target varia significativamente
• Differenze di illuminazione possono influenzare l&apos;accuratezza della corrispondenza
• Non adatto per target sconosciuti
Ideale per: trovare oggetti specifici noti (colore specifico del veicolo, abbigliamento specifico), quando si dispone di un campione target da abbinare

═══════════════════════════════════════════════════
MR MAP (Multi-Resolution Map)
═══════════════════════════════════════════════════
Cosa fa: rilevamento di caratteristiche multi-risoluzione a varie scale spaziali
Punti di forza:
• Rileva caratteristiche a più scale contemporaneamente
• Buono per trovare oggetti di dimensioni variabili
• Efficace per l&apos;analisi di scene complesse
• Può rilevare sia caratteristiche grandi che piccole in un unico passaggio
Punti deboli:
• Più intensivo dal punto di vista computazionale
• Richiede un&apos;accurata regolazione dei parametri
• Un numero più alto di segmenti aumenta significativamente il tempo di elaborazione
• Può produrre più falsi positivi richiedendo filtraggio
Ideale per: scene complesse con oggetti di dimensioni variabili, quando la dimensione del target è sconosciuta, mappatura generale di caratteristiche

═══════════════════════════════════════════════════
AI PERSON DETECTOR
═══════════════════════════════════════════════════
Cosa fa: modello AI di deep learning addestrato specificamente per rilevare persone
Punti di forza:
• Estremamente accurato nel rilevare persone in varie pose
• Funziona con visibilità parziale e abbigliamento vario
• Nessun requisito di colore/temperatura - funziona su immagini RGB standard
• Addestrato su milioni di immagini per un rilevamento robusto
• Rileva persone in sfondi complessi
• Richiede minima regolazione dei parametri
Punti deboli:
• Rileva solo persone (non veicoli, attrezzature, ecc.)
• Computazionalmente intensivo - elaborazione più lenta
• Richiede una risoluzione immagine adeguata
• Può faticare con persone molto lontane/piccole
• Meno efficace con occlusione elevata
Ideale per: operazioni di Search &amp; Rescue (persone scomparse), conteggio persone, situazioni in cui è necessario solo il rilevamento di persone

═══════════════════════════════════════════════════
GUIDA ALLA SELEZIONE DELL&apos;ALGORITMO
═══════════════════════════════════════════════════
• Per oggetti colorati (abbigliamento vivace, attrezzatura): HSV Color Range
• Per camere termiche che cercano persone: Thermal Range o Thermal Anomaly
• Per soggetti mimetizzati o nascosti: RX Anomaly
• Per rilevare specificamente persone: AI Person Detector
• Quando hai un campione target: Matched Filter
• Per target sconosciuti che spiccano: RX Anomaly o Thermal Anomaly
• Per l&apos;elaborazione più veloce: Color Range (RGB) o HSV Color Range
• Per il rilevamento persone più accurato: AI Person Detector</translation>
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
        <translation>Avvia l&apos;elaborazione delle immagini con l&apos;algoritmo selezionato.
Requisiti prima di iniziare:
• La cartella di input deve essere selezionata con immagini valide
• La cartella di output deve essere selezionata
• L&apos;algoritmo deve essere selezionato
• Tutti i parametri richiesti dell&apos;algoritmo devono essere configurati
L&apos;elaborazione:
• Analizzerà tutte le immagini nella cartella di input usando l&apos;algoritmo selezionato
• Applicherà filtri globali (area min/max, K-Means, normalizzazione istogramma)
• Salverà i risultati nella cartella di output (immagini marcate, file CSV, KML)
• Visualizzerà avanzamento e risultati nella finestra di output
Clicca Annulla durante l&apos;elaborazione per fermare l&apos;analisi.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="918"/>
        <source>Start</source>
        <translation>Avvia</translation>
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
        <translation>Annulla il processo di analisi immagini attualmente in esecuzione.
Interrompe l&apos;elaborazione immediatamente e termina in modo sicuro tutti i processi worker.
Effetti dell&apos;annullamento:
• Tutti i processi di analisi in esecuzione vengono fermati
• I risultati parziali vengono salvati fino al punto di annullamento
• Le immagini già elaborate avranno file di output nella cartella di output
• L&apos;elaborazione può essere riavviata dopo l&apos;annullamento
• Ritorna allo stato pronto
Usa quando devi fermare l&apos;elaborazione per regolare le impostazioni o correggere problemi.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="963"/>
        <source> Cancel</source>
        <translation> Annulla</translation>
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
        <translation>Apri il Visualizzatore Risultati per rivedere i risultati del rilevamento.
Disponibile dopo il completamento dell&apos;elaborazione.
Il Visualizzatore Risultati offre:
• Navigazione interattiva delle immagini con oggetti rilevati evidenziati
• Confronto affiancato tra immagini originali ed elaborate
• Navigazione attraverso tutte le immagini elaborate
• Dettagli e metadati AOI (Area di Interesse)
• Coordinate GPS per gli oggetti rilevati
• Opzioni di esportazione per i rilevamenti selezionati
• Funzionalità di zoom e panoramica
• Filtri e ordinamento dei risultati di rilevamento
Usa per rivedere, verificare ed esportare i risultati dell&apos;analisi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1594"/>
        <location filename="../resources/views/images/MainWindow.ui" line="1018"/>
        <source> View Results</source>
        <translation> Visualizza Risultati</translation>
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
        <translation>Aiuto</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1111"/>
        <source>Image Analysis Wizard</source>
        <translation>Procedura guidata analisi immagini</translation>
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
        <translation>Avvia la procedura guidata di Analisi Immagini per configurare le impostazioni di analisi.
Apre una procedura guidata passo-passo per:
• Selezionare le cartelle di input e output
• Configurare le impostazioni di acquisizione immagini (drone, altitudine, GSD)
• Impostare la dimensione dell&apos;oggetto target
• Scegliere l&apos;algoritmo di rilevamento
• Configurare i parametri specifici dell&apos;algoritmo
• Impostare opzioni generali di elaborazione
La procedura guidata chiuderà questa finestra e si aprirà con tutte le impostazioni precompilate.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1132"/>
        <source>Load Results File</source>
        <translation>Carica File Risultati</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1135"/>
        <source>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</source>
        <translation>Carica un file risultati salvato in precedenza per la visualizzazione.
Apre una finestra di dialogo per selezionare un file risultati (formato .pkl).
Carica i risultati dell&apos;analisi e apre il Visualizzatore Risultati.
Usa questo per rivedere i risultati di sessioni di analisi precedenti senza rielaborare.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1151"/>
        <source>Scan a folder recursively for ADIAT_DATA.XML files.
Displays all found results in a dialog for easy browsing.
Use this to quickly find and open results from multiple analysis sessions.</source>
        <translation>Esegue una scansione ricorsiva di una cartella alla ricerca di file ADIAT_DATA.XML.
Mostra tutti i risultati trovati in una finestra di dialogo per una facile consultazione.
Usala per trovare e aprire rapidamente i risultati di più sessioni di analisi.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1163"/>
        <source>Preferences</source>
        <translation>Preferenze</translation>
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
        <translation>Apri la finestra Preferenze per configurare le impostazioni dell&apos;applicazione.
Regola le impostazioni globali incluse:
• Tema dell&apos;applicazione (Chiaro/Scuro)
• Soglia di avviso max AOI
• Raggio cerchio AOI per clustering
• Formato del sistema di coordinate (Lat/Long, UTM)
• Unità di temperatura (Fahrenheit/Celsius)
• Unità di distanza (Metri/Piedi)
• File di configurazione sensore drone
Tutte le modifiche vengono salvate automaticamente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1185"/>
        <source>Video Parser</source>
        <translation>Parser Video</translation>
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
        <translation>Apri l&apos;utilità Parser Video per estrarre fotogrammi da file video.
Converte le riprese video in singole immagini di fotogrammi per l&apos;analisi.
Funzionalità:
• Estrae fotogrammi a intervalli di tempo specificati
• Supporto opzionale file SRT per metadati GPS
• Supporta formati video comuni (MP4, AVI, MOV, ecc.)
• Incorpora dati di posizione nei fotogrammi estratti
Usa per preparare le riprese video per l&apos;analisi basata su immagini.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1205"/>
        <source>Streaming Detector</source>
        <translation>Rilevatore Streaming</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1208"/>
        <source>Switch to the Streaming Detector</source>
        <translation>Passa al Rilevatore Streaming</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1218"/>
        <source>Flight Viewer</source>
        <translation>Visore voli</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1221"/>
        <source>Open the Flight Viewer to pair with ADIAT Mobile drone controllers and watch their live feeds.</source>
        <translation>Apri il Visore voli per abbinare controller drone ADIAT Mobile e guardare i loro flussi live.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1231"/>
        <source>Real-Time Anomaly Detection</source>
        <translation>Rilevamento Anomalie in Tempo Reale</translation>
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
        <translation>Apri la finestra Rilevamento Anomalie in Tempo Reale per analisi avanzate dal vivo.
Combina più algoritmi di rilevamento per un rilevamento completo di anomalie in tempo reale.
Funzionalità:
• Rilevamento del movimento con sottrazione dello sfondo
• Rilevamento anomalie con quantizzazione del colore
• Elaborazione avanzata di video in streaming
• Fusione dei rilevamenti e filtraggio temporale
• Ottimizzazione delle prestazioni in tempo reale
• Elaborazione multi-thread per migliori prestazioni
• Maggiore accuratezza di rilevamento grazie alla combinazione di algoritmi
Progettato per rilevare oggetti insoliti, movimento e colori nei flussi video in tempo reale.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1254"/>
        <source>Search Coordinator</source>
        <translation>Coordinatore di Ricerca</translation>
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
        <translation>Apri la finestra Coordinatore di Ricerca per gestire progetti di revisione multi-batch.
Funzionalità:
• Crea e gestisce progetti di ricerca con più batch
• Traccia l&apos;avanzamento dei revisori su più set di immagini
• Consolida i risultati di revisione di più revisori
• Visualizza un dashboard con stato e metriche della ricerca
• Esporta risultati consolidati
• Gestisce assegnazioni dei batch e coordinamento dei revisori
Ideale per ricerche su larga scala con più revisori e batch di immagini.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1273"/>
        <source>Ctrl+Shift+C</source>
        <translation>Ctrl+Shift+C</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1278"/>
        <source>Manual</source>
        <translation>Manuale</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1281"/>
        <source>Open the online help documentation in your web browser.
Access comprehensive documentation, tutorials, and user guides.
Provides detailed information on all features and algorithms.</source>
        <translation>Apri la documentazione di aiuto online nel browser.
Accedi a documentazione completa, tutorial e guide utente.
Fornisce informazioni dettagliate su tutte le funzionalità e gli algoritmi.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1293"/>
        <source>Check for Updates</source>
        <translation>Verifica Aggiornamenti</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1296"/>
        <source>Check the update feed for a newer ADIAT installer.
If an update is available, you can download and launch the installer from here.</source>
        <translation>Controlla il feed degli aggiornamenti per un nuovo installer ADIAT.
Se è disponibile un aggiornamento, puoi scaricare e avviare l&apos;installer da qui.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1307"/>
        <source>Community Forum</source>
        <translation>Forum della Comunità</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1310"/>
        <source>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</source>
        <translation>Unisciti al server Discord della comunità per supporto e discussioni.
Connettiti con altri utenti, condividi esperienze e ottieni aiuto.
Fai domande, segnala problemi e suggerisci nuove funzionalità.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1322"/>
        <source>YouTube Channel</source>
        <translation>Canale YouTube</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="794"/>
        <source>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</source>
        <translation>Impossibile analizzare il file XML. Controlla i percorsi dei file in &quot;{file_name}&quot;</translation>
    </message>
</context>
<context>
    <name>MapDock</name>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="263"/>
        <source>Map</source>
        <translation>Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="360"/>
        <source>QtWebEngine not available — install PySide6-Addons for the interactive map. Showing list view instead.</source>
        <translation>QtWebEngine non disponibile — installa PySide6-Addons per la mappa interattiva. Verrà mostrata la vista elenco.</translation>
    </message>
</context>
<context>
    <name>MapExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="34"/>
        <source>Map Export Options</source>
        <translation>Opzioni Esportazione Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="45"/>
        <source>Configure Map Export</source>
        <translation>Configura Esportazione Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="53"/>
        <source>Export Type</source>
        <translation>Tipo di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="56"/>
        <source>KML File</source>
        <translation>File KML</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="58"/>
        <source>Export to a KML file for use in Google Earth, etc.</source>
        <translation>Esporta in un file KML per l&apos;uso in Google Earth, ecc.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="60"/>
        <source>CalTopo</source>
        <translation>CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="61"/>
        <source>Export directly to a CalTopo map</source>
        <translation>Esporta direttamente su una mappa CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="73"/>
        <source>Data to Include</source>
        <translation>Dati da Includere</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="76"/>
        <source>Drone/Image Locations</source>
        <translation>Posizioni Drone/Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="78"/>
        <source>Include markers for each drone image location</source>
        <translation>Includi indicatori per ogni posizione immagine del drone</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="80"/>
        <source>Flagged Areas of Interest</source>
        <translation>Aree di Interesse Contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="82"/>
        <source>Include markers for flagged AOIs</source>
        <translation>Includi indicatori per le AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="84"/>
        <source>Coverage Area</source>
        <translation>Area di Copertura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="86"/>
        <source>Include polygon(s) showing the geographic coverage extent</source>
        <translation>Includi poligono/i che mostrano l&apos;estensione della copertura geografica</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="88"/>
        <source>Include images without flagged AOIs</source>
        <translation>Includi immagini senza AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="90"/>
        <source>If unchecked, only export locations for images that have flagged AOIs</source>
        <translation>Se deselezionato, esporta solo le posizioni delle immagini che hanno AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="101"/>
        <source>Probability of Detection (POD)</source>
        <translation>Probabilità di rilevamento (POD)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="104"/>
        <source>POD coverage heatmap (terrain-aware)</source>
        <translation>Heatmap di copertura POD (con analisi del terreno)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="107"/>
        <source>Compute a terrain and canopy aware probability-of-detection raster for the whole mission (all non-hidden images, independent of the selections above). KML exports embed the heatmap in the KML/KMZ as an image overlay; the GeoTIFF products (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) are also written — the GeoTIFF can be imported into CalTopo Map Sheets. May take several minutes.</source>
        <translation>Calcola un raster di probabilità di rilevamento consapevole di terreno e chioma per l&apos;intera missione (tutte le immagini non nascoste, indipendente dalle selezioni sopra). Le esportazioni KML incorporano la mappa di calore nel KML/KMZ come sovrapposizione immagine; vengono scritti anche i prodotti GeoTIFF (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json); il GeoTIFF può essere importato in CalTopo Map Sheets. Può richiedere diversi minuti.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="114"/>
        <source>Show on map when complete</source>
        <translation>Mostra sulla mappa al termine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="125"/>
        <source>CalTopo Options</source>
        <translation>Opzioni CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="128"/>
        <source>Include Images</source>
        <translation>Includi Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="130"/>
        <source>Upload photos to CalTopo markers (CalTopo only)</source>
        <translation>Carica foto sui marker CalTopo (solo CalTopo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="150"/>
        <source>Export</source>
        <translation>Esporta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>MatchedFilter</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="42"/>
        <source>Add a new color signature for matched filter detection. Each color can have its own threshold value.</source>
        <translation>Aggiungi una nuova firma colore per il rilevamento con filtro matched. Ogni colore può avere il proprio valore di soglia.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="45"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
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
        <translation>Apre la finestra Visualizzatore Intervallo per:
- Vedere l&apos;intervallo di colori che verranno cercati nell&apos;analisi delle immagini.
Usalo per vedere quali colori verranno rilevati e ottimizzare le soglie prima dell&apos;elaborazione.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="88"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
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
        <translation>Nessun Colore Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="299"/>
        <source>Please add at least one color to detect.</source>
        <translation>Aggiungi almeno un colore da rilevare.</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilterWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Aggiungi Colore</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="47"/>
        <source>No Targets Selected</source>
        <translation>Nessun Obiettivo Selezionato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="57"/>
        <source>View Range</source>
        <translation>Visualizza Intervallo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="218"/>
        <source>Please add at least one target color to detect.</source>
        <translation>Aggiungi almeno un colore obiettivo da rilevare.</translation>
    </message>
</context>
<context>
    <name>MeasureDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="71"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Distance</source>
        <translation>Misura Distanza</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="85"/>
        <source>Measure Shadow</source>
        <translation>Misura ombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="87"/>
        <source>When checked, the two clicks estimate the height of a vertical object from its shadow. Click the base of the object first, then the tip of its shadow.</source>
        <translation>Se selezionata, i due clic stimano l&apos;altezza di un oggetto verticale dalla sua ombra. Fai prima clic sulla base dell&apos;oggetto, poi sulla punta della sua ombra.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="94"/>
        <source>Ground Sample Distance</source>
        <translation>Distanza di Campionamento al Suolo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="97"/>
        <source>GSD:</source>
        <translation>GSD:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="99"/>
        <source>Enter GSD value</source>
        <translation>Inserisci valore GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="103"/>
        <source>cm/px</source>
        <translation>cm/px</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="111"/>
        <source>Measurement</source>
        <translation>Misurazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="114"/>
        <source>Distance:</source>
        <translation>Distanza:</translation>
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
        <translation>Stima altezza da ombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="135"/>
        <source>Use Anyway</source>
        <translation>Usa comunque</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="137"/>
        <source>Force the estimate with the current base/tip clicks even though the drawn line doesn&apos;t match the expected shadow direction. Use only when you&apos;re confident the geometry is correct.</source>
        <translation>Forza la stima con i clic base/punta correnti anche se la linea disegnata non corrisponde alla direzione prevista dell&apos;ombra. Usalo solo se sei sicuro che la geometria sia corretta.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="181"/>
        <source>Click the BASE of the object first, then the TIP of its shadow.</source>
        <translation>Fai clic prima sulla BASE dell&apos;oggetto, poi sulla PUNTA della sua ombra.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="185"/>
        <source>Click on the image to place the first point,
then click again to place the second point.</source>
        <translation>Clicca sull&apos;immagine per posizionare il primo punto,
poi clicca di nuovo per posizionare il secondo punto.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="158"/>
        <source>Clear</source>
        <translation>Cancella</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="160"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Shadow Height</source>
        <translation>Misura altezza da ombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="415"/>
        <source>Image metadata unavailable</source>
        <translation>Metadati immagine non disponibili</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="553"/>
        <source>Rejected</source>
        <translation>Rifiutata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="577"/>
        <source>No GSD value</source>
        <translation>Nessun valore GSD</translation>
    </message>
</context>
<context>
    <name>MediaSelector</name>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool (ADIAT)</source>
        <translation>Strumento Automatico di Analisi Immagini Drone (ADIAT)</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="31"/>
        <source>What would you like to do?</source>
        <translation>Cosa vuoi fare?</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="86"/>
        <source>Image Analysis</source>
        <translation>Analisi immagini</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="169"/>
        <source>Stream Analysis</source>
        <translation>Analisi streaming</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="246"/>
        <source>Pair with ADIAT Mobile drone controllers to receive their live camera feeds with detections.</source>
        <translation>Abbina i controller drone ADIAT Mobile per ricevere i loro flussi video live con rilevamenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="163"/>
        <source>RTMP, Video Files, HDMI Capture</source>
        <translation>RTMP, File Video, Acquisizione HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="252"/>
        <source>Flight Viewer</source>
        <translation>Visore voli</translation>
    </message>
</context>
<context>
    <name>MissionGalleryContents</name>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="32"/>
        <source>Filters</source>
        <translation>Filtri</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="38"/>
        <source>Feed</source>
        <translation>Flusso</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="48"/>
        <source>Detector</source>
        <translation>Rilevatore</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="58"/>
        <source>Min score</source>
        <translation>Punteggio min.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="99"/>
        <source>0 detections</source>
        <translation>0 rilevamenti</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="119"/>
        <source>Export</source>
        <translation>Esporta</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="122"/>
        <source>Export filtered detections to the standard ADIAT image-mode gallery format.</source>
        <translation>Esporta i rilevamenti filtrati nel formato galleria standard della modalità immagini ADIAT.</translation>
    </message>
</context>
<context>
    <name>MissionGalleryDock</name>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="28"/>
        <source>Mission Gallery</source>
        <translation>Galleria missione</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="53"/>
        <source>All feeds</source>
        <translation>Tutti i flussi</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="59"/>
        <source>All detectors</source>
        <translation>Tutti i rilevatori</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="126"/>
        <source>0 detections</source>
        <translation>0 rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="151"/>
        <source>{n} detections</source>
        <translation>{n} rilevamenti</translation>
    </message>
</context>
<context>
    <name>PDFExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="151"/>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="160"/>
        <source>No Images to Export</source>
        <translation>Nessuna Immagine da Esportare</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="153"/>
        <source>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</source>
        <translation>Non ci sono immagini disponibili da includere nel report PDF.

Tutte le immagini potrebbero essere nascoste oppure non ci sono immagini nel dataset.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="162"/>
        <source>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</source>
        <translation>Non ci sono immagini con AOI contrassegnate da includere nel report PDF.

Contrassegna almeno una AOI oppure seleziona &apos;Includi immagini senza AOI contrassegnate&apos; per includere tutte le immagini nel report.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="172"/>
        <source>Save PDF File</source>
        <translation>Salva File PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="174"/>
        <source>PDF files (*.pdf)</source>
        <translation>File PDF (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="216"/>
        <source>Generating PDF Report</source>
        <translation>Generazione Report PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="219"/>
        <source>Generating PDF Report...</source>
        <translation>Generazione Report PDF...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="260"/>
        <source>Failed to generate PDF file: {error}</source>
        <translation>Impossibile generare il file PDF: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="276"/>
        <source>Success</source>
        <translation>Successo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="277"/>
        <source>PDF report generated successfully!</source>
        <translation>Report PDF generato con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="294"/>
        <source>PDF generation failed: {error}</source>
        <translation>Generazione PDF non riuscita: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="308"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
</context>
<context>
    <name>PDFExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="27"/>
        <source>PDF Export Settings</source>
        <translation>Impostazioni Esportazione PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="35"/>
        <source>Enter the following information for the PDF report:</source>
        <translation>Inserisci le seguenti informazioni per il report PDF:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="44"/>
        <source>Enter organization name</source>
        <translation>Inserisci nome organizzazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="45"/>
        <source>Organization:</source>
        <translation>Organizzazione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="49"/>
        <source>Enter search name</source>
        <translation>Inserisci nome ricerca</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="50"/>
        <source>Search Name:</source>
        <translation>Nome Ricerca:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="55"/>
        <source>Export Options:</source>
        <translation>Opzioni di Esportazione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="60"/>
        <source>Include images without flagged AOIs</source>
        <translation>Includi immagini senza AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="62"/>
        <source>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</source>
        <translation>Quando selezionato, tutte le immagini saranno incluse nel report PDF, anche se non hanno AOI contrassegnate. Quando deselezionato, verranno incluse solo le immagini con AOI contrassegnate.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="69"/>
        <source>Map Tiles:</source>
        <translation>Tile mappa:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="71"/>
        <source>Map</source>
        <translation>Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="72"/>
        <source>Satellite</source>
        <translation>Satellite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="73"/>
        <source>Choose the background tiles for the PDF overview map.</source>
        <translation>Scegli le tile di sfondo per la mappa panoramica del PDF.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="80"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="82"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
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
  ... e altri {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="92"/>
        <source>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</source>
        <translation>{count} immagine/i sorgente non trovata/e nelle posizioni previste:

{files}

Seleziona la cartella contenente le immagini sorgente.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="100"/>
        <source>Source Images Not Found</source>
        <translation>Immagini Sorgente Non Trovate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="111"/>
        <source>Select Source Images Folder</source>
        <translation>Seleziona Cartella Immagini Sorgente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="143"/>
        <source>Some Images Still Missing</source>
        <translation>Alcune Immagini Mancano Ancora</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="145"/>
        <source>Found {found} of {total} images.

Still missing:
{missing}</source>
        <translation>Trovate {found} di {total} immagini.

Ancora mancanti:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="175"/>
        <source>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</source>
        <translation>{count} maschera/e di rilevamento non trovata/e nelle posizioni previste:

{files}

Seleziona la cartella contenente i file delle maschere.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="183"/>
        <source>Detection Masks Not Found</source>
        <translation>Maschere di Rilevamento Non Trovate</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="194"/>
        <source>Select Masks Folder</source>
        <translation>Seleziona Cartella Maschere</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="226"/>
        <source>Some Masks Still Missing</source>
        <translation>Alcune Maschere Mancano Ancora</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="228"/>
        <source>Found {found} of {total} masks.

Still missing:
{missing}</source>
        <translation>Trovate {found} di {total} maschere.

Ancora mancanti:
{missing}</translation>
    </message>
</context>
<context>
    <name>PersonReferenceDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="277"/>
        <source>Person Size Reference</source>
        <translation>Riferimento dimensioni persona</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="284"/>
        <source>Reference Person</source>
        <translation>Persona di riferimento</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="303"/>
        <source>Standing</source>
        <translation>In piedi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="305"/>
        <source>Lying down</source>
        <translation>Sdraiata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="307"/>
        <source>Sitting</source>
        <translation>Seduta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="316"/>
        <source>Show shadows (from capture time)</source>
        <translation>Mostra ombre (all&apos;ora dello scatto)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="319"/>
        <source>Use terrain elevation (DEM)</source>
        <translation>Usa quota del terreno (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="328"/>
        <source>Rotate the person on the ground to line it up with an object</source>
        <translation>Ruota la persona sul terreno per allinearla a un oggetto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="333"/>
        <source>Click to choose overlay color</source>
        <translation>Fai clic per scegliere il colore della sovrapposizione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="341"/>
        <source>Size:</source>
        <translation>Dimensione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="342"/>
        <source>Show:</source>
        <translation>Mostra:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="343"/>
        <source>Rotation:</source>
        <translation>Rotazione:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="346"/>
        <source>Color:</source>
        <translation>Colore:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="359"/>
        <source>Drag the white handle to position the reference person. Silhouettes are drawn at true ground scale for this image&apos;s altitude and camera angle.</source>
        <translation>Trascina la maniglia bianca per posizionare la persona di riferimento. Le sagome sono disegnate in scala reale al suolo per l&apos;altitudine e l&apos;angolo della fotocamera di questa immagine.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="367"/>
        <source>Recenter</source>
        <translation>Ricentra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="368"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="423"/>
        <source>Perspective overlay unavailable: this image is missing the altitude or lens metadata needed to project a person.</source>
        <translation>Sovrapposizione prospettica non disponibile: a questa immagine mancano i metadati di quota o obiettivo necessari per proiettare una persona.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="441"/>
        <source>no image loaded</source>
        <translation>nessuna immagine caricata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="446"/>
        <source>image metadata could not be read</source>
        <translation>impossibile leggere i metadati dell&apos;immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="450"/>
        <source>image has no GPS coordinates</source>
        <translation>l&apos;immagine non ha coordinate GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="462"/>
        <source>capture time / timezone not in metadata</source>
        <translation>ora di scatto / fuso orario non presenti nei metadati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="468"/>
        <source>sun position could not be computed</source>
        <translation>impossibile calcolare la posizione del sole</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="477"/>
        <source>Sun at capture: {elev:.0f}° above horizon, azimuth {az:.0f}°.</source>
        <translation>Sole allo scatto: {elev:.0f}° sopra l&apos;orizzonte, azimut {az:.0f}°.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="482"/>
        <source>Capture time zone estimated from GPS location.</source>
        <translation>Fuso orario dello scatto stimato dalla posizione GPS.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="487"/>
        <source>the sun was below the horizon at capture</source>
        <translation>il sole era sotto l&apos;orizzonte al momento dello scatto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="489"/>
        <source>sun position unavailable</source>
        <translation>posizione del sole non disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="490"/>
        <source>Shadow unavailable: {reason}.</source>
        <translation>Ombra non disponibile: {reason}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="589"/>
        <source>Place the person and shadow on the DEM terrain surface</source>
        <translation>Posiziona la persona e l&apos;ombra sulla superficie del terreno DEM</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="593"/>
        <source>Terrain (DEM) data is not available for this image</source>
        <translation>I dati del terreno (DEM) non sono disponibili per questa immagine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="853"/>
        <source>Choose Overlay Color</source>
        <translation>Scegli colore sovrapposizione</translation>
    </message>
</context>
<context>
    <name>PlaybackControlBar</name>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="54"/>
        <source>Play/Pause (Space)</source>
        <translation>Riproduci/Pausa (Spazio)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="67"/>
        <source>Seek through video</source>
        <translation>Naviga nel video</translation>
    </message>
</context>
<context>
    <name>Preferences</name>
    <message>
        <location filename="../resources/views/Preferences.ui" line="14"/>
        <source>Preferences</source>
        <translation>Preferenze</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="55"/>
        <source>Select the application theme appearance.
Changes the overall color scheme and visual style.</source>
        <translation>Seleziona l&apos;aspetto del tema dell&apos;applicazione.
Cambia lo schema colori generale e lo stile visivo.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="59"/>
        <source>Theme:</source>
        <translation>Tema:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="71"/>
        <source>Choose the application theme:
• Light: Bright theme with light backgrounds and dark text
• Dark: Dark theme with dark backgrounds and light text
Changes apply immediately to all windows.</source>
        <translation>Scegli il tema dell&apos;applicazione:
• Chiaro: Tema luminoso con sfondi chiari e testo scuro
• Scuro: Tema scuro con sfondi scuri e testo chiaro
Le modifiche si applicano immediatamente a tutte le finestre.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="78"/>
        <source>Light</source>
        <translation>Chiaro</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="83"/>
        <source>Dark</source>
        <translation>Scuro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="109"/>
        <source>Elevation Source:</source>
        <translation>Origine elevazione:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="142"/>
        <location filename="../app/core/controllers/Preferences.py" line="378"/>
        <source>3DEP is inactive until both paths are set — the AWS Terrain Tiles baseline is used. Use Download tiles… or Browse.</source>
        <translation>3DEP è inattivo finché non vengono impostati entrambi i percorsi: viene usata la base AWS Terrain Tiles. Usa Scarica tile… o Sfoglia.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="174"/>
        <source>Terrain</source>
        <translation>Terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="191"/>
        <source>Canopy Data Source</source>
        <translation>Origine dati chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="195"/>
        <source>Source:</source>
        <translation>Origine:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="206"/>
        <source>Path to the canopy manifest CSV</source>
        <translation>Percorso del CSV manifest della chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="236"/>
        <source>Download tiles...</source>
        <translation>Scarica tile...</translation>
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
        <translation>I file 3DEP registrati non esistono più sul disco: viene usata la base AWS Terrain Tiles. Scarica di nuovo o correggi i percorsi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="416"/>
        <source>Select 3DEP manifest CSV</source>
        <translation>Seleziona CSV manifest 3DEP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="418"/>
        <location filename="../app/core/controllers/Preferences.py" line="482"/>
        <source>CSV files (*.csv);;All files (*)</source>
        <translation>File CSV (*.csv);;Tutti i file (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="428"/>
        <source>Select 3DEP tiles directory</source>
        <translation>Seleziona cartella tile 3DEP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="457"/>
        <source>The registered canopy files no longer exist on disk — canopy is disabled. Re-download or fix the paths.</source>
        <translation>I file della chioma registrati non esistono più sul disco: la chioma è disattivata. Scarica di nuovo o correggi i percorsi.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="481"/>
        <source>Select canopy manifest CSV</source>
        <translation>Seleziona il CSV manifest della chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="490"/>
        <source>Select canopy tiles directory</source>
        <translation>Seleziona la cartella delle tile della chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="501"/>
        <source>Download Tiles</source>
        <translation>Scarica tile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="502"/>
        <source>The tile downloader is unavailable:
{error}</source>
        <translation>Il downloader delle tile non è disponibile:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="575"/>
        <source>{tiles} tiles ({size_mb:.1f} MB)</source>
        <translation>{tiles} tasselli ({size_mb:.1f} MB)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="567"/>
        <source>Not available</source>
        <translation>Non disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="587"/>
        <location filename="../app/core/controllers/Preferences.py" line="595"/>
        <location filename="../app/core/controllers/Preferences.py" line="623"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="596"/>
        <source>Terrain service not available.</source>
        <translation>Servizio terreno non disponibile.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="602"/>
        <source>Clear Terrain Cache</source>
        <translation>Cancella Cache Terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="604"/>
        <source>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Sei sicuro di voler cancellare tutti i dati di elevazione del terreno memorizzati nella cache?

Ciò richiederà il nuovo download dei tasselli quando verrà utilizzata l&apos;elevazione del terreno.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="617"/>
        <source>Cache Cleared</source>
        <translation>Cache Cancellata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="618"/>
        <source>Cleared {count} cached terrain tiles.</source>
        <translation>Cancellati {count} tasselli di terreno dalla cache.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="624"/>
        <source>Failed to clear cache: {error}</source>
        <translation>Impossibile cancellare la cache: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="631"/>
        <source>Select a Drone Sensor File</source>
        <translation>Seleziona un File Sensore Drone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="69"/>
        <source>Language:</source>
        <translation>Lingua:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="101"/>
        <source>AWS Terrain Tiles (online, ~30 m) is always available as the baseline; local USGS 3DEP adds 1 m detail where downloaded.</source>
        <translation>AWS Terrain Tiles (online, ~30 m) è sempre disponibile come base; l&apos;USGS 3DEP locale aggiunge dettaglio a 1 m dove scaricato.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="119"/>
        <location filename="../app/core/controllers/Preferences.py" line="204"/>
        <source>Manifest CSV:</source>
        <translation>CSV manifest:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="121"/>
        <source>Path to dem_manifest.csv</source>
        <translation>Percorso di dem_manifest.csv</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="122"/>
        <location filename="../app/core/controllers/Preferences.py" line="133"/>
        <location filename="../app/core/controllers/Preferences.py" line="207"/>
        <location filename="../app/core/controllers/Preferences.py" line="217"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="130"/>
        <location filename="../app/core/controllers/Preferences.py" line="214"/>
        <source>Tiles directory:</source>
        <translation>Cartella tile:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="132"/>
        <location filename="../app/core/controllers/Preferences.py" line="216"/>
        <source>Folder containing the GeoTIFF tiles</source>
        <translation>Cartella contenente i tile GeoTIFF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="226"/>
        <location filename="../app/core/controllers/Preferences.py" line="451"/>
        <source>Canopy is disabled until both paths are set — use Download tiles… or Browse.</source>
        <translation>La chioma è disabilitata finché entrambi i percorsi non sono impostati — usa Scarica tile… o Sfoglia.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="238"/>
        <source>Download DEM and/or canopy tiles for an area of interest and register them here. Note: the canopy download uses Meta/WRI data and registers it as the canopy source.</source>
        <translation>Scarica le tile DEM e/o chioma per un&apos;area di interesse e registrale qui. Nota: il download della chioma usa dati Meta/WRI e li registra come origine dati chioma.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="584"/>
        <source>N/A (local tiles)</source>
        <translation>N/D (tile locali)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="633"/>
        <source>CSV Files (*.csv)</source>
        <translation>File CSV (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="659"/>
        <source>Restart Required</source>
        <translation>Riavvio Richiesto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="660"/>
        <source>Please restart the application for language changes to take effect.</source>
        <translation>Riavvia l&apos;applicazione affinché le modifiche alla lingua abbiano effetto.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="118"/>
        <source>Max Areas of Interest: </source>
        <translation>Aree di Interesse Massime: </translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="165"/>
        <source>Area of Interest Circle Radius(px):</source>
        <translation>Raggio Cerchio Area di Interesse (px):</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="213"/>
        <source>Coordinate System:</source>
        <translation>Sistema di Coordinate:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="266"/>
        <source>Temperature Unit:</source>
        <translation>Unità di Temperatura:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="315"/>
        <source>Distance Unit:</source>
        <translation>Unità di Distanza:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="366"/>
        <source>Offline Only Mode:</source>
        <translation>Modalità Solo Offline:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="404"/>
        <source>Use Terrain Elevation:</source>
        <translation>Usa Elevazione Terreno:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="416"/>
        <source>Enable terrain-corrected AOI positioning using DEM/DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</source>
        <translation>Abilita il posizionamento AOI corretto per il terreno usando dati di elevazione DEM/DTM/DSM.
• Quando abilitato: scarica e memorizza in cache i tasselli di elevazione per un posizionamento accurato
• Quando disabilitato: usa l&apos;assunzione di terreno piatto (più veloce, funziona offline)
I dati del terreno vengono memorizzati localmente e funzionano offline dopo il primo download.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="444"/>
        <source>Terrain Cache:</source>
        <translation>Cache Terreno:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="521"/>
        <source>Drone Sensor File Version:</source>
        <translation>Versione File Sensore Drone:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="588"/>
        <source>Replace</source>
        <translation>Sostituisci</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="485"/>
        <source>Clear Cache</source>
        <translation>Cancella Cache</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="114"/>
        <source>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</source>
        <translation>Soglia di avviso per il totale di AOI rilevate in tutte le immagini.
Avvisa l&apos;utente quando questo limite viene raggiunto durante l&apos;elaborazione.</translation>
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
        <translation>Imposta la soglia di avviso per il totale di AOI rilevate durante l&apos;elaborazione.
• Intervallo: da 0 a 1000
• Predefinito: 100
Quando questo numero di AOI è rilevato su tutte le immagini:
• L&apos;interfaccia mostra un messaggio di avviso
• L&apos;utente può annullare l&apos;elaborazione, regolare le impostazioni e rieseguire
• Se non viene intrapresa alcuna azione, il rilevamento continua automaticamente
Usa valori più bassi per individuare presto conteggi elevati di rilevamenti.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="161"/>
        <source>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</source>
        <translation>Raggio per combinare AOI vicine in singoli rilevamenti.
Le AOI entro questa distanza vengono unite.</translation>
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
        <translation>Imposta il raggio per combinare AOI vicine durante il rilevamento.
• Intervallo: da 0 a 100 pixel
• Predefinito: 25 pixel
Quando le AOI sono entro questo raggio l&apos;una dall&apos;altra:
• Vengono combinate in una singola AOI
• Il processo si ripete finché non restano vicini entro il raggio
• Valori più grandi: combina rilevamenti più distanti (meno AOI totali)
• Valori più piccoli: mantiene i rilevamenti separati (più AOI individuali)
Usa per consolidare rilevamenti raggruppati in singoli oggetti.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="209"/>
        <source>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</source>
        <translation>Formato per visualizzare le coordinate geografiche in tutta l&apos;applicazione.
Influisce su come le posizioni GPS sono mostrate nel visualizzatore e nelle esportazioni.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="225"/>
        <source>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</source>
        <translation>Seleziona il formato di visualizzazione delle coordinate geografiche:
• Lat/Long - Gradi Decimali: 34.123456, -118.987654 (più comune, facile da usare)
• Lat/Long - Gradi, Minuti, Secondi: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (navigazione tradizionale)
• UTM: sistema di griglia Universal Transverse Mercator con zona, est, nord (militare, topografia)
Questa impostazione influisce sulla visualizzazione delle coordinate nel visualizzatore, nelle esportazioni e nelle sovrapposizioni.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="233"/>
        <source>Lat/Long - Decimal Degrees</source>
        <translation>Lat/Long - Gradi Decimali</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="238"/>
        <source>Lat/Long - Degrees, Minutes, Seconds</source>
        <translation>Lat/Long - Gradi, Minuti, Secondi</translation>
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
        <translation>Unità per visualizzare le misure di temperatura da immagini termiche.
Usata quando si analizzano immagini termiche da camere termiche.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="278"/>
        <source>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</source>
        <translation>Seleziona l&apos;unità di temperatura per l&apos;analisi di immagini termiche:
• Fahrenheit (°F): scala imperiale della temperatura (standard USA)
  - L&apos;acqua congela a 32°F, bolle a 212°F
• Celsius (°C): scala metrica della temperatura (standard internazionale)
  - L&apos;acqua congela a 0°C, bolle a 100°C
Si applica alla visualizzazione dei dati della camera termica e ai risultati di analisi.</translation>
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
        <translation>Unità per visualizzare misure di distanza e altitudine.
Usata per altitudine del drone, distanze degli oggetti e calcoli spaziali.</translation>
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
        <translation>Seleziona l&apos;unità di distanza per le misurazioni:
• Metri (m): unità di distanza metrica (standard internazionale)
  - 1 metro = 3.281 piedi
  - Usato per altitudine, GSD e calcoli di distanza
• Piedi (ft): unità di distanza imperiale (standard USA)
  - 1 piede = 0.3048 metri
  - Comune in aviazione e topografia USA
Si applica alle visualizzazioni dell&apos;altitudine, ai calcoli GSD e alle misurazioni delle distanze.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="338"/>
        <source>Meters</source>
        <translation>Metri</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="343"/>
        <source>Feet</source>
        <translation>Piedi</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="362"/>
        <source>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</source>
        <translation>Attiva/disattiva la modalità Solo Offline.
Quando abilitata, l&apos;app salta tutte le chiamate di rete (tessere mappa, esportazioni CalTopo) e lavora solo con dati in cache.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="378"/>
        <source>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</source>
        <translation>Disabilita le funzionalità online (download tessere, integrazione CalTopo) e lavora completamente offline.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="381"/>
        <location filename="../resources/views/Preferences.ui" line="422"/>
        <source>Enable</source>
        <translation>Abilita</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="399"/>
        <source>Use terrain elevation data (DEM/DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online or local elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</source>
        <translation>Usa i dati di elevazione del terreno (DEM/DTM/DSM) per calcoli più accurati delle coordinate GPS delle AOI.
Quando abilitato, usa dati di elevazione online o locali per tenere conto delle variazioni del terreno.
Quando disabilitato, assume terreno piatto all&apos;altitudine di decollo.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="440"/>
        <source>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</source>
        <translation>Gestisci la cache dei dati di elevazione del terreno.
I tasselli del terreno vengono scaricati e memorizzati localmente per l&apos;uso offline.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="456"/>
        <source>0 tiles (0 MB)</source>
        <translation>0 tasselli (0 MB)</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="481"/>
        <source>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Cancella tutti i tasselli di elevazione del terreno memorizzati nella cache.
Ciò richiederà il nuovo download dei tasselli quando verrà utilizzata l&apos;elevazione del terreno.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="517"/>
        <source>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</source>
        <translation>Versione del file di configurazione del sensore drone corrente.
Contiene specifiche della camera, dimensioni del sensore e dati sulla lunghezza focale per diversi modelli di drone.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="546"/>
        <source>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</source>
        <translation>Numero di versione del file sensore drone attualmente caricato.
Il file sensore definisce i parametri della camera per calcoli accurati di GSD e AOI.</translation>
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
        <translation>Sostituisci il file di configurazione del sensore drone corrente.
Consente di aggiornare a una versione più recente o a specifiche sensore personalizzate.
Formato file richiesto: JSON con modelli di drone, sensori, lunghezze focali e dimensioni.
Usa questo quando:
• Sono disponibili nuovi modelli di drone
• Le specifiche del sensore devono essere aggiornate
• Sono necessarie configurazioni personalizzate della camera
Esegui un backup del file esistente prima di sostituirlo.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="609"/>
        <source>Close the Preferences window.
All changes are saved automatically when modified.</source>
        <translation>Chiudi la finestra Preferenze.
Tutte le modifiche vengono salvate automaticamente quando vengono modificate.</translation>
    </message>
</context>
<context>
    <name>QtImageViewer</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/QtImageViewer.py" line="384"/>
        <source>Open image</source>
        <translation>Apri immagine</translation>
    </message>
</context>
<context>
    <name>RXAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
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
        <translation>Numero di segmenti in cui dividere ogni immagine per l&apos;analisi.
L&apos;algoritmo RX analizza ogni segmento indipendentemente per rilevare anomalie locali.
Impatto sulle prestazioni:
• Numero di segmenti più alto: AUMENTA il tempo di elaborazione (più segmenti da analizzare)
• Numero di segmenti più basso: DIMINUISCE il tempo di elaborazione (meno segmenti da analizzare)
• 1 segmento: elaborazione più veloce (analizza l&apos;immagine intera una sola volta)
Un numero più alto di segmenti migliora il rilevamento in immagini con sfondi variabili.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Segmenti Immagine:</translation>
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
        <translation>Seleziona il numero di segmenti in cui dividere ogni immagine.
• Opzioni: 1, 2, 4, 6, 9, 16, 25, 36 segmenti
• Predefinito: 1 (analizza l&apos;immagine intera come un singolo segmento)
L&apos;algoritmo RX Anomaly usa analisi statistica per rilevare pixel insoliti:
• 1 segmento: analizza l&apos;intera immagine in una sola volta (ideale per immagini piccole)
• Più segmenti: analizza regioni locali indipendentemente (meglio per immagini grandi)
Un numero più alto di segmenti migliora il rilevamento in immagini con sfondi variabili.
Consigliato: 4-9 segmenti per immagini tipiche da drone.</translation>
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
        <translation>Sensibilità di rilevamento per l&apos;individuazione di anomalie.
• Intervallo: da 1 a 10
• Predefinito: 5
Controlla quanto un pixel deve essere statisticamente diverso dallo sfondo per essere rilevato:
• Valori più bassi (1-3): DIMINUISCONO i rilevamenti - meno sensibile, rileva solo anomalie marcate
• Valori più alti (7-10): AUMENTANO i rilevamenti - più sensibile, rileva anomalie sottili
Una sensibilità più alta trova più potenziali target ma può includere rumore/falsi positivi.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="146"/>
        <source>Sensitivity:</source>
        <translation>Sensibilità:</translation>
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
        <translation>Regola la sensibilità di rilevamento per l&apos;individuazione di anomalie.
• Intervallo: da 1 a 10
• Predefinito: 5
L&apos;algoritmo RX usa analisi statistica per trovare pixel che differiscono dallo sfondo:
• Valori più bassi (1-3): meno sensibile, rileva solo anomalie marcate (meno falsi positivi)
• Valori medi (4-6): rilevamento bilanciato (consigliato per la maggior parte dei casi)
• Valori più alti (7-10): più sensibile, rileva anomalie sottili (più rilevamenti, può includere rumore)
Le anomalie sono pixel statisticamente diversi dallo sfondo circostante.
Usa sensibilità più bassa per immagini pulite, più alta per trovare target sottili.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="205"/>
        <source>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</source>
        <translation>Livello di sensibilità corrente per il rilevamento di anomalie.
Visualizza il valore selezionato sul cursore di sensibilità (1-10).</translation>
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
        <translation>Le tue immagini contengono scene complesse con edifici, veicoli o coperture del terreno artificiali miste?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="49"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="64"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="100"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Quanto aggressivamente dovrebbe ADIAT cercare le anomalie?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="113"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta troverà più potenziali anomalie ma potrebbe anche aumentare i falsi positivi.</translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="50"/>
        <source>Very 
Conservative</source>
        <translation>Molto 
Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="51"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="52"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="53"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="54"/>
        <source>Very 
Aggressive</source>
        <translation>Molto 
Aggressivo</translation>
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
        <translation>&lt;br&gt;&lt;b&gt;Soglia:&lt;/b&gt; {value}</translation>
    </message>
</context>
<context>
    <name>RecentColorsDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="151"/>
        <source>Recent Colors</source>
        <translation>Colori Recenti</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="162"/>
        <source>Select a recently used color:</source>
        <translation>Seleziona un colore usato di recente:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="178"/>
        <source>No recent colors found</source>
        <translation>Nessun colore recente trovato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="204"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
<context>
    <name>RenderingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="44"/>
        <source>Shape Options</source>
        <translation>Opzioni Forma</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="47"/>
        <source>Shape Mode:</source>
        <translation>Modalità Forma:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="49"/>
        <source>Box</source>
        <translation>Riquadro</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="50"/>
        <source>Circle</source>
        <translation>Cerchio</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="51"/>
        <source>Dot</source>
        <translation>Punto</translation>
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
        <translation>Forma da disegnare attorno ai rilevamenti:

• Riquadro: rettangolo attorno al bounding box del rilevamento.
  Da usare per: confini precisi, visualizzazione tecnica.

• Cerchio: cerchio che racchiude il rilevamento (150% del raggio del contorno).
  Da usare per: uso generale, aspetto più pulito (predefinito).

• Punto: piccolo punto sul centroide del rilevamento.
  Da usare per: overlay minimale, rendering rapido.

• Off: nessun overlay di forma (solo miniature/testo se attivati).
  Da usare per: video puliti con overlay minimali.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="70"/>
        <source>Visual Options</source>
        <translation>Opzioni Visuali</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="73"/>
        <source>Show Text Labels (slower)</source>
        <translation>Mostra Etichette di Testo (più lento)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="75"/>
        <source>Displays text labels near detections showing detection information.
Adds ~5-15ms processing overhead depending on detection count.
Labels show: detection type, confidence, area.
Recommended: OFF for speed, ON for debugging/analysis.</source>
        <translation>Mostra etichette di testo accanto ai rilevamenti con le relative informazioni.
Aggiunge un sovraccarico di elaborazione di ~5-15 ms in base al numero di rilevamenti.
Le etichette mostrano: tipo di rilevamento, confidenza, area.
Consigliato: OFF per la velocità, ON per debug/analisi.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="82"/>
        <source>Show Contours (slowest)</source>
        <translation>Mostra Contorni (più lento di tutti)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="84"/>
        <source>Draws exact detection contours (pixel-precise boundaries).
Adds ~10-20ms processing overhead (very expensive).
Shows exact shape detected by algorithm.
Recommended: OFF for speed, ON only for detailed analysis.</source>
        <translation>Disegna i contorni esatti dei rilevamenti (confini precisi al pixel).
Aggiunge ~10-20 ms di sovraccarico (molto oneroso).
Mostra la forma esatta rilevata dall&apos;algoritmo.
Consigliato: OFF per la velocità, ON solo per analisi dettagliate.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="92"/>
        <source>Use Detection Color (hue @ 100% sat/val for color anomalies)</source>
        <translation>Usa Colore di Rilevamento (tonalità a 100% sat/val per le anomalie di colore)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="95"/>
        <source>Color the detection overlay based on detected color.
For color anomalies: Uses the detected hue at 100% saturation/value.
For motion detections: Uses default color (green/blue).
Helps visually identify what color was detected.
Recommended: ON for color detection, OFF for motion-only.</source>
        <translation>Colora l&apos;overlay del rilevamento in base al colore rilevato.
Per le anomalie di colore: usa la tonalità rilevata al 100% di saturazione/valore.
Per i rilevamenti di movimento: usa il colore predefinito (verde/blu).
Aiuta a identificare visivamente quale colore è stato rilevato.
Consigliato: ON per il rilevamento colore, OFF per il solo movimento.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="106"/>
        <source>Performance Limits</source>
        <translation>Limiti di Prestazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="109"/>
        <source>Max Detections:</source>
        <translation>Rilevamenti Massimi:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="115"/>
        <source>Maximum number of detections to render on screen (0-1000).
Prevents rendering slowdown when hundreds of detections occur.
Shows highest confidence detections first.
0 = Unlimited (may cause lag with many detections).
Recommended: 10 for general use, 50 for complex rendering (text+contours).</source>
        <translation>Numero massimo di rilevamenti da disegnare a schermo (0-1000).
Evita rallentamenti del rendering quando si verificano centinaia di rilevamenti.
Mostra prima i rilevamenti con maggior confidenza.
0 = illimitato (può causare lag con molti rilevamenti).
Consigliato: 10 per uso generale, 50 per rendering complessi (testo+contorni).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="126"/>
        <source>Temporal Voting</source>
        <translation>Voto Temporale</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="129"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Abilita Voto Temporale (riduce lo sfarfallio)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="132"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Smussa i rilevamenti tra i frame usando la consistenza temporale.
I rilevamenti devono comparire in N degli M frame consecutivi per essere confermati.
Riduce notevolmente i falsi positivi intermittenti.
Consigliato: ON in tutti i casi d&apos;uso (predefinito).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="142"/>
        <source>Window Frames (M):</source>
        <translation>Frame Finestra (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="147"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Dimensione della finestra di voto temporale (2-30 frame).
I rilevamenti devono comparire in N degli M frame consecutivi.
Valori più alti = memoria più lunga, più stabile, risposta più lenta ai nuovi oggetti.
Valori più bassi = memoria più breve, risposta più rapida, meno stabile.
Consigliato: 5 per 30 fps (finestra ~167 ms), 7 per 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="155"/>
        <source>Threshold (N of M):</source>
        <translation>Soglia (N su M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="160"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be ≤ Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Numero di frame, all&apos;interno della finestra, in cui il rilevamento deve comparire (N su M).
Valori più alti = più rigoroso, filtra i falsi positivi transitori.
Valori più bassi = più permissivo, risposta più rapida ai nuovi oggetti.
Deve essere ≤ Frame Finestra.
Consigliato: 3 su 5 (rilevamento nel 60% dei frame).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="173"/>
        <source>Detection Cleanup</source>
        <translation>Pulizia Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="177"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Abilita Filtro Rapporto d&apos;Aspetto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="180"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filtra i rilevamenti molto sottili o allungati in base a larghezza/altezza.
Utile per rimuovere fili, ombre allungate o altre forme non corrispondenti a oggetti.
La maggior parte degli utenti può lasciarlo OFF, a meno di rilevare molti falsi positivi sottili e allungati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="189"/>
        <source>Min Ratio:</source>
        <translation>Rapporto Min:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="195"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 ≈ reject if height is more than 5× width.</source>
        <translation>Rapporto larghezza/altezza minimo da mantenere (0,1-10,0).
Valori più bassi = consente rilevamenti più alti e sottili.
Valori più alti = richiede rilevamenti più simili a un quadrato.
Esempio: 0,2 ≈ rifiuta se l&apos;altezza è più di 5× la larghezza.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="202"/>
        <source>Max Ratio:</source>
        <translation>Rapporto Max:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="208"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Rapporto larghezza/altezza massimo da mantenere (0,1-20,0).
Valori più bassi = rifiuta i rilevamenti molto larghi e sottili.
Valori più alti = consente oggetti più larghi come veicoli o attrezzature lunghe.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="217"/>
        <source>Detection Clustering</source>
        <translation>Clustering Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="220"/>
        <source>Enable Detection Clustering</source>
        <translation>Abilita Clustering Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="223"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Unisce facoltativamente i rilevamenti vicini in un unico rilevamento più grande.
Utile quando un oggetto compare come molti piccoli rilevamenti adiacenti.
La maggior parte degli utenti può lasciarlo OFF, a meno che gli oggetti non appaiano frammentati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="232"/>
        <source>Clustering Distance (px):</source>
        <translation>Distanza Clustering (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="237"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Distanza massima tra i centri di rilevamento per unirli (0-500 pixel).
Valori più bassi = unisce solo rilevamenti molto vicini.
Valori più alti = unisce rilevamenti più distanti (può unire troppo).</translation>
    </message>
</context>
<context>
    <name>ResultsFolderDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="115"/>
        <source>Load Results Folder</source>
        <translation>Carica Cartella Risultati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="124"/>
        <source>Found {count} result(s)</source>
        <translation>Trovati {count} risultati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Folder</source>
        <translation>Cartella</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Images</source>
        <translation>Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Missing</source>
        <translation>Mancanti</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>AOIs</source>
        <translation>AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Map</source>
        <translation>Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>View</source>
        <translation>Visualizza</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="170"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="216"/>
        <source>Open in Google Maps</source>
        <translation>Apri in Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="226"/>
        <source>No images available - cannot get GPS location</source>
        <translation>Nessuna immagine disponibile - impossibile ottenere la posizione GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="228"/>
        <source>No GPS coordinates found in images</source>
        <translation>Nessuna coordinata GPS trovata nelle immagini</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="248"/>
        <source>Open in Results Viewer</source>
        <translation>Apri nel Visualizzatore Risultati</translation>
    </message>
</context>
<context>
    <name>ResultsLoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="29"/>
        <source>Loading Results</source>
        <translation>Caricamento risultati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="43"/>
        <source>Opening results...</source>
        <translation>Apertura risultati...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="55"/>
        <source>Preparing...</source>
        <translation>Preparazione...</translation>
    </message>
</context>
<context>
    <name>ReviewOrNewPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="70"/>
        <source>No file selected</source>
        <translation>Nessun file selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="114"/>
        <source>Select ADIAT Results File</source>
        <translation>Seleziona File Risultati ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>File XML (*.xml);;Tutti i File (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="126"/>
        <source>File Name Warning</source>
        <translation>Avviso Nome File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="128"/>
        <source>The selected file does not appear to be an ADIAT_Data.xml result or an ADIAT_Search project file.

Do you want to continue with this file?</source>
        <translation>Il file selezionato non sembra essere un risultato ADIAT_Data.xml né un file di progetto ADIAT_Search.

Vuoi continuare con questo file?</translation>
    </message>
</context>
<context>
    <name>ReviewerNameDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="25"/>
        <source>Reviewer Name</source>
        <translation>Nome Revisore</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="45"/>
        <source>Review Tracking</source>
        <translation>Tracciamento Revisione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="51"/>
        <source>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</source>
        <translation>Inserisci il tuo nome per tracciare la tua attività di revisione.
Questo aiuta a coordinare le revisioni tra più revisori.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="60"/>
        <source>Your Name:</source>
        <translation>Il tuo nome:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="64"/>
        <source>Enter your name</source>
        <translation>Inserisci il tuo nome</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="65"/>
        <source>Enter your full name or identifier for review tracking</source>
        <translation>Inserisci il tuo nome completo o un identificativo per il tracciamento della revisione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="71"/>
        <source>Remember my name</source>
        <translation>Ricorda il mio nome</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="74"/>
        <source>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</source>
        <translation>Salva il tuo nome per future sessioni di revisione.
Puoi cambiarlo più avanti nelle Preferenze o cliccando il nome del revisore nel visualizzatore.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="86"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="91"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="123"/>
        <source>Name Required</source>
        <translation>Nome Richiesto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="124"/>
        <source>Please enter your name to continue.</source>
        <translation>Inserisci il tuo nome per continuare.</translation>
    </message>
</context>
<context>
    <name>ScanProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="51"/>
        <source>Scanning for Results</source>
        <translation>Scansione dei Risultati</translation>
    </message>
</context>
<context>
    <name>SimilarityGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="172"/>
        <source>Reference</source>
        <translation>Riferimento</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="181"/>
        <source>Unknown</source>
        <translation>Sconosciuto</translation>
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
        <translation>Coordinate GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="45"/>
        <source>Relative Altitude</source>
        <translation>Altitudine Relativa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="46"/>
        <source>Gimbal Orientation</source>
        <translation>Orientamento Gimbal</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="47"/>
        <source>Estimated Average GSD</source>
        <translation>GSD Medio Stimato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="48"/>
        <source>Temperature</source>
        <translation>Temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="49"/>
        <source>Color Values</source>
        <translation>Valori Colore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="50"/>
        <source>Drone Orientation</source>
        <translation>Orientamento Drone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="51"/>
        <source>Grid Review</source>
        <translation>Revisione a griglia</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="116"/>
        <source>Error Loading Images</source>
        <translation>Errore nel Caricamento delle Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="122"/>
        <source>No active images available.</source>
        <translation>Nessuna immagine attiva disponibile.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="126"/>
        <source>No other images available.</source>
        <translation>Nessun&apos;altra immagine disponibile.</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="90"/>
        <source>Are you primarily looking for a person?</source>
        <translation>Stai cercando principalmente una persona?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="156"/>
        <source>Do you know a distinctive target color?</source>
        <translation>Conosci un colore distintivo del target?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Rilevamento Colore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Rilevamento Anomalie Colore &amp; Movimento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>Rilevatore Persone AI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="186"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Algoritmo Selezionato: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="191"/>
        <source>{result}
Secondary Recommendation: {secondary}</source>
        <translation>{result}
Raccomandazione secondaria: {secondary}</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Rilevamento Colore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Rilevamento Anomalie Colore &amp; Movimento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>Rilevatore Persone AI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="190"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="192"/>
        <source>{algorithm} Parameters</source>
        <translation>Parametri {algorithm}</translation>
    </message>
</context>
<context>
    <name>StreamConnectionPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="92"/>
        <source>Click Scan to find devices...</source>
        <translation>Clicca Scansiona per trovare i dispositivi...</translation>
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
        <translation>Scegli il file video che vuoi analizzare. Usa Sfoglia per scegliere un file dal disco.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="268"/>
        <source>Video File:</source>
        <translation>File Video:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="269"/>
        <source>Click Browse to select a video file...</source>
        <translation>Clicca Sfoglia per selezionare un file video...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="275"/>
        <source>Click Scan to detect available capture devices, then select one from the dropdown.</source>
        <translation>Clicca su Scansiona per rilevare i dispositivi di acquisizione disponibili e seleziona quello desiderato dal menu a discesa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="277"/>
        <source>Device:</source>
        <translation>Dispositivo:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="278"/>
        <source></source>
        <translation></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="298"/>
        <source>OpenCV not available</source>
        <translation>OpenCV non disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="304"/>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="307"/>
        <source>Scanning...</source>
        <translation>Scansione in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="331"/>
        <source>Scan</source>
        <translation>Scansiona</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="337"/>
        <source>No capture devices found</source>
        <translation>Nessun dispositivo di acquisizione trovato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="344"/>
        <source>Device {index} ({backend})</source>
        <translation>Dispositivo {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="284"/>
        <source>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</source>
        <translation>Inserisci l&apos;URL RTMP fornito dal tuo server di streaming (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="286"/>
        <source>Stream URL:</source>
        <translation>URL Stream:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="287"/>
        <source>rtmp://server:port/app/streamKey</source>
        <translation>rtmp://server:port/app/streamKey</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="383"/>
        <source>Select Video File</source>
        <translation>Seleziona File Video</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="386"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</source>
        <translation>File Video (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;Tutti i File (*)</translation>
    </message>
</context>
<context>
    <name>StreamControlWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="827"/>
        <source>Stream Connection</source>
        <translation>Connessione Stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="829"/>
        <source>Configure and connect to video source (file, HDMI capture, or RTMP stream)</source>
        <translation>Configura e connettiti alla sorgente video (file, acquisizione HDMI o stream RTMP)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="834"/>
        <source>Stream Type:</source>
        <translation>Tipo Stream:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="836"/>
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="837"/>
        <source>HDMI Capture</source>
        <translation>Acquisizione HDMI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="838"/>
        <source>RTMP Stream</source>
        <translation>Stream RTMP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="841"/>
        <source>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</source>
        <translation>Seleziona il tipo di sorgente video:
• File: File video preregistrato con controlli timeline
• Acquisizione HDMI: Acquisizione dal vivo da dispositivo di acquisizione HDMI
• Stream RTMP: Streaming in tempo reale da sorgente RTMP/HTTP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="850"/>
        <source>Stream URL/Path:</source>
        <translation>URL/Percorso Stream:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="857"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1056"/>
        <source>Click to browse for video file...</source>
        <translation>Clicca per sfogliare il file video...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="861"/>
        <source>Enter or browse for the video source:
• File: Click to browse for video file (MP4, AVI, MOV, etc.)
• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)</source>
        <translation>Inserisci o sfoglia per la sorgente video:
• File: Clicca per sfogliare il file video (MP4, AVI, MOV, ecc.)
• Stream RTMP: Inserisci l&apos;URL RTMP (rtmp://server:port/app/stream)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="870"/>
        <source>Select HDMI capture device</source>
        <translation>Seleziona dispositivo di acquisizione HDMI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="872"/>
        <source>Scanning for devices...</source>
        <translation>Scansione dispositivi...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="876"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1008"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="880"/>
        <source>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</source>
        <translation>Apri il browser dei file per selezionare un file video per l&apos;analisi.
Formati supportati: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="887"/>
        <source>Scan...</source>
        <translation>Scansiona...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="889"/>
        <source>Scan for available HDMI capture devices</source>
        <translation>Scansiona i dispositivi di acquisizione HDMI disponibili</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="896"/>
        <source>Connect</source>
        <translation>Connetti</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="899"/>
        <source>Connect to the specified video source and begin processing.</source>
        <translation>Connettiti alla sorgente video specificata e inizia l&apos;elaborazione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="901"/>
        <source>Disconnect</source>
        <translation>Disconnetti</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="905"/>
        <source>Disconnect from the current video source and stop processing.</source>
        <translation>Disconnettiti dalla sorgente video corrente e interrompi l&apos;elaborazione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="912"/>
        <source>Status: Disconnected</source>
        <translation>Stato: Disconnesso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="914"/>
        <source>Current connection status</source>
        <translation>Stato della connessione corrente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="917"/>
        <source>Performance</source>
        <translation>Prestazioni</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="918"/>
        <source>Real-time performance metrics</source>
        <translation>Metriche di prestazioni in tempo reale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="922"/>
        <source>Video: --</source>
        <translation>Video: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="923"/>
        <source>Original video resolution</source>
        <translation>Risoluzione video originale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="924"/>
        <source>Processing: --</source>
        <translation>Elaborazione: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="926"/>
        <source>Resolution used for detection processing</source>
        <translation>Risoluzione usata per l&apos;elaborazione del rilevamento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="930"/>
        <source>Source FPS: --</source>
        <translation>FPS Sorgente: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="931"/>
        <source>Source frame rate and the applied processing cadence</source>
        <translation>Frame rate della sorgente e cadenza di elaborazione applicata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="932"/>
        <source>Proc FPS: --</source>
        <translation>FPS Elaborazione: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="934"/>
        <source>Actual frames per second being processed</source>
        <translation>Fotogrammi al secondo effettivamente elaborati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="938"/>
        <source>Time: -- ms</source>
        <translation>Tempo: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="940"/>
        <source>Time in milliseconds to process each frame</source>
        <translation>Tempo in millisecondi per elaborare ogni fotogramma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="942"/>
        <source>Latency: -- ms</source>
        <translation>Latenza: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="944"/>
        <source>End-to-end latency from frame capture to display</source>
        <translation>Latenza end-to-end dalla cattura del fotogramma alla visualizzazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="948"/>
        <source>Frames: --</source>
        <translation>Fotogrammi: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="949"/>
        <source>Total number of frames processed</source>
        <translation>Numero totale di fotogrammi elaborati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="950"/>
        <source>Detections: --</source>
        <translation>Rilevamenti: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="951"/>
        <source>Number of detections in current frame</source>
        <translation>Numero di rilevamenti nel fotogramma corrente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="965"/>
        <source>Recording</source>
        <translation>Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="970"/>
        <source>Start Recording</source>
        <translation>Avvia Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="973"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Avvia la registrazione dello stream video con sovrapposizioni di rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="975"/>
        <source>Stop Recording</source>
        <translation>Interrompi Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="978"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Interrompi la registrazione corrente e salva su file.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="985"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1173"/>
        <source>Status: Not Recording</source>
        <translation>Stato: Non in Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="988"/>
        <source>Current recording status and output file path</source>
        <translation>Stato di registrazione corrente e percorso del file di output</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="992"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1180"/>
        <source>Duration: --</source>
        <translation>Durata: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="994"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Statistiche registrazione: Durata, FPS, Fotogrammi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1003"/>
        <source>Save to:</source>
        <translation>Salva in:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1006"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Cartella in cui verranno salvate le registrazioni video.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1010"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Scegli una cartella per salvare le registrazioni.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1064"/>
        <source>rtmp://server:port/app/stream</source>
        <translation>rtmp://server:port/app/stream</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1081"/>
        <source>Invalid Device</source>
        <translation>Dispositivo Non Valido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1082"/>
        <source>Please select a valid HDMI capture device.</source>
        <translation>Seleziona un dispositivo di acquisizione HDMI valido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1094"/>
        <source>Invalid URL</source>
        <translation>URL Non Valido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1095"/>
        <source>Please enter a valid stream URL.</source>
        <translation>Inserisci un URL stream valido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1112"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1125"/>
        <source>Status: {message}</source>
        <translation>Stato: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1161"/>
        <source>Status: Recording</source>
        <translation>Stato: Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1165"/>
        <source>Output: {value}</source>
        <translation>Output: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1177"/>
        <source>Duration: {value}</source>
        <translation>Durata: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1206"/>
        <source>Select Recording Directory</source>
        <translation>Seleziona Cartella Registrazioni</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1217"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1220"/>
        <source>Scanning...</source>
        <translation>Scansione in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1244"/>
        <source>Scan</source>
        <translation>Scansiona</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1257"/>
        <source>Device {index} ({backend})</source>
        <translation>Dispositivo {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1310"/>
        <source>Source FPS: {source:.1f} (Applied {applied:.1f})</source>
        <translation>FPS Sorgente: {source:.1f} (Applicati {applied:.1f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1317"/>
        <source>Source FPS: {fps:.1f}</source>
        <translation>FPS Sorgente: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1250"/>
        <source>No capture devices found</source>
        <translation>Nessun dispositivo di acquisizione trovato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1287"/>
        <source>Video: {width}x{height}</source>
        <translation>Video: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1294"/>
        <source>Processing: {width}x{height}</source>
        <translation>Elaborazione: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1320"/>
        <source>Proc FPS: {fps:.1f}</source>
        <translation>FPS Elaborazione: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1328"/>
        <source>Time: {time:.1f} ms</source>
        <translation>Tempo: {time:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1331"/>
        <source>Latency: {latency:.1f} ms</source>
        <translation>Latenza: {latency:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1339"/>
        <source>Frames: {count}</source>
        <translation>Fotogrammi: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1342"/>
        <source>Detections: {count}</source>
        <translation>Rilevamenti: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1349"/>
        <source>Select Video File</source>
        <translation>Seleziona File Video</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1352"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</source>
        <translation>File Video (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;Tutti i File (*)</translation>
    </message>
</context>
<context>
    <name>StreamImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="66"/>
        <source>Select Drone/Camera</source>
        <translation>Seleziona Drone/Fotocamera</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="70"/>
        <source>No drones available</source>
        <translation>Nessun drone disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="112"/>
        <source>Other</source>
        <translation>Altro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="148"/>
        <source>Error loading drone data</source>
        <translation>Errore nel caricamento dei dati del drone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="222"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (Dati fotocamera non validi)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="423"/>
        <source>{sensor_name}: Sensor dimensions not available</source>
        <translation>{sensor_name}: dimensioni del sensore non disponibili</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="430"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (Dati fotocamera mancanti)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="431"/>
        <source>Unable to calculate GSD. Sensor dimensions are required.</source>
        <translation>Impossibile calcolare il GSD. Sono richieste le dimensioni del sensore.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="437"/>
        <source>-- (Error)</source>
        <translation>-- (Errore)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="468"/>
        <source>Sensor {n}</source>
        <translation>Sensore {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="470"/>
        <source>Primary</source>
        <translation>Principale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="472"/>
        <source>Sensor</source>
        <translation>Sensore</translation>
    </message>
</context>
<context>
    <name>StreamTargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Cappello, Casco, Sacchetto di plastica</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Gatto, Zaino da giorno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Zaino grande, Cane medio</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Sacco a pelo, Cane grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Barca piccola, Tenda da 2 persone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Auto/SUV, Pickup piccolo, Tenda grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Casa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Altri esempi:</translation>
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
    <name>StreamViewerWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="102"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Strumento Automatico di Analisi Immagini Drone v{version} - Sponsorizzato da TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="214"/>
        <source>Live View</source>
        <translation>Vista Live</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="219"/>
        <source>Gallery</source>
        <translation>Galleria</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="260"/>
        <source>Menu</source>
        <translation>Menu</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="261"/>
        <source>Streaming Analysis Wizard</source>
        <translation>Procedura guidata Analisi Streaming</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="262"/>
        <source>Image Analysis</source>
        <translation>Analisi Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="263"/>
        <source>Flight Viewer</source>
        <translation>Visore voli</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="264"/>
        <source>Preferences</source>
        <translation>Preferenze</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="274"/>
        <source>Help</source>
        <translation>Aiuto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="275"/>
        <source>Check for Updates</source>
        <translation>Verifica Aggiornamenti</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="276"/>
        <source>Manual</source>
        <translation>Manuale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="277"/>
        <source>Community Forum</source>
        <translation>Forum della Comunità</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="278"/>
        <source>YouTube Channel</source>
        <translation>Canale YouTube</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="305"/>
        <source>Start Recording</source>
        <translation>Avvia Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="308"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Avvia la registrazione dello stream video con sovrapposizioni di rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="310"/>
        <source>Stop Recording</source>
        <translation>Interrompi Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="313"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Interrompi la registrazione corrente e salva su file.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="320"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1881"/>
        <source>Status: Not Recording</source>
        <translation>Stato: Non in Registrazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="323"/>
        <source>Current recording status and output file path</source>
        <translation>Stato di registrazione corrente e percorso del file di output</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="327"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1883"/>
        <source>Duration: --</source>
        <translation>Durata: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="329"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Statistiche registrazione: Durata, FPS, Fotogrammi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="334"/>
        <source>Save to:</source>
        <translation>Salva in:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="338"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Cartella in cui verranno salvate le registrazioni video.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="340"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="342"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Scegli una cartella per salvare le registrazioni.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="393"/>
        <source>Select Recording Directory</source>
        <translation>Seleziona Cartella Registrazioni</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="413"/>
        <source>Algorithm:</source>
        <translation>Algoritmo:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="415"/>
        <source>Select which streaming detection algorithm to use</source>
        <translation>Seleziona quale algoritmo di rilevamento in streaming utilizzare</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="421"/>
        <source>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</source>
        <translation>Scegli quale algoritmo di rilevamento in streaming eseguire.
• Rilevamento Anomalie Colore &amp; Movimento: rilevatori di anomalie combinati
• Rilevamento Colore: evidenziazione basata sul colore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="456"/>
        <source>Gallery Threshold:</source>
        <translation>Soglia Galleria:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="459"/>
        <source>Number of frames a detection must be seen before appearing in the Gallery tab</source>
        <translation>Numero di fotogrammi in cui un rilevamento deve essere visto prima di apparire nella scheda Galleria</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="466"/>
        <source> frames</source>
        <translation> fotogrammi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="469"/>
        <source>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</source>
        <translation>I rilevamenti devono essere visti per questo numero di fotogrammi consecutivi
prima di apparire nella Galleria. Valori più alti riducono
i falsi positivi ma ritardano la comparsa del rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="530"/>
        <source>Device {index}</source>
        <translation>Dispositivo {index}</translation>
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
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="725"/>
        <source>Failed to open Streaming Analysis Guide:
{error}</source>
        <translation>Impossibile aprire la Guida Analisi Streaming:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="744"/>
        <source>Failed to open Image Analysis:
{error}</source>
        <translation>Impossibile aprire Analisi Immagini:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="758"/>
        <source>Failed to open Preferences:
{error}</source>
        <translation>Impossibile aprire Preferenze:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="781"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>Impossibile aprire il Visore voli:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="795"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Impossibile aprire la documentazione di aiuto:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="809"/>
        <source>Failed to open Community Forum:
{error}</source>
        <translation>Impossibile aprire il Forum della Comunità:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="823"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Impossibile aprire il Canale YouTube:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="934"/>
        <source>Loaded: {algorithm}</source>
        <translation>Caricato: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="950"/>
        <source>Error loading algorithm: {error}</source>
        <translation>Errore nel caricamento dell&apos;algoritmo: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="954"/>
        <source>Algorithm Load Error</source>
        <translation>Errore Caricamento Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1462"/>
        <source>Algorithm switched to {label}</source>
        <translation>Algoritmo cambiato in {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1512"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1589"/>
        <source>No Stream Connected</source>
        <translation>Nessuno Stream Connesso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1529"/>
        <source>{state} - {message}</source>
        <translation>{state} - {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1530"/>
        <source>Connected</source>
        <translation>Connesso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1530"/>
        <source>Disconnected</source>
        <translation>Disconnesso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1542"/>
        <source>✓ Connected: {message}</source>
        <translation>✓ Connesso: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1571"/>
        <source>✗ Disconnected: {message}</source>
        <translation>✗ Disconnesso: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1780"/>
        <source>No detections found.</source>
        <translation>Nessun rilevamento trovato.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1784"/>
        <source>Detection Results ({count} found):</source>
        <translation>Risultati Rilevamento ({count} trovati):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1796"/>
        <source>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</source>
        <translation>#{index}: Tipo({cls}) Pos({x},{y}) Dim({w}x{h})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1806"/>
        <source>#{index}: Type({cls})</source>
        <translation>#{index}: Tipo({cls})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1811"/>
        <source> Conf({confidence:.2f})</source>
        <translation> Conf({confidence:.2f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1856"/>
        <source>Recording started: {path}</source>
        <translation>Registrazione avviata: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1863"/>
        <source>Recording stopped</source>
        <translation>Registrazione interrotta</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1877"/>
        <source>Status: Recording to {path}</source>
        <translation>Stato: Registrazione su {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1897"/>
        <source>Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}</source>
        <translation>Durata: {duration:.1f}s | FPS: {fps:.1f} | Frame: {frames} | Coda: {queue}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1915"/>
        <source>✗ Error: {error}</source>
        <translation>✗ Errore: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1982"/>
        <source>Live Stream</source>
        <translation>Stream Live</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1984"/>
        <source>Cannot seek in live stream.

Detection was first seen at frame {frame}.</source>
        <translation>Impossibile spostarsi nello stream live.

Il rilevamento è stato visto per la prima volta al fotogramma {frame}.</translation>
    </message>
</context>
<context>
    <name>StreamingGuide</name>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="14"/>
        <source>Streaming Setup Guide</source>
        <translation>Guida Configurazione Streaming</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="51"/>
        <source>Connect to Your Stream</source>
        <translation>Connettiti al tuo stream</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="115"/>
        <source>Pre-recorded video file with playback controls</source>
        <translation>File video preregistrato con controlli di riproduzione</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="122"/>
        <source>File</source>
        <translation>File</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="161"/>
        <source>Live HDMI capture device (enter device index)</source>
        <translation>Dispositivo di acquisizione HDMI live (inserisci indice dispositivo)</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="168"/>
        <source>HDMI</source>
        <translation>HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="204"/>
        <source>Network stream via RTMP URL</source>
        <translation>Stream di rete tramite URL RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="211"/>
        <source>RTMP</source>
        <translation>RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="254"/>
        <source>File: Use local video files (MP4, MOV, etc.) with timeline controls.</source>
        <translation>File: usa file video locali (MP4, MOV, ecc.) con controlli timeline.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="269"/>
        <source>HDMI: Connect to a live HDMI capture device.</source>
        <translation>HDMI: connettiti a un dispositivo di acquisizione HDMI live.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="284"/>
        <source>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</source>
        <translation>RTMP: connettiti a uno stream di rete live (rtmp://server:port/app/key).</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="328"/>
        <source>Connection Details</source>
        <translation>Dettagli Connessione</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="347"/>
        <source>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</source>
        <translation>Fornisci il percorso o l&apos;URL per il tipo di stream selezionato. Puoi opzionalmente connetterti automaticamente quando la guida è finita.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="364"/>
        <source>Stream URL/Path:</source>
        <translation>URL/Percorso Stream:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="373"/>
        <source>Click Browse to select a file or enter a URL...</source>
        <translation>Clicca Sfoglia per selezionare un file o inserire un URL...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="385"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="399"/>
        <source>Auto Connect:</source>
        <translation>Connessione Automatica:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="411"/>
        <source>Connect as soon as the guide finishes</source>
        <translation>Connetti non appena la guida termina</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="423"/>
        <source>Capture Devices:</source>
        <translation>Dispositivi di Acquisizione:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="444"/>
        <source>Scan...</source>
        <translation>Scansiona...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="484"/>
        <source>Processing Resolution:</source>
        <translation>Risoluzione Elaborazione:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="532"/>
        <source>Video Capture Information</source>
        <translation>Informazioni Acquisizione Video</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="554"/>
        <source>What drone/camera was used to capture the video?</source>
        <translation>Quale drone/telecamera è stata utilizzata per acquisire il video?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="584"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>A quale altitudine dal livello del suolo (AGL) volava il drone?</translation>
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
        <translation>Distanza di campionamento al suolo (GSD) stimata:</translation>
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
        <translation>Dimensione target di ricerca</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="774"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>Quanto sono approssimativamente grandi gli oggetti che vuoi identificare?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="805"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Altri esempi:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 ft² – Cappello, Casco, Sacchetto di plastica &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 ft² – Gatto, Zaino da giorno &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 ft² – Zaino grande, Cane medio &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 ft² – Sacco a pelo, Cane grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 ft² – Barca piccola, Tenda da 2 persone &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 ft² – Auto/SUV, Pickup piccolo, Tenda grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 ft² – Casa &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="847"/>
        <source>Detection &amp; Processing</source>
        <translation>Rilevamento e Elaborazione</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="869"/>
        <source>Are you looking for specific colors?</source>
        <translation>Stai cercando colori specifici?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="914"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="945"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1018"/>
        <source>Reset</source>
        <translation>Reimposta</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1091"/>
        <source>Algorithm Parameters</source>
        <translation>Parametri Algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1126"/>
        <source>Close</source>
        <translation>Chiudi</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1138"/>
        <source>Skip this streaming guide next time</source>
        <translation>Salta questa guida streaming la prossima volta</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1166"/>
        <source>Back</source>
        <translation>Indietro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="138"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1178"/>
        <source>Continue</source>
        <translation>Continua</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="84"/>
        <source>ADIAT Streaming Setup Guide</source>
        <translation>Guida Configurazione Streaming ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="136"/>
        <source>Open Stream Viewer</source>
        <translation>Apri Visualizzatore Stream</translation>
    </message>
</context>
<context>
    <name>StreamingVideoDisplay</name>
    <message>
        <location filename="../app/core/views/streaming/components/StreamingVideoDisplay.py" line="66"/>
        <source>No Stream Connected</source>
        <translation>Nessuno Stream Connesso</translation>
    </message>
</context>
<context>
    <name>TargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Cappello, Casco, Sacchetto di plastica</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Gatto, Zaino da giorno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Zaino grande, Cane medio</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Sacco a pelo, Cane grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Barca piccola, Tenda da 2 persone</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Auto/SUV, Pickup piccolo, Tenda grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Casa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Altri esempi:</translation>
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
        <translation>Nessun AOI Contrassegnato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="49"/>
        <source>There are no flagged AOIs to assign.

Flag at least one AOI in the viewer before using Plan Verification.</source>
        <translation>Non ci sono AOI contrassegnati da assegnare.

Contrassegna almeno un AOI nel visualizzatore prima di usare Pianifica Verifiche.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="210"/>
        <source>No Team Selected</source>
        <translation>Nessuna Squadra Selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="211"/>
        <source>Select a target team (or &apos;Unassigned&apos;) in the list first.</source>
        <translation>Seleziona prima una squadra di destinazione (o &apos;Non assegnati&apos;) nella lista.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="219"/>
        <source>No AOIs Selected</source>
        <translation>Nessun AOI Selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="221"/>
        <source>Select one or more AOIs on the map first.
Click on markers, or use Rectangle Select for area selection.</source>
        <translation>Seleziona prima uno o più AOI sulla mappa.
Clicca sui marker, oppure usa la Selezione Rettangolare per selezionare un&apos;area.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="300"/>
        <source>No AOIs</source>
        <translation>Nessun AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="301"/>
        <source>Team &apos;{name}&apos; has no assigned AOIs.</source>
        <translation>La squadra &apos;{name}&apos; non ha AOI assegnati.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="312"/>
        <source>Save Team PDF</source>
        <translation>Salva PDF Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="314"/>
        <source>PDF files (*.pdf)</source>
        <translation>File PDF (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="326"/>
        <source>Select Export Folder</source>
        <translation>Seleziona Cartella di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="336"/>
        <source>Exporting Team PDFs</source>
        <translation>Esportazione PDF Squadre</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="354"/>
        <source>Generating PDF for {name}...</source>
        <translation>Generazione PDF per {name}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="365"/>
        <source>Generating master summary...</source>
        <translation>Generazione riepilogo generale...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="373"/>
        <source>Export complete</source>
        <translation>Esportazione completata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="406"/>
        <source>Generating PDF Report</source>
        <translation>Generazione Report PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="414"/>
        <source>Done</source>
        <translation>Completato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="418"/>
        <source>Success</source>
        <translation>Successo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="419"/>
        <source>PDF report generated successfully!</source>
        <translation>Report PDF generato con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="380"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="426"/>
        <source>Export Error</source>
        <translation>Errore di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="381"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="427"/>
        <source>PDF generation failed: {error}</source>
        <translation>Generazione PDF fallita: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="389"/>
        <source>Export Complete</source>
        <translation>Esportazione Completata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="390"/>
        <source>Team PDFs saved to:
{folder}</source>
        <translation>PDF delle squadre salvati in:
{folder}</translation>
    </message>
</context>
<context>
    <name>TeamPlanningDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="55"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="65"/>
        <source>Plan Verification</source>
        <translation>Pianifica Verifiche</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="122"/>
        <source>Teams</source>
        <translation>Squadre</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="124"/>
        <source>+ New</source>
        <translation>+ Nuova</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="125"/>
        <source>Create a new field team</source>
        <translation>Crea una nuova squadra di verifica</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="127"/>
        <source>✕ Remove</source>
        <translation>✕ Rimuovi</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="128"/>
        <source>Remove the selected team</source>
        <translation>Rimuovi la squadra selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="143"/>
        <source>Assign Selection ▶</source>
        <translation>Assegna Selezione ▶</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="145"/>
        <source>Assign the selected AOIs on the map to the chosen team</source>
        <translation>Assegna gli AOI selezionati sulla mappa alla squadra scelta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="158"/>
        <source>Team AOIs</source>
        <translation>AOI della Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="172"/>
        <source>Export Team PDF</source>
        <translation>Esporta PDF Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="174"/>
        <source>Generate a PDF report for the selected team only</source>
        <translation>Genera un report PDF solo per la squadra selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="179"/>
        <source>Export All PDFs</source>
        <translation>Esporta Tutti i PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="181"/>
        <source>Generate one PDF per team plus a master summary PDF</source>
        <translation>Genera un PDF per squadra più un PDF riepilogativo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="86"/>
        <source>Zoom In (+)</source>
        <translation>Ingrandisci (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="88"/>
        <source>Zoom Out (-)</source>
        <translation>Riduci (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="90"/>
        <source>Fit All (F)</source>
        <translation>Adatta Tutto (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="93"/>
        <source>Rectangle Select</source>
        <translation>Selezione Rettangolare</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="96"/>
        <source>Draw a rectangle on the map to select multiple AOIs</source>
        <translation>Disegna un rettangolo sulla mappa per selezionare più AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="316"/>
        <source>Satellite View</source>
        <translation>Vista Satellite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="313"/>
        <source>Map View</source>
        <translation>Vista Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="195"/>
        <source>Click to select AOI • Ctrl+Click to multi-select • Use Rectangle Select for area selection • Scroll to zoom</source>
        <translation>Clicca per selezionare AOI • Ctrl+Clic per selezione multipla • Usa Selezione Rettangolare per selezione area • Scorri per zoom</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="222"/>
        <source>Team</source>
        <translation>Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>New Team</source>
        <translation>Nuova Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>Team name:</source>
        <translation>Nome squadra:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="246"/>
        <source>Duplicate Name</source>
        <translation>Nome Duplicato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="247"/>
        <source>A team named &apos;{name}&apos; already exists.</source>
        <translation>Una squadra chiamata &apos;{name}&apos; esiste già.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="265"/>
        <source>Unassigned</source>
        <translation>Non assegnati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="298"/>
        <source>No Team Selected</source>
        <translation>Nessuna Squadra Selezionata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="299"/>
        <source>Please select a team to export.</source>
        <translation>Seleziona una squadra da esportare.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="305"/>
        <source>No Teams</source>
        <translation>Nessuna Squadra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="306"/>
        <source>Create at least one team before exporting.</source>
        <translation>Crea almeno una squadra prima di esportare.</translation>
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
        <translation>dati vecchi {age}s</translation>
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
        <translation>Molto Conservativo</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="239"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="240"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="241"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="242"/>
        <source>Very Aggressive</source>
        <translation>Molto Aggressivo</translation>
    </message>
</context>
<context>
    <name>ThermalAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="29"/>
        <source>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</source>
        <translation>Tipo di anomalia termica da rilevare nelle immagini termiche.
Determina se trovare punti caldi, punti freddi o entrambi.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Tipo di Anomalia:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="45"/>
        <source>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</source>
        <translation>Seleziona il tipo di anomalia termica da rilevare:
• Sopra o Sotto la Media: rileva sia anomalie calde che fredde (predefinito)
• Sopra la Media: rileva solo punti caldi (temperature sopra la media)
• Sotto la Media: rileva solo punti freddi (temperature sotto la media)
L&apos;algoritmo confronta la temperatura di ogni pixel con la temperatura media del suo segmento.
Usa &quot;Sopra la Media&quot; per trovare fonti di calore, &quot;Sotto la Media&quot; per oggetti freddi.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="54"/>
        <source>Above or Below Mean</source>
        <translation>Sopra o Sotto la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="59"/>
        <source>Above Mean</source>
        <translation>Sopra la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="64"/>
        <source>Below Mean</source>
        <translation>Sotto la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="77"/>
        <source>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</source>
        <translation>Soglia di temperatura per rilevare anomalie termiche.
Misurata in deviazioni standard dalla temperatura media.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="81"/>
        <source>Anomaly Threshold:</source>
        <translation>Soglia Anomalia:</translation>
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
        <translation>Imposta la soglia di rilevamento delle anomalie in deviazioni standard.
• Intervallo: da 0 a 7 deviazioni standard
• Predefinito: 4
Definisce quanto una temperatura deve differire dalla media per essere rilevata:
• Valori più bassi (1-2): molto sensibile, rileva sottili differenze di temperatura (più rilevamenti)
• Valori medi (3-5): rilevamento bilanciato (consigliato per la maggior parte dei casi)
• Valori più alti (6-7): rileva solo differenze di temperatura estreme (meno rilevamenti)
Esempio: valore 4 rileva pixel 4 deviazioni standard sopra/sotto la temperatura media.</translation>
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
        <translation>Numero di segmenti in cui dividere ogni immagine termica per l&apos;analisi.
Ogni segmento viene analizzato indipendentemente per anomalie termiche locali.
Impatto sulle prestazioni:
• Numero di segmenti più alto: AUMENTA il tempo di elaborazione (più segmenti da analizzare)
• Numero di segmenti più basso: DIMINUISCE il tempo di elaborazione (meno segmenti da analizzare)
• 1 segmento: elaborazione più veloce (analizza l&apos;immagine intera una sola volta)
Un numero più alto di segmenti migliora il rilevamento in scene con gradienti di temperatura.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="122"/>
        <source>Image Segments:</source>
        <translation>Segmenti Immagine:</translation>
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
        <translation>Seleziona il numero di segmenti in cui dividere ogni immagine termica.
• Opzioni: 1, 2, 4, 6, 9, 16, 25, 36 segmenti
• Predefinito: 1 (analizza l&apos;immagine intera come un singolo segmento)
L&apos;algoritmo calcola la temperatura media per ogni segmento in modo indipendente:
• 1 segmento: analisi della temperatura globale (ideale per scene uniformi)
• Più segmenti: analisi della temperatura locale (meglio per sfondi variabili)
Un numero più alto di segmenti migliora il rilevamento in scene con gradienti di temperatura.
Consigliato: 4-9 segmenti per immagini termiche tipiche da drone.</translation>
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
        <translation>Le tue immagini contengono scene complesse con edifici, veicoli o coperture del terreno artificiali miste?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="57"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="72"/>
        <source>Yes</source>
        <translation>Sì</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="105"/>
        <source>What type of anomalies are you looking for?</source>
        <translation>Che tipo di anomalie stai cercando?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="122"/>
        <source>Warmer than surroundings</source>
        <translation>Più caldo dell&apos;ambiente circostante</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="134"/>
        <source>Cooler than surroundings</source>
        <translation>Più freddo dell&apos;ambiente circostante</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="146"/>
        <source>Both</source>
        <translation>Entrambi</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="185"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Quanto aggressivamente dovrebbe ADIAT cercare le anomalie?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="198"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta troverà più potenziali anomalie ma potrebbe anche aumentare i falsi positivi.</translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="45"/>
        <source>Very 
Conservative</source>
        <translation>Molto 
Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="46"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="47"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="48"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="49"/>
        <source>Very 
Aggressive</source>
        <translation>Molto 
Aggressivo</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramChart</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="98"/>
        <source>No histogram data available</source>
        <translation>Nessun dato istogramma disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="434"/>
        <source>All Pixels</source>
        <translation>Tutti i Pixel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="445"/>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="456"/>
        <source>AOI Pixels</source>
        <translation>Pixel AOI</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="32"/>
        <source>Thermal Histogram Unavailable</source>
        <translation>Istogramma Termico Non Disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="33"/>
        <source>No thermal temperature data is available for the current image.</source>
        <translation>Per l&apos;immagine corrente non sono disponibili dati di temperatura termica.</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="14"/>
        <source>Thermal Histogram</source>
        <translation>Istogramma Termico</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="23"/>
        <source>Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.</source>
        <translation>Le barre grigie mostrano la distribuzione completa delle temperature, quelle arancioni indicano i bin di AOI/anomalie e passando il mouse sul grafico vengono evidenziati i pixel corrispondenti nell&apos;immagine.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="32"/>
        <source>Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Trascina sull&apos;istogramma per fare zoom. Doppio clic o &quot;Reimposta zoom&quot; per tornare all&apos;intervallo completo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Reimposta zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="64"/>
        <source>Visible Temperature Range</source>
        <translation>Intervallo Temperature Visibile</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="59"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="75"/>
        <source>Minimum: --</source>
        <translation>Minimo: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="60"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="82"/>
        <source>Maximum: --</source>
        <translation>Massimo: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="105"/>
        <source>Reset Range</source>
        <translation>Reimposta intervallo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="61"/>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="126"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="117"/>
        <source>Hover over the histogram to inspect a temperature band.</source>
        <translation>Passa il mouse sull&apos;istogramma per ispezionare una banda di temperatura.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="30"/>
        <source>No thermal histogram data available</source>
        <translation>Nessun dato disponibile per l&apos;istogramma termico</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="131"/>
        <source>Hover band: {lower:.1f} to {upper:.1f} °{unit}</source>
        <translation>Banda evidenziata: da {lower:.1f} a {upper:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="141"/>
        <source>Minimum: {minimum:.1f} °{unit}</source>
        <translation>Minimo: {minimum:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="147"/>
        <source>Maximum: {maximum:.1f} °{unit}</source>
        <translation>Massimo: {maximum:.1f} °{unit}</translation>
    </message>
</context>
<context>
    <name>ThermalRange</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
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
        <translation>Soglia di temperatura minima per il rilevamento nelle immagini termiche.
• Intervallo: da -30°C a 50°C
• Predefinito: 35°C
Definisce il limite inferiore dell&apos;intervallo di rilevamento della temperatura:
• Valori più bassi: AUMENTANO i rilevamenti - accetta oggetti più freddi
• Valori più alti: DIMINUISCONO i rilevamenti - rileva solo oggetti più caldi
Combinata con Temperatura Massima per creare un intervallo di rilevamento (es. 35-40°C per la temperatura corporea umana).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="38"/>
        <source>Minimum Temp (°C)</source>
        <translation>Temperatura Minima (°C)</translation>
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
        <translation>Imposta la temperatura minima per il rilevamento in Celsius.
• Intervallo: da -30°C a 50°C
• Predefinito: 35°C
I pixel con temperature uguali o superiori a questa soglia verranno rilevati.
• Valori più bassi: rilevano oggetti più freddi (più rilevamenti)
• Valori più alti: rilevano solo oggetti più caldi (meno rilevamenti)
Nota: la temperatura è visualizzata in Celsius, convertita in base alle Preferenze.
Usa per trovare oggetti entro un intervallo di temperatura specifico (es. persone 35-40°C).</translation>
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
        <translation>Soglia di temperatura massima per il rilevamento nelle immagini termiche.
• Intervallo: da -30°C a 93°C
• Predefinito: 40°C
Definisce il limite superiore dell&apos;intervallo di rilevamento della temperatura:
• Valori più bassi: DIMINUISCONO i rilevamenti - rileva solo oggetti più freddi
• Valori più alti: AUMENTANO i rilevamenti - accetta oggetti più caldi
Combinata con Temperatura Minima per creare un intervallo di rilevamento (es. 35-40°C per la temperatura corporea umana).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="103"/>
        <source>Maximum Temp (°C)</source>
        <translation>Temperatura Massima (°C)</translation>
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
        <translation>Imposta la temperatura massima per il rilevamento in Celsius.
• Intervallo: da -30°C a 93°C
• Predefinito: 40°C
I pixel con temperature uguali o inferiori a questa soglia verranno rilevati.
• Valori più bassi: rilevano solo oggetti più freddi (meno rilevamenti)
• Valori più alti: rilevano oggetti più caldi (più rilevamenti)
Nota: la temperatura è visualizzata in Celsius, convertita in base alle Preferenze.
Il rilevamento avviene per i pixel compresi tra la temperatura minima e massima (inclusi).</translation>
    </message>
</context>
<context>
    <name>ThermalRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="108"/>
        <source>Minimum Temp ({degree} F)</source>
        <translation>Temperatura Minima ({degree} F)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="114"/>
        <source>Maximum Temp ({degree} F)</source>
        <translation>Temperatura Massima ({degree} F)</translation>
    </message>
</context>
<context>
    <name>ThermalRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRangeWizard.ui" line="34"/>
        <source>What range of temperatures should ADIAT look for?</source>
        <translation>Quale intervallo di temperature dovrebbe cercare ADIAT?</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Modulo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="29"/>
        <source>Type of local thermal residual anomaly to detect in radiometric imagery.
Determines whether to find warm anomalies, cool anomalies, or both.</source>
        <translation>Tipo di anomalia termica residua locale da rilevare nelle immagini radiometriche.
Determina se cercare anomalie calde, fredde o entrambe.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Tipo di Anomalia:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="45"/>
        <source>Select the type of thermal residual anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to its local background estimate.</source>
        <translation>Seleziona il tipo di anomalia termica residua da rilevare:
• Sopra o Sotto la Media: rileva sia anomalie calde che fredde (predefinito)
• Sopra la Media: rileva solo punti caldi (temperature superiori alla media)
• Sotto la Media: rileva solo punti freddi (temperature inferiori alla media)
L&apos;algoritmo confronta la temperatura di ogni pixel con la stima locale del fondo.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="53"/>
        <source>Above or Below Mean</source>
        <translation>Sopra o Sotto la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="58"/>
        <source>Above Mean</source>
        <translation>Sopra la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="63"/>
        <source>Below Mean</source>
        <translation>Sotto la Media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="92"/>
        <source>Detection sensitivity for thermal residual anomalies.
• Range: 1 to 10
• Default: 5
Lower values are more conservative (fewer detections).
Higher values are more aggressive (more detections).</source>
        <translation>Sensibilità di rilevamento per le anomalie termiche residue.
• Intervallo: da 1 a 10
• Predefinito: 5
Valori più bassi sono più conservativi (meno rilevamenti).
Valori più alti sono più aggressivi (più rilevamenti).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="99"/>
        <source>Sensitivity:</source>
        <translation>Sensibilità:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="112"/>
        <source>Adjust detection sensitivity for local thermal residual anomalies.
• 1-3: Conservative
• 4-6: Moderate
• 7-10: Aggressive</source>
        <translation>Regola la sensibilità di rilevamento per le anomalie termiche residue locali.
• 1-3: conservativo
• 4-6: moderato
• 7-10: aggressivo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="153"/>
        <source>Current sensitivity level for residual anomaly detection.</source>
        <translation>Livello di sensibilità attuale per il rilevamento delle anomalie residue.</translation>
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
        <translation>Che tipo di anomalie stai cercando?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="54"/>
        <source>Warmer than surroundings</source>
        <translation>Più caldo dell&apos;ambiente circostante</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="66"/>
        <source>Cooler than surroundings</source>
        <translation>Più freddo dell&apos;ambiente circostante</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="78"/>
        <source>Both</source>
        <translation>Entrambi</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="117"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>Quanto aggressivamente dovrebbe ADIAT cercare le anomalie?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="130"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: un&apos;impostazione più alta troverà più potenziali anomalie ma potrebbe anche aumentare i falsi positivi.</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="33"/>
        <source>Very 
Conservative</source>
        <translation>Molto 
Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="34"/>
        <source>Conservative</source>
        <translation>Conservativo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="35"/>
        <source>Moderate</source>
        <translation>Moderato</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="36"/>
        <source>Aggressive</source>
        <translation>Aggressivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="37"/>
        <source>Very 
Aggressive</source>
        <translation>Molto 
Aggressivo</translation>
    </message>
</context>
<context>
    <name>TileFetchController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="150"/>
        <source>Invalid Area</source>
        <translation>Area non valida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="151"/>
        <source>Please enter a valid bounding box.</source>
        <translation>Inserisci un riquadro di delimitazione valido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="154"/>
        <source>No Output Folder</source>
        <translation>Nessuna cartella di output</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="155"/>
        <source>Please choose an output folder.</source>
        <translation>Scegli una cartella di output.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="158"/>
        <source>No Dataset</source>
        <translation>Nessun set di dati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="159"/>
        <source>Please select at least one dataset.</source>
        <translation>Seleziona almeno un set di dati.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="286"/>
        <source>No GPS Found</source>
        <translation>Nessun GPS trovato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="287"/>
        <source>No GPS positions were found in the {source} images.</source>
        <translation>Nessuna posizione GPS trovata nelle immagini di {source}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="302"/>
        <source>Select image folder</source>
        <translation>Seleziona la cartella delle immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="311"/>
        <source>No Images</source>
        <translation>Nessuna immagine</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="312"/>
        <source>No images were found in the selected folder.</source>
        <translation>Nessuna immagine trovata nella cartella selezionata.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="358"/>
        <source>Replace Canopy Source?</source>
        <translation>Sostituire l&apos;origine dati chioma?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="359"/>
        <source>A LANDFIRE canopy source is currently configured.

Register the downloaded Meta/WRI canopy tiles instead? (Your LANDFIRE files stay on disk; only the selected source changes.)</source>
        <translation>È attualmente configurata un&apos;origine dati chioma LANDFIRE.

Registrare invece le tile chioma Meta/WRI scaricate? (I file LANDFIRE restano su disco; cambia solo l&apos;origine selezionata.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Elevation (DEM)</source>
        <translation>Elevazione (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Canopy height</source>
        <translation>Altezza della chioma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="385"/>
        <source>{product}: cancelled before completion.</source>
        <translation>{product}: annullato prima del completamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="387"/>
        <source>{product}: {failed} tile(s) failed to download.</source>
        <translation>{product}: {failed} tile non scaricate.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="390"/>
        <source>{product}: no data covers this area.</source>
        <translation>{product}: nessun dato copre quest&apos;area.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="392"/>
        <source>{product}: nothing was downloaded.</source>
        <translation>{product}: non è stato scaricato nulla.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="399"/>
        <source>{product}: registered as the active source.</source>
        <translation>{product}: registrato come origine attiva.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="402"/>
        <source>{product}: NOT registered (no usable tiles).</source>
        <translation>{product}: NON registrato (nessuna tile utilizzabile).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="411"/>
        <source>Download Finished with Problems</source>
        <translation>Download completato con problemi</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="417"/>
        <source>Download Complete</source>
        <translation>Download completato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="406"/>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="413"/>
        <source>Downloaded {count} tiles.</source>
        <translation>Scaricate {count} tile.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="428"/>
        <source>Download Cancelled</source>
        <translation>Download annullato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="429"/>
        <source>The download was cancelled. No tiles were registered.</source>
        <translation>Il download è stato annullato. Nessuna tile è stata registrata.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="436"/>
        <source>Download Error</source>
        <translation>Errore di download</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="437"/>
        <source>Tile download failed:
{error}</source>
        <translation>Download delle tile non riuscito:
{error}</translation>
    </message>
</context>
<context>
    <name>TileFetchDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="48"/>
        <source>Download Coverage Data</source>
        <translation>Scarica dati di copertura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="58"/>
        <source>Area of Interest (WGS84)</source>
        <translation>Area di interesse (WGS84)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="68"/>
        <source>Fill area from</source>
        <translation>Riempi area da</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="73"/>
        <source>Fill the area from the loaded mission&apos;s image GPS, or from an image folder.</source>
        <translation>Riempi l&apos;area dal GPS delle immagini della missione caricata o da una cartella di immagini.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="70"/>
        <source>Loaded mission extent</source>
        <translation>Estensione della missione caricata</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="71"/>
        <source>Image folder...</source>
        <translation>Cartella immagini...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="93"/>
        <source>Min longitude:</source>
        <translation>Longitudine min.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="95"/>
        <source>Min latitude:</source>
        <translation>Latitudine min.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="97"/>
        <source>Max longitude:</source>
        <translation>Longitudine max.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="99"/>
        <source>Max latitude:</source>
        <translation>Latitudine max.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="104"/>
        <source>Footprint buffer (m):</source>
        <translation>Buffer dell&apos;impronta (m):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="109"/>
        <source>Padding added around the camera positions so downloaded tiles cover the image footprints. Auto-sized from the mission; edit and re-fill to change.</source>
        <translation>Spazio aggiunto attorno alle posizioni della camera affinché le tile scaricate coprano le impronte delle immagini. Dimensionato automaticamente dalla missione; modifica e ricompila per cambiarlo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="118"/>
        <source>Datasets</source>
        <translation>Set di dati</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="120"/>
        <source>USGS 3DEP DEM</source>
        <translation>USGS 3DEP DEM</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="123"/>
        <source>USGS 3DEP provides 1 m local elevation. Optional when you already have a terrain source configured (AWS Terrain Tiles online, or downloaded 3DEP) — enable it to download higher-resolution data.</source>
        <translation>USGS 3DEP fornisce un&apos;elevazione locale a 1 m. Opzionale quando è già configurata una sorgente del terreno (AWS Terrain Tiles online o 3DEP scaricato): abilitalo per scaricare dati a risoluzione più elevata.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="127"/>
        <source>Meta/WRI Canopy Height</source>
        <translation>Altezza chioma Meta/WRI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="142"/>
        <source>Store in:</source>
        <translation>Salva in:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="144"/>
        <source>Central tile library (recommended)</source>
        <translation>Libreria centrale dei tile (consigliato)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="146"/>
        <source>Mission results folder</source>
        <translation>Cartella dei risultati della missione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="147"/>
        <source>Custom folder...</source>
        <translation>Cartella personalizzata...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="149"/>
        <source>The central library collects tiles from all missions in one place (they merge, nothing gets replaced) and registers automatically. Choose the results folder or a custom folder to keep tiles beside a specific mission instead.</source>
        <translation>La libreria centrale raccoglie i tile di tutte le missioni in un unico posto (si uniscono, nulla viene sostituito) e si registra automaticamente. Scegli la cartella dei risultati o una cartella personalizzata per tenere i tile accanto a una missione specifica.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="158"/>
        <source>Output folder:</source>
        <translation>Cartella di output:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="162"/>
        <source>Browse...</source>
        <translation>Sfoglia...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="168"/>
        <source>Register in Preferences when complete</source>
        <translation>Registra nelle Preferenze al termine</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="177"/>
        <source>Download</source>
        <translation>Scarica</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="180"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="206"/>
        <source>This area is already covered by your registered tiles.</source>
        <translation>Quest&apos;area è già coperta dai tile registrati.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="208"/>
        <source>Partially covered by your registered tiles — downloading fills the gaps.</source>
        <translation>Parzialmente coperto dai tile registrati: il download colma le lacune.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="214"/>
        <source>Your downloaded 1 m tiles don&apos;t include this area — without this download, online AWS Terrain Tiles (~30 m) are used here instead.</source>
        <translation>I tile a 1 m scaricati non includono quest&apos;area: senza questo download, qui vengono usati gli AWS Terrain Tiles online (~30 m).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="217"/>
        <source>Your downloaded canopy tiles don&apos;t include this area — without this download, POD runs with no canopy attenuation here.</source>
        <translation>I tile della chioma scaricati non includono quest&apos;area: senza questo download, il POD viene eseguito qui senza attenuazione della chioma.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="222"/>
        <source>No local elevation tiles registered — online AWS Terrain Tiles (~30 m) serve as the baseline.</source>
        <translation>Nessun tile di elevazione locale registrato: gli AWS Terrain Tiles online (~30 m) fungono da base.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="224"/>
        <source>No canopy source is configured yet.</source>
        <translation>Nessuna sorgente di chioma è ancora configurata.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="276"/>
        <source>Select output folder</source>
        <translation>Seleziona la cartella di output</translation>
    </message>
</context>
<context>
    <name>TrackGalleryWidget</name>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="41"/>
        <source>Detection Gallery</source>
        <translation>Galleria Rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="82"/>
        <source>0 detections</source>
        <translation>0 rilevamenti</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="149"/>
        <source>1 detection</source>
        <translation>1 rilevamento</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="151"/>
        <source>{count} detections</source>
        <translation>{count} rilevamenti</translation>
    </message>
</context>
<context>
    <name>UnifiedMapExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="438"/>
        <source>No Data Selected</source>
        <translation>Nessun Dato Selezionato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="439"/>
        <source>Please select at least one type of data to export.</source>
        <translation>Seleziona almeno un tipo di dato da esportare.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="468"/>
        <source>Select folder for POD coverage files</source>
        <translation>Seleziona la cartella per i file di copertura POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="476"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="583"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="855"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="889"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="934"/>
        <source>Export Error</source>
        <translation>Errore di Esportazione</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="477"/>
        <source>An error occurred during export:
{error}</source>
        <translation>Si è verificato un errore durante l&apos;esportazione:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="495"/>
        <source>Save Map Export</source>
        <translation>Salva Esportazione Mappa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="497"/>
        <source>KML files (*.kml);;KMZ files (*.kmz)</source>
        <translation>File KML (*.kml);;File KMZ (*.kmz)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="584"/>
        <source>Failed to export to KML:
{error}</source>
        <translation>Impossibile esportare in KML:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="651"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="822"/>
        <source>POD Error</source>
        <translation>Errore POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="652"/>
        <source>Could not start the POD calculation:
{error}</source>
        <translation>Impossibile avviare il calcolo POD:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="702"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="714"/>
        <source>POD coverage complete</source>
        <translation>Copertura POD completata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="711"/>
        <source>POD coverage complete — {count} frame(s) used online elevation (outside local DEM)</source>
        <translation>Copertura POD completata: {count} fotogramma/i hanno usato l&apos;elevazione online (fuori dal DEM locale)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="719"/>
        <source>POD complete — {skipped} of {total} frames skipped</source>
        <translation>POD completato: {skipped} di {total} fotogrammi saltati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="722"/>
        <source>({count} without elevation data)</source>
        <translation>({count} senza dati di elevazione)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="730"/>
        <source>(canopy data covered {pct}% of the searched area)</source>
        <translation>(i dati sulla chioma coprivano il {pct}% dell&apos;area cercata)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="785"/>
        <source>Terrain and canopy aware probability-of-detection heatmap.</source>
        <translation>Mappa di calore della probabilità di rilevamento consapevole di terreno e chioma.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="789"/>
        <source>Mean POD over covered area: {pod}%</source>
        <translation>POD media sull&apos;area coperta: {pod}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="792"/>
        <source>POD Coverage</source>
        <translation>Copertura POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="800"/>
        <source>POD Overlay</source>
        <translation>Sovrapposizione POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="801"/>
        <source>The POD coverage was computed, but embedding it into the exported file failed:
{error}

The POD GeoTIFF products were still written next to the export.</source>
        <translation>La copertura POD è stata calcolata, ma l&apos;incorporamento nel file esportato non è riuscito:
{error}

I prodotti GeoTIFF POD sono stati comunque scritti accanto all&apos;esportazione.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="814"/>
        <source>POD calculation cancelled</source>
        <translation>Calcolo POD annullato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="823"/>
        <source>POD calculation failed:
{error}</source>
        <translation>Calcolo POD non riuscito:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="856"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="890"/>
        <source>Failed to export to CalTopo:
{error}</source>
        <translation>Impossibile esportare su CalTopo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="906"/>
        <source>Map export completed successfully!</source>
        <translation>Esportazione mappa completata con successo!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="921"/>
        <source>Map export cancelled</source>
        <translation>Esportazione mappa annullata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="935"/>
        <source>Map export failed:
{error}</source>
        <translation>Esportazione mappa non riuscita:
{error}</translation>
    </message>
</context>
<context>
    <name>UpdateController</name>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="52"/>
        <source>Disabled while Offline Only mode is enabled.</source>
        <translation>Disabilitato quando la modalita&apos; Solo offline e&apos; attiva.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="56"/>
        <source>Check the update feed for a newer ADIAT installer.</source>
        <translation>Controlla il feed degli aggiornamenti per un installer ADIAT piu&apos; recente.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="85"/>
        <source>Updates Disabled</source>
        <translation>Aggiornamenti disabilitati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="87"/>
        <source>Update checks are disabled while Offline Only mode is enabled.</source>
        <translation>Il controllo aggiornamenti e&apos; disabilitato quando la modalita&apos; Solo offline e&apos; attiva.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="101"/>
        <source>Update Check Failed</source>
        <translation>Controllo aggiornamenti non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="102"/>
        <source>Unable to check for updates:
{error}</source>
        <translation>Impossibile controllare gli aggiornamenti:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="110"/>
        <source>No Updates Available</source>
        <translation>Nessun aggiornamento disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="112"/>
        <source>You are already running the latest available version of ADIAT.</source>
        <translation>Stai gia&apos; utilizzando la versione piu&apos; recente disponibile di ADIAT.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="130"/>
        <source>Installer Launch Failed</source>
        <translation>Avvio installer non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="131"/>
        <source>The installer was downloaded but could not be launched:
{error}</source>
        <translation>L&apos;installer e&apos; stato scaricato ma non e&apos; stato possibile avviarlo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="137"/>
        <source>Installer Started</source>
        <translation>Installer avviato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="139"/>
        <source>The installer has been launched. Close ADIAT when you are ready to continue the update.</source>
        <translation>L&apos;installer e&apos; stato avviato. Chiudi ADIAT quando sei pronto per continuare l&apos;aggiornamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="148"/>
        <source>Update Available</source>
        <translation>Aggiornamento disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="150"/>
        <source>ADIAT {new_version} is available. You are running {current_version}.</source>
        <translation>ADIAT {new_version} e&apos; disponibile. Stai usando {current_version}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="156"/>
        <source>Do you want to download and launch the installer now?</source>
        <translation>Vuoi scaricare e avviare subito l&apos;installer?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="159"/>
        <source>Download and Install</source>
        <translation>Scarica e installa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="168"/>
        <source>Downloading ADIAT {version}...</source>
        <translation>Download di ADIAT {version} in corso...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="169"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="174"/>
        <source>Downloading Update</source>
        <translation>Download aggiornamento</translation>
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
        <translation>sconosciuto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="196"/>
        <source>Downloading ADIAT {version}...
{downloaded} of {total}</source>
        <translation>Download di ADIAT {version}...
{downloaded} di {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="204"/>
        <location filename="../app/core/controllers/UpdateController.py" line="210"/>
        <source>Update download canceled.</source>
        <translation>Download aggiornamento annullato.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="215"/>
        <source>Download Failed</source>
        <translation>Download non riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="216"/>
        <source>Unable to download the update installer:
{error}</source>
        <translation>Impossibile scaricare l&apos;installer di aggiornamento:
{error}</translation>
    </message>
</context>
<context>
    <name>UpscaleDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="187"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="367"/>
        <source>Upscaled View - {level}x</source>
        <translation>Vista Upscalata - {level}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="229"/>
        <source>Upscale Method:</source>
        <translation>Metodo di Upscale:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="233"/>
        <source>Auto (Recommended)</source>
        <translation>Automatico (Consigliato)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="234"/>
        <source>Fast (Lanczos)</source>
        <translation>Veloce (Lanczos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="236"/>
        <source>Balanced (OpenCV EDSR)</source>
        <translation>Bilanciato (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="264"/>
        <source>Upres Again</source>
        <translation>Aumenta Risoluzione di Nuovo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="267"/>
        <source>Upscale the currently visible portion by {factor}x</source>
        <translation>Effettua l&apos;upscale della porzione visibile corrente di {factor}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="271"/>
        <source>Quit</source>
        <translation>Esci</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="274"/>
        <source>Close this upscale window</source>
        <translation>Chiudi questa finestra di upscale</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="302"/>
        <source>Resolution: {width} × {height} pixels | Original: {orig_w} × {orig_h} pixels | Upscale: {level}x | Use mouse wheel to zoom, right-click to pan</source>
        <translation>Risoluzione: {width} × {height} pixel | Originale: {orig_w} × {orig_h} pixel | Upscale: {level}x | Usa la rotella del mouse per lo zoom, tasto destro per spostare</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="375"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="387"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="532"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="564"/>
        <source>Upscale Error</source>
        <translation>Errore di Upscale</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="376"/>
        <source>Error during initial upscale: {error}</source>
        <translation>Errore durante l&apos;upscale iniziale: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="388"/>
        <source>Unable to extract visible image portion.</source>
        <translation>Impossibile estrarre la porzione visibile dell&apos;immagine.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="397"/>
        <source>Maximum Upscale Reached</source>
        <translation>Upscale Massimo Raggiunto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="399"/>
        <source>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</source>
        <translation>È stato raggiunto il livello massimo di upscale di {level}x.
Ulteriori upscaling non sono consentiti per prevenire problemi di memoria.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="413"/>
        <source>Image Too Large</source>
        <translation>Immagine Troppo Grande</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="415"/>
        <source>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</source>
        <translation>L&apos;upscale produrrebbe un&apos;immagine di {width}×{height} pixel.
La dimensione massima consentita è {max_dim} pixel.

Prova a ingrandire una zona più piccola prima di effettuare l&apos;upscale.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="426"/>
        <source>Image Too Small</source>
        <translation>Immagine Troppo Piccola</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="428"/>
        <source>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</source>
        <translation>La porzione visibile è troppo piccola ({width}×{height} pixel).
Per favore ingrandisci un&apos;area più grande prima di effettuare l&apos;upscale.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="468"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="565"/>
        <source>An error occurred during upscaling:
{error}</source>
        <translation>Si è verificato un errore durante l&apos;upscale:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="487"/>
        <source>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</source>
        <translation>Upscale dell&apos;immagine con miglioramento AI...
Da {width}×{height} a {new_width}×{new_height} pixel
Potrebbe richiedere alcuni secondi.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="760"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="504"/>
        <source>Upscaling (OpenCV EDSR)</source>
        <translation>Upscale (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="533"/>
        <source>Failed to start upscaling:
{error}</source>
        <translation>Impossibile avviare l&apos;upscale:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="603"/>
        <source>Method Not Available</source>
        <translation>Metodo Non Disponibile</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="605"/>
        <source>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</source>
        <translation>Real-ESRGAN non è ancora implementato.
Si torna all&apos;interpolazione Lanczos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="759"/>
        <source>Downloading {model_name} model...</source>
        <translation>Download del modello {model_name}...</translation>
    </message>
</context>
<context>
    <name>VideoParser</name>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="14"/>
        <source>Video Parser</source>
        <translation>Parser Video</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="45"/>
        <source>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</source>
        <translation>Percorso del file video da cui estrarre i fotogrammi.
Formati supportati: MP4, AVI, MOV, MKV e altri formati video comuni.
Clicca il pulsante Seleziona per cercare un file video.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="62"/>
        <source>Metadata file containing GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Optional: Provides location information for extracted frames.
Without a metadata file, frames will have no GPS data.</source>
        <translation>File di metadati contenente i dati di telemetria GPS.
Supporta file di sottotitoli SRT DJI e log di volo CSV Skydio.
Opzionale: fornisce informazioni di localizzazione per i frame estratti.
Senza un file di metadati, i frame non avranno dati GPS.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="68"/>
        <source>The metadata file contains timestamped GPS information for the video.  It is optional, but without it output images won&apos;t include location information.  Supports SRT (DJI) and CSV (Skydio) formats.</source>
        <translation>Il file di metadati contiene informazioni GPS con timestamp per il video. È opzionale, ma senza di esso le immagini in uscita non includeranno informazioni di localizzazione. Supporta i formati SRT (DJI) e CSV (Skydio).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="71"/>
        <source>Metadata File (optional): </source>
        <translation>File di Metadati (opzionale): </translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="83"/>
        <source>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</source>
        <translation>Cartella di destinazione dove verranno salvate le immagini dei fotogrammi estratti.
Ogni fotogramma viene salvato come file immagine separato con informazioni di timestamp.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="87"/>
        <source>Output Folder:</source>
        <translation>Cartella Output:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="99"/>
        <source>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</source>
        <translation>Percorso della cartella di output per le immagini dei fotogrammi estratti.
Tutti i fotogrammi saranno salvati in questa directory con nomi sequenziali.
Clicca il pulsante Seleziona per scegliere una cartella diversa.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="116"/>
        <source>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</source>
        <translation>Sfoglia la cartella di output per salvare i fotogrammi estratti.
Apre una finestra di selezione cartella.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="120"/>
        <location filename="../resources/views/images/VideoParser.ui" line="162"/>
        <location filename="../resources/views/images/VideoParser.ui" line="200"/>
        <source>Select</source>
        <translation>Seleziona</translation>
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
        <translation>Seleziona il file video sorgente da analizzare.
Il video verrà diviso in singole immagini di fotogrammi.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="146"/>
        <source>Video File:</source>
        <translation>File Video:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="158"/>
        <source>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</source>
        <translation>Sfoglia un file video da cui estrarre i fotogrammi.
Apre una finestra di selezione file per video (MP4, AVI, MOV, ecc.).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="177"/>
        <source>Path to the optional metadata file with GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
If provided, extracted frames will include GPS metadata (latitude, longitude, altitude).
Can be left empty if location data is not needed.</source>
        <translation>Percorso del file di metadati opzionale con dati di telemetria GPS.
Supporta file di sottotitoli SRT DJI e log di volo CSV Skydio.
Se fornito, i frame estratti includeranno metadati GPS (latitudine, longitudine, altitudine).
Può essere lasciato vuoto se i dati di localizzazione non sono necessari.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="195"/>
        <source>Browse for optional metadata file containing GPS telemetry.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Opens a file selection dialog for SRT and CSV files.</source>
        <translation>Sfoglia per scegliere un file di metadati opzionale contenente la telemetria GPS.
Supporta file di sottotitoli SRT DJI e log di volo CSV Skydio.
Apre una finestra di dialogo per la selezione di file SRT e CSV.</translation>
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
        <translation>Avvia l&apos;estrazione dei frame dal file video.
Requisiti:
• Il file video deve essere selezionato
• La cartella di output deve essere selezionata
• L&apos;intervallo di tempo deve essere impostato (predefinito: 5 secondi)
Il processo estrarrà i frame all&apos;intervallo specificato e li salverà come immagini.
Se viene fornito un file di metadati (SRT o CSV), i metadati GPS verranno incorporati nei frame estratti.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="219"/>
        <source>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</source>
        <translation>Intervallo di tempo tra i fotogrammi estratti.
Determina la frequenza con cui i fotogrammi vengono catturati dal video.
Intervalli più piccoli = più fotogrammi estratti (output più grande)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="224"/>
        <source>Time Interval (seconds):</source>
        <translation>Intervallo di Tempo (secondi):</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="236"/>
        <source>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</source>
        <translation>Imposta l&apos;intervallo di tempo in secondi tra le estrazioni dei fotogrammi.
• Intervallo: da 0.1 a illimitati secondi
• Predefinito: 5.0 secondi (estrae 1 fotogramma ogni 5 secondi)
• Valori più bassi: più fotogrammi estratti (es. 0.5s = 2 fotogrammi al secondo)
• Valori più alti: meno fotogrammi estratti (es. 10s = 1 fotogramma ogni 10 secondi)
Consigliato: 3-5 secondi per la maggior parte delle analisi di filmati da drone</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="320"/>
        <source>Start</source>
        <translation>Avvia</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="351"/>
        <source>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</source>
        <translation>Annulla il processo di estrazione dei fotogrammi.
Interrompe l&apos;operazione immediatamente e torna allo stato pronto.
I fotogrammi già estratti verranno salvati nella cartella di output.
Clicca per interrompere l&apos;operazione di parsing corrente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="360"/>
        <source> Cancel</source>
        <translation> Annulla</translation>
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
        <translation>Finestra di output di avanzamento e stato.
Mostra informazioni in tempo reale durante l&apos;estrazione dei fotogrammi:
• Fotogramma corrente in elaborazione
• Timestamp e numeri dei fotogrammi
• Coordinate GPS (se il file SRT è fornito)
• Percentuale di avanzamento e stato di completamento
• Eventuali errori o avvisi riscontrati
Mostra il totale dei fotogrammi estratti al termine.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="57"/>
        <source>Select a Video File</source>
        <translation>Seleziona un File Video</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="72"/>
        <source>Select a Metadata File</source>
        <translation>Seleziona un File di Metadati</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="73"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv)</source>
        <translation>File di metadati (*.srt *.csv);;File SRT (*.srt);;Log di volo CSV (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="90"/>
        <source>Select Directory</source>
        <translation>Seleziona Cartella</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="110"/>
        <source>Please set the video file and output directory.</source>
        <translation>Imposta il file video e la cartella di output.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="115"/>
        <source>--- Starting video processing ---</source>
        <translation>--- Avvio elaborazione video ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="164"/>
        <source>Confirmation</source>
        <translation>Conferma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="165"/>
        <source>Are you sure you want to cancel the video processing in progress?</source>
        <translation>Sei sicuro di voler annullare l&apos;elaborazione video in corso?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="201"/>
        <source>--- Video Processing Completed ---</source>
        <translation>--- Elaborazione video completata ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="203"/>
        <source>{count} images created</source>
        <translation>{count} immagini create</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="256"/>
        <source>Error Starting Processing</source>
        <translation>Errore Avvio Elaborazione</translation>
    </message>
</context>
<context>
    <name>Viewer</name>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</source>
        <translation>Strumento Automatico di Analisi Immagini Drone :: Visualizzatore - Sponsorizzato da TEXSAR</translation>
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
        <translation>Visualizza scorciatoie da tastiera e aiuto</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="199"/>
        <source>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</source>
        <translation>Attiva/disattiva l&apos;overlay di rilevamento sull&apos;immagine.
Quando abilitato, mostra l&apos;immagine elaborata con gli oggetti rilevati evidenziati.
Quando disabilitato, mostra l&apos;immagine originale non elaborata.
Usa per confrontare l&apos;immagine originale con i risultati del rilevamento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="450"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="205"/>
        <source>Show Overlay</source>
        <translation>Mostra Overlay</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1242"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="225"/>
        <source>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</source>
        <translation>Attiva/disattiva modalità Galleria (G)
Mostra tutte le AOI di tutte le immagini in una vista a griglia</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="255"/>
        <source>Highlight Pixels of Interest(H)</source>
        <translation>Evidenzia Pixel di Interesse (H)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="277"/>
        <source>Show AOIs</source>
        <translation>Mostra AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1262"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="328"/>
        <source>Open Histogram</source>
        <translation>Apri Istogramma</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="344"/>
        <source>Map with Image Locations (M)</source>
        <translation>Mappa con Posizioni Immagini (M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="360"/>
        <source>North-Oriented View of Image (R)</source>
        <translation>Vista dell&apos;immagine orientata a Nord (R)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="376"/>
        <source>Adjust Image (Ctrl+H)</source>
        <translation>Regola Immagine (Ctrl+H)</translation>
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
        <translation>Misura Distanza (Ctrl+M)</translation>
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
        <translation>Riferimento dimensioni persona (Ctrl+P)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="299"/>
        <source>Toggle the measurement ruler drawn over the selected AOI</source>
        <translation>Mostra/nascondi il righello di misura disegnato sopra l&apos;AOI selezionata</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="439"/>
        <source>person.png</source>
        <translation>person.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="446"/>
        <source>Toggle Grid Review Mode (S) — sweep the image cell by cell; Shift+S for grid settings</source>
        <translation>Attiva/disattiva modalità revisione a griglia (S) — esegue la scansione dell&apos;immagine cella per cella; Maiusc+S per le impostazioni della griglia</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="461"/>
        <source>grid.png</source>
        <translation>grid.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="468"/>
        <source>Toggle Magnifying Glass (Middle Mouse)</source>
        <translation>Attiva/disattiva lente di ingrandimento (tasto centrale)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="498"/>
        <source>magnify.png</source>
        <translation>magnify.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="512"/>
        <source>Map Export (KML / CalTopo)</source>
        <translation>Esportazione Mappa (KML / CalTopo)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="542"/>
        <source>map.png</source>
        <translation>map.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="549"/>
        <source>Generate PDF Report</source>
        <translation>Genera Report PDF</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="579"/>
        <source>pdf.png</source>
        <translation>pdf.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="591"/>
        <source>Generate Zip Bundle</source>
        <translation>Genera Pacchetto Zip</translation>
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
        <translation>Salta le immagini nascoste durante la navigazione.
Quando abilitato, i pulsanti Precedente/Successivo saltano le immagini contrassegnate come nascoste.
Usa per concentrarti su immagini non ancora revisionate o contrassegnate per l&apos;esclusione.
Scorciatoia da tastiera: H per nascondere/mostrare l&apos;immagine corrente</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="652"/>
        <source>Skip Hidden</source>
        <translation>Salta Nascoste</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="691"/>
        <source>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</source>
        <translation>Contrassegna l&apos;immagine corrente come nascosta.
Le immagini nascoste possono essere escluse da report, esportazioni e navigazione.
Usa per rimuovere immagini con falsi positivi o senza rilevamenti rilevanti.
Quando &quot;Salta Nascoste&quot; è abilitato, le immagini nascoste vengono saltate durante la navigazione.
Scorciatoia da tastiera: H</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="698"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="718"/>
        <source>Hide Image</source>
        <translation>Nascondi Immagine</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="710"/>
        <source>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</source>
        <translation>Visualizza il nome dell&apos;immagine attualmente nascosta.
Quando un&apos;immagine è contrassegnata come nascosta, il suo nome file appare qui.
Le immagini nascoste sono escluse dalla navigazione quando &quot;Salta Nascoste&quot; è abilitato.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="746"/>
        <source>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</source>
        <translation>Salta direttamente a un numero immagine specifico.
Inserisci un numero immagine e premi Invio per navigare istantaneamente.
Utile per rivedere immagini specifiche o tornare a una posizione annotata.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="751"/>
        <source>Jump To:</source>
        <translation>Vai a:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="776"/>
        <source>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</source>
        <translation>Inserisci un numero immagine (da 1 al totale) e premi Invio.
Naviga rapidamente a qualsiasi immagine nei risultati dell&apos;analisi.
Esempio: digita &quot;25&quot; e premi Invio per andare all&apos;immagine n. 25</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="790"/>
        <source>Jump to a specific AOI by its run-wide number.
Enter an AOI number and press Enter to select and scroll to it.</source>
        <translation>Vai a una AOI specifica tramite il suo numero globale nell&apos;esecuzione.
Inserisci un numero AOI e premi Invio per selezionarla e scorrere fino a essa.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="794"/>
        <source>Go to AOI #:</source>
        <translation>Vai ad AOI n.:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="819"/>
        <source>Enter an AOI number and press Enter.
Selects that AOI and scrolls it into view in the gallery or single-image list.</source>
        <translation>Inserisci un numero AOI e premi Invio.
Seleziona quell&apos;AOI e la porta in vista nella galleria o nell&apos;elenco a immagine singola.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="832"/>
        <source>Previous Image</source>
        <translation>Immagine Precedente</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="839"/>
        <source>previous.png</source>
        <translation>previous.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="854"/>
        <source>Next Image</source>
        <translation>Immagine Successiva</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="861"/>
        <source>next.png</source>
        <translation>next.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1004"/>
        <source>Filter AOIs by color and pixel area</source>
        <translation>Filtra AOI per colore e area in pixel</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1076"/>
        <source>Sort By</source>
        <translation>Ordina per</translation>
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
        <translation>Ordina le Aree di Interesse (AOI) nell&apos;elenco.
Scegli come ordinare gli oggetti rilevati:
• Area in pixel: ordina per dimensione (dal più grande al più piccolo)
• Distanza: ordina per distanza dal centro dell&apos;immagine o punto di riferimento
• Colore: raggruppa per colori simili
• Ordine di rilevamento: ordine originale dall&apos;analisi
L&apos;ordinamento aiuta a dare priorità alla revisione di oggetti più grandi o più vicini.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1176"/>
        <source>Open</source>
        <translation>Apri</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="132"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Strumento Automatico di Analisi Immagini Drone v{version} - Sponsorizzato da TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="144"/>
        <source>Reading result file...</source>
        <translation>Lettura file risultati...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="161"/>
        <source>Checking image dimensions ({n} images)...</source>
        <translation>Controllo dimensioni immagini ({n} immagini)...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="171"/>
        <source>Validating image paths...</source>
        <translation>Convalida percorsi immagini...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="178"/>
        <source>Load Results Failed</source>
        <translation>Caricamento Risultati Non Riuscito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="180"/>
        <source>Cannot load results without valid image and mask locations.

The viewer will now close.</source>
        <translation>Impossibile caricare i risultati senza posizioni valide di immagini e maschere.

Il visualizzatore verrà chiuso.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="187"/>
        <source>Scanning source folder for full flight...</source>
        <translation>Scansione cartella sorgente per l&apos;intero volo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="203"/>
        <source>Initialising controllers...</source>
        <translation>Inizializzazione controller...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="214"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1455"/>
        <source>Skip Hidden ({count}) </source>
        <translation>Salta Nascoste ({count}) </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="246"/>
        <source>Loading detection results from {n} images...</source>
        <translation>Caricamento risultati rilevamenti da {n} immagini...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="285"/>
        <source>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</source>
        <translation>Metadati e informazioni dell&apos;immagine.
Clicca su Coordinate GPS per copiare, condividere o aprire in applicazioni di mappatura.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="317"/>
        <source>Loading first image...</source>
        <translation>Caricamento prima immagine...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="332"/>
        <source>Preparing thumbnails...</source>
        <translation>Preparazione miniature...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="648"/>
        <source>No Dataset</source>
        <translation>Nessun Dataset</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="649"/>
        <source>No dataset is currently loaded.</source>
        <translation>Nessun dataset è attualmente caricato.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="656"/>
        <source>Generate Cache</source>
        <translation>Genera Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="658"/>
        <source>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</source>
        <translation>Questo rigenererà la cache delle miniature e dei colori per tutte le AOI in questo dataset.

Questo potrebbe richiedere alcuni minuti a seconda della dimensione del dataset.

Continuare?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="671"/>
        <source>Initializing cache generation...</source>
        <translation>Inizializzazione generazione cache...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="672"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="677"/>
        <source>Generating Cache</source>
        <translation>Generazione Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="714"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="715"/>
        <source>Failed to start cache generation:
{error}</source>
        <translation>Impossibile avviare la generazione della cache:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="733"/>
        <source>Cache Generated</source>
        <translation>Cache Generata</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="735"/>
        <source>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</source>
        <translation>Generazione cache completata!

Elaborate {images} immagini con {aois} AOI.

Il visualizzatore ora caricherà miniature e colori molto più velocemente.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="766"/>
        <source>Cache Generation Error</source>
        <translation>Errore Generazione Cache</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="768"/>
        <source>An error occurred during cache generation:

{error}</source>
        <translation>Si è verificato un errore durante la generazione della cache:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="954"/>
        <source>AOI Not Visible</source>
        <translation>AOI Non Visibile</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="956"/>
        <source>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</source>
        <translation>L&apos;AOI alla posizione del cursore non può essere selezionata perché attualmente è nascosta a causa dei filtri attivi.

Per selezionare questa AOI, cancella o regola i tuoi filtri.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1121"/>
        <source>Update Image Dimensions</source>
        <translation>Aggiorna Dimensioni Immagini</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1123"/>
        <source>This dataset is missing image dimensions needed for heatmap filtering ({count} images).

Would you like to read dimensions from the image files and update the results file?</source>
        <translation>In questo dataset mancano le dimensioni delle immagini necessarie per il filtraggio tramite heatmap ({count} immagini).

Vuoi leggere le dimensioni dai file immagine e aggiornare il file dei risultati?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1162"/>
        <source>Reading image dimensions ({done}/{total})...</source>
        <translation>Lettura dimensioni immagini ({done}/{total})...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1253"/>
        <source>Show Pixels of Interest (H or Ctrl+I)</source>
        <translation>Mostra Pixel di Interesse (H o Ctrl+I)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1268"/>
        <source>Toggle AOI Circles</source>
        <translation>Attiva/disattiva Cerchi AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1275"/>
        <source>Toggle AOI Ruler</source>
        <translation>Mostra/nascondi righello AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1641"/>
        <source>Missing Dependency</source>
        <translation>Dipendenza Mancante</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1643"/>
        <source>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</source>
        <translation>Il modulo qimage2ndarray è richiesto per la funzione di upscale.
Installalo usando: pip install qimage2ndarray</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1652"/>
        <source>Upscale Error</source>
        <translation>Errore di Upscale</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1654"/>
        <source>An error occurred while opening the upscale dialog:
{error}</source>
        <translation>Si è verificato un errore durante l&apos;apertura della finestra di upscale:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1985"/>
        <source>Person Size Reference is unavailable: no GSD for this image</source>
        <translation>Riferimento dimensioni persona non disponibile: nessun GSD per questa immagine</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2082"/>
        <source>Unknown Reviewer</source>
        <translation>Revisore Sconosciuto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2145"/>
        <source>Loading gallery...</source>
        <translation>Caricamento galleria...</translation>
    </message>
</context>
<context>
    <name>WaldoPrePassDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="58"/>
        <source>Preparing WALDO Images</source>
        <translation>Preparazione immagini WALDO</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="70"/>
        <source>Synthesising WALDO metadata...</source>
        <translation>Generazione metadati WALDO...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="82"/>
        <source>Initialising...</source>
        <translation>Inizializzazione...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="93"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="96"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="146"/>
        <source>WALDO Pre-Pass Complete</source>
        <translation>Pre-pass WALDO completato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="147"/>
        <source>WALDO Pre-Pass Cancelled</source>
        <translation>Pre-pass WALDO annullato</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="154"/>
        <source>Processed:        {n}</source>
        <translation>Elaborate:        {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="155"/>
        <source>Already up-to-date: {n}</source>
        <translation>Già aggiornate: {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="156"/>
        <source>Skipped (non-WALDO): {n}</source>
        <translation>Saltate (non WALDO): {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="157"/>
        <source>Errors:           {n}</source>
        <translation>Errori:           {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="160"/>
        <source>Per-image errors:</source>
        <translation>Errori per immagine:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="174"/>
        <source>Cancelling...</source>
        <translation>Annullamento...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="175"/>
        <source>Cancellation requested...</source>
        <translation>Annullamento richiesto...</translation>
    </message>
</context>
<context>
    <name>WingtraDataDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="44"/>
        <source>Wingtra Data Import</source>
        <translation>Importazione Dati Wingtra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="54"/>
        <source>Import Summary</source>
        <translation>Riepilogo Importazione</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="58"/>
        <source>&lt;b&gt;Matched images:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV entries without match:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Result images without CSV data:&lt;/b&gt; {unmatched_images}</source>
        <translation>&lt;b&gt;Immagini abbinate:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;Voci CSV senza corrispondenza:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Immagini di risultato senza dati CSV:&lt;/b&gt; {unmatched_images}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="73"/>
        <source>Altitude &amp; GSD</source>
        <translation>Altitudine &amp; GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="78"/>
        <source>&lt;b&gt;AGL computed from terrain:&lt;/b&gt; {agl_count} of {matched_count} images&lt;br&gt;&lt;br&gt;Per-image AGL is derived from the CSV altitude (ASL) minus terrain elevation at each GPS location. GSD will be calculated automatically using the camera sensor data and focal length.</source>
        <translation>&lt;b&gt;AGL calcolata dal terreno:&lt;/b&gt; {agl_count} di {matched_count} immagini&lt;br&gt;&lt;br&gt;L&apos;AGL per immagine è derivata dall&apos;altitudine CSV (ASL) meno la quota del terreno in corrispondenza di ciascuna posizione GPS. Il GSD verrà calcolato automaticamente usando i dati del sensore della fotocamera e la lunghezza focale.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="89"/>
        <source>&lt;b&gt;Terrain data unavailable&lt;/b&gt; - AGL could not be computed.&lt;br&gt;&lt;br&gt;Orientation (yaw/pitch/roll) will still be applied from the CSV. GSD and altitude displays require terrain data or a manual altitude override (Shift+O) after import.</source>
        <translation>&lt;b&gt;Dati del terreno non disponibili&lt;/b&gt; - impossibile calcolare l&apos;AGL.&lt;br&gt;&lt;br&gt;L&apos;orientamento (yaw/pitch/roll) verrà comunque applicato dal CSV. Le visualizzazioni di GSD e altitudine richiedono i dati del terreno o un override manuale dell&apos;altitudine (Maiusc+O) dopo l&apos;importazione.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="106"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="110"/>
        <source>Apply Wingtra Data</source>
        <translation>Applica Dati Wingtra</translation>
    </message>
</context>
<context>
    <name>ZipExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="130"/>
        <source>Save Zip File</source>
        <translation>Salva File Zip</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="132"/>
        <source>Zip files (*.zip)</source>
        <translation>File Zip (*.zip)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="163"/>
        <source>No images to export</source>
        <translation>Nessuna immagine da esportare</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="397"/>
        <source>ZIP file created</source>
        <translation>File ZIP creato</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="403"/>
        <source>Failed to generate Zip file: {error}</source>
        <translation>Impossibile generare il file Zip: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="424"/>
        <source>Error</source>
        <translation>Errore</translation>
    </message>
</context>
<context>
    <name>ZipExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="18"/>
        <source>ZIP Export Options</source>
        <translation>Opzioni Esportazione ZIP</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="26"/>
        <source>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</source>
        <translation>Scegli cosa esportare:

- Nativo: immagini originali, maschere TIFF e XML (percorsi resi portabili).
- Aumentato: ciò che vedi nel visualizzatore (AOI/POI), mantiene EXIF/XMP.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="34"/>
        <source>Export Native data (original files + XML)</source>
        <translation>Esporta dati nativi (file originali + XML)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="35"/>
        <source>Export Augmented images (viewer overlays + metadata)</source>
        <translation>Esporta immagini aumentate (overlay visualizzatore + metadati)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="50"/>
        <source>Include images without flagged AOIs</source>
        <translation>Includi immagini senza AOI contrassegnate</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="53"/>
        <source>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</source>
        <translation>Quando deselezionato, verranno esportate solo le immagini con almeno una AOI contrassegnata.
Quando selezionato, verranno esportate tutte le immagini indipendentemente dallo stato delle AOI contrassegnate.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="59"/>
        <source>OK</source>
        <translation>OK</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="60"/>
        <source>Cancel</source>
        <translation>Annulla</translation>
    </message>
</context>
</TS>
