#!/usr/bin/env python3
"""
Shared workspace paths for the id-hyphenation-patterns pipeline.

Provides fallback resolution for dictionary data paths from output/ or GitHub.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
OUTPUT = ROOT / 'output'
RULES = ROOT / 'rules'

# Check workspace location or local output fallbacks
BAHASA = SRC.parents[2] if len(SRC.parents) > 2 else ROOT
DATA_EXT = BAHASA / 'data' / 'kbbi-harvester-cdn' / 'hyphenation'

DATA = DATA_EXT if DATA_EXT.exists() else OUTPUT

ID_DIC = DATA / 'id.dic' if (DATA / 'id.dic').exists() else (OUTPUT / 'indonesia_clean.dic')
ID_ORTHOS_DIC = DATA / 'id_orthos.dic' if (DATA / 'id_orthos.dic').exists() else (OUTPUT / 'indonesia_pure.dic')
ID_WORDS_DIC = DATA / 'id_words.dic' if (DATA / 'id_words.dic').exists() else (OUTPUT / 'indonesia_training.dic')
PEMENGGALAN_TXT = DATA / 'kbbi_pemenggalan.txt' if (DATA / 'kbbi_pemenggalan.txt').exists() else (OUTPUT / 'ground_truth.txt')
