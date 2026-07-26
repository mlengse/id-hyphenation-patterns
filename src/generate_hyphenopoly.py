#!/usr/bin/env python3
"""
Generate Hyphenopoly JSON format directly from patterns.
Avoids line ending issues with tex2json.js on Windows.
"""

import json
import re

def parse_pattern(pattern_str):
    """
    Parse a TeX pattern string into (chars, digits) arrays.
    Example: "2b1d" -> chars=[98, 100], digits=[2, 1]
    """
    chars = []
    digits = []
    prev_was_char = True
    
    for char in pattern_str:
        code = ord(char)
        if code >= 49 and code <= 57:  # Digit 1-9
            digits.append(code - 48)
            prev_was_char = False
        else:
            chars.append(code)
            if prev_was_char:
                digits.append(0)
            prev_was_char = True
    
    return chars, digits

def main():
    # Read patterns
    patterns = []
    
    with open('output/hyph-id.pat.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and re.search(r'[a-zA-Z]', line):
                chars, digits = parse_pattern(line)
                patterns.append([line, chars, digits])
    
    # Build JSON structure
    data = {
        "chr": [
            "aA", "bB", "cC", "dD", "eE", "fF", "gG", "hH", "iI", "jJ",
            "kK", "lL", "mM", "nN", "oO", "pP", "qQ", "rR", "sS", "tT",
            "uU", "vV", "wW", "xX", "yY", "zZ"
        ],
        "lic": "Hyphenation patterns for Bahasa Indonesia\nCopyright (C) 2025 Generated from KBBI 2025 data\nBased on KBBI hyphenation data with 72,000+ verified words.\nlicence: MIT",
        "lrmin": [2, 2],
        "pat": patterns
    }
    
    # Write JSON
    output_path = 'Hyphenopoly/lang/id/src/id.json'
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Generated {output_path}")
    print(f"  Characters: {len(data['chr'])}")
    print(f"  Patterns: {len(patterns)}")
    
    # Verify first few patterns
    print("\nFirst 5 patterns:")
    for p in patterns[:5]:
        print(f"  {p[0]}: chars={p[1][:5]}..., digits={p[2][:5]}...")

if __name__ == '__main__':
    main()
