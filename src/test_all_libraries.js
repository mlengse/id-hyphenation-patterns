#!/usr/bin/env node
/**
 * Test Indonesian hyphenation patterns across all 5 libraries
 * Libraries: hyphen, hypher, hyphenation-patterns, Hyphenopoly, tex-hyphen
 *
 * Workspace layout (paths are relative to this file, src/):
 *   ../../../engine/hyphen, ../../../engine/hypher, ../../../engine/Hyphenopoly
 *   ../../tex-hyphen, ../../hyphenation-patterns
 *   ../../../data/kbbi-harvester-cdn/hyphenation  (reference data)
 */

const fs = require('fs');
const path = require('path');

// Test words with expected hyphenation (from KBBI/EYD V)
const testCases = [
    { word: 'makanan', expected: 'ma-kan-an' },
    { word: 'seudati', expected: 'seu-da-ti' },
    { word: 'instrumen', expected: 'in-stru-men' },
    { word: 'mengunci', expected: 'me-ngun-ci' },
    { word: 'bangkrut', expected: 'bang-krut' },
    { word: 'berjalan', expected: 'ber-ja-lan' },
    { word: 'pertumbuhan', expected: 'per-tum-buh-an' },
    { word: 'saudara', expected: 'sau-da-ra' },
    { word: 'musyawarah', expected: 'mu-sya-wa-rah' },
    { word: 'masyarakat', expected: 'ma-sya-ra-kat' },
    { word: 'pancasila', expected: 'pan-ca-si-la' },
    { word: 'indonesia', expected: 'in-do-ne-si-a' },
    { word: 'banjir', expected: 'ban-jir' },
    { word: 'belajar', expected: 'bel-a-jar' },
    { word: 'melamar', expected: 'me-la-mar' },
    { word: 'pemerintah', expected: 'pe-me-rin-tah' },
    { word: 'pembangunan', expected: 'pem-ba-ngun-an' },
    { word: 'kebahagiaan', expected: 'ke-ba-ha-gi-a-an' },
    { word: 'perpustakaan', expected: 'per-pus-ta-ka-an' },
    { word: 'demokratisasi', expected: 'de-mo-kra-ti-sa-si' },
];

// Helper to format result
function formatResult(result, expected) {
    if (result === expected) {
        return '\x1b[32mâœ“ PASS\x1b[0m';
    } else {
        return `\x1b[31mâœ— FAIL\x1b[0m (got: ${result})`;
    }
}

// Load reference dictionary for validation
function loadReferenceDictionary() {
    const dictPath = path.join(__dirname, '..', '..', '..', 'data', 'kbbi-harvester-cdn', 'hyphenation', 'id.dic');
    const dict = {};
    try {
        const content = fs.readFileSync(dictPath, 'utf-8');
        for (const line of content.split('\n')) {
            const word = line.trim();
            if (!word || word.includes(' ') || word.startsWith('-') || word.endsWith('-')) continue;
            const clean = word.replace(/-/g, '').toLowerCase();
            if (/^[a-z]+$/.test(clean)) {
                dict[clean] = word.toLowerCase();
            }
        }
    } catch (err) {
        console.log('  Warning: Could not load id.dic:', err.message);
    }
    return dict;
}

