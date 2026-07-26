#!/usr/bin/env node
/**
 * Stage 2: Run additional orthos levels (6-9) for improved accuracy
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG = {
    leftHyphenMin: 2,
    rightHyphenMin: 2,
    dictionaryFile: 'id_orthos.dic',
    orthosPath: path.join(__dirname, 'orthos', 'orthos.js'),
    outputDir: 'output',
    
    // Additional levels 6-9
    levels: [
        { level: 6, patStart: 3, patFinish: 7, goodWt: 1, badWt: 7, thresh: 1 },
        { level: 7, patStart: 3, patFinish: 7, goodWt: 7, badWt: 1, thresh: 1 },
        { level: 8, patStart: 4, patFinish: 8, goodWt: 1, badWt: 9, thresh: 1 },
        { level: 9, patStart: 4, patFinish: 8, goodWt: 9, badWt: 1, thresh: 1 },
    ]
};

async function runLevel(levelConfig, inputPatternFile, outputPatternFile) {
    return new Promise((resolve, reject) => {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`Running Level ${levelConfig.level}`);
        console.log(`  Input: ${inputPatternFile}`);
        console.log(`  Output: ${outputPatternFile}`);
        console.log(`  Params: pat=${levelConfig.patStart}-${levelConfig.patFinish}, g=${levelConfig.goodWt}, b=${levelConfig.badWt}`);
        console.log('='.repeat(60));

        const args = [CONFIG.orthosPath, CONFIG.dictionaryFile, inputPatternFile, outputPatternFile];
        const orthos = spawn('node', args, { cwd: __dirname, stdio: ['pipe', 'pipe', 'pipe'] });

        let output = '';

        orthos.stdout.on('data', (data) => {
            const text = data.toString();
            output += text;
            process.stdout.write(text);

            if (text.includes('left_hyphen_min, right_hyphen_min:')) {
                setTimeout(() => orthos.stdin.write(`${CONFIG.leftHyphenMin} ${CONFIG.rightHyphenMin}\n`), 100);
            } else if (text.includes('hyph_start, hyph_finish:')) {
                setTimeout(() => orthos.stdin.write(`${levelConfig.level} ${levelConfig.level}\n`), 100);
            } else if (text.includes('pat_start, pat_finish:')) {
                setTimeout(() => orthos.stdin.write(`${levelConfig.patStart} ${levelConfig.patFinish}\n`), 100);
            } else if (text.includes('good weight, bad weight, threshold:')) {
                setTimeout(() => orthos.stdin.write(`${levelConfig.goodWt} ${levelConfig.badWt} ${levelConfig.thresh}\n`), 100);
            } else if (text.includes('hyphenate word list?')) {
                setTimeout(() => orthos.stdin.write('n\n'), 100);
            }
        });

        orthos.stderr.on('data', (data) => process.stderr.write(data.toString()));

        orthos.on('close', (code) => {
            if (code === 0) {
                if (fs.existsSync(outputPatternFile)) {
                    const lines = fs.readFileSync(outputPatternFile, 'utf-8').split('\n').filter(l => l.trim());
                    console.log(`\nLevel ${levelConfig.level} complete: ${lines.length} patterns`);
                }
                resolve(output);
            } else {
                reject(new Error(`Exit code ${code}`));
            }
        });

        setTimeout(() => { orthos.kill(); reject(new Error('Timeout')); }, 10 * 60 * 1000);
    });
}

async function main() {
    console.log('Stage 2: Running additional orthos levels 6-9');
    
    // Start from level 5 output
    let currentPatternFile = path.join(CONFIG.outputDir, 'hyph-id.level5.pat.txt');
    
    if (!fs.existsSync(currentPatternFile)) {
        currentPatternFile = path.join(CONFIG.outputDir, 'hyph-id.pat.txt');
    }
    
    if (!fs.existsSync(currentPatternFile)) {
        console.error('No input patterns found. Run initial levels first.');
        process.exit(1);
    }

    for (const levelConfig of CONFIG.levels) {
        const outputFile = path.join(CONFIG.outputDir, `hyph-id.level${levelConfig.level}.pat.txt`);
        
        try {
            await runLevel(levelConfig, currentPatternFile, outputFile);
            currentPatternFile = outputFile;
        } catch (err) {
            console.error(`Error at level ${levelConfig.level}:`, err.message);
            break;
        }
    }

    // Copy final to main output
    const finalOutput = path.join(CONFIG.outputDir, 'hyph-id.pat.txt');
    if (currentPatternFile !== finalOutput && fs.existsSync(currentPatternFile)) {
        fs.copyFileSync(currentPatternFile, finalOutput);
        const lines = fs.readFileSync(finalOutput, 'utf-8').split('\n').filter(l => l.trim());
        console.log(`\nFinal patterns: ${lines.length} (${finalOutput})`);
    }
}

main().catch(console.error);
