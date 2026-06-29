#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const HOME = os.homedir();
const COPILOT_DIR = path.join(HOME, ".copilot");
const TARGETS = [
  path.join(COPILOT_DIR, "memory"),
  path.join(COPILOT_DIR, "learning"),
];

const dryRun = process.argv.includes("--dry-run");

function exists(target) {
  return fs.existsSync(target);
}

function removePath(target) {
  if (!exists(target)) return false;

  const stat = fs.statSync(target);
  if (dryRun) {
    console.log(`[dry-run] remove ${stat.isDirectory() ? "dir" : "file"} ${target}`);
    return true;
  }

  if (stat.isDirectory()) {
    fs.rmSync(target, { recursive: true, force: true });
    console.log(`removed dir ${target}`);
  } else {
    fs.unlinkSync(target);
    console.log(`removed file ${target}`);
  }

  return true;
}

function cleanupEmptyParents(startDir, stopDir) {
  let current = startDir;
  const stop = path.resolve(stopDir);

  while (path.resolve(current).startsWith(stop) && path.resolve(current) !== stop) {
    if (!exists(current) || !fs.statSync(current).isDirectory()) break;
    if (fs.readdirSync(current).length !== 0) break;

    if (dryRun) {
      console.log(`[dry-run] remove empty dir ${current}`);
    } else {
      fs.rmdirSync(current);
      console.log(`removed empty dir ${current}`);
    }

    current = path.dirname(current);
  }
}

function main() {
  let removed = 0;

  for (const target of TARGETS) {
    if (removePath(target)) {
      removed += 1;
      cleanupEmptyParents(path.dirname(target), COPILOT_DIR);
    }
  }

  console.log(
    dryRun
      ? `Dry run complete. ${removed} Copilot memory item(s) would be removed.`
      : `Cleanup complete. ${removed} Copilot memory item(s) removed.`
  );
}

main();
