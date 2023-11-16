# -*- mode: python -*-

block_cipher = None

a = Analysis(['app\__main__.py'],
             pathex=['app'],
             binaries=None,
             datas=[('resources\\icons\\ADIAT.ico','.')],
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
