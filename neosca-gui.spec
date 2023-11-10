# vim:ft=python

a = Analysis(
    ["src/neosca_gui/ng_main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (
            "src/neosca_gui/neosca/data/anc_all_count.pickle.lzma",
            "neosca_gui/neosca/data/anc_all_count.pickle.lzma",
        ),
        (
            "src/neosca_gui/neosca/data/bnc_all_filtered.pickle.lzma",
            "neosca_gui/neosca/data/bnc_all_filtered.pickle.lzma",
        ),
        (
            "src/neosca_gui/neosca/data/structure_data.json",
            "neosca_gui/neosca/data/structure_data.json",
        ),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="neosca-gui",
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
    # Additional options
    contents_directory="libs",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="neosca-gui",
)
