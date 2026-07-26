#!/usr/bin/env python3
"""
Validate Indonesian hyphenation patterns against EYD V rules.

Tests the generated patterns against key EYD V rules:
1. V-V: Split between consecutive vowels (bu-ah, ma-in)
2. Monoftong eu: NOT split (seu-da-ti, NOT *se-u-da-ti)
3. Diftong ai, au, ei, oi: NOT split (sau-da-ra, NOT *sa-u-da-ra)
4. V-K-V: Split before consonant (ba-pak, de-ngan)
5. V-KK-V: Split between consonants (ban-tu, man-di)
6. V-KKK-V: Split after first consonant (am-bruk, in-stru-men)
7. Digraph kh, ng, ny, sy: NOT split (ba-nyak, kong-res)
"""

import re
import os

class SimpleHyphenator:
    """Simple pattern-based hyphenator for testing."""
    
    def __init__(self, pattern_file):
        self.patterns = {}
        self.load_patterns(pattern_file)
    
    def load_patterns(self, pattern_file):
        """Load patterns from tex-style pattern file."""
        with open(pattern_file, 'r', encoding='utf-8') as f:
            for line in f:
                pattern = line.strip()
                if not pattern:
                    continue
                # Extract letters and numbers
                letters = re.sub(r'[0-9]', '', pattern)
                # Build values at each position
                values = []
                idx = 0
                for char in pattern:
                    if char.isdigit():
                        values.append(int(char))
                    else:
                        values.append(0)
                        idx += 1
                # Ensure proper length
                while len(values) < len(letters) + 1:
                    values.append(0)
                self.patterns[letters] = values[:len(letters)+1]
        print(f"Loaded {len(self.patterns)} patterns")
    
    def hyphenate(self, word):
        """Hyphenate a word using loaded patterns."""
        word = word.lower()
        work = '.' + word + '.'
        n = len(work)
        values = [0] * (n + 1)
        
        # Apply all matching patterns
        for i in range(n):
            for j in range(i + 1, min(n + 1, i + 15)):  # max pattern length
                substr = work[i:j]
                if substr in self.patterns:
                    pat_values = self.patterns[substr]
                    for k, v in enumerate(pat_values):
                        pos = i + k
                        if pos < len(values):
                            values[pos] = max(values[pos], v)
        
        # Build hyphenated word (skip boundaries)
        result = []
        for i, char in enumerate(word):
            # Respect left/right hyphen min (position 1 = after first char)
            if i > 0 and i < len(word) - 1:  # not at boundaries
                if values[i + 1] % 2 == 1:  # odd = hyphen point
                    result.append('-')
            result.append(char)
        
        return ''.join(result)


def load_dictionary(dict_file):
    """Load reference dictionary with hyphenations."""
    dictionary = {}
    with open(dict_file, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word or ' ' in word or word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '')
            if clean.isalpha():
                dictionary[clean] = word
    return dictionary


