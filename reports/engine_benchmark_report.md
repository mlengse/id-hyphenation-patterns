# Benchmark Results: Indonesian Hyphenation Engines & Pattern Repositories

**Execution Date**: 2026-08-02 19:31:09 UTC  
**Ground Truth Dataset**: KBBI Ground Truth (`ground_truth.txt`) — **72.259 words** (400 malformed entries filtered: leading/trailing hyphens, letter-split abbreviations)  
**Engines Evaluated**: `hypher`, `hyphen`, `Hyphenopoly`  
**Repositories**: `github:mlengse/hypher`, `github:mlengse/hyphen`, `github:mlengse/Hyphenopoly`, `github:mlengse/hyphenation-patterns`, `github:mlengse/id-hyphenation-patterns`  

## 1. Summary Matrix: Accuracy & Performance

| Benchmark Combination | Engine | Pattern Source | Exact Accuracy (%) | Point F1 | Precision | Recall | Speed (words/sec) | Time (s) | File Size |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **hypher + hyphenation-patterns** | `hypher` | hyphenation-patterns (github:mlengse/hyphenation-patterns) | **99.87%** | **0.9994** | 0.9992 | 0.9997 | **325.438** | 0.222s | 184.6 KB |
| **hypher + id-hyphenation-patterns** | `hypher` | id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns) | **99.87%** | **0.9994** | 0.9992 | 0.9997 | **367.465** | 0.1966s | 184.4 KB |
| **hypher + engine (shipped)** | `hypher` | hypher lib/patterns/id.js (shipped in engine/hypher) | **99.9%** | **0.9995** | 0.9993 | 0.9998 | **464.349** | 0.1556s | 191.6 KB |
| **hyphen + hyphenation-patterns** | `hyphen` | hyphenation-patterns (github:mlengse/hyphenation-patterns) | **95.58%** | **0.99** | 0.9991 | 0.9811 | **315.895** | 0.2287s | 1650.7 KB |
| **hyphen + id-hyphenation-patterns** | `hyphen` | id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns) | **95.59%** | **0.9901** | 0.9992 | 0.9812 | **165.664** | 0.4362s | 156.4 KB |
| **Hyphenopoly + hyphenation-patterns** | `Hyphenopoly` | hyphenation-patterns (github:mlengse/Hyphenopoly WASM) | **83.36%** | **0.9609** | 0.9992 | 0.9254 | **160.179** | 0.4511s | 127.5 KB |
| **Hyphenopoly + id-hyphenation-patterns** | `Hyphenopoly` | id-hyphenation-patterns (github:mlengse/Hyphenopoly min WASM) | **83.36%** | **0.9609** | 0.9992 | 0.9254 | **1.037.432** | 0.0697s | 2.7 KB |

## 2. EYD V Rule Violations Breakdown

Illegal internal splits on Indonesian diphthongs (`ai`, `au`, `ei`, `oi`), monophthongs (`eu`), and digraphs (`ng`, `ny`, `kh`, `sy`, `gh`, `dz`).  
**Genuine** = the split is NOT present in the ground truth (real EYD V violation).  
**GT-consistent** = the same split point IS present in the KBBI ground truth (KBBI itself breaks the pair on loan/foreign words, e.g. `a-ib`, `ab-la-ut`), so it is not a real defect.

| Benchmark Combination | Mono `eu` (gen) | Dif `ai/au/ei/oi` (gen) | Dig `ng/ny/kh/sy/...` (gen) | Total Genuine | GT-Consistent |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **hypher + hyphenation-patterns** | 1 | 5 | 0 | **6** | 2.018 |
| **hypher + id-hyphenation-patterns** | 1 | 5 | 0 | **6** | 2.018 |
| **hypher + engine (shipped)** | 1 | 4 | 0 | **5** | 2.020 |
| **hyphen + hyphenation-patterns** | 2 | 8 | 24 | **34** | 1.870 |
| **hyphen + id-hyphenation-patterns** | 1 | 5 | 0 | **6** | 1.869 |
| **Hyphenopoly + hyphenation-patterns** | 1 | 3 | 0 | **4** | 1.791 |
| **Hyphenopoly + id-hyphenation-patterns** | 1 | 3 | 0 | **4** | 1.791 |

## 3. Wrong-Word Analysis

Full per-word breakdowns are exported to `reports/`:  

| Benchmark Combination | Wrong Words | Same-Point Errors | Violation Words | Wrong Words File | Violations File |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **hypher + hyphenation-patterns** | 94 | 19 | 6 | `reports\wrong_words_hypher_hyphenation_patterns.json` | `reports\violations_hypher_hyphenation_patterns.json` |
| **hypher + id-hyphenation-patterns** | 94 | 19 | 6 | `reports\wrong_words_hypher_id_hyphenation_patterns.json` | `reports\violations_hypher_id_hyphenation_patterns.json` |
| **hypher + engine (shipped)** | 73 | 10 | 5 | `reports\wrong_words_hypher_engine_shipped.json` | `reports\violations_hypher_engine_shipped.json` |
| **hyphen + hyphenation-patterns** | 3.196 | 26 | 27 | `reports\wrong_words_hyphen_hyphenation_patterns.json` | `reports\violations_hyphen_hyphenation_patterns.json` |
| **hyphen + id-hyphenation-patterns** | 3.190 | 17 | 6 | `reports\wrong_words_hyphen_id_hyphenation_patterns.json` | `reports\violations_hyphen_id_hyphenation_patterns.json` |
| **Hyphenopoly + hyphenation-patterns** | 12.027 | 6 | 4 | `reports\wrong_words_hyphenopoly_hyphenation_patterns.json` | `reports\violations_hyphenopoly_hyphenation_patterns.json` |
| **Hyphenopoly + id-hyphenation-patterns** | 12.027 | 6 | 4 | `reports\wrong_words_hyphenopoly_id_hyphenation_patterns.json` | `reports\violations_hyphenopoly_id_hyphenation_patterns.json` |

## 4. Detailed Per-Engine Analysis

### 4.1 `hypher` (`github:mlengse/hypher`)
- **Performance**: High throughput (~250,000 - 280,000 words/second).
- **Pattern Compatibility**: Native support for JSON pattern objects with `leftmin` / `rightmin` boundaries.
- **Shipped patterns**: `lib/patterns/id.js` — the default patterns bundled with the `hypher` npm package.

### 4.2 `hyphen` (`github:mlengse/hyphen`)
- **Performance**: Extremely fast execution (~150,000 - 290,000 words/second).
- **Pattern Compatibility**: Uses precompiled Trie pattern weights (`weightsTable` + `patternTrie`).

### 4.3 `Hyphenopoly` (`github:mlengse/Hyphenopoly`)
- **Performance**: WebAssembly implementation with deterministic execution across browser & Node environments (~640,000 words/sec on WASM).
- **Pattern Compatibility**: Consumes binary `.wasm` compiled pattern files.

---
*Report automatically generated by `benchmark_engines_suite.js`.*
