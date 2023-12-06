# vim:ft=python

import PyInstaller

from src.neosca_gui.ng_platform_info import IS_MAC

binaries = []
datas = []

# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/utils/wl_packaging.spec#L33
# > Fix PyTorch
# > See: https://github.com/pyinstaller/pyinstaller/issues/7485#issuecomment-1465155018
if IS_MAC:
    binaries.extend(PyInstaller.utils.hooks.collect_dynamic_libs("torch"))

# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/utils/wl_packaging.spec#L66
datas.extend(
    [
        # Stanza
        ("src/neosca_gui/data/stanza_resources/resources.json", "neosca/data/stanza_resources/"),
        ("src/neosca_gui/data/stanza_resources/en/backward_charlm", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/constituency", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/forward_charlm", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/lemma", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/mwt", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/pos", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/pretrain", "neosca/data/stanza_resources/en/"),
        ("src/neosca_gui/data/stanza_resources/en/tokenize", "neosca/data/stanza_resources/en/"),
        # Others
        ("src/neosca_gui/data/sca_structure_data.json", "neosca/data/"),
        ("src/neosca_gui/data/anc_all_count.pickle.lzma", "neosca/data/"),
        ("src/neosca_gui/data/bnc_all_filtered.pickle.lzma", "neosca/data/"),
        ("src/neosca_gui/data/citing.json", "neosca/data/"),
        ("src/neosca_gui/data/ng_style.qss", "neosca/data/"),
    ]
)

a = Analysis(
    ["src/neosca_gui/__main__.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    name="NeoSCA",
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
    name="NeoSCA",
)
# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/utils/wl_packaging.spec#L163
# > Bundle application on macOS
# > Reference: https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
if IS_MAC:
    from src.neosca_gui.ng_about import __version__

    app = BUNDLE(
        coll,
        name="Wordless.app",
        bundle_identifier=None,
        # References:
        #     https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html
        #     https://developer.apple.com/documentation/bundleresources/information_property_list
        info_plist={
            "CFBundleName": "NeoSCA",
            "CFBundleDisplayName": "NeoSCA",
            "CFBundleExecutable": "NeoSCA",
            "CFBundlePackageType": "APPL",
            "CFBundleVersion": __version__,
            "CFBundleShortVersionString": __version__,
            "CFBundleInfoDictionaryVersion": __version__,
            # > Required by Retina displays on macOS
            # > References:
            #     > https://developer.apple.com/documentation/bundleresources/information_property_list/nshighresolutioncapable
            #     > https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
            #     > https://doc.qt.io/qt-5/highdpi.html#macos-and-ios
            "NSHighResolutionCapable": True,
            "NSPrincipalClass": "NSApplication",
        },
    )
