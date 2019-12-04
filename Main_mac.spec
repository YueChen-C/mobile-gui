# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['app/main.py'],
             pathex=['./mobile-gui'],
             binaries=[],
             datas=[('./app/app.ini','.'),('./app/mobile.ico','.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Mobile-GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Mobile-GUI')
app = BUNDLE(coll,
             name='Mobile-GUI.app',
             icon='mobile.icns',
             bundle_identifier=None,
             info_plist={
             'NSHighResolutionCapable': 'True',
             'LSEnvironment':{'GUI':'/usr/local/bin:/Users/tools/android-sdk/tools:'} # 该行是环境变量选填，避免打包后 mac gui 程序无法引用环境变量问题
             })