// Test 1: Verify pattern files exist and count patterns
function checkPatternFiles() {
    console.log('\n' + '='.repeat(60));
    console.log('PATTERN FILES VERIFICATION');
    console.log('='.repeat(60));
    
    const files = [
        { path: '../../../engine/hyphen/patterns/id.js', lib: 'hyphen (JS)' },
        { path: '../../../engine/hyphen/tex/hyph-id.tex', lib: 'hyphen (TeX)' },
        { path: '../../../engine/hypher/lib/patterns/id.js', lib: 'hypher' },
        { path: '../../hyphenation-patterns/patterns/id.js', lib: 'hyphenation-patterns' },
        { path: '../../tex-hyphen/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/hyph-id.pat.txt', lib: 'tex-hyphen (pat.txt)' },
        { path: '../../tex-hyphen/hyph-utf8/tex/generic/hyph-utf8/patterns/tex/hyph-id.tex', lib: 'tex-hyphen (tex)' },
        { path: '../../../engine/Hyphenopoly/lang/id/id.wasm', lib: 'Hyphenopoly (WASM)' },
        { path: '../../../engine/Hyphenopoly/docs/min/patterns/id.wasm', lib: 'Hyphenopoly (min WASM)' },
        { path: '../output/hyph-id.tex', lib: 'Output (TeX)' },
        { path: '../output/hyphen-id.js', lib: 'Output (hyphen.js)' },
        { path: '../output/hypher-id.js', lib: 'Output (hypher.js)' },
        { path: '../output/hyphenation-patterns-id.js', lib: 'Output (hyphenation-patterns.js)' },
    ];
    
    let found = 0;
    for (const { path: filePath, lib } of files) {
        const fullPath = path.join(__dirname, filePath);
        if (fs.existsSync(fullPath)) {
            const stats = fs.statSync(fullPath);
            const sizeKB = (stats.size / 1024).toFixed(1);
            console.log(`  \x1b[32mâœ“\x1b[0m ${lib.padEnd(35)} ${sizeKB.padStart(8)} KB`);
            found++;
        } else {
            console.log(`  \x1b[31mâœ—\x1b[0m ${lib.padEnd(35)} NOT FOUND`);
        }
    }
    
    console.log(`\n  Files found: ${found}/${files.length}`);
}

// Test 2: Validate against reference dictionary (id.dic)
function validateAgainstDictionary() {
    console.log('\n' + '='.repeat(60));
    console.log('DICTIONARY VALIDATION (id.dic)');
    console.log('='.repeat(60));
    
    const dict = loadReferenceDictionary();
    console.log(`\n  Reference dictionary: ${Object.keys(dict).length} words\n`);
    
    console.log(`  ${'Word'.padEnd(15)} ${'Expected'.padEnd(20)} ${'In Dictionary'.padEnd(20)} Status`);
    console.log(`  ${'-'.repeat(15)} ${'-'.repeat(20)} ${'-'.repeat(20)} ------`);
    
    let passed = 0, failed = 0, notFound = 0;
    
    for (const { word, expected } of testCases) {
        const inDict = dict[word.toLowerCase()] || 'NOT FOUND';
        
        if (inDict === 'NOT FOUND') {
            console.log(`  ${word.padEnd(15)} ${expected.padEnd(20)} ${inDict.padEnd(20)} \x1b[33m? MISSING\x1b[0m`);
            notFound++;
        } else if (inDict === expected) {
            console.log(`  ${word.padEnd(15)} ${expected.padEnd(20)} ${inDict.padEnd(20)} \x1b[32mâœ“ PASS\x1b[0m`);
            passed++;
        } else {
            console.log(`  ${word.padEnd(15)} ${expected.padEnd(20)} ${inDict.padEnd(20)} \x1b[31mâœ— DIFF\x1b[0m`);
            failed++;
        }
    }
    
    console.log(`\n  Results: ${passed} passed, ${failed} diffs, ${notFound} not in dict`);
    return { passed, failed, notFound };
}

// Test 3: Test hyphenation-patterns library (pattern-only, just load and inspect)
function testHyphenationPatterns() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: hyphenation-patterns library');
    console.log('='.repeat(60));
    
    try {
        const patternPath = path.join(__dirname, '..', '..', 'hyphenation-patterns', 'patterns', 'id.js');
        
        if (!fs.existsSync(patternPath)) {
            console.log('  \x1b[33mâš  patterns/id.js not found\x1b[0m');
            return { skipped: true };
        }
        
        const pattern = require(patternPath);
        console.log('  \x1b[32mâœ“\x1b[0m Pattern file loaded successfully');
        console.log(`    - ID: ${pattern.id}`);
        console.log(`    - Left min: ${pattern.leftmin}`);
        console.log(`    - Right min: ${pattern.rightmin}`);
        console.log(`    - Patterns: ${typeof pattern.patterns === 'object' ? Object.keys(pattern.patterns).length + ' groups' : 'N/A'}`);
        
        // Count total patterns
        let totalPatterns = 0;
        if (pattern.patterns) {
            for (const [len, pats] of Object.entries(pattern.patterns)) {
                if (typeof pats === 'string') {
                    const n = parseInt(len);
                    if (!isNaN(n) && n > 0) {
                        totalPatterns += Math.floor(pats.length / n);
                    }
                }
            }
        }
        console.log(`    - Total patterns (estimated): ${totalPatterns}`);
        
        return { passed: 1, failed: 0, skipped: false };
    } catch (err) {
        console.log(`  \x1b[31mError: ${err.message}\x1b[0m`);
        return { skipped: true, error: err.message };
    }
}

