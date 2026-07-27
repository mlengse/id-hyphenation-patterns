import json
import os
import re

def normalize_lemma(lemma):
    # Remove hyphens, dots, convert to lower case for loose comparison
    return lemma.replace('-', '').replace('.', '').replace(':', '').lower()

def load_json_lemmas(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"JSON loaded. Types: {type(data)}")
    if isinstance(data, list):
         # If it's a list of dicts or strings, handle accordingly.
         # Based on previous `command_status` output, it looked like a dict: {"ahas": "a.has", ...}
         # But verify if it turns out to be a list.
         pass
    return set(data.keys())

def load_pemenggalan_lemmas(path):
    lemmas = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            parts = line.split(':')
            if len(parts) >= 1:
                lemmas.add(parts[0].strip())
    return lemmas

def load_dic_lemmas(path):
    lemmas = set()
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            # id.dic format: A-ba-don. We want to reconstruct the lemma.
            # Since we can't distinguish hyphen from syllable separator easily without a reference,
            # we will provide a "stripped" version for comparison, 
            # BUT we can also keep the raw if we want to count lines.
            # Let's count lines first.
            # And for comparison, we'll align on the "stripped" version.
            lemmas.add(line)
    return lemmas

path_json = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_vi_hyphenation_dict.json'
path_txt = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
path_dic = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'

lemmas_json = load_json_lemmas(path_json)
lemmas_txt = load_pemenggalan_lemmas(path_txt)
lemmas_dic = load_dic_lemmas(path_dic)

print(f"Count {os.path.basename(path_json)}: {len(lemmas_json)}")
print(f"Count {os.path.basename(path_txt)}: {len(lemmas_txt)}")
print(f"Count {os.path.basename(path_dic)}: {len(lemmas_dic)}")

# Normalized comparison
norm_json = {normalize_lemma(x) for x in lemmas_json}
norm_txt = {normalize_lemma(x) for x in lemmas_txt}
norm_dic = {normalize_lemma(x) for x in lemmas_dic}

print(f"Normalized Count JSON: {len(norm_json)}")
print(f"Normalized Count TXT: {len(norm_txt)}")
print(f"Normalized Count DIC: {len(norm_dic)}")

# Intersections
common_all = norm_json.intersection(norm_txt).intersection(norm_dic)
print(f"Common to all (normalized): {len(common_all)}")

# In JSON but not in TXT
json_not_txt = norm_json - norm_txt
print(f"In JSON but not in TXT (normalized): {len(json_not_txt)}")

# In TXT but not in JSON
txt_not_json = norm_txt - norm_json
print(f"In TXT but not in JSON (normalized): {len(txt_not_json)}")

# In DIC but not in TXT
dic_not_txt = norm_dic - norm_txt
print(f"In DIC but not in TXT (normalized): {len(dic_not_txt)}")

# Sample differences
print("\nSample JSON not in TXT:")
for val in list(json_not_txt)[:10]:
    print(val)

print("\nSample TXT not in JSON:")
for val in list(txt_not_json)[:10]:
    print(val)

print("\nSample DIC not in TXT:")
for val in list(dic_not_txt)[:10]:
    print(val)
