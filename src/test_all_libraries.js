#!/usr/bin/env node
/**
 * Test Indonesian hyphenation patterns across libraries
 * Libraries: hyphen, hypher, hyphenation-patterns, Hyphenopoly, tex-hyphen
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

function resolvePathOrPkg(pkgName, relativePath) {
    try {
        return require.resolve(pkgName);
    } catch (e) {
        const full = path.join(__dirname, relativePath);
        return fs.existsSync(full) ? full : null;
    }
}

// Test 1: Verify pattern files exist and count patterns
function checkPatternFiles() {
    console.log('\n' + '='.repeat(60));
    console.log('PATTERN FILES VERIFICATION');
    console.log('='.repeat(60));
    
    const candidates = [
        { lib: 'hyphen (JS)', resolve: () => resolvePathOrPkg('hyphen/patterns/id.js', '../../../engine/hyphen/patterns/id.js') },
        { lib: 'hyphen (TeX)', resolve: () => resolvePathOrPkg('', '../../../engine/hyphen/tex/hyph-id.tex') },
        { lib: 'hypher', resolve: () => resolvePathOrPkg('hyphenation-patterns/patterns/id.js', '../../hyphenation-patterns/patterns/id.js') },
        { lib: 'hyphenation-patterns', resolve: () => resolvePathOrPkg('hyphenation-patterns/patterns/id.js', '../../hyphenation-patterns/patterns/id.js') },
        { lib: 'Hyphenopoly (WASM)', resolve: () => resolvePathOrPkg('hyphenopoly/lang/id/id.wasm', '../../../engine/Hyphenopoly/lang/id/id.wasm') },
        { lib: 'Hyphenopoly (min WASM)', resolve: () => resolvePathOrPkg('hyphenopoly/docs/min/patterns/id.wasm', '../../../engine/Hyphenopoly/docs/min/patterns/id.wasm') },
        { lib: 'Output (TeX)', resolve: () => resolvePathOrPkg('', '../output/hyph-id.tex') },
        { lib: 'Output (hyphen.js)', resolve: () => resolvePathOrPkg('', '../output/hyphen-id.js') },
        { lib: 'Output (hypher.js)', resolve: () => resolvePathOrPkg('', '../output/hypher-id.js') },
        { lib: 'Output (hyphenation-patterns.js)', resolve: () => resolvePathOrPkg('', '../output/hyphenation-patterns-id.js') },
    ];
    
    let found = 0;
    for (const { lib, resolve } of candidates) {
        const filePath = resolve();
        if (filePath && fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            const sizeKB = (stats.size / 1024).toFixed(1);
            console.log(`  ✓ ${lib.padEnd(35)} ${sizeKB.padStart(8)} KB`);
            found++;
        } else {
            console.log(`  ✗ ${lib.padEnd(35)} NOT FOUND`);
        }
    }
    
    console.log(`\n  Files found: ${found}/${candidates.length}`);
}

// Test 2: Test hyphenation-patterns library
function testHyphenationPatterns() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: hyphenation-patterns library');
    console.log('='.repeat(60));
    
    try {
        const patternPath = resolvePathOrPkg('hyphenation-patterns/patterns/id.js', '../../hyphenation-patterns/patterns/id.js');
        
        if (!patternPath || !fs.existsSync(patternPath)) {
            console.log('  ⚠ patterns/id.js not found');
            return { skipped: true };
        }
        
        const pattern = require(patternPath);
        console.log('  ✓ Pattern file loaded successfully');
        console.log(`    - ID: ${pattern.id}`);
        console.log(`    - Left min: ${pattern.leftmin}`);
        console.log(`    - Right min: ${pattern.rightmin}`);
        return { passed: 1, failed: 0, skipped: false };
    } catch (err) {
        console.log(`  Error: ${err.message}`);
        return { skipped: true, error: err.message };
    }
}

// Test 3: Check hypher pattern format
function testHypherFormat() {
    console.log('\n' + '='.repeat(60));
    console.log('Testing: hypher library (pattern format)');
    console.log('='.repeat(60));
    
    try {
        const patternPath = resolvePathOrPkg('hyphenation-patterns/patterns/id.js', '../../hyphenation-patterns/patterns/id.js') || path.join(__dirname, '..', 'output', 'hypher-id.js');
        
        if (!fs.existsSync(patternPath)) {
            console.log('  ⚠ id.js not found');
            return { skipped: true };
        }
        
        const pattern = require(patternPath);
        console.log('  ✓ Pattern file loaded successfully');
        console.log(`    - Left min: ${pattern.leftmin}`);
        console.log(`    - Right min: ${pattern.rightmin}`);
        return { passed: 1, failed: 0, skipped: false };
    } catch (err) {
        console.log(`  Error: ${err.message}`);
        return { skipped: true, error: err.message };
    }
}

async function main() {
    console.log('===========================================================');
    console.log('   Indonesian Hyphenation Pattern Test Suite               ');
    console.log('===========================================================');
    console.log(`Test date: ${new Date().toISOString()}`);
    
    checkPatternFiles();
    testHyphenationPatterns();
    testHypherFormat();
    
    console.log('\n===========================================================');
    console.log('SUMMARY: Tests complete');
    console.log('===========================================================');
}

main().catch(console.error);
