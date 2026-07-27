#!/usr/bin/env python3
"""Extract hyphenation from cloned KBBI repository in WSL"""

import json
import os
from pathlib import Path

print('=== KBBI VI Hyphenation Extractor (WSL) ===')
print()

# Path to cloned repo in WSL
word_details = Path('/tmp/kbbi-harvester-cdn/word-details')

if not word_details.exists():
    print(f"ERROR: {word_details} not found!")
    print("Please clone the repo first:")
    print("  git clone --depth 1 https://github.com/Naandalist/kbbi-harvester-cdn.git /tmp/kbbi-harvester-cdn")
    exit(1)

all_hyphenations = []
hyphenation_dict = {}

for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    letter_dir = word_details / letter
    if not letter_dir.exists():
        continue
    
    json_files = list(letter_dir.glob('*.json'))
    print(f'{letter}: {len(json_files)} files...', end=' ', flush=True)
    
    count = 0
    for jf in json_files:
        try:
            with open(jf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            word = data.get('word', '')
            for entry in data.get('entries', []):
                nama = entry.get('nama', '')
                if nama:
                    all_hyphenations.append({
                        'word': word, 
                        'hyphenation': nama,
                        'id': entry.get('id', ''),
                        'nomor': entry.get('nomor', '')
                    })
                    if word not in hyphenation_dict:
                        hyphenation_dict[word] = nama
                    count += 1
        except Exception as e:
            pass
    print(f'({count} entries)')

print()
print(f'Total entries: {len(all_hyphenations)}')
print(f'Unique words: {len(hyphenation_dict)}')

# Save to Windows-accessible path
out_dir = Path('/mnt/c/Users/anjan/dev/bahasa_indonesia/kbbi')

# Save text format (word<tab>hyphenation)
txt_file = out_dir / 'kbbi_vi_hyphenation.txt'
with open(txt_file, 'w', encoding='utf-8') as f:
    for h in all_hyphenations:
        f.write(f"{h['word']}\t{h['hyphenation']}\n")
print(f'Saved: {txt_file}')

# Save full JSON array
json_file = out_dir / 'kbbi_vi_hyphenation.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(all_hyphenations, f, ensure_ascii=False, indent=2)
print(f'Saved: {json_file}')

# Save dict JSON (word -> hyphenation)
dict_file = out_dir / 'kbbi_vi_hyphenation_dict.json'
with open(dict_file, 'w', encoding='utf-8') as f:
    json.dump(hyphenation_dict, f, ensure_ascii=False, indent=2)
print(f'Saved: {dict_file}')

# Show samples
print()
print('Sample entries:')
items = list(hyphenation_dict.items())
for word, hyph in items[:20]:
    print(f'  {word:30} -> {hyph}')
