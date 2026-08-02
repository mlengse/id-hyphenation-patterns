#!/usr/bin/env node
/*
 * sync_engine_patterns.js
 *
 * Single-source sync: copies the freshly generated hypher engine patterns
 * from output/engine/ into engine/hypher/lib/patterns/.
 *
 * Source of truth: convert_engine_format.js -> output/engine/{id.js,id-exceptions.js}
 *   - id.js            (UMD language object, exceptions inline)
 *   - id-exceptions.js (plain string export)
 *
 * The engine package (engine/hypher) ships lib/patterns/id.js + id-exceptions.js.
 * This script guarantees they always equal the pipeline output, so the engine
 * never drifts from the pattern generation pipeline.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const BASE = path.join(ROOT, '..', '..');

const SRC_DIR = path.join(ROOT, 'output', 'engine');
const DST_DIR = path.join(BASE, 'engine', 'hypher', 'lib', 'patterns');

const FILES = ['id.js', 'id-exceptions.js'];

function main() {
  if (!fs.existsSync(SRC_DIR)) {
    console.error('Source dir not found: ' + SRC_DIR);
    console.error('Run convert_engine_format.js first.');
    process.exit(1);
  }
  fs.mkdirSync(DST_DIR, { recursive: true });

  for (const f of FILES) {
    const src = path.join(SRC_DIR, f);
    const dst = path.join(DST_DIR, f);
    if (!fs.existsSync(src)) {
      console.error('Missing source: ' + src);
      process.exit(1);
    }
    fs.copyFileSync(src, dst);
    const size = fs.statSync(dst).size;
    console.log('[OK] ' + f + ' (' + size.toLocaleString() + ' bytes) -> ' + path.relative(BASE, dst));
  }
  console.log('\nEngine patterns synced from output/engine/ (single source).');
}

main();
