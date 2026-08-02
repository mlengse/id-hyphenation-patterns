#!/usr/bin/env node
/**
 * Automated Iterative Pattern Generator for Indonesian using orthos.js
 * 
 * This script runs orthos.js iteratively through multiple levels to generate
 * optimized hyphenation patterns. It automates the interactive prompts.
 * 
 * Usage: node run_orthos_iterative.js
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configuration for Indonesian hyphenation
const ROOT = path.join(__dirname, '..');
const DATA = path.join(__dirname, '..', '..', '..', 'data', 'kbbi-harvester-cdn', 'hyphenation');

const CONFIG = {
    leftHyphenMin: 2,
    rightHyphenMin: 2,
    dictionaryFile: path.join(DATA, 'id_orthos.dic'),
    emptyPatternFile: path.join(ROOT, 'rules', 'empty.pat'),
    outputDir: path.join(ROOT, 'output'),
    // orthos fork kini repo terpisah di pattern/orthos (sibling). Override via ORTHOS_PATH bila perlu.
    orthosPath: process.env.ORTHOS_PATH || path.join(__dirname, '..', '..', 'orthos', 'orthos.js'),
    
    // Level configurations: [pat_start, pat_finish, good_wt, bad_wt, thresh]
    // Odd levels find hyphens, even levels correct errors
    levels: [
        { level: 1, patStart: 2, patFinish: 4, goodWt: 1, badWt: 2, thresh: 1 },
        { level: 2, patStart: 2, patFinish: 4, goodWt: 2, badWt: 1, thresh: 1 },
        { level: 3, patStart: 2, patFinish: 5, goodWt: 1, badWt: 3, thresh: 1 },
        { level: 4, patStart: 2, patFinish: 5, goodWt: 3, badWt: 1, thresh: 1 },
        { level: 5, patStart: 2, patFinish: 6, goodWt: 1, badWt: 5, thresh: 1 },
    ]
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

// Create empty pattern file if not exists
if (!fs.existsSync(CONFIG.emptyPatternFile)) {
    fs.writeFileSync(CONFIG.emptyPatternFile, '', 'utf-8');
}

/**
 * Run a single orthos level
 */
