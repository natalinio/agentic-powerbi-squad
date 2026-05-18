/**
 * Lock file management — tracks installed components and detects user modifications.
 * Lock file path: <workspace>/.github/.pbi-agent-squad.lock.json
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const LOCK_FILE_NAME = '.pbi-agent-squad.lock.json';

function getLockFilePath(targetDir) {
  return path.join(targetDir, LOCK_FILE_NAME);
}

function hashContent(content) {
  return crypto.createHash('sha256').update(content).digest('hex');
}

function loadLockFile(targetDir) {
  const lockPath = getLockFilePath(targetDir);
  try {
    const raw = fs.readFileSync(lockPath, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return createEmpty();
  }
}

function createEmpty() {
  return {
    version: 1,
    packageVersion: '0.1.0',
    installedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    components: {}
  };
}

function saveLockFile(targetDir, lock) {
  lock.updatedAt = new Date().toISOString();
  const lockPath = getLockFilePath(targetDir);
  fs.mkdirSync(path.dirname(lockPath), { recursive: true });
  fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2), 'utf-8');
}

function isInstalled(lock, componentId) {
  return !!lock.components[componentId];
}

function markInstalled(lock, componentId, targetPath, content, version) {
  lock.components[componentId] = {
    id: componentId,
    version,
    installedAt: new Date().toISOString(),
    contentHash: hashContent(content),
    userModified: false,
    targetPath
  };
}

function markRemoved(lock, componentId) {
  delete lock.components[componentId];
}

function checkUserModified(lock, componentId, currentContent) {
  const entry = lock.components[componentId];
  if (!entry) return false;
  const currentHash = hashContent(currentContent);
  return currentHash !== entry.contentHash;
}

module.exports = {
  loadLockFile,
  saveLockFile,
  createEmpty,
  isInstalled,
  markInstalled,
  markRemoved,
  checkUserModified,
  hashContent
};
