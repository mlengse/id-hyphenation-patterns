#!/usr/bin/env python3
"""
Script untuk mengekstrak pola pemenggalan dari:
- kbbi_kata_tanpa_pemenggalan.csv
- kbbi_frasa_tanpa_pemenggalan.csv

dan menambahkannya ke kbbi_pemenggalan.txt jika belum ada.

Kriteria: hanya entri yang kolom keduanya mengandung `.` yang dianggap memiliki pemenggalan.
"""

import os

def main():
    base_dir = r"c:\Users\anjan\dev\bahasa_indonesia\kbbi"
    csv_files = [
        os.path.join(base_dir, "kbbi_kata_tanpa_pemenggalan.csv"),
        os.path.join(base_dir, "kbbi_frasa_tanpa_pemenggalan.csv"),
        os.path.join(base_dir, "kbbi_pemenggalan_otomatis.csv"),
    ]
    txt_path = os.path.join(base_dir, "kbbi_pemenggalan.txt")
    
    # Baca pemenggalan yang sudah ada
    existing = set()
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                kata = line.split(':')[0].strip()
                existing.add(kata.lower())  # Normalize ke lowercase
    
    print(f"Jumlah pemenggalan yang sudah ada: {len(existing)}")
    
    # Proses semua CSV files
    new_entries = []
    total_with_hyphen = 0
    total_already_exists = 0
    
    for csv_path in csv_files:
        filename = os.path.basename(csv_path)
        if not os.path.exists(csv_path):
            print(f"\nSkipping (not found): {filename}")
            continue
            
        print(f"\nMemproses: {filename}")
        is_auto_file = "kbbi_pemenggalan_otomatis" in filename
        
        count_with_hyphen = 0
        count_already_exists = 0
        count_new = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Split by tab
                parts = line.split('\t')
                if len(parts) >= 2:
                    kata = parts[0].strip()
                    pemenggalan = parts[1].strip()
                    
                    # Normalisasi pemenggalan dari file otomatis (hyphen -> dot)
                    if is_auto_file and '-' in pemenggalan and '.' not in pemenggalan:
                        # Convert hyphens to dots for consistency with existing db
                        # Note: This might convert hyphenated-words (kata-kata) to kata.kata
                        # But since we don't have better info, it's acceptable for now to standardize
                        # Or we could try to preserve if we knew the structure.
                        # For now, simplistic conversion:
                        pemenggalan = pemenggalan.replace('-', '.')
                    
                    # Kriteria pemenggalan valid (berdasarkan EYD V):
                    # 1. Kolom kedua HARUS mengandung titik (.) sebagai pemisah suku kata
                    # 2. KECUALI untuk imbuhan (diawali/diakhiri tanda hubung)
                    # 3. Jika kolom kedua sama persis dengan kolom pertama (case-insensitive), tidak valid
                    
                    is_affix = kata.startswith('-') or kata.endswith('-')
                    has_syllable_dot = '.' in pemenggalan
                    is_same_as_word = kata.lower() == pemenggalan.lower().replace('.', '')
                    
                    # Valid jika: (ada titik suku kata DAN tidak sama dengan kata asli) ATAU imbuhan
                    if (has_syllable_dot and not is_same_as_word) or (is_affix and has_syllable_dot):
                        count_with_hyphen += 1
                        
                        # Cek apakah kata sudah ada di existing
                        if kata.lower() not in existing:
                            new_entries.append(f"{kata}: {pemenggalan}")
                            existing.add(kata.lower())
                            count_new += 1
                        else:
                            count_already_exists += 1
        
        print(f"  - Entri dengan pemenggalan (ada titik): {count_with_hyphen}")
        print(f"  - Sudah ada di txt: {count_already_exists}")
        print(f"  - Entri baru: {count_new}")
        
        total_with_hyphen += count_with_hyphen
        total_already_exists += count_already_exists
    
    print(f"\n=== TOTAL ===")
    print(f"Entri dengan pemenggalan: {total_with_hyphen}")
    print(f"Sudah ada di txt: {total_already_exists}")
    print(f"Entri baru yang akan ditambahkan: {len(new_entries)}")
    
    # Tampilkan beberapa sample
    if new_entries:
        print("\nSample entri baru (10 pertama):")
        for entry in new_entries[:10]:
            print(f"  {entry}")
    
    # Tambahkan ke file
    if new_entries:
        with open(txt_path, 'a', encoding='utf-8') as f:
            f.write('\n')  # Pastikan ada newline
            for entry in new_entries:
                f.write(entry + '\n')
        print(f"\nBerhasil menambahkan {len(new_entries)} entri baru ke {txt_path}")
    else:
        print("\nTidak ada entri baru untuk ditambahkan.")

if __name__ == "__main__":
    main()