async function runLevel(levelConfig, inputPatternFile, outputPatternFile) {
    return new Promise((resolve, reject) => {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`Running Level ${levelConfig.level}`);
        console.log(`  Pattern input: ${inputPatternFile}`);
        console.log(`  Pattern output: ${outputPatternFile}`);
        console.log(`  Parameters: pat=${levelConfig.patStart}-${levelConfig.patFinish}, g=${levelConfig.goodWt}, b=${levelConfig.badWt}, t=${levelConfig.thresh}`);
        console.log('='.repeat(60));

        const args = [
            CONFIG.orthosPath,
            CONFIG.dictionaryFile,
            inputPatternFile,
            outputPatternFile
        ];

        const orthos = spawn('node', args, {
            cwd: ROOT,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let errorOutput = '';
        let inputPhase = 'left_right';  // Track which prompt we're responding to

        // Collect output
        orthos.stdout.on('data', (data) => {
            const text = data.toString();
            output += text;
            process.stdout.write(text);

            // Respond to prompts
            if (text.includes('left_hyphen_min, right_hyphen_min:')) {
                setTimeout(() => {
                    orthos.stdin.write(`${CONFIG.leftHyphenMin} ${CONFIG.rightHyphenMin}\n`);
                    inputPhase = 'hyph';
                }, 100);
            } else if (text.includes('hyph_start, hyph_finish:')) {
                setTimeout(() => {
                    // For a single level, hyph_start and hyph_finish are the same
                    orthos.stdin.write(`${levelConfig.level} ${levelConfig.level}\n`);
                    inputPhase = 'pat';
                }, 100);
            } else if (text.includes('pat_start, pat_finish:')) {
                setTimeout(() => {
                    orthos.stdin.write(`${levelConfig.patStart} ${levelConfig.patFinish}\n`);
                    inputPhase = 'gbt';
                }, 100);
            } else if (text.includes('good weight, bad weight, threshold:')) {
                setTimeout(() => {
                    orthos.stdin.write(`${levelConfig.goodWt} ${levelConfig.badWt} ${levelConfig.thresh}\n`);
                    inputPhase = 'wordlist';
                }, 100);
            } else if (text.includes('hyphenate word list?')) {
                setTimeout(() => {
                    orthos.stdin.write('n\n');
                    inputPhase = 'done';
                }, 100);
            }
        });

        orthos.stderr.on('data', (data) => {
            errorOutput += data.toString();
            process.stderr.write(data.toString());
        });

        orthos.on('close', (code) => {
            if (code === 0) {
                console.log(`\nLevel ${levelConfig.level} completed successfully`);
                
                // Check if output file was created
                if (fs.existsSync(outputPatternFile)) {
                    const stats = fs.statSync(outputPatternFile);
                    const lines = fs.readFileSync(outputPatternFile, 'utf-8').split('\n').filter(l => l.trim());
                    console.log(`  Output: ${lines.length} patterns (${(stats.size / 1024).toFixed(1)} KB)`);
                }
                resolve(output);
            } else {
                console.error(`Level ${levelConfig.level} failed with code ${code}`);
                reject(new Error(`orthos exited with code ${code}: ${errorOutput}`));
            }
        });

        orthos.on('error', (err) => {
            reject(err);
        });

        // Timeout after 10 minutes per level
        setTimeout(() => {
            console.error('Timeout - killing orthos process');
            orthos.kill();
            reject(new Error('Timeout'));
        }, 10 * 60 * 1000);
    });
}

/**
 * Run all levels iteratively
 */
async function runAllLevels() {
    console.log('Indonesian Hyphenation Pattern Generator');
    console.log('Using orthos.js (patgen port)');
    console.log(`Dictionary: ${CONFIG.dictionaryFile}`);
    
    // Check dictionary exists
    if (!fs.existsSync(CONFIG.dictionaryFile)) {
        console.error(`Error: Dictionary file ${CONFIG.dictionaryFile} not found`);
        console.error('Run: python prepare_orthos_dictionary.py first');
        process.exit(1);
    }

    const dictStats = fs.statSync(CONFIG.dictionaryFile);
    const dictLines = fs.readFileSync(CONFIG.dictionaryFile, 'utf-8').split('\n').filter(l => l.trim());
    console.log(`  ${dictLines.length} words (${(dictStats.size / 1024).toFixed(1)} KB)`);

    let currentPatternFile = CONFIG.emptyPatternFile;

    for (const levelConfig of CONFIG.levels) {
        const outputFile = path.join(CONFIG.outputDir, `hyph-id.level${levelConfig.level}.pat.txt`);
        
        try {
            await runLevel(levelConfig, currentPatternFile, outputFile);
            currentPatternFile = outputFile;
        } catch (err) {
            console.error(`\nError at level ${levelConfig.level}:`, err.message);
            console.log('Stopping iteration. Last successful patterns are in:', currentPatternFile);
            break;
        }
    }

    // Copy final patterns to output
    const finalOutput = path.join(CONFIG.outputDir, 'hyph-id.pat.txt');
    if (currentPatternFile !== CONFIG.emptyPatternFile && fs.existsSync(currentPatternFile)) {
        fs.copyFileSync(currentPatternFile, finalOutput);
        console.log(`\n${'='.repeat(60)}`);
        console.log('PATTERN GENERATION COMPLETE');
        console.log('='.repeat(60));
        console.log(`Final patterns: ${finalOutput}`);
        
        const finalStats = fs.statSync(finalOutput);
        const finalLines = fs.readFileSync(finalOutput, 'utf-8').split('\n').filter(l => l.trim());
        console.log(`  ${finalLines.length} patterns (${(finalStats.size / 1024).toFixed(1)} KB)`);
    } else {
        console.log('\nNo patterns were generated.');
    }
}

// Interactive mode for single level testing
async function interactiveMode() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const question = (prompt) => new Promise(resolve => rl.question(prompt, resolve));

    console.log('Interactive Mode - Run single level');
    
    const level = parseInt(await question('Level (1-9): '), 10);
    const patStart = parseInt(await question('pat_start (2-4): '), 10);
    const patFinish = parseInt(await question('pat_finish (4-8): '), 10);
    const goodWt = parseInt(await question('good_wt (1-5): '), 10);
    const badWt = parseInt(await question('bad_wt (1-5): '), 10);
    const thresh = parseInt(await question('thresh (1-5): '), 10);
    const inputFile = await question('Input pattern file (empty.pat for level 1): ');
    const outputFile = await question('Output pattern file: ');

    rl.close();

    await runLevel(
        { level, patStart, patFinish, goodWt, badWt, thresh },
        inputFile || CONFIG.emptyPatternFile,
        outputFile || `output/hyph-id.level${level}.pat.txt`
    );
}

// Main
const args = process.argv.slice(2);
if (args.includes('--interactive') || args.includes('-i')) {
    interactiveMode().catch(console.error);
} else {
    runAllLevels().catch(console.error);
}
