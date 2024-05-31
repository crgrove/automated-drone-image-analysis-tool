# -*- mode: python -*-

block_cipher = None

a = Analysis(['app\__main__.py'],
             pathex=['app'],
             binaries=[('app\\dependencies\\exiftool.exe','dependencies'),('app\\dependencies\\dji_thermal_sdk_v1.4_20220929','dependencies\\dji_thermal_sdk_v1.4_20220929')],
             datas=[('resources\\icons\\ADIAT.ico','.'),('app\\algorithms.conf','.')],
             hiddenimports=[],
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
          icon='resources\\icons\\ADIAT.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='ADIAT')

app = BUNDLE(coll,
             name='App.app',
             icon='resources/icons/texsar.icns',
             bundle_identifier=None)