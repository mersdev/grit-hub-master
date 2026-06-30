#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { AGENTS_ROOT, REPO_ROOT } = require(path.join(__dirname, "..", "agents", "ai-engineer", "lib", "agent-routing"));

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const target = args.find((arg) => !arg.startsWith("--"));

function usage() {
  console.error(
    "Usage: node scripts/remove-agent.js <agent-slug|role/agent-name|path/to/agent.agent.md> [--dry-run]"
  );
}

function exists(p) {
  return fs.existsSync(p);
}

function walkAgentFiles(dir, acc = []) {
  if (!exists(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkAgentFiles(full, acc);
    } else if (entry.name.endsWith(".agent.md")) {
      acc.push(full);
    }
  }
  return acc;
}

function walkMirrorFiles(dir, acc = []) {
  if (!exists(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkMirrorFiles(full, acc);
    } else if (entry.name.endsWith(".agent.md")) {
      acc.push(full);
    }
  }
  return acc;
}

function cleanupEmptyParents(startDir, stopDir) {
  let current = path.resolve(startDir);
  const stop = path.resolve(stopDir);

  while (current.startsWith(stop) && current !== stop) {
    if (!exists(current) || fs.readdirSync(current).length > 0) {
      break;
    }

    if (dryRun) {
      console.log(`[dry-run] remove empty dir ${current}`);
    } else {
      fs.rmdirSync(current);
      console.log(`removed empty dir ${current}`);
    }

    current = path.dirname(current);
  }
}

function removeFile(filePath) {
  if (!exists(filePath)) return false;
  if (dryRun) {
    console.log(`[dry-run] remove file ${filePath}`);
    return true;
  }
  fs.unlinkSync(filePath);
  console.log(`removed file ${filePath}`);
  return true;
}

function resolveSourceAgent(input) {
  const normalized = input.replace(/[\\/]+/g, path.sep);
  const directCandidates = [];

  if (normalized.endsWith(".agent.md")) {
    directCandidates.push(path.resolve(REPO_ROOT, normalized));
    directCandidates.push(path.resolve(AGENTS_ROOT, normalized));
  } else {
    const baseName = `${path.basename(normalized)}.agent.md`;
    directCandidates.push(path.join(AGENTS_ROOT, normalized, baseName));
    directCandidates.push(path.join(REPO_ROOT, normalized, baseName));
    directCandidates.push(path.join(AGENTS_ROOT, baseName));
  }

  for (const candidate of directCandidates) {
    if (exists(candidate)) return candidate;
  }

  const baseName = normalized.endsWith(".agent.md")
    ? path.basename(normalized)
    : `${path.basename(normalized)}.agent.md`;
  const matches = walkAgentFiles(AGENTS_ROOT).filter((file) => path.basename(file) === baseName);

  if (matches.length === 1) return matches[0];
  if (matches.length > 1) {
    console.error(`Multiple agents match "${input}". Please use a more specific path:`);
    for (const match of matches) {
      console.error(`- ${path.relative(REPO_ROOT, match).replaceAll("\\", "/")}`);
    }
    process.exit(1);
  }

  return null;
}

function resolveMirrorAgent(input) {
  const normalized = input.replace(/[\\/]+/g, path.sep);
  const segments = normalized.split(path.sep).filter(Boolean);
  const mirrorRoot = path.join(REPO_ROOT, ".github", "agents");

  const agentsIndex = segments.lastIndexOf("agents");
  if (normalized.endsWith(".agent.md") && agentsIndex >= 0 && segments.length >= agentsIndex + 4) {
    const role = segments[agentsIndex + 1];
    const slug = segments[agentsIndex + 2];
    const mirrorPath = path.join(mirrorRoot, `${role}-${slug}.agent.md`);
    if (exists(mirrorPath)) {
      return { mirrorPath, role, slug };
    }
    return { mirrorPath, role, slug };
  }

  const baseName = normalized.endsWith(".agent.md")
    ? path.basename(normalized)
    : `${path.basename(normalized)}.agent.md`;

  if (normalized.includes(path.sep)) {
    const pathMatches = walkMirrorFiles(mirrorRoot).filter((file) => path.basename(file) === baseName);
    if (pathMatches.length === 1) {
      const mirrorPath = pathMatches[0];
      const mirrorBase = path.basename(mirrorPath, ".agent.md");
      const hyphen = mirrorBase.indexOf("-");
      if (hyphen > 0) {
        return {
          mirrorPath,
          role: mirrorBase.slice(0, hyphen),
          slug: mirrorBase.slice(hyphen + 1),
        };
      }
    }
    return null;
  }

  const slug = baseName.replace(/\.agent\.md$/, "");
  const suffix = `-${slug}.agent.md`;
  const matches = walkMirrorFiles(mirrorRoot).filter((file) => file.endsWith(suffix));

  if (matches.length === 1) {
    const mirrorPath = matches[0];
    const mirrorBase = path.basename(mirrorPath, ".agent.md");
    const hyphen = mirrorBase.indexOf("-");
    return {
      mirrorPath,
      role: mirrorBase.slice(0, hyphen),
      slug,
    };
  }

  if (matches.length > 1) {
    console.error(`Multiple generated mirrors match "${input}". Please use a more specific path:`);
    for (const match of matches) {
      console.error(`- ${path.relative(REPO_ROOT, match).replaceAll("\\", "/")}`);
    }
    process.exit(1);
  }

  return null;
}

function main() {
  if (!target) {
    usage();
    process.exit(1);
  }

  const sourcePath = resolveSourceAgent(target);
  const mirrorInfo = resolveMirrorAgent(target);

  if (!sourcePath && !mirrorInfo) {
    console.error(`Could not find an agent for "${target}".`);
    usage();
    process.exit(1);
  }

  let role = null;
  let slug = null;
  if (sourcePath) {
    const relativeSource = path.relative(REPO_ROOT, sourcePath).replaceAll("\\", "/");
    const parts = relativeSource.split("/");
    if (parts.length < 4 || parts[0] !== "agents") {
      console.error(`Resolved path is not a generated agent file: ${relativeSource}`);
      process.exit(1);
    }
    role = parts[1];
    slug = parts[2];
  } else {
    role = mirrorInfo.role;
    slug = mirrorInfo.slug;
  }

  const mirrorPath = mirrorInfo?.mirrorPath || path.join(REPO_ROOT, ".github", "agents", `${role}-${slug}.agent.md`);

  console.log(`Removing agent: ${sourcePath ? path.relative(REPO_ROOT, sourcePath).replaceAll("\\", "/") : path.relative(REPO_ROOT, mirrorPath).replaceAll("\\", "/")}`);
  if (exists(mirrorPath)) {
    console.log(`Removing mirrored copy: ${path.relative(REPO_ROOT, mirrorPath).replaceAll("\\", "/")}`);
  }

  let removed = 0;
  if (sourcePath && removeFile(sourcePath)) removed += 1;
  if (removeFile(mirrorPath)) removed += 1;

  if (sourcePath) {
    cleanupEmptyParents(path.dirname(sourcePath), AGENTS_ROOT);
  }
  cleanupEmptyParents(path.dirname(mirrorPath), path.join(REPO_ROOT, ".github"));

  console.log(
    dryRun
      ? `Dry run complete. ${removed} file(s) would be removed.`
      : `Cleanup complete. ${removed} file(s) removed.`
  );
}

main();
