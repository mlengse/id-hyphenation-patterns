#!/usr/bin/env python3
"""
Generate Indonesian hyphenation patterns for multiple library formats.

This script reads orthos-generated patterns and converts them to all supported formats:
1. TeX format (.tex)
2. Plain patterns (.pat.txt)
3. Exceptions list (.hyp.txt)
4. hyphen library JS format
5. hypher library format
6. hyphenation-patterns format
"""

import re
import json
import os
from datetime import datetime

def load_orthos_patterns(filepath):
    """Load patterns from orthos output file."""
    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            pattern = line.strip()
            if pattern:
                patterns.append(pattern)
    return patterns

def load_exceptions(filepath):
    """Load hyphenated words as exceptions."""
    exceptions = []
    if not os.path.exists(filepath):
        return exceptions
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            # Skip entries with spaces (phrases), starting/ending with -
            if ' ' in word or word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '').lower()
            if re.match(r'^[a-zéü]+$', clean):
                exceptions.append(word.lower())
    return exceptions

def write_tex_file(patterns, exceptions, output_file):
    """Write patterns and exceptions in TeX format."""
    date = datetime.now().strftime("%Y/%m/%d")
    
    header = f"""% title: Hyphenation patterns for Bahasa Indonesia
% copyright: Copyright (C) 2025 Generated from KBBI data via orthos.js
% notice: This file contains hyphenation patterns for Indonesian.
%     Generated using orthos.js (patgen port) with 72,000+ words.
% language:
%     name: Bahasa Indonesia, Indonesian  
%     tag: id
% version: 3.0 <{date}>
% authors:
%   - Generated from KBBI dictionary via orthos.js
% licence:
%     - MIT License
% hyphenmins:
%     typesetting:
%         left: 2
%         right: 2
% texlive:
%     babelname: indonesian
%     message: Indonesian hyphenation patterns
%     package: hyph-utf8
% ==========================================

\\patterns{{%
"""
    
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header)
        
        # Write patterns
        line = ""
        for p in patterns:
            if len(line) + len(p) + 1 > 75:
                f.write(line.strip() + "\n")
                line = p + " "
            else:
                line += p + " "
        if line:
            f.write(line.strip() + "\n")
        
        f.write("}%\n\n\\hyphenation{%\n")
        
        # Write exceptions (limit to reasonable size for TeX)
        line = ""
        for word in exceptions[:10000]:  # Limit exceptions
            if len(line) + len(word) + 1 > 75:
                f.write(line.strip() + "\n")  
                line = word + " "
            else:
                line += word + " "
        if line:
            f.write(line.strip() + "\n")
        
        f.write("}\n")
    
    print(f"Written TeX file: {output_file}")
    print(f"  Patterns: {len(patterns)}")
    print(f"  Exceptions: {min(len(exceptions), 10000)}")

def write_plain_patterns(patterns, output_file):
    """Write patterns in plain text format (one per line)."""
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        for p in patterns:
            f.write(p + "\n")
    print(f"Written plain text: {output_file} ({len(patterns)} patterns)")

def write_plain_exceptions(exceptions, output_file):
    """Write exceptions in plain text format."""
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        for word in exceptions:
            f.write(word + "\n")
    print(f"Written exceptions: {output_file} ({len(exceptions)} words)")

def convert_to_hyphen_js(patterns, exceptions, output_file):
    """Convert to hyphen library JS format."""
    # Group patterns by length
    grouped = {}
    for p in patterns:
        # Get pattern length (letters only)
        letters = re.sub(r'[0-9]', '', p.replace('.', ''))
        length = len(letters)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(p)
    
    # Build pattern object
    pattern_obj = {}
    for length, pats in sorted(grouped.items()):
        # Join patterns without separator for compact format
        pattern_obj[str(length)] = ''.join(pats)
    
    # Build exception object (word -> hyphenated)
    exception_obj = {}
    for word in exceptions[:5000]:  # Limit for JS file size
        clean = word.replace('-', '')
        exception_obj[clean] = word
    
    js_content = '''(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.hyphenationPatternsId = factory();
  }
})(this, function () {
  // Indonesian hyphenation patterns
  // Generated from KBBI via orthos.js
  // Patterns: ''' + str(len(patterns)) + '''
  // Exceptions: ''' + str(len(exceptions)) + '''
  return {
    id: 'id',
    leftmin: 2,
    rightmin: 2,
    patterns: ''' + json.dumps(pattern_obj, ensure_ascii=False) + ''',
    exceptions: ''' + json.dumps(exception_obj, ensure_ascii=False) + '''
  };
});
'''
    
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_content)
    print(f"Written hyphen JS: {output_file}")

def write_hypher_format(patterns, exceptions, output_file):
    """Write patterns in hypher library format with grouped patterns."""
    grouped = {}
    for raw_p in patterns:
        p = raw_p
        if p.startswith('.'):
            p = '_' + p[1:]
        if p.endswith('.'):
            p = p[:-1] + '_'
        length = len(p)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(p)
    
    pattern_obj = {}
    for length in sorted(grouped.keys()):
        pattern_obj[str(length)] = ''.join(grouped[length])
    
    hypher_exceptions = [e.replace('-', '\u2027') for e in exceptions if e]
    exception_str = ','.join(hypher_exceptions)
    
    js_content = '''// Indonesian hyphenation patterns for hypher
// Generated from KBBI via orthos.js
(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.Hypher = root.Hypher || {};
    root.Hypher.languages = root.Hypher.languages || {};
    root.Hypher.languages["id"] = factory();
  }
})(this, function () {
  return {
    id: "id",
    leftmin: 2,
    rightmin: 2,
    patterns: ''' + json.dumps(pattern_obj, ensure_ascii=False) + ''',
    exceptions: ''' + json.dumps(exception_str, ensure_ascii=False) + '''
  };
});
'''
    
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_content)
    print(f"Written hypher JS: {output_file}")

