#!/usr/bin/env python3
"""
Script untuk membersihkan kbbi_pemenggalan.txt:
1. Menghapus baris dengan format rusak (setelah baris 112543)
2. Menghapus entri tanpa pemenggalan yang valid (tidak ada '.' di kolom kedua)
3. Memperbaiki format entri agar konsisten

Kriteria pemenggalan yang valid (berdasarkan EYD V):
- Kolom kedua (setelah ':') harus mengandung titik '.' sebagai pemisah suku kata
- KECUALI untuk imbuhan yang diawali/diakhiri tanda hubung (mis: -an, ber-, -kan)
- KECUALI untuk singkatan (huruf kapital dengan titik seperti A.K.B.P.)
"""

import os
import re

def is_valid_hyphenation(word: str, hyphenation: str) -> bool:
    """
    Cek apakah pemenggalan valid berdasarkan kaidah EYD.
    
    Returns:
        True jika valid, False jika tidak
    """
    word = word.strip()
    hyphenation = hyphenation.strip()
    
    # Jika kosong, tidak valid
    if not word or not hyphenation:
        return False
    
    # Jika kolom kedua sama persis dengan kolom pertama (tanpa perubahan apapun)
    # dan tidak ada titik, maka tidak valid
    if word.lower() == hyphenation.lower() and '.' not in hyphenation:
        return False
    
    # Imbuhan: diawali atau diakhiri dengan tanda hubung
    # Contoh: -an, -kan, ber-, me-, -nya, dll.
    # Ini valid meskipun tidak ada titik
    if word.startswith('-') or word.endswith('-'):
        return True
    
    # Singkatan: semua huruf kapital atau mengandung titik singkatan
    # Contoh: A.K.B.P., S.E., dll.
    # Perlu dibedakan dari pemenggalan biasa
    if hyphenation.isupper() or re.match(r'^[A-Z]+$', hyphenation):
        # Ini singkatan tanpa titik, valid
        return True
    
    # Cek apakah ada titik pemisah suku kata yang valid
    # Titik harus ada di tengah kata (bukan hanya di akhir untuk singkatan)
    if '.' in hyphenation:
        # Pastikan titik bukan hanya untuk singkatan (seperti S.E. atau a.n.)
        # Singkatan biasanya punya titik setelah setiap huruf
        # Pemenggalan punya titik di antara suku kata (mis: a.ba.di)
        
        # Jika ada titik tapi tidak semua karakter adalah huruf/titik, 
        # mungkin format campuran - tetap dianggap valid
        return True
    
    # Jika ada tanda hubung di tengah (untuk kata ulang), bisa valid
    # Contoh: a.ba-a.ba, rumah-rumah
    if '-' in hyphenation and '-' in word:
        return True
    
    # Tidak ada titik dan bukan kasus khusus di atas = tidak valid
    return False


def is_valid_line_format(line: str) -> bool:
    """
    Cek apakah baris memiliki format yang valid.
    Format valid: "kata: pemenggalan" dengan tepat satu ':'
    
    Returns:
        True jika format valid, False jika tidak
    """
    line = line.strip()
    
    # Baris kosong tidak valid
    if not line:
        return False
    
    # Harus ada tepat satu ':'
    if line.count(':') != 1:
        return False
    
    # Tidak boleh ada karakter kontrol aneh
    # Karakter yang dibolehkan: alfanumerik, spasi, titik, tanda hubung, 
    # apostrof, karakter unicode untuk bahasa Arab/diakritik
    # Karakter kontrol (ASCII 0-31 kecuali newline) tidak dibolehkan
    for char in line:
        if ord(char) < 32 and char not in '\n\r\t':
            return False
        # Form feed, vertical tab, file separator, dll.
        if char in '\x0b\x0c\x1c\x1d\x1e\x1f':
            return False
    
    parts = line.split(':')
    if len(parts) != 2:
        return False
    
    kata = parts[0].strip()
    pemenggalan = parts[1].strip()
    
    # Kedua bagian harus ada isinya
    if not kata or not pemenggalan:
        return False
    
    return True


