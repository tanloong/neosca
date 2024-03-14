#!/usr/bin/env python3

import stanza
from neosca import STANZA_MODEL_DIR

stanza.download("en", model_dir=str(STANZA_MODEL_DIR), resources_url="stanford")
