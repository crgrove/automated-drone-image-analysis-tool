<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="es_ES">
<context>
    <name>AIPersonDetector</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="27"/>
        <source>Confidence threshold for AI person detection.
Controls the minimum confidence level required to report a person detection.</source>
        <translation>Límite mínimo de confianza para la detección de personas con IA.
Controla el nivel mínimo de confianza requerido para reportar una detección de persona.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="31"/>
        <source>Confidence Threshold</source>
        <translation>Umbral de confianza</translation>
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
        <translation>Ajuste el límite mínimo de confianza para la detección de personas.
• Rango: 0% a 100% (deslizador -1 a 100, -1 se muestra como 0%)
• Predeterminado: 50%
El modelo de IA asigna un puntaje de confianza a cada detección de persona:
• Valores más bajos (0-30%): Aceptar detecciones de baja confianza (más detecciones, más falsos positivos)
• Valores medios (31-60%): Detección equilibrada (recomendado para la mayoría de los casos)
• Valores más altos (61-100%): Aceptar solo detecciones de alta confianza (menos detecciones, menos falsos positivos)
La confianza representa la certeza del modelo de IA de que un objeto detectado es una persona.
Empiece con 50% y ajuste según sus requisitos de precisión.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="81"/>
        <source>Current confidence threshold percentage.
Displays the value selected on the confidence slider (0-100%).
Detections below this confidence level will be filtered out.</source>
        <translation>Porcentaje de límite mínimo de confianza actual.
Muestra el valor seleccionado en el deslizador de confianza (0-100%).
Las detecciones por debajo de este nivel de confianza se filtrarán.</translation>
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
        <translation>Estado de la GPU e información de disponibilidad.
Muestra si la aceleración por GPU está disponible para la detección de personas con IA.
• GPU disponible: La detección con IA usará el GPU para un procesamiento más rápido
• Solo CPU: La detección con IA usará el CPU (más lento pero aún funcional)
La aceleración por GPU mejora significativamente la velocidad de procesamiento de los modelos de IA.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetector.ui" line="107"/>
        <source>GPU Label</source>
        <translation>Etiqueta de GPU</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="54"/>
        <source>Person Detection</source>
        <translation>Detección de personas</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="55"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Entradas y procesamiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="56"/>
        <source>Frame</source>
        <translation>Marco</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="57"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Renderizado y limpieza</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="78"/>
        <source>Model</source>
        <translation>Modelo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="80"/>
        <source>Force CPU (disable DirectML)</source>
        <translation>Forzar CPU (desactivar DirectML)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="81"/>
        <source>Use 1024 model (higher quality, slower)</source>
        <translation>Usar modelo 1024 (mayor calidad, más lento)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="86"/>
        <source>Detection</source>
        <translation>Detección</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/views/AIPersonDetectorControlWidget.py" line="91"/>
        <source>Confidence Threshold:</source>
        <translation>Nivel mínimo de confianza:</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="81"/>
        <source>GPU Not Available</source>
        <translation>GPU no disponible</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorController.py" line="87"/>
        <source>GPU Available</source>
        <translation>GPU disponible</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="91"/>
        <source>FPS: {fps} | Processing: {ms}ms</source>
        <translation>FPS: {fps} | Procesamiento: {ms}ms</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorController.py" line="96"/>
        <source>{status} | Tile fallback active</source>
        <translation>{status} | Respaldo de mosaicos activo</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizard</name>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="40"/>
        <source>How confident should ADIAT be before marking something as a person?</source>
        <translation>¿Qué nivel de confianza debe tener ADIAT antes de marcar algo como una persona?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/AIPersonDetectorWizard.ui" line="56"/>
        <source>Note: A higher setting may increase false positives.</source>
        <translation>Nota: Un valor más alto puede aumentar los positivos falsos.</translation>
    </message>
</context>
<context>
    <name>AIPersonDetectorWizardController</name>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="33"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="52"/>
        <source>Very 
Confident</source>
        <translation>Muy 
confiado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="34"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="53"/>
        <source>Confident</source>
        <translation>Confiado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="35"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="54"/>
        <source>Balanced</source>
        <translation>Equilibrado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="36"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="55"/>
        <source>Permissive</source>
        <translation>Permisivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="37"/>
        <location filename="../app/algorithms/streaming/AIPersonDetector/controllers/AIPersonDetectorWizardController.py" line="56"/>
        <source>Very 
Permissive</source>
        <translation>Muy 
permisivo</translation>
    </message>
</context>
<context>
    <name>AOICommentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="27"/>
        <source>AOI Comment</source>
        <translation>Comentario de AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="37"/>
        <source>Add a comment for this flagged AOI (max 256 characters):</source>
        <translation>Añadir un comentario para este AOI marcado (máx. 256 caracteres):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="44"/>
        <source>Enter your comment here...</source>
        <translation>Escriba su comentario aquí...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="57"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICommentDialog.py" line="59"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>AOIController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="380"/>
        <source>No AOI #{number} in this analysis.</source>
        <translation>No hay ningún AOI #{number} en este análisis.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="393"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="403"/>
        <source>AOI #{number} is hidden by the current filter.</source>
        <translation>El AOI #{number} está oculto por el filtro actual.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="699"/>
        <source>Comment saved</source>
        <translation>Comentario guardado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="701"/>
        <source>Comment cleared</source>
        <translation>Comentario borrado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="790"/>
        <source>Copy Data</source>
        <translation>Copiar datos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="796"/>
        <source>Find Similar AOIs</source>
        <translation>Buscar AOI similares</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="899"/>
        <source>AOI data copied</source>
        <translation>Datos del AOI copiados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="986"/>
        <source>Invalid image index</source>
        <translation>Índice de imagen no válido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="991"/>
        <source>Invalid AOI index</source>
        <translation>Índice de AOI no válido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1054"/>
        <source>Could not calculate AOI location. Diagnostic info copied to clipboard!</source>
        <translation>No se pudo calcular la ubicación del AOI. ¡Información de diagnóstico copiada al portapapeles!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1060"/>
        <source>Could not calculate AOI location</source>
        <translation>No se pudo calcular la ubicación del AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1517"/>
        <source>Temperature sorting unavailable (no thermal data)</source>
        <translation>Ordenación por temperatura no disponible (no existen datos térmicos)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1869"/>
        <source>Cannot Delete AOI</source>
        <translation>No se puede eliminar el AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1871"/>
        <source>Only manually created AOIs can be deleted. Algorithm-detected AOIs cannot be deleted.</source>
        <translation>Solo se pueden eliminar los AOI creados manualmente. Los AOI detectados por el algoritmo no se pueden eliminar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1880"/>
        <source>Delete AOI</source>
        <translation>Eliminar AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIController.py" line="1882"/>
        <source>Are you sure you want to delete this AOI? This action cannot be undone.</source>
        <translation>¿Está seguro de que desea eliminar este AOI? Esta acción no se puede deshacer.</translation>
    </message>
</context>
<context>
    <name>AOICreationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="23"/>
        <source>Create AOI</source>
        <translation>Crear AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="31"/>
        <source>Create AOI?</source>
        <translation>¿Crear AOI?</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="39"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOICreationDialog.py" line="43"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>AOIFilterDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="74"/>
        <source>Filter AOIs</source>
        <translation>Filtrar AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="91"/>
        <source>Filter Areas of Interest by flagged status, comments, color, and/or pixel area:</source>
        <translation>Filtrar áreas de interés por estado marcado, comentarios, color y/o área de píxeles:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="96"/>
        <source>Flagged AOIs</source>
        <translation>AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="99"/>
        <source>Show Only Flagged AOIs</source>
        <translation>Mostrar solo AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="103"/>
        <source>Only AOIs marked with a flag will be displayed</source>
        <translation>Solo se mostrarán los AOI marcados con una marca</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="111"/>
        <source>Comment Filter</source>
        <translation>Filtro de comentario</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="115"/>
        <source>Enable Comment Filter</source>
        <translation>Habilitar filtro de comentario</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="122"/>
        <source>Pattern:</source>
        <translation>Patrón:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="125"/>
        <source>e.g., damage or crack</source>
        <translation>p. ej., daño o grieta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="133"/>
        <source>Case-insensitive substring match (e.g. &quot;blue&quot; matches &quot;blueface&quot;)</source>
        <translation>Coincidencia de subcadena sin distinción entre mayúsculas y minúsculas (p. ej., &quot;azul&quot; coincide con &quot;azulado&quot;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="137"/>
        <source>Only AOIs with non-empty comments matching the pattern will be shown</source>
        <translation>Solo se mostrarán los AOI con comentarios no vacíos que coincidan con el patrón</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="145"/>
        <source>Color Filter</source>
        <translation>Filtro de color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="149"/>
        <source>Enable Color Filter</source>
        <translation>Habilitar filtro de color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="156"/>
        <source>Show Only This Color</source>
        <translation>Mostrar solo este color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="157"/>
        <source>Exclude This Color</source>
        <translation>Excluir este color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="174"/>
        <source>Target Hue:</source>
        <translation>Matiz objetiva:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="176"/>
        <source>Select Color</source>
        <translation>Seleccionar color</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="188"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="556"/>
        <source>No color selected</source>
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="196"/>
        <source>Hue Range (±):</source>
        <translation>Rango de matiz (±):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="214"/>
        <source>AOIs with hue within ±range of target will be shown</source>
        <translation>Se mostrarán los AOI con la matiz dentro del ±rango del objetivo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="222"/>
        <source>Pixel Area Filter</source>
        <translation>Filtro de área de píxeles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="226"/>
        <source>Enable Pixel Area Filter</source>
        <translation>Habilitar filtro de área de píxeles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="233"/>
        <source>Minimum Area (px):</source>
        <translation>Área mínima (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="247"/>
        <source>Maximum Area (px):</source>
        <translation>Área máxima (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="263"/>
        <source>Temperature Filter</source>
        <translation>Filtro de temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="267"/>
        <source>Enable Temperature Filter</source>
        <translation>Habilitar filtro de temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="321"/>
        <source>Temperature filtering unavailable (no thermal data)</source>
        <translation>Filtrado de temperatura no disponible (no hay datos térmicos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="336"/>
        <source>Spatial Filters</source>
        <translation>Filtros espaciales</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="341"/>
        <source>Detection Density Heatmap</source>
        <translation>Mapa de calor de densidad de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="347"/>
        <source>Off</source>
        <translation>Desactivado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="348"/>
        <source>Filter Hot Zones</source>
        <translation>Filtrar zonas calientes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="349"/>
        <source>Show Hot Zones Only</source>
        <translation>Mostrar solo zonas calientes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="374"/>
        <source>Threshold:</source>
        <translation>Límite Mínimo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="392"/>
        <source>View Heatmap</source>
        <translation>Ver mapa de calor</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="405"/>
        <source>Heatmap filtering unavailable (image dimensions not in dataset)</source>
        <translation>Filtrado por mapa de calor no disponible (las dimensiones de la imagen no están en el conjunto de datos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="418"/>
        <source>Image Mask Filter</source>
        <translation>Filtro de máscara de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="422"/>
        <source>Enable Image Mask Filter</source>
        <translation>Habilitar filtro de máscara de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="429"/>
        <source>Show Only Detections in Mask</source>
        <translation>Mostrar solo detecciones en la máscara</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="430"/>
        <source>Exclude Detections in Mask</source>
        <translation>Excluir detecciones en la máscara</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="449"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="630"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="690"/>
        <source>No mask image selected</source>
        <translation>Ninguna imagen de máscara seleccionada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="454"/>
        <source>Browse...</source>
        <translation>Navegar...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="458"/>
        <source>Clear</source>
        <translation>Borrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="465"/>
        <source>White regions = areas of interest. Mask is scaled to each image&apos;s dimensions.</source>
        <translation>Regiones blancas = áreas de interés. La máscara se escala a las dimensiones de cada imagen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="483"/>
        <source>Clear All Filters</source>
        <translation>Borrar todos los filtros</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="489"/>
        <source>Apply</source>
        <translation>Aplicar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="494"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="531"/>
        <source>Select Target Hue</source>
        <translation>Seleccionar objetivo de la matiz</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="607"/>
        <source>Select Mask Image</source>
        <translation>Seleccionar imagen de máscara</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="609"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)</source>
        <translation>Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff);;Todos los archivos (*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="618"/>
        <source>Invalid Image</source>
        <translation>Imagen no válida</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="619"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>No se pudo cargar la imagen seleccionada. Elija un archivo de imagen válido.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="637"/>
        <source>AOIs in high-density zones (above threshold) will be hidden</source>
        <translation>Los AOI en zonas de alta densidad (por encima del límite mínimo) se ocultarán</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="640"/>
        <source>Only AOIs in high-density zones (above threshold) will be shown</source>
        <translation>Solo se mostrarán los AOI en zonas de alta densidad (por encima del nivel mínimo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="643"/>
        <source>Heatmap spatial filtering is disabled</source>
        <translation>El filtrado espacial por mapa de calor está desactivado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="649"/>
        <source>Heatmap</source>
        <translation>Mapa de calor</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOIFilterDialog.py" line="650"/>
        <source>No heatmap data available. Ensure image dimensions are present in the dataset.</source>
        <translation>No hay datos de mapa de calor disponibles. Asegúrese de que las dimensiones de la imagen estén en el conjunto de datos.</translation>
    </message>
</context>
<context>
    <name>AOINeighborGalleryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="341"/>
        <source>AOI in Neighboring Images</source>
        <translation>AOI en imágenes vecinas</translation>
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
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="414"/>
        <source>Reset View</source>
        <translation>Restablecer vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="417"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Restablecer el zoom y ajustar todas las miniaturas a la vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="424"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
</context>
<context>
    <name>AOINeighborTrackingController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="192"/>
        <source>No AOI Selected</source>
        <translation>Ningún AOI seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="193"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Primero seleccione un AOI haciendo clic sobre él en el panel de miniaturas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="404"/>
        <source>Cannot Calculate GPS</source>
        <translation>No se puede calcular GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="406"/>
        <source>Unable to calculate GPS coordinates for this AOI.

This may be due to missing image metadata (GPS, altitude, or camera info).</source>
        <translation>No se pueden calcular las coordenadas GPS para este AOI.

Puede deberse a la falta de metadatos de imagen (GPS, altitud o información de cámara).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="225"/>
        <source>Searching for AOI in neighboring images...</source>
        <translation>Buscando AOI en imágenes vecinas...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="226"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="230"/>
        <source>Tracking AOI</source>
        <translation>Rastreando AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="297"/>
        <source>Tracking Error</source>
        <translation>Error de rastreo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="298"/>
        <source>An error occurred while tracking the AOI:
{error}</source>
        <translation>Se produjo un error al rastrear el AOI:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="436"/>
        <source>No Neighbors Found</source>
        <translation>No se encontraron imágenes vecinas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="437"/>
        <source>The AOI was not found in any neighboring images.</source>
        <translation>El AOI no se encontró en ninguna imagen vecina.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="467"/>
        <source>Search Error</source>
        <translation>Error de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="468"/>
        <source>An error occurred during the search:
{error}</source>
        <translation>Se produjo un error durante la búsqueda:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="584"/>
        <source> (no detections)</source>
        <translation> (sin detecciones)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="599"/>
        <source>Display Error</source>
        <translation>Error de visualización</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/neighbor/AOINeighborTrackingController.py" line="600"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Se produjo un error al mostrar los resultados:
{error}</translation>
    </message>
</context>
<context>
    <name>AOISimilarityController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="141"/>
        <source>No AOI Selected</source>
        <translation>No se ha seleccionado ningún AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="142"/>
        <source>Please select an AOI first by clicking on it in the thumbnail panel.</source>
        <translation>Seleccione primero un AOI haciendo clic en él en el panel de miniaturas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="159"/>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="311"/>
        <source>Similarity Search Error</source>
        <translation>Error de búsqueda de similitud</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="160"/>
        <source>An error occurred while starting the similarity search:
{error}</source>
        <translation>Se produjo un error al iniciar la búsqueda de similitud:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="171"/>
        <source>Analyzing AOIs for visual similarity...</source>
        <translation>Analizando AOI por similitud visual...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="172"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="176"/>
        <source>Find Similar AOIs</source>
        <translation>Buscar AOI similares</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="233"/>
        <source>Analyzing AOI {done} of {total}...</source>
        <translation>Analizando AOI {done} de {total}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="278"/>
        <source>No Similar AOIs</source>
        <translation>No hay AOI similares</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="279"/>
        <source>No other AOIs could be analyzed for similarity.</source>
        <translation>No se pudo analizar ningún otro AOI para buscar similitud.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="312"/>
        <source>The similarity search could not be completed:
{error}</source>
        <translation>No se pudo completar la búsqueda de similitud:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="418"/>
        <source>Display Error</source>
        <translation>Error de visualización</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="419"/>
        <source>An error occurred while displaying results:
{error}</source>
        <translation>Se produjo un error al mostrar los resultados:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="471"/>
        <source>Flagged {count} AOI(s)</source>
        <translation>{count} AOI marcado(s)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="474"/>
        <source>Removed flag from {count} AOI(s)</source>
        <translation>Marca quitada de {count} AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="506"/>
        <source>Comment saved on {count} AOI(s)</source>
        <translation>Comentario guardado en {count} AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/similarity/AOISimilarityController.py" line="509"/>
        <source>Comment cleared on {count} AOI(s)</source>
        <translation>Comentario borrado en {count} AOI</translation>
    </message>
</context>
<context>
    <name>AOISimilarityResultsDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="442"/>
        <source>Similar AOIs</source>
        <translation>AOI similares</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="479"/>
        <source>Top {shown} of {total} AOIs ranked by similarity to {reference}. Use mouse wheel to zoom, right-click drag to pan. Click a thumbnail to jump to that AOI.</source>
        <translation>Los {shown} primeros de {total} AOI ordenados por similitud con {reference}. Use la rueda del ratón para hacer zoom, arrastre con clic derecho para desplazar la vista. Haga clic en una miniatura para ir a ese AOI.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="500"/>
        <source>Select All</source>
        <translation>Seleccionar todo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="504"/>
        <source>Clear Selection</source>
        <translation>Borrar selección</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="508"/>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="556"/>
        <source>{count} selected</source>
        <translation>{count} seleccionados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="514"/>
        <source>Flag</source>
        <translation>Marcar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="515"/>
        <source>Flag all checked AOIs</source>
        <translation>Marcar todos los AOI seleccionados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="520"/>
        <source>Unflag</source>
        <translation>Desmarcar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="521"/>
        <source>Remove the flag from all checked AOIs</source>
        <translation>Quitar la marca de todos los AOI seleccionados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="526"/>
        <source>Comment...</source>
        <translation>Comentario...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="527"/>
        <source>Add or edit the comment on all checked AOIs</source>
        <translation>Añadir o editar el comentario en todos los AOI seleccionados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="538"/>
        <source>Reset View</source>
        <translation>Restablecer vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="541"/>
        <source>Reset zoom and fit all thumbnails in view</source>
        <translation>Restablecer el zoom y ajustar todas las miniaturas a la vista</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="546"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="581"/>
        <source>AOI #{number}</source>
        <translation>AOI #{number}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="582"/>
        <source>the selected AOI</source>
        <translation>el AOI seleccionado</translation>
    </message>
</context>
<context>
    <name>AOIUIComponent</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="250"/>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="346"/>
        <source>AOI Information
Right-click to copy data to clipboard</source>
        <translation>Información del AOI
Clic derecho para copiar los datos al portapapeles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="256"/>
        <source>

Score Type: {type}
Raw Score: {score} ({method})</source>
        <translation>

Tipo de puntaje: {type}
Puntaje bruto: {score} ({method})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="320"/>
        <source>Confidence Score: {score:.1f}%</source>
        <translation>Puntaje de confianza: {score:.1f}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Unflag AOI</source>
        <translation>Desmarcar AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="386"/>
        <source>Flag AOI</source>
        <translation>Marcar AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="403"/>
        <source>Comment:
{comment}

Click to edit comment</source>
        <translation>Comentario:
{comment}

Haga clic para editar el comentario</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="411"/>
        <source>No comment yet.
Click to add a comment for this AOI.

Use comments to note important details, observations,
or actions needed for this detection.</source>
        <translation>Todavía no hay comentarios.
Haga clic para añadir un comentario para este AOI.

Use los comentarios para anotar detalles importantes, observaciones
o acciones necesarias para esta detección.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="428"/>
        <source>Calculate and show GPS location for this AOI</source>
        <translation>Calcular y mostrar la ubicación GPS de este AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="446"/>
        <source>Delete this AOI</source>
        <translation>Eliminar este AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Area</source>
        <translation>Área</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="484"/>
        <source>Areas</source>
        <translation>Áreas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="486"/>
        <source>{filtered} of {total} {label}</source>
        <translation>{filtered} de {total} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="495"/>
        <source>Area of Interest</source>
        <translation>Área de interés</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="497"/>
        <source>Areas of Interest</source>
        <translation>Áreas de interés</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="500"/>
        <source>{count} {label}</source>
        <translation>{count} {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="643"/>
        <source>Loading AOIs...</source>
        <translation>Cargando AOI...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/aoi/AOIUIComponent.py" line="684"/>
        <source>Loading AOIs... ({current}/{total})</source>
        <translation>Cargando AOI... ({current}/{total})</translation>
    </message>
</context>
<context>
    <name>AlertManager</name>
    <message>
        <location filename="../app/core/services/AlertService.py" line="294"/>
        <source>ADIAT - Color Detection Alerts</source>
        <translation>ADIAT - Alertas de detección de color</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="569"/>
        <source>ADIAT - Color Detection Alert</source>
        <translation>ADIAT - Alerta de detección de color</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="610"/>
        <source>Detected {count} object(s)
Average confidence: {avg_confidence:.2f}
Total area: {area:.0f} pixels
</source>
        <translation>Se detectaron {count} objetos
Confianza media: {avg_confidence:.2f}
Área total: {area:.0f} píxeles
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="620"/>
        <source>
Details:
</source>
        <translation>
Detalles:
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="624"/>
        <source>  #{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}
</source>
        <translation>  n.º{index}: ({x},{y}) {w}x{h} conf:{confidence:.2f}
</translation>
    </message>
    <message>
        <location filename="../app/core/services/AlertService.py" line="644"/>
        <source>ADIAT - Detection Alert</source>
        <translation>ADIAT - Alerta de detección</translation>
    </message>
</context>
<context>
    <name>AlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmParametersPage.py" line="165"/>
        <source>{algorithm} Algorithm Settings</source>
        <translation>Configuración del algoritmo {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlgorithmSelectionPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="92"/>
        <source>Are you using thermal images?</source>
        <translation>¿Está usando imágenes térmicas?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="156"/>
        <source>Are you looking for anomalies within a specific temperature range?</source>
        <translation>¿Está buscando anomalías dentro de un rango de temperatura específico?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="159"/>
        <source>Do you specifically want to detect people?</source>
        <translation>¿Quiere detectar personas específicamente?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="168"/>
        <source>Do you want to detect anomalies relative to local surroundings?</source>
        <translation>¿Quiere detectar anomalías relativas al entorno local?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="185"/>
        <source>Are you trying to find a specific color?</source>
        <translation>¿Está intentando encontrar un color específico?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="190"/>
        <source>Do you want to manually adjust the color range?</source>
        <translation>¿Quiere ajustar manualmente el rango de color?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="193"/>
        <source>Do your images contain complex backgrounds or structures?</source>
        <translation>¿Sus imágenes contienen fondos o estructuras complejas?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="200"/>
        <source>Do your images include shadows or areas with uneven lighting?</source>
        <translation>¿Sus imágenes incluyen sombras o áreas con iluminación desigual?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/AlgorithmSelectionPage.py" line="226"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Algoritmo seleccionado: {algorithm}</translation>
    </message>
</context>
<context>
    <name>AlignImageController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="46"/>
        <source>No image available to align</source>
        <translation>No hay una imagen disponible para alinear</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="52"/>
        <source>This image has no GPS data and cannot be aligned</source>
        <translation>Esta imagen no tiene datos GPS y no se puede alinear</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="84"/>
        <source>Could not save the alignment</source>
        <translation>No se pudo guardar la alineación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AlignImageController.py" line="95"/>
        <source>Image alignment saved</source>
        <translation>Alineación de imagen guardada</translation>
    </message>
</context>
<context>
    <name>AlignImageDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="53"/>
        <source>This saved alignment looks mirrored - re-place each corner handle on its matching photo corner (coloured squares).</source>
        <translation>Esta alineación guardada parece estar invertida: vuelva a colocar cada tirador de esquina sobre la esquina correspondiente de la foto (cuadros de color).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="60"/>
        <source>Align Image</source>
        <translation>Alinear imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="130"/>
        <source>Rotate the drone image to line it up with the map. The small coloured squares mark the photo&apos;s corners - drag each corner handle onto the map where its matching-coloured photo corner belongs. For extra accuracy, add tie points: put the IMAGE end on a feature in the drone photo and the MAP end on the same feature on the map.</source>
        <translation>Gire la imagen del dron para alinearla con el mapa. Los cuadros de color pequeños marcan las esquinas de la foto: arrastre cada tirador de esquina en el mapa hasta el lugar donde corresponde la esquina de la foto del mismo color. Para mayor precisión, añada puntos de amarre: coloque el extremo IMAGEN sobre un rasgo de la foto del dron y el extremo MAPA sobre el mismo rasgo en el mapa.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="137"/>
        <source>Rotation:</source>
        <translation>Rotación:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="138"/>
        <source>Map opacity:</source>
        <translation>Opacidad del mapa:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="139"/>
        <source>FOV overlay opacity:</source>
        <translation>Opacidad de la superposición del FOV:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="140"/>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="192"/>
        <source>Show Street Map</source>
        <translation>Mostrar mapa de calles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="141"/>
        <source>Add Tie Point</source>
        <translation>Añadir punto de amarre</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="142"/>
        <source>Reset</source>
        <translation>Restablecer</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="195"/>
        <source>Show Satellite</source>
        <translation>Mostrar satélite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="218"/>
        <source>Corners look mirrored</source>
        <translation>Las esquinas parecen invertidas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="220"/>
        <source>The four corners appear mirrored - the drone image would map to the ground flipped.

Each corner handle is colour-matched to a corner of the drone photo (the small coloured squares). Make sure every handle sits where its matching photo corner belongs.</source>
        <translation>Las cuatro esquinas parecen invertidas: la imagen del dron se proyectaría volteada sobre el terreno.

Cada tirador de esquina tiene el mismo color que una esquina de la foto del dron (los cuadros de color pequeños). Asegúrese de que cada tirador esté donde corresponde su esquina de foto coincidente.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AlignImageDialog.py" line="230"/>
        <source>Go Back and Fix</source>
        <translation>Volver y corregir</translation>
    </message>
</context>
<context>
    <name>AlignImageView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="425"/>
        <source>IMAGE</source>
        <translation>IMAGEN</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="427"/>
        <source>MAP</source>
        <translation>MAPA</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/AlignImageView.py" line="672"/>
        <source>Remove Tie Point</source>
        <translation>Quitar punto de amarre</translation>
    </message>
</context>
<context>
    <name>AltitudeController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>meters</source>
        <translation>metros</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="98"/>
        <source>feet</source>
        <translation>pies</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="109"/>
        <source>Negative Altitude Detected</source>
        <translation>Altitud negativa detectada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="111"/>
        <source>WARNING! Relative Altitude is negative. Enter an AGL altitude to be used for GSD calculations (in {unit}):</source>
        <translation>¡ADVERTENCIA! La altitud relativa es negativa. Introduzca una altitud AGL para usarla en los cálculos de GSD (en {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="130"/>
        <source>Override Altitude</source>
        <translation>Reemplazar altitud</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="132"/>
        <source>Enter a custom AGL altitude to be used for GSD calculations for all images (in {unit}):</source>
        <translation>Introduzca una altitud AGL personalizada para usarla en los cálculos de GSD de todas las imágenes (en {unit}):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/AltitudeController.py" line="180"/>
        <source>Custom AGL set to {value:.1f} {unit}</source>
        <translation>AGL personalizado establecido a {value:.1f} {unit}</translation>
    </message>
</context>
<context>
    <name>AnalyzeService</name>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="161"/>
        <source>Processing {count} files</source>
        <translation>Procesando {count} archivos</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="205"/>
        <source>Skipping {file} :: File is not an image</source>
        <translation>Omitiendo {file} :: El archivo no es una imagen</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="210"/>
        <source>All {count} images queued, processing started...</source>
        <translation>Las {count} imágenes se han puesto en una fila, procesamiento iniciado...</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="268"/>
        <source>{images} images with {aois} areas of interest identified</source>
        <translation>{images} imágenes con {aois} áreas de interés identificadas</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="274"/>
        <source>Total Processing Time: {seconds} seconds</source>
        <translation>Tiempo total de procesamiento: {seconds} segundos</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="277"/>
        <source>Total Images Processed: {count}</source>
        <translation>Imágenes totales procesadas: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="495"/>
        <source>Unable to process {file} :: {error} ({percent}%)</source>
        <translation>No se pudo procesar {file} :: {error} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="518"/>
        <source>{count} areas of interest identified in {file} ({percent}%)</source>
        <translation>{count} áreas de interés identificadas en {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="535"/>
        <source>No areas of interest identified in {file} ({percent}%)</source>
        <translation>No se identificaron áreas de interés en {file} ({percent}%)</translation>
    </message>
    <message>
        <location filename="../app/core/services/AnalyzeService.py" line="617"/>
        <source>--- Cancelling Image Processing ---</source>
        <translation>--- Cancelando procesamiento de imágenes ---</translation>
    </message>
</context>
<context>
    <name>BearingRecoveryDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="124"/>
        <source>Missing Bearings Detected</source>
        <translation>Rumbos faltantes detectados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="132"/>
        <source>Some images are missing bearing/heading information. We can estimate bearings from a flight track file (KML/GPX/CSV) or calculate them automatically from image GPS coordinates.</source>
        <translation>A algunas imágenes les falta información de rumbo/dirección. Podemos estimar los rumbos a partir de un archivo de ruta de vuelo (KML/GPX/CSV) o calcularlos automáticamente a partir de las coordenadas GPS de las imágenes.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="150"/>
        <source>📁 Load Track File (KML/GPX/CSV)</source>
        <translation>📁 Cargar archivo de ruta (KML/GPX/CSV)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="156"/>
        <source>🧭 Auto-Calculate from Image GPS</source>
        <translation>🧭 Calcular automáticamente desde el GPS de la imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="174"/>
        <source>Preparing...</source>
        <translation>Preparando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="190"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="195"/>
        <source>Skip</source>
        <translation>Omitir</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="259"/>
        <source>Select Track File</source>
        <translation>Seleccionar archivo de ruta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="261"/>
        <source>Track Files (*.kml *.gpx *.csv);;KML Files (*.kml);;GPX Files (*.gpx);;CSV Files (*.csv);;All Files (*.*)</source>
        <translation>Archivos de ruta (*.kml *.gpx *.csv);;Archivos KML (*.kml);;Archivos GPX (*.gpx);;Archivos CSV (*.csv);;Todos los archivos (*.*)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="345"/>
        <source>Bearings set for {count} images ({source})</source>
        <translation>Rumbos establecidos para {count} imágenes ({source})</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="350"/>
        <source>, {count} flagged near turns</source>
        <translation>, {count} marcados cerca de giros</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="352"/>
        <source>, {count} hover estimates</source>
        <translation>, {count} estimaciones de vuelo estacionario</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="354"/>
        <source>, {count} time gaps</source>
        <translation>, {count} intervalos de tiempo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="361"/>
        <source>Bearing Calculation Complete</source>
        <translation>Cálculo de rumbo completado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="362"/>
        <source>{summary}.</source>
        <translation>{summary}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="389"/>
        <source>Bearing Calculation Failed</source>
        <translation>Error en el cálculo de rumbo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="391"/>
        <source>An error occurred during bearing calculation:

{error}

Please check your input files and try again.</source>
        <translation>Se produjo un error durante el cálculo de rumbo:

{error}

Compruebe sus archivos de entrada e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="411"/>
        <source>Cancelled</source>
        <translation>Cancelado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="422"/>
        <source>Cancelling...</source>
        <translation>Cancelando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="435"/>
        <source>Bearing Recovery Not Needed</source>
        <translation>Recuperación de rumbo no necesaria</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="437"/>
        <source>Bearing recovery requires multiple images to calculate direction of travel.

With only one image, bearing recovery cannot be performed.</source>
        <translation>La recuperación de rumbo requiere varias imágenes para calcular la dirección de desplazamiento.

Con solo una imagen, no se puede realizar la recuperación de rumbo.</translation>
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
&lt;h3&gt;¿Qué es la Recuperación de rumbo?&lt;/h3&gt;

&lt;p&gt;El &lt;b&gt;rumbo&lt;/b&gt; (también llamado dirección, guiñada o curso) es la dirección hacia la que apuntaba
el dron/cámara cuando se capturó una imagen, medida en grados en sentido horario desde el Norte (0-360°).&lt;/p&gt;

&lt;h4&gt;¿Por qué es importante?&lt;/h4&gt;
&lt;p&gt;Los rumbos son esenciales para:&lt;/p&gt;
&lt;ul&gt;
&lt;li&gt;Georreferenciación y cartografía precisas&lt;/li&gt;
&lt;li&gt;Alineación y unión correcta de imágenes&lt;/li&gt;
&lt;li&gt;Comprender el campo de visión de la cámara&lt;/li&gt;
&lt;li&gt;Análisis de objetos detectados en contexto geográfico&lt;/li&gt;
&lt;/ul&gt;

&lt;h4&gt;Métodos de recuperación:&lt;/h4&gt;

&lt;p&gt;&lt;b&gt;Cargar archivo de ruta (KML/GPX/CSV)&lt;/b&gt;&lt;br/&gt;
Utiliza un registro de ruta GPS externo de su dron o controlador de vuelo. La ruta contiene
posiciones con marca de tiempo que permiten una interpolación precisa del rumbo. Método más exacto.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Calcular automáticamente desde el GPS de la imagen&lt;/b&gt;&lt;br/&gt;
Estima los rumbos usando solo las coordenadas GPS incrustadas en sus imágenes. Analiza el
patrón de vuelo para determinar la dirección de desplazamiento. Funciona bien con patrones de vuelo sistemáticos
como los barridos en zigzag.&lt;/p&gt;

&lt;p&gt;&lt;b&gt;Omitir&lt;/b&gt;&lt;br/&gt;
Continuar sin recuperación de rumbo. Es posible que algunas funciones no funcionen correctamente.&lt;/p&gt;
        </translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/BearingRecoveryDialog.py" line="483"/>
        <source>About Bearing Recovery</source>
        <translation>Acerca de la recuperación de rumbo</translation>
    </message>
</context>
<context>
    <name>CacheLocationDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="35"/>
        <source>Cache Not Found</source>
        <translation>Caché no encontrada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="47"/>
        <source>Cached Data Not Found</source>
        <translation>Datos en caché no encontrados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="56"/>
        <source>The following cached items were not found:
</source>
        <translation>No se encontraron los siguientes elementos en caché:
</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="66"/>
        <source>Without cached data, thumbnails and colors will be generated on-demand, which may cause delays when viewing results.

If you have previously processed this dataset and have an ADIAT_Results folder with cached data, you can locate it now to improve performance.</source>
        <translation>Sin datos en caché, las miniaturas y los colores se generarán bajo demanda, lo que puede causar retrasos al ver los resultados.

Si ha procesado previamente este conjunto de datos y tiene una carpeta ADIAT_Results con datos en caché, puede localizarla ahora para mejorar el rendimiento.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="80"/>
        <source>Locate Cache Folder...</source>
        <translation>Localizar carpeta de caché...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="85"/>
        <source>Skip (Generate On-Demand)</source>
        <translation>Omitir (Generar bajo demanda)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="122"/>
        <source>Select ADIAT_Results Folder</source>
        <translation>Seleccionar carpeta ADIAT_Results</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="136"/>
        <source>Invalid Cache Folder</source>
        <translation>Carpeta de caché no válida</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CacheLocationDialog.py" line="138"/>
        <source>The selected folder does not contain thumbnail cache directory.

Expected to find:
  • .thumbnails/

Please select a valid ADIAT_Results folder.</source>
        <translation>La carpeta seleccionada no contiene el directorio de caché de miniaturas.

Se esperaba encontrar:
  • .thumbnails/

Seleccione una carpeta ADIAT_Results válida.</translation>
    </message>
</context>
<context>
    <name>CalTopoAPIMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="42"/>
        <source>Select CalTopo Map</source>
        <translation>Seleccionar mapa de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="68"/>
        <source>Select a CalTopo map:</source>
        <translation>Seleccione un mapa de CalTopo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="77"/>
        <source>Search:</source>
        <translation>Búsqueda:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="79"/>
        <source>Filter maps by name...</source>
        <translation>Filtrar mapas por nombre...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="111"/>
        <source>Update Credentials</source>
        <translation>Actualizar credenciales</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="117"/>
        <source>Select Map</source>
        <translation>Seleccionar mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="121"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="150"/>
        <source>No account data available.</source>
        <translation>No hay datos de cuenta disponibles.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="515"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="540"/>
        <source>Credentials Updated</source>
        <translation>Credenciales actualizadas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="516"/>
        <source>Credentials have been updated and the map list has been refreshed.</source>
        <translation>Las credenciales se han actualizado y la lista de mapas se ha renovado.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="521"/>
        <source>Update Failed</source>
        <translation>Error de actualización</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="523"/>
        <source>Failed to refresh account data with new credentials.

Please check your credentials and try again.</source>
        <translation>Error al actualizar los datos de la cuenta con las nuevas credenciales.

Compruebe sus credenciales e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="530"/>
        <source>Update Error</source>
        <translation>Error de actualización</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="531"/>
        <source>An error occurred while updating credentials:

{error}</source>
        <translation>Se produjo un error al actualizar las credenciales:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="542"/>
        <source>Credentials have been updated. Please close and reopen this dialog to refresh the map list.</source>
        <translation>Las credenciales se han actualizado. Cierre y vuelva a abrir este diálogo para renovar la lista de mapas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="559"/>
        <source>No Map Selected</source>
        <translation>Ningún mapa seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAPIMapDialog.py" line="560"/>
        <source>Please select a map from the list.</source>
        <translation>Seleccione un mapa de la lista.</translation>
    </message>
</context>
<context>
    <name>CalTopoAuthDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="155"/>
        <source>CalTopo Login &amp; Map Selection</source>
        <translation>Inicio de sesión y selección de mapa de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="240"/>
        <source>Current map: Not selected</source>
        <translation>Mapa actual: No seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="244"/>
        <source>(Login → Navigate to your map → Click &apos;I&apos;m Logged In&apos;)</source>
        <translation>(Inicie sesión → Vaya a su mapa → Haga clic en &apos;He iniciado sesión&apos;)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="258"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="799"/>
        <source>I&apos;m Logged In - Export Data</source>
        <translation>He iniciado sesión - Exportar datos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="260"/>
        <source>Click this after logging in and navigating to your map</source>
        <translation>Haga clic en esto tras iniciar sesión y navegar hasta su mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="263"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="369"/>
        <source>Initialization Error</source>
        <translation>Error de inicialización</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="370"/>
        <source>Failed to initialize CalTopo browser:
{error}</source>
        <translation>Error al inicializar el navegador de CalTopo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="414"/>
        <source>Failed to Load</source>
        <translation>Error al cargar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="416"/>
        <source>Failed to load CalTopo. Please check your internet connection and try again.</source>
        <translation>Error al cargar CalTopo. Compruebe su conexión a Internet e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="447"/>
        <source>Current map: {map_id}</source>
        <translation>Mapa actual: {map_id}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="475"/>
        <source>No Map Selected</source>
        <translation>Ningún mapa seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="477"/>
        <source>Please navigate to a CalTopo map before capturing the session.

The map URL should contain a map ID (e.g., /m/ABC123 or #id=ABC123).</source>
        <translation>Navegue a un mapa de CalTopo antes de capturar la sesión.

La URL del mapa debe contener un ID de mapa (p. ej., /m/ABC123 o #id=ABC123).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="486"/>
        <source>Browser Not Ready</source>
        <translation>Navegador no listo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="487"/>
        <source>The CalTopo browser is still loading. Please wait a moment and try again.</source>
        <translation>El navegador de CalTopo aún se está cargando. Espere un momento e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="493"/>
        <source>Starting export...</source>
        <translation>Iniciando exportación...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="511"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="762"/>
        <source>Authentication Failed</source>
        <translation>Error de autenticación</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="512"/>
        <source>Browser not initialized. Please try again.</source>
        <translation>Navegador no inicializado. Inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoAuthDialog.py" line="764"/>
        <source>Could not read your CalTopo session.

Make sure you are signed in to CalTopo in this window and have opened your map, then click &apos;I&apos;m Logged In - Export Data&apos; again.</source>
        <translation>No se pudo leer su sesión de CalTopo.

Asegúrese de haber iniciado sesión en CalTopo en esta ventana y de haber abierto su mapa, y luego haga clic de nuevo en &apos;He iniciado sesión - Exportar datos&apos;.</translation>
    </message>
</context>
<context>
    <name>CalTopoCredentialDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="33"/>
        <source>CalTopo API Credentials</source>
        <translation>Credenciales de API de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="54"/>
        <source>Enter new credential secret...</source>
        <translation>Introduzca el nuevo secreto de la credencial...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="76"/>
        <source>CalTopo Team API Credentials</source>
        <translation>Credenciales de API de equipo CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="85"/>
        <source>Enter your CalTopo Team API credentials.
These can be found in the Team Admin page under Service Accounts.</source>
        <translation>Introduzca sus credenciales de API de equipo de CalTopo.
Puede encontrarlas en la página de administración del equipo en Servicios de Cuentas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="97"/>
        <source>How to get your API credentials</source>
        <translation>Cómo obtener sus credenciales de API</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="101"/>
        <source>Opens CalTopo API documentation in your browser</source>
        <translation>Abre la documentación de la API de CalTopo en su navegador</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="107"/>
        <source>Change credentials</source>
        <translation>Cambiar credenciales</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="114"/>
        <source>Team ID:</source>
        <translation>ID de equipo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="116"/>
        <source>6-digit alphanumeric Team ID</source>
        <translation>ID de equipo alfanumérico de 6 dígitos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="123"/>
        <source>Credential ID:</source>
        <translation>ID de credencial:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="125"/>
        <source>Credential ID</source>
        <translation>ID de credencial</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="132"/>
        <source>Credential Secret:</source>
        <translation>Secreto de credencial:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="134"/>
        <source>Credential Secret (will be encrypted)</source>
        <translation>Secreto de credencial (se cifrará)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="146"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="344"/>
        <source>Test Credentials</source>
        <translation>Probar credenciales</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="148"/>
        <source>Test the credentials by calling the CalTopo API</source>
        <translation>Probar las credenciales llamando a la API de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="150"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="154"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="204"/>
        <source>Enter credential secret...</source>
        <translation>Introduzca el secreto de la credencial...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="286"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="294"/>
        <source>Invalid Input</source>
        <translation>Entrada no válida</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="226"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="286"/>
        <source>Please enter a Team ID.</source>
        <translation>Introduzca un ID de equipo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="230"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="290"/>
        <source>Please enter a Credential ID.</source>
        <translation>Introduzca un ID de credencial.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="234"/>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="294"/>
        <source>Please enter a Credential Secret.</source>
        <translation>Introduzca un secreto de credencial.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="261"/>
        <source>Invalid Credential Secret</source>
        <translation>Secreto de credencial no válido</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="263"/>
        <source>The Credential Secret cannot be used to sign a CalTopo request.

Copy it exactly as shown on the CalTopo Team Admin page under Service Accounts - it is a long base64 string, not the Credential ID or the Team ID.

Details: {error}</source>
        <translation>El secreto de credencial no se puede usar para firmar una solicitud de CalTopo.

Cópielo exactamente como aparece en la página de administración del equipo de CalTopo, en Service Accounts: es una cadena base64 larga, no el ID de credencial ni el ID de equipo.

Detalles: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="302"/>
        <source>Testing...</source>
        <translation>Probando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="317"/>
        <source>Credentials Valid</source>
        <translation>Credenciales válidas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="318"/>
        <source>The credentials are valid and successfully authenticated with CalTopo API.</source>
        <translation>Las credenciales son válidas y se autenticaron correctamente con la API de CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="323"/>
        <source>Credentials Invalid</source>
        <translation>Credenciales no válidas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="325"/>
        <source>The credentials failed to authenticate with CalTopo API.

Please check:
• Team ID is correct
• Credential ID is correct
• Credential Secret is correct (copy it exactly as shown)
• Your service account has the required permissions</source>
        <translation>Las credenciales no se autenticaron correctamente con la API de CalTopo.

Compruebe:
• El ID del equipo es correcto
• El ID de credencial es correcto
• El secreto de credencial es correcto (cópielo exactamente como se muestra)
• Su cuenta de servicio tiene los permisos requeridos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="336"/>
        <source>Test Error</source>
        <translation>Error de prueba</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoCredentialDialog.py" line="337"/>
        <source>An error occurred while testing credentials:

{error}</source>
        <translation>Se produjo un error al probar las credenciales:

{error}</translation>
    </message>
</context>
<context>
    <name>CalTopoExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="487"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1292"/>
        <source>Offline Mode Enabled</source>
        <translation>Modo sin conexión habilitado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="489"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1294"/>
        <source>Offline Only is turned on in Preferences:

• Map tiles will not be retrieved.
• CalTopo integration is disabled.

Turn off Offline Only to export to CalTopo.</source>
        <translation>El modo Solo sin conexión está activado en Preferencias:

• No se recuperarán los mosaicos del mapa.
• La integración con CalTopo está desactivada.

Desactive Solo sin conexión para exportar a CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="500"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1305"/>
        <source>Nothing Selected</source>
        <translation>Nada seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="502"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1307"/>
        <source>Select at least one data type (flagged AOIs, drone/image locations, or coverage area) to export.</source>
        <translation>Seleccione al menos un tipo de datos (AOI marcados, ubicaciones de dron/imagen o área de cobertura) para exportar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="510"/>
        <source>Preparing Export Data</source>
        <translation>Preparando datos de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="513"/>
        <source>Preparing data for export...</source>
        <translation>Preparando datos para exportación...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="514"/>
        <source>Processing images and AOIs...</source>
        <translation>Procesando imágenes y AOI...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="559"/>
        <source>Preparation Error</source>
        <translation>Error de preparación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="561"/>
        <source>An error occurred while preparing export data:

{error}</source>
        <translation>Se produjo un error al preparar los datos de exportación:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="570"/>
        <source>flagged AOIs</source>
        <translation>AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="572"/>
        <source>image locations</source>
        <translation>ubicaciones de imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="574"/>
        <source>coverage area</source>
        <translation>área de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="578"/>
        <source>No flagged AOIs, geotagged image locations, or coverage areas are available.
Flag some AOIs with the &apos;F&apos; key or ensure your images have GPS metadata.</source>
        <translation>No hay AOI marcados, ubicaciones de imágenes geoetiquetadas ni áreas de cobertura disponibles.
Marque algunos AOI con la tecla &apos;F&apos; o asegúrese de que sus imágenes tengan metadatos GPS.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="584"/>
        <source>Found {count} flagged AOI(s), but could not extract GPS coordinates.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The image files have been moved or renamed

Please ensure your images have GPS coordinates embedded.</source>
        <translation>Se encontraron {count} AOI marcados, pero no se pudieron extraer las coordenadas GPS.

Esto normalmente significa:
• Las imágenes no tienen datos GPS en sus metadatos EXIF
• Los archivos de imagen se han movido o renombrado

Asegúrese de que sus imágenes tengan coordenadas GPS incrustadas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="592"/>
        <source>No geotagged drone/image locations were found.
Ensure your images contain GPS metadata and try again.</source>
        <translation>No se encontraron ubicaciones geoetiquetadas del dron/imagen.
Asegúrese de que sus imágenes contengan metadatos GPS e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="597"/>
        <source>No coverage area polygons could be calculated.

This usually means:
• The images don&apos;t have GPS data in their EXIF metadata
• The images are not nadir (gimbal pitch must be between -85° and -95°)
• GSD (ground sample distance) could not be calculated

Please ensure your images have GPS coordinates and are nadir shots.</source>
        <translation>No se pudieron calcular polígonos de área de cobertura.

Esto normalmente significa:
• Las imágenes no tienen datos GPS en sus metadatos EXIF
• Las imágenes no son nadir (la inclinación del gimbal debe estar entre -85° y -95°)
• No se pudo calcular el GSD (distancia de muestreo del suelo)

Asegúrese de que sus imágenes tengan coordenadas GPS y sean tomas nadir.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="606"/>
        <source>No {types} are available to export.</source>
        <translation>No hay {types} disponibles para exportar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="611"/>
        <source>Nothing to Export</source>
        <translation>Nada para exportar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="636"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="679"/>
        <source>No Map Selected</source>
        <translation>Ningún mapa seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="638"/>
        <source>Please navigate to a CalTopo map before clicking &apos;I&apos;m Logged In&apos;.

The map URL should look like:
https://caltopo.com/map.html#...&amp;id=ABC123</source>
        <translation>Navegue a un mapa de CalTopo antes de hacer clic en &apos;He iniciado sesión&apos;.

La URL del mapa debería verse así:
https://caltopo.com/map.html#...&amp;id=ABC123</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="681"/>
        <source>No CalTopo map was selected, so there was nothing to export to.

Open your map in the CalTopo window before clicking &apos;I&apos;m Logged In - Export Data&apos;.</source>
        <translation>No se seleccionó ningún mapa de CalTopo, por lo que no había destino para la exportación.

Abra su mapa en la ventana de CalTopo antes de hacer clic en &apos;He iniciado sesión - Exportar datos&apos;.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1607"/>
        <source>Nothing could be exported to CalTopo.

The reason was written to the log (adiat_logs.txt) and the console.</source>
        <translation>No se pudo exportar nada a CalTopo.

El motivo se registró en el archivo de registro (adiat_logs.txt) y en la consola.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1616"/>
        <source>Photos uploaded: {uploaded} of {total}.</source>
        <translation>Fotos subidas: {uploaded} de {total}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1624"/>
        <source>Successfully exported all {total} item(s) to CalTopo.

The items should now be visible on your map.</source>
        <translation>Se exportaron correctamente los {total} elemento(s) a CalTopo.

Los elementos ya deberían aparecer en su mapa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1633"/>
        <source>Exported {created} of {total} item(s) to CalTopo.{photos}

Details for anything that failed were written to the log (adiat_logs.txt) and the console.</source>
        <translation>Se exportaron {created} de {total} elemento(s) a CalTopo.{photos}

Los detalles de lo que falló se registraron en el archivo de registro (adiat_logs.txt) y en la consola.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1622"/>
        <source>Export Successful</source>
        <translation>Exportación exitosa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1631"/>
        <source>Partial Success</source>
        <translation>Éxito parcial</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1605"/>
        <source>Export Failed</source>
        <translation>Exportación fallida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="717"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1372"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1567"/>
        <source>Export Error</source>
        <translation>Error de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="719"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1569"/>
        <source>An error occurred during CalTopo export:

{error}</source>
        <translation>Se produjo un error durante la exportación a CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1049"/>
        <source>Coverage area: {sqkm:.3f} km² ({acres:.2f} acres)
Area in square meters: {sqm:.0f} m²
Number of corners: {count}</source>
        <translation>Área de cobertura: {sqkm:.3f} km² ({acres:.2f} acres)
Área en metros cuadrados: {sqm:.0f} m²
Número de esquinas: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1529"/>
        <source>Exporting to CalTopo</source>
        <translation>Exportando a CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1260"/>
        <source>Logged Out</source>
        <translation>Sesión cerrada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1261"/>
        <source>Successfully logged out from CalTopo.</source>
        <translation>Sesión cerrada correctamente en CalTopo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1420"/>
        <source>Loading CalTopo Maps</source>
        <translation>Cargando mapas de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1423"/>
        <source>Connecting to CalTopo...</source>
        <translation>Conectando a CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1424"/>
        <source>Fetching account data and maps...</source>
        <translation>Obteniendo datos de la cuenta y mapas...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1479"/>
        <source>Connection Error</source>
        <translation>Error de conexión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1481"/>
        <source>An error occurred while connecting to CalTopo API:

{error}</source>
        <translation>Se produjo un error al conectarse a la API de CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="694"/>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1484"/>
        <source>Authentication Failed</source>
        <translation>Error de autenticación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="695"/>
        <source>No CalTopo session cookies were captured. Please log in and try again.</source>
        <translation>No se capturaron cookies de sesión de CalTopo. Inicie sesión e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1374"/>
        <source>An error occurred during CalTopo API export:

{error}</source>
        <translation>Se produjo un error durante la exportación a la API de CalTopo:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1486"/>
        <source>CalTopo did not accept these credentials.

The reason was written to the log (adiat_logs.txt) and the console.

Would you like to re-enter your Team ID, Credential ID and Credential Secret?</source>
        <translation>CalTopo no aceptó estas credenciales.

El motivo se registró en el archivo de registro (adiat_logs.txt) y en la consola.

¿Desea volver a introducir su ID de equipo, ID de credencial y secreto de credencial?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1532"/>
        <source>Exporting to CalTopo...</source>
        <translation>Exportando a CalTopo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CalTopoExportController.py" line="1533"/>
        <source>Preparing data and exporting...</source>
        <translation>Preparando datos y exportando...</translation>
    </message>
</context>
<context>
    <name>CalTopoMethodDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="34"/>
        <source>CalTopo Export Method</source>
        <translation>Método de exportación de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="52"/>
        <source>Select CalTopo Export Method</source>
        <translation>Seleccionar método de exportación de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="61"/>
        <source>Choose how you want to authenticate with CalTopo:</source>
        <translation>Elija cómo desea autenticarse con CalTopo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="68"/>
        <source>Export Method</source>
        <translation>Método de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="72"/>
        <source>API (Recommended for CalTopo Team Account)</source>
        <translation>API (recomendado para cuenta de equipo CalTopo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="75"/>
        <source>Use CalTopo Team API with service account credentials.
Best for Teams accounts with service accounts configured.</source>
        <translation>Usar la API de equipo de CalTopo con credenciales de cuenta de servicio.
Ideal para cuentas de equipo con cuentas de servicio configuradas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="79"/>
        <source>Browser Login</source>
        <translation>Inicio de sesión por navegador</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="81"/>
        <source>Use browser-based authentication.
Log in through an embedded browser window.</source>
        <translation>Usar autenticación basada en navegador.
Inicie sesión a través de una ventana de navegador incrustada.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="96"/>
        <source>API method requires Team ID and Credential Secret from your
CalTopo Team Admin page. Browser method uses your regular login.</source>
        <translation>El método API requiere el ID de equipo y el secreto de credencial de su
página de administración de equipo CalTopo. El método navegador usa su inicio de sesión habitual.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="109"/>
        <source>Continue</source>
        <translation>Continuar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/CalTopoMethodDialog.py" line="113"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>CleanupTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="32"/>
        <source>Temporal Voting</source>
        <translation>Votación temporal</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="35"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Activar votación temporal (reducir parpadeo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="38"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Suaviza las detecciones entre fotogramas usando coherencia temporal.
Las detecciones deben aparecer en N de M fotogramas consecutivos para confirmarse.
Reduce considerablemente los falsos positivos intermitentes.
Recomendado: activado para todos los casos de uso (predeterminado).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="48"/>
        <source>Window Frames (M):</source>
        <translation>Fotogramas de ventana (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="53"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Tamaño de la ventana de votación temporal (2-30 fotogramas).
Las detecciones deben aparecer en N de M fotogramas consecutivos.
Valores mayores = más memoria, más estabilidad y respuesta más lenta ante objetos nuevos.
Valores menores = menos memoria, respuesta más rápida y menor estabilidad.
Recomendado: 5 para video de 30 fps (ventana de ~167 ms), 7 para 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="61"/>
        <source>Threshold (N of M):</source>
        <translation>Umbral (N de M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="66"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be &lt;= Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Número de fotogramas dentro de la ventana en los que debe aparecer la detección (N de M).
Valores mayores = criterio más estricto; filtra falsos positivos transitorios.
Valores menores = criterio más flexible; responde más rápido a objetos nuevos.
Debe ser &lt;= que los fotogramas de ventana.
Recomendado: 3 de 5 (detección en el 60% de los fotogramas).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="78"/>
        <source>Detection Cleanup</source>
        <translation>Limpieza de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="82"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Activar filtro de relación de aspecto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="85"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filtra detecciones muy delgadas o alargadas según la relación ancho/alto.
Útil para eliminar cables, sombras largas u otras formas que no son objetos.
La mayoría de los usuarios puede dejarlo desactivado salvo que vea muchos falsos positivos largos y estrechos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="94"/>
        <source>Min Ratio:</source>
        <translation>Relación mín.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="100"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 = reject if height is more than 5x width.</source>
        <translation>Relación ancho/alto mínima que se conservará (0,1-10,0).
Valores menores = permiten detecciones más altas y delgadas.
Valores mayores = exigen detecciones más cuadradas.
Ejemplo: 0,2 = rechazar si la altura es más de 5 veces el ancho.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="107"/>
        <source>Max Ratio:</source>
        <translation>Relación máx.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="113"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Relación ancho/alto máxima que se conservará (0,1-20,0).
Valores menores = rechazan detecciones muy anchas y delgadas.
Valores mayores = permiten objetos más anchos, como vehículos o equipos largos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="122"/>
        <source>Detection Clustering</source>
        <translation>Agrupación de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="125"/>
        <source>Enable Detection Clustering</source>
        <translation>Activar agrupación de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="128"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Fusiona opcionalmente las detecciones cercanas en una detección única más grande.
Útil cuando un objeto aparece como varias detecciones pequeñas contiguas.
La mayoría de los usuarios puede dejarlo desactivado salvo que los objetos se vean fragmentados.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="137"/>
        <source>Clustering Distance (px):</source>
        <translation>Distancia de agrupación (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/CleanupTab.py" line="142"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Distancia máxima entre centros de detección para fusionarlos (0-500 píxeles).
Valores menores = solo fusionan detecciones muy cercanas.
Valores mayores = fusionan detecciones más alejadas (puede agrupar de más).</translation>
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
Haga clic para cambiar el color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRowWizardWidget.py" line="71"/>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWizardWidget.py" line="71"/>
        <source>HSV: ({h}, {s}, {v})
Click to change color</source>
        <translation>HSV: ({h}, {s}, {v})
Haga clic para cambiar el color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/HSVColorRowWidget.py" line="78"/>
        <source>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Click to change color</source>
        <translation>HSV: ({h}°, {s}%, {v}%)
RGB: ({r}, {g}, {b})
Haga clic para cambiar el color</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="67"/>
        <source>Color Anomaly</source>
        <translation>Anomalía de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="68"/>
        <source>Motion Detection</source>
        <translation>Detección de movimiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="69"/>
        <source>Fusion</source>
        <translation>Fusión</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="77"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Entrada y procesamiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="78"/>
        <source>Frame</source>
        <translation>Fotograma</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="79"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Renderizado y limpieza</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="146"/>
        <source>Enable Motion Detection</source>
        <translation>Activar detección de movimiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="149"/>
        <source>Turn ON to highlight moving objects in the scene.
Most users can leave all other settings at their defaults.
Works best for stationary or slow-moving cameras and can be combined
with Color-Based Anomaly Detection for more robust results.</source>
        <translation>Active esta opción para resaltar objetos en movimiento en la escena.
La mayoría de los usuarios puede dejar el resto de ajustes con sus valores predeterminados.
Funciona mejor con cámaras fijas o de movimiento lento y puede combinarse
con la detección de anomalías por color para obtener resultados más robustos.</translation>
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
        <translation>Algoritmo de detección de movimiento (ajuste avanzado):

• FRAME_DIFF: rápido y simple; muy sensible a cualquier movimiento.
• MOG2: equilibrado y adaptable (recomendado para la mayoría de escenas).
• KNN: más robusto frente al ruido y fondos complejos.

Si no está seguro, déjelo en MOG2.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="185"/>
        <source>Detection Parameters</source>
        <translation>Parámetros de detección</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="191"/>
        <source>Motion Threshold:</source>
        <translation>Umbral de movimiento:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="196"/>
        <source>Minimum pixel intensity change to consider as motion (1-255).
Lower values = more sensitive, detects subtle motion, more false positives.
Higher values = less sensitive, only strong motion, fewer false positives.
Recommended: 10 for general use, 5 for subtle motion, 15-20 for high contrast scenes.</source>
        <translation>Cambio mínimo de intensidad de píxel para considerarlo movimiento (1-255).
Valores menores = más sensibilidad; detecta movimiento sutil y genera más falsos positivos.
Valores mayores = menos sensibilidad; solo movimiento fuerte y menos falsos positivos.
Recomendado: 10 para uso general, 5 para movimiento sutil, 15-20 para escenas de alto contraste.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="204"/>
        <source>Blur Kernel (odd):</source>
        <translation>Kernel de desenfoque (impar):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="210"/>
        <source>Gaussian blur kernel size (must be odd: 1, 3, 5, 7, etc.).
Smooths the frame before motion detection to reduce noise.
Larger values = more smoothing, less noise, less detail.
Smaller values = less smoothing, more detail, more noise.
Recommended: 5 for general use, 1 for no blur, 7-9 for noisy videos.</source>
        <translation>Tamaño del kernel de desenfoque gaussiano (debe ser impar: 1, 3, 5, 7, etc.).
Suaviza el fotograma antes de detectar movimiento para reducir ruido.
Valores mayores = más suavizado, menos ruido y menos detalle.
Valores menores = menos suavizado, más detalle y más ruido.
Recomendado: 5 para uso general, 1 sin desenfoque, 7-9 para videos con ruido.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="219"/>
        <source>Morphology Kernel:</source>
        <translation>Kernel morfológico:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="225"/>
        <source>Morphological operation kernel size (odd numbers: 1, 3, 5, etc.).
Removes small noise and fills holes in detections.
Larger values = remove more noise, merge nearby detections.
Smaller values = preserve detail, keep detections separate.
Recommended: 3 for general use, 1 for precise edges, 5-7 for noisy videos.</source>
        <translation>Tamaño del kernel de operación morfológica (números impares: 1, 3, 5, etc.).
Elimina ruido pequeño y rellena huecos en las detecciones.
Valores mayores = eliminan más ruido y fusionan detecciones cercanas.
Valores menores = conservan detalle y mantienen las detecciones separadas.
Recomendado: 3 para uso general, 1 para bordes precisos, 5-7 para videos con ruido.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="236"/>
        <source>Persistence Filter</source>
        <translation>Filtro de persistencia</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="241"/>
        <source>Window Frames (M):</source>
        <translation>Fotogramas de ventana (M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="246"/>
        <source>Size of temporal window for persistence filtering (2-30 frames).
Motion must appear in N out of M consecutive frames to be confirmed.
Larger values = longer memory, more stable, slower response.
Smaller values = shorter memory, faster response, more flicker.
Recommended: 3 for 30fps video (100ms window), 5 for 60fps.</source>
        <translation>Tamaño de la ventana temporal para el filtro de persistencia (2-30 fotogramas).
El movimiento debe aparecer en N de M fotogramas consecutivos para confirmarse.
Valores mayores = más memoria, más estabilidad y respuesta más lenta.
Valores menores = menos memoria, respuesta más rápida y más parpadeo.
Recomendado: 3 para video de 30 fps (ventana de 100 ms), 5 para 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="254"/>
        <source>Threshold (N of M):</source>
        <translation>Umbral (N de M):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="259"/>
        <source>Number of frames within window where motion must appear (N of M).
Higher values = more stringent, filters flickering false positives.
Lower values = more lenient, detects brief/intermittent motion.
Must be ≤ Window Frames.
Recommended: 2 (motion in 2 of last 3 frames).</source>
        <translation>Número de fotogramas dentro de la ventana en los que debe aparecer movimiento (N de M).
Valores mayores = criterio más estricto; filtra falsos positivos intermitentes.
Valores menores = criterio más flexible; detecta movimiento breve o intermitente.
Debe ser ≤ que los fotogramas de ventana.
Recomendado: 2 (movimiento en 2 de los últimos 3 fotogramas).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="270"/>
        <source>Background Subtraction (MOG2/KNN)</source>
        <translation>Sustracción de fondo (MOG2/KNN)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="275"/>
        <source>History Frames:</source>
        <translation>Fotogramas de historial:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="280"/>
        <source>Number of frames to learn background model (10-500).
Only applies to MOG2 and KNN algorithms.
Longer history = adapts slower to lighting changes, more stable.
Shorter history = adapts faster, less stable.
Recommended: 50 (~1.7 sec at 30fps) for general use.</source>
        <translation>Número de fotogramas para aprender el modelo de fondo (10-500).
Solo se aplica a los algoritmos MOG2 y KNN.
Historial más largo = se adapta más lento a cambios de iluminación y es más estable.
Historial más corto = se adapta más rápido y es menos estable.
Recomendado: 50 (~1,7 s a 30 fps) para uso general.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="288"/>
        <source>Variance Threshold:</source>
        <translation>Umbral de varianza:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="293"/>
        <source>Variance threshold for background/foreground classification (1.0-100.0).
Only applies to MOG2 and KNN algorithms.
Lower values = more sensitive, detects subtle changes, more false positives.
Higher values = less sensitive, only strong foreground objects.
Recommended: 10.0 for indoor, 15-20 for outdoor with varying lighting.</source>
        <translation>Umbral de varianza para clasificar fondo/primer plano (1,0-100,0).
Solo se aplica a los algoritmos MOG2 y KNN.
Valores menores = más sensibilidad; detecta cambios sutiles y genera más falsos positivos.
Valores mayores = menos sensibilidad; solo objetos de primer plano marcados.
Recomendado: 10,0 para interiores, 15-20 para exteriores con iluminación variable.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="301"/>
        <source>Detect Shadows (slower)</source>
        <translation>Detectar sombras (más lento)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="303"/>
        <source>Enables shadow detection in MOG2 background subtractor.
Helps distinguish shadows from actual objects (reduces false positives).
Adds ~10-20% processing overhead.
Recommended: ON for outdoor scenes with strong shadows, OFF for speed.</source>
        <translation>Activa la detección de sombras en el sustractor de fondo MOG2.
Ayuda a distinguir sombras de objetos reales (reduce falsos positivos).
Añade ~10-20% de carga de procesamiento.
Recomendado: activado en exteriores con sombras marcadas; desactivado para mayor velocidad.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="313"/>
        <source>Object Size Filter</source>
        <translation>Filtro de tamaño de objeto</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="318"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="454"/>
        <source>Min Object Area (px):</source>
        <translation>Área mín. del objeto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="323"/>
        <source>Minimum detection area in pixels (1-100000).
Filters out very small detections such as noise, insects, or raindrops.
Lower values = detect smaller objects (more noise).
Higher values = only larger objects (less noise).
Recommended: 5-10 for person-sized motion, 50-100 for vehicles.</source>
        <translation>Área mínima de detección en píxeles (1-100000).
Filtra detecciones muy pequeñas, como ruido, insectos o gotas de lluvia.
Valores menores = detectan objetos más pequeños (más ruido).
Valores mayores = solo objetos más grandes (menos ruido).
Recomendado: 5-10 para movimiento de tamaño humano, 50-100 para vehículos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="331"/>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="467"/>
        <source>Max Object Area (px):</source>
        <translation>Área máx. del objeto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="336"/>
        <source>Maximum detection area in pixels (10-1000000).
Filters out very large regions such as full-frame lighting changes or giant shadows.
Lower values = only small/medium objects.
Higher values = allow large objects.
Recommended: 1000 for people, 10000 for vehicles, higher for very large objects.</source>
        <translation>Área máxima de detección en píxeles (10-1000000).
Filtra regiones muy grandes, como cambios de iluminación en todo el fotograma o sombras enormes.
Valores menores = solo objetos pequeños/medianos.
Valores mayores = permiten objetos grandes.
Recomendado: 1000 para personas, 10000 para vehículos, más alto para objetos muy grandes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="347"/>
        <source>Camera Movement Detection</source>
        <translation>Detección de movimiento de cámara</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="350"/>
        <source>Pause on Camera Movement</source>
        <translation>Pausar si la cámara se mueve</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="353"/>
        <source>Automatically pauses motion detection when camera is moving/panning.
Prevents false positives caused by camera movement (entire scene appears to move).
Detects camera movement by measuring percentage of frame with motion.
Recommended: ON for handheld/drone footage, OFF for stationary tripod cameras.</source>
        <translation>Pausa automáticamente la detección de movimiento cuando la cámara se mueve o panea.
Evita falsos positivos causados por el movimiento de la cámara (parece que se mueve toda la escena).
Detecta el movimiento de cámara midiendo el porcentaje del fotograma con movimiento.
Recomendado: activado para video de mano/dron; desactivado para cámaras fijas en trípode.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="361"/>
        <source>Threshold:</source>
        <translation>Umbral:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="366"/>
        <source>Percentage of frame with motion to consider as camera movement (1-100%).
If more than this % of pixels show motion, pause detection.
Lower values = detect camera movement sooner (more pauses).
Higher values = tolerate more motion before pausing (fewer pauses).
Recommended: 15% for drone/handheld, 30% for shaky tripod.</source>
        <translation>Porcentaje del fotograma con movimiento para considerarlo movimiento de cámara (1-100%).
Si más de este % de píxeles muestra movimiento, se pausa la detección.
Valores menores = detectan movimiento de cámara antes (más pausas).
Valores mayores = toleran más movimiento antes de pausar (menos pausas).
Recomendado: 15% para dron/mano, 30% para trípode inestable.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="380"/>
        <source>Show Advanced Motion Settings</source>
        <translation>Mostrar ajustes avanzados de movimiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="383"/>
        <source>Advanced users can expand this to adjust the motion algorithm
and detailed thresholds (sensitivity, filters, background model).
If you are unsure, leave this unchecked and use the defaults.</source>
        <translation>Los usuarios avanzados pueden expandir esto para ajustar el algoritmo de movimiento
y los umbrales detallados (sensibilidad, filtros, modelo de fondo).
Si no está seguro, déjelo sin marcar y use los valores predeterminados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="402"/>
        <source>Enable Color-Based Anomaly Detection</source>
        <translation>Activar detección de anomalías por color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="405"/>
        <source>Detects pixels whose colors are statistically rare in the frame.
Conceptually similar to MRMap&apos;s rarity-based detection for images.
Works well for: bright colored clothing, vehicles, equipment in natural scenes.
Can be combined with Motion Detection for more robust detection.</source>
        <translation>Detecta píxeles cuyos colores son estadísticamente infrecuentes en el fotograma.
Es conceptualmente similar a la detección por rareza de MRMap para imágenes.
Funciona bien para: ropa de colores vivos, vehículos y equipo en escenas naturales.
Puede combinarse con la detección de movimiento para obtener detecciones más robustas.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="413"/>
        <source>Color Rarity Settings</source>
        <translation>Ajustes de rareza de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="418"/>
        <source>Color Resolution (bins):</source>
        <translation>Resolución de color (intervalos):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="424"/>
        <source>Controls how finely colors are grouped into histogram bins (3-8 bits).
Analogous to MRMap&apos;s color binning.
Lower values (3-4) = fewer bins → faster, more grouping, fewer but stronger detections.
Higher values (6-8) = more bins → slower, less grouping, more but weaker/smaller detections.
Recommended: 4-5 for a balanced number of detections; use lower for very clean results,
and higher only when you need to pull out very subtle color differences.</source>
        <translation>Controla con qué nivel de detalle se agrupan los colores en intervalos de histograma (3-8 bits).
Es análogo al agrupamiento de colores de MRMap.
Valores menores (3-4) = menos intervalos → más rápido, más agrupamiento, menos detecciones pero más sólidas.
Valores mayores (6-8) = más intervalos → más lento, menos agrupamiento, más detecciones pero más débiles/pequeñas.
Recomendado: 4-5 para una cantidad equilibrada de detecciones; use valores menores para resultados muy limpios
y valores mayores solo cuando necesite distinguir diferencias de color muy sutiles.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="432"/>
        <source>4 bits</source>
        <translation>4 bits</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="436"/>
        <source>Rarity Threshold (% of colors):</source>
        <translation>Umbral de rareza (% de colores):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="442"/>
        <source>Sensitivity threshold for how rare a color must be to be flagged (0-100%).
Computed from the distribution of color-bin counts in the frame, similar in role
to MRMap&apos;s detection threshold.
Lower values (10-20%) = stricter: only very rare colors (fewer detections).
Medium values (25-40%) = balanced (recommended for general use).
Higher values (40-60%) = more sensitive: includes more common colors (more detections).</source>
        <translation>Umbral de sensibilidad que define qué tan infrecuente debe ser un color para marcarse (0-100%).
Se calcula a partir de la distribución de conteos por intervalo de color en el fotograma, con una función similar
al umbral de detección de MRMap.
Valores menores (10-20%) = más estricto: solo colores muy raros (menos detecciones).
Valores medios (25-40%) = equilibrado (recomendado para uso general).
Valores mayores (40-60%) = más sensible: incluye colores más comunes (más detecciones).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="459"/>
        <source>Minimum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s minimum AOI area.
Lower values = detect smaller colored objects (more noise).
Higher values = only larger colored regions (less noise).
Recommended: 15 for person-sized targets, 50+ for vehicles or large objects.</source>
        <translation>Área mínima en píxeles para que una anomalía de color se trate como objeto de interés.
Equivale conceptualmente al área mínima de AOI de MRMap.
Valores menores = detectan objetos de color más pequeños (más ruido).
Valores mayores = solo regiones de color más grandes (menos ruido).
Recomendado: 15 para objetivos de tamaño humano, 50+ para vehículos u objetos grandes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="472"/>
        <source>Maximum area in pixels for a color anomaly to be treated as an object of interest.
Conceptually matches MRMap&apos;s maximum AOI area.
Lower values = only detect smaller colored objects.
Higher values = allow larger colored regions.
Recommended: 50000 for general use, 10000 for small-object-only searches.</source>
        <translation>Área máxima en píxeles para que una anomalía de color se trate como objeto de interés.
Equivale conceptualmente al área máxima de AOI de MRMap.
Valores menores = solo detectan objetos de color más pequeños.
Valores mayores = permiten regiones de color más grandes.
Recomendado: 50000 para uso general, 10000 para búsquedas solo de objetos pequeños.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="480"/>
        <source>Blob Detection Method:</source>
        <translation>Método de detección de regiones:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="482"/>
        <source>Find Contours</source>
        <translation>Encontrar contornos</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="483"/>
        <source>Connected Components</source>
        <translation>Componentes conectados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="486"/>
        <source>Method for extracting blob regions from the detection mask:

Find Contours: Traditional OpenCV contour detection (default).
  Better for irregular shapes, provides detailed contour outlines.

Connected Components: Uses cv2.connectedComponentsWithStats.
  Provides direct blob statistics in a single pass.</source>
        <translation>Método para extraer regiones de la máscara de detección:

Find Contours: detección tradicional de contornos de OpenCV (predeterminado).
  Mejor para formas irregulares; proporciona contornos detallados.

Connected Components: usa cv2.connectedComponentsWithStats.
  Proporciona estadísticas directas de las regiones en una sola pasada.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="497"/>
        <source>Color Space (Lighting Invariance)</source>
        <translation>Espacio de color (invariancia a la iluminación)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="502"/>
        <source>Color Space:</source>
        <translation>Espacio de color:</translation>
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
        <translation>Espacio de color para detección de anomalías basada en histogramas:

RGB: usa los 3 canales de color. Es rápido, pero sensible a la iluminación.
  Una camisa roja en sombra puede no coincidir con una camisa roja al sol.

HSV (basado en tono): usa solo el canal de tono; es invariante a la iluminación.
  El rojo sigue siendo rojo independientemente del brillo. Bueno para objetos de color.
  Filtra grises/blancos donde el tono no está definido.

LAB (cromaticidad a,b): usa los canales a,b; es invariante a la iluminación y perceptualmente uniforme.
  No tiene discontinuidad en rojo (a diferencia de HSV). Es lo mejor para búsqueda y rescate.
  Filtra grises neutros donde a,b están cerca de cero.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="522"/>
        <source>HSV Min Saturation:</source>
        <translation>Saturación mín. HSV:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="529"/>
        <source>Minimum saturation for HSV mode (0-255).
Pixels below this saturation are ignored (grays, whites, blacks).
These have undefined/noisy hue values.
Lower = include more desaturated colors (may add noise).
Higher = only vivid colors (may miss faded/shadowed objects).
Recommended: 30-50 for general use.</source>
        <translation>Saturación mínima para el modo HSV (0-255).
Los píxeles por debajo de esta saturación se ignoran (grises, blancos, negros).
Estos tienen valores de tono indefinidos o ruidosos.
Menor = incluye más colores desaturados (puede añadir ruido).
Mayor = solo colores vivos (puede omitir objetos desteñidos o en sombra).
Recomendado: 30-50 para uso general.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="542"/>
        <source>LAB Min Chroma:</source>
        <translation>Croma mín. LAB:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="549"/>
        <source>Minimum chroma (color intensity) for LAB mode (0-128).
Chroma = distance from neutral gray in a,b plane.
Pixels below this are ignored (near-neutral grays).
Lower = include more muted colors.
Higher = only vivid, saturated colors.
Recommended: 10-20 for general use.</source>
        <translation>Croma mínimo (intensidad de color) para el modo LAB (0-128).
Croma = distancia respecto del gris neutro en el plano a,b.
Los píxeles por debajo de este valor se ignoran (grises casi neutros).
Menor = incluye más colores apagados.
Mayor = solo colores vivos y saturados.
Recomendado: 10-20 para uso general.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="567"/>
        <source>Color Match Expansion</source>
        <translation>Expansión de coincidencia de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="570"/>
        <source>Allow Similar Colors (Hue Expansion)</source>
        <translation>Permitir colores similares (expansión de tono)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="573"/>
        <source>Lets the detector treat similar colors as the same object.
For example, a red jacket that looks slightly orange in some frames will still be grouped together.
Turn this OFF if you only care about one very specific color shade.
Turn this ON if you want a whole family of colors (e.g., any warm reds/oranges).</source>
        <translation>Permite que el detector trate colores similares como el mismo objeto.
Por ejemplo, una chaqueta roja que se ve algo anaranjada en algunos fotogramas seguirá agrupándose.
Desactive esto si solo le importa un matiz muy específico.
Actívelo si desea una familia completa de colores (por ejemplo, cualquier rojo/naranja cálido).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="581"/>
        <source>Color Match Range:</source>
        <translation>Rango de coincidencia de color:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="586"/>
        <source>How wide to stretch the color match around each detected color.
Smaller values = stay very close to the original color (more specific).
Larger values = include a wider range of similar colors (more forgiving).
Recommended: low values for precise colors, higher values when lighting or camera color shifts a lot.</source>
        <translation>Qué tanto se amplía la coincidencia alrededor de cada color detectado.
Valores menores = se mantiene muy cerca del color original (más específico).
Valores mayores = incluye un rango más amplio de colores similares (más tolerante).
Recomendado: valores bajos para colores precisos; valores mayores cuando la iluminación o el color de la cámara cambian mucho.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="592"/>
        <source>±5 (~10°)</source>
        <translation>±5 (~10°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="599"/>
        <source>Color Exclusion</source>
        <translation>Exclusión de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="602"/>
        <source>Enable Color Exclusion</source>
        <translation>Activar exclusión de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="605"/>
        <source>Exclude specific background colors from color anomaly detection.
Useful for ignoring dominant scene colors such as grass, sky, or buildings.
Click on the color wheel below to choose colors to ignore.
Selected colors are highlighted with a dark border.</source>
        <translation>Excluye colores de fondo específicos de la detección de anomalías de color.
Útil para ignorar colores dominantes de la escena, como pasto, cielo o edificios.
Haga clic en la rueda de color inferior para elegir los colores que se ignorarán.
Los colores seleccionados se resaltan con un borde oscuro.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="613"/>
        <source>Click on color wheel to exclude colors (20° steps, 0-360°):</source>
        <translation>Haga clic en la rueda de color para excluir colores (pasos de 20°, 0-360°):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="618"/>
        <source>Click on any color segment to toggle exclusion on/off.
Segments represent broad color ranges (e.g., blues, greens, reds).
Use this to teach the system which background colors to ignore.</source>
        <translation>Haga clic en cualquier segmento de color para activar o desactivar su exclusión.
Los segmentos representan rangos amplios de color (por ejemplo, azules, verdes, rojos).
Use esta opción para indicar al sistema qué colores de fondo debe ignorar.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="635"/>
        <source>Detection Fusion</source>
        <translation>Fusión de detecciones</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="638"/>
        <source>Enable Fusion (when both motion and color enabled)</source>
        <translation>Activar fusión (cuando movimiento y color estén activados)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="641"/>
        <source>Combines motion and color detections when both are enabled.
Only active when both Motion and Color detection are ON.
Different modes control how detections are merged.
Recommended: ON for robust multi-modal detection.</source>
        <translation>Combina detecciones de movimiento y color cuando ambas están activadas.
Solo está activa cuando la detección de movimiento y la de color están activadas.
Los distintos modos controlan cómo se fusionan las detecciones.
Recomendado: activado para una detección multimodal robusta.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/views/ColorAnomalyAndMotionDetectionControlWidget.py" line="649"/>
        <source>Fusion Mode:</source>
        <translation>Modo de fusión:</translation>
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
        <translation>Cómo combinar detecciones de movimiento y color:

• UNION: muestra todas las detecciones de ambos métodos (más detecciones).
  Use esta opción para: cobertura máxima, no perder nada.

• INTERSECTION: muestra solo detecciones encontradas por ambos (menos falsos positivos).
  Use esta opción para: alta confianza y menos falsos positivos.

• COLOR_PRIORITY: muestra detecciones de color + detecciones de movimiento que coincidan con el color.
  Use esta opción para: dar más peso al color (por ejemplo, objetos de colores vivos).

• MOTION_PRIORITY: muestra detecciones de movimiento + detecciones de color que coincidan con el movimiento.
  Use esta opción para: dar más peso al movimiento (por ejemplo, objetos camuflados en movimiento).</translation>
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
        <translation>FPS: {fps} | Procesamiento: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="12"/>
        <source>Color Anomaly Detection</source>
        <translation>Detección de anomalías de color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="16"/>
        <source>Enable Color Anomaly Detection</source>
        <translation>Habilitar detección de anomalías de color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="27"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>¿Con qué agresividad debe ADIAT buscar anomalías?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="38"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: Un valor más alto encontrará más anomalías potenciales pero también puede aumentar los falsos positivos.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="56"/>
        <source>Motion Detection</source>
        <translation>Detección de movimiento</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="65"/>
        <source>Do you want to enable motion detection?</source>
        <translation>¿Quiere habilitar la detección de movimiento?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="73"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorAnomalyAndMotionDetectionWizard.ui" line="79"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
</context>
<context>
    <name>ColorAnomalyAndMotionDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="48"/>
        <source>Very 
Conservative</source>
        <translation>Muy 
conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="49"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="50"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="51"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorAnomalyAndMotionDetection/controllers/ColorAnomalyAndMotionDetectionWizardController.py" line="52"/>
        <source>Very 
Aggressive</source>
        <translation>Muy 
agresivo</translation>
    </message>
</context>
<context>
    <name>ColorDetectionControlWidget</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="76"/>
        <source>Color Selection</source>
        <translation>Selección de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="77"/>
        <source>Detection</source>
        <translation>Detección</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="78"/>
        <source>Input &amp;&amp; Processing</source>
        <translation>Entrada y procesamiento</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="79"/>
        <source>Frame</source>
        <translation>Fotograma</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="80"/>
        <source>Rendering &amp;&amp; Cleanup</source>
        <translation>Renderizado y limpieza</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="108"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="111"/>
        <source>Add a new color range to detect.
Choose from HSV Color Picker, Image, List, or Recent Colors.
You can add multiple color ranges to detect different colors simultaneously.</source>
        <translation>Añadir un nuevo rango de color a detectar.
Elija entre Selector de color HSV, Imagen, Lista o Colores recientes.
Puede añadir varios rangos de color para detectar distintos colores simultáneamente.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="131"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="134"/>
        <source>View HSV color ranges for all configured colors.
Opens a viewer dialog for each color range showing
the hue, saturation, and value ranges that will be detected.
Useful for understanding and fine-tuning multi-color detection.</source>
        <translation>Ver los rangos de color HSV para todos los colores configurados.
Abre un diálogo de visor para cada rango de color que muestra
los rangos de tono, saturación y valor que se detectarán.
Útil para entender y ajustar la detección multicolor.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="157"/>
        <source>No colors configured. Add at least one color to start detection.</source>
        <translation>No hay colores configurados. Añada al menos un color para iniciar la detección.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="178"/>
        <source>Min Object Area (px):</source>
        <translation>Área mín. del objeto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="184"/>
        <source>Minimum detection area in pixels (10-50000).
Filters out very small detections (noise, small objects, fragments).
Lower values = detect smaller objects, more detections, more noise.
Higher values = only large objects, fewer detections, less noise.
Recommended: 100 for general use, 50 for small objects, 200-500 for large objects.</source>
        <translation>Área mínima de detección en píxeles (10-50000).
Filtra las detecciones muy pequeñas (ruido, objetos pequeños, fragmentos).
Valores más bajos = detectan objetos más pequeños, más detecciones, más ruido.
Valores más altos = solo objetos grandes, menos detecciones, menos ruido.
Recomendado: 100 para uso general, 50 para objetos pequeños, 200-500 para objetos grandes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="193"/>
        <source>Max Object Area (px):</source>
        <translation>Área máx. del objeto (px):</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="199"/>
        <source>Maximum detection area in pixels (100-500000).
Filters out very large detections (shadows, lighting changes, entire scene).
Lower values = only small/medium objects.
Higher values = allow large objects, may include unwanted large regions.
Recommended: 100000 for general use, 50000 for small objects, 200000+ for large objects.</source>
        <translation>Área máxima de detección en píxeles (100-500000).
Filtra las detecciones muy grandes (sombras, cambios de iluminación, escena completa).
Valores más bajos = solo objetos pequeños/medianos.
Valores más altos = permiten objetos grandes, pueden incluir regiones grandes no deseadas.
Recomendado: 100000 para uso general, 50000 para objetos pequeños, 200000+ para objetos grandes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/views/ColorDetectionControlWidget.py" line="208"/>
        <source>Confidence Threshold:</source>
        <translation>Umbral de confianza:</translation>
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
        <translation>Puntuación de confianza mínima para aceptar una detección (0-100%).
La confianza se calcula a partir de:
• Puntuación de tamaño: área relativa al área máxima
• Puntuación de forma: solidez (qué tan compacta/regular es la forma)
• Final: promedio de ambas puntuaciones

Valores más bajos (0-30%) = aceptan más detecciones, incluyendo las débiles/fragmentadas.
Valores más altos (70-100%) = solo detecciones de alta calidad, formas bien definidas.
Recomendado: 50% para un filtrado equilibrado, 30% para más detecciones, 70% para calidad estricta.</translation>
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
        <translation>Rangos de color: {count} colores</translation>
    </message>
</context>
<context>
    <name>ColorDetectionController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionController.py" line="134"/>
        <source>FPS: {fps} | Processing: {time}ms</source>
        <translation>FPS: {fps} | Procesamiento: {time}ms</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorDetectionWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
</context>
<context>
    <name>ColorDetectionWizardController</name>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="52"/>
        <source>No Colors Selected</source>
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="62"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="244"/>
        <source>Color Ranges: {count} colors</source>
        <translation>Rangos de color: {count} colores</translation>
    </message>
    <message>
        <location filename="../app/algorithms/streaming/ColorDetection/controllers/ColorDetectionWizardController.py" line="329"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="57"/>
        <source>Hue Histogram Unavailable</source>
        <translation>Histograma de matiz no disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ColorHistogramController.py" line="59"/>
        <source>No color image data is available for the current image.</source>
        <translation>No hay datos de imagen en color disponibles para la imagen actual.</translation>
    </message>
</context>
<context>
    <name>ColorHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="14"/>
        <source>Hue Histogram</source>
        <translation>Histograma de matiz</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="23"/>
        <source>Hue distribution of all pixels vs. AOI pixels. Hovering the chart highlights matching pixels in the image.</source>
        <translation>Distribución de la matiz de todos los píxeles frente a los píxeles del AOI. Pasar el cursor sobre el gráfico resalta los píxeles coincidentes en la imagen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="32"/>
        <source>AOIs Only</source>
        <translation>Solo AOI</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Restablecer zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="61"/>
        <source>Drag on the histogram or use the mouse wheel to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Arrastre sobre el histograma o use la rueda del ratón para acercar. Haga doble clic o use Restablecer zoom para volver al rango completo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="74"/>
        <source>Visible Hue Range</source>
        <translation>Rango visible de la matiz</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="61"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="85"/>
        <source>Minimum: --</source>
        <translation>Mínimo: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="62"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="92"/>
        <source>Maximum: --</source>
        <translation>Máximo: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="115"/>
        <source>Reset Range</source>
        <translation>Restablecer rango</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="64"/>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="174"/>
        <location filename="../resources/views/images/viewer/ColorHistogramDialog.ui" line="127"/>
        <source>Hover over the histogram to inspect a hue band.</source>
        <translation>Pase el cursor sobre el histograma para inspeccionar una banda de la matiz.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="30"/>
        <source>No hue histogram data available</source>
        <translation>No hay datos de histograma disponible de la matiz</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="180"/>
        <source>Hover hue: {value}°</source>
        <translation>Matiz baja del cursor: {value}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="188"/>
        <source>Minimum: {minimum}°</source>
        <translation>Mínimo: {minimum}°</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ColorHistogramDialog.py" line="193"/>
        <source>Maximum: {maximum}°</source>
        <translation>Máximo: {maximum}°</translation>
    </message>
</context>
<context>
    <name>ColorListDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="30"/>
        <source>Select Color from List</source>
        <translation>Seleccionar color desde lista</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="42"/>
        <source>Search:</source>
        <translation>Búsqueda:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="44"/>
        <source>Filter by name or uses…</source>
        <translation>Filtrar por nombre o usos…</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="56"/>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="61"/>
        <source>Name</source>
        <translation>Nombre</translation>
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
        <translation>Usos</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorListDialog.py" line="73"/>
        <source>Use Color</source>
        <translation>Usar color</translation>
    </message>
</context>
<context>
    <name>ColorPickerDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="35"/>
        <source>Select Color from Image</source>
        <translation>Seleccionar color desde imagen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerDialog.py" line="55"/>
        <source>Use Color</source>
        <translation>Usar color</translation>
    </message>
</context>
<context>
    <name>ColorPickerImageViewer</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="97"/>
        <source>Load Image</source>
        <translation>Cargar imagen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="102"/>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="290"/>
        <source>Color Selector</source>
        <translation>Selector de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="159"/>
        <source>Select Image</source>
        <translation>Seleccionar imagen</translation>
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
        <translation>No se pudo cargar la imagen: {path}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="231"/>
        <source>Error loading image: {error}</source>
        <translation>Error al cargar la imagen: {error}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="286"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="358"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: ({h}°, {s}%, {v}%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="445"/>
        <source>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (hover)</source>
        <translation>RGB: ({r}, {g}, {b}) {hex} | HSV: {h}°, {s}%, {v}% (cursor)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorPickerImageViewer.py" line="589"/>
        <source>Error setting image: {error}</source>
        <translation>Error al establecer la imagen: {error}</translation>
    </message>
</context>
<context>
    <name>ColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="42"/>
        <source>Add a new color range to detect. Each color can have its own RGB range tolerances.</source>
        <translation>Añadir un nuevo rango de color a detectar. Cada color puede tener sus propias tolerancias de rango RGB.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="45"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
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
        <translation>Abre la ventana del Visor de rango para:
- Ver el rango de colores que se buscarán en el análisis de imágenes.
Úselo para ver qué colores se detectarán y optimizar los rangos de color antes del procesamiento.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ColorRange.ui" line="88"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
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
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeController.py" line="324"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
    </message>
</context>
<context>
    <name>ColorRangeDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="39"/>
        <source>HSV Color Range Selection</source>
        <translation>Selección de rango de color HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="122"/>
        <source>Color Range Selection</source>
        <translation>Selección de rango de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="206"/>
        <source>Preview</source>
        <translation>Vista previa</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="210"/>
        <source>Original Image</source>
        <translation>Imagen original</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="216"/>
        <source>Original image preview.
Shows the unmodified input image for reference.
Use this to compare with the filtered result below.</source>
        <translation>Vista previa de la imagen original.
Muestra la imagen de entrada sin modificar como referencia.
Úsela para compararla con el resultado filtrado de abajo.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="222"/>
        <source>Filtered Result</source>
        <translation>Resultado filtrado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="228"/>
        <source>Filtered result preview.
Shows pixels that match your current HSV color range settings.
Updates in real-time as you adjust the color and range values.
Matching pixels are shown, non-matching pixels appear black.</source>
        <translation>Vista previa del resultado filtrado.
Muestra los píxeles que coinciden con los ajustes actuales de rango de color HSV.
Se actualiza en tiempo real al ajustar el color y los valores del rango.
Los píxeles coincidentes se muestran; los no coincidentes aparecen en negro.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="235"/>
        <source>Show mask only</source>
        <translation>Mostrar solo máscara</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="237"/>
        <source>Toggle between masked color result and grayscale mask.
• Unchecked (default): Shows the original image with matching colors visible
• Checked: Shows a black and white mask where white = matching pixels
Use the mask view to clearly see which pixels are being detected.</source>
        <translation>Alterna entre el resultado de color enmascarado y la máscara en escala de grises.
• Sin marcar (predeterminado): muestra la imagen original con los colores coincidentes visibles
• Marcado: muestra una máscara en blanco y negro donde blanco = píxeles coincidentes
Use la vista de máscara para ver claramente qué píxeles se detectan.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="244"/>
        <source>Original:</source>
        <translation>Original:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="246"/>
        <source>Result:</source>
        <translation>Resultado:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="262"/>
        <source>Pick from Image...</source>
        <translation>Elegir desde imagen...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="268"/>
        <source>Test on Image</source>
        <translation>Probar en imagen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="270"/>
        <source>Test current HSV range settings on the loaded image.
Manually triggers a preview update to see detection results.
Preview updates automatically as you adjust settings.</source>
        <translation>Prueba los ajustes actuales de rango HSV en la imagen cargada.
Activa manualmente una actualización de vista previa para ver los resultados de detección.
La vista previa se actualiza automáticamente al ajustar la configuración.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="280"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="282"/>
        <source>Cancel color selection.
Discards all changes and closes the dialog without applying the color range.</source>
        <translation>Cancela la selección de color.
Descarta todos los cambios y cierra el cuadro de diálogo sin aplicar el rango de color.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="287"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="289"/>
        <source>Apply color selection.
Saves the current HSV color range settings and closes the dialog.
The selected color range will be used for image analysis.</source>
        <translation>Aplica la selección de color.
Guarda los ajustes actuales del rango HSV y cierra el cuadro de diálogo.
El rango de color seleccionado se usará para el análisis de imágenes.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="309"/>
        <source>Custom Colors</source>
        <translation>Colores personalizados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="312"/>
        <source>Standard Dialog...</source>
        <translation>Diálogo estándar...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="318"/>
        <source>Add Current</source>
        <translation>Añadir actual</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/ColorRangeDialog.py" line="381"/>
        <source>Select Color</source>
        <translation>Seleccionar color</translation>
    </message>
</context>
<context>
    <name>ColorRangeViewer</name>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="14"/>
        <source>Color Range Viewer</source>
        <translation>Visor de rango de color</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="37"/>
        <source>Selected images for viewing.
Shows images that you&apos;ve chosen to view in the range viewer.
Click on images below to add or remove them from this section.</source>
        <translation>Imágenes seleccionadas para visualizar.
Muestra las imágenes que ha elegido ver en el visor de rango.
Haga clic en las imágenes de abajo para añadirlas o quitarlas de esta sección.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="42"/>
        <source>Selected</source>
        <translation>Seleccionado</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="76"/>
        <source>Available images for viewing.
Shows all images from the input folder that are available to select.
Click on images to move them to the Selected section above.</source>
        <translation>Imágenes disponibles para ver.
Muestra todas las imágenes de la carpeta de entrada que están disponibles para seleccionar.
Haga clic en las imágenes para moverlas a la sección Seleccionadas de arriba.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RangeViewer.ui" line="81"/>
        <source>Unselected</source>
        <translation>Deseleccionado</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
</context>
<context>
    <name>ColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="69"/>
        <source>No Colors Selected</source>
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="79"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ColorRange/controllers/ColorRangeWizardController.py" line="258"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
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
        <translation>Espacio vacío: añada un color personalizado</translation>
    </message>
</context>
<context>
    <name>CoordinateController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="122"/>
        <source>GPS Coordinates: {coords}</source>
        <translation>Coordenadas GPS: {coords}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="148"/>
        <source>📋 Copy coordinates</source>
        <translation>📋 Copiar coordenadas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="152"/>
        <source>🗺️ Open in Google Maps</source>
        <translation>🗺️ Abrir en Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="156"/>
        <source>🌍 View in Google Earth</source>
        <translation>🌍 Ver en Google Earth</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="160"/>
        <source>📱 Send via WhatsApp</source>
        <translation>📱 Enviar por WhatsApp</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="164"/>
        <source>📨 Send via Telegram</source>
        <translation>📨 Enviar por Telegram</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="236"/>
        <source>Coordinates copied</source>
        <translation>Coordenadas copiadas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="246"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="260"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="323"/>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="343"/>
        <source>Coordinates unavailable</source>
        <translation>Coordenadas no disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="330"/>
        <source>Coordinate: {lat}, {lon} — {maps}</source>
        <translation>Coordenada: {lat}, {lon} — {maps}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="350"/>
        <source>Coordinates: {lat}, {lon}</source>
        <translation>Coordenadas: {lat}, {lon}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="390"/>
        <source>No bearing info available</source>
        <translation>No hay información de rumbo disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="412"/>
        <source>North-Oriented View (Rotated {angle:.1f}°)</source>
        <translation>Vista orientada al norte (rotada {angle:.1f}°)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="444"/>
        <source>Original bearing: {bearing:.1f}° | Rotation applied: {rotation:.1f}°</source>
        <translation>Rumbo original: {bearing:.1f}° | Rotación aplicada: {rotation:.1f}°</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="454"/>
        <source>↑ NORTH</source>
        <translation>↑ NORTE</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/CoordinateController.py" line="463"/>
        <source>Close</source>
        <translation>Cerrar</translation>
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
        <translation>Coordinador de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="58"/>
        <source>Create New Search</source>
        <translation>Crear nueva búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="63"/>
        <source>Open Existing Search</source>
        <translation>Abrir búsqueda existente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="68"/>
        <source>Save Search</source>
        <translation>Guardar búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="74"/>
        <source>Add Batches to Search</source>
        <translation>Añadir lotes a la búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="78"/>
        <source>Add more batch XML files to the current search project</source>
        <translation>Añadir más archivos XML de lotes al proyecto de búsqueda actual</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="96"/>
        <source>Dashboard</source>
        <translation>Panel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="100"/>
        <source>Batch Status</source>
        <translation>Estado del lote</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="104"/>
        <source>AOI Analysis</source>
        <translation>Análisis de AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="112"/>
        <source>Review Selected Batch</source>
        <translation>Revisar lote seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="116"/>
        <source>Open the selected batch&apos;s results in the Viewer to review (same as double-clicking the batch).</source>
        <translation>Abrir los resultados del lote seleccionado en el Visor para revisarlos (igual que al hacer doble clic en el lote).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="122"/>
        <source>Load Review XML</source>
        <translation>Cargar XML de revisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="128"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="658"/>
        <source>Export Consolidated Results</source>
        <translation>Exportar resultados consolidados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="140"/>
        <source>Project Information</source>
        <translation>Información del proyecto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="145"/>
        <source>No project loaded</source>
        <translation>Ningún proyecto cargado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="147"/>
        <source>Project:</source>
        <translation>Proyecto:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="152"/>
        <source>Created by:</source>
        <translation>Creado por:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="157"/>
        <source>Date:</source>
        <translation>Fecha:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="176"/>
        <source>Total Batches</source>
        <translation>Lotes totales</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="177"/>
        <source>Total Images</source>
        <translation>Imágenes totales</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="178"/>
        <source>Total Reviews</source>
        <translation>Revisiones totales</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="179"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="327"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="361"/>
        <source>Reviewers</source>
        <translation>Revisores</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="189"/>
        <source>Review Progress</source>
        <translation>Progreso de revisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="194"/>
        <source>Overall Completion:</source>
        <translation>Finalización global:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="199"/>
        <source>0%</source>
        <translation>0%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="213"/>
        <source>Not Reviewed</source>
        <translation>No revisado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="222"/>
        <source>In Progress</source>
        <translation>En curso</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="231"/>
        <source>Complete</source>
        <translation>Completo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="239"/>
        <source>AOI Summary</source>
        <translation>Resumen de AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="247"/>
        <source>Total AOIs</source>
        <translation>AOI totales</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="255"/>
        <source>Flagged AOIs</source>
        <translation>AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="262"/>
        <source>Active Reviewers</source>
        <translation>Revisores activos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="264"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="714"/>
        <source>No reviewers yet</source>
        <translation>Todavía no hay revisores</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="312"/>
        <source>Batch review status and assignments. Load reviewer XMLs to update progress. Double-click a batch to open its results in the Viewer.</source>
        <translation>Estado y asignaciones de la revisión por lotes. Cargue los XML de los revisores para actualizar el progreso. Haga doble clic en un lote para abrir sus resultados en el visor.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="323"/>
        <source>Batch ID</source>
        <translation>ID de lote</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="324"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="325"/>
        <source>Images</source>
        <translation>Imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="326"/>
        <source>Reviews</source>
        <translation>Revisiones</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="328"/>
        <source>Status</source>
        <translation>Estado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="349"/>
        <source>Consolidated AOI data from all reviews. Shows flag counts and reviewer comments.</source>
        <translation>Datos consolidados de AOI de todas las revisiones. Muestra los recuentos de marcas y comentarios de revisores.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="358"/>
        <source>Image</source>
        <translation>Imagen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="359"/>
        <source>Location</source>
        <translation>Ubicación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="360"/>
        <source>Flag Count</source>
        <translation>Recuento de marcas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="362"/>
        <source>Comments</source>
        <translation>Comentarios</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="379"/>
        <source>New Search Project</source>
        <translation>Nuevo proyecto de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="380"/>
        <source>Enter project name:</source>
        <translation>Introduzca el nombre del proyecto:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="389"/>
        <source>Coordinator Information</source>
        <translation>Información del coordinador</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="390"/>
        <source>Enter your name:</source>
        <translation>Introduzca su nombre:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="399"/>
        <source>Select Batch Files</source>
        <translation>Seleccionar archivos de lotes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="400"/>
        <source>Select Initial Batch XML Files</source>
        <translation>Seleccionar archivos XML de lote inicial</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="403"/>
        <source>You can select multiple ADIAT_Data.xml files from different folders.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• You can add more batches later using &apos;Add Batches to Search&apos; button
• Each batch should be a processed ADIAT_Data.xml file</source>
        <translation>Puede seleccionar varios archivos ADIAT_Data.xml de diferentes carpetas.

Consejos:
• Mantenga Ctrl (Windows/Linux) o Cmd (Mac) para seleccionar varios archivos
• Puede añadir más lotes más tarde usando el botón &apos;Añadir lotes a la búsqueda&apos;
• Cada lote debe ser un archivo ADIAT_Data.xml procesado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="417"/>
        <source>Select Batch ADIAT_Data.xml Files (Hold Ctrl to select multiple)</source>
        <translation>Seleccionar archivos ADIAT_Data.xml de lotes (Mantenga Ctrl para seleccionar varios)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="419"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="434"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="558"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="605"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="660"/>
        <source>XML Files (*.xml)</source>
        <translation>Archivos XML (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="432"/>
        <source>Save Search Project</source>
        <translation>Guardar proyecto de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="444"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="473"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="517"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="577"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="641"/>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="667"/>
        <source>Success</source>
        <translation>Éxito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="445"/>
        <source>Search project &apos;{project}&apos; created successfully!</source>
        <translation>¡Proyecto de búsqueda &apos;{project}&apos; creado correctamente!</translation>
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
        <translation>Error al guardar el archivo del proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="456"/>
        <source>Failed to create project.</source>
        <translation>Error al crear el proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="462"/>
        <source>Open Search Project</source>
        <translation>Abrir proyecto de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="464"/>
        <source>Search Project Files (ADIAT_Search_*.xml);;All XML Files (*.xml)</source>
        <translation>Archivos de proyecto de búsqueda (ADIAT_Search_*.xml);;Todos los archivos XML (*.xml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="474"/>
        <source>Project loaded successfully!</source>
        <translation>¡Proyecto cargado correctamente!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="493"/>
        <source>Search project file not found:
{path}</source>
        <translation>No se encontró el archivo del proyecto de búsqueda:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="507"/>
        <source>Failed to load project file.</source>
        <translation>Error al cargar el archivo del proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="518"/>
        <source>Project saved successfully!</source>
        <translation>¡Proyecto guardado correctamente!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="521"/>
        <source>Failed to save project.</source>
        <translation>Error al guardar el proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="528"/>
        <source>No Project</source>
        <translation>Sin proyecto</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="529"/>
        <source>Please create or open a project first.</source>
        <translation>Primero cree o abra un proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="536"/>
        <source>Add Batches</source>
        <translation>Añadir lotes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="537"/>
        <source>Add More Batch XML Files</source>
        <translation>Añadir más archivos XML de lotes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="540"/>
        <source>Select additional ADIAT_Data.xml batch files to add to this search.

Tips:
• Hold Ctrl (Windows/Linux) or Cmd (Mac) to select multiple files
• Files can be in different folders
• Each batch should be a processed ADIAT_Data.xml file
• New batches will be numbered sequentially</source>
        <translation>Seleccionar archivos adicionales ADIAT_Data.xml de lotes para añadir a esta búsqueda.

Consejos:
• Mantenga Ctrl (Windows/Linux) o Cmd (Mac) para seleccionar varios archivos
• Los archivos pueden estar en diferentes carpetas
• Cada lote debe ser un archivo ADIAT_Data.xml procesado
• Los nuevos lotes se numerarán secuencialmente</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="556"/>
        <source>Select Batch ADIAT_Data.xml Files to Add (Hold Ctrl to select multiple)</source>
        <translation>Seleccionar archivos ADIAT_Data.xml de lotes para añadir (Mantenga Ctrl para seleccionar varios)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="579"/>
        <source>Successfully added {count} batch(es) to the project!
Total batches: {total}</source>
        <translation>¡Se añadieron correctamente {count} lotes al proyecto!
Lotes totales: {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="589"/>
        <source>No Batches Added</source>
        <translation>No se añadieron lotes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="591"/>
        <source>No batches were added. Check that the XML files are valid ADIAT_Data.xml files.</source>
        <translation>No se añadió ningún lote. Compruebe que los archivos XML sean archivos ADIAT_Data.xml válidos.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="603"/>
        <source>Select Reviewer&apos;s ADIAT_Data.xml File</source>
        <translation>Seleccionar archivo ADIAT_Data.xml del revisor</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="616"/>
        <source>No Batches</source>
        <translation>Sin lotes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="617"/>
        <source>No batches found in project.</source>
        <translation>No se encontraron lotes en el proyecto.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="625"/>
        <source>Select Batch</source>
        <translation>Seleccionar lote</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="626"/>
        <source>Which batch does this review belong to?</source>
        <translation>¿A qué lote pertenece esta revisión?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="642"/>
        <source>Review data loaded and merged successfully!</source>
        <translation>¡Datos de revisión cargados y combinados correctamente!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="648"/>
        <source>Failed to load review data.</source>
        <translation>Error al cargar los datos de revisión.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="668"/>
        <source>Consolidated results exported to:
{path}</source>
        <translation>Resultados consolidados exportados a:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="671"/>
        <source>Failed to export results.</source>
        <translation>Error al exportar los resultados.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="697"/>
        <source>{value}%</source>
        <translation>{value}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="758"/>
        <source>No Batch Selected</source>
        <translation>Ningún lote seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/coordinator/CoordinatorWindow.py" line="759"/>
        <source>Select a batch in the table, then click Review Selected Batch.</source>
        <translation>Seleccione un lote de la tabla y, a continuación, haga clic en Revisar lote seleccionado.</translation>
    </message>
</context>
<context>
    <name>CoverageExtentExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="129"/>
        <source>Generate Coverage Extent KML</source>
        <translation>Generar KML de extensión de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="131"/>
        <source>Generate a KML file showing the geographic coverage extent of all images?

This will create polygon(s) representing the area covered by all images. Overlapping image areas will be merged into a single polygon.</source>
        <translation>¿Generar un archivo KML que muestre la extensión geográfica de cobertura de todas las imágenes?

Esto creará polígonos que representan el área cubierta por todas las imágenes. Las áreas superpuestas se fusionarán en un único polígono.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="145"/>
        <source>Save Coverage Extent KML</source>
        <translation>Guardar KML de extensión de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="147"/>
        <source>KML files (*.kml)</source>
        <translation>Archivos KML (*.kml)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="160"/>
        <source>Generating Coverage Extent KML</source>
        <translation>Generando KML de extensión de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="163"/>
        <source>Calculating coverage extent...</source>
        <translation>Calculando extensión de cobertura...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="209"/>
        <source>Error generating coverage extent KML</source>
        <translation>Error al generar el KML de extensión de cobertura</translation>
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
        <translation>Error al generar el KML de extensión de cobertura:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="246"/>
        <source>Coverage extent generation cancelled</source>
        <translation>Generación de extensión de cobertura cancelada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="257"/>
        <source>Error generating coverage extent</source>
        <translation>Error al generar la extensión de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="270"/>
        <source>No valid images found for coverage extent calculation</source>
        <translation>No se encontraron imágenes válidas para el cálculo de la extensión de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="276"/>
        <source>Coverage Extent</source>
        <translation>Extensión de cobertura</translation>
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
        <translation>No se pudo calcular la extensión de cobertura.

Imágenes procesadas: {processed}
Imágenes omitidas: {skipped}

Las imágenes pueden omitirse por los siguientes motivos:
  • Faltan datos GPS en EXIF
  • GSD no válido (falta altitud/distancia focal)
  • Gimbal no en posición nadir (debe estar entre -85° y -95°)</translation>
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
        <translation>KML de extensión de cobertura guardado: {area}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="318"/>
        <source>

Images may be skipped for:
  • Missing GPS data
  • No valid GSD
  • Gimbal not nadir</source>
        <translation>

Las imágenes pueden omitirse por:
  • Faltan datos GPS
  • GSD no válido
  • Gimbal no en posición nadir</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="326"/>
        <source>Coverage Extent KML Generated</source>
        <translation>KML de extensión de cobertura generado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/CoverageExtentExportController.py" line="328"/>
        <source>Coverage extent KML file created successfully!

File: {file}
Images processed: {processed}
Images skipped: {skipped}
Coverage areas: {areas}
Total area: {area}{skip_info}</source>
        <translation>¡Archivo KML de extensión de cobertura creado correctamente!

Archivo: {file}
Imágenes procesadas: {processed}
Imágenes omitidas: {skipped}
Áreas de cobertura: {areas}
Área total: {area}{skip_info}</translation>
    </message>
</context>
<context>
    <name>DetectionRowWidget</name>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="62"/>
        <source>CLASS</source>
        <translation>CLASE</translation>
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
        <translation>Transmisión: --</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="109"/>
        <source>View</source>
        <translation>Ver</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="112"/>
        <source>Open the full-size thumbnail and metadata.</source>
        <translation>Abrir la miniatura a tamaño completo y los metadatos.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="119"/>
        <source>Copy GPS</source>
        <translation>Copiar GPS</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/detection_row.ui" line="122"/>
        <source>Copy the detection&apos;s coordinates to the clipboard in the operator-preferred format.</source>
        <translation>Copiar las coordenadas de la detección al portapapeles en el formato preferido por el operador.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="115"/>
        <source>{name} ({code})</source>
        <translation>{name} ({code})</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="124"/>
        <source>Feed: {feed}</source>
        <translation>Transmisión: {feed}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="132"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Serie de la aeronave: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="150"/>
        <source>no
thumb</source>
        <translation>sin
miniatura</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="156"/>
        <source>bad
thumb</source>
        <translation>miniatura
inválida</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="224"/>
        <source>Detection</source>
        <translation>Detección</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/DetectionRowWidget.py" line="283"/>
        <source>No image available.</source>
        <translation>No hay imagen disponible.</translation>
    </message>
</context>
<context>
    <name>DirectoriesPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="55"/>
        <source>Select Input Directory</source>
        <translation>Seleccionar directorio de entrada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/DirectoriesPage.py" line="72"/>
        <source>Select Output Directory</source>
        <translation>Seleccionar directorio de salida</translation>
    </message>
</context>
<context>
    <name>ExportProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="65"/>
        <source>Processing...</source>
        <translation>Procesando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="79"/>
        <source>Starting...</source>
        <translation>Iniciando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="83"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="135"/>
        <source>Cancelling...</source>
        <translation>Cancelando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ExportProgressDialog.py" line="136"/>
        <source>Cancellation requested...</source>
        <translation>Cancelación solicitada...</translation>
    </message>
</context>
<context>
    <name>FlightPairingDialog</name>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="14"/>
        <source>Add Flight Feed</source>
        <translation>Agregar transmisión de vuelo</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="27"/>
        <source>Ask the drone operator to read out the 6-character pairing code shown on their controller.</source>
        <translation>Pida al operador del dron que lea el código de emparejamiento de 6 caracteres que aparece en su controlador.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="40"/>
        <source>e.g. K3F7PM</source>
        <translation>p. ej., K3F7PM</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="85"/>
        <source>Pairing…</source>
        <translation>Emparejando…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="98"/>
        <source>Looking up code, exchanging keys, gathering ICE candidates.</source>
        <translation>Buscando el código, intercambiando claves y recopilando candidatos ICE.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="135"/>
        <source>Pairing failed</source>
        <translation>Error de emparejamiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="69"/>
        <location filename="../resources/views/flight/flight_pairing.ui" line="200"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_pairing.ui" line="207"/>
        <source>Connect</source>
        <translation>Conectar</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="67"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="85"/>
        <source>drone has {current}/{limit} viewers</source>
        <translation>el dron tiene {current}/{limit} visores conectados</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="98"/>
        <source>known device — same fingerprint as last pair</source>
        <translation>dispositivo conocido — misma huella que en el último emparejamiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightPairingDialog.py" line="101"/>
        <source>new device</source>
        <translation>dispositivo nuevo</translation>
    </message>
</context>
<context>
    <name>FlightTile</name>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="460"/>
        <source>Feed {code}</source>
        <translation>Transmisión {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="298"/>
        <source>Choose recording directory</source>
        <translation>Elegir directorio de grabación</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="328"/>
        <source>REC ● {filename}</source>
        <translation>REC ● {filename}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="333"/>
        <source>REC error: {msg}</source>
        <translation>Error de REC: {msg}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="341"/>
        <source>REC failed to start</source>
        <translation>No se pudo iniciar la grabación</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="355"/>
        <source>Recording saved</source>
        <translation>Grabación guardada</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="364"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="383"/>
        <source>Network: {state}</source>
        <translation>Red: {state}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="377"/>
        <source>latency: {ms:.0f}ms</source>
        <translation>latencia: {ms:.0f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="379"/>
        <source>latency: --</source>
        <translation>latencia: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="457"/>
        <source>{name} · {code}</source>
        <translation>{name} · {code}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="482"/>
        <source>Aircraft serial: {sn}</source>
        <translation>Serie de la aeronave: {sn}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="520"/>
        <source>Rename Feed</source>
        <translation>Cambiar nombre de transmisión</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="522"/>
        <source>Nickname for this drone (persists across new pairing codes via the aircraft serial number). Leave blank to clear.</source>
        <translation>Alias de este dron (se conserva aunque cambie el código de emparejamiento, mediante el número de serie de la aeronave). Déjelo en blanco para borrarlo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="554"/>
        <source>Initializing</source>
        <translation>Inicializando</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="555"/>
        <source>Connecting</source>
        <translation>Conectando</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="556"/>
        <location filename="../app/core/views/flight/FlightTile.py" line="557"/>
        <source>Connected</source>
        <translation>Conectado</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="558"/>
        <source>Disconnected</source>
        <translation>Desconectado</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="559"/>
        <source>Failed</source>
        <translation>Fallido</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="560"/>
        <source>Closed</source>
        <translation>Cerrado</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="574"/>
        <source>Rename Feed...</source>
        <translation>Cambiar nombre de transmisión...</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="591"/>
        <source>Restore</source>
        <translation>Restaurar</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="595"/>
        <source>Maximize</source>
        <translation>Maximizar</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="580"/>
        <source>Full Screen</source>
        <translation>Pantalla completa</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="601"/>
        <source>Mute Detections in Gallery</source>
        <translation>Ocultar detecciones en la galería</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="617"/>
        <source>Stop Recording</source>
        <translation>Detener grabación</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="621"/>
        <source>Start Recording…</source>
        <translation>Iniciar grabación…</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="625"/>
        <source>Reconnect</source>
        <translation>Reconectar</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightTile.py" line="631"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
</context>
<context>
    <name>FlightTileContents</name>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="44"/>
        <source>Waiting for video…</source>
        <translation>Esperando video…</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_tile.ui" line="90"/>
        <source>Network: new</source>
        <translation>Red: nueva</translation>
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
        <translation>latencia: --</translation>
    </message>
</context>
<context>
    <name>FlightTileController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="191"/>
        <source>Looking up code {code} and connecting to the drone.</source>
        <translation>Buscando el código {code} y conectando con el dron.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="266"/>
        <source>Name this device</source>
        <translation>Nombrar este dispositivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="268"/>
        <source>Give this publisher a name so you can recognise it next time (e.g. &apos;Operator A&apos;s M4E&apos;).</source>
        <translation>Asigne un nombre a este emisor para reconocerlo la próxima vez (p. ej., &apos;M4E del operador A&apos;).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="286"/>
        <source>Device &apos;{label}&apos; presented a different DTLS fingerprint than the last time you paired with it. This could mean the controller was reset, a different controller is using the label, or somebody is impersonating it.

Reject if you weren&apos;t expecting this.</source>
        <translation>El dispositivo &apos;{label}&apos; presentó una huella DTLS distinta de la del último emparejamiento. Esto podría significar que el controlador se restableció, que otro controlador está usando esa etiqueta o que alguien está suplantándolo.

Rechácelo si no esperaba este cambio.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="453"/>
        <source>Pairing ended before video could start. Ask the operator to generate a new code and try again.</source>
        <translation>El emparejamiento terminó antes de que pudiera iniciarse el video. Pida al operador que genere un código nuevo e inténtelo de nuevo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="294"/>
        <source>Fingerprint mismatch — &apos;{label}&apos;</source>
        <translation>Huella no coincidente — &apos;{label}&apos;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="303"/>
        <source>Fingerprint changed on {ts}; previous identity was overwritten after operator review.</source>
        <translation>La huella cambió el {ts}; la identidad anterior se sobrescribió tras la revisión del operador.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightTileController.py" line="395"/>
        <source>This drone already has {current} viewers connected (maximum {limit}). Ask one to disconnect, or try again later.</source>
        <translation>Este dron ya tiene {current} visores conectados (máximo {limit}). Pida a uno que se desconecte o inténtelo más tarde.</translation>
    </message>
</context>
<context>
    <name>FlightViewerController</name>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="499"/>
        <source>New flight session</source>
        <translation>Nueva sesión de vuelo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="501"/>
        <source>Mobile started a new flight under code {code}. The previous session&apos;s detections are still saved on this computer. Discard them, or keep them archived?</source>
        <translation>La app móvil inició un vuelo nuevo con el código {code}. Las detecciones de la sesión anterior siguen guardadas en este equipo. ¿Desea descartarlas o mantenerlas archivadas?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="627"/>
        <source>Image Analysis</source>
        <translation>Análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="650"/>
        <source>Streaming Detector</source>
        <translation>Detector de transmisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="667"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/flight/FlightViewerController.py" line="668"/>
        <source>Failed to open {target}:
{error}</source>
        <translation>No se pudo abrir {target}:
{error}</translation>
    </message>
</context>
<context>
    <name>FlightViewerWindow</name>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="14"/>
        <source>ADIAT Flight Viewer</source>
        <translation>Visor de vuelo ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="21"/>
        <source>Add a feed to begin.  Use Add Feed in the toolbar.</source>
        <translation>Agregue una transmisión para comenzar. Use Agregar transmisión en la barra de herramientas.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="76"/>
        <source>Main Toolbar</source>
        <translation>Barra de herramientas principal</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="97"/>
        <source>+ Add Feed</source>
        <translation>+ Agregar transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="49"/>
        <source>Menu</source>
        <translation>Menú</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="66"/>
        <source>Help</source>
        <translation>Ayuda</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="100"/>
        <source>Pair with an ADIAT Mobile drone controller using a 6-character code.</source>
        <translation>Emparejar con un controlador de dron de ADIAT Mobile mediante un código de 6 caracteres.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="105"/>
        <source>Mission Gallery</source>
        <translation>Galería de la misión</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="114"/>
        <source>Show or hide the aggregate Mission Gallery panel.</source>
        <translation>Mostrar u ocultar el panel agregado de la galería de la misión.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="119"/>
        <source>Save Layout</source>
        <translation>Guardar diseño</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="122"/>
        <source>Save the current dock arrangement for next session.</source>
        <translation>Guardar la disposición actual de paneles para la próxima sesión.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="127"/>
        <source>Restore Layout</source>
        <translation>Restaurar diseño</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="130"/>
        <source>Apply the last saved dock arrangement.</source>
        <translation>Aplicar la última disposición de paneles guardada.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="135"/>
        <source>Close Viewer</source>
        <translation>Cerrar visor</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="140"/>
        <source>Map</source>
        <translation>Mapa</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="149"/>
        <source>Show or hide the detection map dock.</source>
        <translation>Mostrar u ocultar el panel del mapa de detecciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="154"/>
        <source>Open Image Analysis</source>
        <translation>Abrir análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="157"/>
        <source>Switch to the Image Analysis window for post-flight image review.</source>
        <translation>Cambiar a la ventana de análisis de imágenes para revisar imágenes después del vuelo.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="162"/>
        <source>Open Streaming Detector</source>
        <translation>Abrir detector de transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="165"/>
        <source>Switch to the Streaming Detector window for RTMP / HDMI capture sessions.</source>
        <translation>Cambiar a la ventana del detector de transmisión para sesiones de captura RTMP / HDMI.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="170"/>
        <source>ADIAT Help</source>
        <translation>Ayuda de ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/flight_viewer.ui" line="173"/>
        <source>Open the ADIAT documentation in your browser.</source>
        <translation>Abrir la documentación de ADIAT en el navegador.</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/FlightViewerWindow.py" line="274"/>
        <source>Rename Feed...</source>
        <translation>Cambiar nombre de transmisión...</translation>
    </message>
</context>
<context>
    <name>FrameTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="52"/>
        <source>Enable Processing Region Mask</source>
        <translation>Activar máscara de región de procesamiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="55"/>
        <source>Enable to restrict detection processing to a specific region of the video.
Useful for excluding edges, UI overlays, or focusing on specific areas.
Improves performance by not processing masked regions.</source>
        <translation>Active esta opción para limitar el procesamiento de detecciones a una región específica del video.
Útil para excluir bordes, superposiciones de interfaz o concentrarse en áreas concretas.
Mejora el rendimiento al no procesar las regiones enmascaradas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="67"/>
        <source>Enable Frame Buffer</source>
        <translation>Activar margen de fotograma</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="69"/>
        <source>Exclude a uniform border from all edges of the video.
Enter the number of pixels to exclude from each edge.
The inner area will be processed for detections.</source>
        <translation>Excluye un borde uniforme en todos los lados del video.
Introduzca el número de píxeles que se excluirán de cada borde.
El área interior se procesará para buscar detecciones.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="77"/>
        <source>Frame Buffer Settings</source>
        <translation>Ajustes de margen de fotograma</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="82"/>
        <source>Buffer (pixels):</source>
        <translation>Margen (píxeles):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="87"/>
        <source>Number of pixels to exclude from all edges (0-1000).
A value of 50 excludes 50 pixels from top, bottom, left, and right.
Useful for removing UI overlays or camera lens distortion at edges.
This value is based on the original video resolution.</source>
        <translation>Número de píxeles que se excluirán de todos los bordes (0-1000).
Un valor de 50 excluye 50 píxeles arriba, abajo, a la izquierda y a la derecha.
Útil para quitar superposiciones de interfaz o distorsión de lente en los bordes.
Este valor se basa en la resolución original del video.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="97"/>
        <source>Enable Image Mask</source>
        <translation>Activar máscara de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="99"/>
        <source>Load a black/white image as a custom mask.
White areas will be processed, black areas excluded.
The mask will be scaled to match the video resolution.</source>
        <translation>Carga una imagen en blanco y negro como máscara personalizada.
Las zonas blancas se procesarán y las zonas negras se excluirán.
La máscara se escalará para coincidir con la resolución del video.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="107"/>
        <source>Image Mask Settings</source>
        <translation>Ajustes de máscara de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="114"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="211"/>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="332"/>
        <source>No mask image selected</source>
        <translation>No se ha seleccionado ninguna imagen de máscara</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="117"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="118"/>
        <source>Select a black/white image file to use as mask</source>
        <translation>Seleccionar un archivo de imagen en blanco y negro para usarlo como máscara</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="121"/>
        <source>Clear</source>
        <translation>Borrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="122"/>
        <source>Clear the selected mask image</source>
        <translation>Borrar la imagen de máscara seleccionada</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="128"/>
        <source>White = Process, Black = Exclude</source>
        <translation>Blanco = procesar, negro = excluir</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="136"/>
        <source>Visualization</source>
        <translation>Visualización</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="139"/>
        <source>Show mask overlay on video</source>
        <translation>Mostrar superposición de máscara en el video</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="142"/>
        <source>Display the processing region on the rendered video.
Frame mode: Shows a cyan rectangle outline of the processed area.
Image mask: Shows a semi-transparent overlay of excluded regions.</source>
        <translation>Muestra la región de procesamiento sobre el video renderizado.
Modo de fotograma: muestra un contorno rectangular cian del área procesada.
Máscara de imagen: muestra una superposición semitransparente de las regiones excluidas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="226"/>
        <source>Invalid Image</source>
        <translation>Imagen no válida</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="227"/>
        <source>{error}</source>
        <translation>{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="229"/>
        <source>Could not load the selected image. Please choose a valid image file.</source>
        <translation>No se pudo cargar la imagen seleccionada. Elija un archivo de imagen válido.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="238"/>
        <source>Aspect Ratio Mismatch</source>
        <translation>Discrepancia de relación de aspecto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/FrameTab.py" line="240"/>
        <source>{error}

The mask will be scaled to fit, which may cause distortion.

Do you want to continue?</source>
        <translation>{error}

La máscara se escalará para ajustarse, lo que puede causar distorsión.

¿Desea continuar?</translation>
    </message>
</context>
<context>
    <name>GPSMapController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="104"/>
        <source>No GPS data found in images</source>
        <translation>No se encontraron datos GPS en las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="189"/>
        <source>POD overlay cleared — the elevation/canopy source changed. Recalculate to refresh it.</source>
        <translation>Superposición POD borrada: la fuente de elevación/dosel cambió. Recalcule para actualizarla.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="200"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>La descarga de teselas está deshabilitada en el modo solo sin conexión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="231"/>
        <source>Calculate POD Coverage?</source>
        <translation>¿Calcular la cobertura POD?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="232"/>
        <source>Coverage data is ready. Calculate the probability-of-detection heatmap for this mission now? (May take several minutes.)</source>
        <translation>Los datos de cobertura están listos. ¿Calcular ahora el mapa de calor de probabilidad de detección para esta misión? (Puede tardar varios minutos.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="291"/>
        <source>Your local USGS 3DEP tiles only partially cover this mission.</source>
        <translation>Sus teselas locales USGS 3DEP solo cubren parcialmente esta misión.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="294"/>
        <source>Your local USGS 3DEP tiles do not cover this mission.</source>
        <translation>Sus teselas locales USGS 3DEP no cubren esta misión.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="298"/>
        <source>Local Elevation Coverage</source>
        <translation>Cobertura de elevación local</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="300"/>
        <source>Frames outside the local tiles will use online AWS Terrain Tiles (~30 m) elevation instead. You can download 1 m tiles for this area first, or continue with the fallback.</source>
        <translation>Los fotogramas fuera de las teselas locales usarán la elevación en línea de AWS Terrain Tiles (~30 m). Puede descargar primero teselas de 1 m para esta área o continuar con la alternativa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="303"/>
        <source>Download Tiles...</source>
        <translation>Descargar teselas...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="305"/>
        <source>Continue</source>
        <translation>Continuar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="334"/>
        <source>POD calculation is unavailable</source>
        <translation>El cálculo de POD no está disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="353"/>
        <source>The tile downloader is unavailable</source>
        <translation>El descargador de teselas no está disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="383"/>
        <source>Download Canopy Data?</source>
        <translation>¿Descargar datos de dosel?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="384"/>
        <source>No canopy-height data is configured for this mission.

Download elevation and canopy tiles for this area now so the canopy overlay and terrain-aware detection coverage can use them?

This downloads Meta/WRI canopy height (1 m) and sets it as the canopy source, replacing any LANDFIRE selection (LANDFIRE tiles must be added manually).</source>
        <translation>No hay datos de altura del dosel configurados para esta misión.

¿Descargar ahora teselas de elevación y dosel para esta área para que la superposición de dosel y la cobertura de detección que considera el terreno puedan usarlas?

Esto descarga la altura del dosel Meta/WRI (1 m) y la establece como fuente de datos de dosel, reemplazando cualquier selección de LANDFIRE (las teselas de LANDFIRE deben añadirse manualmente).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="579"/>
        <source>Not covered — no looks</source>
        <translation>Sin cobertura — sin vistas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="580"/>
        <source>Terrain occlusion</source>
        <translation>Oclusión del terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="581"/>
        <source>Canopy</source>
        <translation>Dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="582"/>
        <source>Image resolution (GSD)</source>
        <translation>Resolución de imagen (GSD)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="583"/>
        <source>None</source>
        <translation>Ninguno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="585"/>
        <source>Unknown</source>
        <translation>Desconocido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="603"/>
        <source>{value} ft</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="605"/>
        <source>{value} m</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="606"/>
        <source>Altitude basis: takeoff elevation {elev}</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="608"/>
        <source>Altitude basis: reported AGL (approximate over terrain)</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="789"/>
        <source>Building canopy overlay...</source>
        <translation>Generando superposición de dosel...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="815"/>
        <source>No canopy data covers this area</source>
        <translation>Ningún dato de dosel cubre esta área</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="875"/>
        <source>POD: {pod}% (beta)   Looks: {looks}</source>
        <translation>POD: {pod}% (beta)   Vistas: {looks}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="878"/>
        <source>Limiting factor: {factor}</source>
        <translation>Factor limitante: {factor}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="917"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="930"/>
        <source>Image {n}</source>
        <translation>Imagen {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="918"/>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="933"/>
        <source>View {name}</source>
        <translation>Vista {name}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="890"/>
        <source>Find location in images</source>
        <translation>Buscar ubicación en las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="937"/>
        <source>{name} (no flagged AOIs)</source>
        <translation>{name} (sin AOI marcados)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/GPSMapController.py" line="1072"/>
        <source>GPS coordinate not in any images</source>
        <translation>La coordenada GPS no está en ninguna imagen</translation>
    </message>
</context>
<context>
    <name>GPSMapDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="54"/>
        <source>GPS Map View</source>
        <translation>Vista de mapa GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="108"/>
        <source>Zoom In (+)</source>
        <translation>Acercar (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="112"/>
        <source>Zoom Out (-)</source>
        <translation>Alejar (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="116"/>
        <source>Fit All (F)</source>
        <translation>Ajustar todo (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="120"/>
        <source>Rotate (R)</source>
        <translation>Rotar (R)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="128"/>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="338"/>
        <source>Satellite View</source>
        <translation>Vista satélite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="135"/>
        <source>POD Overlay</source>
        <translation>Superposición POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="139"/>
        <source>Run a map export with the POD option to generate this overlay</source>
        <translation>Ejecute una exportación de mapa con la opción POD para generar esta superposición</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="144"/>
        <source>POD (beta)</source>
        <translation>POD (beta)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="145"/>
        <source>Look count</source>
        <translation>Número de vistas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="146"/>
        <source>Canopy height</source>
        <translation>Altura del dosel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="156"/>
        <source>POD overlay opacity</source>
        <translation>Opacidad de la superposición POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="162"/>
        <source>Download Canopy Tiles</source>
        <translation>Descargar teselas de dosel</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="169"/>
        <source>Calculate POD</source>
        <translation>Calcular POD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="171"/>
        <source>Compute the terrain-aware probability-of-detection heatmap for this mission (may take several minutes)</source>
        <translation>Calcular el mapa de calor de probabilidad de detección que considera el terreno para esta misión (puede tardar varios minutos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="179"/>
        <source>Click point to select • Drag to pan • Scroll to zoom</source>
        <translation>Haga clic en un punto para seleccionar • Arrastre para desplazar • Rueda para acercar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="263"/>
        <source>Downloading tiles is disabled in Offline Only mode</source>
        <translation>La descarga de teselas está deshabilitada en el modo solo sin conexión</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="265"/>
        <source>Download elevation and canopy-height tiles for this mission&apos;s area</source>
        <translation>Descargar teselas de elevación y altura del dosel para el área de esta misión</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="335"/>
        <source>Map View</source>
        <translation>Vista de mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="372"/>
        <source>⚠ {error}</source>
        <translation>⚠ {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="382"/>
        <source>Map Tile Loading Issue</source>
        <translation>Problema al cargar los mosaicos del mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GPSMapDialog.py" line="384"/>
        <source>{error}

The map will continue to work with cached tiles where available.</source>
        <translation>{error}

El mapa seguirá funcionando con los mosaicos en caché donde estén disponibles.</translation>
    </message>
</context>
<context>
    <name>GPSMapView</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1216"/>
        <source>Copy Data</source>
        <translation>Copiar datos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1777"/>
        <location filename="../app/core/views/images/viewer/widgets/GPSMapView.py" line="1888"/>
        <source>Zoom FOV</source>
        <translation>FOV de zoom</translation>
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
        <translation>Área de interés</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/gallery/GalleryUIComponent.py" line="432"/>
        <source>Areas of Interest</source>
        <translation>Áreas de interés</translation>
    </message>
</context>
<context>
    <name>GeneralSettingsPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="121"/>
        <source>Select AOI Highlight Color</source>
        <translation>Seleccionar color de resaltado del AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="159"/>
        <source>Benchmark Complete</source>
        <translation>Evaluación completada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/GeneralSettingsPage.py" line="161"/>
        <source>Detected {count} CPU core(s).

Recommended number of processes: {recommended}

The slider has been set to {recommended} processes.</source>
        <translation>Se detectaron {count} núcleos de CPU.

Número de procesos recomendado: {recommended}

El deslizador se ha establecido en {recommended} procesos.</translation>
    </message>
</context>
<context>
    <name>GridReviewController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="151"/>
        <source>Grid review works in single-image mode — exit the gallery first.</source>
        <translation>La revisión por cuadrícula funciona en modo de imagen única; salga primero de la galería.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="273"/>
        <source>This image keeps its existing grid — the new size applies to unstarted images.</source>
        <translation>Esta imagen conserva su cuadrícula existente; el nuevo tamaño se aplicará a las imágenes no iniciadas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="320"/>
        <source>Apply Grid to All Images</source>
        <translation>Aplicar cuadrícula a todas las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="322"/>
        <source>{n} image(s) already have review progress recorded at a different grid size.

Reset their progress and apply {rows}×{cols} to them too?

Yes resets them; No keeps them at their current size.</source>
        <translation>{n} imagen(es) ya tienen progreso de revisión registrado con un tamaño de cuadrícula distinto.

¿Restablecer su progreso y aplicarles también {rows}×{cols}?

Sí las restablece; No las mantiene en su tamaño actual.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="391"/>
        <source>Image fully reviewed — advancing</source>
        <translation>Imagen completamente revisada; avanzando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/grid/GridReviewController.py" line="628"/>
        <source>cell {cell}/{cells} — image {image}/{images} — run {percent}% reviewed</source>
        <translation>celda {cell}/{cells} — imagen {image}/{images} — conjunto {percent}% revisado</translation>
    </message>
</context>
<context>
    <name>GridReviewDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="52"/>
        <source>Suggested: {rows}×{cols} (person ≈ {px} px on screen at cell zoom)</source>
        <translation>Sugerido: {rows}×{cols} (persona ≈ {px} px en pantalla con zoom de celda)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/GridReviewDialog.py" line="55"/>
        <source>Suggested: {rows}×{cols}</source>
        <translation>Sugerido: {rows}×{cols}</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="14"/>
        <source>Grid Review Settings</source>
        <translation>Configuración de revisión por cuadrícula</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="23"/>
        <source>Choose how many cells the review grid divides each image into. Smaller cells mean a higher zoom per cell.</source>
        <translation>Elija en cuántas celdas divide cada imagen la cuadrícula de revisión. Las celdas más pequeñas implican mayor zoom por celda.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="32"/>
        <source>Rows</source>
        <translation>Filas</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="52"/>
        <source>Columns</source>
        <translation>Columnas</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="74"/>
        <source>Mark cells reviewed when advancing (Space)</source>
        <translation>Marcar las celdas como revisadas al avanzar (Espacio)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="84"/>
        <source>Draw a 3×3 guide inside the active cell to focus your scan. Visual only — it does not change what gets reviewed.</source>
        <translation>Dibujar una guía 3×3 dentro de la celda activa para enfocar la revisión. Solo visual; no cambia lo que se marca como revisado.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="87"/>
        <source>Show 3×3 focus guide inside each cell</source>
        <translation>Mostrar guía de enfoque 3×3 dentro de cada celda</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="97"/>
        <source>Apply the chosen rows and columns to every image in this dataset, not just the current one. Images you have already started reviewing keep their progress unless you confirm a reset.</source>
        <translation>Aplicar las filas y columnas elegidas a todas las imágenes de este conjunto de datos, no solo a la actual. Las imágenes cuya revisión ya haya empezado conservan su progreso salvo que confirme un restablecimiento.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="100"/>
        <source>Apply this grid size to all images</source>
        <translation>Aplicar este tamaño de cuadrícula a todas las imágenes</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="112"/>
        <source>No grid suggestion available (image GSD unknown).</source>
        <translation>No hay sugerencia de cuadrícula disponible (GSD de la imagen desconocido).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/GridReviewDialog.ui" line="119"/>
        <source>Use Suggestion</source>
        <translation>Usar sugerencia</translation>
    </message>
</context>
<context>
    <name>HSVColorRange</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
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
        <translation>Seleccionar un color objetivo desde una imagen para detectar.
Abre un selector de color que le permite:
• Cargar una imagen de la carpeta de entrada
• Hacer clic en píxeles para muestrear colores
• Calcular automáticamente los valores HSV
• Establecer los rangos de la matiz, Saturación y Valor
El color seleccionado se convierte en el centro de su rango de detección HSV.
Ajuste los valores de rango +/- para capturar variaciones de color.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="37"/>
        <source> Pick Color</source>
        <translation> Elegir color</translation>
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
        <translation>Vista previa visual del color objetivo seleccionado actualmente.
Muestra el color central de su rango de detección HSV.
La detección real coincidirá con los colores dentro de los rangos +/- especificados alrededor de este color.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="92"/>
        <source>Hue range tolerance for color detection.
Hue represents the actual color (red, green, blue, etc.) on a 0-179 scale.
Adjust the -/+ values to allow variation in the color hue.</source>
        <translation>Tolerancia de rango de la matiz para la detección de color.
La matiz representa el color real (rojo, verde, azul, etc.) en una escala de 0 a 179.
Ajuste los valores -/+ para permitir variaciones en el tono del color.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="97"/>
        <source>Hue Range</source>
        <translation>Rango de la matiz</translation>
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
        <translation>Tolerancia inferior del rango de tono.
• Rango: 0 a 179
• Predeterminado: 20
Se resta del valor de tono objetivo para definir el límite inferior.
Valores más bajos = coincidencia de color más estricta, valores más altos = mayor variación de color aceptada.
Ejemplo: Tono objetivo 100, menos 20 = detecta tonos de 80 a 100.</translation>
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
        <translation>Tolerancia superior del rango de tono.
• Rango: 0 a 179
• Predeterminado: 20
Se suma al valor de tono objetivo para definir el límite superior.
Valores más bajos = coincidencia de color más estricta, valores más altos = mayor variación de color aceptada.
Ejemplo: Tono objetivo 100, más 20 = detecta tonos de 100 a 120.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="198"/>
        <source>Saturation range tolerance for color detection.
Saturation represents color intensity (0=gray, 255=fully saturated) on a 0-255 scale.
Adjust the -/+ values to allow variation in color intensity.</source>
        <translation>Tolerancia del rango de saturación para la detección de color.
La saturación representa la intensidad del color (0=gris, 255=totalmente saturado) en una escala de 0 a 255.
Ajuste los valores -/+ para permitir variaciones en la intensidad del color.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="203"/>
        <source>Saturation Range</source>
        <translation>Rango de saturación</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="227"/>
        <source>Lower saturation range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target saturation value to define the lower bound.
Lower values = requires vivid colors, higher values = accepts faded/washed out colors.
Example: Target saturation 150, minus 50 = detects saturations from 100-150.</source>
        <translation>Tolerancia inferior del rango de saturación.
• Rango: 0 a 255
• Predeterminado: 50
Se resta del valor de saturación objetivo para definir el límite inferior.
Valores más bajos = requiere colores vivos, valores más altos = acepta colores apagados/desaturados.
Ejemplo: Saturación objetivo 150, menos 50 = detecta saturaciones de 100 a 150.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="262"/>
        <source>Upper saturation range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target saturation value to define the upper bound.
Lower values = requires exact saturation, higher values = accepts more saturated colors.
Example: Target saturation 150, plus 50 = detects saturations from 150-200.</source>
        <translation>Tolerancia superior del rango de saturación.
• Rango: 0 a 255
• Predeterminado: 50
Se suma al valor de saturación objetivo para definir el límite superior.
Valores más bajos = requiere saturación exacta, valores más altos = acepta colores más saturados.
Ejemplo: Saturación objetivo 150, más 50 = detecta saturaciones de 150 a 200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="298"/>
        <source>Value (brightness) range tolerance for color detection.
Value represents brightness (0=black, 255=bright) on a 0-255 scale.
Adjust the -/+ values to allow variation in brightness.</source>
        <translation>Tolerancia del rango de valor (brillo) para la detección de color.
El valor representa el brillo (0=negro, 255=brillante) en una escala de 0 a 255.
Ajuste los valores -/+ para permitir variaciones en el brillo.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="303"/>
        <source>Value Range</source>
        <translation>Rango de valor</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="327"/>
        <source>Lower value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Subtracts from the target brightness value to define the lower bound.
Lower values = requires bright pixels, higher values = accepts darker pixels.
Example: Target value 200, minus 50 = detects brightness from 150-200.</source>
        <translation>Tolerancia inferior del rango de valor (brillo).
• Rango: 0 a 255
• Predeterminado: 50
Se resta del valor de brillo objetivo para definir el límite inferior.
Valores más bajos = requiere píxeles brillantes, valores más altos = acepta píxeles más oscuros.
Ejemplo: Valor objetivo 200, menos 50 = detecta brillo de 150 a 200.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="362"/>
        <source>Upper value (brightness) range tolerance.
• Range: 0 to 255
• Default: 50
Adds to the target brightness value to define the upper bound.
Lower values = requires exact brightness, higher values = accepts brighter pixels.
Example: Target value 200, plus 50 = detects brightness from 200-250.</source>
        <translation>Tolerancia superior del rango de valor (brillo).
• Rango: 0 a 255
• Predeterminado: 50
Se suma al valor de brillo objetivo para definir el límite superior.
Valores más bajos = requiere brillo exacto, valores más altos = acepta píxeles más brillantes.
Ejemplo: Valor objetivo 200, más 50 = detecta brillo de 200 a 250.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="410"/>
        <source>Opens the Range Viewer window to:
- See the range of colors that will be searched for in the image analysis.
Use this to see what colors are going to be detected and optimize the color ranges before processing.</source>
        <translation>Abre la ventana del Visor de rango para:
- Ver el rango de colores que se buscarán en el análisis de imágenes.
Úselo para ver qué colores se detectarán y optimizar los rangos de color antes del procesamiento.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRange.ui" line="415"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
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
        <translation>Asistente de rango de color HSV - Selección por clic</translation>
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
        <translation>Visor interactivo de imagen con selección de color.

NAVEGACIÓN:
• Rueda del mouse: acercar/alejar
• Arrastrar con clic izquierdo: desplazar la imagen
• Doble clic: ajustar la imagen a la vista

SELECCIÓN DE COLOR:
• Mantener CTRL + clic izquierdo: seleccionar colores similares
• Mantener CTRL+MAYÚS + clic izquierdo: quitar/borrar selección
• Teclas [ ]: ajustar el radio de selección
• CTRL+Z: deshacer la última selección
• CTRL+MAYÚS+Z: rehacer

VISUALIZACIÓN:
• Superposición blanca = píxeles seleccionados
• Texto amarillo = valores HSV en la posición del cursor
• El cursor circular aparece al mantener CTRL</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="741"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="743"/>
        <source>Browse for an image file to load.
Opens a file dialog to select an image from your computer.
• Supported formats: PNG, JPG, JPEG, BMP
• Load an image to start selecting colors
The image will be displayed in the main viewer on the left.</source>
        <translation>Busque un archivo de imagen para cargarlo.
Abre un cuadro de diálogo para seleccionar una imagen del equipo.
• Formatos admitidos: PNG, JPG, JPEG, BMP
• Cargue una imagen para empezar a seleccionar colores
La imagen se mostrará en el visor principal de la izquierda.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="753"/>
        <source>Reset</source>
        <translation>Restablecer</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="755"/>
        <source>Reset all selections and start over.
• Clears all selected pixels (white overlay)
• Resets HSV ranges to defaults
• Clears the mask preview
• Undoable with CTRL+Z
Use this to start fresh without reloading the image.</source>
        <translation>Restablece todas las selecciones y empieza de nuevo.
• Borra todos los píxeles seleccionados (superposición blanca)
• Restablece los rangos HSV a sus valores predeterminados
• Borra la vista previa de la máscara
• Puede deshacerse con CTRL+Z
Use esta opción para empezar de cero sin volver a cargar la imagen.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="766"/>
        <source>Selection Radius:</source>
        <translation>Radio de selección:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="768"/>
        <source>Size of the circular selection cursor.
Determines how many pixels are sampled when you CTRL+Click.</source>
        <translation>Tamaño del cursor circular de selección.
Determina cuántos píxeles se muestrean al hacer CTRL+clic.</translation>
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
        <translation>Define el radio del cursor de selección en píxeles.
• Rango: 1-50 píxeles
• Predeterminado: 1 píxel (selección de un solo píxel)
Radio mayor:
• Muestrea más píxeles al hacer clic
• Promedia los colores dentro del círculo
• Útil para seleccionar degradados o áreas texturizadas
Radio menor:
• Selección más precisa
• Mejor para colores sólidos
Atajos de teclado: [ disminuye, ] aumenta 2 píxeles</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="793"/>
        <source>Color Tolerance:</source>
        <translation>Tolerancia de color:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="795"/>
        <source>HSV color matching tolerance.
Controls how similar colors must be to get selected.</source>
        <translation>Tolerancia de coincidencia de color HSV.
Controla qué tan similares deben ser los colores para seleccionarse.</translation>
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
        <translation>Define la tolerancia de color para detectar píxeles similares.
• Rango: 0-50
• Predeterminado: 2
Al hacer CTRL+clic, se seleccionan los píxeles cuyos valores HSV estén dentro de esta tolerancia:
• 0: solo coincidencia exacta (muy estricto)
• 2-5: variaciones pequeñas (recomendado para la mayoría de los casos)
• 10+: variaciones grandes (puede seleccionar demasiados colores)
Tolerancia mayor:
• Selecciona más colores similares
• Útil para imágenes con variación de iluminación
• Puede incluir colores no deseados
Tolerancia menor:
• Coincidencia de color más precisa
• Puede omitir algunos píxeles del color objetivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="825"/>
        <source>CTRL+Click: Select similar colors | CTRL+SHIFT+Click: Remove | [ ] : Radius</source>
        <translation>CTRL+clic: seleccionar colores similares | CTRL+MAYÚS+clic: quitar | [ ]: radio</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="831"/>
        <source>Help</source>
        <translation>Ayuda</translation>
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
        <translation>Muestra ayuda e instrucciones detalladas.
Abre un cuadro de diálogo con:
• Instrucciones de uso paso a paso
• Explicación de controles de navegación
• Técnicas de selección de color
• Referencia de atajos de teclado
Haga clic aquí si no sabe cómo usar esta herramienta.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="859"/>
        <source>Selected Color</source>
        <translation>Color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="861"/>
        <source>Average color of all selected pixels.
Shows the center/mean color that will be used for HSV range detection.</source>
        <translation>Color promedio de todos los píxeles seleccionados.
Muestra el color central/promedio que se usará para la detección por rango HSV.</translation>
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
        <translation>Vista previa visual del color seleccionado promedio.
Es el color central calculado a partir de todos los píxeles seleccionados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="876"/>
        <source>Color swatch showing the average of all selected pixels.
This becomes the center color for HSV range detection.</source>
        <translation>Muestra de color con el promedio de todos los píxeles seleccionados.
Este será el color central para la detección por rango HSV.</translation>
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
        <translation>Representación hexadecimal del color seleccionado.
Formato: #RRGGBB</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="889"/>
        <source>Hex color code of the average selected color.
Can be used to identify the exact RGB color value.</source>
        <translation>Código de color hexadecimal del color seleccionado promedio.
Puede usarse para identificar el valor RGB exacto.</translation>
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
        <translation>Valores HSV del color seleccionado.
H = tono (0-360°), S = saturación (0-100%), V = valor (0-100%)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="902"/>
        <source>HSV color values of the average selected color.
This is the center point of your color range.</source>
        <translation>Valores HSV del color seleccionado promedio.
Este es el punto central del rango de color.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="910"/>
        <source>HSV Ranges</source>
        <translation>Rangos HSV</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="912"/>
        <source>HSV color range configuration.
Defines the detection range for each HSV channel.
Center values are calculated from selected pixels.
Buffer values add extra tolerance to catch color variations.</source>
        <translation>Configuración del rango de color HSV.
Define el rango de detección de cada canal HSV.
Los valores centrales se calculan a partir de los píxeles seleccionados.
Los márgenes añaden tolerancia adicional para captar variaciones de color.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="920"/>
        <source>Channel</source>
        <translation>Canal</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="921"/>
        <source>HSV color channel (Hue, Saturation, Value)</source>
        <translation>Canal de color HSV (tono, saturación, valor)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="924"/>
        <source>Center</source>
        <translation>Centro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="925"/>
        <source>Average value of selected pixels for this channel</source>
        <translation>Valor promedio de los píxeles seleccionados para este canal</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="928"/>
        <source>- Buffer</source>
        <translation>- Margen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="929"/>
        <source>Extra tolerance below center value (lower bound buffer)</source>
        <translation>Tolerancia adicional por debajo del valor central (margen inferior)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="932"/>
        <source>+ Buffer</source>
        <translation>+ Margen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="933"/>
        <source>Extra tolerance above center value (upper bound buffer)</source>
        <translation>Tolerancia adicional por encima del valor central (margen superior)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="936"/>
        <source>Final Range</source>
        <translation>Rango final</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="937"/>
        <source>Complete detection range (min-max) after applying buffers</source>
        <translation>Rango de detección completo (mín-máx) después de aplicar los márgenes</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="941"/>
        <source>Hue:</source>
        <translation>Tono:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="942"/>
        <source>Hue channel (color type): 0-360 degrees on color wheel</source>
        <translation>Canal de tono (tipo de color): 0-360 grados en la rueda de color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="947"/>
        <source>Center hue value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-360° (red=0°, green=120°, blue=240°)</source>
        <translation>Valor central de tono (promedio de los píxeles seleccionados).
Se calcula automáticamente a partir de la selección.
Rango: 0-360° (rojo=0°, verde=120°, azul=240°)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="957"/>
        <source>Hue lower bound buffer (subtract from center).
• Range: 0-360°
• Adds tolerance below the center hue
• Larger values detect more hues in the minus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Margen inferior del tono (se resta del centro).
• Rango: 0-360°
• Añade tolerancia por debajo del tono central
• Valores mayores detectan más tonos en la dirección negativa
• Manténgalo estrecho para evitar detectar colores no deseados
ADVERTENCIA: un rango total de tono (menos + más) &gt; 60° puede causar falsos positivos</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="971"/>
        <source>Hue upper bound buffer (add to center).
• Range: 0-360°
• Adds tolerance above the center hue
• Larger values detect more hues in the plus direction
• Keep narrow to avoid detecting unwanted colors
WARNING: Total hue range (minus + plus) &gt; 60° may cause false positives</source>
        <translation>Margen superior del tono (se suma al centro).
• Rango: 0-360°
• Añade tolerancia por encima del tono central
• Valores mayores detectan más tonos en la dirección positiva
• Manténgalo estrecho para evitar detectar colores no deseados
ADVERTENCIA: un rango total de tono (menos + más) &gt; 60° puede causar falsos positivos</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="983"/>
        <source>Final hue detection range.
Shows the complete min-max hue range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Rango final de detección de tono.
Muestra el rango completo mín-máx de tono que se detectará.
Se calcula como: (centro - margen negativo) a (centro + margen positivo)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="990"/>
        <source>WARNING: Too wide of a Hue range can result in false positives!</source>
        <translation>ADVERTENCIA: un rango de tono demasiado amplio puede generar falsos positivos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="994"/>
        <source>Hue range warning.
Your total hue range exceeds 60°.
Wide hue ranges may detect many different colors.
Consider narrowing the buffers for more accurate detection.</source>
        <translation>Advertencia de rango de tono.
El rango total de tono supera 60°.
Los rangos amplios pueden detectar muchos colores distintos.
Considere reducir los márgenes para una detección más precisa.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1002"/>
        <source>Sat:</source>
        <translation>Sat.:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1003"/>
        <source>Saturation channel (color intensity): 0-100%</source>
        <translation>Canal de saturación (intensidad del color): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1008"/>
        <source>Center saturation value (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=gray, 100%=vivid color)</source>
        <translation>Valor central de saturación (promedio de los píxeles seleccionados).
Se calcula automáticamente a partir de la selección.
Rango: 0-100% (0%=gris, 100%=color vivo)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1018"/>
        <source>Saturation lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center saturation
• Larger values detect more desaturated/grayish colors
• Be careful: very low saturation includes gray colors
WARNING: Lower bound &lt; 25% may include unwanted gray/desaturated colors</source>
        <translation>Margen inferior de saturación (se resta del centro).
• Rango: 0-100%
• Añade tolerancia por debajo de la saturación central
• Valores mayores detectan más colores desaturados/grisáceos
• Tenga cuidado: una saturación muy baja incluye colores grises
ADVERTENCIA: un límite inferior &lt; 25% puede incluir colores grises/desaturados no deseados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1032"/>
        <source>Saturation upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center saturation
• Larger values detect more saturated/vivid colors
• Higher saturation generally safe to increase</source>
        <translation>Margen superior de saturación (se suma al centro).
• Rango: 0-100%
• Añade tolerancia por encima de la saturación central
• Valores mayores detectan colores más saturados/vivos
• Aumentar la saturación superior suele ser seguro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1043"/>
        <source>Final saturation detection range.
Shows the complete min-max saturation range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Rango final de detección de saturación.
Muestra el rango completo mín-máx de saturación que se detectará.
Se calcula como: (centro - margen negativo) a (centro + margen positivo)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1050"/>
        <source>WARNING: Too low of a Saturation level can result in false positives!</source>
        <translation>ADVERTENCIA: un nivel de saturación demasiado bajo puede generar falsos positivos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1054"/>
        <source>Saturation range warning.
Your lower saturation bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unwanted gray or desaturated objects.</source>
        <translation>Advertencia de rango de saturación.
El límite inferior de saturación está por debajo del 25%.
La saturación baja incluye colores grisáceos o apagados.
Puede detectar objetos grises o desaturados no deseados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1062"/>
        <source>Val:</source>
        <translation>Val.:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1063"/>
        <source>Value channel (brightness): 0-100%</source>
        <translation>Canal de valor (brillo): 0-100%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1068"/>
        <source>Center value/brightness (average of selected pixels).
Automatically calculated from your selection.
Range: 0-100% (0%=black, 100%=bright)</source>
        <translation>Valor/brillo central (promedio de los píxeles seleccionados).
Se calcula automáticamente a partir de la selección.
Rango: 0-100% (0%=negro, 100%=brillante)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1078"/>
        <source>Value lower bound buffer (subtract from center).
• Range: 0-100%
• Adds tolerance below the center brightness
• Larger values detect darker versions of the color
• Be careful: very low value includes very dark/black colors
WARNING: Lower bound &lt; 25% may include unwanted shadows or dark objects</source>
        <translation>Margen inferior de valor (se resta del centro).
• Rango: 0-100%
• Añade tolerancia por debajo del brillo central
• Valores mayores detectan versiones más oscuras del color
• Tenga cuidado: un valor muy bajo incluye colores muy oscuros/negros
ADVERTENCIA: un límite inferior &lt; 25% puede incluir sombras u objetos oscuros no deseados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1092"/>
        <source>Value upper bound buffer (add to center).
• Range: 0-100%
• Adds tolerance above the center brightness
• Larger values detect brighter versions of the color
• Higher brightness generally safe to increase</source>
        <translation>Margen superior de valor (se suma al centro).
• Rango: 0-100%
• Añade tolerancia por encima del brillo central
• Valores mayores detectan versiones más brillantes del color
• Aumentar el brillo superior suele ser seguro</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1103"/>
        <source>Final value/brightness detection range.
Shows the complete min-max brightness range that will be detected.
Calculated as: (center - minus buffer) to (center + plus buffer)</source>
        <translation>Rango final de detección de valor/brillo.
Muestra el rango completo mín-máx de brillo que se detectará.
Se calcula como: (centro - margen negativo) a (centro + margen positivo)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1110"/>
        <source>WARNING: Too low of a Value level can result in false positives!</source>
        <translation>ADVERTENCIA: un nivel de valor demasiado bajo puede generar falsos positivos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1114"/>
        <source>Value range warning.
Your lower value bound is below 25%.
Low value includes very dark colors.
May detect unwanted shadows or dark objects.</source>
        <translation>Advertencia de rango de valor.
El límite inferior de valor está por debajo del 25%.
Los valores bajos incluyen colores muy oscuros.
Puede detectar sombras u objetos oscuros no deseados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1124"/>
        <source>Statistics</source>
        <translation>Estadísticas</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1126"/>
        <source>Statistics about your current selection.
Shows how many pixels are selected and what percentage of the image they represent.</source>
        <translation>Estadísticas de la selección actual.
Muestra cuántos píxeles están seleccionados y qué porcentaje de la imagen representan.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1130"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1225"/>
        <source>Selected Pixels: 0</source>
        <translation>Píxeles seleccionados: 0</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1132"/>
        <source>Number of pixels currently selected.
Shows the total count of white-highlighted pixels in the main viewer.
Updates in real-time as you select colors.</source>
        <translation>Número de píxeles seleccionados actualmente.
Muestra el conteo total de píxeles resaltados en blanco en el visor principal.
Se actualiza en tiempo real al seleccionar colores.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1137"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1226"/>
        <source>Coverage: 0%</source>
        <translation>Cobertura: 0%</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1139"/>
        <source>Percentage of image covered by selection.
Shows what portion of the total image is selected.
• Low %: Precise selection, may miss some target pixels
• High %: Broad selection, may include unwanted areas</source>
        <translation>Porcentaje de la imagen cubierto por la selección.
Muestra qué parte de la imagen total está seleccionada.
• % bajo: selección precisa; puede omitir algunos píxeles objetivo
• % alto: selección amplia; puede incluir áreas no deseadas</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1148"/>
        <source>Mask Preview</source>
        <translation>Vista previa de máscara</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1150"/>
        <source>Black and white preview of the detection mask.
Shows what pixels will be detected with current HSV ranges and buffers.</source>
        <translation>Vista previa en blanco y negro de la máscara de detección.
Muestra qué píxeles se detectarán con los rangos y márgenes HSV actuales.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1161"/>
        <source>Grayscale mask preview.
• White pixels: Will be detected with current settings
• Black pixels: Will NOT be detected
Updates automatically when you adjust buffers.
Use this to verify your HSV range captures the target without false positives.</source>
        <translation>Vista previa de máscara en escala de grises.
• Píxeles blancos: se detectarán con los ajustes actuales
• Píxeles negros: NO se detectarán
Se actualiza automáticamente al ajustar los márgenes.
Use esta opción para verificar que el rango HSV capture el objetivo sin falsos positivos.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1179"/>
        <source>Select Image</source>
        <translation>Seleccionar imagen</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1180"/>
        <source>Images (*.png *.jpg *.jpeg *.bmp)</source>
        <translation>Imágenes (*.png *.jpg *.jpeg *.bmp)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1237"/>
        <source>Selected Pixels: {0:,}</source>
        <translation>Píxeles seleccionados: {0:,}</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1238"/>
        <source>Coverage: {0:.1f}%</source>
        <translation>Cobertura: {0:.1f}%</translation>
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
&lt;h2&gt;Asistente de rango de color HSV - Ayuda&lt;/h2&gt;

&lt;p&gt;Esta herramienta le ayuda a elegir el rango de color HSV de un color específico en una foto.
Haga clic en el botón EXAMINAR para abrir una imagen.&lt;/p&gt;

&lt;h3&gt;Navegación:&lt;/h3&gt;
&lt;p&gt;• Use la rueda del ratón para acercar/alejar la imagen&lt;br&gt;
• Use el botón izquierdo del ratón para arrastrar y desplazar la imagen&lt;/p&gt;

&lt;h3&gt;Selección de color:&lt;/h3&gt;
&lt;p&gt;• Mantenga pulsada la &lt;b&gt;tecla CTRL/OPCIÓN&lt;/b&gt; mientras hace clic izquierdo sobre un color de la imagen que desee seleccionar&lt;br&gt;
• Todos los píxeles de la imagen que compartan ese valor de color HSV se seleccionarán y resaltarán en blanco&lt;/p&gt;

&lt;h3&gt;Radio de selección:&lt;/h3&gt;
        &lt;p&gt;Puede ajustar el Radio de selección del cursor del ratón para que sea mayor o menor.
        Al hacer CTRL+clic se seleccionarán todos los colores dentro de ese radio del cursor.&lt;/p&gt;

&lt;h3&gt;Correcciones:&lt;/h3&gt;
&lt;p&gt;Si comete un error, puede DESHACER la última selección o pulsar el botón REINICIAR para empezar de nuevo.&lt;/p&gt;

&lt;h3&gt;Vista previa de la máscara:&lt;/h3&gt;
        &lt;p&gt;En el lado derecho, la sección Vista previa de la máscara le mostrará qué píxeles de la imagen se seleccionaron.
        Si ve píxeles fuera del objeto que intenta seleccionar, es posible que deba
        ajustar la Tolerancia de color o ser más cuidadoso con sus selecciones.&lt;/p&gt;
</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVColorRangeAssistant.py" line="1504"/>
        <source>HSV Color Range Assistant - Help</source>
        <translation>Asistente de rango de color HSV - Ayuda</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="97"/>
        <source>No Colors Selected</source>
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="120"/>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="125"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="176"/>
        <source>Hue Expansion</source>
        <translation>Expansión de tono</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="178"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Cuando está habilitado, expandir cada AOI a través de los vecinos cuyo tono esté dentro de +/- {0}
(unidades OpenCV) del tono medio de los píxeles detectados originalmente.
Se excluyen los píxeles con saturación inferior al {1}% o valor inferior al {2}%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeController.py" line="468"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/HSVColorRangeWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
</context>
<context>
    <name>HSVColorRangeWizardController</name>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="53"/>
        <source>No Colors Selected</source>
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="63"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="99"/>
        <source>Hue Expansion</source>
        <translation>Expansión de tono</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="101"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Cuando está habilitado, expandir cada AOI a través de los vecinos cuyo tono esté dentro de +/- {0}
(unidades OpenCV) del tono medio de los píxeles detectados originalmente.
Se excluyen los píxeles con saturación inferior al {1}% o valor inferior al {2}%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/controllers/HSVColorRangeWizardController.py" line="408"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
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
        <translation>Tolerancia
de coincidencia:</translation>
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
        <translation>Entrada de código de color hexadecimal.
Introduzca colores como códigos hexadecimales (por ejemplo, #FF0000 para rojo).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="102"/>
        <source>Enter a hexadecimal color code.
• Format: #RRGGBB (e.g., #FF0000 for red, #00FF00 for green)
• Also accepts short format: #RGB (e.g., #F00 for red)
Type or paste a hex code to quickly set a specific color.
The color will be converted to HSV automatically.</source>
        <translation>Introduzca un código de color hexadecimal.
• Formato: #RRGGBB (por ejemplo, #FF0000 para rojo, #00FF00 para verde)
• También acepta el formato corto: #RGB (por ejemplo, #F00 para rojo)
Escriba o pegue un código hexadecimal para establecer rápidamente un color específico.
El color se convertirá automáticamente a HSV.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="111"/>
        <source>Reset to Default</source>
        <translation>Restablecer valores predeterminados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="114"/>
        <source>Reset to default color and ranges.
• Color: Pure red (H:0°, S:100%, V:100%)
• Hue range: ±20° (total 40° range)
• Saturation range: ±20%
• Value range: ±20%
Use this to start over with standard settings.</source>
        <translation>Restablece el color y los rangos predeterminados.
• Color: rojo puro (H:0°, S:100%, V:100%)
• Rango de tono: ±20° (rango total de 40°)
• Rango de saturación: ±20%
• Rango de valor: ±20%
Use esta opción para empezar de nuevo con ajustes estándar.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="137"/>
        <source>Saturation / Value</source>
        <translation>Saturación / Valor</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="141"/>
        <source>Saturation and Value (brightness) selector.
Saturation controls color intensity (left=gray, right=vivid).
Value controls brightness (bottom=dark, top=bright).</source>
        <translation>Selector de saturación y valor (brillo).
La saturación controla la intensidad del color (izquierda=gris, derecha=vivo).
El valor controla el brillo (abajo=oscuro, arriba=brillante).</translation>
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
        <translation>Selector interactivo de saturación/valor.
• Haga clic en cualquier punto para definir la saturación y el brillo del color central
• Círculo blanco = posición actual del color central
• Rectángulo blanco = rango de detección (ajustable)
• Arrastre los tiradores blancos de las esquinas para ajustar los rangos de saturación/valor
• Rango horizontal = tolerancia de saturación
• Rango vertical = tolerancia de valor/brillo
Los rangos mayores detectan más variaciones de color, pero pueden incluir colores no deseados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="165"/>
        <source>Hue</source>
        <translation>Tono</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="169"/>
        <source>Hue (color type) selector.
Hue represents the actual color: red, orange, yellow, green, cyan, blue, purple, magenta.</source>
        <translation>Selector de tono (tipo de color).
El tono representa el color propiamente dicho: rojo, naranja, amarillo, verde, cian, azul, morado, magenta.</translation>
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
        <translation>Selector interactivo de tono en anillo de color.
• Haga clic en el anillo para seleccionar un tono (tipo de color)
• Línea blanca = tono central actual
• Arcos y líneas grises = rango de detección de tono (ajustable)
• Arrastre los tiradores circulares blancos para ajustar el rango de tono
• Tirador izquierdo = límite inferior (rango negativo)
• Tirador derecho = límite superior (rango positivo)
Advertencia: los rangos de tono mayores de 60° pueden detectar demasiados colores.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="205"/>
        <source>Use Image</source>
        <translation>Usar imagen</translation>
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
        <translation>Abre el asistente de rango de color HSV.
Herramienta avanzada para seleccionar colores desde una imagen:
• Cargue una imagen desde la carpeta de entrada
• Haga clic en píxeles para muestrear colores
• Calcula automáticamente rangos HSV óptimos
• Muestra una vista previa en tiempo real de los resultados de detección
Recomendado para encontrar el mejor rango de color para el objetivo.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="219"/>
        <source>Pick Screen Color</source>
        <translation>Tomar color de pantalla</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="222"/>
        <source>Pick a color from anywhere on your screen.
Opens a color picker that lets you:
• Click anywhere on your screen to sample a color
• Sample from other applications or images
The picked color will be set as the center color.
Ranges remain unchanged - adjust manually after picking.</source>
        <translation>Toma un color de cualquier lugar de la pantalla.
Abre un selector de color que permite:
• Hacer clic en cualquier punto de la pantalla para muestrear un color
• Muestrear desde otras aplicaciones o imágenes
El color elegido se establecerá como color central.
Los rangos no cambian; ajústelos manualmente después de elegir el color.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="232"/>
        <source>Add to Custom Colors</source>
        <translation>Añadir a colores personalizados</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="235"/>
        <source>Save current color to Custom Colors palette.
Adds the current center color to the first empty slot in Custom Colors.
• Only saves the color, not the ranges
• Click saved colors to quickly reuse them
• Custom colors persist across sessions
Useful for building a palette of frequently used colors.</source>
        <translation>Guarda el color actual en la paleta Colores personalizados.
Añade el color central actual al primer espacio vacío de Colores personalizados.
• Solo guarda el color, no los rangos
• Haga clic en colores guardados para reutilizarlos rápidamente
• Los colores personalizados persisten entre sesiones
Útil para crear una paleta de colores usados con frecuencia.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="253"/>
        <source>Basic Colors:</source>
        <translation>Colores básicos:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="256"/>
        <source>Preset basic color palette.
Quick access to common colors like red, orange, yellow, green, cyan, blue, purple, and grayscale.
Click any color swatch to set it as the center color.</source>
        <translation>Paleta predefinida de colores básicos.
Acceso rápido a colores comunes como rojo, naranja, amarillo, verde, cian, azul, morado y escala de grises.
Haga clic en cualquier muestra para establecerla como color central.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="264"/>
        <source>Basic color swatches.
Click any color to quickly set it as your center color.
• Top row: Primary colors and tints
• Bottom row: Grayscale and darker shades
Useful for quickly selecting standard colors.</source>
        <translation>Muestras de colores básicos.
Haga clic en cualquier color para establecerlo rápidamente como color central.
• Fila superior: colores primarios y tintes
• Fila inferior: escala de grises y tonos más oscuros
Útil para seleccionar rápidamente colores estándar.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="274"/>
        <source>Custom Colors:</source>
        <translation>Colores personalizados:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="277"/>
        <source>Your saved custom color palette.
Colors you&apos;ve saved using &apos;Add to Custom Colors&apos; button.
Click any saved color to reuse it.</source>
        <translation>Paleta de colores personalizados guardados.
Colores guardados con el botón &apos;Añadir a colores personalizados&apos;.
Haga clic en cualquier color guardado para reutilizarlo.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="285"/>
        <source>Custom color swatches.
Click any color to set it as your center color.
• Empty slots shown as gray
• Use &apos;Add to Custom Colors&apos; button to save current color
• Custom colors persist across sessions
Build your own palette of frequently used colors.</source>
        <translation>Muestras de colores personalizados.
Haga clic en cualquier color para establecerlo como color central.
• Los espacios vacíos se muestran en gris
• Use el botón &apos;Añadir a colores personalizados&apos; para guardar el color actual
• Los colores personalizados persisten entre sesiones
Cree su propia paleta de colores usados con frecuencia.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="461"/>
        <source>Current HSV color range summary.
Shows the center color and detection ranges in real-time.
Warning indicators appear when ranges may cause detection issues.</source>
        <translation>Resumen del rango de color HSV actual.
Muestra el color central y los rangos de detección en tiempo real.
Aparecen indicadores de advertencia cuando los rangos pueden causar problemas de detección.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Center HSV:</source>
        <translation>HSV central:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Hue Range:</source>
        <translation>Rango de tono:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Sat Range:</source>
        <translation>Rango de sat.:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="470"/>
        <source>Val Range:</source>
        <translation>Rango de val.:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="472"/>
        <source>Current center HSV color values.
H = Hue (0-360°), S = Saturation (0-100%), V = Value/brightness (0-100%).</source>
        <translation>Valores HSV centrales actuales.
H = tono (0-360°), S = saturación (0-100%), V = valor/brillo (0-100%).</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="473"/>
        <source>Hue detection range (minus/plus from center).
Total range = minus + plus. Warning shown if total &gt; 60°.</source>
        <translation>Rango de detección de tono (menos/más desde el centro).
Rango total = menos + más. Se muestra una advertencia si el total &gt; 60°.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="474"/>
        <source>Saturation detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Rango de detección de saturación (menos/más desde el centro).
Se muestra una advertencia si el límite inferior &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="475"/>
        <source>Value detection range (minus/plus from center).
Warning shown if lower bound &lt; 25%.</source>
        <translation>Rango de detección de valor (menos/más desde el centro).
Se muestra una advertencia si el límite inferior &lt; 25%.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="497"/>
        <source>⚠ Too wide!</source>
        <translation>⚠ Demasiado amplio</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="502"/>
        <source>Hue range warning.
Your hue range is wider than 60° total.
Wide hue ranges may detect too many different colors.
Consider narrowing the range for more accurate detection.</source>
        <translation>Advertencia de rango de tono.
El rango de tono supera 60° en total.
Los rangos amplios pueden detectar demasiados colores distintos.
Considere reducir el rango para una detección más precisa.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="510"/>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="523"/>
        <source>⚠ Too low!</source>
        <translation>⚠ Demasiado bajo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="515"/>
        <source>Saturation range warning.
Your saturation lower bound is below 25%.
Low saturation includes grayish/washed out colors.
May detect unintended gray or desaturated colors.</source>
        <translation>Advertencia de rango de saturación.
El límite inferior de saturación está por debajo del 25%.
La saturación baja incluye colores grisáceos o apagados.
Puede detectar colores grises o desaturados no deseados.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/HSVColorRange/views/HSVRangePickerWidget.py" line="528"/>
        <source>Value range warning.
Your value lower bound is below 25%.
Low value includes very dark colors.
May detect shadows or dark unintended objects.</source>
        <translation>Advertencia de rango de valor.
El límite inferior de valor está por debajo del 25%.
Los valores bajos incluyen colores muy oscuros.
Puede detectar sombras u objetos oscuros no deseados.</translation>
    </message>
</context>
<context>
    <name>HeatmapViewerDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="34"/>
        <source>AOI Detection Heatmap</source>
        <translation>Mapa de calor de detecciones AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="59"/>
        <source>Threshold</source>
        <translation>Umbral</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="62"/>
        <source>Percentile:</source>
        <translation>Percentil:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="81"/>
        <source>Grid Resolution</source>
        <translation>Resolución de cuadrícula</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="86"/>
        <source>Low (100)</source>
        <translation>Baja (100)</translation>
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
        <translation>Las zonas calientes (en color) muestran áreas con alta densidad de detecciones. Las zonas grises están por debajo del umbral. Ajuste el umbral para controlar qué cuenta como zona caliente.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="126"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HeatmapViewerDialog.py" line="150"/>
        <source>No heatmap data available</source>
        <translation>No hay datos de mapa de calor disponibles</translation>
    </message>
</context>
<context>
    <name>HelpDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="25"/>
        <source>Viewer Help</source>
        <translation>Ayuda del visor</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/HelpDialog.py" line="60"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
</context>
<context>
    <name>ImageAdjustmentDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="83"/>
        <source>Image Adjustment</source>
        <translation>Ajuste de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="96"/>
        <source>Adjustments</source>
        <translation>Ajustes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="124"/>
        <source>Exposure:</source>
        <translation>Exposición:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="127"/>
        <source>Highlights:</source>
        <translation>Luces:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="130"/>
        <source>Shadows:</source>
        <translation>Sombras:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="133"/>
        <source>Clarity:</source>
        <translation>Nitidez:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="136"/>
        <source>Radius:</source>
        <translation>Radio:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="146"/>
        <source>Reset</source>
        <translation>Restablecer</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="147"/>
        <source>Apply</source>
        <translation>Aplicar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ImageAdjustmentDialog.py" line="148"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
</context>
<context>
    <name>ImageAnalysisGuide</name>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="14"/>
        <source>Image Analysis Guide</source>
        <translation>Guía de análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="39"/>
        <source>Welcome to ADIAT</source>
        <translation>Bienvenido a ADIAT</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="67"/>
        <source>Select a results file from a previous analysis: an ADIAT_Data.xml result, or a batch&apos;s Search Coordinator project (ADIAT_Search_*.xml).</source>
        <translation>Seleccione un archivo de resultados de un análisis anterior: un resultado ADIAT_Data.xml o un proyecto de revisión por lotes del Coordinador de búsqueda (ADIAT_Search_*.xml).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="79"/>
        <source>No file selected</source>
        <translation>Ningún archivo seleccionado</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="94"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="266"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="307"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="123"/>
        <source>What would you like to do?</source>
        <translation>¿Qué le gustaría hacer?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="160"/>
        <source>Start New Image Analysis</source>
        <translation>Iniciar nuevo análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="178"/>
        <source>Review Existing Image Analysis</source>
        <translation>Revisar análisis de imágenes existente</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="223"/>
        <source>Select Directories</source>
        <translation>Seleccionar directorios</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="245"/>
        <source>Where are the images you want to analyze?</source>
        <translation>¿Dónde están las imágenes que desea analizar?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="286"/>
        <source>Where do you want ADIAT to store the output files?</source>
        <translation>¿Dónde desea que ADIAT almacene los archivos de salida?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="348"/>
        <source>Image Capture Information</source>
        <translation>Información de captura de imagen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="370"/>
        <source>What drone/camera was used to capture images?</source>
        <translation>¿Qué dron/cámara se usó para capturar las imágenes?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="400"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>¿A qué altitud sobre el nivel del suelo (AGL) volaba el dron?</translation>
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
        <translation>Distancia de muestreo del suelo (GSD) estimada:</translation>
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
        <translation>Tamaño del objetivo de búsqueda</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="590"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>¿Aproximadamente qué tamaño tienen los objetos que desea identificar?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="621"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Más ejemplos:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 pie² – Sombrero, casco, bolsa de plástico &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 pies² – Gato, mochila pequeña &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 pies² – Mochila grande, perro mediano &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 pies² – Saco de dormir, perro grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 pies² – Barco pequeño, tienda de 2 personas &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 pies² – Coche/SUV, camioneta pequeña, tienda grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 pies² – Casa &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="660"/>
        <source>ALGORITHM SELECTION GUIDE</source>
        <translation>GUÍA DE SELECCIÓN DE ALGORITMO</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="682"/>
        <source>Are you using thermal images?</source>
        <translation>¿Está usando imágenes térmicas?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="727"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1114"/>
        <source>Yes</source>
        <translation>Sí</translation>
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
        <translation>Restablecer</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="147"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="888"/>
        <source>Algorithm Parameters</source>
        <translation>Parámetros del algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="918"/>
        <source>General Settings</source>
        <translation>Configuración general</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="940"/>
        <source>What color should be used to highlight Areas of Interest (AOIs)?</source>
        <translation>¿Qué color se debe usar para resaltar las áreas de interés (AOI)?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="960"/>
        <source>Select Color</source>
        <translation>Seleccionar color</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1009"/>
        <source>How many images should be processed at the same time?</source>
        <translation>¿Cuántas imágenes deben procesarse al mismo tiempo?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1033"/>
        <source>Run Benchmark</source>
        <translation>Ejecutar evaluación</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1056"/>
        <source>What resolution should images be processed at?</source>
        <translation>¿A qué resolución deben procesarse las imágenes?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1084"/>
        <source>Were the images captured in different lighting conditions?</source>
        <translation>¿Se capturaron las imágenes en diferentes condiciones de iluminación?</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1177"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1189"/>
        <source>Skip this wizard in the future</source>
        <translation>Omitir este asistente en el futuro</translation>
    </message>
    <message>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1217"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="261"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="266"/>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="272"/>
        <location filename="../resources/views/images/ImageAnalysisGuide.ui" line="1229"/>
        <source>Continue</source>
        <translation>Continuar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="102"/>
        <source>ADIAT Image Analysis Guide</source>
        <translation>Guía de análisis de imágenes ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="256"/>
        <source>Load Results</source>
        <translation>Cargar resultados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/ImageAnalysisGuide.py" line="269"/>
        <source>Start Processing</source>
        <translation>Iniciar procesamiento</translation>
    </message>
</context>
<context>
    <name>ImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="78"/>
        <source>Select Drone/Camera</source>
        <translation>Seleccionar dron/cámara</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="82"/>
        <source>No drones available</source>
        <translation>No hay drones disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="126"/>
        <source>Other</source>
        <translation>Otro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="162"/>
        <source>Error loading drone data</source>
        <translation>Error al cargar los datos del dron</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="240"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (datos de cámara no válidos)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="473"/>
        <source>{sensor_name}: Focal length not found in image EXIF</source>
        <translation>{sensor_name}: no se encontró la distancia focal en el EXIF de la imagen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="475"/>
        <source>{sensor_name}: Select input directory to extract focal length from images</source>
        <translation>{sensor_name}: seleccione el directorio de entrada para extraer la distancia focal de las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="482"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (faltan datos de cámara)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="483"/>
        <source>Unable to calculate GSD. Sensor dimensions found, but:</source>
        <translation>No se puede calcular el GSD. Se encontraron dimensiones del sensor, pero:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="484"/>
        <source>• Focal length is required (available from image EXIF data)</source>
        <translation>• Se requiere distancia focal (disponible en los datos EXIF de la imagen)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="485"/>
        <source>GSD calculation requires an actual image file to extract focal length.</source>
        <translation>El cálculo de GSD requiere un archivo de imagen real para extraer la distancia focal.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="491"/>
        <source>-- (Error)</source>
        <translation>-- (error)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="523"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ImageCapturePage.py" line="525"/>
        <source>Primary</source>
        <translation>Principal</translation>
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
        <translation>(Imagen {current} de {total})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/image/ImageLoadController.py" line="474"/>
        <source>Error Loading Image</source>
        <translation>Error al cargar la imagen</translation>
    </message>
</context>
<context>
    <name>InputProcessingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="31"/>
        <source>Processing Resolution</source>
        <translation>Resolución de procesamiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="36"/>
        <source>Resolution:</source>
        <translation>Resolución:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="41"/>
        <source>Original</source>
        <translation>Original</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="52"/>
        <source>Custom</source>
        <translation>Personalizada</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="61"/>
        <source>Select a preset resolution for processing. Lower resolutions are faster but less detailed.
&apos;Original&apos; uses the video&apos;s native resolution (no downsampling).
720P (1280x720) provides excellent balance between speed and detection accuracy.
Select &apos;Custom&apos; to manually set width and height.</source>
        <translation>Seleccione una resolución predefinida para el procesamiento. Las resoluciones más bajas son más rápidas, pero tienen menos detalle.
&apos;Original&apos; usa la resolución nativa del video (sin reducción de escala).
720P (1280x720) ofrece un equilibrio excelente entre velocidad y precisión de detección.
Seleccione &apos;Personalizada&apos; para definir manualmente el ancho y la altura.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="71"/>
        <source>Width:</source>
        <translation>Ancho:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="78"/>
        <source>Custom processing width in pixels (320-3840).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Ancho de procesamiento personalizado en píxeles (320-3840).
Solo se activa cuando se selecciona la resolución &apos;Personalizada&apos;.
Valores menores = procesamiento más rápido y menos detalle.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="84"/>
        <source>Height:</source>
        <translation>Altura:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="91"/>
        <source>Custom processing height in pixels (240-2160).
Only enabled when &apos;Custom&apos; resolution is selected.
Lower values = faster processing, less detail.</source>
        <translation>Altura de procesamiento personalizada en píxeles (240-2160).
Solo se activa cuando se selecciona la resolución &apos;Personalizada&apos;.
Valores menores = procesamiento más rápido y menos detalle.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="107"/>
        <source>Performance Options</source>
        <translation>Opciones de rendimiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="112"/>
        <source>Frame Rate:</source>
        <translation>Frecuencia de fotogramas:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="118"/>
        <source>Source FPS</source>
        <translation>FPS de origen</translation>
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
        <translation>Limita la frecuencia de fotogramas usada para el procesamiento.

• FPS de origen: sigue la cadencia del origen (las fuentes en vivo pueden aplicar un límite de seguridad)
• 30 FPS: buen equilibrio entre fluidez y rendimiento
• 25 FPS: estándar para video PAL
• 20 FPS: menor uso de CPU
• 15 FPS: uso de CPU más bajo
• 10 FPS: ahorro considerable de CPU
• 5 FPS: ahorro máximo de CPU; puede omitir objetos rápidos

Las frecuencias más bajas reducen el uso de CPU, pero pueden omitir objetos que se mueven rápido.
Las detecciones persisten entre fotogramas saltados para mantener la continuidad visual.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="148"/>
        <source>Render at Processing Resolution (faster for high-res)</source>
        <translation>Renderizar a resolución de procesamiento (más rápido en alta resolución)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/InputProcessingTab.py" line="151"/>
        <source>Renders detection overlays at processing resolution instead of original video resolution.
Significantly faster for high-resolution videos (1080p+) with minimal visual impact.
Example: Processing at 720p but video is 4K - renders at 720p then upscales.
Recommended: ON for high-res videos, OFF for native 720p or lower.</source>
        <translation>Renderiza las superposiciones de detección a la resolución de procesamiento en lugar de la resolución original del video.
Es mucho más rápido para videos de alta resolución (1080p+) con impacto visual mínimo.
Ejemplo: si se procesa a 720p pero el video es 4K, renderiza a 720p y luego amplía.
Recomendado: activado para videos de alta resolución; desactivado para 720p nativo o inferior.</translation>
    </message>
</context>
<context>
    <name>LoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="12"/>
        <source>Generating Report</source>
        <translation>Generando informe</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="29"/>
        <source>Report generation in progress...</source>
        <translation>Generación de informe en curso...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/LoadingDialog.py" line="33"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>MRMap</name>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
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
        <translation>Número de segmentos en los que dividir cada imagen para el análisis MR Map.
Cada segmento se procesa independientemente para la detección de características multirresolución.
Impacto en el rendimiento:
• Mayor número de segmentos: AUMENTA el tiempo de procesamiento (más segmentos a analizar)
• Menor número de segmentos: REDUCE el tiempo de procesamiento (menos segmentos a analizar)
• 1 segmento: Procesamiento más rápido (analiza toda la imagen de una vez)
Un mayor número de segmentos mejora la detección en imágenes con características variadas.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Segmentos de imagen:</translation>
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
        <translation>Seleccione el número de segmentos en los que dividir cada imagen.
• Opciones: 1, 2, 4, 6, 9, 16, 25, 36 segmentos
• Predeterminado: 1 (analizar toda la imagen como un segmento)
El algoritmo MR Map (Mapa de Multirresolución) analiza características a múltiples escalas:
• 1 segmento: Procesa toda la imagen (mejor para imágenes pequeñas o contenido uniforme)
• Más segmentos: Analiza regiones locales independientemente (mejor para imágenes grandes)
Un mayor número de segmentos mejora la detección en imágenes con características variadas a lo largo de la escena.
Recomendado: 4-9 segmentos para imágenes típicas de dron.</translation>
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
        <translation>Espacio de color:</translation>
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
        <translation>Seleccione el espacio de color para el análisis MR Map.
El algoritmo MR Map analiza características en distintas representaciones de color:
• LAB: Espacio de color perceptualmente uniforme (predeterminado, mejor para análisis de diferencias de color)
• RGB: Espacio de color rojo-verde-azul estándar (bueno para uso general)
• HSV: Espacio de color Tono-Saturación-Valor (mejor para la detección de características basada en color)
Diferentes espacios de color pueden mejorar la detección según el contenido de la imagen.
Recomendado: LAB para la mayoría de los casos, HSV para imágenes ricas en color.</translation>
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
        <translation>Tamaño de ventana para el análisis multirresolución.
Determina la escala espacial de las características a detectar.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="202"/>
        <source>Window Size:</source>
        <translation>Tamaño de ventana:</translation>
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
        <translation>Establezca el tamaño de la ventana para el análisis multirresolución.
• Rango: 1 a 10
• Predeterminado: 5
El algoritmo MR Map analiza características a múltiples escalas espaciales usando ventanas deslizantes:
• Valores más pequeños (1-3): Detectan detalles finos y características pequeñas
• Valores medios (4-6): Detección equilibrada (recomendado para la mayoría de los casos)
• Valores más grandes (7-10): Detectan características y patrones más grandes
El tamaño de la ventana afecta la resolución espacial de la detección de características.
Ventanas más grandes proporcionan más contexto pero pueden omitir objetos pequeños.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="254"/>
        <source>Detection threshold for MR Map feature detection.
Controls the sensitivity of feature detection across multiple resolutions.</source>
        <translation>Umbral de detección para la detección de características MR Map.
Controla la sensibilidad de la detección de características en múltiples resoluciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="258"/>
        <source>Threshold:</source>
        <translation>Umbral:</translation>
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
        <translation>Ajuste el umbral de detección para el algoritmo MR Map.
• Rango: 1 a 200
• Predeterminado: 100
• El deslizador está invertido: IZQUIERDA = umbral mayor, DERECHA = umbral menor
El algoritmo MR Map detecta características en múltiples resoluciones espaciales:
• Valores más bajos (1-50): Muy sensible, detecta muchas características (puede incluir ruido)
• Valores medios (51-150): Detección equilibrada (recomendado para la mayoría de los casos)
• Valores más altos (151-200): Menos sensible, solo detecta características prominentes
El umbral controla qué tan distintiva debe ser una característica para ser detectada.
Nota: El aspecto del deslizador está invertido: mueva a la izquierda para ser más estricto, a la derecha para ser más permisivo.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMap.ui" line="326"/>
        <source>Current threshold value for MR Map feature detection.
Displays the value selected on the threshold slider (1-200).
Lower values = more sensitive detection.</source>
        <translation>Valor de umbral actual para la detección de características MR Map.
Muestra el valor seleccionado en el deslizador de umbral (1-200).
Valores más bajos = detección más sensible.</translation>
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
        <translation>Expansión de detección (opcional)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="48"/>
        <source>Threshold Expansion</source>
        <translation>Expansión de umbral</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="50"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Cuando está habilitado, expandir cada AOI para incluir también los píxeles con recuentos de bin del histograma
por debajo de (umbral + {0}). Los píxeles dentro del rectángulo del clúster se añaden incondicionalmente;
los píxeles fuera se añaden si están conectados a través de otros píxeles que cumplan las condiciones.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="57"/>
        <source>Hue Expansion</source>
        <translation>Expansión de tono</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapController.py" line="59"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Cuando está habilitado, expandir cada AOI a través de los vecinos cuyo tono esté dentro de +/- {0}
(unidades OpenCV) del tono medio de los píxeles detectados originalmente.
Se excluyen los píxeles con saturación inferior al {1}% o valor inferior al {2}%.</translation>
    </message>
</context>
<context>
    <name>MRMapWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="21"/>
        <source>Do your images contain complex scenes with buildings, vehicles, or mixed manmade ground cover?</source>
        <translation>¿Sus imágenes contienen escenas complejas con edificios, vehículos o cobertura del suelo antropogénica mixta?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="41"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="56"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="92"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>¿Con qué agresividad debe ADIAT buscar anomalías?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MRMapWizard.ui" line="105"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: Un valor más alto encontrará más anomalías potenciales pero también puede aumentar los falsos positivos.</translation>
    </message>
</context>
<context>
    <name>MRMapWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="39"/>
        <source>Very 
Conservative</source>
        <translation>Muy 
conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="40"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="41"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="42"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="43"/>
        <source>Very 
Aggressive</source>
        <translation>Muy 
agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="60"/>
        <source>Detection Expansion (optional)</source>
        <translation>Expansión de detección (opcional)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="67"/>
        <source>Threshold Expansion</source>
        <translation>Expansión de umbral</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="69"/>
        <source>When enabled, expand each AOI to also include pixels with histogram bin-counts
below (threshold + {0}). Pixels inside the cluster rectangle are added unconditionally;
pixels outside are added if they are connected through other qualifying pixels.</source>
        <translation>Cuando está habilitado, expandir cada AOI para incluir también los píxeles con recuentos de bin del histograma
por debajo de (umbral + {0}). Los píxeles dentro del rectángulo del clúster se añaden incondicionalmente;
los píxeles fuera se añaden si están conectados a través de otros píxeles que cumplan las condiciones.</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="76"/>
        <source>Hue Expansion</source>
        <translation>Expansión de tono</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MRMap/controllers/MRMapWizardController.py" line="78"/>
        <source>When enabled, expand each AOI through neighbors whose hue is within +/- {0}
(OpenCV units) of the mean hue of the original detected pixels.
Pixels with saturation below {1}% or value below {2}% are excluded.</source>
        <translation>Cuando está habilitado, expandir cada AOI a través de los vecinos cuyo tono esté dentro de +/- {0}
(unidades OpenCV) del tono medio de los píxeles detectados originalmente.
Se excluyen los píxeles con saturación inferior al {1}% o valor inferior al {2}%.</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="22"/>
        <source>Automated Drone Image Analysis Tool  v1.2 - Sponsored by TEXSAR</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron v1.2 - Patrocinado por TEXSAR</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="52"/>
        <source>Browse for the output folder to save analysis results.
Opens a folder selection dialog.
Choose an empty folder or create a new one to avoid overwriting existing files.</source>
        <translation>Buscar la carpeta de salida para guardar los resultados del análisis.
Abre un diálogo de selección de carpeta.
Elija una carpeta vacía o cree una nueva para evitar sobrescribir archivos existentes.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="57"/>
        <location filename="../resources/views/images/MainWindow.ui" line="133"/>
        <location filename="../resources/views/images/MainWindow.ui" line="597"/>
        <source> Select</source>
        <translation> Seleccionar</translation>
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
        <translation>Ruta a la carpeta de salida para guardar los resultados del análisis.
Haga clic en el botón Seleccionar para buscar una carpeta de destino.
Los resultados incluyen:
• Imágenes procesadas con los objetos detectados marcados
• Archivo CSV con coordenadas y metadatos de detección
• Archivo KML para ver los resultados en aplicaciones de mapas
• Archivos de salida adicionales específicos del algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="97"/>
        <source>Select the folder containing images to analyze.
Supported formats: JPG, PNG, TIFF, and other common image formats.</source>
        <translation>Seleccione la carpeta que contiene las imágenes a analizar.
Formatos compatibles: JPG, PNG, TIFF y otros formatos de imagen comunes.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="101"/>
        <source>Input Folder:</source>
        <translation>Carpeta de entrada:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="113"/>
        <source>Select the destination folder for analysis results.
Output includes processed images with marked detections and CSV data files.</source>
        <translation>Seleccione la carpeta de destino para los resultados del análisis.
La salida incluye imágenes procesadas con detecciones marcadas y archivos de datos CSV.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="117"/>
        <source>Output Folder:</source>
        <translation>Carpeta de salida:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="129"/>
        <source>Browse for the input folder containing images to analyze.
Opens a folder selection dialog.</source>
        <translation>Buscar la carpeta de entrada que contiene las imágenes a analizar.
Abre un diálogo de selección de carpeta.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="152"/>
        <source>Path to the input folder containing images for analysis.
Click the Select button to browse for a folder.
All supported image files in this folder will be processed.</source>
        <translation>Ruta a la carpeta de entrada que contiene las imágenes para el análisis.
Haga clic en el botón Seleccionar para buscar una carpeta.
Todos los archivos de imagen compatibles en esta carpeta se procesarán.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="209"/>
        <source>Minimum object size in pixels for detection filtering.
Objects smaller than this will be ignored.</source>
        <translation>Tamaño mínimo del objeto en píxeles para el filtrado de detecciones.
Los objetos más pequeños que esto se ignorarán.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="213"/>
        <source>Min Object Area (px):</source>
        <translation>Área mín. del objeto (px):</translation>
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
        <translation>Establezca el área mínima del objeto en píxeles para el filtrado de detecciones.
• Rango: 1 a 999 píxeles
• Predeterminado: 10 píxeles
Los objetos menores que este umbral serán filtrados y no detectados.
• Valores más bajos: Detecta objetos más pequeños (puede aumentar los falsos positivos)
• Valores más altos: Solo detecta objetos más grandes (reduce el ruido)
Úselo para filtrar pequeños artefactos y ruido en los resultados de detección.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="269"/>
        <source>Maximum object size in pixels for detection filtering.
Objects larger than this will be ignored.</source>
        <translation>Tamaño máximo del objeto en píxeles para el filtrado de detecciones.
Los objetos más grandes que esto se ignorarán.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="273"/>
        <source>Max Object Area (px):</source>
        <translation>Área máx. del objeto (px):</translation>
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
        <translation>Establezca el área máxima del objeto en píxeles para el filtrado de detecciones.
• Rango: 0 a 99999 píxeles
• Predeterminado: 0 (Ninguno - sin filtro máximo aplicado)
• Valor especial: 0 se muestra como &quot;Ninguno&quot;
Los objetos mayores que este umbral serán filtrados y no detectados.
• Valores más bajos: Solo detecta objetos más pequeños
• Valores más altos: Permite la detección de objetos más grandes
• Establezca a 0 (Ninguno): Sin filtrado de tamaño máximo
Úselo para excluir detecciones muy grandes de falsos positivos como sombras o rasgos del terreno.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="299"/>
        <source>None</source>
        <translation>Ninguno</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="323"/>
        <source>Disable the maximum size filter and allow detections of any size.</source>
        <translation>Desactivar el filtro de tamaño máximo y permitir detecciones de cualquier tamaño.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="326"/>
        <source>No max limit</source>
        <translation>Sin límite máximo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="359"/>
        <source>Color used to mark and identify detected objects in output images.
Click the color button to select a different color.</source>
        <translation>Color usado para marcar e identificar los objetos detectados en las imágenes de salida.
Haga clic en el botón de color para seleccionar uno diferente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="363"/>
        <source>Object Identifer Color:</source>
        <translation>Color del identificador de objeto:</translation>
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
        <translation>Seleccione el color usado para marcar los objetos detectados en las imágenes de salida.
• Predeterminado: Verde (RGB: 0, 255, 0)
Haga clic para abrir un diálogo de selector de color y elegir un color de marcador diferente.
El color seleccionado se usará para:
• Dibujar círculos/rectángulos alrededor de los objetos detectados
• Resaltar las ubicaciones de AOI en las imágenes de salida
• Crear marcadores visuales en el visor de resultados
Elija un color que contraste bien con el contenido de su imagen para una mejor visibilidad.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="395"/>
        <source>Maximum number of parallel processes to use for image analysis.
More processes = faster processing but higher CPU/memory usage.</source>
        <translation>Número máximo de procesos paralelos a usar para el análisis de imágenes.
Más procesos = procesamiento más rápido pero mayor uso de CPU/memoria.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="399"/>
        <source>Max Processes: </source>
        <translation>Procesos máx.: </translation>
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
        <translation>Establezca el número máximo de procesos paralelos para el análisis de imágenes.
• Rango: 1 a 20 procesos
• Predeterminado: 10 procesos
La aplicación usa multiprocesamiento para analizar varias imágenes simultáneamente:
• Valores más altos: Procesamiento más rápido (usa más núcleos de CPU y memoria)
• Valores más bajos: Procesamiento más lento (usa menos recursos del sistema)
• Recomendado: Establezca al número de núcleos de CPU o ligeramente más
• Para sistemas con RAM limitada, reduzca este valor para evitar problemas de memoria
Cada proceso analiza una imagen a la vez, por lo que más procesos = más procesamiento paralelo de imágenes.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="446"/>
        <source>Resolution at which images are processed.
Lower resolutions = faster processing but may miss small objects.</source>
        <translation>Resolución a la que se procesan las imágenes.
Resoluciones más bajas = procesamiento más rápido pero pueden omitir objetos pequeños.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="450"/>
        <source>Processing Resolution:</source>
        <translation>Resolución de procesamiento:</translation>
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
        <translation>Seleccione la resolución de procesamiento como porcentaje del tamaño de la imagen original:
• 100%: Resolución original (sin escalar, máxima calidad, más lento)
• 75%: Alta calidad (~56% de los píxeles, ~1,8x más rápido)
• 50%: Calidad equilibrada (25% de los píxeles, ~4x más rápido) - RECOMENDADO
• 33%: Procesamiento rápido (~11% de los píxeles, ~9x más rápido)
• 25%: Muy rápido (6% de los píxeles, ~16x más rápido)
• 10%: Ultra rápido (1% de los píxeles, ~100x más rápido)

El escalado porcentual conserva la relación de aspecto original.
Funciona con cualquier tamaño, orientación o relación de aspecto de imagen.

Los valores de área mín./máx. se especifican siempre en la resolución original.
Todos los resultados se devuelven en coordenadas de la resolución original.</translation>
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
        <translation>Habilitar el preprocesamiento de normalización de histograma en las imágenes antes de la detección.
La normalización de histograma ajusta los colores de la imagen para que coincidan con una imagen de referencia:
• Iguala las diferencias de iluminación y color entre imágenes
• Corrige ángulos solares variables, sombras y condiciones atmosféricas
• Estandariza la apariencia de color en el conjunto de imágenes
• Mejora la coherencia de los resultados de detección
Cuando esté habilitado, seleccione una imagen de referencia con condiciones ideales de iluminación/color.
Útil al procesar imágenes tomadas en distintos momentos o bajo condiciones variables.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="540"/>
        <source>Normalize Histograms</source>
        <translation>Normalizar histogramas</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="555"/>
        <source>Select the reference image for histogram normalization.
All images will be adjusted to match this image&apos;s color distribution.</source>
        <translation>Seleccione la imagen de referencia para la normalización del histograma.
Todas las imágenes se ajustarán para coincidir con la distribución de color de esta imagen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="559"/>
        <source>Reference Image:</source>
        <translation>Imagen de referencia:</translation>
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
        <translation>Ruta a la imagen de referencia para la normalización del histograma.
Haga clic en el botón Seleccionar para elegir una imagen.
Elija una imagen con condiciones ideales de iluminación y color:
• Imagen clara y bien iluminada de su conjunto de datos
• Representativa de la apariencia deseada
• Condiciones de iluminación típicas para su misión
Todas las demás imágenes se ajustarán en color para coincidir con esta referencia.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="592"/>
        <source>Browse for a reference image for histogram normalization.
Opens an image file selection dialog.
Select a representative image with good lighting and typical color conditions.</source>
        <translation>Buscar una imagen de referencia para la normalización del histograma.
Abre un diálogo de selección de archivo de imagen.
Seleccione una imagen representativa con buena iluminación y condiciones de color típicas.</translation>
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
        <translation>Seleccione el algoritmo de detección a usar para el análisis de imágenes.

Cada algoritmo tiene fortalezas y casos de uso específicos:

• Rango de color HSV: Mejor para detectar objetos coloreados específicos
• Rango de color (RGB): Detección alternativa de color usando el espacio de color RGB
• Anomalía RX: Detección estadística de objetos inusuales/anómalos
• Anomalía térmica: Detecta anomalías de temperatura en imágenes térmicas
• Rango térmico: Detección basada en temperatura en imágenes térmicas
• Filtro adaptado: Detección basada en objetivo usando coincidencia espectral
• MR Map: Detección de características multirresolución a varias escalas
• Detector de personas con IA: Aprendizaje automático para detectar personas

Pase el cursor sobre el menú desplegable de algoritmo para obtener descripciones detalladas de cada uno.</translation>
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
        <translation>Seleccione el algoritmo de detección para su tarea de análisis de imágenes.
Cada algoritmo tiene fortalezas únicas y casos de uso óptimos:

═══════════════════════════════════════════════════
RANGO DE COLOR HSV
═══════════════════════════════════════════════════
Qué hace: Detecta objetos por rangos de color específicos usando el espacio de color HSV
Fortalezas:
• Mejor para detectar objetos de colores brillantes (ropa naranja, amarilla, roja)
• Robusto ante variaciones de iluminación (HSV separa color del brillo)
• Altamente personalizable con rangos por canal
• Herramientas interactivas de selección de color disponibles
Debilidades:
• Requiere ajuste cuidadoso del rango de color para resultados óptimos
• Puede tener dificultades con variaciones de color en sombras
• No es efectivo para objetos incoloros o camuflados
Mejor para: Búsqueda y rescate (ropa, equipamiento de colores), vehículos coloreados, tiendas, lonas de colores

═══════════════════════════════════════════════════
RANGO DE COLOR (RGB)
═══════════════════════════════════════════════════
Qué hace: Detecta objetos por rangos de color RGB
Fortalezas:
• Especificación de color RGB simple e intuitiva
• Velocidad de procesamiento rápida
• Bueno para detección básica basada en color
Debilidades:
• Más sensible a los cambios de iluminación que HSV
• Los canales RGB mezclan información de color y brillo
• Menos flexible que HSV para variaciones de color complejas
Mejor para: Situaciones de iluminación controlada, detección rápida básica de color, escenarios simples

═══════════════════════════════════════════════════
ANOMALÍA RX
═══════════════════════════════════════════════════
Qué hace: Detección estadística de anomalías - encuentra píxeles inusuales comparados con el fondo
Fortalezas:
• Detecta objetos que no coinciden con el fondo (no se necesita muestra del objetivo)
• Excelente para encontrar objetos camuflados o parcialmente ocultos
• Funciona con todos los tipos de imagen (RGB, térmica, multiespectral)
• Se adapta automáticamente a las características de la escena
• Bueno para detectar diferencias sutiles
Debilidades:
• Puede detectar anomalías naturales (rocas, cambios de vegetación)
• Requiere ajustar la sensibilidad para equilibrar detección vs. falsos positivos
• Mayor número de segmentos aumenta significativamente el tiempo de procesamiento
• Menos efectivo en fondos muy variados/desordenados
Mejor para: Búsqueda de personas desaparecidas (humanos entre vegetación), objetos camuflados, objetivos desconocidos, cualquier cosa inusual en la escena

═══════════════════════════════════════════════════
ANOMALÍA TÉRMICA
═══════════════════════════════════════════════════
Qué hace: Detecta anomalías de temperatura en imágenes térmicas (puntos calientes/fríos)
Fortalezas:
• Encuentra valores atípicos de temperatura automáticamente (no se necesita temp. específica)
• Excelente para detectar fuentes de calor (personas, animales, fuegos)
• Funciona de día o noche con cámaras térmicas
• Detecta a través de vegetación ligera
• Ajustable para anomalías calientes, frías o ambas
Debilidades:
• Requiere imágenes térmicas (FLIR)
• Puede detectar objetos calentados por el sol (rocas, vehículos)
• Los gradientes de temperatura pueden causar falsos positivos
• Afectado por la temperatura ambiente y el clima
Mejor para: Búsquedas nocturnas, detección de personas/animales por calor corporal, búsqueda de fuentes de calor, detección de puntos fríos

═══════════════════════════════════════════════════
RANGO TÉRMICO
═══════════════════════════════════════════════════
Qué hace: Detección basada en temperatura dentro de un rango de temperatura específico
Fortalezas:
• Detección precisa basada en temperatura
• Excelente para encontrar humanos (temp. corporal ~35-40°C / 95-104°F)
• Filtra eficazmente temperaturas no objetivo
• Funciona de día o noche con cámaras térmicas
• Muy fiable cuando se conoce la temperatura objetivo
Debilidades:
• Requiere imágenes térmicas (FLIR) con datos de temperatura
• Debe conocer el rango de temperatura objetivo de antemano
• Las condiciones ambientales afectan la temperatura objetivo
• Puede omitir objetivos en clima extremo (casos de hipotermia)
Mejor para: Detección de humanos (temp. corporal conocida), objetivos de temperatura específica, detección de incendios (rango de alta temp.)

═══════════════════════════════════════════════════
FILTRO ADAPTADO
═══════════════════════════════════════════════════
Qué hace: Detección basada en objetivo usando coincidencia de firma espectral
Fortalezas:
• Muy precisa cuando se tiene una muestra del objetivo
• Usa la &quot;firma&quot; espectral/de color del objetivo para la coincidencia
• Reduce los falsos positivos al coincidir con las características conocidas del objetivo
• Bueno para detectar tipos de objetos específicos
Debilidades:
• Requiere una imagen de referencia o muestra de color del objetivo
• Menos efectiva si la apariencia del objetivo varía significativamente
• Las diferencias de iluminación pueden afectar la precisión de la coincidencia
• No es adecuada para objetivos desconocidos
Mejor para: Encontrar objetos conocidos específicos (color de vehículo específico, ropa específica), cuando se tiene una muestra del objetivo para coincidir

═══════════════════════════════════════════════════
MR MAP (Mapa de Multirresolución)
═══════════════════════════════════════════════════
Qué hace: Detección de características en multirresolución a varias escalas espaciales
Fortalezas:
• Detecta características en múltiples escalas simultáneamente
• Bueno para encontrar objetos de tamaños variados
• Efectivo para análisis de escenas complejas
• Puede detectar características grandes y pequeñas en una pasada
Debilidades:
• Más intensivo computacionalmente
• Requiere ajuste cuidadoso de parámetros
• Mayor número de segmentos aumenta significativamente el tiempo de procesamiento
• Puede producir más falsos positivos que requieran filtrado
Mejor para: Escenas complejas con tamaños de objeto variados, cuando el tamaño del objetivo es desconocido, mapeo general de características

═══════════════════════════════════════════════════
DETECTOR DE PERSONAS CON IA
═══════════════════════════════════════════════════
Qué hace: Modelo de IA de aprendizaje profundo entrenado específicamente para detectar personas
Fortalezas:
• Extremadamente preciso para detectar personas en diversas poses
• Funciona con visibilidad parcial y ropa variada
• Sin requisitos de color/temperatura - funciona con imágenes RGB normales
• Entrenado con millones de imágenes para una detección robusta
• Detecta personas en fondos complejos
• Se necesita un ajuste mínimo de parámetros
Debilidades:
• Solo detecta personas (no vehículos, equipamiento, etc.)
• Intensivo computacionalmente - procesamiento más lento
• Requiere resolución de imagen adecuada
• Puede tener dificultades con personas muy distantes/pequeñas
• Menos efectivo con oclusión severa
Mejor para: Operaciones de Búsqueda y Rescate (personas desaparecidas), conteo de personas, situaciones donde solo se necesita detección humana

═══════════════════════════════════════════════════
GUÍA DE SELECCIÓN DE ALGORITMO
═══════════════════════════════════════════════════
• Para objetos coloridos (ropa brillante, equipo): Rango de color HSV
• Para cámaras térmicas buscando personas: Rango térmico o Anomalía térmica
• Para sujetos camuflados u ocultos: Anomalía RX
• Para detectar personas específicamente: Detector de personas con IA
• Cuando tenga una muestra del objetivo: Filtro adaptado
• Para objetivos desconocidos que destacan: Anomalía RX o Anomalía térmica
• Para el procesamiento más rápido: Rango de color (RGB) o Rango de color HSV
• Para la detección de personas más precisa: Detector de personas con IA</translation>
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
        <translation>Iniciar el procesamiento de imágenes con el algoritmo seleccionado.
Requisitos antes de iniciar:
• Se debe seleccionar la carpeta de entrada con imágenes válidas
• Se debe seleccionar la carpeta de salida
• Se debe seleccionar el algoritmo
• Deben configurarse todos los parámetros del algoritmo requeridos
El procesamiento:
• Analizará todas las imágenes en la carpeta de entrada usando el algoritmo seleccionado
• Aplicará los filtros globales (área mín./máx., K-Means, normalización de histograma)
• Guardará los resultados en la carpeta de salida (imágenes marcadas, archivos CSV, KML)
• Mostrará el progreso y los resultados en la ventana de salida
Haga clic en Cancelar durante el procesamiento para detener el análisis.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="918"/>
        <source>Start</source>
        <translation>Iniciar</translation>
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
        <translation>Cancelar el proceso de análisis de imágenes en ejecución.
Detiene el procesamiento inmediatamente y termina de forma segura todos los procesos de trabajo.
Efectos de la cancelación:
• Se detienen todos los procesos de análisis en ejecución
• Los resultados parciales se guardan hasta el punto de cancelación
• Las imágenes ya procesadas tendrán archivos de salida en la carpeta de salida
• El procesamiento puede reiniciarse tras la cancelación
• Vuelve al estado listo
Úselo cuando necesite detener el procesamiento para ajustar la configuración o solucionar problemas.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="963"/>
        <source> Cancel</source>
        <translation> Cancelar</translation>
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
        <translation>Abrir el Visor de resultados para revisar los resultados de detección.
Disponible después de que el procesamiento finalice correctamente.
El Visor de resultados ofrece:
• Exploración interactiva de imágenes con los objetos detectados resaltados
• Comparación lado a lado de imágenes originales y procesadas
• Navegación por todas las imágenes procesadas
• Detalles y metadatos de AOI (Área de interés)
• Coordenadas GPS de los objetos detectados
• Opciones de exportación para las detecciones seleccionadas
• Capacidades de zoom y desplazamiento
• Filtrado y ordenación de resultados de detección
Úselo para revisar, verificar y exportar los resultados del análisis.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1744"/>
        <location filename="../resources/views/images/MainWindow.ui" line="1018"/>
        <source> View Results</source>
        <translation> Ver resultados</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1028"/>
        <source>search</source>
        <translation>búsqueda</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1085"/>
        <source>Menu</source>
        <translation>Menú</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1098"/>
        <source>Help</source>
        <translation>Ayuda</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1111"/>
        <source>Image Analysis Wizard</source>
        <translation>Asistente de análisis de imágenes</translation>
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
        <translation>Iniciar el asistente de la Guía de análisis de imágenes para configurar los ajustes del análisis.
Abre un asistente paso a paso para:
• Seleccionar directorios de entrada y salida
• Configurar los ajustes de captura de imagen (dron, altitud, GSD)
• Establecer el tamaño del objeto objetivo
• Elegir el algoritmo de detección
• Configurar los parámetros específicos del algoritmo
• Establecer las opciones generales de procesamiento
El asistente cerrará esta ventana y se abrirá con todos los ajustes rellenados previamente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1132"/>
        <source>Load Results File</source>
        <translation>Cargar archivo de resultados</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1135"/>
        <source>Load a previously saved results file for viewing.
Opens a file dialog to select a results file (.pkl format).
Loads the analysis results and opens the Results Viewer.
Use this to review results from previous analysis sessions without reprocessing.</source>
        <translation>Cargar un archivo de resultados guardado previamente para visualizarlo.
Abre un diálogo de archivo para seleccionar un archivo de resultados (formato .pkl).
Carga los resultados del análisis y abre el Visor de resultados.
Úselo para revisar resultados de sesiones de análisis anteriores sin reprocesar.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1148"/>
        <source>Load Results Folder</source>
        <translation>Cargar carpeta de resultados</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1151"/>
        <source>Scan a folder recursively for ADIAT_DATA.XML files.
Displays all found results in a dialog for easy browsing.
Use this to quickly find and open results from multiple analysis sessions.</source>
        <translation>Escanear una carpeta recursivamente en busca de archivos ADIAT_DATA.XML.
Muestra todos los resultados encontrados en un diálogo para facilitar la exploración.
Úselo para encontrar y abrir rápidamente resultados de múltiples sesiones de análisis.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1163"/>
        <source>Preferences</source>
        <translation>Preferencias</translation>
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
        <translation>Abrir el diálogo de Preferencias para configurar los ajustes de la aplicación.
Ajustar la configuración global incluyendo:
• Tema de la aplicación (Claro/Oscuro)
• Umbral de advertencia de AOI máximos
• Radio del círculo de AOI para agrupación
• Formato del sistema de coordenadas (Lat/Lon, UTM)
• Unidad de temperatura (Fahrenheit/Celsius)
• Unidad de distancia (Metros/Pies)
• Archivo de configuración del sensor del dron
Todos los cambios se guardan automáticamente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1185"/>
        <source>Video Parser</source>
        <translation>Analizador de vídeo</translation>
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
        <translation>Abrir la utilidad Analizador de vídeo para extraer fotogramas de archivos de vídeo.
Convertir el metraje de vídeo en imágenes de fotogramas individuales para el análisis.
Características:
• Extraer fotogramas a intervalos de tiempo especificados
• Soporte opcional para archivos SRT para metadatos GPS
• Compatible con formatos de vídeo comunes (MP4, AVI, MOV, etc.)
• Incrusta datos de ubicación en los fotogramas extraídos
Úselo para preparar metraje de vídeo para análisis basado en imágenes.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1205"/>
        <source>Streaming Detector</source>
        <translation>Detector de transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1208"/>
        <source>Switch to the Streaming Detector</source>
        <translation>Cambiar al Detector de transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1218"/>
        <source>Flight Viewer</source>
        <translation>Visor de vuelo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1221"/>
        <source>Open the Flight Viewer to pair with ADIAT Mobile drone controllers and watch their live feeds.</source>
        <translation>Abra el visor de vuelo para emparejar controladores de dron de ADIAT Mobile y ver sus transmisiones en vivo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1231"/>
        <source>Real-Time Anomaly Detection</source>
        <translation>Detección de anomalías en tiempo real</translation>
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
        <translation>Abrir la ventana de Detección de anomalías en tiempo real para un análisis en vivo avanzado.
Combina múltiples algoritmos de detección para una detección integral de anomalías en tiempo real.
Características:
• Detección de movimiento con sustracción de fondo
• Detección de anomalías por cuantización de color
• Procesamiento avanzado de vídeo en transmisión
• Fusión de detección y filtrado temporal
• Optimización del rendimiento en tiempo real
• Procesamiento multihilo para mejor rendimiento
• Mayor precisión de detección mediante la combinación de algoritmos
Diseñado para detectar objetos, movimiento y colores inusuales en transmisiones de vídeo en tiempo real.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1254"/>
        <source>Search Coordinator</source>
        <translation>Coordinador de búsqueda</translation>
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
        <translation>Abrir la ventana del Coordinador de búsqueda para administrar proyectos de revisión de múltiples lotes.
Características:
• Crear y administrar proyectos de búsqueda con múltiples lotes
• Rastrear el progreso de los revisores a través de múltiples conjuntos de imágenes
• Consolidar los resultados de revisión de varios revisores
• Ver un panel con el estado y las métricas de la búsqueda
• Exportar resultados consolidados
• Gestionar asignaciones de lotes y coordinación de revisores
Ideal para búsquedas a gran escala con múltiples revisores y lotes de imágenes.</translation>
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
        <translation>Abrir la documentación de ayuda en línea en su navegador web.
Acceda a documentación completa, tutoriales y guías de usuario.
Proporciona información detallada sobre todas las funciones y algoritmos.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1293"/>
        <source>Check for Updates</source>
        <translation>Buscar actualizaciones</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1296"/>
        <source>Check the update feed for a newer ADIAT installer.
If an update is available, you can download and launch the installer from here.</source>
        <translation>Consulte la fuente de actualizaciones para un instalador de ADIAT más reciente.
Si hay una actualización disponible, puede descargar e iniciar el instalador desde aquí.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1307"/>
        <source>Community Forum</source>
        <translation>Foro de la comunidad</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1310"/>
        <source>Join the community Discord server for support and discussions.
Connect with other users, share experiences, and get help.
Ask questions, report issues, and suggest new features.</source>
        <translation>Únase al servidor de Discord de la comunidad para obtener soporte y participar en discusiones.
Conéctese con otros usuarios, comparta experiencias y obtenga ayuda.
Haga preguntas, reporte problemas y sugiera nuevas funciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/MainWindow.ui" line="1322"/>
        <source>YouTube Channel</source>
        <translation>Canal de YouTube</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="89"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron v{version} - Patrocinado por TEXSAR</translation>
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
        <translation>Seleccione el algoritmo de detección para su tarea de análisis de imágenes:

RANGO DE COLOR HSV: Detecta objetos de colores brillantes (ropa, vehículos, tiendas)
  • Mejor para: Objetos coloreados en condiciones de iluminación variables
  • Limitación: Requiere ajuste de color, no para objetos camuflados

RANGO DE COLOR (RGB): Detección simple de color RGB, procesamiento rápido
  • Mejor para: Detección básica de color en iluminación controlada
  • Limitación: Sensible a los cambios de iluminación

ANOMALÍA RX: Encuentra objetos que no coinciden con el fondo (no se necesita muestra)
  • Mejor para: Sujetos camuflados/ocultos, objetivos desconocidos
  • Limitación: Puede detectar anomalías naturales, más lento con más segmentos

ANOMALÍA TÉRMICA: Detecta puntos calientes/fríos en imágenes térmicas
  • Mejor para: Búsquedas nocturnas, detección de personas/animales por calor corporal
  • Limitación: Requiere cámara térmica, puede detectar objetos calentados por el sol

ANOMALÍA RESIDUAL DE TEMPERATURA: Detecta valores atípicos delta-T locales usando residuos radiométricos
  • Mejor para: Aislar firmas térmicas calientes/frías raras en fondos mixtos
  • Limitación: Requiere datos térmicos radiométricos, puede ser sensible a la elección del umbral

RANGO TÉRMICO: Detección basada en temperatura (p. ej., 35-40°C para humanos)
  • Mejor para: Detección de humanos con cámara térmica (temp. corporal conocida)
  • Limitación: Requiere cámara térmica, debe conocer la temperatura objetivo

FILTRO ADAPTADO: Coincide objetivos usando la firma de color de una muestra
  • Mejor para: Objetos conocidos específicos cuando se tiene una muestra del objetivo
  • Limitación: Requiere imagen de referencia, no para objetivos desconocidos

MR MAP: Detección multirresolución para objetos de tamaños variados
  • Mejor para: Escenas complejas con tamaños de objetivo desconocidos
  • Limitación: Procesamiento más lento, más falsos positivos

DETECTOR DE PERSONAS CON IA: Modelo de aprendizaje profundo para detección precisa de personas
  • Mejor para: Búsqueda y rescate, encontrar personas en cualquier ropa/pose
  • Limitación: Solo detecta personas, procesamiento más lento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="384"/>
        <source>Select AOI Highlight Color</source>
        <translation>Seleccionar color de resaltado del AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="398"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="416"/>
        <source>Select Directory</source>
        <translation>Seleccionar directorio</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="433"/>
        <source>Select a Reference Image</source>
        <translation>Seleccionar una imagen de referencia</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="435"/>
        <source>Images (*.png *.jpg)</source>
        <translation>Imágenes (*.png *.jpg)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="496"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="528"/>
        <source>Value Adjusted</source>
        <translation>Valor ajustado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="498"/>
        <source>Maximum area has been adjusted to {value} pixels to maintain valid range.
(Minimum area must be less than maximum area)</source>
        <translation>El área máxima se ha ajustado a {value} píxeles para mantener un rango válido.
(El área mínima debe ser menor que el área máxima)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="530"/>
        <source>Minimum area has been adjusted to {value} pixels to maintain valid range.
(Maximum area must be greater than minimum area)</source>
        <translation>El área mínima se ha ajustado a {value} píxeles para mantener un rango válido.
(El área máxima debe ser mayor que el área mínima)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="644"/>
        <source>Please set the input and output directories.</source>
        <translation>Establezca los directorios de entrada y salida.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="651"/>
        <source>--- Starting image processing ---</source>
        <translation>--- Iniciando procesamiento de imágenes ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="847"/>
        <source>Could not parse XML file. Check file paths in &quot;{file_name}&quot;</source>
        <translation>No se pudo analizar el archivo XML. Compruebe las rutas de archivo en &quot;{file_name}&quot;</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="870"/>
        <source>Area of Interest Limit ({limit}) exceeded. Continue?</source>
        <translation>Se ha superado el límite de áreas de interés ({limit}). ¿Continuar?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="873"/>
        <source>Area of Interest Limit Exceeded</source>
        <translation>Límite de áreas de interés superado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="925"/>
        <source>--- Image Processing Completed ---</source>
        <translation>--- Procesamiento de imágenes completado ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="926"/>
        <source>Image processing complete</source>
        <translation>Procesamiento de imágenes completado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="929"/>
        <source>{count} images with areas of interest identified</source>
        <translation>{count} imágenes con áreas de interés identificadas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="935"/>
        <source>No areas of interest identified</source>
        <translation>No se identificaron áreas de interés</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1019"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1561"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1584"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1614"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1630"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1646"/>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1662"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1039"/>
        <source>Open Recent Results</source>
        <translation>Abrir resultados recientes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1083"/>
        <source>(no results opened yet)</source>
        <translation>(aún no se ha abierto ningún resultado)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1099"/>
        <source>This results file no longer exists:
{path}</source>
        <translation>Este archivo de resultados ya no existe:
{path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1116"/>
        <source>Select File</source>
        <translation>Seleccionar archivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>Archivos XML (*.xml);;Todos los archivos (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1137"/>
        <source>Select Results Folder</source>
        <translation>Seleccionar carpeta de resultados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1170"/>
        <source>Failed to scan folder: {error}</source>
        <translation>Error al escanear la carpeta: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1192"/>
        <source>No Results Found</source>
        <translation>No se encontraron resultados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1193"/>
        <source>No ADIAT_DATA.XML files were found in the selected folder.</source>
        <translation>No se encontraron archivos ADIAT_DATA.XML en la carpeta seleccionada.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1210"/>
        <source>Failed to display results: {error}</source>
        <translation>Error al mostrar los resultados: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1221"/>
        <source>Scan failed: {error}</source>
        <translation>Error en el escaneo: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1264"/>
        <source>Failed to open viewer: {error}</source>
        <translation>Error al abrir el visor: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1295"/>
        <source>The selected file is not a valid XML file: {path}</source>
        <translation>El archivo seleccionado no es un archivo XML válido: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1507"/>
        <source>Error Loading Results</source>
        <translation>Error al cargar los resultados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1508"/>
        <source>Failed to load results file:
{error}</source>
        <translation>Error al cargar el archivo de resultados:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1562"/>
        <source>Failed to open Streaming Detector:
{error}</source>
        <translation>Error al abrir el Detector de transmisión:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1585"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>No se pudo abrir el visor de vuelo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1615"/>
        <source>Failed to open Search Coordinator:
{error}</source>
        <translation>Error al abrir el Coordinador de búsqueda:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1631"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Error al abrir la documentación de Ayuda:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1647"/>
        <source>Failed to open Community Help:
{error}</source>
        <translation>Error al abrir la Ayuda de la comunidad:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1663"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Error al abrir el canal de YouTube:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1738"/>
        <source> Open Search Coordinator</source>
        <translation> Abrir Coordinador de búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1740"/>
        <source>Open the Search Coordinator to review every batch in this run.</source>
        <translation>Abra el Coordinador de búsqueda para revisar todos los lotes de esta ejecución.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1746"/>
        <source>Open the Results Viewer to review detection results.</source>
        <translation>Abra el Visor de resultados para revisar los resultados de las detecciones.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/MainWindow.py" line="1833"/>
        <source>Invalid Value</source>
        <translation>Valor no válido</translation>
    </message>
</context>
<context>
    <name>MapDock</name>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="263"/>
        <source>Map</source>
        <translation>Mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MapDock.py" line="360"/>
        <source>QtWebEngine not available — install PySide6-Addons for the interactive map. Showing list view instead.</source>
        <translation>QtWebEngine no está disponible — instale PySide6-Addons para usar el mapa interactivo. Se mostrará la vista de lista.</translation>
    </message>
</context>
<context>
    <name>MapExportDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="34"/>
        <source>Map Export Options</source>
        <translation>Opciones de exportación de mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="45"/>
        <source>Configure Map Export</source>
        <translation>Configurar exportación de mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="53"/>
        <source>Export Type</source>
        <translation>Tipo de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="56"/>
        <source>KML File</source>
        <translation>Archivo KML</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="58"/>
        <source>Export to a KML file for use in Google Earth, etc.</source>
        <translation>Exportar a un archivo KML para usar en Google Earth, etc.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="60"/>
        <source>CalTopo</source>
        <translation>CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="61"/>
        <source>Export directly to a CalTopo map</source>
        <translation>Exportar directamente a un mapa de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="73"/>
        <source>Data to Include</source>
        <translation>Datos a incluir</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="76"/>
        <source>Drone/Image Locations</source>
        <translation>Ubicaciones del dron/imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="78"/>
        <source>Include markers for each drone image location</source>
        <translation>Incluir marcadores para cada ubicación de imagen del dron</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="80"/>
        <source>Flagged Areas of Interest</source>
        <translation>Áreas de interés marcadas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="82"/>
        <source>Include markers for flagged AOIs</source>
        <translation>Incluir marcadores para los AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="84"/>
        <source>Coverage Area</source>
        <translation>Área de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="86"/>
        <source>Include polygon(s) showing the geographic coverage extent</source>
        <translation>Incluir polígonos que muestren la extensión geográfica de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="88"/>
        <source>Include images without flagged AOIs</source>
        <translation>Incluir imágenes sin AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="90"/>
        <source>If unchecked, only export locations for images that have flagged AOIs</source>
        <translation>Si no está marcada, exportar solo las ubicaciones de las imágenes que tengan AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="101"/>
        <source>Probability of Detection (POD)</source>
        <translation>Probabilidad de detección (POD)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="104"/>
        <source>POD coverage heatmap (terrain-aware)</source>
        <translation>Mapa de calor de cobertura POD (considera el terreno)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="107"/>
        <source>Compute a terrain and canopy aware probability-of-detection raster for the whole mission (all non-hidden images, independent of the selections above). KML exports embed the heatmap in the KML/KMZ as an image overlay; the GeoTIFF products (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json) are also written — the GeoTIFF can be imported into CalTopo Map Sheets. May take several minutes.</source>
        <translation>Calcula un ráster de probabilidad de detección consciente del terreno y del dosel para toda la misión (todas las imágenes no ocultas, independiente de las selecciones anteriores). Las exportaciones KML incrustan el mapa de calor en el KML/KMZ como superposición de imagen; también se escriben los productos GeoTIFF (coverage_pod.tif, coverage_looks.tif, coverage_gaps.geojson, stats.json); el GeoTIFF puede importarse en CalTopo Map Sheets. Puede tardar varios minutos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="114"/>
        <source>Show on map when complete</source>
        <translation>Mostrar en el mapa al finalizar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="125"/>
        <source>CalTopo Options</source>
        <translation>Opciones de CalTopo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="128"/>
        <source>Include Images</source>
        <translation>Incluir imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="130"/>
        <source>Upload photos to CalTopo markers (CalTopo only)</source>
        <translation>Subir fotos a los marcadores de CalTopo (solo CalTopo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="135"/>
        <source>Photo for flagged AOIs:</source>
        <translation>Foto para los AOI marcados:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="137"/>
        <source>Large Image (with zoom insets)</source>
        <translation>Imagen grande (con recuadros ampliados)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="138"/>
        <source>AOI Thumbnail Only</source>
        <translation>Solo miniatura del AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="139"/>
        <source>Both</source>
        <translation>Ambas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="142"/>
        <source>Large Image uploads the same multi-zoom composite used in the PDF report
(full image with 3x and 6x insets). AOI Thumbnail uploads a zoomed crop
centered on the detection. Both uploads each.</source>
        <translation>&quot;Imagen grande&quot; sube el mismo compuesto multizoom que se usa en el informe PDF
(imagen completa con recuadros a 3x y 6x). &quot;Solo miniatura del AOI&quot; sube un recorte
ampliado centrado en la detección. &quot;Ambas&quot; sube las dos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="173"/>
        <source>Export</source>
        <translation>Exportar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MapExportDialog.py" line="177"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>MatchedFilter</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="42"/>
        <source>Add a new color signature for matched filter detection. Each color can have its own threshold value.</source>
        <translation>Añadir una nueva firma de color para la detección por filtro adaptado. Cada color puede tener su propio valor de umbral.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="45"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
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
        <translation>Abre la ventana del Visor de rango para:
- Ver el rango de colores que se buscarán en el análisis de imágenes.
Úselo para ver qué colores se detectarán y optimizar los umbrales antes del procesamiento.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilter.ui" line="88"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
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
        <translation>Ningún color seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterController.py" line="299"/>
        <source>Please add at least one color to detect.</source>
        <translation>Añada al menos un color para detectar.</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizard</name>
    <message>
        <location filename="../resources/views/algorithms/MatchedFilterWizard.ui" line="16"/>
        <source>Add Color</source>
        <translation>Añadir color</translation>
    </message>
</context>
<context>
    <name>MatchedFilterWizardController</name>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="47"/>
        <source>No Targets Selected</source>
        <translation>Ningún objetivo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="57"/>
        <source>View Range</source>
        <translation>Ver rango</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/MatchedFilter/controllers/MatchedFilterWizardController.py" line="218"/>
        <source>Please add at least one target color to detect.</source>
        <translation>Añada al menos un color objetivo para detectar.</translation>
    </message>
</context>
<context>
    <name>MeasureDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="71"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Distance</source>
        <translation>Medir distancia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="85"/>
        <source>Measure Shadow</source>
        <translation>Medir sombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="87"/>
        <source>When checked, the two clicks estimate the height of a vertical object from its shadow. Click the base of the object first, then the tip of its shadow.</source>
        <translation>Al marcarlo, los dos clics estiman la altura de un objeto vertical a partir de su sombra. Haga clic primero en la base del objeto y luego en la punta de su sombra.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="94"/>
        <source>Ground Sample Distance</source>
        <translation>Distancia de muestreo del suelo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="97"/>
        <source>GSD:</source>
        <translation>GSD:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="99"/>
        <source>Enter GSD value</source>
        <translation>Introducir valor GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="103"/>
        <source>cm/px</source>
        <translation>cm/px</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="111"/>
        <source>Measurement</source>
        <translation>Medición</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="114"/>
        <source>Distance:</source>
        <translation>Distancia:</translation>
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
        <translation>Estimación de altura por sombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="135"/>
        <source>Use Anyway</source>
        <translation>Usar de todos modos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="137"/>
        <source>Force the estimate with the current base/tip clicks even though the drawn line doesn&apos;t match the expected shadow direction. Use only when you&apos;re confident the geometry is correct.</source>
        <translation>Fuerza la estimación con los clics actuales de base/punta aunque la línea dibujada no coincida con la dirección esperada de la sombra. Úselo solo si está seguro de que la geometría es correcta.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="181"/>
        <source>Click the BASE of the object first, then the TIP of its shadow.</source>
        <translation>Haga clic primero en la BASE del objeto y luego en la PUNTA de su sombra.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="185"/>
        <source>Click on the image to place the first point,
then click again to place the second point.</source>
        <translation>Haga clic en la imagen para colocar el primer punto,
y luego vuelva a hacer clic para colocar el segundo punto.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="158"/>
        <source>Clear</source>
        <translation>Borrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="160"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="228"/>
        <source>Measure Shadow Height</source>
        <translation>Medir altura por sombra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="415"/>
        <source>Image metadata unavailable</source>
        <translation>Metadatos de imagen no disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="553"/>
        <source>Rejected</source>
        <translation>Rechazado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/MeasureDialog.py" line="577"/>
        <source>No GSD value</source>
        <translation>Sin valor GSD</translation>
    </message>
</context>
<context>
    <name>MediaSelector</name>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool (ADIAT)</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron (ADIAT)</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="31"/>
        <source>What would you like to do?</source>
        <translation>¿Qué desea hacer?</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="86"/>
        <source>Image Analysis</source>
        <translation>Análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="163"/>
        <source>Open a completed analysis for review: scan a folder for results or reopen a recent one.</source>
        <translation>Abra un análisis completado para revisarlo: busque resultados en una carpeta o vuelva a abrir uno reciente.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="169"/>
        <source>Review Results</source>
        <translation>Revisar resultados</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="252"/>
        <source>Stream Analysis</source>
        <translation>Análisis de transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="329"/>
        <source>Pair with ADIAT Mobile drone controllers to receive their live camera feeds with detections.</source>
        <translation>Empareje controladores de dron de ADIAT Mobile para recibir sus transmisiones de cámara en vivo con detecciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="246"/>
        <source>RTMP, Video Files, HDMI Capture</source>
        <translation>RTMP, archivos de vídeo, captura HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/SelectionDialog.ui" line="335"/>
        <source>Flight Viewer</source>
        <translation>Visor de vuelo</translation>
    </message>
</context>
<context>
    <name>MissionGalleryContents</name>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="32"/>
        <source>Filters</source>
        <translation>Filtros</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="38"/>
        <source>Feed</source>
        <translation>Transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="48"/>
        <source>Detector</source>
        <translation>Detector</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="58"/>
        <source>Min score</source>
        <translation>Puntuación mín.</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="99"/>
        <source>0 detections</source>
        <translation>0 detecciones</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="119"/>
        <source>Export</source>
        <translation>Exportar</translation>
    </message>
    <message>
        <location filename="../resources/views/flight/mission_gallery_dock.ui" line="122"/>
        <source>Export filtered detections to the standard ADIAT image-mode gallery format.</source>
        <translation>Exportar las detecciones filtradas al formato estándar de galería del modo de imágenes de ADIAT.</translation>
    </message>
</context>
<context>
    <name>MissionGalleryDock</name>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="28"/>
        <source>Mission Gallery</source>
        <translation>Galería de la misión</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="53"/>
        <source>All feeds</source>
        <translation>Todas las transmisiones</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="59"/>
        <source>All detectors</source>
        <translation>Todos los detectores</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="126"/>
        <source>0 detections</source>
        <translation>0 detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/MissionGalleryDock.py" line="151"/>
        <source>{n} detections</source>
        <translation>{n} detecciones</translation>
    </message>
</context>
<context>
    <name>NeighborGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOINeighborGalleryDialog.py" line="172"/>
        <source>Unknown</source>
        <translation type="unfinished">Desconocido</translation>
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
        <translation>Sin imágenes para exportar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="153"/>
        <source>There are no images available to include in the PDF report.

All images may be hidden or there are no images in the dataset.</source>
        <translation>No hay imágenes disponibles para incluir en el informe PDF.

Todas las imágenes pueden estar ocultas o no hay imágenes en el conjunto de datos.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="162"/>
        <source>There are no images with flagged AOIs to include in the PDF report.

Please flag at least one AOI, or check &apos;Include images without flagged AOIs&apos; to include all images in the report.</source>
        <translation>No hay imágenes con AOI marcados para incluir en el informe PDF.

Marque al menos un AOI, o active &apos;Incluir imágenes sin AOI marcados&apos; para incluir todas las imágenes en el informe.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="172"/>
        <source>Save PDF File</source>
        <translation>Guardar archivo PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="174"/>
        <source>PDF files (*.pdf)</source>
        <translation>Archivos PDF (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="216"/>
        <source>Generating PDF Report</source>
        <translation>Generando informe PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="219"/>
        <source>Generating PDF Report...</source>
        <translation>Generando informe PDF...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="260"/>
        <source>Failed to generate PDF file: {error}</source>
        <translation>Error al generar el archivo PDF: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="276"/>
        <source>Success</source>
        <translation>Éxito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="277"/>
        <source>PDF report generated successfully!</source>
        <translation>¡Informe PDF generado correctamente!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/PDFExportController.py" line="294"/>
        <source>PDF generation failed: {error}</source>
        <translation>Error en la generación del PDF: {error}</translation>
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
        <translation>Configuración de exportación de PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="35"/>
        <source>Enter the following information for the PDF report:</source>
        <translation>Introduzca la siguiente información para el informe en PDF:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="44"/>
        <source>Enter organization name</source>
        <translation>Introduzca el nombre de la organización</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="45"/>
        <source>Organization:</source>
        <translation>Organización:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="49"/>
        <source>Enter search name</source>
        <translation>Introduzca el nombre de la búsqueda</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="50"/>
        <source>Search Name:</source>
        <translation>Nombre de la búsqueda:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="55"/>
        <source>Export Options:</source>
        <translation>Opciones de exportación:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="60"/>
        <source>Include images without flagged AOIs</source>
        <translation>Incluir imágenes sin AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="62"/>
        <source>When checked, all images will be included in the PDF report, even if they don&apos;t have any flagged AOIs. When unchecked, only images with flagged AOIs will be included.</source>
        <translation>Cuando está activado, se incluirán todas las imágenes en el informe PDF, incluso si no tienen AOI marcados. Cuando está desactivado, solo se incluirán las imágenes con AOI marcados.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="69"/>
        <source>Map Tiles:</source>
        <translation>Mosaicos del mapa:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="71"/>
        <source>Map</source>
        <translation>Mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="72"/>
        <source>Satellite</source>
        <translation>Satélite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="73"/>
        <source>Choose the background tiles for the PDF overview map.</source>
        <translation>Elija los mosaicos de fondo para el mapa general en PDF.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="80"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PDFExportDialog.py" line="82"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>PathValidationController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="515"/>
        <source>
  ... and {count} more</source>
        <translation>
  ... y {count} más</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="131"/>
        <source>{count} source image(s) not found at expected locations:

{files}

Please select the folder containing the source images.</source>
        <translation>{count} imágenes de origen no encontradas en las ubicaciones esperadas:

{files}

Seleccione la carpeta que contiene las imágenes de origen.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="129"/>
        <source>Source Images Not Found</source>
        <translation>Imágenes de origen no encontradas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="135"/>
        <source>Select Source Images Folder</source>
        <translation>Seleccionar carpeta de imágenes origen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="136"/>
        <source>Some Images Still Missing</source>
        <translation>Aún faltan algunas imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="165"/>
        <source>{count} detection mask(s) not found at expected locations:

{files}

Please select the folder containing the mask files.</source>
        <translation>{count} máscaras de detección no encontradas en las ubicaciones esperadas:

{files}

Seleccione la carpeta que contiene los archivos de máscara.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="163"/>
        <source>Detection Masks Not Found</source>
        <translation>Máscaras de detección no encontradas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="138"/>
        <source>Found {found} of {total} images.

Still missing:
{missing}</source>
        <translation>Se encontraron {found} de {total} imágenes.

Aún faltan:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="142"/>
        <source>None of the {total} missing images were found in that folder (including its subfolders).

Expected to find files named:
{missing}</source>
        <translation>No se encontró en esa carpeta (ni en sus subcarpetas) ninguna de las {total} imágenes que faltan.

Se esperaba encontrar archivos con estos nombres:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="169"/>
        <source>Select Masks Folder</source>
        <translation>Seleccionar carpeta de máscaras</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="170"/>
        <source>Some Masks Still Missing</source>
        <translation>Aún faltan algunas máscaras</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="172"/>
        <source>Found {found} of {total} masks.

Still missing:
{missing}</source>
        <translation>Se encontraron {found} de {total} máscaras.

Aún faltan:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="176"/>
        <source>None of the {total} missing masks were found in that folder (including its subfolders).

Expected to find files named:
{missing}</source>
        <translation>No se encontró en esa carpeta (ni en sus subcarpetas) ninguna de las {total} máscaras que faltan.

Se esperaba encontrar archivos con estos nombres:
{missing}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="410"/>
        <source>

{count} of these appear more than once in that folder, so which capture they belong to cannot be determined:
{files}

Choose the specific flight/sortie folder rather than a folder containing several of them.</source>
        <translation type="unfinished"></translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="421"/>
        <source>Choose Another Folder</source>
        <translation>Elegir otra carpeta</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/path/PathValidationController.py" line="428"/>
        <source>Continue Anyway</source>
        <translation>Continuar de todos modos</translation>
    </message>
</context>
<context>
    <name>PersonReferenceDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="285"/>
        <source>Person Size Reference</source>
        <translation>Referencia de tamaño de persona</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="292"/>
        <source>Reference Person</source>
        <translation>Persona de referencia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="311"/>
        <source>Standing</source>
        <translation>De pie</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="313"/>
        <source>Lying down</source>
        <translation>Acostada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="315"/>
        <source>Sitting</source>
        <translation>Sentada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="324"/>
        <source>Show shadows (from capture time)</source>
        <translation>Mostrar sombras (según la hora de captura)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="327"/>
        <source>Use terrain elevation (DEM)</source>
        <translation>Usar elevación del terreno (DEM)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="336"/>
        <source>Rotate the person on the ground to line it up with an object</source>
        <translation>Gire la persona sobre el terreno para alinearla con un objeto</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="341"/>
        <source>Click to choose overlay color</source>
        <translation>Haga clic para elegir el color de superposición</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="349"/>
        <source>Size:</source>
        <translation>Tamaño:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="350"/>
        <source>Show:</source>
        <translation>Mostrar:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="351"/>
        <source>Rotation:</source>
        <translation>Rotación:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="354"/>
        <source>Color:</source>
        <translation>Color:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="370"/>
        <source>Adjust camera clock...</source>
        <translation>Ajustar el reloj de la cámara...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="374"/>
        <source>Drag the white handle to position the reference person. Silhouettes are drawn at true ground scale for this image&apos;s altitude and camera angle.</source>
        <translation>Arrastre el controlador blanco para colocar a la persona de referencia. Las siluetas se dibujan a escala real del terreno según la altitud y el ángulo de cámara de esta imagen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="382"/>
        <source>Recenter</source>
        <translation>Centrar de nuevo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="383"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="446"/>
        <source>No camera clock fault or applied correction was found for this folder.</source>
        <translation>No se encontró ningún fallo del reloj de la cámara ni ninguna corrección aplicada en esta carpeta.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="490"/>
        <source>Perspective overlay unavailable: this image is missing the altitude or lens metadata needed to project a person.</source>
        <translation>Superposición de perspectiva no disponible: a esta imagen le faltan los metadatos de altitud o lente necesarios para proyectar una persona.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="545"/>
        <source>Zoomed to the reference person: at this altitude a person spans only a few pixels.</source>
        <translation>Ampliado a la persona de referencia: a esta altitud una persona ocupa solo unos pocos píxeles.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="561"/>
        <source>no image loaded</source>
        <translation>no hay imagen cargada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="566"/>
        <source>image metadata could not be read</source>
        <translation>no se pudieron leer los metadatos de la imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="570"/>
        <source>image has no GPS coordinates</source>
        <translation>la imagen no tiene coordenadas GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="582"/>
        <source>capture time / timezone not in metadata</source>
        <translation>la hora de captura / zona horaria no está en los metadatos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="588"/>
        <source>sun position could not be computed</source>
        <translation>no se pudo calcular la posición del sol</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="598"/>
        <source>Sun at capture: {elev:.0f}° above horizon, azimuth {az:.0f}°.</source>
        <translation>Sol durante la captura: {elev:.0f}° sobre el horizonte, acimut {az:.0f}°.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="603"/>
        <source>Capture time zone estimated from GPS location.</source>
        <translation>Zona horaria de captura estimada a partir de la ubicación GPS.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="606"/>
        <source>Using repaired capture time (camera clock fault).</source>
        <translation>Se usa la hora de captura corregida (fallo del reloj de la cámara).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="611"/>
        <source>the sun was below the horizon at capture</source>
        <translation>el sol estaba por debajo del horizonte durante la captura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="613"/>
        <source>sun position unavailable</source>
        <translation>posición del sol no disponible</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="614"/>
        <source>Shadow unavailable: {reason}.</source>
        <translation>Sombra no disponible: {reason}.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="713"/>
        <source>Place the person and shadow on the DEM terrain surface</source>
        <translation>Colocar la persona y la sombra sobre la superficie del terreno DEM</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="717"/>
        <source>Terrain (DEM) data is not available for this image</source>
        <translation>Los datos de terreno (DEM) no están disponibles para esta imagen</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/PersonReferenceDialog.py" line="977"/>
        <source>Choose Overlay Color</source>
        <translation>Elegir color de superposición</translation>
    </message>
</context>
<context>
    <name>PlaybackControlBar</name>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="54"/>
        <source>Play/Pause (Space)</source>
        <translation>Reproducir/Pausar (Espacio)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/PlaybackControlBar.py" line="67"/>
        <source>Seek through video</source>
        <translation>Desplazarse por el video</translation>
    </message>
</context>
<context>
    <name>Preferences</name>
    <message>
        <location filename="../resources/views/Preferences.ui" line="14"/>
        <source>Preferences</source>
        <translation>Preferencias</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="55"/>
        <source>Select the application theme appearance.
Changes the overall color scheme and visual style.</source>
        <translation>Seleccione la apariencia del tema de la aplicación.
Cambia el esquema de colores general y el estilo visual.</translation>
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
        <translation>Elija el tema de la aplicación:
• Claro: Tema brillante con fondos claros y texto oscuro
• Oscuro: Tema oscuro con fondos oscuros y texto claro
Los cambios se aplican inmediatamente a todas las ventanas.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="78"/>
        <source>Light</source>
        <translation>Claro</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="83"/>
        <source>Dark</source>
        <translation>Oscuro</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="114"/>
        <source>Warning threshold for total AOIs detected across all images.
Prompts user when this limit is reached during processing.</source>
        <translation>Umbral de advertencia para el total de AOI detectados en todas las imágenes.
Avisa al usuario cuando se alcanza este límite durante el procesamiento.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="118"/>
        <source>Max Areas of Interest: </source>
        <translation>Áreas de interés máx.: </translation>
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
        <translation>Establezca el umbral de advertencia para el total de AOI detectados durante el procesamiento.
• Rango: 0 a 1000
• Predeterminado: 100
Cuando se detecta este número de AOI en todas las imágenes:
• La interfaz muestra un mensaje de advertencia
• El usuario puede cancelar el procesamiento, ajustar la configuración y volver a ejecutar
• Si no se toma ninguna acción, la detección continúa automáticamente
Use valores más bajos para detectar recuentos altos de detección con anticipación.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="161"/>
        <source>Radius for combining neighboring AOIs into single detections.
AOIs within this distance are merged together.</source>
        <translation>Radio para combinar AOI vecinos en detecciones únicas.
Los AOI dentro de esta distancia se fusionan.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="165"/>
        <source>Area of Interest Circle Radius(px):</source>
        <translation>Radio del círculo del área de interés (px):</translation>
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
        <translation>Establezca el radio para combinar AOI cercanos durante la detección.
• Rango: 0 a 100 píxeles
• Predeterminado: 25 píxeles
Cuando los AOI están dentro de este radio entre sí:
• Se combinan en un único AOI
• El proceso se repite hasta que no queden vecinos dentro del radio
• Valores mayores: Combina detecciones más distantes (menos AOI totales)
• Valores menores: Mantiene las detecciones separadas (más AOI individuales)
Úselo para consolidar detecciones agrupadas en objetos únicos.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="209"/>
        <source>Format for displaying geographic coordinates throughout the application.
Affects how GPS locations are shown in the viewer and exports.</source>
        <translation>Formato para mostrar coordenadas geográficas en toda la aplicación.
Afecta cómo se muestran las ubicaciones GPS en el visor y las exportaciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="213"/>
        <source>Coordinate System:</source>
        <translation>Sistema de coordenadas:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="225"/>
        <source>Select the geographic coordinate display format:
• Lat/Long - Decimal Degrees: 34.123456, -118.987654 (most common, easy to use)
• Lat/Long - Degrees, Minutes, Seconds: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; W (traditional navigation)
• UTM: Universal Transverse Mercator grid system with zone, easting, northing (military, surveying)
This setting affects coordinate display in the viewer, exports, and overlays.</source>
        <translation>Seleccione el formato de visualización de coordenadas geográficas:
• Lat/Lon - Grados decimales: 34.123456, -118.987654 (más común, fácil de usar)
• Lat/Lon - Grados, minutos, segundos: 34° 7&apos; 24.4416&quot; N, 118° 59&apos; 15.5424&quot; O (navegación tradicional)
• UTM: Sistema de cuadrícula Universal Transversal de Mercator con zona, este, norte (militar, topografía)
Esta configuración afecta la visualización de coordenadas en el visor, exportaciones y superposiciones.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="233"/>
        <source>Lat/Long - Decimal Degrees</source>
        <translation>Lat/Lon - Grados decimales</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="238"/>
        <source>Lat/Long - Degrees, Minutes, Seconds</source>
        <translation>Lat/Lon - Grados, minutos, segundos</translation>
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
        <translation>Unidad para mostrar medidas de temperatura de imágenes térmicas.
Usada al analizar imágenes térmicas de cámaras térmicas.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="266"/>
        <source>Temperature Unit:</source>
        <translation>Unidad de temperatura:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="278"/>
        <source>Select the temperature unit for thermal image analysis:
• Fahrenheit (°F): Imperial temperature scale (US standard)
  - Water freezes at 32°F, boils at 212°F
• Celsius (°C): Metric temperature scale (international standard)
  - Water freezes at 0°C, boils at 100°C
Applies to thermal camera data display and analysis results.</source>
        <translation>Seleccione la unidad de temperatura para el análisis de imágenes térmicas:
• Fahrenheit (°F): Escala de temperatura imperial (estándar de EE. UU.)
  - El agua se congela a 32°F, hierve a 212°F
• Celsius (°C): Escala de temperatura métrica (estándar internacional)
  - El agua se congela a 0°C, hierve a 100°C
Se aplica a la visualización de datos de cámara térmica y a los resultados del análisis.</translation>
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
        <translation>Unidad para mostrar medidas de distancia y altitud.
Usada para la altitud del dron, distancias de objetos y cálculos espaciales.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="315"/>
        <source>Distance Unit:</source>
        <translation>Unidad de distancia:</translation>
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
        <translation>Seleccione la unidad de distancia para las mediciones:
• Metros (m): Unidad de distancia métrica (estándar internacional)
  - 1 metro = 3,281 pies
  - Usada para altitud, GSD y cálculos de distancia
• Pies (ft): Unidad de distancia imperial (estándar de EE. UU.)
  - 1 pie = 0,3048 metros
  - Común en aviación y topografía de EE. UU.
Se aplica a la visualización de altitud, cálculos de GSD y mediciones de distancia.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="338"/>
        <source>Meters</source>
        <translation>Metros</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="343"/>
        <source>Feet</source>
        <translation>Pies</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="362"/>
        <source>Toggle Offline Only mode.
When enabled, the app skips any network calls (map tiles, CalTopo exports) and works with cached data only.</source>
        <translation>Alternar el modo Solo sin conexión.
Cuando está habilitado, la aplicación omite cualquier llamada de red (mosaicos de mapa, exportaciones a CalTopo) y funciona solo con datos en caché.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="366"/>
        <source>Offline Only Mode:</source>
        <translation>Modo solo sin conexión:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="378"/>
        <source>Disable online functionality (tile downloads, CalTopo integration) and work entirely offline.</source>
        <translation>Desactivar la funcionalidad en línea (descargas de mosaicos, integración con CalTopo) y trabajar totalmente sin conexión.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="381"/>
        <location filename="../resources/views/Preferences.ui" line="422"/>
        <source>Enable</source>
        <translation>Habilitar</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="399"/>
        <source>Use terrain elevation data (DEM/DTM/DSM) for more accurate AOI GPS coordinate calculations.
When enabled, uses online or local elevation data to account for terrain variations.
When disabled, assumes flat terrain at takeoff altitude.</source>
        <translation>Usar datos de elevación del terreno (DEM/DTM/DSM) para cálculos más precisos de coordenadas GPS de AOI.
Cuando está habilitado, usa datos de elevación en línea o locales para tener en cuenta las variaciones del terreno.
Cuando está deshabilitado, asume terreno plano a la altitud de despegue.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="416"/>
        <source>Enable terrain-corrected AOI positioning using DEM/DTM/DSM elevation data.
• When enabled: Downloads and caches elevation tiles for accurate positioning
• When disabled: Uses flat terrain assumption (faster, works offline)
Terrain data is cached locally and works offline after first download.</source>
        <translation>Habilitar el posicionamiento de AOI corregido por terreno usando datos de elevación DEM/DTM/DSM.
• Cuando está habilitado: Descarga y almacena en caché mosaicos de elevación para un posicionamiento preciso
• Cuando está deshabilitado: Usa el supuesto de terreno plano (más rápido, funciona sin conexión)
Los datos de terreno se almacenan en caché localmente y funcionan sin conexión tras la primera descarga.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="404"/>
        <source>Use Terrain Elevation:</source>
        <translation>Usar elevación del terreno:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="440"/>
        <source>Manage the terrain elevation data cache.
Terrain tiles are downloaded and stored locally for offline use.</source>
        <translation>Administrar la caché de datos de elevación del terreno.
Los mosaicos de terreno se descargan y almacenan localmente para uso sin conexión.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="444"/>
        <source>Terrain Cache:</source>
        <translation>Caché de terreno:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="456"/>
        <source>0 tiles (0 MB)</source>
        <translation>0 mosaicos (0 MB)</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="481"/>
        <source>Clear all cached terrain elevation tiles.
This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>Borrar todos los mosaicos de elevación del terreno almacenados en caché.
Esto requerirá volver a descargar los mosaicos cuando se use la elevación del terreno.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="485"/>
        <source>Clear Cache</source>
        <translation>Borrar caché</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="517"/>
        <source>Version of the current drone sensor configuration file.
Contains camera specifications, sensor dimensions, and focal length data for different drone models.</source>
        <translation>Versión del archivo de configuración del sensor del dron actual.
Contiene especificaciones de cámara, dimensiones del sensor y datos de distancia focal para diferentes modelos de dron.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="521"/>
        <source>Drone Sensor File Version:</source>
        <translation>Versión del archivo de sensor del dron:</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="546"/>
        <source>Currently loaded drone sensor file version number.
The sensor file defines camera parameters for accurate GSD and AOI calculations.</source>
        <translation>Número de versión del archivo de sensor de dron cargado actualmente.
El archivo de sensor define los parámetros de cámara para cálculos precisos de GSD y AOI.</translation>
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
        <translation>Reemplazar el archivo de configuración del sensor del dron actual.
Permite actualizar a una versión más nueva o a especificaciones de sensor personalizadas.
Formato de archivo requerido: JSON con modelos de dron, sensores, distancias focales y dimensiones.
Úselo cuando:
• Haya nuevos modelos de dron disponibles
• Sea necesario actualizar las especificaciones del sensor
• Se necesiten configuraciones de cámara personalizadas
Haga una copia de seguridad del archivo existente antes de reemplazarlo.</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="588"/>
        <source>Replace</source>
        <translation>Reemplazar</translation>
    </message>
    <message>
        <location filename="../resources/views/Preferences.ui" line="609"/>
        <source>Close the Preferences window.
All changes are saved automatically when modified.</source>
        <translation>Cerrar la ventana de Preferencias.
Todos los cambios se guardan automáticamente al modificarse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="69"/>
        <source>Language:</source>
        <translation>Idioma:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="101"/>
        <source>AWS Terrain Tiles (online, ~30 m) is always available as the baseline; local USGS 3DEP adds 1 m detail where downloaded.</source>
        <translation>AWS Terrain Tiles (en línea, ~30 m) siempre está disponible como base; el USGS 3DEP local añade detalle de 1 m donde se haya descargado.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="109"/>
        <source>Elevation Source:</source>
        <translation>Fuente de elevación:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="119"/>
        <location filename="../app/core/controllers/Preferences.py" line="204"/>
        <source>Manifest CSV:</source>
        <translation>CSV de manifiesto:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="121"/>
        <source>Path to dem_manifest.csv</source>
        <translation>Ruta a dem_manifest.csv</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="122"/>
        <location filename="../app/core/controllers/Preferences.py" line="133"/>
        <location filename="../app/core/controllers/Preferences.py" line="207"/>
        <location filename="../app/core/controllers/Preferences.py" line="217"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="130"/>
        <location filename="../app/core/controllers/Preferences.py" line="214"/>
        <source>Tiles directory:</source>
        <translation>Directorio de teselas:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="132"/>
        <location filename="../app/core/controllers/Preferences.py" line="216"/>
        <source>Folder containing the GeoTIFF tiles</source>
        <translation>Carpeta que contiene las teselas GeoTIFF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="142"/>
        <location filename="../app/core/controllers/Preferences.py" line="378"/>
        <source>3DEP is inactive until both paths are set — the AWS Terrain Tiles baseline is used. Use Download tiles… or Browse.</source>
        <translation>3DEP está inactivo hasta que se establezcan ambas rutas; se usa la base de AWS Terrain Tiles. Use Descargar teselas… o Examinar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="174"/>
        <source>Terrain</source>
        <translation>Terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="191"/>
        <source>Canopy Data Source</source>
        <translation>Fuente de datos de dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="195"/>
        <source>Source:</source>
        <translation>Fuente:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="206"/>
        <source>Path to the canopy manifest CSV</source>
        <translation>Ruta al CSV de manifiesto del dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="226"/>
        <location filename="../app/core/controllers/Preferences.py" line="451"/>
        <source>Canopy is disabled until both paths are set — use Download tiles… or Browse.</source>
        <translation>El dosel está deshabilitado hasta que ambas rutas estén configuradas — use Descargar teselas… o Examinar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="236"/>
        <source>Download tiles...</source>
        <translation>Descargar teselas...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="238"/>
        <source>Download DEM and/or canopy tiles for an area of interest and register them here. Note: the canopy download uses Meta/WRI data and registers it as the canopy source.</source>
        <translation>Descargar teselas de MDE y/o dosel para un área de interés y registrarlas aquí. Nota: la descarga de dosel usa datos de Meta/WRI y los registra como fuente de dosel.</translation>
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
        <translation>Los archivos 3DEP registrados ya no existen en el disco; se usa la base de AWS Terrain Tiles. Vuelva a descargar o corrija las rutas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="416"/>
        <source>Select 3DEP manifest CSV</source>
        <translation>Seleccionar CSV de manifiesto 3DEP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="418"/>
        <location filename="../app/core/controllers/Preferences.py" line="482"/>
        <source>CSV files (*.csv);;All files (*)</source>
        <translation>Archivos CSV (*.csv);;Todos los archivos (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="428"/>
        <source>Select 3DEP tiles directory</source>
        <translation>Seleccionar directorio de teselas 3DEP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="457"/>
        <source>The registered canopy files no longer exist on disk — canopy is disabled. Re-download or fix the paths.</source>
        <translation>Los archivos de dosel registrados ya no existen en el disco; el dosel está desactivado. Vuelva a descargar o corrija las rutas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="481"/>
        <source>Select canopy manifest CSV</source>
        <translation>Seleccionar CSV de manifiesto del dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="490"/>
        <source>Select canopy tiles directory</source>
        <translation>Seleccionar directorio de teselas del dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="501"/>
        <source>Download Tiles</source>
        <translation>Descargar teselas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="502"/>
        <source>The tile downloader is unavailable:
{error}</source>
        <translation>El descargador de teselas no está disponible:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="575"/>
        <source>{tiles} tiles ({size_mb:.1f} MB)</source>
        <translation>{tiles} mosaicos ({size_mb:.1f} MB)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="567"/>
        <source>Not available</source>
        <translation>No disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="584"/>
        <source>N/A (local tiles)</source>
        <translation>N/D (teselas locales)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="587"/>
        <location filename="../app/core/controllers/Preferences.py" line="595"/>
        <location filename="../app/core/controllers/Preferences.py" line="623"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="596"/>
        <source>Terrain service not available.</source>
        <translation>Servicio de terreno no disponible.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="602"/>
        <source>Clear Terrain Cache</source>
        <translation>Borrar caché de terreno</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="604"/>
        <source>Are you sure you want to clear all cached terrain elevation data?

This will require re-downloading tiles when terrain elevation is used.</source>
        <translation>¿Está seguro de que desea borrar todos los datos de elevación del terreno almacenados en caché?

Esto requerirá volver a descargar los mosaicos cuando se use la elevación del terreno.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="617"/>
        <source>Cache Cleared</source>
        <translation>Caché borrada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="618"/>
        <source>Cleared {count} cached terrain tiles.</source>
        <translation>Se borraron {count} mosaicos de terreno en caché.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="624"/>
        <source>Failed to clear cache: {error}</source>
        <translation>Error al borrar la caché: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="631"/>
        <source>Select a Drone Sensor File</source>
        <translation>Seleccionar un archivo de sensor de dron</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="633"/>
        <source>CSV Files (*.csv)</source>
        <translation>Archivos CSV (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="659"/>
        <source>Restart Required</source>
        <translation>Reinicio necesario</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/Preferences.py" line="660"/>
        <source>Please restart the application for language changes to take effect.</source>
        <translation>Reinicie la aplicación para que los cambios de idioma surtan efecto.</translation>
    </message>
</context>
<context>
    <name>QtImageViewer</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/QtImageViewer.py" line="384"/>
        <source>Open image</source>
        <translation>Abrir imagen</translation>
    </message>
</context>
<context>
    <name>RXAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
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
        <translation>Número de segmentos en los que dividir cada imagen para el análisis.
El algoritmo RX analiza cada segmento independientemente para detectar anomalías locales.
Impacto en el rendimiento:
• Mayor número de segmentos: AUMENTA el tiempo de procesamiento (más segmentos a analizar)
• Menor número de segmentos: REDUCE el tiempo de procesamiento (menos segmentos a analizar)
• 1 segmento: Procesamiento más rápido (analiza toda la imagen de una vez)
Un mayor número de segmentos mejora la detección en imágenes con fondos variados.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="38"/>
        <source>Image Segments:</source>
        <translation>Segmentos de imagen:</translation>
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
        <translation>Seleccione el número de segmentos en los que dividir cada imagen.
• Opciones: 1, 2, 4, 6, 9, 16, 25, 36 segmentos
• Predeterminado: 1 (analizar toda la imagen como un segmento)
El algoritmo Anomalía RX usa análisis estadístico para detectar píxeles inusuales:
• 1 segmento: Analiza toda la imagen de una vez (mejor para imágenes pequeñas)
• Más segmentos: Analiza regiones locales independientemente (mejor para imágenes grandes)
Un mayor número de segmentos mejora la detección en imágenes con fondos variados.
Recomendado: 4-9 segmentos para imágenes típicas de dron.</translation>
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
        <translation>Sensibilidad de detección para la detección de anomalías.
• Rango: 1 a 10
• Predeterminado: 5
Controla qué tan estadísticamente diferente debe ser un píxel del fondo para ser detectado:
• Valores más bajos (1-3): REDUCEN las detecciones - menos sensible, solo detecta anomalías fuertes
• Valores más altos (7-10): AUMENTAN las detecciones - más sensible, detecta anomalías sutiles
Mayor sensibilidad encuentra más objetivos potenciales pero puede incluir ruido/falsos positivos.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="146"/>
        <source>Sensitivity:</source>
        <translation>Sensibilidad:</translation>
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
        <translation>Ajuste la sensibilidad de detección para la detección de anomalías.
• Rango: 1 a 10
• Predeterminado: 5
El algoritmo RX usa análisis estadístico para encontrar píxeles que difieran del fondo:
• Valores más bajos (1-3): Menos sensible, solo detecta anomalías fuertes (menos falsos positivos)
• Valores medios (4-6): Detección equilibrada (recomendado para la mayoría de los casos)
• Valores más altos (7-10): Más sensible, detecta anomalías sutiles (más detecciones, puede incluir ruido)
Las anomalías son píxeles estadísticamente distintos del fondo circundante.
Use menor sensibilidad para imágenes limpias, mayor para encontrar objetivos sutiles.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomaly.ui" line="205"/>
        <source>Current sensitivity level for anomaly detection.
Displays the value selected on the sensitivity slider (1-10).</source>
        <translation>Nivel de sensibilidad actual para la detección de anomalías.
Muestra el valor seleccionado en el deslizador de sensibilidad (1-10).</translation>
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
        <translation>¿Sus imágenes contienen escenas complejas con edificios, vehículos o cobertura del suelo antropogénica mixta?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="49"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="64"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="100"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>¿Con qué agresividad debe ADIAT buscar anomalías?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/RXAnomalyWizard.ui" line="113"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: Un valor más alto encontrará más anomalías potenciales pero también puede aumentar los falsos positivos.</translation>
    </message>
</context>
<context>
    <name>RXAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="50"/>
        <source>Very 
Conservative</source>
        <translation>Muy 
conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="51"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="52"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="53"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/RXAnomaly/controllers/RXAnomalyWizardController.py" line="54"/>
        <source>Very 
Aggressive</source>
        <translation>Muy 
agresivo</translation>
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
        <translation>&lt;br&gt;&lt;b&gt;Umbral:&lt;/b&gt; {value}</translation>
    </message>
</context>
<context>
    <name>RecentColorsDialog</name>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="151"/>
        <source>Recent Colors</source>
        <translation>Colores recientes</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="162"/>
        <source>Select a recently used color:</source>
        <translation>Seleccione un color usado recientemente:</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="178"/>
        <source>No recent colors found</source>
        <translation>No se encontraron colores recientes</translation>
    </message>
    <message>
        <location filename="../app/algorithms/Shared/views/RecentColorsDialog.py" line="204"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
<context>
    <name>RenderingTab</name>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="44"/>
        <source>Shape Options</source>
        <translation>Opciones de forma</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="47"/>
        <source>Shape Mode:</source>
        <translation>Modo de forma:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="49"/>
        <source>Box</source>
        <translation>Rectángulo</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="50"/>
        <source>Circle</source>
        <translation>Círculo</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="51"/>
        <source>Dot</source>
        <translation>Punto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="52"/>
        <source>Off</source>
        <translation>Desactivado</translation>
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
        <translation>Forma que se dibujará alrededor de las detecciones:

• Rectángulo: rectángulo alrededor del cuadro delimitador de la detección.
  Use esta opción para: límites precisos y visualización técnica.

• Círculo: círculo que engloba la detección (150% del radio del contorno).
  Use esta opción para: uso general y aspecto más limpio (predeterminado).

• Punto: punto pequeño en el centroide de la detección.
  Use esta opción para: superposición mínima y renderizado rápido.

• Desactivado: sin superposición de forma (solo miniaturas/texto si están activados).
  Use esta opción para: video limpio con superposiciones mínimas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="70"/>
        <source>Visual Options</source>
        <translation>Opciones visuales</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="73"/>
        <source>Show Text Labels (slower)</source>
        <translation>Mostrar etiquetas de texto (más lento)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="75"/>
        <source>Displays text labels near detections showing detection information.
Adds ~5-15ms processing overhead depending on detection count.
Labels show: detection type, confidence, area.
Recommended: OFF for speed, ON for debugging/analysis.</source>
        <translation>Muestra etiquetas de texto junto a las detecciones con información de la detección.
Añade ~5-15 ms de carga de procesamiento según la cantidad de detecciones.
Las etiquetas muestran: tipo de detección, confianza y área.
Recomendado: desactivado para mayor velocidad; activado para depuración/análisis.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="82"/>
        <source>Show Contours (slowest)</source>
        <translation>Mostrar contornos (lo más lento)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="84"/>
        <source>Draws exact detection contours (pixel-precise boundaries).
Adds ~10-20ms processing overhead (very expensive).
Shows exact shape detected by algorithm.
Recommended: OFF for speed, ON only for detailed analysis.</source>
        <translation>Dibuja los contornos exactos de las detecciones (límites con precisión de píxel).
Añade ~10-20 ms de carga de procesamiento (muy costoso).
Muestra la forma exacta detectada por el algoritmo.
Recomendado: desactivado para velocidad; activado solo para análisis detallado.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="92"/>
        <source>Use Detection Color (hue @ 100% sat/val for color anomalies)</source>
        <translation>Usar color de la detección (tono al 100% de sat./valor para anomalías de color)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="95"/>
        <source>Color the detection overlay based on detected color.
For color anomalies: Uses the detected hue at 100% saturation/value.
For motion detections: Uses default color (green/blue).
Helps visually identify what color was detected.
Recommended: ON for color detection, OFF for motion-only.</source>
        <translation>Colorea la superposición de detección según el color detectado.
Para anomalías de color: usa el tono detectado al 100% de saturación/valor.
Para detecciones de movimiento: usa el color predeterminado (verde/azul).
Ayuda a identificar visualmente qué color se detectó.
Recomendado: activado para detección de color; desactivado si solo se usa movimiento.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="106"/>
        <source>Performance Limits</source>
        <translation>Límites de rendimiento</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="109"/>
        <source>Max Detections:</source>
        <translation>Detecciones máx.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="115"/>
        <source>Maximum number of detections to render on screen (0-1000).
Prevents rendering slowdown when hundreds of detections occur.
Shows highest confidence detections first.
0 = Unlimited (may cause lag with many detections).
Recommended: 10 for general use, 50 for complex rendering (text+contours).</source>
        <translation>Número máximo de detecciones que se renderizarán en pantalla (0-1000).
Evita lentitud de renderizado cuando aparecen cientos de detecciones.
Muestra primero las detecciones de mayor confianza.
0 = sin límite (puede causar retraso con muchas detecciones).
Recomendado: 10 para uso general, 50 para renderizado complejo (texto + contornos).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="126"/>
        <source>Temporal Voting</source>
        <translation>Votación temporal</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="129"/>
        <source>Enable Temporal Voting (reduce flicker)</source>
        <translation>Activar votación temporal (reducir parpadeo)</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="132"/>
        <source>Smooths detections across frames using temporal consistency.
Detections must appear in N out of M consecutive frames to be confirmed.
Significantly reduces flickering false positives.
Recommended: ON for all use cases (default).</source>
        <translation>Suaviza las detecciones entre fotogramas usando coherencia temporal.
Las detecciones deben aparecer en N de M fotogramas consecutivos para confirmarse.
Reduce considerablemente los falsos positivos intermitentes.
Recomendado: activado para todos los casos de uso (predeterminado).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="142"/>
        <source>Window Frames (M):</source>
        <translation>Fotogramas de ventana (M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="147"/>
        <source>Size of temporal voting window (2-30 frames).
Detections must appear in N out of M consecutive frames.
Larger values = longer memory, more stable, slower response to new objects.
Smaller values = shorter memory, faster response, less stable.
Recommended: 5 for 30fps (~167ms window), 7 for 60fps.</source>
        <translation>Tamaño de la ventana de votación temporal (2-30 fotogramas).
Las detecciones deben aparecer en N de M fotogramas consecutivos.
Valores mayores = más memoria, más estabilidad y respuesta más lenta ante objetos nuevos.
Valores menores = menos memoria, respuesta más rápida y menor estabilidad.
Recomendado: 5 para video de 30 fps (ventana de ~167 ms), 7 para 60 fps.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="155"/>
        <source>Threshold (N of M):</source>
        <translation>Umbral (N de M):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="160"/>
        <source>Number of frames within window where detection must appear (N of M).
Higher values = more stringent, filters transient false positives.
Lower values = more lenient, faster response to new objects.
Must be ≤ Window Frames.
Recommended: 3 out of 5 (detection in 60% of frames).</source>
        <translation>Número de fotogramas dentro de la ventana en los que debe aparecer la detección (N de M).
Valores mayores = criterio más estricto; filtra falsos positivos transitorios.
Valores menores = criterio más flexible; responde más rápido a objetos nuevos.
Debe ser ≤ que los fotogramas de ventana.
Recomendado: 3 de 5 (detección en el 60% de los fotogramas).</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="173"/>
        <source>Detection Cleanup</source>
        <translation>Limpieza de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="177"/>
        <source>Enable Aspect Ratio Filtering</source>
        <translation>Activar filtro de relación de aspecto</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="180"/>
        <source>Filter out very thin or stretched detections based on width/height.
Useful for removing wires, long shadows, or other non-object shapes.
Most users can leave this OFF unless you see many long skinny false detections.</source>
        <translation>Filtra detecciones muy delgadas o alargadas según la relación ancho/alto.
Útil para eliminar cables, sombras largas u otras formas que no son objetos.
La mayoría de los usuarios puede dejarlo desactivado salvo que vea muchos falsos positivos largos y estrechos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="189"/>
        <source>Min Ratio:</source>
        <translation>Relación mín.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="195"/>
        <source>Minimum width/height ratio to keep (0.1-10.0).
Lower values = allow taller, thinner detections.
Higher values = require detections to be more square.
Example: 0.2 ≈ reject if height is more than 5× width.</source>
        <translation>Relación ancho/alto mínima que se conservará (0,1-10,0).
Valores menores = permiten detecciones más altas y delgadas.
Valores mayores = exigen detecciones más cuadradas.
Ejemplo: 0,2 ≈ rechazar si la altura es más de 5 veces el ancho.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="202"/>
        <source>Max Ratio:</source>
        <translation>Relación máx.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="208"/>
        <source>Maximum width/height ratio to keep (0.1-20.0).
Lower values = reject very wide, thin detections.
Higher values = allow wider objects such as vehicles or long equipment.</source>
        <translation>Relación ancho/alto máxima que se conservará (0,1-20,0).
Valores menores = rechazan detecciones muy anchas y delgadas.
Valores mayores = permiten objetos más anchos, como vehículos o equipos largos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="217"/>
        <source>Detection Clustering</source>
        <translation>Agrupación de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="220"/>
        <source>Enable Detection Clustering</source>
        <translation>Activar agrupación de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="223"/>
        <source>Optionally merge nearby detections into a single, larger detection.
Useful when one object appears as many small adjacent detections.
Most users can leave this OFF unless objects look fragmented.</source>
        <translation>Fusiona opcionalmente las detecciones cercanas en una detección única más grande.
Útil cuando un objeto aparece como varias detecciones pequeñas contiguas.
La mayoría de los usuarios puede dejarlo desactivado salvo que los objetos se vean fragmentados.</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="232"/>
        <source>Clustering Distance (px):</source>
        <translation>Distancia de agrupación (px):</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/RenderingTab.py" line="237"/>
        <source>Maximum distance between detection centers to merge them (0-500 pixels).
Lower values = only merge very close detections.
Higher values = merge detections that are farther apart (may over-merge).</source>
        <translation>Distancia máxima entre centros de detección para fusionarlos (0-500 píxeles).
Valores menores = solo fusionan detecciones muy cercanas.
Valores mayores = fusionan detecciones más alejadas (puede agrupar de más).</translation>
    </message>
</context>
<context>
    <name>ResultsFolderDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="115"/>
        <source>Load Results Folder</source>
        <translation>Cargar carpeta de resultados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="124"/>
        <source>Found {count} result(s)</source>
        <translation>Se encontraron {count} resultados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Folder</source>
        <translation>Carpeta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="132"/>
        <source>Images</source>
        <translation>Imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Missing</source>
        <translation>Faltante</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>AOIs</source>
        <translation>AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>Map</source>
        <translation>Mapa</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="133"/>
        <source>View</source>
        <translation>Ver</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="170"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="216"/>
        <source>Open in Google Maps</source>
        <translation>Abrir en Google Maps</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="226"/>
        <source>No images available - cannot get GPS location</source>
        <translation>No hay imágenes disponibles - no se puede obtener la ubicación GPS</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="228"/>
        <source>No GPS coordinates found in images</source>
        <translation>No se encontraron coordenadas GPS en las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="248"/>
        <source>Open in Results Viewer</source>
        <translation>Abrir en el Visor de resultados</translation>
    </message>
</context>
<context>
    <name>ResultsLoadingDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="29"/>
        <source>Loading Results</source>
        <translation>Cargando resultados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="43"/>
        <source>Opening results...</source>
        <translation>Abriendo resultados...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsLoadingDialog.py" line="55"/>
        <source>Preparing...</source>
        <translation>Preparando...</translation>
    </message>
</context>
<context>
    <name>ReviewOrNewPage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="70"/>
        <source>No file selected</source>
        <translation>Ningún archivo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="114"/>
        <source>Select ADIAT Results File</source>
        <translation>Seleccionar archivo de resultados ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="116"/>
        <source>XML Files (*.xml);;All Files (*)</source>
        <translation>Archivos XML (*.xml);;Todos los archivos (*)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="126"/>
        <source>File Name Warning</source>
        <translation>Advertencia de nombre de archivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/ReviewOrNewPage.py" line="128"/>
        <source>The selected file does not appear to be an ADIAT_Data.xml result or an ADIAT_Search project file.

Do you want to continue with this file?</source>
        <translation>El archivo seleccionado no parece ser un resultado ADIAT_Data.xml ni un archivo de proyecto ADIAT_Search.

¿Desea continuar con este archivo?</translation>
    </message>
</context>
<context>
    <name>ReviewerNameDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="25"/>
        <source>Reviewer Name</source>
        <translation>Nombre del revisor</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="45"/>
        <source>Review Tracking</source>
        <translation>Seguimiento de revisión</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="51"/>
        <source>Enter your name to track your review activity.
This helps coordinate reviews across multiple reviewers.</source>
        <translation>Introduzca su nombre para realizar el seguimiento de su actividad de revisión.
Esto ayuda a coordinar las revisiones entre varios revisores.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="60"/>
        <source>Your Name:</source>
        <translation>Su nombre:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="64"/>
        <source>Enter your name</source>
        <translation>Introduzca su nombre</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="65"/>
        <source>Enter your full name or identifier for review tracking</source>
        <translation>Introduzca su nombre completo o identificador para el seguimiento de revisión</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="71"/>
        <source>Remember my name</source>
        <translation>Recordar mi nombre</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="74"/>
        <source>Save your name for future review sessions.
You can change it later in Preferences or by clicking the reviewer name in the viewer.</source>
        <translation>Guarde su nombre para futuras sesiones de revisión.
Puede cambiarlo más tarde en Preferencias o haciendo clic en el nombre del revisor en el visor.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="86"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="91"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="123"/>
        <source>Name Required</source>
        <translation>Nombre requerido</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ReviewerNameDialog.py" line="124"/>
        <source>Please enter your name to continue.</source>
        <translation>Introduzca su nombre para continuar.</translation>
    </message>
</context>
<context>
    <name>ScanProgressDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ResultsFolderDialog.py" line="51"/>
        <source>Scanning for Results</source>
        <translation>Escaneando en busca de resultados</translation>
    </message>
</context>
<context>
    <name>SimilarityGalleryView</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="172"/>
        <source>Reference</source>
        <translation>Referencia</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/AOISimilarityResultsDialog.py" line="181"/>
        <source>Unknown</source>
        <translation>Desconocido</translation>
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
        <translation>Coordenadas GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="45"/>
        <source>Relative Altitude</source>
        <translation>Altitud relativa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="46"/>
        <source>Gimbal Orientation</source>
        <translation>Orientación del gimbal</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="47"/>
        <source>Estimated Average GSD</source>
        <translation>GSD media estimada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="48"/>
        <source>Temperature</source>
        <translation>Temperatura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="49"/>
        <source>Color Values</source>
        <translation>Valores de color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="50"/>
        <source>Drone Orientation</source>
        <translation>Orientación del dron</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="51"/>
        <source>Grid Review</source>
        <translation>Revisión por cuadrícula</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="116"/>
        <source>Error Loading Images</source>
        <translation>Error al cargar las imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="122"/>
        <source>No active images available.</source>
        <translation>No hay imágenes activas disponibles.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/status/StatusController.py" line="126"/>
        <source>No other images available.</source>
        <translation>No hay otras imágenes disponibles.</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="90"/>
        <source>Are you primarily looking for a person?</source>
        <translation>¿Está buscando principalmente a una persona?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="156"/>
        <source>Do you know a distinctive target color?</source>
        <translation>¿Conoce un color distintivo del objetivo?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="181"/>
        <source>Color Detection</source>
        <translation>Detección de color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="182"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Anomalía de color y detección de movimiento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="183"/>
        <source>AI Person Detector</source>
        <translation>Detector de personas con IA</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="186"/>
        <source>Selected Algorithm: {algorithm}</source>
        <translation>Algoritmo seleccionado: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmPage.py" line="191"/>
        <source>{result}
Secondary Recommendation: {secondary}</source>
        <translation>{result}
Recomendación secundaria: {secondary}</translation>
    </message>
</context>
<context>
    <name>StreamAlgorithmParametersPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="180"/>
        <source>Color Detection</source>
        <translation>Detección de color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="181"/>
        <source>Color Anomaly &amp; Motion Detection</source>
        <translation>Anomalía de color y detección de movimiento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="182"/>
        <source>AI Person Detector</source>
        <translation>Detector de personas con IA</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="189"/>
        <source>Algorithm</source>
        <translation>Algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamAlgorithmParametersPage.py" line="191"/>
        <source>{algorithm} Parameters</source>
        <translation>Parámetros de {algorithm}</translation>
    </message>
</context>
<context>
    <name>StreamConnectionPage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="92"/>
        <source>Click Scan to find devices...</source>
        <translation>Haga clic en Escanear para buscar dispositivos...</translation>
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
        <translation>Elija el archivo de vídeo que desea analizar. Use Examinar para elegir un archivo del disco.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="268"/>
        <source>Video File:</source>
        <translation>Archivo de vídeo:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="269"/>
        <source>Click Browse to select a video file...</source>
        <translation>Haga clic en Examinar para seleccionar un archivo de vídeo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="275"/>
        <source>Click Scan to detect available capture devices, then select one from the dropdown.</source>
        <translation>Haga clic en Escanear para detectar los dispositivos de captura disponibles y luego seleccione uno del menú desplegable.</translation>
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
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="284"/>
        <source>Enter the RTMP URL provided by your streaming server (rtmp://server:port/app/key).</source>
        <translation>Introduzca la URL RTMP proporcionada por su servidor de transmisión (rtmp://servidor:puerto/app/clave).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="286"/>
        <source>Stream URL:</source>
        <translation>URL de transmisión:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="287"/>
        <source>rtmp://server:port/app/streamKey</source>
        <translation>rtmp://servidor:puerto/app/claveTransmisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="298"/>
        <source>OpenCV not available</source>
        <translation>OpenCV no disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="304"/>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="307"/>
        <source>Scanning...</source>
        <translation>Escaneando...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="331"/>
        <source>Scan</source>
        <translation>Escanear</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="337"/>
        <source>No capture devices found</source>
        <translation>No se encontraron dispositivos de captura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="344"/>
        <source>Device {index} ({backend})</source>
        <translation>Dispositivo {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="383"/>
        <source>Select Video File</source>
        <translation>Seleccionar archivo de vídeo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamConnectionPage.py" line="386"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;All Files (*)</source>
        <translation>Archivos de vídeo (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm);;Todos los archivos (*)</translation>
    </message>
</context>
<context>
    <name>StreamControlWidget</name>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="838"/>
        <source>Stream Connection</source>
        <translation>Conexión de transmisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="840"/>
        <source>Configure and connect to video source (file, HDMI capture, or RTMP stream)</source>
        <translation>Configurar y conectar a la fuente de vídeo (archivo, captura HDMI o transmisión RTMP)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="845"/>
        <source>Stream Type:</source>
        <translation>Tipo de transmisión:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="847"/>
        <source>File</source>
        <translation>Archivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="848"/>
        <source>HDMI Capture</source>
        <translation>Captura HDMI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="849"/>
        <source>RTMP Stream</source>
        <translation>Transmisión RTMP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="852"/>
        <source>Select the type of video source:
• File: Pre-recorded video file with timeline controls
• HDMI Capture: Live capture from HDMI capture device
• RTMP Stream: Real-time streaming from RTMP/HTTP source</source>
        <translation>Seleccione el tipo de fuente de vídeo:
• Archivo: Archivo de vídeo pregrabado con controles de línea de tiempo
• Captura HDMI: Captura en vivo desde dispositivo de captura HDMI
• Transmisión RTMP: Transmisión en tiempo real desde fuente RTMP/HTTP</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="861"/>
        <source>Stream URL/Path:</source>
        <translation>URL/ruta de transmisión:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="868"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1067"/>
        <source>Click to browse for video file...</source>
        <translation>Haga clic para buscar un archivo de vídeo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="872"/>
        <source>Enter or browse for the video source:
• File: Click to browse for video file (MP4, AVI, MOV, etc.)
• RTMP Stream: Enter RTMP URL (rtmp://server:port/app/stream)</source>
        <translation>Introduzca o busque la fuente de vídeo:
• Archivo: Haga clic para buscar un archivo de vídeo (MP4, AVI, MOV, etc.)
• Transmisión RTMP: Introduzca la URL RTMP (rtmp://servidor:puerto/app/transmisión)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="881"/>
        <source>Select HDMI capture device</source>
        <translation>Seleccionar dispositivo de captura HDMI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="883"/>
        <source>Scanning for devices...</source>
        <translation>Escaneando en busca de dispositivos...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="887"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1019"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="891"/>
        <source>Open file browser to select a video file for analysis.
Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</source>
        <translation>Abrir el explorador de archivos para seleccionar un archivo de vídeo para analizar.
Formatos compatibles: MP4, AVI, MOV, MKV, FLV, WMV, M4V, 3GP, WebM</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="898"/>
        <source>Scan...</source>
        <translation>Escanear...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="900"/>
        <source>Scan for available HDMI capture devices</source>
        <translation>Escanear en busca de dispositivos de captura HDMI disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="907"/>
        <source>Connect</source>
        <translation>Conectar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="910"/>
        <source>Connect to the specified video source and begin processing.</source>
        <translation>Conectar a la fuente de vídeo especificada e iniciar el procesamiento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="912"/>
        <source>Disconnect</source>
        <translation>Desconectar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="916"/>
        <source>Disconnect from the current video source and stop processing.</source>
        <translation>Desconectar de la fuente de vídeo actual y detener el procesamiento.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="923"/>
        <source>Status: Disconnected</source>
        <translation>Estado: Desconectado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="925"/>
        <source>Current connection status</source>
        <translation>Estado de conexión actual</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="928"/>
        <source>Performance</source>
        <translation>Rendimiento</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="929"/>
        <source>Real-time performance metrics</source>
        <translation>Métricas de rendimiento en tiempo real</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="933"/>
        <source>Video: --</source>
        <translation>Vídeo: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="934"/>
        <source>Original video resolution</source>
        <translation>Resolución original del vídeo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="935"/>
        <source>Processing: --</source>
        <translation>Procesando: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="937"/>
        <source>Resolution used for detection processing</source>
        <translation>Resolución usada para el procesamiento de detección</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="941"/>
        <source>Source FPS: --</source>
        <translation>FPS de origen: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="942"/>
        <source>Source frame rate and the applied processing cadence</source>
        <translation>Tasa de fotogramas de origen y cadencia de procesamiento aplicada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="943"/>
        <source>Proc FPS: --</source>
        <translation>FPS de proc.: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="945"/>
        <source>Actual frames per second being processed</source>
        <translation>Fotogramas por segundo reales que se están procesando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="949"/>
        <source>Time: -- ms</source>
        <translation>Tiempo: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="951"/>
        <source>Time in milliseconds to process each frame</source>
        <translation>Tiempo en milisegundos para procesar cada fotograma</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="953"/>
        <source>Latency: -- ms</source>
        <translation>Latencia: -- ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="955"/>
        <source>End-to-end latency from frame capture to display</source>
        <translation>Latencia de extremo a extremo desde la captura del fotograma hasta la visualización</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="959"/>
        <source>Frames: --</source>
        <translation>Fotogramas: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="960"/>
        <source>Total number of frames processed</source>
        <translation>Número total de fotogramas procesados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="961"/>
        <source>Detections: --</source>
        <translation>Detecciones: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="962"/>
        <source>Number of detections in current frame</source>
        <translation>Número de detecciones en el fotograma actual</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="976"/>
        <source>Recording</source>
        <translation>Grabando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="981"/>
        <source>Start Recording</source>
        <translation>Iniciar grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="984"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Iniciar la grabación de la transmisión de vídeo con superposiciones de detección.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="986"/>
        <source>Stop Recording</source>
        <translation>Detener grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="989"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Detener la grabación actual y guardarla en un archivo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="996"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1195"/>
        <source>Status: Not Recording</source>
        <translation>Estado: No se está grabando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="999"/>
        <source>Current recording status and output file path</source>
        <translation>Estado de grabación actual y ruta del archivo de salida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1003"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1202"/>
        <source>Duration: --</source>
        <translation>Duración: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1005"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Estadísticas de grabación: Duración, FPS, fotogramas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1014"/>
        <source>Save to:</source>
        <translation>Guardar en:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1017"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Directorio donde se guardarán las grabaciones de vídeo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1021"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Elija una carpeta para almacenar las grabaciones.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1075"/>
        <source>rtmp://server:port/app/stream</source>
        <translation>rtmp://servidor:puerto/app/transmisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1092"/>
        <source>Invalid Device</source>
        <translation>Dispositivo no válido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1093"/>
        <source>Please select a valid HDMI capture device.</source>
        <translation>Seleccione un dispositivo de captura HDMI válido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1105"/>
        <source>Invalid URL</source>
        <translation>URL no válida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1106"/>
        <source>Please enter a valid stream URL.</source>
        <translation>Introduzca una URL de transmisión válida.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1123"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1144"/>
        <source>Status: {message}</source>
        <translation>Estado: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1182"/>
        <source>Status: Recording</source>
        <translation>Estado: Grabando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1186"/>
        <source>Output: {value}</source>
        <translation>Salida: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1199"/>
        <source>Duration: {value}</source>
        <translation>Duración: {value}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1228"/>
        <source>Select Recording Directory</source>
        <translation>Seleccionar directorio de grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1239"/>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1242"/>
        <source>Scanning...</source>
        <translation>Escaneando...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1266"/>
        <source>Scan</source>
        <translation>Escanear</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1272"/>
        <source>No capture devices found</source>
        <translation>No se encontraron dispositivos de captura</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1279"/>
        <source>Device {index} ({backend})</source>
        <translation>Dispositivo {index} ({backend})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1309"/>
        <source>Video: {width}x{height}</source>
        <translation>Vídeo: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1316"/>
        <source>Processing: {width}x{height}</source>
        <translation>Procesando: {width}x{height}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1332"/>
        <source>Source FPS: {source:.1f} (Applied {applied:.1f})</source>
        <translation>FPS de origen: {source:.1f} (Aplicado {applied:.1f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1339"/>
        <source>Source FPS: {fps:.1f}</source>
        <translation>FPS de origen: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1342"/>
        <source>Proc FPS: {fps:.1f}</source>
        <translation>FPS de proc.: {fps:.1f}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1350"/>
        <source>Time: {time:.1f} ms</source>
        <translation>Tiempo: {time:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1353"/>
        <source>Latency: {latency:.1f} ms</source>
        <translation>Latencia: {latency:.1f} ms</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1361"/>
        <source>Frames: {count}</source>
        <translation>Fotogramas: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1364"/>
        <source>Detections: {count}</source>
        <translation>Detecciones: {count}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1371"/>
        <source>Select Video File</source>
        <translation>Seleccionar archivo de vídeo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/shared_widgets.py" line="1374"/>
        <source>Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;All Files (*)</source>
        <translation>Archivos de vídeo (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp *.webm *.mpg *.mpeg *.ts *.mts *.m2ts);;Todos los archivos (*)</translation>
    </message>
</context>
<context>
    <name>StreamImageCapturePage</name>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="66"/>
        <source>Select Drone/Camera</source>
        <translation>Seleccionar dron/cámara</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="70"/>
        <source>No drones available</source>
        <translation>No hay drones disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="112"/>
        <source>Other</source>
        <translation>Otro</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="148"/>
        <source>Error loading drone data</source>
        <translation>Error al cargar los datos del dron</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="222"/>
        <source>-- (Invalid camera data)</source>
        <translation>-- (datos de cámara no válidos)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="423"/>
        <source>{sensor_name}: Sensor dimensions not available</source>
        <translation>{sensor_name}: dimensiones del sensor no disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="430"/>
        <source>-- (Missing camera data)</source>
        <translation>-- (faltan datos de cámara)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="431"/>
        <source>Unable to calculate GSD. Sensor dimensions are required.</source>
        <translation>No se puede calcular el GSD. Se requieren las dimensiones del sensor.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="437"/>
        <source>-- (Error)</source>
        <translation>-- (error)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="468"/>
        <source>Sensor {n}</source>
        <translation>Sensor {n}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamImageCapturePage.py" line="470"/>
        <source>Primary</source>
        <translation>Principal</translation>
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
        <translation>Sombrero, casco, bolsa de plástico</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Gato, mochila pequeña</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Mochila grande, perro mediano</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Saco de dormir, perro grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Barco pequeño, tienda de 2 personas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Coche/SUV, camioneta pequeña, tienda grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Casa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Más ejemplos:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>m²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/guidePages/StreamTargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>pies²</translation>
    </message>
</context>
<context>
    <name>StreamViewerWindow</name>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="105"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron v{version} - Patrocinado por TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="218"/>
        <source>Live View</source>
        <translation>Vista en vivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="223"/>
        <source>Gallery</source>
        <translation>Galería</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="264"/>
        <source>Menu</source>
        <translation>Menú</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="265"/>
        <source>Streaming Analysis Wizard</source>
        <translation>Asistente de análisis de transmisión</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="266"/>
        <source>Image Analysis</source>
        <translation>Análisis de imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="267"/>
        <source>Flight Viewer</source>
        <translation>Visor de vuelo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="268"/>
        <source>Preferences</source>
        <translation>Preferencias</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="278"/>
        <source>Help</source>
        <translation>Ayuda</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="279"/>
        <source>Check for Updates</source>
        <translation>Buscar actualizaciones</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="280"/>
        <source>Manual</source>
        <translation>Manual</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="281"/>
        <source>Community Forum</source>
        <translation>Foro de la comunidad</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="282"/>
        <source>YouTube Channel</source>
        <translation>Canal de YouTube</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="309"/>
        <source>Start Recording</source>
        <translation>Iniciar grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="312"/>
        <source>Start recording the video stream with detection overlays.</source>
        <translation>Iniciar la grabación de la transmisión de vídeo con superposiciones de detección.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="314"/>
        <source>Stop Recording</source>
        <translation>Detener grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="317"/>
        <source>Stop the current recording and save to file.</source>
        <translation>Detener la grabación actual y guardarla en un archivo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="324"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1908"/>
        <source>Status: Not Recording</source>
        <translation>Estado: No se está grabando</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="327"/>
        <source>Current recording status and output file path</source>
        <translation>Estado de grabación actual y ruta del archivo de salida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="331"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1910"/>
        <source>Duration: --</source>
        <translation>Duración: --</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="333"/>
        <source>Recording statistics: Duration, FPS, Frames</source>
        <translation>Estadísticas de grabación: Duración, FPS, fotogramas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="338"/>
        <source>Save to:</source>
        <translation>Guardar en:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="342"/>
        <source>Directory where video recordings will be saved.</source>
        <translation>Directorio donde se guardarán las grabaciones de vídeo.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="344"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="346"/>
        <source>Choose a folder to store recordings.</source>
        <translation>Elija una carpeta para almacenar las grabaciones.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="397"/>
        <source>Select Recording Directory</source>
        <translation>Seleccionar directorio de grabación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="417"/>
        <source>Algorithm:</source>
        <translation>Algoritmo:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="419"/>
        <source>Select which streaming detection algorithm to use</source>
        <translation>Seleccione qué algoritmo de detección de transmisión usar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="425"/>
        <source>Choose which streaming detection algorithm to run.
• Color Anomaly &amp; Motion Detection: fused anomaly detectors
• Color Detection: color-based highlighting</source>
        <translation>Elija qué algoritmo de detección de transmisión ejecutar.
• Anomalía de color y detección de movimiento: detectores de anomalías fusionados
• Detección de color: resaltado basado en color</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="460"/>
        <source>Gallery Threshold:</source>
        <translation>Umbral de galería:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="463"/>
        <source>Number of frames a detection must be seen before appearing in the Gallery tab</source>
        <translation>Número de fotogramas que debe verse una detección antes de aparecer en la pestaña Galería</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="470"/>
        <source> frames</source>
        <translation> fotogramas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="473"/>
        <source>Detections must be seen for this many consecutive frames
before appearing in the Gallery. Higher values reduce
false positives but delay detection appearance.</source>
        <translation>Las detecciones deben verse durante este número de fotogramas consecutivos
antes de aparecer en la Galería. Los valores más altos reducen
los falsos positivos, pero retrasan la aparición de la detección.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="534"/>
        <source>Device {index}</source>
        <translation>Dispositivo {index}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="728"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="747"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="761"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="784"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="798"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="812"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="826"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1944"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="729"/>
        <source>Failed to open Streaming Analysis Guide:
{error}</source>
        <translation>Error al abrir la Guía de análisis de transmisión:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="748"/>
        <source>Failed to open Image Analysis:
{error}</source>
        <translation>Error al abrir Análisis de imágenes:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="762"/>
        <source>Failed to open Preferences:
{error}</source>
        <translation>Error al abrir Preferencias:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="785"/>
        <source>Failed to open Flight Viewer:
{error}</source>
        <translation>No se pudo abrir el visor de vuelo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="799"/>
        <source>Failed to open Help documentation:
{error}</source>
        <translation>Error al abrir la documentación de Ayuda:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="813"/>
        <source>Failed to open Community Forum:
{error}</source>
        <translation>Error al abrir el Foro de la comunidad:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="827"/>
        <source>Failed to open YouTube Channel:
{error}</source>
        <translation>Error al abrir el canal de YouTube:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="937"/>
        <source>Loaded: {algorithm}</source>
        <translation>Cargado: {algorithm}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="953"/>
        <source>Error loading algorithm: {error}</source>
        <translation>Error al cargar el algoritmo: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="957"/>
        <source>Algorithm Load Error</source>
        <translation>Error al cargar el algoritmo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1465"/>
        <source>Algorithm switched to {label}</source>
        <translation>Algoritmo cambiado a {label}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1515"/>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1598"/>
        <source>No Stream Connected</source>
        <translation>No hay ninguna transmisión conectada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1532"/>
        <source>{state} - {message}</source>
        <translation>{state} - {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1533"/>
        <source>Connected</source>
        <translation>Conectado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1533"/>
        <source>Disconnected</source>
        <translation>Desconectado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1545"/>
        <source>✓ Connected: {message}</source>
        <translation>✓ Conectado: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1580"/>
        <source>✗ Disconnected: {message}</source>
        <translation>✗ Desconectado: {message}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1801"/>
        <source>No detections found.</source>
        <translation>No se encontraron detecciones.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1805"/>
        <source>Detection Results ({count} found):</source>
        <translation>Resultados de detección ({count} encontrados):</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1817"/>
        <source>#{index}: Type({cls}) Pos({x},{y}) Size({w}x{h})</source>
        <translation>n.º{index}: Tipo({cls}) Pos({x},{y}) Tamaño({w}x{h})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1827"/>
        <source>#{index}: Type({cls})</source>
        <translation>n.º{index}: Tipo({cls})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1832"/>
        <source> Conf({confidence:.2f})</source>
        <translation> Conf({confidence:.2f})</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1877"/>
        <source>Recording started: {path}</source>
        <translation>Grabación iniciada: {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1884"/>
        <source>Recording stopped</source>
        <translation>Grabación detenida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1901"/>
        <source>Status: Recording to {path}</source>
        <translation>Estado: Grabando a {path}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1924"/>
        <source>Duration: {duration:.1f}s | FPS: {fps:.1f} | Frames: {frames} | Queue: {queue}</source>
        <translation>Duración: {duration:.1f}s | FPS: {fps:.1f} | Fotogramas: {frames} | Cola: {queue}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="1942"/>
        <source>✗ Error: {error}</source>
        <translation>✗ Error: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2009"/>
        <source>Live Stream</source>
        <translation>Transmisión en vivo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamViewerWindow.py" line="2011"/>
        <source>Cannot seek in live stream.

Detection was first seen at frame {frame}.</source>
        <translation>No se puede buscar en una transmisión en vivo.

La detección se vio por primera vez en el fotograma {frame}.</translation>
    </message>
</context>
<context>
    <name>StreamingGuide</name>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="14"/>
        <source>Streaming Setup Guide</source>
        <translation>Guía de configuración de transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="51"/>
        <source>Connect to Your Stream</source>
        <translation>Conectar a su transmisión</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="115"/>
        <source>Pre-recorded video file with playback controls</source>
        <translation>Archivo de vídeo pregrabado con controles de reproducción</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="122"/>
        <source>File</source>
        <translation>Archivo</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="161"/>
        <source>Live HDMI capture device (enter device index)</source>
        <translation>Dispositivo de captura HDMI en vivo (introduzca el índice del dispositivo)</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="168"/>
        <source>HDMI</source>
        <translation>HDMI</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="204"/>
        <source>Network stream via RTMP URL</source>
        <translation>Transmisión por red vía URL RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="211"/>
        <source>RTMP</source>
        <translation>RTMP</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="254"/>
        <source>File: Use local video files (MP4, MOV, etc.) with timeline controls.</source>
        <translation>Archivo: Use archivos de vídeo locales (MP4, MOV, etc.) con controles de línea de tiempo.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="269"/>
        <source>HDMI: Connect to a live HDMI capture device.</source>
        <translation>HDMI: Conectar a un dispositivo de captura HDMI en vivo.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="284"/>
        <source>RTMP: Connect to a live network stream (rtmp://server:port/app/key).</source>
        <translation>RTMP: Conectar a una transmisión de red en vivo (rtmp://servidor:puerto/app/clave).</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="328"/>
        <source>Connection Details</source>
        <translation>Detalles de conexión</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="347"/>
        <source>Provide the path or URL for your selected stream type. You can optionally auto-connect when the guide is finished.</source>
        <translation>Proporcione la ruta o URL del tipo de transmisión seleccionado. Opcionalmente puede conectar automáticamente cuando termine la guía.</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="364"/>
        <source>Stream URL/Path:</source>
        <translation>URL/ruta de transmisión:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="373"/>
        <source>Click Browse to select a file or enter a URL...</source>
        <translation>Haga clic en Examinar para seleccionar un archivo o introducir una URL...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="385"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="399"/>
        <source>Auto Connect:</source>
        <translation>Conexión automática:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="411"/>
        <source>Connect as soon as the guide finishes</source>
        <translation>Conectar en cuanto termine la guía</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="423"/>
        <source>Capture Devices:</source>
        <translation>Dispositivos de captura:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="444"/>
        <source>Scan...</source>
        <translation>Escanear...</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="484"/>
        <source>Processing Resolution:</source>
        <translation>Resolución de procesamiento:</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="532"/>
        <source>Video Capture Information</source>
        <translation>Información de captura de vídeo</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="554"/>
        <source>What drone/camera was used to capture the video?</source>
        <translation>¿Qué dron/cámara se usó para capturar el vídeo?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="584"/>
        <source>At what above ground level (AGL) altitude was the drone flying?</source>
        <translation>¿A qué altitud sobre el nivel del suelo (AGL) volaba el dron?</translation>
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
        <translation>Distancia de muestreo del suelo (GSD) estimada:</translation>
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
        <translation>Tamaño del objetivo de búsqueda</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="774"/>
        <source>Approximately how large are the objects you&apos;re wanting to identify?</source>
        <translation>¿Aproximadamente qué tamaño tienen los objetos que desea identificar?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="805"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;More Examples:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 sqft – Hat, Helmet, Plastic Bag &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 sqft – Cat, Daypack &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 sqft – Large Pack, Medium Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 sqft – Sleeping Bag, Large Dog &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 sqft – Small Boat, 2-Person Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 sqft – Car/SUV, Small Pickup Truck, Large Tent &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 sqft – House &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;&lt;p&gt;&lt;span style=&quot; font-weight:700;&quot;&gt;Más ejemplos:&lt;/span&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1 pie² – Sombrero, casco, bolsa de plástico &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;3 pies² – Gato, mochila pequeña &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;6 pies² – Mochila grande, perro mediano &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;12 pies² – Saco de dormir, perro grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;50 pies² – Barco pequeño, tienda de 2 personas &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;200 pies² – Coche/SUV, camioneta pequeña, tienda grande &lt;/li&gt;&lt;li&gt;&amp;nbsp;&amp;nbsp;1000 pies² – Casa &lt;/li&gt;&lt;/ul&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="847"/>
        <source>Detection &amp; Processing</source>
        <translation>Detección y procesamiento</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="869"/>
        <source>Are you looking for specific colors?</source>
        <translation>¿Está buscando colores específicos?</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="914"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="945"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1018"/>
        <source>Reset</source>
        <translation>Restablecer</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1091"/>
        <source>Algorithm Parameters</source>
        <translation>Parámetros del algoritmo</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1126"/>
        <source>Close</source>
        <translation>Cerrar</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1138"/>
        <source>Skip this streaming guide next time</source>
        <translation>Omitir esta guía de transmisión la próxima vez</translation>
    </message>
    <message>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1166"/>
        <source>Back</source>
        <translation>Atrás</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="138"/>
        <location filename="../resources/views/streaming/StreamingGuide.ui" line="1178"/>
        <source>Continue</source>
        <translation>Continuar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="84"/>
        <source>ADIAT Streaming Setup Guide</source>
        <translation>Guía de configuración de transmisión ADIAT</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/streaming/StreamingGuide.py" line="136"/>
        <source>Open Stream Viewer</source>
        <translation>Abrir visor de transmisión</translation>
    </message>
</context>
<context>
    <name>StreamingVideoDisplay</name>
    <message>
        <location filename="../app/core/views/streaming/components/StreamingVideoDisplay.py" line="66"/>
        <source>No Stream Connected</source>
        <translation>No hay ninguna transmisión conectada</translation>
    </message>
</context>
<context>
    <name>TargetSizePage</name>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="79"/>
        <source>Hat, Helmet, Plastic Bag</source>
        <translation>Sombrero, casco, bolsa de plástico</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="80"/>
        <source>Cat, Daypack</source>
        <translation>Gato, mochila pequeña</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="81"/>
        <source>Large Pack, Medium Dog</source>
        <translation>Mochila grande, perro mediano</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="82"/>
        <source>Sleeping Bag, Large Dog</source>
        <translation>Saco de dormir, perro grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="83"/>
        <source>Small Boat, 2-Person Tent</source>
        <translation>Barco pequeño, tienda de 2 personas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="84"/>
        <source>Car/SUV, Small Pickup Truck, Large Tent</source>
        <translation>Coche/SUV, camioneta pequeña, tienda grande</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="85"/>
        <source>House</source>
        <translation>Casa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="90"/>
        <source>More Examples:</source>
        <translation>Más ejemplos:</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="103"/>
        <source>sqm</source>
        <translation>m²</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/guidePages/TargetSizePage.py" line="106"/>
        <source>sqft</source>
        <translation>pies²</translation>
    </message>
</context>
<context>
    <name>TeamPlanningController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="47"/>
        <source>No Flagged AOIs</source>
        <translation>Ningún AOI marcado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="49"/>
        <source>There are no flagged AOIs to assign.

Flag at least one AOI in the viewer before using Plan Verification.</source>
        <translation>No hay AOI marcados para asignar.

Marque al menos un AOI en el visor antes de usar la Verificación del plan.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="210"/>
        <source>No Team Selected</source>
        <translation>Ningún equipo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="211"/>
        <source>Select a target team (or &apos;Unassigned&apos;) in the list first.</source>
        <translation>Primero seleccione un equipo objetivo (o &apos;Sin asignar&apos;) en la lista.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="219"/>
        <source>No AOIs Selected</source>
        <translation>Ningún AOI seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="221"/>
        <source>Select one or more AOIs on the map first.
Click on markers, or use Rectangle Select for area selection.</source>
        <translation>Primero seleccione uno o más AOI en el mapa.
Haga clic en los marcadores o use Selección rectangular para selección por área.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="300"/>
        <source>No AOIs</source>
        <translation>Sin AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="301"/>
        <source>Team &apos;{name}&apos; has no assigned AOIs.</source>
        <translation>El equipo &apos;{name}&apos; no tiene AOI asignados.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="312"/>
        <source>Save Team PDF</source>
        <translation>Guardar PDF del equipo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="314"/>
        <source>PDF files (*.pdf)</source>
        <translation>Archivos PDF (*.pdf)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="326"/>
        <source>Select Export Folder</source>
        <translation>Seleccionar carpeta de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="336"/>
        <source>Exporting Team PDFs</source>
        <translation>Exportando PDF del equipo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="354"/>
        <source>Generating PDF for {name}...</source>
        <translation>Generando PDF para {name}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="365"/>
        <source>Generating master summary...</source>
        <translation>Generando resumen maestro...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="373"/>
        <source>Export complete</source>
        <translation>Exportación completada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="380"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="426"/>
        <source>Export Error</source>
        <translation>Error de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="381"/>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="427"/>
        <source>PDF generation failed: {error}</source>
        <translation>Error en la generación del PDF: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="389"/>
        <source>Export Complete</source>
        <translation>Exportación completada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="390"/>
        <source>Team PDFs saved to:
{folder}</source>
        <translation>PDF del equipo guardados en:
{folder}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="406"/>
        <source>Generating PDF Report</source>
        <translation>Generando informe PDF</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="414"/>
        <source>Done</source>
        <translation>Listo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="418"/>
        <source>Success</source>
        <translation>Éxito</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/TeamPlanningController.py" line="419"/>
        <source>PDF report generated successfully!</source>
        <translation>¡Informe PDF generado correctamente!</translation>
    </message>
</context>
<context>
    <name>TeamPlanningDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="55"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="65"/>
        <source>Plan Verification</source>
        <translation>Verificación del plan</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="86"/>
        <source>Zoom In (+)</source>
        <translation>Acercar (+)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="88"/>
        <source>Zoom Out (-)</source>
        <translation>Alejar (-)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="90"/>
        <source>Fit All (F)</source>
        <translation>Ajustar todo (F)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="93"/>
        <source>Rectangle Select</source>
        <translation>Selección rectangular</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="96"/>
        <source>Draw a rectangle on the map to select multiple AOIs</source>
        <translation>Dibuje un rectángulo en el mapa para seleccionar varios AOI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="100"/>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="316"/>
        <source>Satellite View</source>
        <translation>Vista satélite</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="122"/>
        <source>Teams</source>
        <translation>Equipos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="124"/>
        <source>+ New</source>
        <translation>+ Nuevo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="125"/>
        <source>Create a new field team</source>
        <translation>Crear un nuevo equipo de campo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="127"/>
        <source>✕ Remove</source>
        <translation>✕ Eliminar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="128"/>
        <source>Remove the selected team</source>
        <translation>Eliminar el equipo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="143"/>
        <source>Assign Selection ▶</source>
        <translation>Asignar selección ▶</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="145"/>
        <source>Assign the selected AOIs on the map to the chosen team</source>
        <translation>Asignar los AOI seleccionados en el mapa al equipo elegido</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="158"/>
        <source>Team AOIs</source>
        <translation>AOI del equipo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="172"/>
        <source>Export Team PDF</source>
        <translation>Exportar PDF del equipo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="174"/>
        <source>Generate a PDF report for the selected team only</source>
        <translation>Generar un informe PDF solo para el equipo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="179"/>
        <source>Export All PDFs</source>
        <translation>Exportar todos los PDF</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="181"/>
        <source>Generate one PDF per team plus a master summary PDF</source>
        <translation>Generar un PDF por equipo más un PDF resumen maestro</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="195"/>
        <source>Click to select AOI • Ctrl+Click to multi-select • Use Rectangle Select for area selection • Scroll to zoom</source>
        <translation>Haga clic para seleccionar AOI • Ctrl+Clic para selección múltiple • Use Selección rectangular para selección por área • Rueda para acercar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="222"/>
        <source>Team</source>
        <translation>Equipo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>New Team</source>
        <translation>Nuevo equipo</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="239"/>
        <source>Team name:</source>
        <translation>Nombre del equipo:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="246"/>
        <source>Duplicate Name</source>
        <translation>Nombre duplicado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="247"/>
        <source>A team named &apos;{name}&apos; already exists.</source>
        <translation>Ya existe un equipo llamado &apos;{name}&apos;.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="265"/>
        <source>Unassigned</source>
        <translation>Sin asignar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="298"/>
        <source>No Team Selected</source>
        <translation>Ningún equipo seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="299"/>
        <source>Please select a team to export.</source>
        <translation>Seleccione un equipo para exportar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="305"/>
        <source>No Teams</source>
        <translation>Sin equipos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="306"/>
        <source>Create at least one team before exporting.</source>
        <translation>Cree al menos un equipo antes de exportar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TeamPlanningDialog.py" line="313"/>
        <source>Map View</source>
        <translation>Vista de mapa</translation>
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
        <translation>VUELO</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="147"/>
        <source>stale {age}s</source>
        <translation>sin actualizar {age}s</translation>
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
        <translation>RUM —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="188"/>
        <source>HDG {bearing:03d}° {cardinal}</source>
        <translation>RUM {bearing:03d}° {cardinal}</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="194"/>
        <location filename="../resources/views/flight/telemetry_hud.ui" line="98"/>
        <source>SPD —</source>
        <translation>VEL —</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="200"/>
        <source>SPD {value} mph</source>
        <translation>VEL {value} mph</translation>
    </message>
    <message>
        <location filename="../app/core/views/flight/TelemetryHud.py" line="203"/>
        <source>SPD {value} m/s</source>
        <translation>VEL {value} m/s</translation>
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
        <location filename="../app/core/views/components/LabeledSlider.py" line="259"/>
        <source>Very Conservative</source>
        <translation>Muy conservador</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="260"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="261"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="262"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/core/views/components/LabeledSlider.py" line="263"/>
        <source>Very Aggressive</source>
        <translation>Muy agresivo</translation>
    </message>
</context>
<context>
    <name>ThermalAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="29"/>
        <source>Type of thermal anomaly to detect in thermal imagery.
Determines whether to find hot spots, cold spots, or both.</source>
        <translation>Tipo de anomalía térmica a detectar en imágenes térmicas.
Determina si se buscan puntos calientes, fríos o ambos.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Tipo de anomalía:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="45"/>
        <source>Select the type of thermal anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to the mean temperature of its segment.
Use &quot;Above Mean&quot; for finding heat sources, &quot;Below Mean&quot; for cold objects.</source>
        <translation>Seleccione el tipo de anomalía térmica a detectar:
• Por encima o por debajo de la media: Detecta anomalías tanto calientes como frías (predeterminado)
• Por encima de la media: Solo detecta puntos calientes (temperaturas por encima del promedio)
• Por debajo de la media: Solo detecta puntos fríos (temperaturas por debajo del promedio)
El algoritmo compara la temperatura de cada píxel con la temperatura media de su segmento.
Use &quot;Por encima de la media&quot; para encontrar fuentes de calor, &quot;Por debajo de la media&quot; para objetos fríos.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="54"/>
        <source>Above or Below Mean</source>
        <translation>Por encima o por debajo de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="59"/>
        <source>Above Mean</source>
        <translation>Por encima de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="64"/>
        <source>Below Mean</source>
        <translation>Por debajo de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="77"/>
        <source>Temperature threshold for detecting thermal anomalies.
Measured in standard deviations from the mean temperature.</source>
        <translation>Umbral de temperatura para detectar anomalías térmicas.
Medido en desviaciones estándar desde la temperatura media.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="81"/>
        <source>Anomaly Threshold:</source>
        <translation>Umbral de anomalía:</translation>
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
        <translation>Establezca el umbral de detección de anomalías en desviaciones estándar.
• Rango: 0 a 7 desviaciones estándar
• Predeterminado: 4
Define qué tan diferente debe ser una temperatura de la media para ser detectada:
• Valores más bajos (1-2): Muy sensible, detecta diferencias sutiles de temperatura (más detecciones)
• Valores medios (3-5): Detección equilibrada (recomendado para la mayoría de los casos)
• Valores más altos (6-7): Solo detecta diferencias extremas de temperatura (menos detecciones)
Ejemplo: Un valor de 4 detecta píxeles a 4 desviaciones estándar por encima/debajo de la temperatura media.</translation>
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
        <translation>Número de segmentos en los que dividir cada imagen térmica para el análisis.
Cada segmento se analiza independientemente para detectar anomalías térmicas locales.
Impacto en el rendimiento:
• Mayor número de segmentos: AUMENTA el tiempo de procesamiento (más segmentos a analizar)
• Menor número de segmentos: REDUCE el tiempo de procesamiento (menos segmentos a analizar)
• 1 segmento: Procesamiento más rápido (analiza toda la imagen de una vez)
Un mayor número de segmentos mejora la detección en escenas con gradientes de temperatura.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomaly.ui" line="122"/>
        <source>Image Segments:</source>
        <translation>Segmentos de imagen:</translation>
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
        <translation>Seleccione el número de segmentos en los que dividir cada imagen térmica.
• Opciones: 1, 2, 4, 6, 9, 16, 25, 36 segmentos
• Predeterminado: 1 (analizar toda la imagen como un segmento)
El algoritmo calcula la temperatura media para cada segmento independientemente:
• 1 segmento: Análisis global de temperatura (mejor para escenas uniformes)
• Más segmentos: Análisis local de temperatura (mejor para fondos variados)
Un mayor número de segmentos mejora la detección en escenas con gradientes de temperatura.
Recomendado: 4-9 segmentos para imágenes térmicas típicas de dron.</translation>
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
        <translation>¿Sus imágenes contienen escenas complejas con edificios, vehículos o cobertura del suelo antropogénica mixta?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="57"/>
        <source>No</source>
        <translation>No</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="72"/>
        <source>Yes</source>
        <translation>Sí</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="105"/>
        <source>What type of anomalies are you looking for?</source>
        <translation>¿Qué tipo de anomalías está buscando?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="122"/>
        <source>Warmer than surroundings</source>
        <translation>Más cálido que el entorno</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="134"/>
        <source>Cooler than surroundings</source>
        <translation>Más frío que el entorno</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="146"/>
        <source>Both</source>
        <translation>Ambos</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="185"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>¿Con qué agresividad debe ADIAT buscar anomalías?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalAnomalyWizard.ui" line="198"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: Un valor más alto encontrará más anomalías potenciales pero también puede aumentar los falsos positivos.</translation>
    </message>
</context>
<context>
    <name>ThermalAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="45"/>
        <source>Very 
Conservative</source>
        <translation>Muy 
conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="46"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="47"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="48"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalAnomaly/controllers/ThermalAnomalyWizardController.py" line="49"/>
        <source>Very 
Aggressive</source>
        <translation>Muy 
agresivo</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramChart</name>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="98"/>
        <source>No histogram data available</source>
        <translation>No hay datos de histograma disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="434"/>
        <source>All Pixels</source>
        <translation>Todos los píxeles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="445"/>
        <location filename="../app/core/views/images/viewer/widgets/ThermalHistogramChart.py" line="456"/>
        <source>AOI Pixels</source>
        <translation>Píxeles del AOI</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="32"/>
        <source>Thermal Histogram Unavailable</source>
        <translation>Histograma térmico no disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/ThermalHistogramController.py" line="33"/>
        <source>No thermal temperature data is available for the current image.</source>
        <translation>No hay datos de temperatura térmica disponibles para la imagen actual.</translation>
    </message>
</context>
<context>
    <name>ThermalHistogramDialog</name>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="14"/>
        <source>Thermal Histogram</source>
        <translation>Histograma térmico</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="23"/>
        <source>Gray bars show the full temperature distribution, orange bars mark AOI/anomaly bins, and hovering the chart highlights matching pixels in the image.</source>
        <translation>Las barras grises muestran la distribución completa de temperatura, las barras naranjas marcan los bins de AOI/anomalías y al pasar el cursor sobre el gráfico se resaltan los píxeles coincidentes en la imagen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="32"/>
        <source>Drag on the histogram to zoom. Double-click or use Reset Zoom to return to the full range.</source>
        <translation>Arrastre sobre el histograma para acercar. Haga doble clic o use Restablecer zoom para volver al rango completo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="52"/>
        <source>Reset Zoom</source>
        <translation>Restablecer zoom</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="64"/>
        <source>Visible Temperature Range</source>
        <translation>Rango de temperatura visible</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="59"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="75"/>
        <source>Minimum: --</source>
        <translation>Mínimo: --</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="60"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="82"/>
        <source>Maximum: --</source>
        <translation>Máximo: --</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="105"/>
        <source>Reset Range</source>
        <translation>Restablecer rango</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="61"/>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="126"/>
        <location filename="../resources/views/images/viewer/ThermalHistogramDialog.ui" line="117"/>
        <source>Hover over the histogram to inspect a temperature band.</source>
        <translation>Pase el cursor sobre el histograma para inspeccionar una banda de temperatura.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="30"/>
        <source>No thermal histogram data available</source>
        <translation>No hay datos de histograma térmico disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="131"/>
        <source>Hover band: {lower:.1f} to {upper:.1f} °{unit}</source>
        <translation>Banda bajo el cursor: {lower:.1f} a {upper:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="141"/>
        <source>Minimum: {minimum:.1f} °{unit}</source>
        <translation>Mínimo: {minimum:.1f} °{unit}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ThermalHistogramDialog.py" line="147"/>
        <source>Maximum: {maximum:.1f} °{unit}</source>
        <translation>Máximo: {maximum:.1f} °{unit}</translation>
    </message>
</context>
<context>
    <name>ThermalRange</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
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
        <translation>Umbral de temperatura mínima para la detección en imágenes térmicas.
• Rango: -30°C a 50°C
• Predeterminado: 35°C
Define el límite inferior del rango de detección de temperatura:
• Valores más bajos: AUMENTAN las detecciones - acepta objetos más fríos
• Valores más altos: REDUCEN las detecciones - solo se detectan objetos más cálidos
Combinado con la Temp. máxima crea un rango de detección (p. ej., 35-40°C para la temperatura corporal humana).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="38"/>
        <source>Minimum Temp (°C)</source>
        <translation>Temp. mínima (°C)</translation>
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
        <translation>Establezca la temperatura mínima para la detección en Celsius.
• Rango: -30°C a 50°C
• Predeterminado: 35°C
Se detectarán los píxeles con temperaturas iguales o superiores a este umbral.
• Valores más bajos: Detecta objetos más fríos (más detecciones)
• Valores más altos: Solo detecta objetos más cálidos (menos detecciones)
Nota: La temperatura se muestra en Celsius, convertida según la configuración de Preferencias.
Úselo para encontrar objetos dentro de un rango de temperatura específico (p. ej., personas 35-40°C).</translation>
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
        <translation>Umbral de temperatura máxima para la detección en imágenes térmicas.
• Rango: -30°C a 93°C
• Predeterminado: 40°C
Define el límite superior del rango de detección de temperatura:
• Valores más bajos: REDUCEN las detecciones - solo se detectan objetos más fríos
• Valores más altos: AUMENTAN las detecciones - acepta objetos más cálidos
Combinado con la Temp. mínima crea un rango de detección (p. ej., 35-40°C para la temperatura corporal humana).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalRange.ui" line="103"/>
        <source>Maximum Temp (°C)</source>
        <translation>Temp. máxima (°C)</translation>
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
        <translation>Establezca la temperatura máxima para la detección en Celsius.
• Rango: -30°C a 93°C
• Predeterminado: 40°C
Se detectarán los píxeles con temperaturas iguales o inferiores a este umbral.
• Valores más bajos: Solo detecta objetos más fríos (menos detecciones)
• Valores más altos: Detecta objetos más cálidos (más detecciones)
Nota: La temperatura se muestra en Celsius, convertida según la configuración de Preferencias.
La detección se produce para píxeles entre las temperaturas mínima y máxima (ambas inclusive).</translation>
    </message>
</context>
<context>
    <name>ThermalRangeController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="108"/>
        <source>Minimum Temp ({degree} F)</source>
        <translation>Temp. mínima ({degree} F)</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalRange/controllers/ThermalRangeController.py" line="114"/>
        <source>Maximum Temp ({degree} F)</source>
        <translation>Temp. máxima ({degree} F)</translation>
    </message>
</context>
<context>
    <name>ThermalRangeWizard</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalRangeWizard.ui" line="34"/>
        <source>What range of temperatures should ADIAT look for?</source>
        <translation>¿Qué rango de temperaturas debe buscar ADIAT?</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomaly</name>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="14"/>
        <source>Form</source>
        <translation>Formulario</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="29"/>
        <source>Type of local thermal residual anomaly to detect in radiometric imagery.
Determines whether to find warm anomalies, cool anomalies, or both.</source>
        <translation>Tipo de anomalía térmica residual local a detectar en imágenes radiométricas.
Determina si se buscan anomalías cálidas, frías o ambas.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="33"/>
        <source>Anomaly Type:</source>
        <translation>Tipo de anomalía:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="45"/>
        <source>Select the type of thermal residual anomaly to detect:
• Above or Below Mean: Detects both hot and cold anomalies (default)
• Above Mean: Only detects hot spots (temperatures above average)
• Below Mean: Only detects cold spots (temperatures below average)
The algorithm compares each pixel&apos;s temperature to its local background estimate.</source>
        <translation>Seleccione el tipo de anomalía térmica residual a detectar:
• Por encima o por debajo de la media: Detecta anomalías tanto calientes como frías (predeterminado)
• Por encima de la media: Solo detecta puntos calientes (temperaturas por encima del promedio)
• Por debajo de la media: Solo detecta puntos fríos (temperaturas por debajo del promedio)
El algoritmo compara la temperatura de cada píxel con la estimación de su fondo local.</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="53"/>
        <source>Above or Below Mean</source>
        <translation>Por encima o por debajo de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="58"/>
        <source>Above Mean</source>
        <translation>Por encima de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="63"/>
        <source>Below Mean</source>
        <translation>Por debajo de la media</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="92"/>
        <source>Detection sensitivity for thermal residual anomalies.
• Range: 1 to 10
• Default: 5
Lower values are more conservative (fewer detections).
Higher values are more aggressive (more detections).</source>
        <translation>Sensibilidad de detección para anomalías térmicas residuales.
• Rango: 1 a 10
• Predeterminado: 5
Los valores más bajos son más conservadores (menos detecciones).
Los valores más altos son más agresivos (más detecciones).</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="99"/>
        <source>Sensitivity:</source>
        <translation>Sensibilidad:</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="112"/>
        <source>Adjust detection sensitivity for local thermal residual anomalies.
• 1-3: Conservative
• 4-6: Moderate
• 7-10: Aggressive</source>
        <translation>Ajuste la sensibilidad de detección para anomalías térmicas residuales locales.
• 1-3: Conservador
• 4-6: Moderado
• 7-10: Agresivo</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomaly.ui" line="153"/>
        <source>Current sensitivity level for residual anomaly detection.</source>
        <translation>Nivel de sensibilidad actual para la detección de anomalías residuales.</translation>
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
        <translation>¿Qué tipo de anomalías está buscando?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="54"/>
        <source>Warmer than surroundings</source>
        <translation>Más cálido que el entorno</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="66"/>
        <source>Cooler than surroundings</source>
        <translation>Más frío que el entorno</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="78"/>
        <source>Both</source>
        <translation>Ambos</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="117"/>
        <source>How aggressively should ADIAT be searching for anomalies?</source>
        <translation>¿Con qué agresividad debe ADIAT buscar anomalías?</translation>
    </message>
    <message>
        <location filename="../resources/views/algorithms/ThermalResidualAnomalyWizard.ui" line="130"/>
        <source>Note: A higher setting will find more potential anomalies but may also increase false positives.</source>
        <translation>Nota: Un valor más alto encontrará más anomalías potenciales pero también puede aumentar los falsos positivos.</translation>
    </message>
</context>
<context>
    <name>ThermalResidualAnomalyWizardController</name>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="33"/>
        <source>Very 
Conservative</source>
        <translation>Muy 
conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="34"/>
        <source>Conservative</source>
        <translation>Conservador</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="35"/>
        <source>Moderate</source>
        <translation>Moderado</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="36"/>
        <source>Aggressive</source>
        <translation>Agresivo</translation>
    </message>
    <message>
        <location filename="../app/algorithms/images/ThermalResidualAnomaly/controllers/ThermalResidualAnomalyWizardController.py" line="37"/>
        <source>Very 
Aggressive</source>
        <translation>Muy 
agresivo</translation>
    </message>
</context>
<context>
    <name>TileFetchController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="150"/>
        <source>Invalid Area</source>
        <translation>Área no válida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="151"/>
        <source>Please enter a valid bounding box.</source>
        <translation>Introduzca un cuadro delimitador válido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="154"/>
        <source>No Output Folder</source>
        <translation>Sin carpeta de salida</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="155"/>
        <source>Please choose an output folder.</source>
        <translation>Elija una carpeta de salida.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="158"/>
        <source>No Dataset</source>
        <translation>Sin conjunto de datos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="159"/>
        <source>Please select at least one dataset.</source>
        <translation>Seleccione al menos un conjunto de datos.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="286"/>
        <source>No GPS Found</source>
        <translation>No se encontró GPS</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="287"/>
        <source>No GPS positions were found in the {source} images.</source>
        <translation>No se encontraron posiciones GPS en las imágenes de {source}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="302"/>
        <source>Select image folder</source>
        <translation>Seleccionar carpeta de imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="311"/>
        <source>No Images</source>
        <translation>Sin imágenes</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="312"/>
        <source>No images were found in the selected folder.</source>
        <translation>No se encontraron imágenes en la carpeta seleccionada.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="358"/>
        <source>Replace Canopy Source?</source>
        <translation>¿Reemplazar la fuente de dosel?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="359"/>
        <source>A LANDFIRE canopy source is currently configured.

Register the downloaded Meta/WRI canopy tiles instead? (Your LANDFIRE files stay on disk; only the selected source changes.)</source>
        <translation>Actualmente hay configurada una fuente de dosel LANDFIRE.

¿Registrar en su lugar las teselas de dosel Meta/WRI descargadas? (Sus archivos LANDFIRE permanecen en el disco; solo cambia la fuente seleccionada.)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Elevation (DEM)</source>
        <translation>Elevación (MDE)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="368"/>
        <source>Canopy height</source>
        <translation>Altura del dosel</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="385"/>
        <source>{product}: cancelled before completion.</source>
        <translation>{product}: cancelado antes de completarse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="387"/>
        <source>{product}: {failed} tile(s) failed to download.</source>
        <translation>{product}: {failed} tesela(s) no se pudieron descargar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="390"/>
        <source>{product}: no data covers this area.</source>
        <translation>{product}: ningún dato cubre esta área.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="392"/>
        <source>{product}: nothing was downloaded.</source>
        <translation>{product}: no se descargó nada.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="399"/>
        <source>{product}: registered as the active source.</source>
        <translation>{product}: registrado como fuente activa.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="402"/>
        <source>{product}: NOT registered (no usable tiles).</source>
        <translation>{product}: NO registrado (sin teselas utilizables).</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="411"/>
        <source>Download Finished with Problems</source>
        <translation>Descarga finalizada con problemas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="417"/>
        <source>Download Complete</source>
        <translation>Descarga completa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="406"/>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="413"/>
        <source>Downloaded {count} tiles.</source>
        <translation>Se descargaron {count} teselas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="428"/>
        <source>Download Cancelled</source>
        <translation>Descarga cancelada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="429"/>
        <source>The download was cancelled. No tiles were registered.</source>
        <translation>La descarga se canceló. No se registró ninguna tesela.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="436"/>
        <source>Download Error</source>
        <translation>Error de descarga</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/TileFetchController.py" line="437"/>
        <source>Tile download failed:
{error}</source>
        <translation>Error al descargar las teselas:
{error}</translation>
    </message>
</context>
<context>
    <name>TileFetchDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="48"/>
        <source>Download Coverage Data</source>
        <translation>Descargar datos de cobertura</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="58"/>
        <source>Area of Interest (WGS84)</source>
        <translation>Área de interés (WGS84)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="68"/>
        <source>Fill area from</source>
        <translation>Rellenar área desde</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="73"/>
        <source>Fill the area from the loaded mission&apos;s image GPS, or from an image folder.</source>
        <translation>Rellenar el área a partir del GPS de las imágenes de la misión cargada, o desde una carpeta de imágenes.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="70"/>
        <source>Loaded mission extent</source>
        <translation>Extensión de la misión cargada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="71"/>
        <source>Image folder...</source>
        <translation>Carpeta de imágenes...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="93"/>
        <source>Min longitude:</source>
        <translation>Longitud mín.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="95"/>
        <source>Min latitude:</source>
        <translation>Latitud mín.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="97"/>
        <source>Max longitude:</source>
        <translation>Longitud máx.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="99"/>
        <source>Max latitude:</source>
        <translation>Latitud máx.:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="104"/>
        <source>Footprint buffer (m):</source>
        <translation>Margen de huella (m):</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="109"/>
        <source>Padding added around the camera positions so downloaded tiles cover the image footprints. Auto-sized from the mission; edit and re-fill to change.</source>
        <translation>Relleno añadido alrededor de las posiciones de la cámara para que las teselas descargadas cubran las huellas de las imágenes. Se dimensiona automáticamente a partir de la misión; edítelo y vuelva a rellenar para cambiarlo.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="118"/>
        <source>Datasets</source>
        <translation>Conjuntos de datos</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="120"/>
        <source>USGS 3DEP DEM</source>
        <translation>USGS 3DEP DEM</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="123"/>
        <source>USGS 3DEP provides 1 m local elevation. Optional when you already have a terrain source configured (AWS Terrain Tiles online, or downloaded 3DEP) — enable it to download higher-resolution data.</source>
        <translation>USGS 3DEP proporciona elevación local de 1 m. Opcional cuando ya tiene configurada una fuente de terreno (AWS Terrain Tiles en línea, o 3DEP descargado): actívelo para descargar datos de mayor resolución.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="127"/>
        <source>Meta/WRI Canopy Height</source>
        <translation>Altura del dosel Meta/WRI</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="142"/>
        <source>Store in:</source>
        <translation>Guardar en:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="144"/>
        <source>Central tile library (recommended)</source>
        <translation>Biblioteca central de teselas (recomendado)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="146"/>
        <source>Mission results folder</source>
        <translation>Carpeta de resultados de la misión</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="147"/>
        <source>Custom folder...</source>
        <translation>Carpeta personalizada...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="149"/>
        <source>The central library collects tiles from all missions in one place (they merge, nothing gets replaced) and registers automatically. Choose the results folder or a custom folder to keep tiles beside a specific mission instead.</source>
        <translation>La biblioteca central reúne las teselas de todas las misiones en un solo lugar (se combinan, nada se reemplaza) y se registra automáticamente. Elija la carpeta de resultados o una carpeta personalizada para guardar las teselas junto a una misión concreta.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="158"/>
        <source>Output folder:</source>
        <translation>Carpeta de salida:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="162"/>
        <source>Browse...</source>
        <translation>Examinar...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="168"/>
        <source>Register in Preferences when complete</source>
        <translation>Registrar en Preferencias al finalizar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="177"/>
        <source>Download</source>
        <translation>Descargar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="180"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="206"/>
        <source>This area is already covered by your registered tiles.</source>
        <translation>Esta área ya está cubierta por sus teselas registradas.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="208"/>
        <source>Partially covered by your registered tiles — downloading fills the gaps.</source>
        <translation>Parcialmente cubierto por sus teselas registradas; la descarga rellena los huecos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="214"/>
        <source>Your downloaded 1 m tiles don&apos;t include this area — without this download, online AWS Terrain Tiles (~30 m) are used here instead.</source>
        <translation>Sus teselas de 1 m descargadas no incluyen esta área; sin esta descarga, aquí se usan los AWS Terrain Tiles en línea (~30 m).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="217"/>
        <source>Your downloaded canopy tiles don&apos;t include this area — without this download, POD runs with no canopy attenuation here.</source>
        <translation>Sus teselas de dosel descargadas no incluyen esta área; sin esta descarga, el POD se ejecuta aquí sin atenuación del dosel.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="222"/>
        <source>No local elevation tiles registered — online AWS Terrain Tiles (~30 m) serve as the baseline.</source>
        <translation>No hay teselas de elevación locales registradas; los AWS Terrain Tiles en línea (~30 m) sirven como base.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="224"/>
        <source>No canopy source is configured yet.</source>
        <translation>Aún no se ha configurado una fuente de dosel.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/TileFetchDialog.py" line="276"/>
        <source>Select output folder</source>
        <translation>Seleccionar carpeta de salida</translation>
    </message>
</context>
<context>
    <name>TrackGalleryWidget</name>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="41"/>
        <source>Detection Gallery</source>
        <translation>Galería de detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="82"/>
        <source>0 detections</source>
        <translation>0 detecciones</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="149"/>
        <source>1 detection</source>
        <translation>1 detección</translation>
    </message>
    <message>
        <location filename="../app/core/views/streaming/components/TrackGalleryWidget.py" line="151"/>
        <source>{count} detections</source>
        <translation>{count} detecciones</translation>
    </message>
</context>
<context>
    <name>UnifiedMapExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="439"/>
        <source>No Data Selected</source>
        <translation>Ningún dato seleccionado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="440"/>
        <source>Please select at least one type of data to export.</source>
        <translation>Seleccione al menos un tipo de datos para exportar.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="470"/>
        <source>Select folder for POD coverage files</source>
        <translation>Seleccionar carpeta para los archivos de cobertura POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="478"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="585"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="886"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="924"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="969"/>
        <source>Export Error</source>
        <translation>Error de exportación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="479"/>
        <source>An error occurred during export:
{error}</source>
        <translation>Se produjo un error durante la exportación:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="497"/>
        <source>Save Map Export</source>
        <translation>Guardar exportación de mapa</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="499"/>
        <source>KML files (*.kml);;KMZ files (*.kmz)</source>
        <translation>Archivos KML (*.kml);;Archivos KMZ (*.kmz)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="586"/>
        <source>Failed to export to KML:
{error}</source>
        <translation>Error al exportar a KML:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="653"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="845"/>
        <source>POD Error</source>
        <translation>Error de POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="654"/>
        <source>Could not start the POD calculation:
{error}</source>
        <translation>No se pudo iniciar el cálculo de POD:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="704"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="716"/>
        <source>POD coverage complete</source>
        <translation>Cobertura POD completada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="713"/>
        <source>POD coverage complete — {count} frame(s) used online elevation (outside local DEM)</source>
        <translation>Cobertura POD completada: {count} fotograma(s) usaron elevación en línea (fuera del DEM local)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="721"/>
        <source>POD complete — {skipped} of {total} frames skipped</source>
        <translation>POD completado: {skipped} de {total} fotogramas omitidos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="724"/>
        <source>({count} without elevation data)</source>
        <translation>({count} sin datos de elevación)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="732"/>
        <source>(canopy data covered {pct}% of the searched area)</source>
        <translation>(los datos de dosel cubrieron el {pct}% del área buscada)</translation>
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
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="808"/>
        <source>Terrain and canopy aware probability-of-detection heatmap.</source>
        <translation>Mapa de calor de probabilidad de detección consciente del terreno y del dosel.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="812"/>
        <source>Mean POD over covered area: {pod}%</source>
        <translation>POD media sobre el área cubierta: {pod}%</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="815"/>
        <source>POD Coverage</source>
        <translation>Cobertura POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="823"/>
        <source>POD Overlay</source>
        <translation>Superposición POD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="824"/>
        <source>The POD coverage was computed, but embedding it into the exported file failed:
{error}

The POD GeoTIFF products were still written next to the export.</source>
        <translation>La cobertura POD se calculó, pero no se pudo incrustar en el archivo exportado:
{error}

Los productos GeoTIFF de POD se escribieron igualmente junto a la exportación.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="837"/>
        <source>POD calculation cancelled</source>
        <translation>Cálculo de POD cancelado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="846"/>
        <source>POD calculation failed:
{error}</source>
        <translation>El cálculo de POD falló:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="887"/>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="925"/>
        <source>Failed to export to CalTopo:
{error}</source>
        <translation>Error al exportar a CalTopo:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="941"/>
        <source>Map export completed successfully!</source>
        <translation>¡Exportación de mapa completada correctamente!</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="956"/>
        <source>Map export cancelled</source>
        <translation>Exportación de mapa cancelada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/UnifiedMapExportController.py" line="970"/>
        <source>Map export failed:
{error}</source>
        <translation>Error en la exportación de mapa:
{error}</translation>
    </message>
</context>
<context>
    <name>UpdateController</name>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="52"/>
        <source>Disabled while Offline Only mode is enabled.</source>
        <translation>Desactivado mientras el modo Solo sin conexión está habilitado.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="56"/>
        <source>Check the update feed for a newer ADIAT installer.</source>
        <translation>Consulte la fuente de actualizaciones para un instalador de ADIAT más reciente.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="85"/>
        <source>Updates Disabled</source>
        <translation>Actualizaciones deshabilitadas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="87"/>
        <source>Update checks are disabled while Offline Only mode is enabled.</source>
        <translation>La búsqueda de actualizaciones está deshabilitada mientras el modo Solo sin conexión está habilitado.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="101"/>
        <source>Update Check Failed</source>
        <translation>Error al buscar actualizaciones</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="102"/>
        <source>Unable to check for updates:
{error}</source>
        <translation>No se pueden buscar actualizaciones:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="110"/>
        <source>No Updates Available</source>
        <translation>No hay actualizaciones disponibles</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="112"/>
        <source>You are already running the latest available version of ADIAT.</source>
        <translation>Ya está ejecutando la última versión disponible de ADIAT.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="130"/>
        <source>Installer Launch Failed</source>
        <translation>Error al iniciar el instalador</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="131"/>
        <source>The installer was downloaded but could not be launched:
{error}</source>
        <translation>El instalador se descargó pero no se pudo iniciar:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="137"/>
        <source>Installer Started</source>
        <translation>Instalador iniciado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="139"/>
        <source>The installer has been launched. Close ADIAT when you are ready to continue the update.</source>
        <translation>El instalador se ha iniciado. Cierre ADIAT cuando esté listo para continuar la actualización.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="148"/>
        <source>Update Available</source>
        <translation>Actualización disponible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="150"/>
        <source>ADIAT {new_version} is available. You are running {current_version}.</source>
        <translation>ADIAT {new_version} está disponible. Usted está ejecutando {current_version}.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="156"/>
        <source>Do you want to download and launch the installer now?</source>
        <translation>¿Quiere descargar e iniciar el instalador ahora?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="159"/>
        <source>Download and Install</source>
        <translation>Descargar e instalar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="168"/>
        <source>Downloading ADIAT {version}...</source>
        <translation>Descargando ADIAT {version}...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="169"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="174"/>
        <source>Downloading Update</source>
        <translation>Descargando actualización</translation>
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
        <translation>desconocido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="196"/>
        <source>Downloading ADIAT {version}...
{downloaded} of {total}</source>
        <translation>Descargando ADIAT {version}...
{downloaded} de {total}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="204"/>
        <location filename="../app/core/controllers/UpdateController.py" line="210"/>
        <source>Update download canceled.</source>
        <translation>Descarga de actualización cancelada.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="215"/>
        <source>Download Failed</source>
        <translation>Error en la descarga</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/UpdateController.py" line="216"/>
        <source>Unable to download the update installer:
{error}</source>
        <translation>No se puede descargar el instalador de actualización:
{error}</translation>
    </message>
</context>
<context>
    <name>UpscaleDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="187"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="367"/>
        <source>Upscaled View - {level}x</source>
        <translation>Vista escalada - {level}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="229"/>
        <source>Upscale Method:</source>
        <translation>Método de escalado:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="233"/>
        <source>Auto (Recommended)</source>
        <translation>Automático (recomendado)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="234"/>
        <source>Fast (Lanczos)</source>
        <translation>Rápido (Lanczos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="236"/>
        <source>Balanced (OpenCV EDSR)</source>
        <translation>Equilibrado (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="264"/>
        <source>Upres Again</source>
        <translation>Volver a escalar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="267"/>
        <source>Upscale the currently visible portion by {factor}x</source>
        <translation>Escalar la porción actualmente visible {factor}x</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="271"/>
        <source>Quit</source>
        <translation>Salir</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="274"/>
        <source>Close this upscale window</source>
        <translation>Cerrar esta ventana de escalado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="302"/>
        <source>Resolution: {width} × {height} pixels | Original: {orig_w} × {orig_h} pixels | Upscale: {level}x | Use mouse wheel to zoom, right-click to pan</source>
        <translation>Resolución: {width} × {height} píxeles | Original: {orig_w} × {orig_h} píxeles | Ampliación: {level}x | Use la rueda del mouse para hacer zoom y el clic derecho para desplazar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="375"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="387"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="467"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="532"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="564"/>
        <source>Upscale Error</source>
        <translation>Error de escalado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="376"/>
        <source>Error during initial upscale: {error}</source>
        <translation>Error durante el escalado inicial: {error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="388"/>
        <source>Unable to extract visible image portion.</source>
        <translation>No se puede extraer la porción visible de la imagen.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="397"/>
        <source>Maximum Upscale Reached</source>
        <translation>Escalado máximo alcanzado</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="399"/>
        <source>Maximum upscale level of {level}x has been reached.
Further upscaling is not allowed to prevent memory issues.</source>
        <translation>Se ha alcanzado el nivel máximo de escalado de {level}x.
No se permite más escalado para evitar problemas de memoria.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="413"/>
        <source>Image Too Large</source>
        <translation>Imagen demasiado grande</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="415"/>
        <source>Upscaling would result in an image of {width}×{height} pixels.
Maximum allowed dimension is {max_dim} pixels.

Try zooming in to a smaller area before upscaling.</source>
        <translation>El escalado resultaría en una imagen de {width}×{height} píxeles.
La dimensión máxima permitida es {max_dim} píxeles.

Intente ampliar a un área más pequeña antes de escalar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="426"/>
        <source>Image Too Small</source>
        <translation>Imagen demasiado pequeña</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="428"/>
        <source>Visible portion is too small ({width}×{height} pixels).
Please zoom in to a larger area before upscaling.</source>
        <translation>La porción visible es demasiado pequeña ({width}×{height} píxeles).
Amplíe a un área más grande antes de escalar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="468"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="565"/>
        <source>An error occurred during upscaling:
{error}</source>
        <translation>Se produjo un error durante el escalado:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="487"/>
        <source>Upscaling image with AI enhancement...
From {width}×{height} to {new_width}×{new_height} pixels
This may take a few seconds.</source>
        <translation>Escalando imagen con mejora por IA...
De {width}×{height} a {new_width}×{new_height} píxeles
Esto puede tardar unos segundos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="499"/>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="760"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="504"/>
        <source>Upscaling (OpenCV EDSR)</source>
        <translation>Escalando (OpenCV EDSR)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="533"/>
        <source>Failed to start upscaling:
{error}</source>
        <translation>Error al iniciar el escalado:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="603"/>
        <source>Method Not Available</source>
        <translation>Método no disponible</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="605"/>
        <source>Real-ESRGAN is not yet implemented.
Falling back to Lanczos interpolation.</source>
        <translation>Real-ESRGAN aún no está implementado.
Retrocediendo a la interpolación Lanczos.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/UpscaleDialog.py" line="759"/>
        <source>Downloading {model_name} model...</source>
        <translation>Descargando modelo {model_name}...</translation>
    </message>
</context>
<context>
    <name>VideoParser</name>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="14"/>
        <source>Video Parser</source>
        <translation>Analizador de vídeo</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="45"/>
        <source>Path to the video file to extract frames from.
Supported formats: MP4, AVI, MOV, MKV, and other common video formats.
Click the Select button to browse for a video file.</source>
        <translation>Ruta al archivo de vídeo del que extraer fotogramas.
Formatos compatibles: MP4, AVI, MOV, MKV y otros formatos de vídeo comunes.
Haga clic en el botón Seleccionar para buscar un archivo de vídeo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="62"/>
        <source>Metadata file containing GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Optional: Provides location information for extracted frames.
Without a metadata file, frames will have no GPS data.</source>
        <translation>Archivo de metadatos que contiene datos de telemetría GPS.
Compatible con archivos de subtítulos SRT de DJI y registros de vuelo CSV de Skydio.
Opcional: Proporciona información de ubicación para los fotogramas extraídos.
Sin un archivo de metadatos, los fotogramas no tendrán datos GPS.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="68"/>
        <source>The metadata file contains timestamped GPS information for the video.  It is optional, but without it output images won&apos;t include location information.  Supports SRT (DJI) and CSV (Skydio) formats.</source>
        <translation>El archivo de metadatos contiene información GPS con marca de tiempo del vídeo. Es opcional, pero sin él las imágenes de salida no incluirán información de ubicación. Compatible con formatos SRT (DJI) y CSV (Skydio).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="71"/>
        <source>Metadata File (optional): </source>
        <translation>Archivo de metadatos (opcional): </translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="83"/>
        <source>Destination folder where extracted frame images will be saved.
Each frame is saved as a separate image file with timestamp information.</source>
        <translation>Carpeta de destino donde se guardarán las imágenes de los fotogramas extraídos.
Cada fotograma se guarda como un archivo de imagen separado con información de marca de tiempo.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="87"/>
        <source>Output Folder:</source>
        <translation>Carpeta de salida:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="99"/>
        <source>Path to the output folder for extracted frame images.
All frames will be saved in this directory with sequential naming.
Click the Select button to choose a different folder.</source>
        <translation>Ruta a la carpeta de salida para las imágenes de fotogramas extraídos.
Todos los fotogramas se guardarán en este directorio con nombres secuenciales.
Haga clic en el botón Seleccionar para elegir una carpeta diferente.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="116"/>
        <source>Browse for output folder to save extracted frames.
Opens a folder selection dialog.</source>
        <translation>Buscar la carpeta de salida para guardar los fotogramas extraídos.
Abre un diálogo de selección de carpeta.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="120"/>
        <location filename="../resources/views/images/VideoParser.ui" line="162"/>
        <location filename="../resources/views/images/VideoParser.ui" line="200"/>
        <source>Select</source>
        <translation>Seleccionar</translation>
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
        <translation>Seleccione el archivo de vídeo origen para analizar.
El vídeo se dividirá en imágenes de fotogramas individuales.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="146"/>
        <source>Video File:</source>
        <translation>Archivo de vídeo:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="158"/>
        <source>Browse for video file to extract frames from.
Opens a file selection dialog for video files (MP4, AVI, MOV, etc.).</source>
        <translation>Buscar un archivo de vídeo del que extraer fotogramas.
Abre un diálogo de selección de archivos de vídeo (MP4, AVI, MOV, etc.).</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="177"/>
        <source>Path to the optional metadata file with GPS telemetry data.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
If provided, extracted frames will include GPS metadata (latitude, longitude, altitude).
Can be left empty if location data is not needed.</source>
        <translation>Ruta al archivo de metadatos opcional con datos de telemetría GPS.
Compatible con archivos de subtítulos SRT de DJI y registros de vuelo CSV de Skydio.
Si se proporciona, los fotogramas extraídos incluirán metadatos GPS (latitud, longitud, altitud).
Se puede dejar vacío si no se necesitan datos de ubicación.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="195"/>
        <source>Browse for optional metadata file containing GPS telemetry.
Supports DJI SRT subtitle files and Skydio CSV flight logs.
Opens a file selection dialog for SRT and CSV files.</source>
        <translation>Buscar un archivo de metadatos opcional que contenga telemetría GPS.
Compatible con archivos de subtítulos SRT de DJI y registros de vuelo CSV de Skydio.
Abre un diálogo de selección de archivos SRT y CSV.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="219"/>
        <source>Time interval between extracted frames.
Determines how frequently frames are captured from the video.
Smaller intervals = More frames extracted (larger output)</source>
        <translation>Intervalo de tiempo entre fotogramas extraídos.
Determina la frecuencia con la que se capturan los fotogramas del vídeo.
Intervalos menores = Más fotogramas extraídos (salida más grande)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="224"/>
        <source>Time Interval (seconds):</source>
        <translation>Intervalo de tiempo (segundos):</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="236"/>
        <source>Set the time interval in seconds between frame extractions.
• Range: 0.1 to unlimited seconds
• Default: 5.0 seconds (extracts 1 frame every 5 seconds)
• Lower values: More frames extracted (e.g., 0.5s = 2 frames per second)
• Higher values: Fewer frames extracted (e.g., 10s = 1 frame every 10 seconds)
Recommendation: 3-5 seconds for most drone footage analysis</source>
        <translation>Establezca el intervalo de tiempo en segundos entre extracciones de fotogramas.
• Rango: 0,1 a ilimitado segundos
• Predeterminado: 5,0 segundos (extrae 1 fotograma cada 5 segundos)
• Valores más bajos: Se extraen más fotogramas (p. ej., 0,5 s = 2 fotogramas por segundo)
• Valores más altos: Se extraen menos fotogramas (p. ej., 10 s = 1 fotograma cada 10 segundos)
Recomendación: 3-5 segundos para la mayoría de los análisis de metraje de dron</translation>
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
        <translation>Iniciar la extracción de fotogramas del archivo de vídeo.
Requisitos:
• Se debe seleccionar el archivo de vídeo
• Se debe seleccionar la carpeta de salida
• Se debe establecer el intervalo de tiempo (predeterminado: 5 segundos)
El proceso extraerá fotogramas al intervalo especificado y los guardará como imágenes.
Si se proporciona un archivo de metadatos (SRT o CSV), los metadatos GPS se incrustarán en los fotogramas extraídos.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="320"/>
        <source>Start</source>
        <translation>Iniciar</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="351"/>
        <source>Cancel the frame extraction process.
Stops the operation immediately and returns to the ready state.
Any frames already extracted will be saved in the output folder.
Click to abort the current parsing operation.</source>
        <translation>Cancelar el proceso de extracción de fotogramas.
Detiene la operación inmediatamente y vuelve al estado listo.
Los fotogramas ya extraídos se guardarán en la carpeta de salida.
Haga clic para abortar la operación de análisis actual.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/VideoParser.ui" line="360"/>
        <source> Cancel</source>
        <translation> Cancelar</translation>
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
        <translation>Ventana de salida de progreso y estado.
Muestra información en tiempo real durante la extracción de fotogramas:
• Fotograma actual en procesamiento
• Marcas de tiempo y números de fotograma
• Coordenadas GPS (si se proporciona un archivo SRT)
• Porcentaje de progreso y estado de finalización
• Cualquier error o advertencia encontrado
Muestra el total de fotogramas extraídos al completarse.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="57"/>
        <source>Select a Video File</source>
        <translation>Seleccionar un archivo de vídeo</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="72"/>
        <source>Select a Metadata File</source>
        <translation>Seleccionar un archivo de metadatos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="73"/>
        <source>Metadata Files (*.srt *.csv);;SRT Files (*.srt);;CSV Flight Logs (*.csv)</source>
        <translation>Archivos de metadatos (*.srt *.csv);;Archivos SRT (*.srt);;Registros de vuelo CSV (*.csv)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="90"/>
        <source>Select Directory</source>
        <translation>Seleccionar directorio</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="110"/>
        <source>Please set the video file and output directory.</source>
        <translation>Establezca el archivo de vídeo y el directorio de salida.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="115"/>
        <source>--- Starting video processing ---</source>
        <translation>--- Iniciando procesamiento de vídeo ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="164"/>
        <source>Confirmation</source>
        <translation>Confirmación</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="165"/>
        <source>Are you sure you want to cancel the video processing in progress?</source>
        <translation>¿Está seguro de que desea cancelar el procesamiento de vídeo en curso?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="201"/>
        <source>--- Video Processing Completed ---</source>
        <translation>--- Procesamiento de vídeo completado ---</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="203"/>
        <source>{count} images created</source>
        <translation>{count} imágenes creadas</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/VideoParser.py" line="256"/>
        <source>Error Starting Processing</source>
        <translation>Error al iniciar el procesamiento</translation>
    </message>
</context>
<context>
    <name>Viewer</name>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="14"/>
        <source>Automated Drone Image Analysis Tool :: Viewer - Sponsored by TEXSAR</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron :: Visor - Patrocinado por TEXSAR</translation>
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
        <translation>Ver atajos de teclado y ayuda</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="199"/>
        <source>Toggle the detection overlay on the image.
When enabled, shows processed image with detected objects highlighted.
When disabled, shows the original unprocessed image.
Use to compare original image with detection results.</source>
        <translation>Alternar la superposición de detección en la imagen.
Cuando está habilitada, muestra la imagen procesada con los objetos detectados resaltados.
Cuando está deshabilitada, muestra la imagen original sin procesar.
Úselo para comparar la imagen original con los resultados de detección.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="460"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="205"/>
        <source>Show Overlay</source>
        <translation>Mostrar superposición</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1302"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="225"/>
        <source>Toggle Gallery Mode (G)
Shows all AOIs from all images in a grid view</source>
        <translation>Alternar modo Galería (G)
Muestra todos los AOI de todas las imágenes en una vista de cuadrícula</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="255"/>
        <source>Highlight Pixels of Interest(H)</source>
        <translation>Resaltar píxeles de interés (H)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="277"/>
        <source>Show AOIs</source>
        <translation>Mostrar AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1322"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="328"/>
        <source>Open Histogram</source>
        <translation>Abrir histograma</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="344"/>
        <source>Map with Image Locations (M)</source>
        <translation>Mapa con ubicaciones de imágenes (M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="360"/>
        <source>North-Oriented View of Image (R)</source>
        <translation>Vista orientada al norte de la imagen (R)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="376"/>
        <source>Adjust Image (Ctrl+H)</source>
        <translation>Ajustar imagen (Ctrl+H)</translation>
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
        <translation>Medir distancia (Ctrl+M)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="420"/>
        <source>ruler.png</source>
        <translation>ruler.png</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2091"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="427"/>
        <source>Person Size Reference (Ctrl+P)</source>
        <translation>Referencia de tamaño de persona (Ctrl+P)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="299"/>
        <source>Toggle the measurement ruler drawn over the selected AOI</source>
        <translation>Mostrar u ocultar la regla de medición dibujada sobre el AOI seleccionado</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="439"/>
        <source>person.png</source>
        <translation>person.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="446"/>
        <source>Toggle Grid Review Mode (S) — sweep the image cell by cell; Shift+S for grid settings</source>
        <translation>Alternar modo de revisión por cuadrícula (S) — recorrer la imagen celda por celda; Mayús+S para ajustes de cuadrícula</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="461"/>
        <source>grid.png</source>
        <translation>grid.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="468"/>
        <source>Toggle Magnifying Glass (Middle Mouse)</source>
        <translation>Alternar lupa (botón central del ratón)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="498"/>
        <source>magnify.png</source>
        <translation>magnify.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="512"/>
        <source>Map Export (KML / CalTopo)</source>
        <translation>Exportación de mapa (KML / CalTopo)</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="542"/>
        <source>map.png</source>
        <translation>map.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="549"/>
        <source>Generate PDF Report</source>
        <translation>Generar informe PDF</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="579"/>
        <source>pdf.png</source>
        <translation>pdf.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="591"/>
        <source>Generate Zip Bundle</source>
        <translation>Generar paquete Zip</translation>
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
        <translation>Omitir imágenes ocultas al navegar.
Cuando está habilitado, los botones Anterior/Siguiente saltarán las imágenes marcadas como ocultas.
Úselo para concentrarse en imágenes que no han sido revisadas o marcadas para exclusión.
Atajo de teclado: H para ocultar/mostrar la imagen actual</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="652"/>
        <source>Skip Hidden</source>
        <translation>Omitir ocultas</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="691"/>
        <source>Mark current image as hidden.
Hidden images can be excluded from reports, exports, and navigation.
Use to remove images with false positives or no relevant detections.
When &quot;Skip Hidden&quot; is enabled, hidden images are skipped during navigation.
Keyboard shortcut: H</source>
        <translation>Marcar la imagen actual como oculta.
Las imágenes ocultas pueden excluirse de informes, exportaciones y navegación.
Úselo para eliminar imágenes con falsos positivos o sin detecciones relevantes.
Cuando &quot;Omitir ocultas&quot; está habilitado, las imágenes ocultas se omiten durante la navegación.
Atajo de teclado: H</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="698"/>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="718"/>
        <source>Hide Image</source>
        <translation>Ocultar imagen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="710"/>
        <source>Displays the name of the currently hidden image.
When an image is marked as hidden, its filename appears here.
Hidden images are excluded from navigation when &quot;Skip Hidden&quot; is enabled.</source>
        <translation>Muestra el nombre de la imagen actualmente oculta.
Cuando una imagen se marca como oculta, su nombre de archivo aparece aquí.
Las imágenes ocultas se excluyen de la navegación cuando &quot;Omitir ocultas&quot; está habilitado.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="746"/>
        <source>Jump directly to a specific image number.
Enter an image number and press Enter to navigate instantly.
Useful for reviewing specific images or returning to a noted location.</source>
        <translation>Saltar directamente a un número de imagen específico.
Introduzca un número de imagen y pulse Enter para navegar al instante.
Útil para revisar imágenes específicas o volver a una ubicación anotada.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="751"/>
        <source>Jump To:</source>
        <translation>Ir a:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="776"/>
        <source>Enter an image number (1 to total) and press Enter.
Quickly navigate to any image in the analysis results.
Example: Type &quot;25&quot; and press Enter to jump to image #25</source>
        <translation>Introduzca un número de imagen (1 al total) y pulse Enter.
Navegue rápidamente a cualquier imagen en los resultados de análisis.
Ejemplo: Escriba &quot;25&quot; y pulse Enter para saltar a la imagen n.º 25</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="790"/>
        <source>Jump to a specific AOI by its run-wide number.
Enter an AOI number and press Enter to select and scroll to it.</source>
        <translation>Saltar a un AOI específico por su número dentro de toda la ejecución.
Introduzca un número de AOI y pulse Intro para seleccionarlo y desplazarse hasta él.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="794"/>
        <source>Go to AOI #:</source>
        <translation>Ir al AOI n.º:</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="819"/>
        <source>Enter an AOI number and press Enter.
Selects that AOI and scrolls it into view in the gallery or single-image list.</source>
        <translation>Introduzca un número de AOI y pulse Intro.
Selecciona ese AOI y lo desplaza a la vista en la galería o en la lista de una sola imagen.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="832"/>
        <source>Previous Image</source>
        <translation>Imagen anterior</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="839"/>
        <source>previous.png</source>
        <translation>previous.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="854"/>
        <source>Next Image</source>
        <translation>Siguiente imagen</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="861"/>
        <source>next.png</source>
        <translation>next.png</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1004"/>
        <source>Filter AOIs by color and pixel area</source>
        <translation>Filtrar AOI por color y área de píxeles</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1076"/>
        <source>Sort By</source>
        <translation>Ordenar por</translation>
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
        <translation>Ordenar las áreas de interés (AOI) en la lista.
Elija cómo ordenar los objetos detectados:
• Área de píxeles: Ordenar por tamaño (de mayor a menor)
• Distancia: Ordenar por distancia desde el centro de la imagen o el punto de referencia
• Color: Agrupar por colores similares
• Orden de detección: Orden original del análisis
La ordenación ayuda a priorizar la revisión de objetos más grandes o más cercanos.</translation>
    </message>
    <message>
        <location filename="../resources/views/images/viewer/Viewer.ui" line="1176"/>
        <source>Open</source>
        <translation>Abrir</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="134"/>
        <source>Automated Drone Image Analysis Tool v{version} - Sponsored by TEXSAR</source>
        <translation>Herramienta automatizada de análisis de imágenes de dron v{version} - Patrocinado por TEXSAR</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="146"/>
        <source>Reading result file...</source>
        <translation>Leyendo archivo de resultados...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="163"/>
        <source>Checking image dimensions ({n} images)...</source>
        <translation>Comprobando dimensiones de imagen ({n} imágenes)...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="173"/>
        <source>Validating image paths...</source>
        <translation>Validando rutas de imagen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="180"/>
        <source>Load Results Failed</source>
        <translation>Error al cargar los resultados</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="182"/>
        <source>Cannot load results without valid image and mask locations.

The viewer will now close.</source>
        <translation>No se pueden cargar los resultados sin ubicaciones válidas de imagen y máscara.

El visor se cerrará ahora.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="189"/>
        <source>Scanning source folder for full flight...</source>
        <translation>Escaneando carpeta de origen para el vuelo completo...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="205"/>
        <source>Initialising controllers...</source>
        <translation>Inicializando controladores...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="216"/>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1565"/>
        <source>Skip Hidden ({count}) </source>
        <translation>Omitir ocultas ({count}) </translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="248"/>
        <source>Loading detection results from {n} images...</source>
        <translation>Cargando resultados de detección de {n} imágenes...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="287"/>
        <source>Image metadata and information.
Click on GPS Coordinates to copy, share, or open in mapping applications.</source>
        <translation>Metadatos e información de la imagen.
Haga clic en las coordenadas GPS para copiar, compartir o abrir en aplicaciones de mapas.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="327"/>
        <source>Loading first image...</source>
        <translation>Cargando primera imagen...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="342"/>
        <source>Preparing thumbnails...</source>
        <translation>Preparando miniaturas...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="678"/>
        <source>No Dataset</source>
        <translation>Sin conjunto de datos</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="679"/>
        <source>No dataset is currently loaded.</source>
        <translation>Actualmente no hay ningún conjunto de datos cargado.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="686"/>
        <source>Generate Cache</source>
        <translation>Generar caché</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="688"/>
        <source>This will regenerate thumbnail and color caches for all AOIs in this dataset.

This may take a few minutes depending on the dataset size.

Continue?</source>
        <translation>Esto regenerará las cachés de miniaturas y colores para todos los AOI de este conjunto de datos.

Esto puede tardar varios minutos según el tamaño del conjunto de datos.

¿Continuar?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="701"/>
        <source>Initializing cache generation...</source>
        <translation>Inicializando generación de caché...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="702"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="707"/>
        <source>Generating Cache</source>
        <translation>Generando caché</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="744"/>
        <source>Error</source>
        <translation>Error</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="745"/>
        <source>Failed to start cache generation:
{error}</source>
        <translation>Error al iniciar la generación de caché:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="763"/>
        <source>Cache Generated</source>
        <translation>Caché generada</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="765"/>
        <source>Cache generation complete!

Processed {images} images with {aois} AOIs.

The viewer will now load thumbnails and colors much faster.</source>
        <translation>¡Generación de caché completada!

Se procesaron {images} imágenes con {aois} AOI.

El visor cargará ahora miniaturas y colores mucho más rápido.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="796"/>
        <source>Cache Generation Error</source>
        <translation>Error de generación de caché</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="798"/>
        <source>An error occurred during cache generation:

{error}</source>
        <translation>Se produjo un error durante la generación de la caché:

{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="985"/>
        <source>AOI Not Visible</source>
        <translation>AOI no visible</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="987"/>
        <source>The AOI at the cursor position cannot be selected because it is currently hidden due to active filters.

To select this AOI, please clear or adjust your filters.</source>
        <translation>No se puede seleccionar el AOI en la posición del cursor porque está actualmente oculto debido a filtros activos.

Para seleccionar este AOI, borre o ajuste sus filtros.</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1181"/>
        <source>Update Image Dimensions</source>
        <translation>Actualizar dimensiones de imagen</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1183"/>
        <source>This dataset is missing image dimensions needed for heatmap filtering ({count} images).

Would you like to read dimensions from the image files and update the results file?</source>
        <translation>A este conjunto de datos le faltan las dimensiones de imagen necesarias para el filtrado por mapa de calor ({count} imágenes).

¿Desea leer las dimensiones desde los archivos de imagen y actualizar el archivo de resultados?</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1222"/>
        <source>Reading image dimensions ({done}/{total})...</source>
        <translation>Leyendo dimensiones de imagen ({done}/{total})...</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1313"/>
        <source>Show Pixels of Interest (H or Ctrl+I)</source>
        <translation>Mostrar píxeles de interés (H o Ctrl+I)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1328"/>
        <source>Toggle AOI Circles</source>
        <translation>Alternar círculos de AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1335"/>
        <source>Toggle AOI Ruler</source>
        <translation>Mostrar/ocultar regla de AOI</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1751"/>
        <source>Missing Dependency</source>
        <translation>Dependencia faltante</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1753"/>
        <source>The qimage2ndarray module is required for the upscale feature.
Please install it using: pip install qimage2ndarray</source>
        <translation>El módulo qimage2ndarray es necesario para la función de escalado.
Instálelo usando: pip install qimage2ndarray</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1762"/>
        <source>Upscale Error</source>
        <translation>Error de escalado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="1764"/>
        <source>An error occurred while opening the upscale dialog:
{error}</source>
        <translation>Se produjo un error al abrir el diálogo de escalado:
{error}</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2095"/>
        <source>Person Size Reference is unavailable: no GSD for this image</source>
        <translation>La referencia de tamaño de persona no está disponible: esta imagen no tiene GSD</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2192"/>
        <source>Unknown Reviewer</source>
        <translation>Revisor desconocido</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/Viewer.py" line="2255"/>
        <source>Loading gallery...</source>
        <translation>Cargando galería...</translation>
    </message>
</context>
<context>
    <name>WaldoClockCorrectionDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="77"/>
        <source>WALDO Camera Clock Correction</source>
        <translation>Corrección del reloj de la cámara WALDO</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="99"/>
        <source>The camera clock on these images appears to be misconfigured:</source>
        <translation>El reloj de la cámara de estas imágenes parece estar mal configurado:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="108"/>
        <source>ADIAT can stamp a corrected capture time into the image metadata. This is non-destructive: the original EXIF fields are not changed, and sun/shadow calculations will use the corrected time. Check the preview against when the flight actually flew - if it is off by 12 hours, adjust the clock face error.</source>
        <translation>ADIAT puede grabar una hora de captura corregida en los metadatos de la imagen. Es un proceso no destructivo: los campos EXIF originales no se modifican y los cálculos de sol y sombra usarán la hora corregida. Compare la vista previa con la hora real del vuelo; si difiere en 12 horas, ajuste el error de la esfera del reloj.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="120"/>
        <source> hours</source>
        <translation> horas</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="121"/>
        <source>Clock face error to remove:</source>
        <translation>Error de la esfera del reloj a corregir:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="128"/>
        <source>IANA time zone name (e.g. America/Los_Angeles) or a fixed UTC offset in hours (e.g. -7)</source>
        <translation>Nombre de zona horaria IANA (p. ej. America/Los_Angeles) o un desfase UTC fijo en horas (p. ej. -7)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="130"/>
        <source>True camera time zone:</source>
        <translation>Zona horaria real de la cámara:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="139"/>
        <source>Remember my choice for this folder</source>
        <translation>Recordar mi elección para esta carpeta</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="159"/>
        <source>Apply Correction</source>
        <translation>Aplicar corrección</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="163"/>
        <source>Not Now</source>
        <translation>Ahora no</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="166"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="170"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="231"/>
        <source>Enter a valid time zone (IANA name or UTC offset in hours).</source>
        <translation>Introduzca una zona horaria válida (nombre IANA o desfase UTC en horas).</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="239"/>
        <source>{name}: camera says {before}  →  corrected {after}</source>
        <translation>{name}: la cámara indica {before}  →  corregido {after}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="245"/>
        <source>Correction preview unavailable.</source>
        <translation>Vista previa de la corrección no disponible.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="272"/>
        <source>Stamping corrected capture times...</source>
        <translation>Grabando las horas de captura corregidas...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="292"/>
        <source>Cancelling...</source>
        <translation>Cancelando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="308"/>
        <source>Corrected:        {n}</source>
        <translation>Corregidas:       {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="309"/>
        <source>Already corrected: {n}</source>
        <translation>Ya corregidas:    {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="310"/>
        <source>Errors:           {n}</source>
        <translation>Errores:          {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoClockCorrectionDialog.py" line="313"/>
        <source>Cancelled - remaining images are uncorrected.</source>
        <translation>Cancelado: las imágenes restantes no se han corregido.</translation>
    </message>
</context>
<context>
    <name>WaldoPrePassDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="58"/>
        <source>Preparing WALDO Images</source>
        <translation>Preparando imágenes WALDO</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="70"/>
        <source>Synthesising WALDO metadata...</source>
        <translation>Sintetizando metadatos WALDO...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="82"/>
        <source>Initialising...</source>
        <translation>Inicializando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="93"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="96"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="146"/>
        <source>WALDO Pre-Pass Complete</source>
        <translation>Prepasada WALDO completada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="147"/>
        <source>WALDO Pre-Pass Cancelled</source>
        <translation>Prepasada WALDO cancelada</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="154"/>
        <source>Processed:        {n}</source>
        <translation>Procesadas:       {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="155"/>
        <source>Already up-to-date: {n}</source>
        <translation>Ya actualizadas:    {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="156"/>
        <source>Skipped (non-WALDO): {n}</source>
        <translation>Omitidas (no WALDO): {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="157"/>
        <source>Errors:           {n}</source>
        <translation>Errores:          {n}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="164"/>
        <source>⚠ Metadata warnings:</source>
        <translation>⚠ Advertencias de metadatos:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="169"/>
        <source>Per-image errors:</source>
        <translation>Errores por imagen:</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="183"/>
        <source>Cancelling...</source>
        <translation>Cancelando...</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WaldoPrePassDialog.py" line="184"/>
        <source>Cancellation requested...</source>
        <translation>Cancelación solicitada...</translation>
    </message>
</context>
<context>
    <name>WingtraDataDialog</name>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="44"/>
        <source>Wingtra Data Import</source>
        <translation>Importación de datos Wingtra</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="54"/>
        <source>Import Summary</source>
        <translation>Resumen de importación</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="58"/>
        <source>&lt;b&gt;Matched images:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;CSV entries without match:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Result images without CSV data:&lt;/b&gt; {unmatched_images}</source>
        <translation>&lt;b&gt;Imágenes coincidentes:&lt;/b&gt; {matched}&lt;br&gt;&lt;b&gt;Entradas CSV sin coincidencia:&lt;/b&gt; {unmatched_csv}&lt;br&gt;&lt;b&gt;Imágenes de resultado sin datos CSV:&lt;/b&gt; {unmatched_images}</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="73"/>
        <source>Altitude &amp; GSD</source>
        <translation>Altitud y GSD</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="78"/>
        <source>&lt;b&gt;AGL computed from terrain:&lt;/b&gt; {agl_count} of {matched_count} images&lt;br&gt;&lt;br&gt;Per-image AGL is derived from the CSV altitude (ASL) minus terrain elevation at each GPS location. GSD will be calculated automatically using the camera sensor data and focal length.</source>
        <translation>&lt;b&gt;AGL calculado a partir del terreno:&lt;/b&gt; {agl_count} de {matched_count} imágenes&lt;br&gt;&lt;br&gt;El AGL de cada imagen se deriva de la altitud CSV (ASL) menos la elevación del terreno en cada ubicación GPS. El GSD se calculará automáticamente usando los datos del sensor de la cámara y la distancia focal.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="89"/>
        <source>&lt;b&gt;Terrain data unavailable&lt;/b&gt; - AGL could not be computed.&lt;br&gt;&lt;br&gt;Orientation (yaw/pitch/roll) will still be applied from the CSV. GSD and altitude displays require terrain data or a manual altitude override (Shift+O) after import.</source>
        <translation>&lt;b&gt;Datos de terreno no disponibles&lt;/b&gt;: no se pudo calcular el AGL.&lt;br&gt;&lt;br&gt;La orientación (yaw/pitch/roll) se aplicará igualmente desde el CSV. Las visualizaciones de GSD y altitud requieren datos de terreno o una sustitución manual de altitud (Mayús+O) después de importar.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="106"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/WingtraDataDialog.py" line="110"/>
        <source>Apply Wingtra Data</source>
        <translation>Aplicar datos Wingtra</translation>
    </message>
</context>
<context>
    <name>ZipExportController</name>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="130"/>
        <source>Save Zip File</source>
        <translation>Guardar archivo Zip</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="132"/>
        <source>Zip files (*.zip)</source>
        <translation>Archivos Zip (*.zip)</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="163"/>
        <source>No images to export</source>
        <translation>No hay imágenes para exportar</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="397"/>
        <source>ZIP file created</source>
        <translation>Archivo ZIP creado</translation>
    </message>
    <message>
        <location filename="../app/core/controllers/images/viewer/exports/ZipExportController.py" line="403"/>
        <source>Failed to generate Zip file: {error}</source>
        <translation>Error al generar el archivo Zip: {error}</translation>
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
        <translation>Opciones de exportación ZIP</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="26"/>
        <source>Choose what to export:

- Native: Original images, TIFF masks, and XML (paths made portable).
- Augmented: What you see in the viewer (AOIs/POIs), keeps EXIF/XMP.</source>
        <translation>Elija qué exportar:

- Nativo: Imágenes originales, máscaras TIFF y XML (con rutas portables).
- Aumentado: Lo que ve en el visor (AOI/POI), conserva EXIF/XMP.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="34"/>
        <source>Export Native data (original files + XML)</source>
        <translation>Exportar datos nativos (archivos originales + XML)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="35"/>
        <source>Export Augmented images (viewer overlays + metadata)</source>
        <translation>Exportar imágenes aumentadas (superposiciones del visor + metadatos)</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="50"/>
        <source>Include images without flagged AOIs</source>
        <translation>Incluir imágenes sin AOI marcados</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="53"/>
        <source>When unchecked, only images with at least one flagged AOI will be exported.
When checked, all images will be exported regardless of flagged AOI status.</source>
        <translation>Cuando está desactivado, solo se exportarán las imágenes con al menos un AOI marcado.
Cuando está activado, se exportarán todas las imágenes independientemente del estado de AOI marcado.</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="59"/>
        <source>OK</source>
        <translation>Aceptar</translation>
    </message>
    <message>
        <location filename="../app/core/views/images/viewer/dialogs/ZipExportDialog.py" line="60"/>
        <source>Cancel</source>
        <translation>Cancelar</translation>
    </message>
</context>
</TS>
