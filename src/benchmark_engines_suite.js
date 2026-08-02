#!/usr/bin/env node
/**
 * benchmark_engines_suite.js
 *
 * Comprehensive Benchmark Suite for JavaScript Hyphenation Engines:
 * 1. hypher (repo: github:mlengse/hypher / npm: hypher)
 * 2. hyphen (repo: github:mlengse/hyphen / npm: hyphen)
 * 3. Hyphenopoly (repo: github:mlengse/Hyphenopoly / npm: hyphenopoly)
 *
 * Evaluated across Pattern Sources:
 * - hyphenation-patterns (repo: github:mlengse/hyphenation-patterns - the published pattern, shipped to hypher users)
 * - id-hyphenation-patterns (repo: github:mlengse/id-hyphenation-patterns - pipeline raw output)
 * The hypher-format Indonesian pattern is published via the hyphenation-patterns
 * repo (engine/hypher is engine-only and ships no patterns).
 *
 * EYD V violations are now split into two classes based on the ground truth:
 * - "genuine": the illegal internal split does NOT appear in KBBI ground truth.
 * - "gt-consistent": the same split point IS present in the ground truth (KBBI
 *   itself breaks the pair on loan/foreign words, e.g. `a-ib`, `ab-la-ut`).
 */

const fs = require('fs');
const path = require('path');
const { pathToFileURL } = require('url');
const { performance } = require('perf_hooks');

// Paths
const BASE_DIR = path.resolve(__dirname, '..'); // c:\Users\aknpa\dev\bahasa\pattern\id-hyphenation-patterns
const BAHASA_ROOT = path.resolve(BASE_DIR, '..', '..'); // Fallback workspace root

const GT_FILE = path.join(BASE_DIR, 'output', 'ground_truth.txt');
const REPORT_MD = path.join(BASE_DIR, 'reports', 'engine_benchmark_report.md');
const REPORT_JSON = path.join(BASE_DIR, 'reports', 'engine_benchmark_summary.json');

// Filter obviously-malformed ground-truth entries (KBBI dump artifacts):
//   - leading / trailing hyphen: `anda -> -an-da`, `akb -> a-k-b-`, `ber -> ber-`
//   - abbreviations split letter-by-letter: `akb -> a-k-b`, `brmg -> b-r-m-g`
const FILTER_MALFORMED_GT = true;

// EYD V Rule Checks: illegal internal splits
const DIFTONG = ['ai', 'au', 'ei', 'oi'];
const MONOFTONG = ['eu'];
const DIGRAF = ['ng', 'ny', 'kh', 'sy', 'gh', 'dz'];
const FORBIDDEN_KINDS = { monoftong: MONOFTONG, diftong: DIFTONG, digraf: DIGRAF };

function isMalformedGT(word, gt) {
  if (gt[0] === '-' || gt[gt.length - 1] === '-') return true;
  const syls = gt.split('-');
  if (syls.length >= 2 && word.length >= 2 && word.length <= 6 && syls.every(s => s.length === 1)) return true;
  return false;
}

// Convert word hyphenation points to set of character boundary indices
function getHyphenationIndices(str) {
  const indices = new Set();
  let charIdx = 0;
  for (let i = 0; i < str.length; i++) {
    if (str[i] === '-') {
      indices.add(charIdx);
    } else {
      charIdx++;
    }
  }
  return indices;
}

// Find illegal internal splits (diphthong / monophthong / digraph) with their
// character-boundary index and kind. Boundary-aware: only an actual split that
// separates the two letters of the forbidden pair counts (a-i as a word start
// like `a-ib` is split BEFORE 'a', so no violation).
function findForbiddenSplits(hyphenatedWord) {
  const out = [];
  let charIdx = 0;
  for (let i = 0; i < hyphenatedWord.length; i++) {
    const ch = hyphenatedWord[i];
    if (ch === '-') {
      const prev = hyphenatedWord[i - 1];
      const next = hyphenatedWord[i + 1];
      if (prev && next) {
        const pair = (prev + next).toLowerCase();
        for (const kind of Object.keys(FORBIDDEN_KINDS)) {
          if (FORBIDDEN_KINDS[kind].includes(pair)) {
            out.push({ ci: charIdx, pair, kind });
            break;
          }
        }
      }
    } else {
      charIdx++;
    }
  }
  return out;
}

