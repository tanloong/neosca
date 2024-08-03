#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

uv pip freeze --strict |\
  # wheel not found for windows, but will be installed as dependency of pyqt5 if any.
  # exclude this to avoid sync failure on windows
  grep -Ewv 'pyqt5-qt5' |\
  grep -Ewv "$(gawk '{ if (match($0, /^[a-z]+/) > 0) { name = substr($0, RSTART, RLENGTH); s = length(s) > 0 ? s "|" name : name } } END { printf  "(" s ")" }' requirements-dev.txt)" |\
  sed -E '/^torch\b/i--find-links https://download.pytorch.org/whl/torch_stable.html' > requirements.txt
