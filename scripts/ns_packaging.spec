# vim:ft=python

import platform
import sys
from pathlib import Path

import PyInstaller

sys.path.insert(0, str(Path(".").parent.absolute() / "src"))
from neosca.ns_platform_info import IS_MAC, IS_LINUX, IS_WINDOWS  # noqa: I001, E402
from neosca.ns_about import __title__, __version__  # noqa: I001, E402
from neosca import ICON_PATH, ICON_MAC_PATH  # noqa: I001, E402

# https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle

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
        (
            "../src/neosca/ns_data/stanza_resources/resources.json",
            "neosca/ns_data/stanza_resources/",
        ),
        (
            "../src/neosca/ns_data/stanza_resources/en/backward_charlm/",
            "neosca/ns_data/stanza_resources/en/backward_charlm/",
        ),
        (
            "../src/neosca/ns_data/stanza_resources/en/constituency/",
            "neosca/ns_data/stanza_resources/en/constituency/",
        ),
        (
            "../src/neosca/ns_data/stanza_resources/en/forward_charlm/",
            "neosca/ns_data/stanza_resources/en/forward_charlm/",
        ),
        ("../src/neosca/ns_data/stanza_resources/en/lemma/", "neosca/ns_data/stanza_resources/en/lemma/"),
        ("../src/neosca/ns_data/stanza_resources/en/mwt/", "neosca/ns_data/stanza_resources/en/mwt/"),
        ("../src/neosca/ns_data/stanza_resources/en/pos/", "neosca/ns_data/stanza_resources/en/pos/"),
        ("../src/neosca/ns_data/stanza_resources/en/pretrain/", "neosca/ns_data/stanza_resources/en/pretrain/"),
        ("../src/neosca/ns_data/stanza_resources/en/tokenize/", "neosca/ns_data/stanza_resources/en/tokenize/"),
        # Others
        ("../src/neosca/ns_data/l2sca_structures.json", "neosca/ns_data/"),
        ("../src/neosca/ns_data/anc_all_count.pickle.lzma", "neosca/ns_data/"),
        ("../src/neosca/ns_data/bnc_all_filtered.pickle.lzma", "neosca/ns_data/"),
        ("../src/neosca/ns_data/citings.json", "neosca/ns_data/"),
        ("../src/neosca/ns_data/acks.json", "neosca/ns_data/"),
        ("../src/neosca/ns_data/styles.qss", "neosca/ns_data/"),
        ("../src/neosca/ns_data/ns_icon.ico", "neosca/ns_data/"),
        ("../src/neosca/ns_data/ns_icon.icns", "neosca/ns_data/"),
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
    ["../src/neosca/ns_main_gui.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["build", "pyproject_hooks",
              "setuptools",
              "wheel",
              "twine",
              "ruff",
              "viztracer", "objprint",
              "mypy", "mypy-extensions"],
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
    name=f"{__title__}-{__version__}-{'macos' if platform.system() == 'Darwin' else platform.system().lower()}",
)
# https://github.com/BLKSerene/Wordless/blob/1c319ce54be60aa948c89d6d3cdd327cccfc7c15/utils/wl_packaging.spec#L163
# > Bundle application on macOS
# > Reference: https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
if IS_MAC:
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
