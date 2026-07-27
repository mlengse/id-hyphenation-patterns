#!/usr/bin/env python3
"""
Download word details and extract hyphenation data from KBBI Harvester CDN.
This version handles Windows filename restrictions by not saving individual JSON files,
just extracting the hyphenation data directly.

Output:
- kbbi_vi_hyphenation.txt: Tab-separated (word<tab>hyphenation)
- kbbi_vi_hyphenation.json: Full data as JSON array
- kbbi_vi_hyphenation_dict.json: Simple word->hyphenation mapping
"""

import urllib.request
import urllib.parse
import json
import time
import concurrent.futures
from pathlib import Path
from typing import Optional
import threading
import ssl

# Disable SSL verification for GitHub (sometimes needed on Windows)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Configuration
BASE_URL = "https://raw.githubusercontent.com/Naandalist/kbbi-harvester-cdn/main/word-details"
WORDLIST_DIR = Path("kbbi-vi-wordlist")
OUTPUT_TXT = Path("kbbi_vi_hyphenation.txt")
OUTPUT_JSON = Path("kbbi_vi_hyphenation.json")
OUTPUT_DICT = Path("kbbi_vi_hyphenation_dict.json")

# Rate limiting - be gentle with GitHub
MAX_WORKERS = 5
REQUEST_DELAY = 0.1

# Progress tracking
progress_lock = threading.Lock()
downloaded_count = 0
failed_words = []
all_hyphenations = []
hyphenation_dict = {}

def encode_word_for_url(word: str) -> str:
    """Encode word for URL (spaces become %20, etc.)."""
    return urllib.parse.quote(word, safe='')

def get_first_letter(word: str) -> str:
    """Get the first letter of a word (uppercase) for folder path."""
    if not word:
        return 'A'
    first_char = word[0].upper()
    if first_char.isalpha():
        return first_char
    return 'A'  # Default fallback

def download_and_extract(word: str) -> Optional[list]:
    """Download word detail and extract hyphenation."""
    global downloaded_count
    
    letter = get_first_letter(word)
    encoded_word = encode_word_for_url(word)
    url = f"{BASE_URL}/{letter}/{encoded_word}.json"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
        content = response.read().decode('utf-8')
        data = json.loads(content)
        
        # Extract hyphenation entries
        hyphenations = []
        word_from_data = data.get('word', word)
        
        for entry in data.get('entries', []):
            nama = entry.get('nama', '')
            if nama:
                hyphenations.append({
                    'word': word_from_data,
                    'hyphenation': nama,
                    'id': entry.get('id', ''),
                    'nomor': entry.get('nomor', '')
                })
        
        with progress_lock:
            downloaded_count += 1
            if downloaded_count % 1000 == 0:
                print(f"  Progress: {downloaded_count} words downloaded...")
        
        return hyphenations
        
    except Exception as e:
        with progress_lock:
            failed_words.append((word, str(e)))
        return None

def process_letter(letter: str, words: list):
    """Process all words for a given letter using thread pool."""
    global all_hyphenations, hyphenation_dict
    
    print(f"\nProcessing {letter}: {len(words)} words...", end=" ", flush=True)
    letter_entries = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_and_extract, word): word for word in words}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    with progress_lock:
                        all_hyphenations.extend(result)
                        letter_entries += len(result)
                        
                        # Add to dictionary (first entry per word)
                        for h in result:
                            w = h['word']
                            if w not in hyphenation_dict:
                                hyphenation_dict[w] = h['hyphenation']
            except Exception as e:
                pass
            
            time.sleep(REQUEST_DELAY)
    
    print(f"✓ ({letter_entries} entries)")

def save_progress():
    """Save current progress to files."""
    global all_hyphenations, hyphenation_dict
    
    # Save text format
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        for h in all_hyphenations:
            f.write(f"{h['word']}\t{h['hyphenation']}\n")
    
    # Save JSON array
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_hyphenations, f, ensure_ascii=False, indent=2)
    
    # Save dictionary
    with open(OUTPUT_DICT, 'w', encoding='utf-8') as f:
        json.dump(hyphenation_dict, f, ensure_ascii=False, indent=2)

def main():
    global all_hyphenations, hyphenation_dict
    
    print("=" * 60)
    print("KBBI VI Hyphenation Downloader")
    print("=" * 60)
    print("\nThis will download word details and extract hyphenation patterns.")
    print("Output files:")
    print(f"  - {OUTPUT_TXT}")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_DICT}")
    print()
    
    if not WORDLIST_DIR.exists():
        print(f"ERROR: Wordlist directory not found: {WORDLIST_DIR}")
        print("Please run download_kbbi_vi_wordlist.py first!")
        return
    
    # Count total words
    total_words = 0
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    words_by_letter = {}
    
    for letter in letters:
        wordlist_file = WORDLIST_DIR / f"{letter}.txt"
        if wordlist_file.exists():
            words = [w.strip() for w in wordlist_file.read_text(encoding='utf-8').strip().split('\n') if w.strip()]
            words_by_letter[letter] = words
            total_words += len(words)
    
    print(f"Total words to download: {total_words:,}")
    print(f"Estimated time: ~{total_words * 0.2 / 60:.0f} minutes")
    print("\nStarting download...\n")
    
    start_time = time.time()
    
    try:
        for letter in letters:
            if letter in words_by_letter:
                process_letter(letter, words_by_letter[letter])
                # Save progress after each letter
                save_progress()
    except KeyboardInterrupt:
        print("\n\nInterrupted! Saving progress...")
        save_progress()
    
    elapsed = time.time() - start_time
    
    # Final save
    save_progress()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Time elapsed: {elapsed / 60:.1f} minutes")
    print(f"Words downloaded: {downloaded_count:,}")
    print(f"Failed downloads: {len(failed_words):,}")
    print(f"Hyphenation entries: {len(all_hyphenations):,}")
    print(f"Unique words in dict: {len(hyphenation_dict):,}")
    print(f"\nFiles saved:")
    print(f"  - {OUTPUT_TXT}")
    print(f"  - {OUTPUT_JSON}")
    print(f"  - {OUTPUT_DICT}")
    
    # Show sample
    print("\nSample entries:")
    samples = list(hyphenation_dict.items())[:15]
    for word, hyph in samples:
        print(f"  {word:25} -> {hyph}")
    
    # Save failed words for debugging
    if failed_words:
        with open("failed_words.txt", 'w', encoding='utf-8') as f:
            for word, error in failed_words[:100]:
                f.write(f"{word}\t{error}\n")
        print(f"\nFailed words saved to: failed_words.txt")

if __name__ == "__main__":
    main()
