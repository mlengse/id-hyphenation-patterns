import os
import re
from hyphenation_eyd_kbbi import EYDHyphenatorV2

def process_file(input_path, output_path, dic_path):
    print(f"Reading {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(input_path, 'r', encoding='latin-1') as f:
            content = f.read()
            
    # Remove BOM if present
    content = content.lstrip('\ufeff')
    
    # Sanitize: Replace control characters (except \t, \n, \r) with \n
    # This covers vertical tab (\x0b), form feed (\x0c), and separators (\x1c-\x1f)
    # \t is kept as it separates columns.
    clean_pattern = r'[\x00-\x08\x0b\x0c\x0e-\x1f]'
    content = re.sub(clean_pattern, '\n', content)
            
    # Normalize separators
    # Split by Form Feed (\f) first, as it seemingly separates stuck-together entries
    # Split by newlines
    # Split by tabs
    
    # Strategy: Replace all potential entry delimiters with \n, then process lines
    # Ideally, we want to extract the "Lemma".
    # Looking at the file, \t separates Lemma from other data.
    # So we should split by \f and \n first to get "Lines".
    # Then for each line, take the first \t-separated component.
    
    chunks = re.split(r'[\n\f\r]+', content)
    
    lemmas = set()
    
    print("Extracting lemmas...")
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        # Take first column
        parts = chunk.split('\t')
        lemma = parts[0].strip()
        
        if lemma:
            lemmas.add(lemma)
            
    sorted_lemmas = sorted(list(lemmas))
    print(f"Found {len(sorted_lemmas)} unique lemmas.")
    
    # Initialize Hyphenator
    print("Initializing Hyphenator...")
    hyphenator = EYDHyphenatorV2(dic_path)
    
    print("Hyphenating...")
    results = []
    
    for lemma in sorted_lemmas:
        # Handle phrases (e.g., "kereta api")
        # Hyphenate each word individually
        words = lemma.split(' ')
        hyphenated_words = []
        for w in words:
            # Check if it's a "clean" word or has symbols
            # If it contains dots (e.g. "a.n."), maybe don't hyphenate or pass through?
            # The hyphenator should handle it (it masks non-vowel/consonant chars as Consonants usually)
            # But let's verify: clean_word = replace('-', '')
            # If "a.n.", clean="a.n." -> v="a", "."'s are consonants. -> "a.n." (Rule 1a? No V-V).
            # It will likely return original.
            
            # Special check: If the word is already hyphenated with '.'?
            # We assume Col 1 is Lemma (Clean).
            hw = hyphenator.hyphenate(w)
            hyphenated_words.append(hw)
            
        full_hyphenation = " ".join(hyphenated_words)
        results.append(f"{lemma}\t{full_hyphenation}")
        
    print(f"Writing results to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(results))
    print("Done.")

if __name__ == "__main__":
    kbbi_path = r"c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_semua_kata.txt"
    output_path = r"c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan_otomatis.txt"
    dic_path = r"c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic"
    
    process_file(kbbi_path, output_path, dic_path)
