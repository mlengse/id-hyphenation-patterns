# Hasil Benchmark Pemenggalan Kata Bahasa Indonesia (CPU Mode)
**Tanggal Run**: 2026-08-03 01:10:33
**Dataset Ground Truth**: KBBI (`kbbi_vi_hyphenation_dict.json`) - 73.800+ kata

## 1. Perbandingan Akurasi & Kualitas Pemenggalan

| Subjek Benchmark | Word Accuracy (%) | Exact Words | Point F1 | Precision | Recall | Pelanggaran EYD V | Ukuran File | Pattern Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **tex-hyphen (hyph-id)** | **0.98%** | 719/73,633 | 0.0716 | 0.0727 | 0.0706 | 7,371 | 2.69 KB | 469 |
| **patgen-train-colab (hyph-id-eydv)** | **0.31%** | 228/73,633 | 0.1174 | 0.1091 | 0.1271 | 13,326 | 8.46 KB | 632 |
| **orthos py (CPU Generated)** | **0.09%** | 63/73,633 | 0.0818 | 0.0757 | 0.0890 | 11,219 | 1.18 KB | 197 |
| **orthos js (Node.js Generated)** | **0.05%** | 40/73,633 | 0.0810 | 0.0731 | 0.0908 | 13,747 | 0.71 KB | 129 |

## 2. Performa Generasi Pattern (Pattern Training Speed on CPU)

| Engine Generator | Total Training Time | Level 1 | Environment |
| :--- | :---: | :---: | :--- |
| **orthos py (CPU Generated)** | **3.65s** | 3.00s | Python 3.14 + Numba CPU |
| **orthos js (Node.js Generated)** | **0.56s** | 0.55s | Node.js (ES6) |

## 3. Kecepatan Inferensi (Hyphenation Speed)

| Subjek Benchmark | Total Inferensi (73.800+ kata) | Kecepatan (Kata / Detik) |
| :--- | :---: | :---: |
| **tex-hyphen (hyph-id)** | 0.372s | **197,821 kata/s** |
| **patgen-train-colab (hyph-id-eydv)** | 0.408s | **180,653 kata/s** |
| **orthos py (CPU Generated)** | 0.371s | **198,322 kata/s** |
| **orthos js (Node.js Generated)** | 0.397s | **185,574 kata/s** |

## 4. Analisis Detail Pelanggaran Aturan EYD V

| Subjek Benchmark | Pemisahan Monoftong (`eu`) | Pemisahan Diftong (`ai/au/ei/oi`) | Pemisahan Konsonan (`ng/ny/kh/sy`) | Total Error |
| :--- | :---: | :---: | :---: | :---: |
| **tex-hyphen (hyph-id)** | 209 | 1,409 | 5,753 | **7,371** |
| **patgen-train-colab (hyph-id-eydv)** | 204 | 1,369 | 11,753 | **13,326** |
| **orthos py (CPU Generated)** | 217 | 1,577 | 9,425 | **11,219** |
| **orthos js (Node.js Generated)** | 225 | 1,645 | 11,877 | **13,747** |