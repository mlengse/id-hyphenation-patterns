import re
import os

class EYDHyphenatorV2:
    def __init__(self, dictionary_path=None):
        self.known_hyphenations = {}
        
        # --- KONFIGURASI INTI (Sesuai EYD V) ---
        self.vowels = "aeioué"
        
        # Mapping Digraf & Monoftong untuk Masking
        self.digraphs = {
            'kh': '\u0001',
            'ng': '\u0002',
            'ny': '\u0003',
            'sy': '\u0004',
            'eu': '\u0005'  # PENTING: EYD V C.1.b (eu tidak dipenggal)
        }
        self.inverse_digraphs = {v: k for k, v in self.digraphs.items()}

        # Daftar Imbuhan (Disederhanakan untuk prioritas stripping)
        self.prefixes = sorted([
            "memper", "diper", "ber", "ter", "per", "se", "ke", "di",
            "meng", "peng", "meny", "peny", "mem", "pem", "men", "pen",
            "me", "pe", "be", "te"
        ], key=len, reverse=True) 
        
        self.suffixes = sorted([
            "kah", "lah", "tah", "pun", "nya", "ku", "mu", "kan", "an", "i"
        ], key=len, reverse=True)

        # Load dictionary jika ada
        if dictionary_path and os.path.exists(dictionary_path):
            self.load_dictionary(dictionary_path)
        elif dictionary_path:
            print(f"[WARN] Kamus tidak ditemukan di path: {dictionary_path}")

    def load_dictionary(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped: continue
                    # Format id.dic: "a-bul-ha-yat"
                    # Key (clean): "abulhayat"
                    # Value: "a-bul-ha-yat"
                    clean = stripped.replace('-', '').lower()
                    self.known_hyphenations[clean] = stripped
            print(f"[INFO] Kamus dimuat: {len(self.known_hyphenations)} kata.")
        except Exception as e:
            print(f"[WARN] Gagal memuat kamus: {e}")

    # --- HELPER: RESTORE CASE ---
    def _restore_case(self, original_word, hyphenated_lower):
        """
        Mengembalikan huruf besar/kecil dari kata asli ke hasil pemenggalan.
        Contoh: original="Makan", hyphenated="ma-kan" -> result="Ma-kan"
        """
        result = []
        orig_idx = 0
        clean_original = original_word.replace('-', '') # Just in case input has hyphens
        
        for char in hyphenated_lower:
            if char == '-':
                result.append('-')
            else:
                if orig_idx < len(clean_original):
                    # Ambil karakter dari kata asli untuk mempertahankan casing
                    result.append(clean_original[orig_idx])
                    orig_idx += 1
                else:
                    result.append(char)
        return "".join(result)

    # --- MESIN UTAMA: REGEX MASKING ---
    def _mask_digraphs(self, word):
        masked = word.lower()
        for digraph, replacement in self.digraphs.items():
            masked = masked.replace(digraph, replacement)
        return masked

    def _unmask_text(self, text, original_text):
        result = []
        mask_idx = 0
        orig_idx = 0
        while mask_idx < len(text):
            char = text[mask_idx]
            if char == '-':
                result.append('-')
                mask_idx += 1
                continue
            
            token_len = 2 if char in self.inverse_digraphs else 1
            result.append(original_text[orig_idx:orig_idx+token_len])
            orig_idx += token_len
            mask_idx += 1
        return "".join(result)

    def syllabify_core(self, word):
        if not word or len(word) < 2: return word

        # 1. Masking
        masked = self._mask_digraphs(word)
        
        # 2. Definisi Pola Regex
        V_chars = self.vowels + self.digraphs['eu']
        V = f"[{V_chars}]"
        K = f"[^{V_chars}]" 

        # 3. Penerapan Aturan EYD V
        masked = re.sub(f"(?<={V}{K})(?={K}{K}{V})", '-', masked) # 1f: V-K-KK-V
        masked = re.sub(f"(?<={V}{K})(?={K}{V})", '-', masked)    # 1e: V-K-K-V
        masked = re.sub(f"(?<={V})(?={K}{V})", '-', masked)       # 1d: V-K-V
        masked = re.sub(f"(?<={V})(?={V})", '-', masked)          # 1a: V-V

        # 4. Unmasking
        return self._unmask_text(masked, word)

    # --- LOGIKA UTAMA (KAMUS + MORFOLOGI) ---
    def hyphenate(self, word):
        clean_word = word.lower().replace('-', '')

        # Cek 1: Kamus (Prioritas Tertinggi & Akurat 100%)
        if clean_word in self.known_hyphenations:
            hyphenated_lower = self.known_hyphenations[clean_word]
            return self._restore_case(word, hyphenated_lower)

        # Cek 2: Analisis Imbuhan (Morfologi)
        found_prefix = ""
        stem = clean_word
        
        for p in self.prefixes:
            if clean_word.startswith(p):
                temp_stem = clean_word[len(p):]
                if len(temp_stem) >= 3: 
                    found_prefix = p
                    stem = temp_stem
                    break
        
        found_suffix = ""
        final_stem = stem
        
        for s in self.suffixes:
            if stem.endswith(s):
                temp_stem = stem[:-len(s)]
                if len(temp_stem) >= 3:
                    found_suffix = s
                    final_stem = temp_stem
                    break

        # Rakit Ulang & Cek Stem di Kamus lagi
        parts = []
        
        # Prefix
        if found_prefix:
            if len(found_prefix) > 3:
                parts.append(self.syllabify_core(found_prefix))
            else:
                parts.append(found_prefix)
        
        # Stem
        # Coba cek stem di kamus dulu sebelum fallback ke regex
        if final_stem in self.known_hyphenations:
            parts.append(self.known_hyphenations[final_stem])
        else:
            parts.append(self.syllabify_core(final_stem))
        
        # Suffix
        if found_suffix:
            parts.append(found_suffix)

        hyphenated_lower = "-".join(parts)
        
        # Restore case untuk hasil morfologi juga
        return self._restore_case(word, hyphenated_lower)

# --- PENGUJIAN ---
if __name__ == "__main__":
    # Konfigurasi: Cek file id.dic di direktori yang sama
    dic_filename = "id.dic"
    dic_path = os.path.join(os.getcwd(), dic_filename)
    
    if os.path.exists(dic_path):
        hyphenator = EYDHyphenatorV2(dictionary_path=dic_path)
    else:
        print(f"[INFO] File '{dic_filename}' tidak ditemukan di folder ini.")
        print("       Menjalankan mode algoritma murni (tanpa kamus).")
        hyphenator = EYDHyphenatorV2(dictionary_path=None)
    
    # Kata-kata uji (Campuran kasus sulit, imbuhan, dan casing)
    test_cases = [
        "Makanan",          # Casing + Suffix
        "mempertanggungjawabkan", # Kompleks
        "Seudati",          # Monoftong 'eu' (Casing)
        "Cileuncang",       # 'eu' + cluster
        "Instrumen",        # 3 Konsonan
        "Bangkrut",         # Digraf 'ng' + 'kr'
        "Mengunci",         # Prefix + Nasal Fusion
        "Abulhayat",        # Dari id.dic
        "Gulai",            # Diftong (jika ada di id.dic akan benar gu-lai, jika tidak gu-la-i)
        "Mulai"             # Vokal (mu-la-i)
    ]

    print(f"\n{'KATA ASLI':<25} | {'HASIL PEMENGGALAN':<30}")
    print("-" * 60)
    for word in test_cases:
        result = hyphenator.hyphenate(word)
        print(f"{word:<25} | {result}")