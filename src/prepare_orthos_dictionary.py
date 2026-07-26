#!/usr/bin/env python3
"""
Prepare id.dic for orthos.js pattern generation.

This script:
1. Reads id.dic (format: hy-phe-na-ted)
2. Filters out problematic entries (abbreviations, special chars, etc.)
3. Outputs clean word list for orthos consumption
"""

import re
import os

def main():
    input_file = 'id.dic'
    output_file = 'id_orthos.dic'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
    
    valid_words = []
    skipped = {
        'abbreviations': 0,
        'special_chars': 0,
        'no_hyphen': 0,
        'too_short': 0,
        'prefix_only': 0,
        'suffix_only': 0,
        'spaces': 0,
    }
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            
            # Skip words with spaces (multi-word entries)
            if ' ' in word:
                skipped['spaces'] += 1
                continue
            
            # Skip abbreviations (all uppercase between hyphens or mixed case patterns)
            clean = word.replace('-', '')
            if clean.isupper() or re.match(r'^[A-Z]+-[A-Z]*$', clean):
                skipped['abbreviations'] += 1
                continue
            
            # Skip entries with special characters (apostrophe, dot in abbreviations, etc.)
            if re.search(r"[.'`]", word):
                skipped['special_chars'] += 1
                continue
            
            # Skip prefix-only entries (starting with -)
            if word.startswith('-'):
                skipped['prefix_only'] += 1
                continue
            
            # Skip suffix-only entries (ending with -)
            if word.endswith('-'):
                skipped['suffix_only'] += 1
                continue
            
            # Skip entries without hyphenation (no actual syllable breaks)
            if '-' not in word:
                skipped['no_hyphen'] += 1
                continue
            
            # Skip very short entries (less than 3 chars without hyphens)
            if len(clean) < 3:
                skipped['too_short'] += 1
                continue
            
            # Valid entry - convert to lowercase for consistent pattern learning
            valid_words.append(word.lower())
    
    # Sort for consistent output
    valid_words.sort()
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        for word in valid_words:
            f.write(word + '\n')
    
    # Report
    total_input = sum(skipped.values()) + len(valid_words)
    print(f"Dictionary Preparation Complete")
    print(f"=" * 40)
    print(f"Input:  {input_file} ({total_input} entries)")
    print(f"Output: {output_file} ({len(valid_words)} entries)")
    print()
    print("Skipped entries:")
    for reason, count in sorted(skipped.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  - {reason}: {count}")
    print()
    print(f"Valid entries: {len(valid_words)} ({100*len(valid_words)/total_input:.1f}%)")

if __name__ == '__main__':
    main()
