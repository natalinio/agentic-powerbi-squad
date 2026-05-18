#!/usr/bin/env node
'use strict';

const path = require('path');
const fs = require('fs');
const { COMPONENT_REGISTRY, getComponentsByType, getComponentById, findComponents, resolveDependencies } = require('./registry');
const { loadLockFile, saveLockFile } = require('./lockfile');
const { installComponent, uninstallComponent } = require('./installer');

// ─── Helpers ────────────────────────────────────────────────────────────────────

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
  bold: '\x1b[1m'
};

function log(msg) { console.log(msg); }
function success(msg) { console.log(`${COLORS.green}✓${COLORS.reset} ${msg}`); }
function warn(msg) { console.log(`${COLORS.yellow}⚠${COLORS.reset} ${msg}`); }
function error(msg) { console.error(`${COLORS.red}✗${COLORS.reset} ${msg}`); }
function info(msg) { console.log(`${COLORS.cyan}ℹ${COLORS.reset} ${msg}`); }

function getTargetDir() {
  return path.join(process.cwd(), '.github');
}

function printUsage() {
  log(`
${COLORS.bold}pbi-agent-squad${COLORS.reset} — Install Power BI Agent Squad into your workspace

${COLORS.bold}Usage:${COLORS.reset}
  pbi-agent-squad install [options]       Install components
  pbi-agent-squad uninstall <ids...>      Uninstall components
  pbi-agent-squad list                    List available components
  pbi-agent-squad status                  Show installed components
  pbi-agent-squad update [options]        Update installed components

${COLORS.bold}Install options:${COLORS.reset}
  --all                    Install all components
  --agent <name>           Install a specific agent (with dependencies)
  --skill <name>           Install a specific skill
  --ref <name>             Install a specific reference
  --agents                 Install all agents (with dependencies)
  --skills                 Install all skills
  --refs                   Install all references
  --force                  Overwrite user-modified files

${COLORS.bold}Examples:${COLORS.reset}
  pbi-agent-squad install --all
  pbi-agent-squad install --agent pbi-report --agent pbi-qa
  pbi-agent-squad install --skill dax-development --skill svg-visuals
  pbi-agent-squad install --agents
  pbi-agent-squad list
  pbi-agent-squad list --type skill
  pbi-agent-squad status
  pbi-agent-squad uninstall skill:dax-development
  pbi-agent-squad update --all
`);
}

// ─── Commands ───────────────────────────────────────────────────────────────────

function cmdList(args) {
  const typeFilter = getArgValue(args, '--type');
  let components = COMPONENT_REGISTRY;
  if (typeFilter) {
    components = getComponentsByType(typeFilter);
  }

  const grouped = {};
  for (const c of components) {
    if (!grouped[c.type]) grouped[c.type] = [];
    grouped[c.type].push(c);
  }

  for (const [type, items] of Object.entries(grouped)) {
    log(`\n${COLORS.bold}${type.toUpperCase()}S${COLORS.reset} (${items.length})`);
    log('─'.repeat(60));
    for (const item of items) {
      const shortId = item.id.split(':')[1];
      log(`  ${COLORS.cyan}${shortId.padEnd(28)}${COLORS.reset} ${item.description}`);
    }
  }
  log('');
}

function cmdInstall(args) {
  const targetDir = getTargetDir();
  const lock = loadLockFile(targetDir);
  const force = args.includes('--force');
  let idsToInstall = [];

  if (args.includes('--all')) {
    idsToInstall = COMPONENT_REGISTRY.map(c => c.id);
  } else if (args.includes('--agents')) {
    const agentIds = getComponentsByType('agent').map(c => c.id);
    idsToInstall = resolveDependencies(agentIds);
  } else if (args.includes('--skills')) {
    idsToInstall = getComponentsByType('skill').map(c => c.id);
  } else if (args.includes('--refs')) {
    idsToInstall = getComponentsByType('reference').map(c => c.id);
  } else {
    // Collect --agent, --skill, --ref values
    const agents = getAllArgValues(args, '--agent');
    const skills = getAllArgValues(args, '--skill');
    const refs = getAllArgValues(args, '--ref');

    for (const name of agents) {
      const id = `agent:${name}`;
      if (!getComponentById(id)) { error(`Unknown agent: ${name}`); listSimilar('agent', name); return; }
      idsToInstall.push(id);
    }
    for (const name of skills) {
      const id = `skill:${name}`;
      if (!getComponentById(id)) { error(`Unknown skill: ${name}`); listSimilar('skill', name); return; }
      idsToInstall.push(id);
    }
    for (const name of refs) {
      const id = `ref:${name}`;
      if (!getComponentById(id)) { error(`Unknown reference: ${name}`); listSimilar('reference', name); return; }
      idsToInstall.push(id);
    }

    if (idsToInstall.length === 0) {
      error('No components specified. Use --all, --agents, --skills, or specify individual components.');
      log('  Run: pbi-agent-squad list');
      return;
    }

    // Resolve dependencies
    idsToInstall = resolveDependencies(idsToInstall);
  }

  info(`Installing ${idsToInstall.length} component(s) into ${targetDir}`);
  log('');

  let installed = 0, skipped = 0, failed = 0;

  for (const id of idsToInstall) {
    const comp = getComponentById(id);
    if (!comp) { warn(`Unknown component: ${id}`); continue; }
    try {
      const result = installComponent(comp, targetDir, lock, { force });
      if (result === 'skipped') {
        warn(`${comp.name} — skipped (user-modified, use --force to overwrite)`);
        skipped++;
      } else {
        success(`${comp.name}`);
        installed++;
      }
    } catch (err) {
      error(`${comp.name} — ${err.message}`);
      failed++;
    }
  }

  saveLockFile(targetDir, lock);
  log('');
  info(`Done: ${installed} installed, ${skipped} skipped, ${failed} failed`);
}

