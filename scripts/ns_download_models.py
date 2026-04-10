#!/usr/bin/env python3

import sys
import stanza
from neosca.ns_consts import STANZA_MODEL_DIR
from neosca.ns_settings.ns_settings_default import SUPPORTED_LANGUAGES


def download_all_models():
    """Download all supported language models."""
    print("Downloading Stanza models for all supported European languages...")
    print(f"Model directory: {STANZA_MODEL_DIR}")
    print()
    
    for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
        print(f"Downloading {lang_name} ({lang_code})...")
        try:
            stanza.download(lang_code, model_dir=str(STANZA_MODEL_DIR))
            print(f"  ✓ {lang_name} model downloaded successfully")
        except Exception as e:
            print(f"  ✗ Failed to download {lang_name}: {e}")
        print()
    
    print("Download complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Download specific language
        lang = sys.argv[1]
        if lang in SUPPORTED_LANGUAGES:
            print(f"Downloading {SUPPORTED_LANGUAGES[lang]} ({lang})...")
            stanza.download(lang, model_dir=str(STANZA_MODEL_DIR))
            print("Download complete!")
        else:
            print(f"Error: Unsupported language '{lang}'")
            print(f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}")
            sys.exit(1)
    else:
        # Download all supported languages
        download_all_models()