def write_hyphenation_patterns_format(patterns, exceptions, output_file):
    """Write patterns in hyphenation-patterns library format."""
    grouped = {}
    for raw_p in patterns:
        p = raw_p
        if p.startswith('.'):
            p = '_' + p[1:]
        if p.endswith('.'):
            p = p[:-1] + '_'
        length = len(p)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(p)
    
    pattern_obj = {}
    for length in sorted(grouped.keys()):
        pattern_obj[str(length)] = ''.join(grouped[length])
    
    hypher_exceptions = [e.replace('-', '\u2027') for e in exceptions if e]
    exception_str = ','.join(hypher_exceptions)

    date = datetime.now().strftime("%Y-%m-%d")
    js_content = f"""// Hyphenation patterns for Bahasa Indonesia (hypher format)
// Generated from KBBI 2025 data via orthos pipeline (id-hyphenation-patterns)
// Patterns: {len(patterns)}, Exceptions: {len(exceptions)}, generated {date}
// Converted by generate_all_formats.py (anchors "." -> "_", exceptions "-" -> U+2027)
(function (root, factory) {{
  if (typeof define === "function" && define.amd) {{
    define([], factory);
  }} else if (typeof module === "object" && module.exports) {{
    module.exports = factory();
  }} else {{
    root.Hypher = root.Hypher || {{}};
    root.Hypher.languages = root.Hypher.languages || {{}};
    root.Hypher.languages["id"] = factory();
  }}
}})(this, function () {{
  return {{
    id: "id",
    leftmin: 2,
    rightmin: 2,
    patterns: {json.dumps(pattern_obj, ensure_ascii=False)},
    exceptions: {json.dumps(exception_str, ensure_ascii=False)}
  }};
}});
"""
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_content)
    print(f"Written hyphenation-patterns JS: {output_file}")

def write_hyphenopoly_json(patterns, exceptions, output_file):
    """Write patterns in Hyphenopoly JSON format."""
    grouped = {}
    for raw_p in patterns:
        p = raw_p
        if p.startswith('.'):
            p = '_' + p[1:]
        if p.endswith('.'):
            p = p[:-1] + '_'
        length = len(p)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(p)
    
    pattern_obj = {}
    for length in sorted(grouped.keys()):
        pattern_obj[str(length)] = ''.join(grouped[length])
    
    hypher_exceptions = [e.replace('-', '\u2027') for e in exceptions if e]
    
    data = {
        "leftmin": 2,
        "rightmin": 2,
        "patterns": pattern_obj,
        "exceptions": ','.join(hypher_exceptions)
    }
    
    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written Hyphenopoly JSON: {output_file}")


def main():
    pattern_file = os.path.join('output', 'hyph-id.pat.txt')
    exception_file = os.path.join('output', 'hyph-id.exceptions.txt')  # Minimal exceptions
    output_dir = 'output'
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("INDONESIAN HYPHENATION PATTERN FORMAT GENERATOR")
    print("=" * 60)
    
    # Load orthos-generated patterns
    if not os.path.exists(pattern_file):
        print(f"Error: Pattern file {pattern_file} not found")
        print("Run: node run_orthos_iterative.js first")
        return
    
    print(f"\nLoading patterns from {pattern_file}...")
    patterns = load_orthos_patterns(pattern_file)
    print(f"  Loaded {len(patterns)} patterns")
    
    # Load exceptions from id.dic
    print(f"\nLoading exceptions from {exception_file}...")
    exceptions = load_exceptions(exception_file)
    print(f"  Loaded {len(exceptions)} exception words")
    
    print("\n" + "-" * 60)
    print("GENERATING OUTPUT FILES")
    print("-" * 60 + "\n")
    
    # Generate all formats
    write_tex_file(patterns, exceptions, os.path.join(output_dir, 'hyph-id.tex'))
    write_plain_exceptions(exceptions, os.path.join(output_dir, 'hyph-id.hyp.txt'))
    convert_to_hyphen_js(patterns, exceptions, os.path.join(output_dir, 'hyphen-id.js'))
    write_hypher_format(patterns, exceptions, os.path.join(output_dir, 'hypher-id.js'))
    write_hyphenation_patterns_format(patterns, exceptions, os.path.join(output_dir, 'hyphenation-patterns-id.js'))
    write_hyphenopoly_json(patterns, exceptions, os.path.join(output_dir, 'hyphenopoly-id.json'))
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Output files in: {output_dir}/")
    print(f"  - hyph-id.pat.txt    (plain patterns)")
    print(f"  - hyph-id.hyp.txt    (exceptions)")
    print(f"  - hyph-id.tex        (TeX format)")
    print(f"  - hyphen-id.js       (hyphen library)")
    print(f"  - hypher-id.js       (hypher library)")
    print(f"  - hyphenation-patterns-id.js")
    print(f"  - hyphenopoly-id.json (Hyphenopoly)")

if __name__ == '__main__':
    main()
