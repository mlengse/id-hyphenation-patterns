#!/usr/bin/env python3
"""
Script to add missing lemmas from kbbi_pemenggalan.txt to id.dic.

kbbi_pemenggalan.txt format: lemma: hy.phen.a.ted
id.dic format: hy-phen-a-ted
"""

def normalize_hyphenation(hyphenation: str) -> str:
    """Convert hyphenation from . to - and lowercase."""
    return hyphenation.replace('.', '-').lower().strip()

def extract_lemma_from_pemenggalan(line: str) -> tuple[str, str] | None:
    """Extract lemma and hyphenation from pemenggalan line."""
    if ':' not in line:
        return None
    parts = line.split(':', 1)
    if len(parts) != 2:
        return None
    lemma = parts[0].strip()
    hyphenation = parts[1].strip()
    if not lemma or not hyphenation:
        return None
    return lemma, hyphenation

def main():
    pemenggalan_path = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi_pemenggalan.txt'
    id_dic_path = r'c:\Users\anjan\dev\bahasa_indonesia\kbbi\kbbi-extractor\data\id.dic'
    
    # Read existing id.dic entries
    print("Reading id.dic...")
    with open(id_dic_path, 'r', encoding='utf-8') as f:
        existing_entries = set()
        for line in f:
            line = line.strip()
            if line:
                existing_entries.add(line.lower())
    print(f"Found {len(existing_entries)} existing entries in id.dic")
    
    # Read pemenggalan entries and find missing ones
    print("Reading kbbi_pemenggalan.txt...")
    missing_entries = []
    with open(pemenggalan_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            result = extract_lemma_from_pemenggalan(line)
            if result is None:
                continue
            lemma, hyphenation = result
            # Convert hyphenation from . to -
            normalized = normalize_hyphenation(hyphenation)
            if normalized and normalized not in existing_entries:
                missing_entries.append(normalized)
                existing_entries.add(normalized)  # Avoid duplicates
    
    print(f"Found {len(missing_entries)} missing entries to add")
    
    # Append missing entries to id.dic
    if missing_entries:
        print("Adding missing entries to id.dic...")
        with open(id_dic_path, 'a', encoding='utf-8') as f:
            for entry in missing_entries:
                f.write(f'\n{entry}')
        print(f"Done! Added {len(missing_entries)} entries")
    else:
        print("No missing entries found")

if __name__ == '__main__':
    main()