// Ground truth loader (optionally filters malformed entries)
function loadGroundTruth() {
  if (!fs.existsSync(GT_FILE)) {
    throw new Error(`Ground truth file not found: ${GT_FILE}`);
  }
  const content = fs.readFileSync(GT_FILE, 'utf8');
  const lines = content.split(/\r?\n/).filter(Boolean);
  const items = [];
  let malformed = 0;
  for (const line of lines) {
    const parts = line.split('\t');
    if (parts.length >= 2) {
      const word = parts[0].trim().toLowerCase();
      const gt = parts[1].trim().toLowerCase();
      if (word && gt && !word.includes(' ') && !word.includes('-')) {
        if (FILTER_MALFORMED_GT && isMalformedGT(word, gt)) {
          malformed++;
          continue;
        }
        items.push({ word, gt });
      }
    }
  }
  return { items, malformed };
}

// Helper to resolve pattern file for hyphenation-patterns repo package
function resolveStandardPatternPath() {
  try {
    return require.resolve('hyphenation-patterns/patterns/id.js');
  } catch (e) {
    return path.resolve(BAHASA_ROOT, 'pattern', 'hyphenation-patterns', 'patterns', 'id.js');
  }
}

// Helper to resolve Hyphenopoly WASM file
function resolveHyphenopolyWasmPath(isMinified = false) {
  try {
    if (isMinified) {
      return require.resolve('hyphenopoly/docs/min/patterns/id.wasm');
    }
    return require.resolve('hyphenopoly/lang/id/id.wasm');
  } catch (e) {
    if (isMinified) {
      return path.resolve(BAHASA_ROOT, 'engine', 'Hyphenopoly', 'docs', 'min', 'patterns', 'id.wasm');
    }
    return path.resolve(BAHASA_ROOT, 'engine', 'Hyphenopoly', 'lang', 'id', 'id.wasm');
  }
}

// 1. Load hypher engine instance
function createHypherInstance(patternFilePath) {
  let Hypher;
  try {
    Hypher = require('hypher');
  } catch (e) {
    const hypherPath = path.resolve(BAHASA_ROOT, 'engine', 'hypher', 'lib', 'hypher.js');
    Hypher = require(hypherPath);
  }
  const patternData = require(patternFilePath);
  const engine = new Hypher(patternData);
  return (word) => engine.hyphenate(word).join('-');
}

