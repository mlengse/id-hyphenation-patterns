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
