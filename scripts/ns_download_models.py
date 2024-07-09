#!/usr/bin/env python3

import stanza
from neosca.ns_consts import STANZA_MODEL_DIR

stanza.download("en", model_dir=str(STANZA_MODEL_DIR))
