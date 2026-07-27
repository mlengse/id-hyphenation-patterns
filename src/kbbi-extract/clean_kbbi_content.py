import json
import os
import re

def normalize_key(key):
    return key.lower().replace('-', '').replace(' ', '')

def main():
    path_json = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_vi_hyphenation_dict.json'
    path_txt = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    path_dic = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'
    
    # 1. Load JSON (The Authority for existence)
    with open(path_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    print(f"Loaded {len(json_data)} entries from JSON.")
    
    # Create lookup map for JSON (normalized key -> value)
    # Actually, we might want to preserve the original lemma casing from JSON labels if needed,
    # but the JSON keys are usually lowercase? 
    # Let's check the JSON content structure in memory (from previous steps it seemed to be a dict).
    # We will trust JSON keys are valid lemmas.
    
    json_lemmas = set(json_data.keys())
    # A normalized set for matching
    json_lemmas_norm = {normalize_key(k) for k in json_lemmas}
    
    # 2. Process TXT
    new_txt_lines = []
    seen_lemmas_norm = set()
    
    deleted_count = 0
    
    with open(path_txt, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if ':' not in line:
                # If no colon, is it valid? Likely not in this file format.
                continue
            
            parts = line.split(':', 1)
            lemma = parts[0].strip()
            val = parts[1].strip()
            
            norm = normalize_key(lemma)
            
            # Filtering Logic
            # Rule: If phrase (has space) AND not hyphenated (no dots), delete.
            # UNLESS it is in JSON (JSON is king).
            
            is_in_json = norm in json_lemmas_norm
            
            has_space = ' ' in lemma
            has_dots = '.' in val
            # Note: monowords like 'cat' have no dots.
            
            if not is_in_json:
                if has_space and not has_dots:
                    # Candidate for deletion
                    deleted_count += 1
                    continue
            
            # Keep the line
            new_txt_lines.append(line)
            seen_lemmas_norm.add(norm)
            
    print(f"Txt processed. Deleted {deleted_count} lines (unhyphenated phrases not in JSON).")
    
    # 3. Add missing entries from JSON to TXT list
    added_count = 0
    for key, val in json_data.items():
        norm = normalize_key(key)
        if norm not in seen_lemmas_norm:
            # Add it
            # Format: 'lemma: value'
            # JSON format: key is lemma, value is hyphenated?
            # Let's verify JSON value format. Previous output suggest: "ahas": "a.has"
            # So yes.
            new_line = f"{key}: {val}"
            new_txt_lines.append(new_line)
            seen_lemmas_norm.add(norm)
            added_count += 1
            
    print(f"Added {added_count} entries from JSON to TXT.")
    
    # Sort TXT lines for consistency (Alphabetical by lemma)
    new_txt_lines.sort(key=lambda x: x.split(':')[0].strip().lower())
    
    # Write New TXT
    with open(path_txt, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(new_txt_lines) + '\n')
    print(f"Saved {path_txt} ({len(new_txt_lines)} lines).")
    
    # 4. Generate DIC
    # DIC format involves: Capitalized-Hyphenation (Wait, we determined it keeps the casing of the Value).
    # And replace dots with dashes used in id.dic.
    
    dic_lines = []
    
    for line in new_txt_lines:
        parts = line.split(':', 1)
        val = parts[1].strip()
        
        # Convert val to id.dic format
        # Replace '.' with '-'
        # Special case: some values might already have '-' (e.g. phrases).
        # Should we replace '.' with '-'?
        # Example: 'a.ba-a.ba' -> 'a-ba-a-ba'. correct.
        
        # What about 'Pak-Pak'? 'Ba.tak Pak-Pak' -> 'Ba-tak Pak-Pak'.
        dic_val = val.replace('.', '-')
        dic_lines.append(dic_val)
        
    # Sort DIC lines (ASCII sort to match id.dic behavior roughly)
    dic_lines.sort()
    
    # Write DIC
    with open(path_dic, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(dic_lines) + '\n')
        
    print(f"Saved {path_dic} ({len(dic_lines)} lines).")

if __name__ == '__main__':
    main()
