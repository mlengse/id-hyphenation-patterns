import re

def clean_eyd_line(line):
    # Remove markdown bold/italics
    # Common patterns: *word*, **word**
    # Also escaped hyphens \-
    
    # 1. Remove markdown stars
    cleaned = line.replace('*', '')
    
    # 2. Remove escaped hyphen logic if any, though usually it's just text
    # The file has things like: b*u*\-*ah*
    # Removing * gives: bu-\-ah
    # Removing \ gives: bu--ah (Wait, markdown \- escapes the hyphen? or is it just a hyphen?)
    # Let's assume standard md. \- matches literal -.
    
    cleaned = cleaned.replace('\\', '')
    
    # 3. Clean up spaces around hyphens? No, usually 'bu-ah'
    
    return cleaned.strip()

def extract_examples():
    eyd_path = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\SK_EYD_Edisi_V_16082022.md'
    
    # We focus on the "Pemenggalan Kata" section, roughly lines 963 to 1200
    # Or just scan whole file for hyphenated words in "Misalnya:" blocks? 
    # The user specifically pointed to examples in that file.
    
    examples = set()
    
    with open(eyd_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_line = 963
    end_line = 1200
    
    relevant_lines = lines[start_line:end_line]
    
    for line in relevant_lines:
        line = line.strip()
        if not line: continue
        
        # Skip instructional text (lines usually starting with number or letter, or long sentences)
        # Examples often are short lines or listed after "Misalnya:"
        # But looking at content:
        # 967: b*u*\-*ah*
        # 979: ci-l*eu*n-cang
        # 1056: *ber-*jalan
        # 1160: biografi bio-grafi
        
        # Heuristic: verify if line contains a hyphen that serves as separator
        # Note: some are "main" -> "ma-in" represented?
        # Actually in the text: "m*a*\-*i*n" -> "ma-in"
        
        # Let's clean formatting first
        cleaned = clean_eyd_line(line)
        
        # Now look for words with hyphens or spaces
        # "biografi bio-grafi" -> The latter is the hyphenation.
        # "bu-ah"
        
        # We want the LEMMA. 
        # For "bu-ah", lemma is "buah".
        # For "ber-jalan", lemma is "berjalan".
        # For "bio-grafi", lemma is "biografi".
        
        # Let's extract potential hyphenated tokens
        tokens = cleaned.split()
        for token in tokens:
            # Check if token looks like a hyphenated word
            # e.g. "bu-ah", "ma-in", "mem-bantu"
            # It might have trailing punctuation
            token = token.rstrip('.').rstrip(',')
            
            if '-' in token:
                # This could be the example 
                # e.g. "bu-ah" -> lemma "buah"
                # "kilo-gram" -> lemma "kilogram"
                
                # Special case: "biografi bio-grafi". "biografi" is unhyphenated, "bio-grafi" is hyphenated.
                # Both represent the lemma content.
                
                # Lemma derivation: remove hyphens
                lemma = token.replace('-', '')
                
                # Filter out obvious no-words or sentences?
                # "b-apak" -> "bapak"
                # "2b. me-ma-kai" ?
                # "di-per-jual-beli-kan" -> "diperjualbelikan"
                
                # Filter noise (like purely numbers or dates, e.g. 1-1-2000 if existed)
                if not lemma.isalpha():
                    continue
                    
                examples.add(lemma.lower())
                
    return examples

def check_against_dictionary():
    examples = extract_examples()
    print(f"Extracted {len(examples)} examples from EYD.")
    
    dict_path = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    
    # Load dictionary lemmas
    # format: lemma: hyp-hen-a-tion
    dict_lemmas = set()
    with open(dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                lemma = line.split(':')[0].strip().lower()
                dict_lemmas.add(lemma)
                
    # Check missing
    missing = []
    for ex in examples:
        if ex not in dict_lemmas:
            missing.append(ex)
            
    if missing:
        print(f"Found {len(missing)} examples missing from Dictionary:")
        for m in missing:
            print(f"- {m}")
    else:
        print("All examples are present in the dictionary.")

if __name__ == '__main__':
    check_against_dictionary()
