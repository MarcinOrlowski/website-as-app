# -*- mode: python ; coding: utf-8 -*-

##################################################################################
#
# Website As App
# Run any website as standalone desktop application
#
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2023-2024 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/website-as-app
#
#####
#
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements-dev.txt
#
# On Windows:
#   pyinstaller webapp.spec
#
# On Ubuntu:
#   apt install -y wine32:i386 libgd3:i386
#   # install python under wine:
#   wget https://www.python.org/ftp/python/3.12.4/python-3.12.4.exe
#   wine python-3.12.4.exe
#
#


block_cipher = None

a = Analysis(
    ['websiteapp/webapp.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('websiteapp/icons/default.png', 'websiteapp/icons'),
        ('websiteapp/icons/logo.png', 'websiteapp/icons'),
    ],
    hiddenimports=['websiteapp.const', 'PySide6', 'PyQtWebEngine'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,

    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='webapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='webapp',
)
