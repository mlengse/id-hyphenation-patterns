#!/usr/bin/env python3
"""
sync_all_repos.py

Synchronizes single source of truth (SSOT) hyphenation pattern outputs
from id-hyphenation-patterns/output to upstream repositories:
1. tex-hyphen (TeX Live / CTAN)
2. hyphenation-patterns (NPM / JS package)
"""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import shutil
import subprocess
from pathlib import Path

# Base directories
SRC_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = SRC_DIR.parent
OUTPUT_DIR = SRC_DIR / "output"

TEX_HYPHEN_DIR = BASE_DIR / "tex-hyphen"
HYPHENATION_PATTERNS_DIR = BASE_DIR / "hyphenation-patterns"

def sync_tex_hyphen():
    print("\n[1/3] Syncing with tex-hyphen (TeX Live / CTAN)...")
    if not TEX_HYPHEN_DIR.exists():
        print(f"  Warning: {TEX_HYPHEN_DIR} does not exist. Skipping.")
        return False

    tex_dest_dir = TEX_HYPHEN_DIR / "hyph-utf8" / "tex" / "generic" / "hyph-utf8" / "patterns" / "tex"
    txt_dest_dir = TEX_HYPHEN_DIR / "hyph-utf8" / "tex" / "generic" / "hyph-utf8" / "patterns" / "txt"

    tex_dest_dir.mkdir(parents=True, exist_ok=True)
    txt_dest_dir.mkdir(parents=True, exist_ok=True)

    files_map = {
        OUTPUT_DIR / "hyph-id.tex": tex_dest_dir / "hyph-id.tex",
        OUTPUT_DIR / "hyph-id.pat.txt": txt_dest_dir / "hyph-id.pat.txt",
        OUTPUT_DIR / "hyph-id.hyp.txt": txt_dest_dir / "hyph-id.hyp.txt",
    }

    synced_count = 0
    for src, dst in files_map.items():
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  [OK] Copied {src.name} -> {dst.relative_to(BASE_DIR)}")
            synced_count += 1
        else:
            print(f"  [FAIL] Error: Source file {src.name} missing!")

    return synced_count == len(files_map)

def sync_hyphenation_patterns():
    print("\n[2/3] Syncing with hyphenation-patterns (JS/NPM)...")
    if not HYPHENATION_PATTERNS_DIR.exists():
        print(f"  Warning: {HYPHENATION_PATTERNS_DIR} does not exist. Skipping.")
        return False

    src_js = OUTPUT_DIR / "hyphenation-patterns-id.js"
    dst_js = HYPHENATION_PATTERNS_DIR / "patterns" / "id.js"

    if not src_js.exists():
        print(f"  [FAIL] Error: Source file {src_js.name} missing!")
        return False

    shutil.copy2(src_js, dst_js)
    print(f"  [OK] Copied {src_js.name} -> {dst_js.relative_to(BASE_DIR)}")

    # Update dist/browser/id.js
    pre_js = HYPHENATION_PATTERNS_DIR / "lib" / "patterns.browser.pre.js"
    post_js = HYPHENATION_PATTERNS_DIR / "lib" / "patterns.browser.post.js"
    dist_js = HYPHENATION_PATTERNS_DIR / "dist" / "browser" / "id.js"

    if pre_js.exists() and post_js.exists():
        dist_js.parent.mkdir(parents=True, exist_ok=True)
        content = pre_js.read_text(encoding="utf-8") + dst_js.read_text(encoding="utf-8") + post_js.read_text(encoding="utf-8")
        dist_js.write_text(content, encoding="utf-8")
        print(f"  [OK] Built browser bundle -> {dist_js.relative_to(BASE_DIR)}")

    return True

def run_validations():
    print("\n[3/3] Running Validation Suite on Downstream Repositories...")
    
    # Run node test/validate-id.js in hyphenation-patterns
    test_script = HYPHENATION_PATTERNS_DIR / "test" / "validate-id.js"
    if test_script.exists():
        proc = subprocess.run(
            ["node", str(test_script)],
            cwd=str(HYPHENATION_PATTERNS_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if proc.returncode == 0:
            print("  [OK] hyphenation-patterns JS validation PASSED!")
            print(proc.stdout.strip())
        else:
            print("  [FAIL] hyphenation-patterns JS validation FAILED!")
            print(proc.stderr.strip())
            return False
    return True

def main():
    print("=" * 60)
    print("INDONESIAN HYPHENATION MULTI-REPO SYNC UTILITY")
    print("=" * 60)

    success_tex = sync_tex_hyphen()
    success_js = sync_hyphenation_patterns()
    success_val = run_validations()

    print("\n" + "=" * 60)
    if success_tex and success_js and success_val:
        print("ALL REPOSITORIES SUCCESSFULLY SYNCHRONIZED & VALIDATED!")
    else:
        print("SYNCHRONIZATION COMPLETED WITH WARNINGS/ERRORS.")
    print("=" * 60)

if __name__ == "__main__":
    main()
