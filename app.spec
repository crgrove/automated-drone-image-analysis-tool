import platform
# -*- mode: python -*-

block_cipher = None

if platform.system() == 'Windows':
    a = Analysis(['app/__main__.py'],
                pathex=['app'],
                binaries=[
                    ('LICENSE','.'),
                    ('app/external/exiftool.exe','external'),
                    ('app/external/dji_thermal_sdk_v1.7_20241205','external/dji_thermal_sdk_v1.7_20241205'),
                    ('app/external/autel', 'external/autel')
                ],
                datas=[
                    ('resources/icons/ADIAT.ico','.'),
                    ('app/algorithms.conf','.'),
                    ('app/drones.pkl', '.'),
                    ('app/xmp.pkl', '.'),
                    ('app/colors.pkl', '.'),
                    ('colors.csv', '.'),
                    # AI Person Detector models
                    ('app/algorithms/images/AIPersonDetector/services/ai_person_model_V2_640.onnx', 'ai_models'),
                    ('app/algorithms/images/AIPersonDetector/services/ai_person_model_V2_1024.onnx', 'ai_models')
                    ],

                hiddenimports=[
                    # Streaming algorithms modules
                    'algorithms.streaming',
                    'algorithms.streaming.MotionDetection',
                    'algorithms.streaming.MotionDetection.controllers',
                    'algorithms.streaming.MotionDetection.controllers.MotionDetectionController',
                    'algorithms.streaming.MotionDetection.controllers.MotionDetectionWizardController',
                    'algorithms.streaming.MotionDetection.services',
                    'algorithms.streaming.MotionDetection.services.MotionDetectionService',
                    'algorithms.streaming.MotionDetection.views',
                    'algorithms.streaming.ColorDetection',
                    'algorithms.streaming.ColorDetection.controllers',
                    'algorithms.streaming.ColorDetection.controllers.ColorDetectionController',
                    'algorithms.streaming.ColorDetection.controllers.ColorDetectionWizardController',
                    'algorithms.streaming.ColorDetection.services',
                    'algorithms.streaming.ColorDetection.services.ColorDetectionService',
                    'algorithms.streaming.ColorDetection.views',
                    'algorithms.streaming.ColorDetection.views.ColorDetectionControlWidget',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionController',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionWizardController',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyAndMotionDetectionOrchestrator',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyService',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services.MotionDetectionService',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services.shared_types',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.services.utils',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.views',
                    'algorithms.streaming.ColorAnomalyAndMotionDetection.views.ColorAnomalyAndMotionDetectionControlWidget',
                ],
                hookspath=None,
                runtime_hooks=None,
                excludes=None,
                cipher=block_cipher)
elif platform.system() == 'Darwin':
    a = Analysis(['app/__main__.py'],
                    pathex=['app'],
                    binaries=[
                        ('LICENSE','.')
                    ],
                    datas=[
                        ('resources/icons/ADIAT.ico','.'),
                        ('app/algorithms.conf','.'),
                        ('app/drones.pkl', '.'),
                        ('app/xmp.pkl', '.'),
                        # Color lists used by ColorListService (expects under app/)
                        ('app/colors.pkl', 'app'),
                        ('colors.csv', 'app'),
                        # AI Person Detector models
                        ('app/algorithms/images/AIPersonDetector/services/ai_person_model_V2_640.onnx', 'ai_models'),
                        ('app/algorithms/images/AIPersonDetector/services/ai_person_model_V2_1024.onnx', 'ai_models')
                        ],
                    hiddenimports=[
                        # Streaming algorithms modules
                        'algorithms.streaming',
                        'algorithms.streaming.MotionDetection',
                        'algorithms.streaming.MotionDetection.controllers',
                        'algorithms.streaming.MotionDetection.controllers.MotionDetectionController',
                        'algorithms.streaming.MotionDetection.controllers.MotionDetectionWizardController',
                        'algorithms.streaming.MotionDetection.services',
                        'algorithms.streaming.MotionDetection.services.MotionDetectionService',
                        'algorithms.streaming.MotionDetection.views',
                        'algorithms.streaming.ColorDetection',
                        'algorithms.streaming.ColorDetection.controllers',
                        'algorithms.streaming.ColorDetection.controllers.ColorDetectionController',
                        'algorithms.streaming.ColorDetection.controllers.ColorDetectionWizardController',
                        'algorithms.streaming.ColorDetection.services',
                        'algorithms.streaming.ColorDetection.services.ColorDetectionService',
                        'algorithms.streaming.ColorDetection.views',
                        'algorithms.streaming.ColorDetection.views.ColorDetectionControlWidget',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionController',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.controllers.ColorAnomalyAndMotionDetectionWizardController',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyAndMotionDetectionOrchestrator',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services.ColorAnomalyService',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services.MotionDetectionService',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services.shared_types',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.services.utils',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.views',
                        'algorithms.streaming.ColorAnomalyAndMotionDetection.views.ColorAnomalyAndMotionDetectionControlWidget',
                    ],
                    hookspath=None,
                    runtime_hooks=None,
                    excludes=None,
                    cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ADIAT',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='resources/icons/ADIAT.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ADIAT')

app = BUNDLE(coll,
             name='ADIAT.app',
             icon='resources/icons/ADIAT.ico',
             bundle_identifier=None)
