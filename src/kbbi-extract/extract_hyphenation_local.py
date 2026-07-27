#!/usr/bin/env python3
"""
Extract hyphenation data from locally cloned KBBI Harvester CDN repository.
Run this AFTER cloning the repository with:
  git clone https://github.com/Naandalist/kbbi-harvester-cdn.git

This is MUCH faster than downloading files individually.
"""

import json
import os
from pathlib import Path
from typing import Optional

# Configuration - adjust this path to where you cloned the repo
REPO_DIR = Path("kbbi-harvester-cdn")
WORD_DETAILS_DIR = REPO_DIR / "word-details"
OUTPUT_HYPHENATION_TXT = Path("kbbi_vi_hyphenation.txt")
OUTPUT_HYPHENATION_JSON = Path("kbbi_vi_hyphenation.json")
OUTPUT_HYPHENATION_DICT = Path("kbbi_vi_hyphenation_dict.json")

def extract_hyphenation_from_file(json_file: Path) -> list:
    """Extract hyphenation patterns from a word detail JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        hyphenations = []
        word = data.get('word', '')
        
        for entry in data.get('entries', []):
            nama = entry.get('nama', '')
            entry_id = entry.get('id', '')
            nomor = entry.get('nomor', '')
            
            if nama:
                hyphenations.append({
                    'word': word,
                    'hyphenation': nama,
                    'id': entry_id,
                    'nomor': nomor
                })
        
        return hyphenations
    except Exception as e:
        return []

def main():
    print("=== KBBI VI Hyphenation Extractor (Local) ===\n")
    
    if not WORD_DETAILS_DIR.exists():
        print(f"ERROR: Directory not found: {WORD_DETAILS_DIR}")
        print("\nPlease clone the repository first:")
        print("  git clone --depth 1 https://github.com/Naandalist/kbbi-harvester-cdn.git")
        return
    
    all_hyphenations = []
    hyphenation_dict = {}  # word -> hyphenation mapping
    
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    for letter in letters:
        letter_dir = WORD_DETAILS_DIR / letter
        if not letter_dir.exists():
            print(f"Skipping {letter} - directory not found")
            continue
        
        # Get all JSON files in this directory
        json_files = list(letter_dir.glob("*.json"))
        print(f"Processing {letter}: {len(json_files)} files...", end=" ")
        
        letter_count = 0
        for json_file in json_files:
            hyphenations = extract_hyphenation_from_file(json_file)
            all_hyphenations.extend(hyphenations)
            letter_count += len(hyphenations)
            
            # Add to dictionary (use first entry for each word)
            for h in hyphenations:
                word = h['word']
                if word not in hyphenation_dict:
                    hyphenation_dict[word] = h['hyphenation']
        
        print(f"✓ ({letter_count} entries)")
    
    # Save results
    print(f"\n=== Saving Results ===")
    
    # 1. Save as tab-separated text (word<tab>hyphenation)
    with open(OUTPUT_HYPHENATION_TXT, 'w', encoding='utf-8') as f:
        for h in all_hyphenations:
            f.write(f"{h['word']}\t{h['hyphenation']}\n")
    print(f"✓ Text format: {OUTPUT_HYPHENATION_TXT}")
    
    # 2. Save full data as JSON array
    with open(OUTPUT_HYPHENATION_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_hyphenations, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON array: {OUTPUT_HYPHENATION_JSON}")
    
    # 3. Save as simple word->hyphenation dictionary
    with open(OUTPUT_HYPHENATION_DICT, 'w', encoding='utf-8') as f:
        json.dump(hyphenation_dict, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON dict: {OUTPUT_HYPHENATION_DICT}")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Total hyphenation entries: {len(all_hyphenations)}")
    print(f"Unique words: {len(hyphenation_dict)}")
    
    # Show samples
    print(f"\nSample entries:")
    for h in all_hyphenations[:20]:
        print(f"  {h['word']:20} -> {h['hyphenation']}")

if __name__ == "__main__":
    main()
