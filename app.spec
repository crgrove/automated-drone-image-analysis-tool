import platform
import os
# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

try:
    spec_dir = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # __file__ may be undefined in some PyInstaller contexts; fall back to cwd
    spec_dir = os.path.abspath(os.getcwd())
translation_candidates = [
    os.path.join(spec_dir, 'translations', 'app_en.qm'),
    os.path.join(spec_dir, 'translations', 'app_it.qm'),
    os.path.join(spec_dir, 'translations', 'app_es.qm'),
    os.path.join(spec_dir, 'translations', 'app_nl.qm'),
]
translation_datas = [(path, 'translations') for path in translation_candidates if os.path.exists(path)]

# Bake the commit this build is cut from into the bundle so every field
# screenshot (window title) and field log self-identifies its code. See
# app/helpers/BuildInfo.py for the runtime side. '+dirty' marks a build from
# a tree with uncommitted changes - such builds are not reproducible.
import subprocess
build_stamp_datas = []
try:
    _rev = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                          cwd=spec_dir, capture_output=True, text=True, timeout=10)
    if _rev.returncode == 0:
        _stamp = _rev.stdout.strip()
        _status = subprocess.run(['git', 'status', '--porcelain'],
                                 cwd=spec_dir, capture_output=True, text=True, timeout=10)
        if _status.returncode == 0 and _status.stdout.strip():
            _stamp += '+dirty'
        _stamp_path = os.path.join(spec_dir, 'build', 'build_info.txt')
        os.makedirs(os.path.dirname(_stamp_path), exist_ok=True)
        with open(_stamp_path, 'w', encoding='utf-8') as _f:
            _f.write(_stamp + '\n')
        build_stamp_datas = [(_stamp_path, '.')]
        print(f"ADIAT build stamp: {_stamp}")
except (OSError, subprocess.SubprocessError) as _e:
    print(f"ADIAT build stamp unavailable (no git?): {_e}")

# timezonefinder + tzdata: runtime data for the Person Size Reference GPS ->
# timezone shadow fallback. PyInstaller misses the data files and tzdata's
# per-zone submodules, so collect both explicitly.
tz_datas = collect_data_files('timezonefinder') + collect_data_files('tzdata')
tz_hiddenimports = ['tzdata'] + collect_submodules('tzdata')

# rasterio/pyproj load submodules lazily and ship GDAL/PROJ data; without this
# the frozen build fails with "No module named 'rasterio.sample'" (POD/terrain).
geo_hiddenimports = collect_submodules('rasterio') + collect_submodules('pyproj')
geo_datas = collect_data_files('rasterio') + collect_data_files('pyproj')


def collect_algorithm_modules():
    """Enumerate every module under app/algorithms/ as a dotted import path.

    Algorithm packages are resolved at runtime from algorithms.conf via
    importlib, so PyInstaller cannot see them statically and every one needs a
    hidden import. Walking the source tree keeps the frozen build in sync by
    construction; the hand-maintained list this replaced had silently dropped
    the streaming AIPersonDetector (wizard died with "No module named
    'algorithms.streaming.AIPersonDetector'") while still naming a
    MotionDetection package that no longer exists.
    """
    app_root = os.path.join(spec_dir, 'app')
    modules = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(app_root, 'algorithms')):
        dirnames[:] = [d for d in dirnames if d != '__pycache__']
        if '__init__.py' not in filenames:
            # Not a package (e.g. algorithms/models/, which holds .onnx only);
            # nothing below it is importable either.
            dirnames[:] = []
            continue
        package = os.path.relpath(dirpath, app_root).replace(os.sep, '.')
        modules.append(package)
        modules.extend(
            '{}.{}'.format(package, name[:-3])
            for name in filenames
            if name.endswith('.py') and name != '__init__.py'
        )
    return sorted(modules)


algorithm_hiddenimports = collect_algorithm_modules()
print("ADIAT algorithm modules bundled: {}".format(len(algorithm_hiddenimports)))

# Dev tooling / installed-but-unused deps that bloat the frozen app (~300 MB).
unused_excludes = ['qt6_applications', 'qt6_tools', 'pyarrow', 'sklearn', 'sympy']

# Packaged builds default to WARNING-level logging (ADIAT_LOG_LEVEL still wins);
# the hook runs inside the frozen app at startup.
adiat_runtime_hooks = [os.path.join(spec_dir, 'runtime_hooks', 'set_log_level.py')]

# Modules loaded dynamically (importlib) or via runtime fallbacks that
# PyInstaller can't see statically. Identical for both platform builds.
common_hiddenimports = [
    'shapely',
    'shapely.geometry',
    # pandas pulls pytz for tz-aware timestamps; PyInstaller can miss it in the
    # frozen build, so pin it explicitly (carried over from the 2.0.3 HDMI hotfix).
    'pytz',
    # timezonefinder + h3 back the GPS -> timezone shadow fallback.
    'timezonefinder',
    'h3',
    # pysolar picks numeric_numpy / numeric_python at runtime.
    'pysolar',
    'pysolar.solar',
    'pysolar.numeric',
    'pysolar.numeric_numpy',
    'pysolar.numeric_python',
    # Image and streaming algorithm packages are added by
    # collect_algorithm_modules() above - do not hand-list them here.
] + algorithm_hiddenimports + tz_hiddenimports + geo_hiddenimports

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
                    ('app/drones.csv', '.'),
                    ('app/xmp.csv', '.'),
                    ('app/colors.pkl', '.'),
                    ('colors.csv', '.'),
                    # Bundled EGM96 geoid grid (global) for offline ellipsoidal<->orthometric
                    # height conversion; PROJ streams it online otherwise.
                    ('app/resources/geoid/us_nga_egm96_15.tif', 'resources/geoid'),
                    # AI Person Detector models
                    ('app/algorithms/models/AIPersonDetector/ai_person_model_V3_640.onnx', 'algorithms/models/AIPersonDetector'),
                    ('app/algorithms/models/AIPersonDetector/ai_person_model_V3_1024.onnx', 'algorithms/models/AIPersonDetector')
                    ] + translation_datas + tz_datas + geo_datas + build_stamp_datas,
                hiddenimports=common_hiddenimports,
                hookspath=None,
                runtime_hooks=adiat_runtime_hooks,
                excludes=['PyQt5', 'PyQt6'] + unused_excludes,
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
                        ('app/drones.csv', '.'),
                        ('app/xmp.csv', '.'),
                        # Color lists used by ColorListService (expects under app/)
                        ('app/colors.pkl', 'app'),
                        ('colors.csv', 'app'),
                        # Bundled EGM96 geoid grid (global) for offline ellipsoidal<->orthometric
                        # height conversion; PROJ streams it online otherwise.
                        ('app/resources/geoid/us_nga_egm96_15.tif', 'resources/geoid'),
                        # AI Person Detector models
                        ('app/algorithms/models/AIPersonDetector/ai_person_model_V3_640.onnx', 'algorithms/models/AIPersonDetector'),
                        ('app/algorithms/models/AIPersonDetector/ai_person_model_V3_1024.onnx', 'algorithms/models/AIPersonDetector')
                        ] + translation_datas + tz_datas + geo_datas + build_stamp_datas,
                    hiddenimports=common_hiddenimports,
                    hookspath=None,
                    runtime_hooks=adiat_runtime_hooks,
                    excludes=['PyQt5', 'PyQt6'] + unused_excludes,
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