function cmdUninstall(args) {
  const ids = args.filter(a => !a.startsWith('-'));
  if (ids.length === 0) {
    error('Specify component IDs to uninstall. Example: pbi-agent-squad uninstall skill:dax-development');
    return;
  }

  const targetDir = getTargetDir();
  const lock = loadLockFile(targetDir);

  for (const id of ids) {
    const comp = getComponentById(id);
    if (!comp) { warn(`Unknown component: ${id}`); continue; }
    uninstallComponent(comp, targetDir, lock);
    success(`Uninstalled: ${comp.name}`);
  }

  saveLockFile(targetDir, lock);
}

function cmdStatus() {
  const targetDir = getTargetDir();
  const lock = loadLockFile(targetDir);
  const components = Object.values(lock.components);

  if (components.length === 0) {
    info('No components installed. Run: pbi-agent-squad install --all');
    return;
  }

  log(`\n${COLORS.bold}Installed Components${COLORS.reset} (${components.length})`);
  log('─'.repeat(60));
  for (const entry of components) {
    const status = entry.userModified
      ? `${COLORS.yellow}modified${COLORS.reset}`
      : `${COLORS.green}clean${COLORS.reset}`;
    const shortId = entry.id.split(':')[1];
    log(`  ${shortId.padEnd(28)} ${status}  ${COLORS.dim}v${entry.version}${COLORS.reset}`);
  }
  log(`\n  Lock file: ${path.join(targetDir, '.pbi-agent-squad.lock.json')}`);
  log('');
}

function cmdUpdate(args) {
  const targetDir = getTargetDir();
  const lock = loadLockFile(targetDir);
  const force = args.includes('--force');

  let idsToUpdate;
  if (args.includes('--all')) {
    idsToUpdate = Object.keys(lock.components);
  } else {
    idsToUpdate = args.filter(a => !a.startsWith('-'));
  }

  if (idsToUpdate.length === 0) {
    info('Nothing to update. Use --all or specify component IDs.');
    return;
  }

  info(`Updating ${idsToUpdate.length} component(s)...`);
  let updated = 0, skipped = 0;

  for (const id of idsToUpdate) {
    const comp = getComponentById(id);
    if (!comp) { warn(`Unknown: ${id}`); continue; }
    try {
      const result = installComponent(comp, targetDir, lock, { force });
      if (result === 'skipped') {
        warn(`${comp.name} — skipped (user-modified)`);
        skipped++;
      } else {
        success(`${comp.name} — updated`);
        updated++;
      }
    } catch (err) {
      error(`${comp.name} — ${err.message}`);
    }
  }

  saveLockFile(targetDir, lock);
  log('');
  info(`Done: ${updated} updated, ${skipped} skipped`);
}

// ─── Arg helpers ────────────────────────────────────────────────────────────────

function getArgValue(args, flag) {
  const idx = args.indexOf(flag);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : null;
}

function getAllArgValues(args, flag) {
  const values = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === flag && i + 1 < args.length) {
      values.push(args[++i]);
    }
  }
  return values;
}

function listSimilar(type, name) {
  const similar = getComponentsByType(type)
    .filter(c => c.id.includes(name) || c.name.toLowerCase().includes(name))
    .slice(0, 5);
  if (similar.length > 0) {
    log(`  Did you mean: ${similar.map(c => c.id.split(':')[1]).join(', ')}?`);
  }
}

// ─── Main ───────────────────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const cmdArgs = args.slice(1);

  switch (command) {
    case 'install':
      cmdInstall(cmdArgs);
      break;
    case 'uninstall':
    case 'remove':
      cmdUninstall(cmdArgs);
      break;
    case 'list':
    case 'ls':
      cmdList(cmdArgs);
      break;
    case 'status':
      cmdStatus();
      break;
    case 'update':
    case 'upgrade':
      cmdUpdate(cmdArgs);
      break;
    case '--help':
    case '-h':
    case undefined:
      printUsage();
      break;
    case '--version':
    case '-v':
      const pkg = require('../package.json');
      log(pkg.version);
      break;
    default:
      error(`Unknown command: ${command}`);
      printUsage();
      process.exit(1);
  }
}

main();
