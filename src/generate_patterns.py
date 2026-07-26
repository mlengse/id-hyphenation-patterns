#!/usr/bin/env python3
"""
Generate hyphenation patterns from the hyphenated word dictionary (id.dic).

This script generates TeX hyphenation patterns directly from the hyphenated word list,
without using patgen. It uses a simple but effective approach:

1. Extract all syllable boundaries from the dictionary
2. Generate patterns for common transitions
3. Output in TeX \patterns{} format

This is a simpler alternative to patgen when patgen configuration is problematic.
"""

import re
from collections import defaultdict
import os

def load_dictionary(filepath):
    """Load hyphenated words from id.dic file."""
    words = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word:
                continue
            # Skip entries with spaces (phrases), starting/ending with -, or with non-Latin chars
            if ' ' in word or word.startswith('-') or word.endswith('-'):
                continue
            # Only keep words with basic Latin alphabet
            clean = word.replace('-', '')
            if re.match(r'^[a-z]+$', clean):
                words.append(word)
    return words

def extract_patterns(hyphenated_words, min_pattern_len=2, max_pattern_len=7):
    """
    Extract hyphenation patterns from hyphenated words.
    
    For each hyphenation point, we extract context patterns that indicate
    where hyphenation should or shouldn't occur.
    """
    # Patterns that encourage hyphenation (odd number = break point)
    break_patterns = defaultdict(int)
    # Patterns that discourage hyphenation (even number = no break)
    nobreak_patterns = defaultdict(int)
    
    for word in hyphenated_words:
        syllables = word.split('-')
        if len(syllables) < 2:
            continue
            
        # Build the word with position markers
        full_word = ''.join(syllables)
        positions = []  # List of hyphenation positions
        pos = 0
        for syl in syllables[:-1]:
            pos += len(syl)
            positions.append(pos)
        
        # For each position in the word, extract patterns
        for i in range(len(full_word) + 1):
            is_break = i in positions
            
            # Extract patterns of various lengths centered around this position
            for plen in range(min_pattern_len, max_pattern_len + 1):
                start = max(0, i - plen // 2)
                end = min(len(full_word), start + plen)
                if end - start < min_pattern_len:
                    continue
                    
                pattern_chars = full_word[start:end]
                relative_pos = i - start
                
                if relative_pos <= 0 or relative_pos >= len(pattern_chars):
                    continue
                
                # Create pattern with digit indicating break position
                if is_break:
                    break_patterns[(pattern_chars, relative_pos)] += 1
                else:
                    nobreak_patterns[(pattern_chars, relative_pos)] += 1
    
    return break_patterns, nobreak_patterns

def generate_tex_patterns(break_patterns, nobreak_patterns, min_count=3):
    """
    Generate TeX hyphenation patterns.
    
    TeX pattern format: letters with digits between them
    - Odd digit = hyphenation allowed
    - Even digit = hyphenation forbidden
    - Higher digit overrides lower
    """
    patterns = []
    
    # Process break patterns (odd numbers encourage breaks)
    for (chars, pos), count in break_patterns.items():
        if count < min_count:
            continue
        # Check if this conflicts with a stronger nobreak pattern
        nobreak_count = nobreak_patterns.get((chars, pos), 0)
        if nobreak_count > count:
            continue
        
        # Determine pattern strength (1, 3, 5, 7 for breaks)
        strength = min(7, 1 + 2 * (count // 10))
        
        # Build pattern string
        pattern = chars[:pos] + str(strength) + chars[pos:]
        patterns.append(pattern)
    
    # Process nobreak patterns where needed (even numbers prevent breaks)
    for (chars, pos), count in nobreak_patterns.items():
        if count < min_count:
            continue
        break_count = break_patterns.get((chars, pos), 0)
        if break_count >= count:
            continue
        
        # Even numbers (2, 4, 6) prevent breaks
        strength = min(6, 2 + 2 * (count // 20))
        
        pattern = chars[:pos] + str(strength) + chars[pos:]
        patterns.append(pattern)
    
    return sorted(set(patterns))

def write_tex_file(patterns, output_file, version="1.0", date="2025/12/20"):
    """Write patterns in TeX format."""
    header = f"""% title: Hyphenation patterns for Bahasa Indonesia
% copyright: Copyright (C) 2025 Generated from KBBI data
% notice: This file contains hyphenation patterns for Indonesian.
% language:
%     name: Bahasa Indonesia, Indonesian
%     tag: id
% version: {version} <{date}>
% licence:
%     - This file is available under MIT license
% hyphenmins:
%     typesetting:
%         left: 2
%         right: 2
% ==========================================

\\patterns{{%
"""
    
    footer = """}
\\hyphenation{}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header)
        
        # Write patterns in lines of reasonable length
        line = ""
        for p in patterns:
            if len(line) + len(p) + 1 > 75:
                f.write(line.strip() + "\n")
                line = p + " "
            else:
                line += p + " "
        if line:
            f.write(line.strip() + "\n")
        
        f.write(footer)
    
    print(f"Written {len(patterns)} patterns to {output_file}")

def main():
    input_file = 'id.dic'
    output_file = 'hyph-id-new.tex'
    
    print("Loading dictionary...")
    words = load_dictionary(input_file)
    print(f"Loaded {len(words)} hyphenated words")
    
    print("Extracting patterns...")
    break_pats, nobreak_pats = extract_patterns(words)
    print(f"Found {len(break_pats)} break patterns, {len(nobreak_pats)} nobreak patterns")
    
    print("Generating TeX patterns...")
    patterns = generate_tex_patterns(break_pats, nobreak_pats, min_count=2)
    print(f"Generated {len(patterns)} patterns")
    
    print("Writing output file...")
    write_tex_file(patterns, output_file)
    print("Done!")

if __name__ == '__main__':
    main()
