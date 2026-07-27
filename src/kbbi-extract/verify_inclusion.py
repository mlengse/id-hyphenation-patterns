import json
import os

def normalize(text):
    # Flexible normalization: remove spaces, hyphens, dots, lower case
    return text.lower().replace('-', '').replace(' ', '').replace('.', '').replace(':', '')

def verify_inclusion():
    path_json = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_vi_hyphenation_dict.json'
    path_txt = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    path_dic = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'
    
    print("Loading JSON...")
    with open(path_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    json_keys = set(json_data.keys())
    # We also want to check if the *value* logic is respected, but the user asked if "entries" (meaning lemmas/words) are in there.
    # Let's check lemmas.
    
    print("Loading TXT...")
    txt_lemmas = set()
    with open(path_txt, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                lemma = line.split(':')[0].strip()
                txt_lemmas.add(lemma)
                
    print("Loading DIC...")
    dic_lemmas = set()
    with open(path_dic, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            # id.dic content is just the hyphenated word: "A-ba-don"
            # We need to reconstruct the "lemma" from this for comparison.
            # Removing hyphens gives us the lemma (mostly).
            # But wait, original lemma might have hyphens (e.g. kupu-kupu).
            # in id.dic: ku-pu-ku-pu. 
            # Removing hyphens: kupukupu.
            # So normalization is key for DIC check.
            dic_lemmas.add(line)

    # CHECK 1: JSON in TXT
    # TXT format "lemma: ..." preserves the lemma string exactly as key.
    # So we can do direct set comparison for most part, or normalized to be safe against casing diffs if any.
    # The previous step suggested exact keys were preserved.
    
    missing_in_txt = [k for k in json_keys if k not in txt_lemmas]
    
    if not missing_in_txt:
        print("SUCCESS: All JSON entries are in TXT.")
    else:
        print(f"FAILURE: {len(missing_in_txt)} JSON entries missing from TXT.")
        print("First 5 missing:", missing_in_txt[:5])

    # CHECK 2: JSON in DIC
    # We must compare normalized because DIC structure transforms the string (inserts hyphens).
    # So we normalize both JSON key and DIC entry to "lowercase letters only".
    
    json_norm = set(normalize(k) for k in json_keys)
    dic_norm = set(normalize(k) for k in dic_lemmas)
    
    missing_in_dic = [k for k in json_keys if normalize(k) not in dic_norm]
    
    if not missing_in_dic:
        print("SUCCESS: All JSON entries are in DIC (normalized check).")
    else:
        print(f"FAILURE: {len(missing_in_dic)} JSON entries missing from DIC.")
        print("First 5 missing:", missing_in_dic[:5])
        
    # Additional Strict Check if user meant "exact value representation"
    # But DIC format is fundamentally different (hyphens instead of dots).
    # Normalized check is the correct proxy for "is this word included".

if __name__ == '__main__':
    verify_inclusion()
