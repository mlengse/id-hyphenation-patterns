#!/usr/bin/env python3
"""
benchmark_runner.py

Comprehensive CPU Benchmark Suite for Indonesian Hyphenation Pattern Generation & Evaluation.
Compares 4 targets against KBBI dataset (73,800+ entries):
1. tex-hyphen baseline (hyph-id.pat.txt)
2. patgen-train-colab baseline (hyph-id-eydv.tex)
3. orthos py (patgen-train-colab/orthos_colab.py CPU mode)
4. orthos js (orthos/orthos.js Node.js engine)
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import json
import time
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

BASE_DIR = Path(__file__).resolve().parent
PATGEN_TRAIN_DIR = BASE_DIR.parent / "patgen-train-colab"
ORTHOS_JS_DIR = BASE_DIR.parent / "orthos"
KBBI_DATA_PATH = BASE_DIR / "output" / "ground_truth.txt"
if not KBBI_DATA_PATH.exists():
    KBBI_DATA_PATH = BASE_DIR.parent.parent / "data" / "kbbi-harvester-cdn" / "hyphenation" / "kbbi_vi_hyphenation_dict.json"
OUTPUT_DIR = BASE_DIR / "reports"
REPORTS_DIR = BASE_DIR / "reports"

sys.path.insert(0, str(PATGEN_TRAIN_DIR))

try:
    from patgen_trainer import PatgenTrainer
    import orthos_colab as orthos_py
except ImportError as e:
    print(f"Error importing patgen_trainer or orthos_colab: {e}")

# EYD V Constants
MONOFTONG = {'eu'}
DIFTONG = {'ai', 'au', 'ei', 'oi'}
GABUNGAN_KONSONAN = {'ng', 'ny', 'kh', 'sy', 'gh', 'dz'}

def parse_tex_patterns(pattern_content: str) -> Dict[str, Dict[int, int]]:
    patterns = {}
    content = re.sub(r'%.*', '', pattern_content)
    content = content.replace('\\patterns', '').replace('{', ' ').replace('}', ' ')
    for token in content.split():
        token = token.strip()
        if not token:
            continue
        letters = []
        values = {}
        pos = 0
        i = 0
        while i < len(token):
            if token[i].isdigit():
                values[pos] = int(token[i])
            else:
                letters.append(token[i])
                pos += 1
            i += 1
        if letters:
            key = ''.join(letters)
            patterns[key] = values
    return patterns

def load_pattern_file(file_path: Path) -> Dict[str, Dict[int, int]]:
    if not file_path.exists():
        raise FileNotFoundError(f"Pattern file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return parse_tex_patterns(content)

class TrieNode:
    __slots__ = ('children', 'values')
    def __init__(self):
        self.children = {}
        self.values = None

class FastHyphenator:
    def __init__(self, patterns: Dict[str, Dict[int, int]]):
        self.root = TrieNode()
        for pat_str, vals in patterns.items():
            node = self.root
            for ch in pat_str:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.values = vals

    def hyphenate(self, word: str, left_min: int = 2, right_min: int = 2) -> str:
        padded = '.' + word + '.'
        wlen = len(padded)
        hval = [0] * (wlen + 1)
        root = self.root
        
        for i in range(wlen):
            node = root
            for j in range(i, wlen):
                ch = padded[j]
                if ch not in node.children:
                    break
                node = node.children[ch]
                if node.values:
                    start = i
                    for dot_pos, val in node.values.items():
                        pos = start + dot_pos
                        if val > hval[pos]:
                            hval[pos] = val

        result = []
        for i in range(1, len(word)):
            padded_pos = i + 1
            if i >= left_min and (len(word) - i) >= right_min:
                if hval[padded_pos] % 2 == 1:
                    result.append('-')
            result.append(word[i - 1])
        result.append(word[-1])
        return ''.join(result)

def prepare_kbbi_datasets() -> Tuple[List[Tuple[str, str, Set[int]]], Path, Path]:
    print(f"Loading KBBI ground truth dataset from {KBBI_DATA_PATH}...")
    with open(KBBI_DATA_PATH, 'r', encoding='utf-8') as f:
        raw_dict = json.load(f)

    dataset = []
    py_dic_lines = []
    js_dic_lines = []

    for word, hyp in raw_dict.items():
        if len(word) < 2 or any(ch in word for ch in r'/\'"?!,;:<>()[]{}0123456789'):
            continue
        if word.startswith('-') or word.endswith('-'):
            continue
        
        hyp_clean = hyp.replace('?', '').replace('.', '-')
        parts = hyp_clean.split('-')
        clean_word = ''.join(parts).lower()

        if len(clean_word) < 2 or len(parts) < 2:
            continue

        gt_positions = set()
        current_pos = 0
        for p in parts[:-1]:
            current_pos += len(p)
            gt_positions.add(current_pos)

        dataset.append((clean_word, hyp_clean.lower(), gt_positions))
        py_dic_lines.append(hyp_clean.lower())

        # For orthos.js: no spaces, ASCII/letters only (no apostrophes)
        if ' ' not in hyp_clean and chr(39) not in hyp_clean:
            js_dic_lines.append(hyp_clean.lower())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    py_dic_path = OUTPUT_DIR / "indonesia_training.dic"
    with open(py_dic_path, 'w', encoding='utf-8', newline='\n') as f:
        for line in sorted(set(py_dic_lines)):
            f.write(line + '\n')

    js_dic_path = OUTPUT_DIR / "indonesia_pure.dic"
    with open(js_dic_path, 'w', encoding='utf-8', newline='\n') as f:
        for line in sorted(set(js_dic_lines)):
            f.write(line + '\n')

    print(f"Loaded {len(dataset):,} entries. PY dic: {py_dic_path.name}, JS dic: {js_dic_path.name}")
    return dataset, py_dic_path, js_dic_path

def benchmark_orthos_py_training(dic_path: Path, levels: int = 1) -> Tuple[float, Path, Dict[str, float]]:
    print(f"\n[Orthos Py CPU] Running pattern generation ({levels} level)...")
    start_total = time.time()

    trainer = PatgenTrainer(str(dic_path), gpu=False)
    level_times = {}

    for lvl in range(1, levels + 1):
        t0 = time.time()
        trainer.train_level(
            pat_start=1, pat_finish=5,
            hyph_level=lvl,
            good_wt=1, bad_wt=1, thresh=10,
            left_hyphen_min=2, right_hyphen_min=2
        )
        elapsed = time.time() - t0
        level_times[f"level_{lvl}"] = elapsed
        print(f"  ✓ Level {lvl} completed in {elapsed:.2f}s")

    out_pattern_path = OUTPUT_DIR / "hyph-id-orthos-py.pat"
    trainer.export(str(out_pattern_path))
    total_time = time.time() - start_total
    print(f"Done orthos py in {total_time:.2f}s -> {out_pattern_path.name}")
    return total_time, out_pattern_path, level_times

def benchmark_orthos_js_training(dic_path: Path, levels: int = 1) -> Tuple[float, Path, Dict[str, float]]:
    print(f"\n[Orthos JS Engine] Running pattern generation ({levels} level)...")
    start_total = time.time()
    
    orthos_js_script = ORTHOS_JS_DIR / "orthos.js"
    empty_pat = OUTPUT_DIR / "empty.pat"
    empty_pat.write_text("", encoding="utf-8")

    out_pattern_path = OUTPUT_DIR / "hyph-id-orthos-js.pat"
    current_in = empty_pat
    level_times = {}

    for lvl in range(1, levels + 1):
        t0 = time.time()
        current_out = OUTPUT_DIR / f"pattern_js_{lvl}.pat"
        stdin_input = f"2 2\n{lvl} {lvl}\n1 5\n1 1 10\n"

        cmd = ["node", str(orthos_js_script), str(dic_path), str(current_in), str(current_out)]
        
        proc = subprocess.run(
            cmd,
            input=stdin_input,
            text=True,
            capture_output=True,
            cwd=str(ORTHOS_JS_DIR)
        )

        elapsed = time.time() - t0
        level_times[f"level_{lvl}"] = elapsed
        
        current_in = current_out
        print(f"  ✓ Level {lvl} completed in {elapsed:.2f}s")

    if current_in.exists():
        out_pattern_path.write_text(current_in.read_text(encoding="utf-8"), encoding="utf-8")

    total_time = time.time() - start_total
    print(f"Done orthos js in {total_time:.2f}s -> {out_pattern_path.name}")
    return total_time, out_pattern_path, level_times

def evaluate_hyphenator(
    name: str,
    hyphenator: FastHyphenator,
    dataset: List[Tuple[str, str, Set[int]]],
    pattern_file_path: Path
) -> Dict[str, Any]:
    print(f"Evaluating {name} on {len(dataset):,} KBBI words...")
    
    total_words = len(dataset)
    exact_matches = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0

    eyd_monophthong_errors = 0
    eyd_diphthong_errors = 0
    eyd_consonant_errors = 0

    t0 = time.time()

    for clean_word, gt_hyp, gt_pos in dataset:
        pred_hyp = hyphenator.hyphenate(clean_word)
        
        if pred_hyp == gt_hyp:
            exact_matches += 1

        parts = pred_hyp.split('-')
        pred_pos = set()
        curr = 0
        for p in parts[:-1]:
            curr += len(p)
            pred_pos.add(curr)

        tp = len(pred_pos & gt_pos)
        fp = len(pred_pos - gt_pos)
        fn = len(gt_pos - pred_pos)

        total_tp += tp
        total_fp += fp
        total_fn += fn

        for pos in pred_pos:
            if 0 < pos < len(clean_word):
                seg = clean_word[pos - 1 : pos + 1]
                if seg in MONOFTONG:
                    eyd_monophthong_errors += 1
                elif seg in DIFTONG:
                    eyd_diphthong_errors += 1
                elif seg in GABUNGAN_KONSONAN:
                    eyd_consonant_errors += 1

    inference_time = time.time() - t0
    words_per_sec = total_words / inference_time if inference_time > 0 else 0

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    word_acc = (exact_matches / total_words) * 100

    pat_size_kb = pattern_file_path.stat().st_size / 1024 if pattern_file_path.exists() else 0
    pat_count = len(parse_tex_patterns(pattern_file_path.read_text(encoding="utf-8", errors="ignore"))) if pattern_file_path.exists() else 0

    results = {
        "name": name,
        "pattern_file": str(pattern_file_path.name),
        "pattern_count": pat_count,
        "pattern_size_kb": round(pat_size_kb, 2),
        "exact_word_matches": exact_matches,
        "total_words": total_words,
        "word_accuracy_pct": round(word_acc, 2),
        "point_precision": round(precision, 4),
        "point_recall": round(recall, 4),
        "point_f1": round(f1, 4),
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn,
        "eyd_monophthong_errors": eyd_monophthong_errors,
        "eyd_diphthong_errors": eyd_diphthong_errors,
        "eyd_consonant_errors": eyd_consonant_errors,
        "total_eyd_errors": eyd_monophthong_errors + eyd_diphthong_errors + eyd_consonant_errors,
        "inference_time_sec": round(inference_time, 3),
        "words_per_sec": round(words_per_sec, 0)
    }

    print(f"  ✓ Word Accuracy: {word_acc:.2f}% ({exact_matches:,}/{total_words:,}) | Point F1: {f1:.4f} | Speed: {words_per_sec:,.0f} w/s")
    return results

def main():
    print("======================================================================")
    print("INDONESIAN HYPHENATION BENCHMARK RUNNER (CPU MODE)")
    print("======================================================================")

    dataset, py_dic_path, js_dic_path = prepare_kbbi_datasets()

    tex_hyphen_file = BASE_DIR / "tex-hyphen" / "hyph-utf8" / "tex" / "generic" / "hyph-utf8" / "patterns" / "txt" / "hyph-id.pat.txt"
    patgen_train_file = PATGEN_TRAIN_DIR / "hyph-id-eydv.tex"

    py_train_time, py_pat_file, py_level_times = benchmark_orthos_py_training(py_dic_path, levels=1)
    js_train_time, js_pat_file, js_level_times = benchmark_orthos_js_training(js_dic_path, levels=1)

    evaluations = []

    targets = [
        ("tex-hyphen (hyph-id)", tex_hyphen_file),
        ("patgen-train-colab (hyph-id-eydv)", patgen_train_file),
        ("orthos py (CPU Generated)", py_pat_file),
        ("orthos js (Node.js Generated)", js_pat_file),
    ]

    for name, pat_file in targets:
        patterns_dict = load_pattern_file(pat_file)
        hyphenator = FastHyphenator(patterns_dict)
        res = evaluate_hyphenator(name, hyphenator, dataset, pat_file)
        
        if "orthos py" in name:
            res["training_time_sec"] = round(py_train_time, 2)
            res["level_times"] = {k: round(v, 2) for k, v in py_level_times.items()}
        elif "orthos js" in name:
            res["training_time_sec"] = round(js_train_time, 2)
            res["level_times"] = {k: round(v, 2) for k, v in js_level_times.items()}
        else:
            res["training_time_sec"] = "N/A (Pre-compiled)"
            res["level_times"] = {}

        evaluations.append(res)

    json_path = REPORTS_DIR / "benchmark_summary.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(evaluations, f, indent=2)

    md_path = REPORTS_DIR / "benchmark_report.md"
    generate_markdown_report(evaluations, md_path)

    print("\n======================================================================")
    print("Benchmark Completed Successfully!")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")
    print("======================================================================")

def generate_markdown_report(evaluations: List[Dict[str, Any]], output_md: Path):
    md = []
    md.append("# Hasil Benchmark Pemenggalan Kata Bahasa Indonesia (CPU Mode)")
    md.append(f"**Tanggal Run**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    md.append(f"**Dataset Ground Truth**: KBBI (`kbbi_vi_hyphenation_dict.json`) - 73.800+ kata")
    md.append("")
    md.append("## 1. Perbandingan Akurasi & Kualitas Pemenggalan")
    md.append("")
    md.append("| Subjek Benchmark | Word Accuracy (%) | Exact Words | Point F1 | Precision | Recall | Pelanggaran EYD V | Ukuran File | Pattern Count |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for e in evaluations:
        md.append(
            f"| **{e['name']}** | **{e['word_accuracy_pct']:.2f}%** | {e['exact_word_matches']:,}/{e['total_words']:,} | "
            f"{e['point_f1']:.4f} | {e['point_precision']:.4f} | {e['point_recall']:.4f} | "
            f"{e['total_eyd_errors']:,} | {e['pattern_size_kb']} KB | {e['pattern_count']:,} |"
        )

    md.append("")
    md.append("## 2. Performa Generasi Pattern (Pattern Training Speed on CPU)")
    md.append("")
    md.append("| Engine Generator | Total Training Time | Level 1 | Environment |")
    md.append("| :--- | :---: | :---: | :--- |")

    for e in evaluations:
        if "training_time_sec" in e and isinstance(e["training_time_sec"], (int, float)):
            lt = e.get("level_times", {})
            l1 = f"{lt.get('level_1', 0):.2f}s"
            env = "Python 3.14 + Numba CPU" if "py" in e["name"] else "Node.js (ES6)"
            md.append(f"| **{e['name']}** | **{e['training_time_sec']:.2f}s** | {l1} | {env} |")

    md.append("")
    md.append("## 3. Kecepatan Inferensi (Hyphenation Speed)")
    md.append("")
    md.append("| Subjek Benchmark | Total Inferensi (73.800+ kata) | Kecepatan (Kata / Detik) |")
    md.append("| :--- | :---: | :---: |")
    for e in evaluations:
        md.append(f"| **{e['name']}** | {e['inference_time_sec']:.3f}s | **{e['words_per_sec']:,.0f} kata/s** |")

    md.append("")
    md.append("## 4. Analisis Detail Pelanggaran Aturan EYD V")
    md.append("")
    md.append("| Subjek Benchmark | Pemisahan Monoftong (`eu`) | Pemisahan Diftong (`ai/au/ei/oi`) | Pemisahan Konsonan (`ng/ny/kh/sy`) | Total Error |")
    md.append("| :--- | :---: | :---: | :---: | :---: |")
    for e in evaluations:
        md.append(
            f"| **{e['name']}** | {e['eyd_monophthong_errors']:,} | {e['eyd_diphthong_errors']:,} | "
            f"{e['eyd_consonant_errors']:,} | **{e['total_eyd_errors']:,}** |"
        )

    output_md.write_text("\n".join(md), encoding="utf-8")

if __name__ == "__main__":
    main()