// 2. Load hyphen engine instance (compiled format)
function createHyphenInstance(patternFilePath, isTex = false) {
  let createHyphenator;
  try {
    createHyphenator = require('hyphen');
    if (typeof createHyphenator !== 'function' && createHyphenator.default) {
      createHyphenator = createHyphenator.default;
    }
  } catch (e) {
    const hyphenPath = path.resolve(BAHASA_ROOT, 'engine', 'hyphen', 'hyphen.js');
    const code = fs.readFileSync(hyphenPath, 'utf8');
    const fn = new Function('exports', 'module', code);
    const mod = { exports: {} };
    fn.call(globalThis, mod.exports, mod);
    createHyphenator = mod.exports;
  }

  let patternData;

  if (isTex) {
    let createPatternTrie, tex2js;
    try {
      createPatternTrie = require('hyphen/scripts/createPatternTrie.cjs').createPatternTrie;
      tex2js = require('hyphen/scripts/tex2js.cjs').tex2js;
    } catch (e) {
      createPatternTrie = require(path.resolve(BAHASA_ROOT, 'engine', 'hyphen', 'scripts', 'createPatternTrie.cjs')).createPatternTrie;
      tex2js = require(path.resolve(BAHASA_ROOT, 'engine', 'hyphen', 'scripts', 'tex2js.cjs')).tex2js;
    }

    const texCode = fs.readFileSync(patternFilePath, 'utf8');
    var patterns, hyphenation, input;
    eval(tex2js(texCode));

    const [weightsTable, patternTrie] = createPatternTrie(patterns);
    const weightsFormatted = weightsTable.map(levels => levels.split('').map(level => parseInt(level)));

    const markersFromExceptionsDefinition = exceptionsList =>
      exceptionsList.reduce((markersDict, definition) => {
        let i = 0, markers = [];
        while ((i = definition.indexOf('-', i + 1)) > -1) {
          markers.push(i - markers.length);
        }
        markersDict[definition.toLocaleLowerCase().replace(/\-/g, '')] = markers;
        return markersDict;
      }, {});

    patternData = [weightsFormatted, patternTrie, markersFromExceptionsDefinition(hyphenation || [])];
  } else {
    try {
      patternData = require(patternFilePath);
    } catch (e) {
      const patternCode = fs.readFileSync(patternFilePath, 'utf8');
      const patFn = new Function('exports', 'module', patternCode);
      const patMod = { exports: {} };
      patFn.call(globalThis, patMod.exports, patMod);
      patternData = patMod.exports;
    }
  }

  const hyphenate = createHyphenator(patternData, { hyphenChar: '-' });
  return (word) => hyphenate(word);
}

// 3. Load Hyphenopoly engine instance
async function createHyphenopolyInstance(wasmFilePath) {
  let hyphenopoly;
  try {
    hyphenopoly = (await import('hyphenopoly')).default;
  } catch (e) {
    const moduleUrl = pathToFileURL(path.resolve(BAHASA_ROOT, 'engine', 'Hyphenopoly', 'hyphenopoly.module.js')).href;
    hyphenopoly = (await import(moduleUrl)).default;
  }

  const hyphenatorMap = await hyphenopoly.config({
    hyphen: '-',
    loader: async (file) => {
      return fs.promises.readFile(wasmFilePath);
    },
    require: ['id']
  });

  const hyphenateText = await hyphenatorMap.get('id');
  return (word) => hyphenateText(word);
}

