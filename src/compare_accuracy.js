#!/usr/bin/env node
/*
 * Compare hyphenation accuracy of the current engine id.js against the
 * converted orthos-pipeline id.js, using KBBI ground truth
 * (output/ground_truth.txt, one "word\thy-phen-a-tion" per line).
 *
 * Reports: overall exact-match accuracy per engine, plus per-word regressions
 * (current correct, gen wrong) and gains (gen correct, current wrong).
 */
'use strict';

const fs = require('fs');
const path = require('path');

let Hypher;
try {
  Hypher = require('hypher');
} catch (e) {
  Hypher = require(path.join(__dirname, '..', '..', '..', 'engine', 'hypher', 'lib', 'hypher.js'));
}

let currentPattern;
try {
  currentPattern = require('hyphenation-patterns/patterns/id.js');
} catch (e) {
  const fallbackPath = path.join(__dirname, '..', '..', '..', 'engine', 'hypher', 'lib', 'patterns', 'id.js');
  currentPattern = fs.existsSync(fallbackPath) ? require(fallbackPath) : require(path.join(__dirname, '..', 'output', 'hypher-id.js'));
}

const GEN_ID = path.join(__dirname, '..', 'output', 'hypher-id.js');
const GT_FILE = path.join(__dirname, '..', 'output', 'ground_truth.txt');

const current = new Hypher(currentPattern);
const generated = new Hypher(require(GEN_ID));

const lines = fs.readFileSync(GT_FILE, 'utf8').split(/\r?\n/).filter(Boolean);

function summarize(engine, name) {
  let exact = 0;
  const detail = [];
  for (const line of lines) {
    const [word, gt] = line.split('\t');
    const got = engine.hyphenate(word).join('-');
    const ok = got === gt;
    if (ok) {
      exact += 1;
    }
    detail.push({ word, gt, got, ok });
  }
  return { name, exact, total: lines.length, detail };
}

const cur = summarize(current, 'current');
const gen = summarize(generated, 'generated');

function report(label, items) {
  console.log('\n' + label + ' (' + items.length + '):');
  for (const it of items.slice(0, 40)) {
    console.log('  ' + it.word.padEnd(20) + ' gt=' + it.gt.padEnd(20) + ' cur=' + it.curGot.padEnd(20) + ' gen=' + it.genGot);
  }
  if (items.length > 40) {
    console.log('  ... and ' + (items.length - 40) + ' more');
  }
}

console.log('Ground truth words: ' + lines.length);
console.log('Current engine: ' + cur.exact + '/' + cur.total + ' (' + (100 * cur.exact / cur.total).toFixed(2) + '%)');
console.log('Generated conv: ' + gen.exact + '/' + gen.total + ' (' + (100 * gen.exact / gen.total).toFixed(2) + '%)');

const curMap = new Map(cur.detail.map((d) => [d.word, d]));

const regressions = [];
const gains = [];
const bothWrong = [];
for (const d of gen.detail) {
  const c = curMap.get(d.word);
  if (d.ok && !c.ok) {
    gains.push({ word: d.word, gt: d.gt, curGot: c.got, genGot: d.got });
  } else if (!d.ok && c.ok) {
    regressions.push({ word: d.word, gt: d.gt, curGot: c.got, genGot: d.got });
  } else if (!d.ok && !c.ok) {
    bothWrong.push({ word: d.word, gt: d.gt, curGot: c.got, genGot: d.got });
  }
}

report('REGRESSIONS (current correct, generated wrong)', regressions);
report('GAINS (generated correct, current wrong)', gains);
report('BOTH WRONG (sample)', bothWrong.slice(0, 25));

const reg = new Set(regressions.map((r) => r.word));
const gain = new Set(gains.map((g) => g.word));
const both = new Set(bothWrong.map((b) => b.word));
console.log('\nUnique word counts: regressions=' + reg.size + ' gains=' + gain.size + ' bothWrong=' + both.size);

fs.writeFileSync(
  path.join(__dirname, '..', 'output', 'accuracy_report.txt'),
  ['Ground truth: ' + lines.length, 'Current: ' + cur.exact + '/' + cur.total + ' (' + (100 * cur.exact / cur.total).toFixed(2) + '%)', 'Generated: ' + gen.exact + '/' + gen.total + ' (' + (100 * gen.exact / gen.total).toFixed(2) + '%)', '', '=== REGRESSIONS ==='].join('\n') + '\n',
  'utf8'
);
