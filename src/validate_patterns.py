#!/usr/bin/env python3
"""
Validate existing hyphen library patterns against the 2025 dictionary (id.dic).
This will help identify if existing patterns are accurate or need updating.
"""

import re
import os
from data_paths import ID_DIC

def load_id_dic(filepath):
    """Load hyphenated words from id.dic as reference."""
    words = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            # Skip entries with spaces (phrases), starting/ending with -
            if ' ' in word or word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '').lower()
            # Only keep words with basic Latin alphabet
            if re.match(r'^[a-z]+$', clean):
                words[clean] = word.lower()
    return words

def simple_syllabify(word, vowels='aiueo'):
    """
    Simple syllabification based on EYD V rules.
    Returns word with - at syllable boundaries.
    """
    if len(word) < 2:
        return word
    
    # Digraphs that should not be split
    digraphs = ['ng', 'ny', 'kh', 'sy']
    
    result = []
    i = 0
    while i < len(word):
        # Check for digraph
        if i < len(word) - 1:
            pair = word[i:i+2]
            if pair in digraphs:
                result.append(pair)
                i += 2
                continue
        result.append(word[i])
        i += 1
    
    # Now apply V-V, V-C-V, V-C-C-V rules
    output = []
    for i, char in enumerate(result):
        output.append(char)
        if i < len(result) - 1:
            # Check if we should add a hyphen after this position
            current = char.lower() if len(char) == 1 else char[0].lower()
            next_char = result[i+1].lower() if len(result[i+1]) == 1 else result[i+1][0].lower()
            
            # V-V: vowel followed by vowel
            if current in vowels and next_char in vowels:
                output.append('-')
            # V-C-V: vowel followed by consonant followed by vowel
            elif current in vowels and next_char not in vowels:
                if i < len(result) - 2:
                    after_next = result[i+2].lower() if len(result[i+2]) == 1 else result[i+2][0].lower()
                    if after_next in vowels:
                        output.append('-')
    
    return ''.join(output)

def compare_hyphenation(reference, generated):
    """Compare two hyphenated forms."""
    # Normalize both
    ref_clean = reference.replace('-', '')
    gen_clean = generated.replace('-', '')
    
    if ref_clean != gen_clean:
        return 'MISMATCH_WORD'
    
    if reference == generated:
        return 'MATCH'
    
    return 'DIFF'

def main():
    # Load reference dictionary
    print("Loading reference dictionary (id.dic)...")
    reference = load_id_dic(str(ID_DIC))
    print(f"Loaded {len(reference)} words")
    
    # Test sample words against simple algorithm
    sample_words = [
        'makanan',
        'seudati', 
        'instrumen',
        'mengunci',
        'bangkrut',
        'berjalan',
        'pertumbuhan',
        'saudara',
        'musyawarah'
    ]
    
    print("\n" + "="*60)
    print("Sample comparison:")
    print("="*60)
    print(f"{'Word':<20} {'Reference (id.dic)':<20} {'Simple Algo':<20}")
    print("-"*60)
    
    for word in sample_words:
        ref = reference.get(word, 'NOT_FOUND')
        generated = simple_syllabify(word)
        status = compare_hyphenation(ref, generated) if ref != 'NOT_FOUND' else 'N/A'
        print(f"{word:<20} {ref:<20} {generated:<20} [{status}]")
    
    # Statistics
    print("\n" + "="*60)
    print("Running comparison on full dictionary...")
    print("="*60)
    
    match = 0
    diff = 0
    
    for word, ref_hyphen in list(reference.items())[:1000]:  # Test first 1000
        generated = simple_syllabify(word)
        status = compare_hyphenation(ref_hyphen, generated)
        if status == 'MATCH':
            match += 1
        elif status == 'DIFF':
            diff += 1
    
    total = match + diff
    if total > 0:
        print(f"Matches: {match} ({100*match/total:.1f}%)")
        print(f"Differences: {diff} ({100*diff/total:.1f}%)")

if __name__ == '__main__':
    main()
