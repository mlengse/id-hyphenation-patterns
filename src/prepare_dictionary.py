#!/usr/bin/env python3
"""
Prepare dictionary file for patgen from id.dic
Converts to lowercase and filters out entries not suitable for pattern generation.
"""

import re
import sys

def is_valid_word(word):
    """Check if word is suitable for patgen (basic a-z Latin alphabet)."""
    # Remove hyphens to check the base word
    clean = word.replace('-', '')
    # Only allow basic Latin letters (a-z)
    return bool(re.match(r'^[a-z]+$', clean, re.IGNORECASE))

def clean_word(word):
    """Convert word to lowercase and clean up."""
    return word.lower().strip()

def main():
    input_file = 'id.dic'
    output_file = 'id_words.dic'
    
    valid_count = 0
    invalid_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                word = line.strip()
                if not word:
                    continue
                
                # Skip entries with spaces (phrases)
                if ' ' in word:
                    invalid_count += 1
                    continue
                
                # Skip entries starting with abbreviation patterns
                if word.startswith('-') or word.endswith('-'):
                    invalid_count += 1
                    continue
                    
                # Clean the word
                word = clean_word(word)
                
                # Check if valid
                if is_valid_word(word):
                    f_out.write(word + '\n')
                    valid_count += 1
                else:
                    invalid_count += 1
    
    print(f"Processed id.dic:")
    print(f"  Valid words: {valid_count}")
    print(f"  Skipped: {invalid_count}")
    print(f"  Output: {output_file}")

if __name__ == '__main__':
    main()
