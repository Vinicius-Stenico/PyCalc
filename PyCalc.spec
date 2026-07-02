# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path.cwd()

datas = [
    (str(ROOT / "configuracoes.json"), "."),
    (str(ROOT / "icons" / "PyCalc_main.png"), "icons"),
    (str(ROOT / "icons" / "PyCalc_main.ico"), "icons"),
    (str(ROOT / "icons" / "modos_icons"), "icons/modos_icons"),
    (str(ROOT / "icons" / "conversores_icons"), "icons/conversores_icons"),
]

a = Analysis(
    ["calculadora.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "matplotlib.backends.backend_tkagg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PyCalc",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "icons" / "PyCalc_main.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PyCalc",
)
