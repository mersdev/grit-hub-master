#!/usr/bin/env node
/**
 * scripts/setup.js — Install GRIT Hub assets for Copilot
 *
 * Canonical locations:
 * - Workspace agents: .github/agents/*.agent.md
 * - User/global custom agents: ~/.copilot/agents/*.agent.md
 * - Global instructions + shared assets: ~/.copilot/
 *
 * Usage:
 *   node scripts/setup.js                    # full interactive setup
 *   node scripts/setup.js --all              # install everything non-interactively
 *   node scripts/setup.js --dry-run          # show what would be installed
 *   node scripts/setup.js --skip-python      # skip Python dependency install
 *   node scripts/setup.js --skip-cleanup     # skip the cleanup.js pass before --all
 *   node scripts/setup.js --memory           # install only memory system
 *   node scripts/setup.js --learning         # install only learning tracker
 *   node scripts/setup.js --skills           # install only skills
 *   node scripts/setup.js --role developer   # install only one role's project agents for IDE
 *   node scripts/setup.js --agent fullstack-engineer # install only one project agent for IDE
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');
const { execSync, spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const HOME = os.homedir();
const COPILOT_DIR = path.join(HOME, '.copilot');

const args = process.argv.slice(2);
const flags = new Set(args.filter(a => a.startsWith('--')).map(a => a.replace(/^--/, '')));
const dryRun = flags.has('dry-run');
const skipPython = flags.has('skip-python');
const skipCleanup = flags.has('skip-cleanup');
const allFlag = flags.has('all') || flags.has('everything');

function flagValue(name) {
  const prefix = `--${name}=`;
  const inline = args.find(a => a.startsWith(prefix));
  if (inline) return inline.slice(prefix.length).trim();
  const index = args.indexOf(`--${name}`);
  if (index >= 0 && args[index + 1] && !args[index + 1].startsWith('--')) return args[index + 1].trim();
  return '';
}

function slug(value) {
  return String(value || '').trim().toLowerCase().replace(/^@/, '').replace(/[_\s]+/g, '-');
}

const selectedRole = slug(flagValue('role'));
const selectedAgent = slug(flagValue('agent'));
const roleOrAgentInstall = Boolean(selectedRole || selectedAgent);

// ─── Helpers ───────────────────────────────────────────────────────────────
function ensureDir(p) {
  if (dryRun) { console.log(`  [dry-run] mkdir ${p}`); return; }
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function requirePath(p, label) {
  if (!fs.existsSync(p)) {
    throw new Error(`Missing ${label}: ${p}`);
  }
  return p;
}

function copyFile(src, dest) {
  if (dryRun) { console.log(`  [dry-run] copy ${src} -> ${dest}`); return; }
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
  console.log(`  ✓ ${path.relative(HOME, dest)}`);
}

function shouldCopySource(src) {
  const parts = src.split(path.sep);
  const base = path.basename(src);
  return !parts.includes('__pycache__')
    && !parts.includes('.pytest_cache')
    && !base.endsWith('.pyc')
    && base !== '.DS_Store';
}

function copyDir(srcDir, destDir, filter = () => true) {
  if (!fs.existsSync(srcDir)) return 0;
  let count = 0;
  const entries = fs.readdirSync(srcDir, { withFileTypes: true });
  for (const entry of entries) {
    const src = path.join(srcDir, entry.name);
    const dest = path.join(destDir, entry.name);
    if (!shouldCopySource(src)) continue;
    if (entry.isDirectory()) {
      count += copyDir(src, dest, filter);
    } else if (filter(entry.name)) {
      copyFile(src, dest);
      count++;
    }
  }
  return count;
}

function prompt(question) {
  return new Promise(resolve => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(question, ans => { rl.close(); resolve(ans.trim()); });
  });
}

// ─── Python Dependencies ────────────────────────────────────────────────────
function checkPython() {
  try {
    const version = execSync('python --version', { encoding: 'utf-8', stdio: 'pipe' });
    console.log(`\n📦 Python detected: ${version.trim()}`);
    return true;
  } catch (e) {
    console.log('\n⚠️  Python not found. Skipping dependency installation.');
    console.log('   Install Python 3.10+ then run: pip install python-pptx PyPDF2 python-dotenv pyyaml');
    return false;
  }
}

function installPythonDependencies() {
  if (dryRun) {
    console.log('\n📦 Installing Python Dependencies (--dry-run mode)');
    console.log('  [dry-run] pip install python-pptx PyPDF2 python-dotenv pyyaml');
    return;
  }

  if (!checkPython()) return;

  console.log('\n📦 Installing Python Dependencies...');
  const packages = ['python-pptx', 'PyPDF2', 'python-dotenv', 'pyyaml'];
  
  try {
    execSync(`pip install ${packages.join(' ')}`, { stdio: 'inherit' });
    console.log('  ✓ Python dependencies installed successfully');
  } catch (err) {
    console.log('  ⚠️  Failed to install Python dependencies.');
    console.log('   Try manually: pip install python-pptx PyPDF2 python-dotenv pyyaml');
  }
}

// ─── Install Functions ─────────────────────────────────────────────────────
function installSkills() {
  console.log('\n📦 Installing Skills...');
  const dest = path.join(COPILOT_DIR, 'skills');
  ensureDir(dest);
  const src = requirePath(path.join(ROOT, 'skills'), 'skills source directory');
  let count = 0;

  // Each skill is in a subfolder with SKILL.md
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      const skillFile = path.join(src, entry.name, 'SKILL.md');
      if (fs.existsSync(skillFile)) {
        copyFile(skillFile, path.join(dest, `${entry.name}.md`));
        count++;
      }
    }
  }
  return count;
}

function installInstructions() {
  console.log('\n📦 Installing Global Instructions...');
  let count = 0;

  // copilot-instructions.md
  const instrSrc = requirePath(
    path.join(ROOT, 'instructions', 'copilot-instructions.md'),
    'global Copilot instructions'
  );
  copyFile(instrSrc, path.join(COPILOT_DIR, 'copilot-instructions.md'));
  count++;

  ensureDir(path.join(COPILOT_DIR, 'agents'));

  return count;
}

function runCleanup() {
  console.log('\n🧹 Refreshing setup-managed files with scripts/cleanup.js...');
  const args = [path.join(__dirname, 'cleanup.js')];
  if (dryRun) args.push('--dry-run');

  const result = spawnSync('node', args, {
    cwd: ROOT,
    stdio: 'inherit',
    shell: false,
  });

  if (result.status !== 0) {
    throw new Error(`scripts/cleanup.js failed with exit code ${result.status || 1}`);
  }
}

// ─── Project-Level Installation (for IDE Copilot) ────────────────────────────
const CWD = process.cwd();
const GITHUB_DIR = path.join(CWD, '.github');

function installProjectAgents() {
  const label = selectedAgent
    ? `Project Agent: ${selectedAgent}`
    : selectedRole
      ? `Project Agents for role: ${selectedRole}`
      : 'Project Agents';
  console.log(`\n📦 Installing ${label} (.github/agents/)...`);
  const agentsRoot = requirePath(path.join(ROOT, 'agents'), 'agents source directory');
  
  const dest = path.join(GITHUB_DIR, 'agents');
  ensureDir(dest);
  let count = 0;
  
  // Copy agents from agents/<role>/<agent-name>/<agent-name>.agent.md
  for (const role of fs.readdirSync(agentsRoot, { withFileTypes: true })) {
    if (!role.isDirectory()) continue;
    if (selectedRole && slug(role.name) !== selectedRole) continue;
    const roleDir = path.join(agentsRoot, role.name);
    
    for (const agent of fs.readdirSync(roleDir, { withFileTypes: true })) {
      if (!agent.isDirectory()) continue;
      const agentSlug = slug(agent.name);
      const fullSlug = slug(`${role.name}-${agent.name}`);
      const roleSlashAgent = slug(`${role.name}/${agent.name}`);
      if (selectedAgent && ![agentSlug, fullSlug, roleSlashAgent].includes(selectedAgent)) continue;
      const agentFile = path.join(roleDir, agent.name, `${agent.name}.agent.md`);
      if (fs.existsSync(agentFile)) {
        const destFile = path.join(dest, `${role.name}-${agent.name}.agent.md`);
        copyFile(agentFile, destFile);
        count++;
      }
    }
  }

  if (roleOrAgentInstall && count === 0) {
    const hint = selectedAgent ? `agent "${selectedAgent}"` : `role "${selectedRole}"`;
    throw new Error(`No ${hint} found. Try: node scripts/setup.js --dry-run --all and check available agents.`);
  }

  return count;
}

function installProjectSkills() {
  console.log('\n📦 Installing Project Skills (.github/skills/)...');
  const skillsRoot = requirePath(path.join(ROOT, 'skills'), 'skills source directory');
  
  const dest = path.join(GITHUB_DIR, 'skills');
  
  // Just copy the entire skills folder as-is, no filtering
  return copyDir(skillsRoot, dest, () => true);
}

function installProjectInstructions() {
  console.log('\n📦 Installing Project Instructions (.github/instructions/)...');
  let count = 0;

  const src = path.join(ROOT, 'instructions');
  if (!fs.existsSync(src)) return 0;

  const dest = path.join(GITHUB_DIR, 'instructions');
  ensureDir(dest);
  count += copyDir(src, dest, () => true);
  return count;
}

// ─── Main ──────────────────────────────────────────────────────────────────
async function main() {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║   Copilot Agent Starter Kit — Global Setup                ║
╚═══════════════════════════════════════════════════════════╝
`);
  console.log(`  Home:     ${HOME}`);
  console.log(`  Target:   ${COPILOT_DIR}`);
  if (dryRun) console.log('  Mode:     DRY RUN (no files will be written)\n');

  const components = {
    skills: { fn: installSkills, desc: 'Skills Library' },
    instructions: { fn: installInstructions, desc: 'Global instructions' },
  };

  let toInstall = [];

  if (allFlag) {
    toInstall = Object.keys(components);
  } else {
    // Check specific flags
    const specific = Object.keys(components).filter(k => flags.has(k));
    if (specific.length > 0) {
      toInstall = specific;
    } else if (roleOrAgentInstall) {
      // Pulling a role/agent should be simple: enough project assets for IDE use, no full global install required.
      toInstall = ['skills', 'instructions'];
    } else if (dryRun) {
      // Dry runs should preview the full install plan instead of prompting.
      toInstall = Object.keys(components);
    } else {
      // Interactive
      console.log('  Select components to install:\n');
      for (const [key, { desc }] of Object.entries(components)) {
        const ans = await prompt(`  Install ${desc}? [Y/n] `);
        if (ans.toLowerCase() !== 'n') toInstall.push(key);
      }
    }
  }

  if (toInstall.length === 0) {
    console.log('\n  Nothing selected. Exiting.');
    return;
  }

  if (allFlag && !skipCleanup) {
    runCleanup();
  }

  console.log(`\n  Installing ${toInstall.length} component(s)...`);
  ensureDir(COPILOT_DIR);

  let totalFiles = 0;
  for (const key of toInstall) {
    totalFiles += components[key].fn();
  }

  console.log(`\n${'═'.repeat(55)}`);
  console.log(`  ✅ Global setup complete! ${totalFiles} file(s) installed to ~/.copilot/`);
  console.log(`${'═'.repeat(55)}`);
  console.log('  User-level custom agents belong in ~/.copilot/agents/*.agent.md');
  
  // Install project-level components for IDE Copilot
  if (toInstall.includes('skills') || allFlag || roleOrAgentInstall) {
    console.log(`\n${'═'.repeat(55)}`);
    console.log(`  Installing project-level components to .github/ (for IDE)`);
    console.log(`${'═'.repeat(55)}`);
    
    let projectFiles = 0;
    projectFiles += installProjectAgents();
    projectFiles += installProjectSkills();
    projectFiles += installProjectInstructions();
    
    console.log(`\n${'═'.repeat(55)}`);
    console.log(`  ✅ Project setup complete! ${projectFiles} file(s) installed to .github/`);
    console.log(`${'═'.repeat(55)}`);
    
    totalFiles += projectFiles;
  }
  
  // Install Python dependencies
  if (!skipPython && toInstall.length > 0) {
    installPythonDependencies();
  }
  
  console.log(`
  Next steps:

  GitHub Copilot CLI:
    1. Install and sign in to Copilot CLI
    2. From this repo, run: copilot
    3. Start with: I want an AI helper for my team. Ask me simple questions and recommend whether to reuse, improve, or create an agent.

  VS Code / IDE Copilot:
    1. Reload IDE: Ctrl+Shift+P → "Developer: Reload Window"
    2. Open Copilot Chat
    3. Start with the same Development Coach prompt
    4. To pull only one role next time: node scripts/setup.js --role developer --skip-python
    5. To pull only one agent: node scripts/setup.js --agent fullstack-engineer --skip-python

  Discovery:
    - Workspace agents: .github/agents/*.agent.md
    - User/global custom agents: ~/.copilot/agents/*.agent.md

  Docs: see README.md and ONBOARDING.md.
`);
}

main().catch(err => { console.error(err); process.exit(1); });
