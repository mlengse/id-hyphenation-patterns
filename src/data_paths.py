#!/usr/bin/env python3
"""
Shared workspace paths for the id-hyphenation-patterns pipeline.

All scripts should import DATA, OUTPUT etc. from here instead of hardcoding
relative paths, so the pipeline keeps working as the workspace evolves.

Layout (relative to this file, src/):
    src/../..                 = pattern/               (sibling repos)
    src/../../..              = dev/bahasa/
    src/../../.. /data/kbbi-harvester-cdn/hyphenation  = pinned input data
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
OUTPUT = ROOT / 'output'
RULES = ROOT / 'rules'

BAHASA = SRC.parents[2]
DATA = BAHASA / 'data' / 'kbbi-harvester-cdn' / 'hyphenation'

ID_DIC = DATA / 'id.dic'
ID_ORTHOS_DIC = DATA / 'id_orthos.dic'
ID_WORDS_DIC = DATA / 'id_words.dic'
PEMENGGALAN_TXT = DATA / 'kbbi_pemenggalan.txt'