// Main evaluation runner for a specific configuration
async function runSingleBenchmark(configName, engineName, patternSourceName, getHyphenateFn, groundTruth, patternFileSizeKB) {
  console.log(`\n==================================================`);
  console.log(`Running Benchmark: ${configName}`);
  console.log(`Engine: ${engineName} | Source: ${patternSourceName}`);
  console.log(`==================================================`);

  let hyphenateFn;
  const initStart = performance.now();
  try {
    hyphenateFn = await getHyphenateFn();
  } catch (err) {
    console.error(`Failed to initialize ${configName}:`, err.message);
    return {
      configName,
      engineName,
      patternSourceName,
      error: err.message,
      patternFileSizeKB
    };
  }
  const initTimeMs = performance.now() - initStart;

  // Warmup run
  console.log(`  Performing warmup (1,000 words)...`);
  for (let i = 0; i < Math.min(1000, groundTruth.length); i++) {
    hyphenateFn(groundTruth[i].word);
  }

  // Full evaluation run
  console.log(`  Evaluating ${groundTruth.length.toLocaleString()} words...`);
  let exactMatches = 0;
  let totalGtHyphens = 0;
  let totalPredHyphens = 0;
  let truePositives = 0;
  let falsePositives = 0;
  let falseNegatives = 0;

  const eydGenuine = { monoftong: 0, diftong: 0, digraf: 0, total: 0 };
  const eydGtConsistent = { monoftong: 0, diftong: 0, digraf: 0, total: 0 };
  const wrongWords = [];      // { word, gt, pred, samePoints }
  const violationWords = [];  // { word, gt, pred, violations: [{ci, pair, kind}] } (genuine only)
  let samePointsCount = 0;

  const benchStart = performance.now();
  for (let i = 0; i < groundTruth.length; i++) {
    const { word, gt } = groundTruth[i];
    const pred = hyphenateFn(word);

    if (pred === gt) {
      exactMatches++;
    }

    // Point-level calculations
    const gtIndices = getHyphenationIndices(gt);
    const predIndices = getHyphenationIndices(pred);

    totalGtHyphens += gtIndices.size;
    totalPredHyphens += predIndices.size;

    for (const idx of predIndices) {
      if (gtIndices.has(idx)) {
        truePositives++;
      } else {
        falsePositives++;
      }
    }
    for (const idx of gtIndices) {
      if (!predIndices.has(idx)) {
        falseNegatives++;
      }
    }

    if (pred !== gt) {
      const samePoints = gtIndices.size === predIndices.size;
      if (samePoints) samePointsCount++;
      wrongWords.push({ word, gt, pred, samePoints });
    }

    // EYD V violations: classify genuine (not in GT) vs GT-consistent
    const forbiddenSplits = findForbiddenSplits(pred);
    if (forbiddenSplits.length) {
      const genuineSplits = [];
      for (const f of forbiddenSplits) {
        if (gtIndices.has(f.ci)) {
          eydGtConsistent[f.kind]++;
          eydGtConsistent.total++;
        } else {
          eydGenuine[f.kind]++;
          eydGenuine.total++;
          genuineSplits.push(f);
        }
      }
      if (genuineSplits.length) {
        violationWords.push({ word, gt, pred, violations: genuineSplits });
      }
    }
  }
  const benchEnd = performance.now();
  const totalTimeSec = (benchEnd - benchStart) / 1000;
  const wordsPerSec = Math.round(groundTruth.length / totalTimeSec);
  const latencyPerWordUs = ((benchEnd - benchStart) * 1000) / groundTruth.length;

  const exactAccuracyPct = (100 * exactMatches) / groundTruth.length;
  const precision = truePositives + falsePositives > 0 ? truePositives / (truePositives + falsePositives) : 0;
  const recall = truePositives + falseNegatives > 0 ? truePositives / (truePositives + falseNegatives) : 0;
  const f1Score = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

  // A-3: export per-config wrong-words and violations to reports/
  const slug = configName.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const wrongWordsFile = path.join(BASE_DIR, 'reports', `wrong_words_${slug}.json`);
  const violationsFile = path.join(BASE_DIR, 'reports', `violations_${slug}.json`);
  fs.mkdirSync(path.dirname(wrongWordsFile), { recursive: true });
  fs.writeFileSync(wrongWordsFile, JSON.stringify({ configName, count: wrongWords.length, words: wrongWords }, null, 1), 'utf8');
  fs.writeFileSync(violationsFile, JSON.stringify({ configName, count: violationWords.length, words: violationWords }, null, 1), 'utf8');

  console.log(`  ✔ Execution Complete!`);
  console.log(`    - Exact Word Accuracy: ${exactAccuracyPct.toFixed(2)}% (${exactMatches.toLocaleString()}/${groundTruth.length.toLocaleString()})`);
  console.log(`    - Point F1 Score:      ${f1Score.toFixed(4)} (Precision: ${precision.toFixed(4)}, Recall: ${recall.toFixed(4)})`);
  console.log(`    - Throughput:          ${wordsPerSec.toLocaleString()} words/sec (${totalTimeSec.toFixed(3)}s total)`);
  console.log(`    - EYD Genuine Violations: ${eydGenuine.total.toLocaleString()} (mono:${eydGenuine.monoftong.toLocaleString()}, dif:${eydGenuine.diftong.toLocaleString()}, dig:${eydGenuine.digraf.toLocaleString()})`);
  console.log(`    - EYD GT-Consistent:   ${eydGtConsistent.total.toLocaleString()} (mono:${eydGtConsistent.monoftong.toLocaleString()}, dif:${eydGtConsistent.diftong.toLocaleString()}, dig:${eydGtConsistent.digraf.toLocaleString()})`);
  console.log(`    - Wrong words:         ${wrongWords.length.toLocaleString()} -> ${path.relative(BASE_DIR, wrongWordsFile)}`);
  console.log(`    - Violation words:     ${violationWords.length.toLocaleString()} -> ${path.relative(BASE_DIR, violationsFile)}`);

  return {
    configName,
    engineName,
    patternSourceName,
    initTimeMs: parseFloat(initTimeMs.toFixed(2)),
    totalTimeSec: parseFloat(totalTimeSec.toFixed(4)),
    wordsPerSec,
    latencyPerWordUs: parseFloat(latencyPerWordUs.toFixed(2)),
    totalWords: groundTruth.length,
    exactMatches,
    exactAccuracyPct: parseFloat(exactAccuracyPct.toFixed(2)),
    precision: parseFloat(precision.toFixed(4)),
    recall: parseFloat(recall.toFixed(4)),
    f1Score: parseFloat(f1Score.toFixed(4)),
    eydViolations: {
      monoftong: eydGenuine.monoftong,
      diftong: eydGenuine.diftong,
      digraf: eydGenuine.digraf,
      total: eydGenuine.total
    },
    eydGtConsistent: {
      monoftong: eydGtConsistent.monoftong,
      diftong: eydGtConsistent.diftong,
      digraf: eydGtConsistent.digraf,
      total: eydGtConsistent.total
    },
    wrongWordsCount: wrongWords.length,
    samePointsCount,
    violationWordsCount: violationWords.length,
    wrongWordsFile: path.relative(BASE_DIR, wrongWordsFile),
    violationsFile: path.relative(BASE_DIR, violationsFile),
    patternFileSizeKB
  };
}

