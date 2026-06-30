#!/usr/bin/env node
/**
 * setup.js — Global user-profile setup for Copilot Agent Starter Kit
 *
 * Installs memory system, learning tracker, skills, MCP config, and
 * global agent instructions into the user's ~/.copilot/ directory.
 * Also installs required Python dependencies.
 *
 * Usage:
 *   node setup.js                    # full interactive setup
 *   node setup.js --all              # install everything non-interactively
 *   node setup.js --dry-run          # show what would be installed
 *   node setup.js --skip-python      # skip Python dependency install
 *   node setup.js --skip-cleanup     # skip the cleanup.js pass before --all
 *   node setup.js --memory           # install only memory system
 *   node setup.js --learning         # install only learning tracker
 *   node setup.js --skills           # install only skills
 *   node setup.js --mcp             # install only MCP config
 *   node setup.js --pptx            # install only PPTX agent
 *   node setup.js --role developer  # install only one role's project agents for IDE
 *   node setup.js --agent fullstack-engineer # install only one project agent for IDE
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const readline = require('readline');
const { execSync, spawnSync } = require('child_process');

const ROOT = __dirname;
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
function installMemory() {
  console.log('\n📦 Installing Memory System...');
  const dest = path.join(COPILOT_DIR, 'memory');
  ensureDir(dest);
  const src = path.join(ROOT, 'memory');
  return copyDir(src, dest, () => true);
}

function installLearning() {
  console.log('\n📦 Installing Learning Tracker...');
  const dest = path.join(COPILOT_DIR, 'learning');
  ensureDir(dest);
  const src = path.join(ROOT, 'learning');
  return copyDir(src, dest, () => true);
}

function installSkills() {
  console.log('\n📦 Installing Skills...');
  const dest = path.join(COPILOT_DIR, 'skills');
  ensureDir(dest);
  const src = path.join(ROOT, 'skills');
  let count = 0;

  // Each skill is in a subfolder with SKILL.md
  if (!fs.existsSync(src)) return 0;
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

function installMcp() {
  console.log('\n📦 Installing MCP Configuration...');
  const src = path.join(ROOT, 'mcp', 'mcp.json');
  const dest = path.join(COPILOT_DIR, 'mcp.json');
  if (fs.existsSync(src)) {
    copyFile(src, dest);
    return 1;
  }
  return 0;
}

function installPptx() {
  console.log('\n📦 Installing PPTX Agent...');
  const dest = path.join(COPILOT_DIR, 'pptx');
  ensureDir(dest);
  const src = path.join(ROOT, 'skills', 'pptx-agent', 'scripts');
  if (fs.existsSync(src)) {
    return copyDir(src, dest, () => true);
  }
  return 0;
}

function installInstructions() {
  console.log('\n📦 Installing Global Instructions...');
  let count = 0;

  // copilot-instructions.md
  const instrSrc = path.join(ROOT, 'instructions', 'copilot-instructions.md');
  if (fs.existsSync(instrSrc)) {
    copyFile(instrSrc, path.join(COPILOT_DIR, 'copilot-instructions.md'));
    count++;
  }

  // AGENTS.md
  const agentsSrc = path.join(ROOT, 'instructions', 'AGENTS.md');
  if (fs.existsSync(agentsSrc)) {
    copyFile(agentsSrc, path.join(HOME, 'AGENTS.md'));
    count++;
  }

  return count;
}

function installBoot() {
  console.log('\n📦 Installing Boot Script...');
  const src = path.join(ROOT, 'scripts', 'boot.py');
  if (fs.existsSync(src)) {
    copyFile(src, path.join(COPILOT_DIR, 'agent_boot.py'));
    return 1;
  }
  return 0;
}

function runCleanup() {
  console.log('\n🧹 Refreshing setup-managed files with cleanup.js...');
  const args = ['cleanup.js'];
  if (dryRun) args.push('--dry-run');

  const result = spawnSync('node', args, {
    cwd: ROOT,
    stdio: 'inherit',
    shell: false,
  });

  if (result.status !== 0) {
    throw new Error(`cleanup.js failed with exit code ${result.status || 1}`);
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
  const agentsRoot = path.join(ROOT, 'agents');
  if (!fs.existsSync(agentsRoot)) return 0;
  
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
    throw new Error(`No ${hint} found. Try: node setup.js --dry-run --all and check available agents.`);
  }

  return count;
}

function installProjectSkills() {
  console.log('\n📦 Installing Project Skills (.github/skills/)...');
  const skillsRoot = path.join(ROOT, 'skills');
  if (!fs.existsSync(skillsRoot)) return 0;
  
  const dest = path.join(GITHUB_DIR, 'skills');
  
  // Just copy the entire skills folder as-is, no filtering
  return copyDir(skillsRoot, dest, () => true);
}

function installProjectScripts() {
  // This function is now deprecated - scripts are installed with installProjectSkills()
  // Keeping it for backward compatibility but it does nothing
  return 0;
}

function installProjectComponents() {
  console.log('\n📦 Installing Project Components (.github/)...');
  const components = ['security', 'instructions', 'prompts', 'chatmodes', 'memory'];
  let count = 0;
  
  for (const comp of components) {
    const src = path.join(ROOT, comp);
    if (!fs.existsSync(src)) continue;
    
    const dest = path.join(GITHUB_DIR, comp);
    ensureDir(dest);
    
    // Copy all files (no filtering)
    count += copyDir(src, dest, () => true);
  }
  return count;
}

function generateAgentCatalog() {
  if (dryRun) {
    console.log('\n📦 Generating Agent Catalog (.github/agent-catalog.json)...');
    console.log('  [dry-run] node agents/ai-engineer/generate-agent-catalog.js');
    return;
  }

  console.log('\n📦 Generating Agent Catalog (.github/agent-catalog.json)...');
  const result = spawnSync('node', ['agents/ai-engineer/generate-agent-catalog.js'], {
    cwd: ROOT,
    stdio: 'inherit',
    shell: false,
  });

  if (result.status !== 0) {
    throw new Error(`agent catalog generation failed with exit code ${result.status || 1}`);
  }
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
    memory: { fn: installMemory, desc: 'Memory System (SQLite + PageIndex)' },
    learning: { fn: installLearning, desc: 'Learning Tracker (5-level progression)' },
    skills: { fn: installSkills, desc: 'Skills Library (memory-recall, code-review, pptx-agent, drawio, etc.)' },
    mcp: { fn: installMcp, desc: 'MCP Servers (filesystem, memory, fetch, thinking, drawio)' },
    pptx: { fn: installPptx, desc: 'PPTX Agent (DHL-branded presentations)' },
    instructions: { fn: installInstructions, desc: 'Global Instructions (copilot-instructions.md + AGENTS.md)' },
    boot: { fn: installBoot, desc: 'Boot Script (auto-init on session start)' },
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
  
  // Install project-level components for IDE Copilot
  if (toInstall.includes('skills') || toInstall.includes('memory') || allFlag || roleOrAgentInstall) {
    console.log(`\n${'═'.repeat(55)}`);
    console.log(`  Installing project-level components to .github/ (for IDE)`);
    console.log(`${'═'.repeat(55)}`);
    
    let projectFiles = 0;
    projectFiles += installProjectAgents();
    projectFiles += installProjectSkills();
    projectFiles += installProjectScripts();
    projectFiles += installProjectComponents();
    generateAgentCatalog();
    
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
    1. Install: winget install GitHub.Copilot
    2. Run: copilot
    3. Login: /login
    4. Initialize: Init & wire my new Agent <Name> and Implement Learning Path, Memory System, Skills System, MCP Integration, Personality & Soul.md into copilot from https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub
    
  Daily use:
    1. copilot
    2. init agent <Your-Name>
    3. Use natural language prompts
  
  VS Code / IDE Copilot:
    1. Reload IDE: Ctrl+Shift+P → "Developer: Reload Window"
    2. Open Copilot Chat (Ctrl+I)
    3. Ask: "What agents are available?"
    4. To pull only one role next time: node setup.js --role developer --skip-python
    5. To pull only one agent: node setup.js --agent fullstack-engineer --skip-python
    6. Memory for VS Code agents is stored in .github/memory/

  Memory storage:
    - VS Code / IDE Copilot: .github/memory/ in this project
    - Copilot CLI: ~/.copilot/memory/ in your user profile

  Docs: see README.md or ONBOARDING.md for full usage guide.
`);
}

main().catch(err => { console.error(err); process.exit(1); });
