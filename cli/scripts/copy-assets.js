/**
 * Copies .github/{agents,skills,references,templates,copilot-instructions.md}
 * into cli/assets/ for distribution in the npm package.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const ASSETS_DIR = path.join(__dirname, '..', 'assets');

const SOURCES = [
  { src: '.github/agents', dest: 'agents' },
  { src: '.github/skills', dest: 'skills' },
  { src: '.github/references', dest: 'references' },
  { src: '.github/templates', dest: 'templates' },
  { src: '.github/copilot-instructions.md', dest: 'copilot-instructions.md' }
];

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

console.log('Copying assets into CLI package...');

// Clean and recreate
if (fs.existsSync(ASSETS_DIR)) {
  fs.rmSync(ASSETS_DIR, { recursive: true });
}
fs.mkdirSync(ASSETS_DIR, { recursive: true });

for (const { src, dest } of SOURCES) {
  const srcPath = path.join(ROOT, src);
  const destPath = path.join(ASSETS_DIR, dest);
  if (fs.existsSync(srcPath)) {
    copyRecursive(srcPath, destPath);
    console.log(`  ${src} → assets/${dest}`);
  } else {
    console.warn(`  ⚠ Not found: ${src}`);
  }
}

console.log('✓ Assets ready for packaging.');
