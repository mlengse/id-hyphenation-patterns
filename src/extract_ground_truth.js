#!/usr/bin/env node
/*
 * Extract hyphenation ground truth from the KBBI harvester word-details JSON
 * collection (data/kbbi-harvester-cdn/word-details). Each entry's `nama` field
 * holds the official syllable split with dots, e.g. "ab.strak".
 *
 * Output: output/ground_truth.txt — lines of "word\thy-phen-a-tion"
 * (dot separators normalized to ASCII hyphens, lowercase, single words only).
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DEFAULT_DIR = 'C:\\Users\\aknpa\\dev\\bahasa\\data\\kbbi-harvester-cdn\\word-details';
const OUT_FILE = path.join(__dirname, '..', 'output', 'ground_truth.txt');

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...walk(full));
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      out.push(full);
    }
  }
  return out;
}

function main() {
  const dir = process.argv[2] || DEFAULT_DIR;
  if (!fs.existsSync(dir)) {
    console.error('Directory not found: ' + dir);
    process.exit(1);
  }
  const files = walk(dir);
  const seen = new Set();
  const result = [];
  let parsed = 0;
  let entries = 0;

  for (const file of files) {
    let data;
    try {
      data = JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch (e) {
      continue;
    }
    parsed += 1;
    if (!data || !Array.isArray(data.entries)) {
      continue;
    }
    for (const en of data.entries) {
      const nama = en && en.nama;
      if (typeof nama !== 'string') {
        continue;
      }
      entries += 1;
      const hyphenated = nama.trim().toLowerCase().replace(/\./g, '-');
      if (!/^[a-zêéü-]+$/.test(hyphenated)) {
        continue; // phrases, digits, abbreviations, special chars
      }
      if (hyphenated.indexOf('-') === -1) {
        continue; // single syllable — not a hyphenation datum
      }
      const word = hyphenated.replace(/-/g, '');
      if (word.length < 3 || seen.has(word)) {
        continue;
      }
      seen.add(word);
      result.push(word + '\t' + hyphenated);
    }
  }

  fs.writeFileSync(OUT_FILE, result.join('\n') + '\n', 'utf8');
  console.log('Parsed ' + parsed + ' JSON files (' + files.length + ' present)');
  console.log('Entries seen: ' + entries);
  console.log('Ground truth words: ' + result.length);
  console.log('Written to ' + OUT_FILE);
}

main();
