# id-hyphenation-patterns

**Lapisan: Pattern (🧩).** Generator + validator pola pemenggalan bahasa Indonesia berbasis EYD V, plus pola hasil generate. Diekstrak dari `bahasa_indonesia/pemenggalan` (kode glue milik sendiri, tanpa fork/data).

> Status: **scaffold lokal (preview)** — belum ada remote GitHub. Bagian dari restrukturisasi `dev/bahasa` (lihat `../../implementation_plan.md`, Fase 5).

## Struktur
```
src/      generator & validator (*.py, *.js) — run_patgen, run_orthos_iterative, generate_*, validate_*, test_*
rules/    SK_EYD_Edisi_V_16082022.md (aturan EYD), id.tra, empty.pat
output/   pola hasil generate (hyph-id.*, hyphenopoly-id.json, hypher-id.js, dll.)
```

## Dependensi antar-repo (workspace `dev/bahasa`)
- ✅ **`pattern/orthos`** (generator pola) — `run_orthos_iterative.js` sudah diarahkan ke `../../orthos/orthos.js` (override: env `ORTHOS_PATH`).
- ⬜ **Data** (`id.dic`, `id_orthos.dic`, `kbbi_pemenggalan.txt`, `hyph-id-new.tex`, dll.) — **belum disertakan**; milik lapisan `data/` (→ `data/kbbi-data`). Generator perlu file ini sebagai input; arahkan ke lokasi data setelah `kbbi-data` dibuat (Fase 5).
- ⬜ **Fork engine untuk uji** — `src/test_all_libraries.js` masih memakai path lama (`hyphen/…`, `hypher/…`, `Hyphenopoly/…`, `tex-hyphen/…`). Lokasi baru: `../../engine/{hyphen,hypher,Hyphenopoly}` dan `../tex-hyphen`, `../hyphenation-patterns`. **TODO: perbarui path fixture.**

## Catatan
Sumber asli di `bahasa_indonesia/pemenggalan` **belum dihapus** (backup) sampai repo ini diverifikasi & di-push.

## Benchmark engine (keadilan perbandingan)

`npm run benchmark` (`src/benchmark_engines_suite.js`) membandingkan `hypher`, `hyphen`, dan `Hyphenopoly` terhadap ground truth KBBI. Persyaratan agar setara:

- **`minWordLength`**: engine `hyphen` default `5`, sehingga kata 2–4 huruf (3.109 entri ground truth) di-skip tanpa pemenggalan → akurasi turun ~4,3 pt. Runner **wajib** men-set `minWordLength: 2` (sama dengan `hyphenmins left:2 right:2` pola id). Lihat komentar di `src/benchmark_engines_suite.js:218`.
- **Pattern source**: pastikan semua engine memakai pattern yang sama. Konfigurasi `hyphen + hyphenation-patterns` membaca `engine/hyphen/patterns/id.js` (v2.0, tanpa exceptions overrides), sedangkan `hypher + hyphenation-patterns` membaca `pattern/hyphenation-patterns/patterns/id.js` (terbaru, dengan overrides) — beda file, bukan beda engine.
