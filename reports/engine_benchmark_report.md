# Benchmark Results: Indonesian Hyphenation Engines & Pattern Repositories

**Execution Date**: 2026-08-03 17:07:14 UTC  
**Ground Truth Dataset**: KBBI Ground Truth (`ground_truth.txt`) — **72,259 words** (400 malformed entries filtered: leading/trailing hyphens, letter-split abbreviations)  
**Engines Evaluated**: `hypher`, `hyphen`, `Hyphenopoly`  
**Repositories**: `github:mlengse/hypher`, `github:mlengse/hyphen`, `github:mlengse/Hyphenopoly`, `github:mlengse/hyphenation-patterns`, `github:mlengse/id-hyphenation-patterns`  

## 1. Summary Matrix: Accuracy & Performance

| Benchmark Combination | Engine | Pattern Source | Exact Accuracy (%) | Point F1 | Precision | Recall | Speed (words/sec) | Time (s) | File Size |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **hypher + hyphenation-patterns** | `hypher` | hyphenation-patterns/patterns/id.js (published npm package, synced from convert_engine_format.js) | **99.99%** | **1** | 1 | 1 | **342,317** | 0.2111s | 192.3 KB |
| **hypher + id-hyphenation-patterns** | `hypher` | id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns) | **99.99%** | **1** | 1 | 1 | **393,685** | 0.1835s | 185.6 KB |
| **hyphen + hyphenation-patterns** | `hyphen` | hyphenation-patterns (github:mlengse/hyphenation-patterns) | **99.99%** | **1** | 1 | 1 | **161,112** | 0.4485s | 393.3 KB |
| **hyphen + id-hyphenation-patterns** | `hyphen` | id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns) | **99.99%** | **1** | 1 | 1 | **167,416** | 0.4316s | 157.5 KB |
| **Hyphenopoly + hyphenation-patterns** | `Hyphenopoly` | hyphenation-patterns (github:mlengse/Hyphenopoly WASM) | **99.99%** | **1** | 1 | 1 | **135,598** | 0.5329s | 128.5 KB |
| **Hyphenopoly + id-hyphenation-patterns** | `Hyphenopoly` | id-hyphenation-patterns (github:mlengse/Hyphenopoly min WASM) | **99.99%** | **1** | 1 | 1 | **1,213,317** | 0.0596s | 128.5 KB |

## 2. EYD V Rule Violations Breakdown

Illegal internal splits on Indonesian diphthongs (`ai`, `au`, `ei`, `oi`), monophthongs (`eu`), and digraphs (`ng`, `ny`, `kh`, `sy`, `gh`, `dz`).  
**Genuine** = the split is NOT present in the ground truth (real EYD V violation).  
**GT-consistent** = the same split point IS present in the KBBI ground truth (KBBI itself breaks the pair on loan/foreign words, e.g. `a-ib`, `ab-la-ut`), so it is not a real defect.

| Benchmark Combination | Mono `eu` (gen) | Dif `ai/au/ei/oi` (gen) | Dig `ng/ny/kh/sy/...` (gen) | Total Genuine | GT-Consistent |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **hypher + hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |
| **hypher + id-hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |
| **hyphen + hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |
| **hyphen + id-hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |
| **Hyphenopoly + hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |
| **Hyphenopoly + id-hyphenation-patterns** | 0 | 0 | 0 | **0** | 2,022 |

## 3. Wrong-Word Analysis

Full per-word breakdowns are exported to `reports/`:  

| Benchmark Combination | Wrong Words | Same-Point Errors | Violation Words | Wrong Words File | Violations File |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **hypher + hyphenation-patterns** | 7 | 5 | 0 | `reports\wrong_words_hypher_hyphenation_patterns.json` | `reports\violations_hypher_hyphenation_patterns.json` |
| **hypher + id-hyphenation-patterns** | 7 | 5 | 0 | `reports\wrong_words_hypher_id_hyphenation_patterns.json` | `reports\violations_hypher_id_hyphenation_patterns.json` |
| **hyphen + hyphenation-patterns** | 7 | 5 | 0 | `reports\wrong_words_hyphen_hyphenation_patterns.json` | `reports\violations_hyphen_hyphenation_patterns.json` |
| **hyphen + id-hyphenation-patterns** | 7 | 5 | 0 | `reports\wrong_words_hyphen_id_hyphenation_patterns.json` | `reports\violations_hyphen_id_hyphenation_patterns.json` |
| **Hyphenopoly + hyphenation-patterns** | 9 | 5 | 0 | `reports\wrong_words_hyphenopoly_hyphenation_patterns.json` | `reports\violations_hyphenopoly_hyphenation_patterns.json` |
| **Hyphenopoly + id-hyphenation-patterns** | 9 | 5 | 0 | `reports\wrong_words_hyphenopoly_id_hyphenation_patterns.json` | `reports\violations_hyphenopoly_id_hyphenation_patterns.json` |

## 4. Detailed Per-Engine Analysis

### 4.1 `hypher` (`github:mlengse/hypher`)
- **Performance**: High throughput (~250,000 - 280,000 words/second).
- **Pattern Compatibility**: Native support for JSON pattern objects with `leftmin` / `rightmin` boundaries.
- **Shipped patterns**: `hyphenation-patterns/patterns/id.js` — the Indonesian pattern published via the `hyphenation-patterns` npm package (synced from `convert_engine_format.js`); `hypher` itself ships no patterns.

### 4.2 `hyphen` (`github:mlengse/hyphen`)
- **Performance**: Extremely fast execution (~150,000 - 290,000 words/second).
- **Pattern Compatibility**: Uses precompiled Trie pattern weights (`weightsTable` + `patternTrie`).

### 4.3 `Hyphenopoly` (`github:mlengse/Hyphenopoly`)
- **Performance**: WebAssembly implementation with deterministic execution across browser & Node environments (~640,000 words/sec on WASM).
- **Pattern Compatibility**: Consumes binary `.wasm` compiled pattern files.

---
*Report automatically generated by `benchmark_engines_suite.js`.*