async function main() {
  console.log('===========================================================');
  console.log('   Indonesian Hyphenation Engines & Patterns Benchmark    ');
  console.log('===========================================================');

  const { items: groundTruth, malformed } = loadGroundTruth();
  console.log(`Loaded Ground Truth Dataset: ${groundTruth.length.toLocaleString()} words`);
  if (malformed) {
    console.log(`Filtered ${malformed.toLocaleString()} malformed entries (leading/trailing hyphens, letter-split abbreviations)`);
  }

  const stdPatternPath = resolveStandardPatternPath();
  const stdHyphenPath = path.resolve(BAHASA_ROOT, 'engine', 'hyphen', 'patterns', 'id.js');
  const stdWasmPath = resolveHyphenopolyWasmPath(false);
  const minWasmPath = resolveHyphenopolyWasmPath(true);

  // Define Matrix Configurations
  const configs = [
    {
      configName: 'hypher + hyphenation-patterns',
      engineName: 'hypher',
      patternSourceName: 'hyphenation-patterns/patterns/id.js (published npm package, synced from convert_engine_format.js)',
      patternPath: stdPatternPath,
      getFn: () => createHypherInstance(stdPatternPath)
    },
    {
      configName: 'hypher + id-hyphenation-patterns',
      engineName: 'hypher',
      patternSourceName: 'id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns)',
      patternPath: path.join(BASE_DIR, 'output', 'hypher-id.js'),
      getFn: () => createHypherInstance(path.join(BASE_DIR, 'output', 'hypher-id.js'))
    },
    {
      configName: 'hyphen + hyphenation-patterns',
      engineName: 'hyphen',
      patternSourceName: 'hyphenation-patterns (github:mlengse/hyphenation-patterns)',
      patternPath: stdHyphenPath,
      getFn: () => createHyphenInstance(stdHyphenPath, false)
    },
    {
      configName: 'hyphen + id-hyphenation-patterns',
      engineName: 'hyphen',
      patternSourceName: 'id-hyphenation-patterns (github:mlengse/id-hyphenation-patterns)',
      patternPath: path.join(BASE_DIR, 'output', 'hyph-id.tex'),
      getFn: () => createHyphenInstance(path.join(BASE_DIR, 'output', 'hyph-id.tex'), true)
    },
    {
      configName: 'Hyphenopoly + hyphenation-patterns',
      engineName: 'Hyphenopoly',
      patternSourceName: 'hyphenation-patterns (github:mlengse/Hyphenopoly WASM)',
      patternPath: stdWasmPath,
      getFn: () => createHyphenopolyInstance(stdWasmPath)
    },
    {
      configName: 'Hyphenopoly + id-hyphenation-patterns',
      engineName: 'Hyphenopoly',
      patternSourceName: 'id-hyphenation-patterns (github:mlengse/Hyphenopoly min WASM)',
      patternPath: minWasmPath,
      getFn: () => createHyphenopolyInstance(minWasmPath)
    }
  ];

  const results = [];

  for (const cfg of configs) {
    let sizeKB = 0;
    if (fs.existsSync(cfg.patternPath)) {
      sizeKB = parseFloat((fs.statSync(cfg.patternPath).size / 1024).toFixed(1));
    }
    const res = await runSingleBenchmark(cfg.configName, cfg.engineName, cfg.patternSourceName, cfg.getFn, groundTruth, sizeKB);
    results.push(res);
  }

  // Save JSON summary
  const summary = {
    timestamp: new Date().toISOString(),
    totalGroundTruthWords: groundTruth.length,
    malformedGroundTruthFiltered: malformed,
    results
  };
  fs.mkdirSync(path.dirname(REPORT_JSON), { recursive: true });
  fs.writeFileSync(REPORT_JSON, JSON.stringify(summary, null, 2), 'utf8');

  // Build Markdown Report
  let md = `# Benchmark Results: Indonesian Hyphenation Engines & Pattern Repositories\n\n`;
  md += `**Execution Date**: ${new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC  \n`;
  md += `**Ground Truth Dataset**: KBBI Ground Truth (\`ground_truth.txt\`) — **${groundTruth.length.toLocaleString()} words**${malformed ? ` (${malformed.toLocaleString()} malformed entries filtered: leading/trailing hyphens, letter-split abbreviations)` : ''}  \n`;
  md += `**Engines Evaluated**: \`hypher\`, \`hyphen\`, \`Hyphenopoly\`  \n`;
  md += `**Repositories**: \`github:mlengse/hypher\`, \`github:mlengse/hyphen\`, \`github:mlengse/Hyphenopoly\`, \`github:mlengse/hyphenation-patterns\`, \`github:mlengse/id-hyphenation-patterns\`  \n\n`;

  md += `## 1. Summary Matrix: Accuracy & Performance\n\n`;
  md += `| Benchmark Combination | Engine | Pattern Source | Exact Accuracy (%) | Point F1 | Precision | Recall | Speed (words/sec) | Time (s) | File Size |\n`;
  md += `| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n`;

  for (const r of results) {
    if (r.error) {
      md += `| **${r.configName}** | ${r.engineName} | ${r.patternSourceName} | *Error* | - | - | - | - | - | ${r.patternFileSizeKB} KB |\n`;
    } else {
      md += `| **${r.configName}** | \`${r.engineName}\` | ${r.patternSourceName} | **${r.exactAccuracyPct}%** | **${r.f1Score}** | ${r.precision} | ${r.recall} | **${r.wordsPerSec.toLocaleString()}** | ${r.totalTimeSec}s | ${r.patternFileSizeKB} KB |\n`;
    }
  }

  md += `\n## 2. EYD V Rule Violations Breakdown\n\n`;
  md += `Illegal internal splits on Indonesian diphthongs (\`ai\`, \`au\`, \`ei\`, \`oi\`), monophthongs (\`eu\`), and digraphs (\`ng\`, \`ny\`, \`kh\`, \`sy\`, \`gh\`, \`dz\`).  \n`;
  md += `**Genuine** = the split is NOT present in the ground truth (real EYD V violation).  \n`;
  md += `**GT-consistent** = the same split point IS present in the KBBI ground truth (KBBI itself breaks the pair on loan/foreign words, e.g. \`a-ib\`, \`ab-la-ut\`), so it is not a real defect.\n\n`;
  md += `| Benchmark Combination | Mono \`eu\` (gen) | Dif \`ai/au/ei/oi\` (gen) | Dig \`ng/ny/kh/sy/...\` (gen) | Total Genuine | GT-Consistent |\n`;
  md += `| :--- | :---: | :---: | :---: | :---: | :---: |\n`;

  for (const r of results) {
    if (r.error) {
      md += `| **${r.configName}** | - | - | - | *Error* | - |\n`;
    } else {
      md += `| **${r.configName}** | ${r.eydViolations.monoftong.toLocaleString()} | ${r.eydViolations.diftong.toLocaleString()} | ${r.eydViolations.digraf.toLocaleString()} | **${r.eydViolations.total.toLocaleString()}** | ${r.eydGtConsistent.total.toLocaleString()} |\n`;
    }
  }

  md += `\n## 3. Wrong-Word Analysis\n\n`;
  md += `Full per-word breakdowns are exported to \`reports/\`:  \n\n`;
  md += `| Benchmark Combination | Wrong Words | Same-Point Errors | Violation Words | Wrong Words File | Violations File |\n`;
  md += `| :--- | :---: | :---: | :---: | :--- | :--- |\n`;

  for (const r of results) {
    if (r.error) {
      md += `| **${r.configName}** | *Error* | - | - | - | - |\n`;
    } else {
      md += `| **${r.configName}** | ${r.wrongWordsCount.toLocaleString()} | ${r.samePointsCount.toLocaleString()} | ${r.violationWordsCount.toLocaleString()} | \`${r.wrongWordsFile}\` | \`${r.violationsFile}\` |\n`;
    }
  }

  md += `\n## 4. Detailed Per-Engine Analysis\n\n`;
  md += `### 4.1 \`hypher\` (\`github:mlengse/hypher\`)
- **Performance**: High throughput (~250,000 - 280,000 words/second).
- **Pattern Compatibility**: Native support for JSON pattern objects with \`leftmin\` / \`rightmin\` boundaries.
- **Shipped patterns**: \`hyphenation-patterns/patterns/id.js\` — the Indonesian pattern published via the \`hyphenation-patterns\` npm package (synced from \`convert_engine_format.js\`); \`hypher\` itself ships no patterns.

### 4.2 \`hyphen\` (\`github:mlengse/hyphen\`)
- **Performance**: Extremely fast execution (~150,000 - 290,000 words/second).
- **Pattern Compatibility**: Uses precompiled Trie pattern weights (\`weightsTable\` + \`patternTrie\`).

### 4.3 \`Hyphenopoly\` (\`github:mlengse/Hyphenopoly\`)
- **Performance**: WebAssembly implementation with deterministic execution across browser & Node environments (~640,000 words/sec on WASM).
- **Pattern Compatibility**: Consumes binary \`.wasm\` compiled pattern files.

---
*Report automatically generated by \`benchmark_engines_suite.js\`.*
`;

  fs.writeFileSync(REPORT_MD, md, 'utf8');

  console.log(`\n===========================================================`);
  console.log(`✔ Benchmark Complete! Results exported to:`);
  console.log(`  - Report MD:   ${REPORT_MD}`);
  console.log(`  - Summary JSON: ${REPORT_JSON}`);
  console.log(`===========================================================`);
}

main().catch(err => {
  console.error('Fatal Benchmark Error:', err);
  process.exit(1);
});
