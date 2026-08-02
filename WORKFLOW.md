# Panduan Alur Kerja Menyeluruh (Unified Multi-Repo Workflow)

Dokumen ini menjelaskan alur kerja 5-tahap untuk pengembangan, pengujian, ekspor, dan sinkronisasi pola pemenggalan kata (*hyphenation patterns*) Bahasa Indonesia di kelima repositori:

1. **`id-hyphenation-patterns`** (Orchestrator & Single Source of Truth)
2. **`orthos`** (Engine Patgen Node.js)
3. **`patgen-train-colab`** (Laboratorium Pelatihan GPU/CPU)
4. **`tex-hyphen`** (Rilis Upstream TeX Live / CTAN)
5. **`hyphenation-patterns`** (Rilis Upstream NPM / JS Package)

---

## Peta Arsitektur Pipeline

```
[ Dataset KBBI ]
       │
       ▼ (Tahap 1: Ekstraksi Kamus)
[ output/indonesia_pure.dic ]
       │
       ▼ (Tahap 2: Training Engine - orthos / patgen)
[ output/hyph-id.pat.txt ]
       │
       ▼ (Tahap 3: Benchmark & Validasi KBBI + EYD V)
[ benchmark_runner.py ] ──► benchmark_report.md
       │
       ▼ (Tahap 4: Multi-Format Exporter - SSOT)
[ src/generate_all_formats.py ]
       ├── output/hyph-id.tex
       ├── output/hyph-id.pat.txt
       ├── output/hyph-id.hyp.txt
       ├── output/hyphenation-patterns-id.js
       └── output/hyphenopoly-id.json
       │
       ▼ (Tahap 5: Sinkronisasi Upstream)
[ src/sync_all_repos.py ]
       ├──► tex-hyphen (hyph-utf8 patterns/tex & patterns/txt)
       └──► hyphenation-patterns (patterns/id.js & dist/browser/id.js)
```

---

## Alur Eksekusi Pengembang (Step-by-Step)

### Tahap 1: Ekstraksi Data KBBI & Persiapan Kamus
Ekstrak kata-kata berimbuhan & berpola dari dataset KBBI:
```powershell
python src/prepare_orthos_dictionary.py
```
*Output*: `output/indonesia_pure.dic` dan `output/indonesia_training.dic`.

---

### Tahap 2: Pelatihan Pola (Training Pattern Engine)
Gunakan engine Patgen `orthos.js` untuk melatih pola level 1–5:
```powershell
node src/run_orthos_iterative.js
```
*Output*: `output/hyph-id.pat.txt` (Pola murni Liang) & `output/hyph-id.exceptions.txt`.

---

### Tahap 3: Pengujian Benchmark & Audit EYD V
Uji pola terhadap 73.800+ kata ground-truth KBBI:
```powershell
python benchmark_runner.py
```
*Output*: `benchmarks/reports/benchmark_report.md` (Mengukur Word Accuracy %, Precision, Recall, F1-Score, dan total pelanggaran EYD V).

---

### Tahap 4: Generasi Format Master (SSOT Exporter)
Setiap kali ada pembaruan pola master yang lolos benchmark, konversikan ke seluruh format target:
```powershell
python src/generate_all_formats.py
```
*Output di `output/`*:
- `hyph-id.tex` (Format TeX murni)
- `hyph-id.pat.txt` (Pola murni)
- `hyph-id.hyp.txt` (Daftar pengecualian murni)
- `hyphenation-patterns-id.js` (Format Hypher JS)
- `hyphenopoly-id.json` (Format Hyphenopoly JSON)

---

### Tahap 5: Sinkronisasi & Validasi Upstream Repositori
Distribusikan hasil ekspor master ke repositori TeX Live (`tex-hyphen`) dan NPM JS (`hyphenation-patterns`):
```powershell
python src/sync_all_repos.py
```
Skrip ini akan secara otomatis:
1. Menyalin `hyph-id.tex`, `hyph-id.pat.txt`, dan `hyph-id.hyp.txt` ke struktur folder `tex-hyphen/hyph-utf8/`.
2. Menyalin `hyphenation-patterns-id.js` ke `hyphenation-patterns/patterns/id.js` dan merakit ulang `dist/browser/id.js`.
3. Menjalankan pengujian integrasi JS (`node test/validate-id.js`).

---

## Standar & Catatan Penting
- **Pola Master**: Jangan mengedit file di `tex-hyphen` atau `hyphenation-patterns` secara manual. Selalu lakukan perubahan dari `id-hyphenation-patterns`.
- **Format Pengecualian Hypher**: Hypher memerlukan jangkar kata `.` diubah menjadi `_` dan pemisah pengecualian menggunakan karakter U+2027 (`‧`). Ini telah ditangani otomatis oleh `generate_all_formats.py`.
- **Rilis PR TeX Live**: Kirimkan Pull Request ke `tex-hyphen` pada folder `hyph-utf8/tex/generic/hyph-utf8/patterns/txt/`.