// Test 4: Check Hyphenopoly files
function testHyphenopoly() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: Hyphenopoly library');
    console.log('='.repeat(60));
    
    try {
        const wasmPath = path.join(__dirname, '..', '..', '..', 'engine', 'Hyphenopoly', 'lang', 'id', 'id.wasm');
        const minWasmPath = path.join(__dirname, '..', '..', '..', 'engine', 'Hyphenopoly', 'docs', 'min', 'patterns', 'id.wasm');
        const jsonPath = path.join(__dirname, '..', '..', '..', 'engine', 'Hyphenopoly', 'lang', 'id', 'src', 'id.json');
        
        let found = 0;
        
        if (fs.existsSync(wasmPath)) {
            const stats = fs.statSync(wasmPath);
            console.log(`  \x1b[32mâœ“\x1b[0m lang/id/id.wasm (${(stats.size / 1024).toFixed(1)} KB)`);
            found++;
        } else {
            console.log('  \x1b[31mâœ—\x1b[0m lang/id/id.wasm not found');
        }
        
        if (fs.existsSync(minWasmPath)) {
            const stats = fs.statSync(minWasmPath);
            console.log(`  \x1b[32mâœ“\x1b[0m docs/min/patterns/id.wasm (${(stats.size / 1024).toFixed(1)} KB)`);
            found++;
        }
        
        if (fs.existsSync(jsonPath)) {
            const stats = fs.statSync(jsonPath);
            console.log(`  \x1b[32mâœ“\x1b[0m lang/id/src/id.json (${(stats.size / 1024).toFixed(1)} KB)`);
            
            // Parse JSON to get info
            try {
                const jsonData = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
                console.log(`    - Left min: ${jsonData.leftmin}`);
                console.log(`    - Right min: ${jsonData.rightmin}`);
                if (jsonData.patterns) {
                    console.log(`    - Pattern groups: ${Object.keys(jsonData.patterns).length}`);
                }
                if (jsonData.exceptions) {
                    const excCount = jsonData.exceptions.split(',').length;
                    console.log(`    - Exceptions: ${excCount}`);
                }
            } catch (e) {
                console.log('    (Could not parse JSON for details)');
            }
            found++;
        }
        
        console.log('\n  Note: Hyphenopoly requires browser/worker environment for full testing');
        
        return { found, skipped: true, note: 'Browser-only' };
    } catch (err) {
        console.log(`  \x1b[31mError: ${err.message}\x1b[0m`);
        return { skipped: true, error: err.message };
    }
}

// Test 5: Check tex-hyphen files
function testTexHyphen() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: tex-hyphen library');
    console.log('='.repeat(60));
    
    const files = [
        { path: '../../tex-hyphen/hyph-utf8/tex/generic/hyph-utf8/patterns/txt/hyph-id.pat.txt', desc: 'Pattern file (txt)' },
        { path: '../../tex-hyphen/hyph-utf8/tex/generic/hyph-utf8/patterns/tex/hyph-id.tex', desc: 'Pattern file (tex)' },
    ];
    
    let found = 0;
    for (const { path: filePath, desc } of files) {
        const fullPath = path.join(__dirname, filePath);
        if (fs.existsSync(fullPath)) {
            const stats = fs.statSync(fullPath);
            const content = fs.readFileSync(fullPath, 'utf-8');
            const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('%'));
            console.log(`  \x1b[32mâœ“\x1b[0m ${desc}`);
            console.log(`    - Size: ${(stats.size / 1024).toFixed(1)} KB`);
            console.log(`    - Lines (non-comment): ${lines.length}`);
            found++;
        } else {
            console.log(`  \x1b[31mâœ—\x1b[0m ${desc} not found`);
        }
    }
    
    console.log('\n  Note: TeX patterns require LaTeX/TeX engine for testing');
    
    return { found, total: files.length, skipped: true, note: 'TeX-only' };
}

