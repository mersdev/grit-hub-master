const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "../../..");
const AGENTS_ROOT = path.join(REPO_ROOT, "agents");
const SKILLS_ROOT = path.join(REPO_ROOT, "skills");

function exists(p) {
  return fs.existsSync(p);
}

function walkDirs(dir, acc = []) {
  if (!exists(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) acc.push(full);
  }
  return acc;
}

function normalize(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function tokenize(text) {
  return [...new Set(normalize(text).split(/\s+/).filter(Boolean))];
}

function titleCase(text) {
  return String(text || "")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function escapeRegExp(text) {
  return String(text || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function roleLabel(role) {
  const raw = String(role || "").trim().toLowerCase();
  const special = {
    "ai-engineer": "AI Engineer",
    "project-manager": "Project Manager",
    "quality-assurance": "Quality Assurance",
    "team-manager": "Team Manager",
    "everyone": "Everyone",
  };
  if (special[raw]) return special[raw];
  const normalized = titleCase(String(role || "").replace(/[-_]+/g, " "));
  return normalized || "Everyone";
}

function agentDisplayName(name, slug, role) {
  const fallback = titleCase(String(slug || "").replace(/[-_]+/g, " "));
  const raw = String(name || "").trim();
  if (!raw) return fallback;

  const roleName = roleLabel(role);
  const rolePrefix = new RegExp(`^${escapeRegExp(roleName)}\\s*(?:—|--|-)?\\s*`, "i");

  let display = raw.replace(rolePrefix, "").trim();
  if (!display) display = raw;

  const dashedParts = display
    .split(/\s+(?:—|--|-)\s+/)
    .map((part) => part.trim())
    .filter(Boolean);

  if (dashedParts.length > 1) {
    display = dashedParts[dashedParts.length - 1];
  }

  display = display.replace(rolePrefix, "").trim();
  return display || fallback;
}

function canonicalAgentName(role, name, slug) {
  return `${roleLabel(role)} — ${agentDisplayName(name, slug, role)}`;
}

const CREATE_STOP_WORDS = new Set([
  "create",
  "make",
  "build",
  "new",
  "design",
  "generate",
  "agent",
  "help",
  "need",
  "want",
  "please",
  "the",
  "a",
  "an",
  "for",
  "to",
  "of",
  "on",
  "with",
  "me",
  "this",
  "that",
  "one",
]);

function signalTokens(query) {
  return tokenize(query).filter((token) => !CREATE_STOP_WORDS.has(token));
}

function agentTokenHitCount(agent, tokens) {
  if (!tokens.length) return 0;
  const fields = [
    agent.name,
    agent.slug,
    agent.role,
    agent.description,
    ...(agent.keywords || []),
    ...(agent.match_examples || []),
    ...(agent.capabilities || []),
    ...(agent.skills || []),
  ]
    .map(normalize)
    .join(" ");

  let count = 0;
  for (const token of tokens) {
    if (fields.includes(token)) count += 1;
  }
  return count;
}

function parseScalar(raw) {
  const value = raw.trim();
  if (!value) return "";
  if (value === "true") return true;
  if (value === "false") return false;
  if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
  if ((value.startsWith("[") && value.endsWith("]")) || (value.startsWith("{") && value.endsWith("}"))) {
    try {
      return JSON.parse(value.replace(/'/g, '"'));
    } catch {
      return value;
    }
  }
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function parseFrontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!match) return {};

  const lines = match[1].split(/\r?\n/);
  const data = {};
  let currentKey = null;
  let currentType = null;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line || line.startsWith("#")) continue;

    const arrayMatch = line.match(/^\s*-\s+(.*)$/);
    if (arrayMatch && currentKey && currentType === "array") {
      data[currentKey].push(parseScalar(arrayMatch[1]));
      continue;
    }

    const kvMatch = line.match(/^([A-Za-z0-9_-]+):(?:\s*(.*))?$/);
    if (kvMatch) {
      const [, key, rawValue = ""] = kvMatch;
      if (rawValue.trim() === "") {
        data[key] = [];
        currentKey = key;
        currentType = "array";
      } else {
        data[key] = parseScalar(rawValue);
        currentKey = null;
        currentType = null;
      }
    }
  }

  return data;
}

function readMarkdownFile(filePath) {
  const text = fs.readFileSync(filePath, "utf8");
  const frontmatter = parseFrontmatter(text);
  const body = text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "");
  return { frontmatter, body, text };
}

function collectGeneratedAgentFiles() {
  const agents = [];

  for (const roleDir of walkDirs(AGENTS_ROOT)) {
    const role = path.basename(roleDir);
    for (const agentDir of walkDirs(roleDir)) {
      const slug = path.basename(agentDir);
      const agentFile = path.join(agentDir, `${slug}.agent.md`);
      if (!exists(agentFile)) continue;

      const { frontmatter, body } = readMarkdownFile(agentFile);
      agents.push({
        role,
        slug,
        path: path.relative(REPO_ROOT, agentFile).replaceAll("\\", "/"),
        name: canonicalAgentName(role, frontmatter.name || slug, slug),
        raw_name: frontmatter.name || slug,
        description: frontmatter.description || "",
        version: frontmatter.version || "",
        applies_to: Array.isArray(frontmatter.applies_to)
          ? frontmatter.applies_to
          : frontmatter.applies_to
            ? [frontmatter.applies_to]
            : [],
        tools: Array.isArray(frontmatter.tools) ? frontmatter.tools : [],
        skills: Array.isArray(frontmatter.skills) ? frontmatter.skills : [],
        keywords: Array.isArray(frontmatter.keywords) ? frontmatter.keywords : [],
        match_examples: Array.isArray(frontmatter.match_examples) ? frontmatter.match_examples : [],
        capabilities: Array.isArray(frontmatter.capabilities) ? frontmatter.capabilities : [],
        routing_priority: frontmatter.routing_priority || "normal",
        buildable: Boolean(frontmatter.buildable),
        body,
      });
    }
  }

  return agents;
}

function collectSkills() {
  const skills = [];
  if (!exists(SKILLS_ROOT)) return skills;

  for (const skillDir of walkDirs(SKILLS_ROOT)) {
    const slug = path.basename(skillDir);
    const skillFile = path.join(skillDir, "SKILL.md");
    if (!exists(skillFile)) continue;

    const { frontmatter, body } = readMarkdownFile(skillFile);
    skills.push({
      slug,
      path: path.relative(REPO_ROOT, skillFile).replaceAll("\\", "/"),
      name: frontmatter.name || slug,
      version: frontmatter.version || "",
      description: frontmatter.description || "",
      category: frontmatter.metadata?.category || frontmatter.category || "",
      tags: Array.isArray(frontmatter.metadata?.tags) ? frontmatter.metadata.tags : [],
      body,
    });
  }

  return skills;
}

function scoreText(query, candidate) {
  const q = normalize(query);
  const c = normalize(candidate);
  if (!q || !c) return 0;
  if (c === q) return 40;
  if (c.includes(q)) return 30;

  const qTokens = tokenize(query);
  const cTokens = new Set(tokenize(candidate));
  let score = 0;
  for (const token of qTokens) {
    if (cTokens.has(token)) score += 4;
  }
  return score;
}

function isCreateIntent(query) {
  return /\b(create|make|build|new|design|generate)\b/i.test(String(query || ""));
}

function rankAgents(query, agents, options = {}) {
  const intent = normalize(options.intent || query);
  const qTokens = tokenize(query);

  return agents
    .filter((agent) => (options.onlyBuildable ? agent.buildable : true))
    .map((agent) => {
      let score = 0;
      score += scoreText(query, agent.name) * 2;
      score += scoreText(query, agent.slug) * 2;
      score += scoreText(query, agent.description);
      score += scoreText(query, agent.role);
      score += agent.keywords.reduce((sum, value) => sum + scoreText(query, value), 0);
      score += agent.match_examples.reduce((sum, value) => sum + scoreText(query, value) * 0.7, 0);
      score += agent.capabilities.reduce((sum, value) => sum + scoreText(query, value) * 0.8, 0);
      score += agent.skills.reduce((sum, value) => sum + scoreText(query, value) * 0.8, 0);

      if (normalize(agent.name).includes(intent) || normalize(agent.description).includes(intent)) {
        score += 15;
      }

      for (const token of qTokens) {
        if (normalize(agent.name).includes(token)) score += 3;
        if (normalize(agent.description).includes(token)) score += 2;
        if (agent.keywords.some((value) => normalize(value).includes(token))) score += 4;
      }

      return { agent, score };
    })
    .sort((a, b) => b.score - a.score || a.agent.name.localeCompare(b.agent.name));
}

function findBestAgent(query, agents, options = {}) {
  const ranked = rankAgents(query, agents, options);
  return ranked.length > 0 ? ranked[0] : null;
}

module.exports = {
  AGENTS_ROOT,
  REPO_ROOT,
  SKILLS_ROOT,
  canonicalAgentName,
  collectGeneratedAgentFiles,
  collectSkills,
  findBestAgent,
  normalize,
  rankAgents,
  tokenize,
};
