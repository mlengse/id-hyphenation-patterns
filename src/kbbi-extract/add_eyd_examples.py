import os

def main():
    path_txt = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    path_dic = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'
    
    additions = {
        "diambil": "di.am.bil",
        "perbuat": "per.bu.at",
        "pertanggungjawabkan": "per.tang.gung.ja.wab.kan",
        "letakkan": "le.tak.kan",
        "pergilah": "per.gi.lah",
        "diperjualbelikan": "di.per.ju.al.be.li.kan",
        "infra": "in.fra",
        "ultra": "ul.tra",
        "unsur-unsur": "un.sur-un.sur"
    }
    
    # 1. Read existing TXT
    lines = []
    existing_keys = set()
    with open(path_txt, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            lines.append(line)
            parts = line.split(':', 1)
            existing_keys.add(parts[0].strip())
            
    # 2. Add new if not extracting
    added_count = 0
    for k, v in additions.items():
        if k not in existing_keys:
            lines.append(f"{k}: {v}")
            added_count += 1
            print(f"Adding: {k}")
        else:
            print(f"Skipping {k}, already exists.")
            
    if added_count == 0:
        print("No new entries to add.")
        return

    # 3. Sort
    lines.sort(key=lambda x: x.split(':')[0].strip().lower())
    
    # 4. Save TXT
    with open(path_txt, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Updated {path_txt}")
    
    # 5. Regenerate DIC
    dic_lines = []
    for line in lines:
        parts = line.split(':', 1)
        val = parts[1].strip()
        dic_val = val.replace('.', '-')
        dic_lines.append(dic_val)
        
    dic_lines.sort()
    
    with open(path_dic, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(dic_lines) + '\n')
    print(f"Updated {path_dic}")

if __name__ == '__main__':
    main()
