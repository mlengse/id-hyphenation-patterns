#!/usr/bin/env python3
"""
Run patgen with predefined parameters for Indonesian hyphenation patterns.
Based on standard patgen parameter recommendations.
"""

import subprocess
import os

# Patgen parameters for Indonesian
# Format for each level: (pat_start, pat_finish, good_weight, bad_weight, threshold)
# These are typical values for initial pattern generation

PATGEN_INPUT = """1 9
1 2 1 1 1
2 3 1 1 1
3 4 1 1 1
4 5 1 2 1
5 6 1 2 1
6 7 1 2 1
7 8 1 2 1
8 9 1 2 1
9 9 1 2 1
"""

def run_patgen():
    """Run patgen with the input parameters."""
    cmd = [
        'patgen',
        'id_words.dic',
        'empty.pat', 
        'hyph-id-new.tex',
        'id.tra'
    ]
    
    print("Running patgen...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run patgen with input piped
    result = subprocess.run(
        cmd,
        input=PATGEN_INPUT,
        text=True,
        capture_output=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print("-" * 50)
    print(f"Return code: {result.returncode}")
    
    if os.path.exists('hyph-id-new.tex'):
        # Count patterns
        with open('hyph-id-new.tex', 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple count of pattern-like entries
            patterns = [l for l in content.split() if any(c.isdigit() for c in l)]
            print(f"Output file created with approximately {len(patterns)} patterns")
    else:
        print("WARNING: Output file not created!")

if __name__ == '__main__':
    run_patgen()