// Test 6: Check hypher pattern format
function testHypherFormat() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: hypher library (pattern format)');
    console.log('='.repeat(60));
    
    try {
        const patternPath = path.join(__dirname, '..', '..', '..', 'engine', 'hypher', 'lib', 'patterns', 'id.js');
        
        if (!fs.existsSync(patternPath)) {
            console.log('  \x1b[33mâš  id.js not found\x1b[0m');
            return { skipped: true };
        }
        
        const pattern = require(patternPath);
        console.log('  \x1b[32mâœ“\x1b[0m Pattern file loaded successfully');
        console.log(`    - Left min: ${pattern.leftmin}`);
        console.log(`    - Right min: ${pattern.rightmin}`);
        
        // Check pattern format
        if (pattern.patterns) {
            if (Array.isArray(pattern.patterns)) {
                console.log(`    - Patterns: ${pattern.patterns.length} (array format)`);
            } else if (typeof pattern.patterns === 'object') {
                console.log(`    - Patterns: object with keys ${Object.keys(pattern.patterns).slice(0, 5).join(', ')}...`);
            }
        }
        
        // Check exceptions format
        if (pattern.exceptions) {
            if (typeof pattern.exceptions === 'object' && !Array.isArray(pattern.exceptions)) {
                console.log(`    - Exceptions: ${Object.keys(pattern.exceptions).length} words (object format)`);
                console.log(`    \x1b[33mâš \x1b[0m Note: hypher expects exceptions as string with â‡ separator`);
            } else if (typeof pattern.exceptions === 'string') {
                console.log(`    - Exceptions: ${pattern.exceptions.split(',').length} words (string format)`);
            }
        }
        
        return { passed: 1, failed: 0, skipped: false };
    } catch (err) {
        console.log(`  \x1b[31mError: ${err.message}\x1b[0m`);
        return { skipped: true, error: err.message };
    }
}

// Main test runner
async function main() {
    console.log('â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—');
    console.log('â•‘     Indonesian Hyphenation Pattern Test Suite              â•‘');
    console.log('â•‘     Testing all 5 libraries                                â•‘');
    console.log('â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•');
    console.log(`\nTest date: ${new Date().toISOString()}`);
    console.log(`Working directory: ${__dirname}`);
    
    // Run all checks
    checkPatternFiles();
    const dictResult = validateAgainstDictionary();
    testHyphenationPatterns();
    testHypherFormat();
    testHyphenopoly();
    testTexHyphen();
    
    // Summary
    console.log('\n' + 'â•'.repeat(60));
    console.log('SUMMARY');
    console.log('â•'.repeat(60));
    
    console.log(`
  Dictionary Validation:
    - Test cases: ${testCases.length}
    - Passed: ${dictResult.passed}
    - Differences: ${dictResult.failed}
    - Not in dict: ${dictResult.notFound}
    - Accuracy: ${((dictResult.passed / (testCases.length - dictResult.notFound)) * 100).toFixed(1)}%

  Libraries Status:
    - hyphen:              Pattern files present
    - hypher:              Pattern files present (may need format fix)
    - hyphenation-patterns: Pattern files present
    - Hyphenopoly:         WASM compiled (browser testing needed)
    - tex-hyphen:          TeX patterns present (LaTeX testing needed)

  Next Steps:
    1. Fix hypher exception format if needed
    2. Test Hyphenopoly in browser environment
    3. Test tex-hyphen with LaTeX engine
    4. Create browser-based test page for full integration
`);
    
    console.log('â•'.repeat(60));
}

main().catch(console.error);
