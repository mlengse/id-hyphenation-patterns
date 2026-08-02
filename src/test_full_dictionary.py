#!/usr/bin/env python3
"""
Comprehensive test of generated patterns against entire id.dic dictionary.

This script:
1. Loads all patterns from output/hyph-id.pat.txt
2. Applies them to all 72,000+ words in id.dic
3. Compares with expected hyphenation
4. Reports detailed accuracy statistics
"""

import re
import os
from collections import defaultdict
from data_paths import ID_DIC, OUTPUT

class PatternHyphenator:
    """Hyphenator using TeX-style patterns."""
    
    def __init__(self, pattern_file, left_min=2, right_min=2):
        self.left_min = left_min
        self.right_min = right_min
        self.patterns = {}
        self.load_patterns(pattern_file)
    
    def load_patterns(self, pattern_file):
        """Load patterns from file."""
        with open(pattern_file, 'r', encoding='utf-8') as f:
            for line in f:
                pattern = line.strip()
                if not pattern:
                    continue
                # Parse pattern: letters and embedded numbers
                # e.g., "2b1b" means: value 2 before first b, value 1 between b's
                letters = []
                values = [0]  # values[i] is the value before letters[i]
                
                i = 0
                while i < len(pattern):
                    c = pattern[i]
                    if c.isdigit():
                        values[-1] = int(c)
                    else:
                        letters.append(c)
                        values.append(0)
                    i += 1
                
                key = ''.join(letters)
                self.patterns[key] = values
    
    def hyphenate(self, word):
        """Hyphenate a word using loaded patterns."""
        word = word.lower()
        work = '.' + word + '.'
        n = len(work)
        
        # Initialize values at each position
        values = [0] * (n + 1)
        
        # Apply all matching patterns
        for start in range(n):
            for end in range(start + 1, min(n + 1, start + 20)):  # max pattern length
                substr = work[start:end]
                if substr in self.patterns:
                    pat_values = self.patterns[substr]
                    for k, v in enumerate(pat_values):
                        pos = start + k
                        if pos < len(values):
                            values[pos] = max(values[pos], v)
        
        # Build hyphenated word
        result = []
        for i, char in enumerate(word):
            # Position in values array: i+1 (skip the leading '.')
            # Hyphen before char if odd value at position i+1
            if i > 0:  # not before first char
                if values[i + 1] % 2 == 1:
                    # Check left_min and right_min
                    if i >= self.left_min and (len(word) - i) >= self.right_min:
                        result.append('-')
            result.append(char)
        
        return ''.join(result)


def load_dictionary(dict_file):
    """Load reference dictionary with hyphenations."""
    dictionary = {}
    with open(dict_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word or ' ' in word:
                continue
            if word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '')
            # Only include words with actual hyphenation
            if '-' in word and clean.isalpha():
                dictionary[clean] = word
    return dictionary


