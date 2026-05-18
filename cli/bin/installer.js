/**
 * Installer — copies component files from assets to workspace .github/ directory.
 */

const fs = require('fs');
const path = require('path');
const lockfile = require('./lockfile');

const ASSETS_DIR = path.join(__dirname, '..', 'assets');

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

function getManifestHash(src) {
  if (fs.statSync(src).isDirectory()) {
    const entries = fs.readdirSync(src, { recursive: true }).sort();
    return Buffer.from(JSON.stringify(entries));
  } else {
    return fs.readFileSync(src);
  }
}

/**
 * Install a single component.
 * Returns: 'installed' | 'skipped' | 'updated'
 */
function installComponent(component, targetDir, lock, options = {}) {
  const sourcePath = path.join(ASSETS_DIR, component.sourcePath);
  const destPath = path.join(targetDir, component.targetPath);

  // Check if source exists
  if (!fs.existsSync(sourcePath)) {
    throw new Error(`Source not found: ${component.sourcePath}`);
  }

  // Check if already installed and user-modified
  if (lockfile.isInstalled(lock, component.id) && !options.force) {
    if (fs.existsSync(destPath)) {
      const currentContent = getManifestHash(destPath);
      if (lockfile.checkUserModified(lock, component.id, currentContent)) {
        return 'skipped';
      }
    }
  }

  // Copy
  copyRecursive(sourcePath, destPath);

  // Update lock
  const content = getManifestHash(sourcePath);
  lockfile.markInstalled(lock, component.id, component.targetPath, content, '0.1.0');

  return lockfile.isInstalled(lock, component.id) ? 'updated' : 'installed';
}

/**
 * Uninstall a component (delete files and remove from lock).
 */
function uninstallComponent(component, targetDir, lock) {
  const destPath = path.join(targetDir, component.targetPath);
  if (fs.existsSync(destPath)) {
    const stat = fs.statSync(destPath);
    if (stat.isDirectory()) {
      fs.rmSync(destPath, { recursive: true, force: true });
    } else {
      fs.unlinkSync(destPath);
    }
  }
  lockfile.markRemoved(lock, component.id);
}

module.exports = { installComponent, uninstallComponent, ASSETS_DIR };
