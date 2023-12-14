# vim:ft=python

import sys
from pathlib import Path

import PyInstaller

sys.path.insert(0, str(Path(".").parent.absolute() / "src"))
from neosca.ns_platform_info import IS_MAC, IS_LINUX, IS_WINDOWS  # noqa: I001, E402
from neosca.ns_about import __title__  # noqa: I001, E402
from neosca import ICON_PATH, ICON_MAC_PATH  # noqa: I001, E402

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
        ("./data/stanza_resources/resources.json", "data/stanza_resources/"),
        (
            "./data/stanza_resources/en/backward_charlm/",
            "./data/stanza_resources/en/backward_charlm/",
        ),
        (
            "./data/stanza_resources/en/constituency/",
            "./data/stanza_resources/en/constituency/",
        ),
        (
            "./data/stanza_resources/en/forward_charlm/",
            "./data/stanza_resources/en/forward_charlm/",
        ),
        ("./data/stanza_resources/en/lemma/", "data/stanza_resources/en/lemma/"),
        ("./data/stanza_resources/en/mwt/", "data/stanza_resources/en/mwt/"),
        ("./data/stanza_resources/en/pos/", "data/stanza_resources/en/pos/"),
        ("./data/stanza_resources/en/pretrain/", "data/stanza_resources/en/pretrain/"),
        ("./data/stanza_resources/en/tokenize/", "data/stanza_resources/en/tokenize/"),
        # Others
        ("./data/ns_syntactic_structures.json", "data/"),
        ("./data/anc_all_count.pickle.lzma", "data/"),
        ("./data/bnc_all_filtered.pickle.lzma", "data/"),
        ("./data/citing.json", "data/"),
        ("./data/ns_style.qss", "data/"),
        ("./imgs/", "imgs/"),
    ]
)

# Icons
if IS_WINDOWS or IS_LINUX:
    icon = str(ICON_PATH)
elif IS_MAC:
    icon = str(ICON_MAC_PATH)
else:
    assert False, "Unsupported platform"

a = Analysis(
    ["src/neosca/__main__.py"],
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
    name=__title__,
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
    icon=icon,
    contents_directory="libs",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=__title__,
)
# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/utils/wl_packaging.spec#L163
# > Bundle application on macOS
# > Reference: https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
if IS_MAC:
    from neosca.ns_about import __version__

    app = BUNDLE(
        coll,
        name=f"{__title__}.app",
        icon=icon,
        bundle_identifier=None,
        # References:
        #     https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html
        #     https://developer.apple.com/documentation/bundleresources/information_property_list
        info_plist={
            "CFBundleName": __title__,
            "CFBundleDisplayName": __title__,
            "CFBundleExecutable": __title__,
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
