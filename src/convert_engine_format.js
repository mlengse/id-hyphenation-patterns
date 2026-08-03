#!/usr/bin/env node
/*
 * Convert orthos pipeline output to hypher engine format.
 *
 * Inputs (from output/):
 *   hyph-id.pat.txt        — one pattern per line, e.g. ".aba3h", "ad3io", ".be6ria."
 *   hyph-id.exceptions.txt — one hyphenated word per line, e.g. "a-a-bi-no-min"
 *
 * Outputs (to output/engine/):
 *   id.js                 — hypher language object (UMD), patterns grouped by
 *                            raw string length, exceptions inline as "‧"-joined string
 *   id-exceptions.js      — plain string export of the exceptions
 *
 * Transformations required by the engine (lib/hypher.js):
 *   1. Boundary anchors "." -> "_"  — hypher pads words as "_word_", so an
 *      underscore node matches the word boundary; a "." node would never match.
 *   2. Exceptions "a-a" -> "a‧a"    — the engine splits exceptions on U+2027 only
 *      (see createTrie/constructor), ASCII hyphens would become part of the key.
 *
 * Manual overrides (rules/exceptions_overrides.txt) are merged into the
 * exceptions list. These are words patgen cannot learn from general patterns
 * (mostly reduplicated/compound dictionary entries such as "yang-yang"), but
 * KBBI hyphenates them as fixed pairs.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUTPUT_DIR = path.join(ROOT, 'output', 'engine');

function readLines(file) {
  const text = fs.readFileSync(file, 'utf8');
  return text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
}

function convertPatterns() {
  const raw = readLines(path.join(ROOT, 'output', 'hyph-id.pat.txt'));
  const groups = new Map();
  const dropped = [];
  let anchored = 0;

  for (const line of raw) {
    let p = line;
    const hasStart = p.startsWith('.');
    const hasEnd = p.endsWith('.');
    if (hasStart || hasEnd) {
      anchored += 1;
    }
    if (hasStart) {
      p = '_' + p.slice(1);
    }
    if (hasEnd) {
      p = p.slice(0, -1) + '_';
    }
    if (!/^[a-zêéü_0-9]+$/.test(p)) {
      dropped.push(line);
      continue;
    }
    if (!groups.has(p.length)) {
      groups.set(p.length, []);
    }
    groups.get(p.length).push(p);
  }

  const patterns = {};
  for (const [len, list] of [...groups.entries()].sort((a, b) => a[0] - b[0])) {
    patterns[String(len)] = list.join('');
  }
  return { patterns, count: raw.length, anchored, dropped };
}

function convertExceptions() {
  const raw = readLines(path.join(ROOT, 'output', 'hyph-id.exceptions.txt'));
  const overrides = readLines(path.join(ROOT, 'rules', 'exceptions_overrides.txt'));
  const out = [];
  const indexByKey = new Map();

  const add = (line) => {
    if (!/^[a-zêéü-]+$/.test(line)) {
      return;
    }
    const key = line.replace(/-/g, '');
    if (indexByKey.has(key)) {
      out.splice(indexByKey.get(key), 1);
    }
    indexByKey.set(key, out.length);
    out.push(line.replace(/-/g, '\u2027'));
  };

  for (const line of [...raw, ...overrides]) {
    add(line);
  }
  return out;
}

function umdId(patterns, exceptions, stats) {
  const date = new Date().toISOString().slice(0, 10);
  return `// Indonesian hyphenation patterns for hypher
// Generated from KBBI 2025 data via orthos pipeline (id-hyphenation-patterns)
// Patterns: ${stats.patterns}, Exceptions: ${stats.exceptions}, generated ${date}
// Converted by convert_engine_format.js (anchors "." -> "_", exceptions "-" -> U+2027)
(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.Hypher.languages["id"] = factory();
  }
})(this, function () {
  return ${languageObject(patterns, exceptions)};
});
`;
}

function languageObject(patterns, exceptions) {
  return JSON.stringify({
    id: 'id',
    leftmin: 2,
    rightmin: 2,
    patterns: patterns,
    exceptions: exceptions.join(', '),
  });
}

function cjsId(patterns, exceptions, stats) {
  const date = new Date().toISOString().slice(0, 10);
  return `// Hyphenation patterns for Bahasa Indonesia (hypher format)
// Generated from KBBI 2025 data via orthos pipeline (id-hyphenation-patterns)
// Patterns: ${stats.patterns}, Exceptions: ${stats.exceptions}, generated ${date}
// Converted by convert_engine_format.js (anchors "." -> "_", exceptions "-" -> U+2027)
module.exports = ${languageObject(patterns, exceptions)};
`;
}

function main() {
  const { patterns, count, anchored, dropped } = convertPatterns();
  const exceptions = convertExceptions();

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const idJs = umdId(patterns, exceptions, {
    patterns: count,
    exceptions: exceptions.length,
  });
  const cjsJs = cjsId(patterns, exceptions, {
    patterns: count,
    exceptions: exceptions.length,
  });
  const exceptionsJs = `// Indonesian hyphenation exceptions for hypher (KBBI 2025, orthos pipeline)\n// ${exceptions.length} words, separator: U+2027\nmodule.exports = ${JSON.stringify(exceptions.join(', '))};\n`;

  fs.writeFileSync(path.join(OUTPUT_DIR, 'id.js'), idJs, 'utf8');
  fs.writeFileSync(path.join(OUTPUT_DIR, 'id.cjs.js'), cjsJs, 'utf8');
  fs.writeFileSync(path.join(OUTPUT_DIR, 'id-exceptions.js'), exceptionsJs, 'utf8');

  console.log('Patterns: ' + count + ' total, ' + anchored + ' dot-anchored (converted to _)');
  console.log('Patterns dropped: ' + dropped.length + (dropped.length ? ' -> ' + JSON.stringify(dropped) : ''));
  console.log('Pattern length groups: ' + [...Object.keys(patterns)].map((k) => k + '=' + patterns[k].length).join(' '));
  console.log('Exceptions: ' + exceptions.length);
  console.log('id.js: ' + idJs.length + ' chars, id.cjs.js: ' + cjsJs.length + ' chars, id-exceptions.js: ' + exceptionsJs.length + ' chars');
  console.log('Written to ' + OUTPUT_DIR);
}

main();
