#!/usr/bin/env python3
"""
Stage 1: Add initial syllable patterns to improve accuracy.

The main error type is missing hyphens at word beginnings like:
- a-bo-ri-gin → abo-ri-gin (missing a-)
- i-bu → ibu (missing i-)

This script:
1. Reads current patterns
2. Adds initial syllable patterns (.a1, .i1, etc.)
3. Tests and reports improvement
"""

import os
import re
from collections import defaultdict

def generate_initial_patterns():
    """Generate patterns for initial vowel syllables."""
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    # Digraphs that should stay together
    digraphs = ['ng', 'ny', 'kh', 'sy']
    
    patterns = []
    
    # Basic vowel at start encourages break after
    for v in vowels:
        patterns.append(f'.{v}1')  # .a1 = break after 'a' at word start
    
    # Vowel + consonant at start
    for v in vowels:
        for c in consonants:
            patterns.append(f'.{v}1{c}')  # .a1b = break between 'a' and 'b' at start
    
    # Vowel + digraph (don't break digraph)
    for v in vowels:
        for dg in digraphs:
            patterns.append(f'.{v}1{dg}')  # .a1ng = break before 'ng'
    
    # Double vowel at start (break between)
    for v1 in vowels:
        for v2 in vowels:
            if v1 != v2:  # Skip same vowel
                patterns.append(f'.{v1}1{v2}')  # .a1i = break between 'a' and 'i'
    
    # Special patterns for common prefixes
    prefixes_break_after = [
        '.ber1',  # ber-jalan
        '.ter1',  # ter-bawa
        '.per1',  # per-gi
        '.mem1',  # mem-beli
        '.men1',  # men-cari
        '.meng1', # meng-ambil
        '.meny1', # meny-apu
        '.pem1',  # pem-bina
        '.pen1',  # pen-didik
        '.peng1', # peng-ajar
        '.peny1', # peny-ebab
        '.di1',   # di-ambil
        '.ke1',   # ke-luar
        '.se1',   # se-orang
    ]
    patterns.extend(prefixes_break_after)
    
    return sorted(set(patterns))


def load_patterns(filepath):
    """Load existing patterns."""
    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            p = line.strip()
            if p:
                patterns.append(p)
    return patterns


def save_patterns(patterns, filepath):
    """Save patterns to file."""
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        for p in patterns:
            f.write(p + '\n')


def main():
    pattern_file = os.path.join('output', 'hyph-id.pat.txt')
    backup_file = os.path.join('output', 'hyph-id.pat.backup.txt')
    
    if not os.path.exists(pattern_file):
        print(f"Error: {pattern_file} not found")
        return
    
    print("=" * 60)
    print("STAGE 1: ADD INITIAL SYLLABLE PATTERNS")
    print("=" * 60)
    
    # Backup original
    print(f"\nBacking up to {backup_file}...")
    existing = load_patterns(pattern_file)
    save_patterns(existing, backup_file)
    print(f"  {len(existing)} existing patterns backed up")
    
    # Generate new patterns
    print("\nGenerating initial syllable patterns...")
    new_patterns = generate_initial_patterns()
    print(f"  {len(new_patterns)} new patterns generated")
    
    # Merge (new patterns first for priority)
    combined = new_patterns + [p for p in existing if p not in new_patterns]
    combined = sorted(set(combined))
    
    # Save
    print(f"\nSaving {len(combined)} patterns to {pattern_file}...")
    save_patterns(combined, pattern_file)
    
    print(f"\n  Added: {len(combined) - len(existing)} new patterns")
    print(f"  Total: {len(combined)} patterns")
    
    print("\n" + "-" * 60)
    print("Run test_full_dictionary.py to check accuracy")
    print("-" * 60)


if __name__ == '__main__':
    main()
