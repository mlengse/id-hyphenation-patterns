import json
import os

def main():
    path_json = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_vi_hyphenation_dict.json'
    path_txt = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    path_dic = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'
    
    print("Loading JSON...")
    with open(path_json, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    print("Loading TXT...")
    txt_lines = []
    with open(path_txt, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if ':' in line:
                txt_lines.append(line)
                
    # Create a map of TXT entries for quick lookup
    txt_map = {}
    for line in txt_lines:
        parts = line.split(':', 1)
        key = parts[0].strip()
        val = parts[1].strip()
        txt_map[key] = val
        
    # FIX: Enforce JSON values in TXT
    updates = 0
    for k, v in json_data.items():
        if k in txt_map:
            current_val = txt_map[k]
            # Normalize to compare (ignore casing differences if any, though JSON usually authoritative)
            if current_val != v:
                # Prioritize JSON value
                print(f"Updating {k}: {current_val} -> {v}")
                txt_map[k] = v
                updates += 1
        else:
            # Should have been added already, but added here just in case
            print(f"Adding missing {k}: {v}")
            txt_map[k] = v
            updates += 1
            
    if updates > 0:
        print(f"Total updates: {updates}")
        # Reconstruct list
        new_lines = [f"{k}: {v}" for k, v in txt_map.items()]
        new_lines.sort(key=lambda x: x.split(':')[0].strip().lower())
        
        with open(path_txt, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(new_lines) + '\n')
        print(f"Saved corrected {path_txt}")
        
        # Regenerate DIC
        dic_lines = []
        for line in new_lines:
            parts = line.split(':', 1)
            val = parts[1].strip()
            # Convert to id.dic format
            dic_val = val.replace('.', '-')
            dic_lines.append(dic_val)
            
        dic_lines.sort()
        with open(path_dic, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(dic_lines) + '\n')
            
        print(f"Saved regenerated {path_dic}")
    else:
        print("No updates needed. Files are in sync with JSON.")

if __name__ == '__main__':
    main()
