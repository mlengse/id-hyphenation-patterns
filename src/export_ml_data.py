#!/usr/bin/env python3
"""
Export id.dic to ML training format for Google Colab.

Creates train/val/test splits in JSON format:
- train.json (80%)
- val.json (10%)
- test.json (10%)
"""

import json
import random
import os

def load_dictionary(filepath):
    """Load hyphenated words from id.dic."""
    words = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            if not word or ' ' in word:
                continue
            if word.startswith('-') or word.endswith('-'):
                continue
            clean = word.replace('-', '')
            if '-' in word and clean.isalpha() and len(clean) >= 2:
                words.append({
                    'input': clean,
                    'output': word,
                    'syllables': word.split('-')
                })
    return words

def export_splits(data, output_dir):
    """Export train/val/test splits."""
    random.seed(42)  # Reproducible
    random.shuffle(data)
    
    n = len(data)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)
    
    splits = {
        'train': data[:train_end],
        'val': data[train_end:val_end],
        'test': data[val_end:]
    }
    
    os.makedirs(output_dir, exist_ok=True)
    
    for name, split_data in splits.items():
        filepath = os.path.join(output_dir, f'{name}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(split_data, f, ensure_ascii=False, indent=2)
        print(f"  {name}.json: {len(split_data)} examples")
    
    # Also export combined for analysis
    with open(os.path.join(output_dir, 'all.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  all.json: {len(data)} examples")

def compute_stats(data):
    """Compute dataset statistics."""
    lengths = [len(d['input']) for d in data]
    syllables = [len(d['syllables']) for d in data]
    
    return {
        'total': len(data),
        'avg_length': sum(lengths) / len(lengths),
        'max_length': max(lengths),
        'avg_syllables': sum(syllables) / len(syllables),
        'max_syllables': max(syllables)
    }

def main():
    input_file = 'id.dic'
    output_dir = 'ml_data'
    
    print("=" * 60)
    print("EXPORT TRAINING DATA FOR ML MODEL")
    print("=" * 60)
    
    print(f"\nLoading {input_file}...")
    data = load_dictionary(input_file)
    print(f"  Loaded {len(data)} words")
    
    stats = compute_stats(data)
    print(f"\nStatistics:")
    print(f"  Average word length: {stats['avg_length']:.1f}")
    print(f"  Max word length: {stats['max_length']}")
    print(f"  Average syllables: {stats['avg_syllables']:.1f}")
    print(f"  Max syllables: {stats['max_syllables']}")
    
    print(f"\nExporting to {output_dir}/...")
    export_splits(data, output_dir)
    
    print(f"\n✓ Done! Upload {output_dir}/ to Colab")

if __name__ == '__main__':
    main()