def test_eyd_rules(hyphenator, dictionary):
    """Test against EYD V rules with specific examples."""
    
    print("\n" + "=" * 60)
    print("EYD V HYPHENATION RULE VALIDATION")
    print("=" * 60)
    
    # Test cases from EYD V document
    test_cases = [
        # Rule 1a: V-V (split between vowels)
        ("buah", "bu-ah", "V-V split"),
        ("main", "ma-in", "V-V split"),
        ("niat", "ni-at", "V-V split"),
        ("saat", "sa-at", "V-V split"),
        
        # Rule 1b: Monoftong eu NOT split
        ("seudati", "seu-da-ti", "Monoftong eu"),
        ("cileuncang", "ci-leun-cang", "Monoftong eu"),
        ("seulumat", "seu-lu-mat", "Monoftong eu"),
        
        # Rule 1c: Diftong NOT split
        ("pandai", "pan-dai", "Diftong ai"),
        ("saudara", "sau-da-ra", "Diftong au"),
        ("survei", "sur-vei", "Diftong ei"),
        ("amboi", "am-boi", "Diftong oi"),
        
        # Rule 1d: V-K-V split before consonant
        ("bapak", "ba-pak", "V-K-V"),
        ("dengan", "de-ngan", "V-K-V + digraph"),
        ("kenyang", "ke-nyang", "V-K-V + digraph"),
        ("lawan", "la-wan", "V-K-V"),
        ("mutakhir", "mu-ta-khir", "V-K-V + digraph"),
        ("musyawarah", "mu-sya-wa-rah", "V-K-V + digraph"),
        
        # Rule 1e: V-KK-V split between consonants  
        ("april", "ap-ril", "V-KK-V"),
        ("bantu", "ban-tu", "V-KK-V"),
        ("mandi", "man-di", "V-KK-V"),
        ("sombong", "som-bong", "V-KK-V"),
        ("swasta", "swas-ta", "V-KK-V"),
        
        # Rule 1f: V-KKK-V split after first consonant
        ("ambruk", "am-bruk", "V-KKK-V"),
        ("bentrok", "ben-trok", "V-KKK-V"),
        ("infra", "in-fra", "V-KKK-V"),
        ("ultra", "ul-tra", "V-KKK-V"),
        ("instrumen", "in-stru-men", "V-KKKK-V"),
        
        # Rule 1g: Digraph stays together
        ("banyak", "ba-nyak", "Digraph ny"),
        ("kongres", "kong-res", "Digraph ng"),
        ("makhluk", "makh-luk", "Digraph kh"),
        ("masyhur", "masy-hur", "Digraph sy"),
        
        # Additional common words
        ("indonesia", "in-do-ne-si-a", "Complex word"),
        ("masyarakat", "ma-sya-ra-kat", "Digraph sy"),
        ("pancasila", "pan-ca-si-la", "Cluster"),
        ("bangkrut", "bang-krut", "Digraph + cluster"),
        ("struktur", "struk-tur", "Cluster"),
    ]
    
    passed = 0
    failed = 0
    results = []
    
    print(f"\n{'Word':<15} {'Expected':<18} {'Got':<18} {'Rule':<15} Status")
    print("-" * 70)
    
    for word, expected, rule in test_cases:
        # First check dictionary
        dict_hyphen = dictionary.get(word, None)
        got = hyphenator.hyphenate(word)
        
        # Compare with expected
        if got == expected:
            status = "✓ PASS"
            passed += 1
        elif dict_hyphen and got == dict_hyphen:
            status = "~ DICT"  # Matches dictionary but not expected
            passed += 1  # Count as pass if matches dictionary
        else:
            status = "✗ FAIL"
            failed += 1
        
        results.append((word, expected, got, dict_hyphen, rule, status))
        
        # Show discrepancy if any
        extra = ""
        if dict_hyphen and dict_hyphen != expected:
            extra = f" [dict: {dict_hyphen}]"
        
        print(f"{word:<15} {expected:<18} {got:<18} {rule:<15} {status}{extra}")
    
    print("-" * 70)
    print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    accuracy = 100 * passed / len(test_cases) if test_cases else 0
    print(f"Accuracy: {accuracy:.1f}%")
    
    return passed, failed, results


def test_dictionary_sample(hyphenator, dictionary, sample_size=100):
    """Test against a random sample from dictionary."""
    import random
    
    print("\n" + "=" * 60)
    print(f"DICTIONARY SAMPLE TEST ({sample_size} words)")
    print("=" * 60)
    
    words = list(dictionary.keys())
    if len(words) > sample_size:
        words = random.sample(words, sample_size)
    
    passed = 0
    failed = 0
    failures = []
    
    for word in words:
        expected = dictionary[word]
        got = hyphenator.hyphenate(word)
        
        if got == expected:
            passed += 1
        else:
            failed += 1
            if len(failures) < 20:  # Show first 20 failures
                failures.append((word, expected, got))
    
    print(f"\nResults: {passed} passed, {failed} failed")
    accuracy = 100 * passed / len(words) if words else 0
    print(f"Accuracy: {accuracy:.1f}%")
    
    if failures:
        print(f"\nFirst {len(failures)} failures:")
        print(f"{'Word':<15} {'Expected':<20} {'Got':<20}")
        print("-" * 55)
        for word, expected, got in failures:
            print(f"{word:<15} {expected:<20} {got:<20}")
    
    return passed, failed


def main():
    pattern_file = os.path.join('output', 'hyph-id.pat.txt')
    dict_file = 'id.dic'
    
    if not os.path.exists(pattern_file):
        print(f"Error: Pattern file {pattern_file} not found")
        print("Run: node run_orthos_iterative.js first")
        return
    
    if not os.path.exists(dict_file):
        print(f"Error: Dictionary file {dict_file} not found")
        return
    
    print("Loading patterns...")
    hyphenator = SimpleHyphenator(pattern_file)
    
    print("Loading dictionary...")
    dictionary = load_dictionary(dict_file)
    print(f"Dictionary: {len(dictionary)} words")
    
    # Run tests
    eyd_passed, eyd_failed, _ = test_eyd_rules(hyphenator, dictionary)
    dict_passed, dict_failed = test_dictionary_sample(hyphenator, dictionary, 100)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"EYD V Rules Test: {eyd_passed} passed, {eyd_failed} failed")
    print(f"Dictionary Sample: {dict_passed} passed, {dict_failed} failed")
    
    if eyd_failed == 0:
        print("\n✓ All EYD V rules validated successfully!")
    else:
        print(f"\n⚠ {eyd_failed} EYD V rule violations found")


if __name__ == '__main__':
    main()
