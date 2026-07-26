#!/usr/bin/env python3
"""
Stage 4: Generate minimal exception list with only failing words.

Instead of including all 72,000 words as exceptions, only include
the ~7,000 words where patterns fail.
"""

import os
import re

class PatternHyphenator:
    """Hyphenator using TeX-style patterns."""
    
    def __init__(self, pattern_file, left_min=2, right_min=2):
        self.left_min = left_min
        self.right_min = right_min
        self.patterns = {}
        self.load_patterns(pattern_file)
    
    def load_patterns(self, pattern_file):
        with open(pattern_file, 'r', encoding='utf-8') as f:
            for line in f:
                pattern = line.strip()
                if not pattern:
                    continue
                letters = []
                values = [0]
                for c in pattern:
                    if c.isdigit():
                        values[-1] = int(c)
                    else:
                        letters.append(c)
                        values.append(0)
                key = ''.join(letters)
                self.patterns[key] = values
    
    def hyphenate(self, word):
        word = word.lower()
        work = '.' + word + '.'
        n = len(work)
        values = [0] * (n + 1)
        
        for start in range(n):
            for end in range(start + 1, min(n + 1, start + 20)):
                substr = work[start:end]
                if substr in self.patterns:
                    pat_values = self.patterns[substr]
                    for k, v in enumerate(pat_values):
                        pos = start + k
                        if pos < len(values):
                            values[pos] = max(values[pos], v)
        
        result = []
        for i, char in enumerate(word):
            if i > 0:
                if values[i + 1] % 2 == 1:
                    if i >= self.left_min and (len(word) - i) >= self.right_min:
                        result.append('-')
            result.append(char)
        
        return ''.join(result)


def load_dictionary(dict_file):
    dictionary = {}
    with open(dict_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word or ' ' in word:
                continue
            if word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '')
            if '-' in word and clean.isalpha():
                dictionary[clean] = word
    return dictionary


def main():
    pattern_file = os.path.join('output', 'hyph-id.pat.txt')
    dict_file = 'id.dic'
    output_file = os.path.join('output', 'hyph-id.exceptions.txt')
    
    print("=" * 60)
    print("STAGE 4: GENERATE MINIMAL EXCEPTION LIST")
    print("=" * 60)
    
    print("\nLoading patterns...")
    hyphenator = PatternHyphenator(pattern_file)
    print(f"  {len(hyphenator.patterns):,} patterns")
    
    print("\nLoading dictionary...")
    dictionary = load_dictionary(dict_file)
    print(f"  {len(dictionary):,} words")
    
    print("\nTesting each word...")
    exceptions = []
    correct = 0
    
    for word, expected in dictionary.items():
        got = hyphenator.hyphenate(word)
        if got == expected:
            correct += 1
        else:
            exceptions.append(expected)
    
    print(f"\n  Patterns correct: {correct:,} ({100*correct/len(dictionary):.2f}%)")
    print(f"  Need exceptions: {len(exceptions):,} ({100*len(exceptions)/len(dictionary):.2f}%)")
    
    # Save minimal exceptions
    print(f"\nSaving exceptions to {output_file}...")
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        for word in sorted(exceptions):
            f.write(word + '\n')
    
    print(f"  {len(exceptions):,} exceptions saved")
    
    # Update hyph-id.hyp.txt with minimal list
    hyp_file = os.path.join('output', 'hyph-id.hyp.txt')
    print(f"\nUpdating {hyp_file}...")
    with open(hyp_file, 'w', encoding='utf-8', newline='\n') as f:
        for word in sorted(exceptions):
            f.write(word + '\n')
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"""
  Total words:      {len(dictionary):,}
  Pattern coverage: {correct:,} ({100*correct/len(dictionary):.2f}%)
  Exceptions:       {len(exceptions):,} ({100*len(exceptions)/len(dictionary):.2f}%)
  
  Combined accuracy: 100%
  
  File size reduction:
    - Full exceptions:    72,000 words
    - Minimal exceptions: {len(exceptions):,} words
    - Reduction:          {100 - 100*len(exceptions)/72000:.1f}%
""")


if __name__ == '__main__':
    main()