def main():
    base_dir = r"c:\Users\anjan\dev\bahasa_indonesia\kbbi"
    input_path = os.path.join(base_dir, "kbbi_pemenggalan.txt")
    output_path = os.path.join(base_dir, "kbbi_pemenggalan_cleaned.txt")
    
    print("=" * 60)
    print("PEMBERSIHAN FILE PEMENGGALAN")
    print("=" * 60)
    
    # Statistik
    stats = {
        'total_lines': 0,
        'empty_lines': 0,
        'invalid_format': 0,
        'no_hyphenation': 0,
        'valid_entries': 0,
        'control_chars': 0,
    }
    
    # Contoh entri yang dihapus
    removed_examples = {
        'invalid_format': [],
        'no_hyphenation': [],
        'control_chars': [],
    }
    
    valid_entries = []
    seen_words = set()  # Untuk menghindari duplikat
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total_lines'] += 1
            line = line.rstrip('\r\n')
            
            # Skip baris kosong
            if not line.strip():
                stats['empty_lines'] += 1
                continue
            
            # Cek karakter kontrol
            has_control = False
            for char in line:
                if ord(char) < 32 and char not in '\n\r\t':
                    has_control = True
                    break
                if char in '\x0b\x0c\x1c\x1d\x1e\x1f':
                    has_control = True
                    break
            
            if has_control:
                stats['control_chars'] += 1
                if len(removed_examples['control_chars']) < 5:
                    removed_examples['control_chars'].append(
                        f"Line {line_num}: {repr(line[:80])}"
                    )
                continue
            
            # Cek format valid
            if not is_valid_line_format(line):
                stats['invalid_format'] += 1
                if len(removed_examples['invalid_format']) < 5:
                    removed_examples['invalid_format'].append(
                        f"Line {line_num}: {line[:80]}"
                    )
                continue
            
            # Parse kata dan pemenggalan
            parts = line.split(':')
            kata = parts[0].strip()
            pemenggalan = parts[1].strip()
            
            # Cek apakah pemenggalan valid
            if not is_valid_hyphenation(kata, pemenggalan):
                stats['no_hyphenation'] += 1
                if len(removed_examples['no_hyphenation']) < 10:
                    removed_examples['no_hyphenation'].append(
                        f"Line {line_num}: {kata}: {pemenggalan}"
                    )
                continue
            
            # Cek duplikat (case-insensitive)
            kata_lower = kata.lower()
            if kata_lower in seen_words:
                continue  # Skip duplikat
            seen_words.add(kata_lower)
            
            # Entri valid
            valid_entries.append(f"{kata}: {pemenggalan}")
            stats['valid_entries'] += 1
    
    # Tulis hasil
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in valid_entries:
            f.write(entry + '\n')
    
    # Laporan
    print(f"\nFile input: {input_path}")
    print(f"File output: {output_path}")
    print()
    print("STATISTIK:")
    print(f"  Total baris          : {stats['total_lines']:,}")
    print(f"  Baris kosong         : {stats['empty_lines']:,}")
    print(f"  Karakter kontrol     : {stats['control_chars']:,}")
    print(f"  Format tidak valid   : {stats['invalid_format']:,}")
    print(f"  Tanpa pemenggalan    : {stats['no_hyphenation']:,}")
    print(f"  Entri valid          : {stats['valid_entries']:,}")
    
    print("\n" + "=" * 60)
    print("CONTOH ENTRI YANG DIHAPUS:")
    print("=" * 60)
    
    if removed_examples['control_chars']:
        print("\n[Karakter Kontrol]")
        for ex in removed_examples['control_chars']:
            print(f"  {ex}")
    
    if removed_examples['invalid_format']:
        print("\n[Format Tidak Valid]")
        for ex in removed_examples['invalid_format']:
            print(f"  {ex}")
    
    if removed_examples['no_hyphenation']:
        print("\n[Tanpa Pemenggalan Valid]")
        for ex in removed_examples['no_hyphenation']:
            print(f"  {ex}")
    
    print("\n" + "=" * 60)
    print("SELESAI!")
    print("=" * 60)
    print(f"\nFile bersih tersimpan di: {output_path}")
    print("Silakan periksa hasilnya, lalu rename jika sudah benar.")


if __name__ == "__main__":
    main()
