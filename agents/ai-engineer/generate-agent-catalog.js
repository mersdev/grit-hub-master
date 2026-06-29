#!/usr/bin/env node
const fs = require("fs");
const { CATALOG_PATH, loadCatalog, writeCatalog } = require("./lib/agent-routing");
const { skillScopeWarning } = require("./lib/skill-scoping");

const checkOnly = process.argv.includes("--check");

function agentNameWarnings(catalog) {
  return catalog.agents
    .filter((agent) => agent.raw_name && agent.name !== agent.raw_name)
    .map((agent) => ({
      message: `Normalized agent name for ${agent.path}: "${agent.raw_name}" -> "${agent.name}"`,
    }));
}

function main() {
  const catalog = loadCatalog();
  const next = `${JSON.stringify(catalog, null, 2)}\n`;
  const warnings = [
    ...agentNameWarnings(catalog),
    ...catalog.agents
    .map(skillScopeWarning)
    .filter(Boolean),
  ];

  if (checkOnly) {
    if (!fs.existsSync(CATALOG_PATH)) {
      console.error("Agent catalog is missing. Run without --check to generate it.");
      process.exit(1);
    }

    const current = fs.readFileSync(CATALOG_PATH, "utf8");
    if (current !== next) {
      console.error("Agent catalog is out of date. Regenerate with:");
      console.error("  node agents/ai-engineer/generate-agent-catalog.js");
      process.exit(1);
    }

    for (const warning of warnings) {
      console.warn(`Warning: ${warning.message}`);
    }

    console.log(`Agent catalog is current: ${CATALOG_PATH}`);
    return;
  }

  const written = writeCatalog(catalog);
  console.log(`Wrote agent catalog to ${written}`);
  console.log(`Agents: ${catalog.agents.length}, skills: ${catalog.skills.length}`);
  for (const warning of warnings) {
    console.warn(`Warning: ${warning.message}`);
  }
}

main();