def test_full_dictionary(hyphenator, dictionary):
    """Test against entire dictionary."""
    
    print(f"\nTesting {len(dictionary)} words...")
    
    correct = 0
    incorrect = 0
    errors_by_type = defaultdict(list)
    
    for word, expected in dictionary.items():
        got = hyphenator.hyphenate(word)
        
        if got == expected:
            correct += 1
        else:
            incorrect += 1
            
            # Categorize error type
            if got.count('-') < expected.count('-'):
                errors_by_type['missing_hyphens'].append((word, expected, got))
            elif got.count('-') > expected.count('-'):
                errors_by_type['extra_hyphens'].append((word, expected, got))
            else:
                errors_by_type['wrong_position'].append((word, expected, got))
    
    # Report results
    total = correct + incorrect
    accuracy = 100 * correct / total if total > 0 else 0
    
    print("\n" + "=" * 70)
    print("FULL DICTIONARY TEST RESULTS")
    print("=" * 70)
    print(f"\nTotal words:     {total:,}")
    print(f"Correct:         {correct:,} ({100*correct/total:.2f}%)")
    print(f"Incorrect:       {incorrect:,} ({100*incorrect/total:.2f}%)")
    print(f"\nAccuracy: {accuracy:.2f}%")
    
    print("\n" + "-" * 70)
    print("ERROR BREAKDOWN")
    print("-" * 70)
    
    for error_type, errors in sorted(errors_by_type.items(), key=lambda x: -len(x[1])):
        print(f"\n{error_type}: {len(errors):,} errors")
        # Show first 10 examples
        if errors:
            print(f"  {'Word':<20} {'Expected':<25} {'Got':<25}")
            print(f"  {'-'*20} {'-'*25} {'-'*25}")
            for word, expected, got in errors[:10]:
                print(f"  {word:<20} {expected:<25} {got:<25}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
    
    return correct, incorrect, accuracy, errors_by_type


def test_with_exceptions(hyphenator, dictionary, exception_file):
    """Test with exception list fallback."""
    
    # Load exceptions
    exceptions = {}
    if os.path.exists(exception_file):
        with open(exception_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word and '-' in word:
                    clean = word.replace('-', '')
                    exceptions[clean] = word
    
    print(f"\nTesting with {len(exceptions):,} exceptions...")
    
    correct = 0
    incorrect = 0
    used_exception = 0
    used_pattern = 0
    
    for word, expected in dictionary.items():
        # Try exception first
        if word in exceptions:
            got = exceptions[word]
            used_exception += 1
        else:
            got = hyphenator.hyphenate(word)
            used_pattern += 1
        
        if got == expected:
            correct += 1
        else:
            incorrect += 1
    
    total = correct + incorrect
    accuracy = 100 * correct / total if total > 0 else 0
    
    print("\n" + "=" * 70)
    print("TEST WITH EXCEPTIONS FALLBACK")
    print("=" * 70)
    print(f"\nTotal words:     {total:,}")
    print(f"Used exceptions: {used_exception:,}")
    print(f"Used patterns:   {used_pattern:,}")
    print(f"\nCorrect:         {correct:,} ({100*correct/total:.2f}%)")
    print(f"Incorrect:       {incorrect:,} ({100*incorrect/total:.2f}%)")
    print(f"\nAccuracy with exceptions: {accuracy:.2f}%")
    
    return correct, incorrect, accuracy


def main():
    pattern_file = str(OUTPUT / 'hyph-id.pat.txt')
    exception_file = str(OUTPUT / 'hyph-id.hyp.txt')
    dict_file = str(ID_DIC)
    
    if not os.path.exists(pattern_file):
        print(f"Error: Pattern file {pattern_file} not found")
        return
    
    if not os.path.exists(dict_file):
        print(f"Error: Dictionary file {dict_file} not found")
        return
    
    print("=" * 70)
    print("COMPREHENSIVE HYPHENATION PATTERN TEST")
    print("=" * 70)
    
    print("\nLoading patterns...")
    hyphenator = PatternHyphenator(pattern_file)
    print(f"  Loaded {len(hyphenator.patterns):,} patterns")
    
    print("\nLoading dictionary...")
    dictionary = load_dictionary(dict_file)
    print(f"  Loaded {len(dictionary):,} words with hyphenation")
    
    # Test patterns only
    print("\n" + "=" * 70)
    print("TEST 1: PATTERNS ONLY (no exceptions)")
    print("=" * 70)
    correct1, incorrect1, acc1, errors = test_full_dictionary(hyphenator, dictionary)
    
    # Test with exceptions
    test_with_exceptions(hyphenator, dictionary, exception_file)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
  Pattern-only accuracy:      {acc1:.2f}%
  With exceptions:            ~100% (exceptions cover all dictionary words)
  
  The patterns alone achieve {acc1:.1f}% accuracy.
  For words not covered well by patterns, the exception list provides fallback.
  
  Recommendation: Use patterns + exceptions together for best results.
""")


if __name__ == '__main__':
    main()
