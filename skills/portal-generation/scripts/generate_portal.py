#!/usr/bin/env python3
"""GRIT Hub Portal Generator - Glass Edition (v2)

Keeps the original scanning/parsing/contributor logic, but instead of building
HTML/CSS/JS inline it injects the discovered data into the canonical glass
template (templates/portal.glass.html). All styling lives in the template.

The activity panel is ranked by REAL data you already have: how many agents
declare each skill (usage_count). It is not faked runtime telemetry. When you
later add an invocation store, swap build_activity() to read from it.
"""
import os, sys, json, yaml, re, shutil, subprocess
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

# ---- config keys (supports both portal-config.json and portal_config.json) --
SCRIPT_DIR  = Path(__file__).resolve().parent
TEMPLATE    = SCRIPT_DIR / "templates" / "portal.glass.html"
CONFIG_PATHS = [
    SCRIPT_DIR / "portal-config.json",
    SCRIPT_DIR / "portal_config.json",
]
PLACEHOLDER = re.compile(r"/\*__PORTAL_DATA__\*/.*?/\*__END_PORTAL_DATA__\*/", re.S)

# role -> accent colour. Known roles get brand-aligned hues; unknowns cycle a palette.
ROLE_COLORS = {
    "Developer": "#FF2A3B", "Manager": "#F5B800", "Tester": "#34e36b",
    "Ai Engineer": "#9b7bff", "AI Engineer": "#9b7bff",
    "Everyone": "#FFD21E", "Data": "#37a6ff", "Architect": "#ff8a3d",
    "General": "#8a93a6",
}
PALETTE = ["#FF2A3B", "#F5B800", "#34e36b", "#9b7bff", "#37a6ff", "#ff8a3d", "#27c4c4", "#e85b9a"]
ROLE_EMOJI = {
    "Developer": "🧩", "Manager": "📋", "Tester": "✅", "AI Engineer": "🧠",
    "Ai Engineer": "🧠", "Everyone": "🌐", "Data": "🗄️", "Architect": "🏛️",
}


class PortalGenerator:
    def __init__(self, repo_root: str, output_dir: str, git_metadata: str | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.cfg = self._load_config()
        self.base_url = self.cfg.get(
            "github_base_url",
            "https://dhl.ghe.com/SMP-Mobile-Customer-Data-Domai/grit-hub/blob/master",
        )
        self.data = {"agents": [], "skills": [], "stats": {}, "generated_at": datetime.now().isoformat()}
        self._contributor_items_map = {}
        self._git_meta = self._load_git_metadata(git_metadata)   # NEW

    def _load_git_metadata(self, path):
        if not path:
            return None
        p = Path(path)
        if not p.exists():
            print(f"⚠️  git metadata not found: {p} (falling back to live git)", flush=True)
            return None
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            print(f"   ✅ Git metadata: {len(meta.get('contributors', []))} contributors, "
                  f"{len(meta.get('files', {}))} files")
            return meta
        except json.JSONDecodeError as e:
            print(f"⚠️  git metadata invalid: {e}", flush=True)
            return None

    @staticmethod
    def _relkey(filepath, repo_root):
        return str(Path(filepath).resolve().relative_to(repo_root)).replace(chr(92), "/")

    # ---------------------------------------------------------------- config
    def _load_config(self) -> dict:
        for config_path in CONFIG_PATHS:
            if not config_path.exists():
                continue
            try:
                return json.loads(config_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                print(f"⚠️  {config_path.name} invalid: {e}")
                break
        return {}

    # ---------------------------------------------------------------- git
    def _get_last_commit_date(self, filepath: Path) -> str:
        if self._git_meta:                                              # NEW
            info = self._git_meta["files"].get(self._relkey(filepath, self.repo_root))
            if info and info.get("last_date"):
                return info["last_date"]
        try:                                                            # ── existing fallback below ──
            rel = filepath.relative_to(self.repo_root)
            r = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=short", str(rel)],
                               cwd=self.repo_root, capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
            print(f"   ⚠️  git log failed for {filepath}: rc={r.returncode} stderr={r.stderr.strip()!r}", flush=True)
        except Exception as e:
            print(f"   ⚠️  git log exception for {filepath}: {type(e).__name__}: {e}", flush=True)
        return datetime.now().strftime("%Y-%m-%d")

    def _days_since(self, iso_date: str) -> int:
        try:
            y, m, d = map(int, iso_date.split("-"))
            return max(0, (date.today() - date(y, m, d)).days)
        except Exception:
            return 0

    def _get_git_contributors(self):
        if self._git_meta and self._git_meta.get("contributors") is not None:   # NEW
            return self._git_meta["contributors"]
        try:                                                                    # ── existing shortlog below ──
            r = subprocess.run(["git", "shortlog", "-sne", "master"],
                               cwd=self.repo_root, capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                print(f"   ⚠️  git shortlog failed: {r.stderr.strip()}", flush=True)
                return []
            out, seen, bots = [], set(), ["copilot", "bot", "github", "dependabot", "renovate", "noreply"]
            for line in r.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.strip().split("\t", 1)
                if len(parts) != 2:
                    continue
                count = int(parts[0])
                if "<" in parts[1] and ">" in parts[1]:
                    email = parts[1].split("<")[1].split(">")[0].strip().lower()
                    if any(b in email for b in bots):
                        continue
                    ldap = email.split("@")[0]
                    if any(b in ldap for b in bots) or ldap in seen:
                        continue
                    out.append({"ldap": ldap, "commits": count})
                    seen.add(ldap)
            return out
        except Exception as e:
            print(f"   ⚠️  contributors exception: {type(e).__name__}: {e}", flush=True)
            return []

    def emit_git_metadata(self, out_path: str):
        """Snapshot all git-derived data so a container build (no .git) can reuse it.
        Run AFTER generate() on a host with full history."""
        files = {}
        for item in self.data["agents"] + self.data["skills"]:
            rel = str(item.get("path", "")).replace(chr(92), "/")
            fp = self.repo_root / rel
            files[rel] = {
                "last_date": item.get("last_updated", ""),                       # from live git during scan
                "last_ldap": self._get_last_commit_ldap(fp) if fp.exists() else None,
            }
        meta = {
            "generated_at": datetime.now().isoformat(),
            "contributors": self.data["stats"].get("contributors_list", []),
            "files": files,
        }
        Path(out_path).write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"   ✅ git metadata → {out_path} ({len(files)} files, {len(meta['contributors'])} contributors)")

    def _get_last_commit_ldap(self, filepath: Path) -> str | None:
        if self._git_meta:                                              # NEW
            info = self._git_meta["files"].get(self._relkey(filepath, self.repo_root))
            return info.get("last_ldap") if info else None
        try:                                                            # ── existing fallback below ──
            rel = filepath.relative_to(self.repo_root)
            r = subprocess.run(
                ["git", "log", "-1", "--format=%ae", str(rel)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode == 0 and r.stdout.strip() and "@" in r.stdout:
                return r.stdout.strip().split("@", 1)[0].lower()
            print(f"   ⚠️  git log %ae failed for {filepath}: rc={r.returncode} stdout={r.stdout.strip()!r} stderr={r.stderr.strip()!r}", flush=True)
        except Exception as e:
            print(f"   ⚠️  git log %ae exception for {filepath}: {type(e).__name__}: {e}", flush=True)
        return None

    def _build_contributor_items_map(self):
        """Map contributor LDAP to recently-touched agents/skills with update dates."""
        items_map = defaultdict(list)

        for a in self.data.get("agents", []):
            path = self.repo_root / Path(a.get("path", ""))
            ldap = self._get_last_commit_ldap(path) if path.exists() else None
            if not ldap:
                continue
            items_map[ldap].append({
                "type": "agent",
                "name": a.get("name", "Unnamed Agent"),
                "role": a.get("role", "General"),
                "updated": a.get("last_updated", ""),
                "path": str(a.get("path", "")),
                "github_url": a.get("github_url", ""),
            })

        for s in self.data.get("skills", []):
            path = self.repo_root / Path(s.get("path", ""))
            ldap = self._get_last_commit_ldap(path) if path.exists() else None
            if not ldap:
                continue
            items_map[ldap].append({
                "type": "skill",
                "name": s.get("name", "Unnamed Skill"),
                "role": "Shared skill",
                "updated": s.get("last_updated", ""),
                "path": str(s.get("path", "")),
                "github_url": s.get("github_url", ""),
            })

        for ldap, items in items_map.items():
            items.sort(key=lambda x: x.get("updated", ""), reverse=True)

        self._contributor_items_map = dict(items_map)

    # ---------------------------------------------------------------- scan (unchanged logic)
    def scan_agents(self):
        print("📁 Scanning agents...")
        d = self.repo_root / "agents"
        if not d.exists():
            print("⚠️  No agents directory"); return
        files = list(d.rglob("*.agent.md"))
        print(f"   Found {len(files)} agent files")
        for f in files:
            try:
                a = self._parse_agent(f)
                if a:
                    self.data["agents"].append(a)
            except Exception as e:
                print(f"   ⚠️  {f.name}: {e}", flush=True)
        print(f"   ✅ {len(self.data['agents'])} agents")

    def scan_skills(self):
        print("📁 Scanning skills...")
        d = self.repo_root / "skills"
        if not d.exists():
            print(f"⚠️  No skills directory at {d}"); return
        files = list(d.glob("*/SKILL.md"))
        print(f"   Found {len(files)} skill files")
        for f in files:
            try:
                s = self._parse_skill(f)
                if s:
                    self.data["skills"].append(s)
            except Exception as e:
                print(f"   ⚠️  {f.parent.name}: {e}", flush=True)
        print(f"   ✅ {len(self.data['skills'])} skills")

    def _parse_agent(self, filepath: Path):
        content = filepath.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return None
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except Exception:
            return None
        body = parts[2].strip()

        path_parts = filepath.parts
        ai = path_parts.index("agents") if "agents" in path_parts else -1
        if ai >= 0 and len(path_parts) > ai + 1:
            role = path_parts[ai + 1].replace("-", " ").title()
        else:
            applies = fm.get("applies_to", [])
            role = (applies[0].title() if isinstance(applies, list) and applies else fm.get("role", "General"))
        if role == "Ai Engineer":
            role = "AI Engineer"

        author = fm.get("author", fm.get("created_by", "GRIT Hub Team"))
        description = fm.get("description", "No description available")

        capabilities = []
        m = re.search(r"## Persona\n\n.*?with expertise in:\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
        if m:
            capabilities = [l.strip("- ").strip() for l in m.group(1).split("\n") if l.strip().startswith("-")]

        use_cases = []
        m = re.search(r"## Common Use Cases\n\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
        if m:
            use_cases = [l.strip("- ").strip().strip('"') for l in m.group(1).split("\n") if l.strip().startswith("-")]

        name = fm.get("name", "Unnamed")
        slug = name.lower().replace(" ", "-").replace("\u2014", "-").replace("--", "-").strip("-")
        _fwd = chr(47)
        usage_cli = f'Include new agent with from {self.base_url}/{str(filepath.relative_to(self.repo_root)).replace(chr(92), _fwd)}'
        usage_ide = (
            f"# VS Code / JetBrains\n"
            f"1. Open GitHub Copilot Chat\n"
            f"2. Click the Agent Dropdown (next to the chat input box)\n"
            f"   — or type @{slug} if the agent file is in your repo\n"
            f"3. Select \"{name}\"\n"
            f"4. Start your conversation"
        )

        rel = filepath.relative_to(self.repo_root)
        last_updated = self._get_last_commit_date(filepath)
        return {
            "name": name, "description": description, "role": role, "author": author,
            "version": fm.get("version", "1.0.0"),
            "capabilities": capabilities[:5], "use_cases": use_cases[:5],
            "skills": fm.get("skills", []) or [], "tools": fm.get("tools", []) or [],
            "path": str(rel), "github_url": f"{self.base_url}/{str(rel).replace(chr(92), '/')}",
            "usage_cli": usage_cli, "usage_ide": usage_ide, "last_updated": last_updated,
        }

    def _parse_skill(self, filepath: Path):
        content = filepath.read_text(encoding="utf-8")
        skill_dir = filepath.parent.name
        name = skill_dir.replace("-", " ").title()
        desc, author, capabilities = "", "GRIT Hub Team", []

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    desc = fm.get("description", desc)
                    author = fm.get("author", fm.get("created_by", author))
                    content = parts[2]
                except Exception:
                    pass

        lines = content.strip().split("\n")
        in_cap = False
        for line in lines:
            if not desc and line.strip() and not line.startswith(("#", "|", "-")):
                desc = line.strip()
            if "what" in line.lower() and "skill" in line.lower():
                in_cap = True
            elif in_cap and line.strip().startswith("-"):
                c = line.strip("- ").strip()
                if len(c) > 10:
                    capabilities.append(c)
            elif in_cap and line.strip() and not line.startswith("-"):
                in_cap = False
        if not capabilities:
            for line in lines:
                if line.strip().startswith("- ") and len(line.strip()) > 15:
                    capabilities.append(line.strip("- ").strip())
                if len(capabilities) >= 5:
                    break

        used_by = []
        for a in self.data["agents"]:
            for s in a.get("skills", []):
                slug = str(s).lower().replace("_", "-").replace(" ", "-")
                if skill_dir in slug or slug in skill_dir:
                    used_by.append(a["name"]); break

        last_updated = self._get_last_commit_date(filepath)
        return {
            "name": name, "filename": skill_dir,
            "description": (desc[:300] if desc else f"Skill: {name}"),
            "author": author, "capabilities": capabilities[:5],
            "path": f"skills/{skill_dir}/SKILL.md",
            "github_url": f"{self.base_url}/skills/{skill_dir}/SKILL.md",
            "used_by": used_by, "usage_count": len(used_by),
            "last_updated": last_updated,
        }

    def compute_stats(self):
        print("📊 Computing statistics...")
        agents_dir = self.repo_root / "agents"
        role_folders = [d.name for d in agents_dir.iterdir() if d.is_dir() and d.name != "everyone"] if agents_dir.exists() else []
        contributors = self._get_git_contributors()
        self._build_contributor_items_map()
        self.data["stats"] = {
            "total_agents": len(self.data["agents"]),
            "total_skills": len(self.data["skills"]),
            "roles": len(role_folders),
            "contributors": len(contributors),
            "contributors_list": contributors,
        }

    # ---------------------------------------------------------------- mapping -> glass shape
    def _role_color_map(self) -> dict:
        roles = {}
        i = 0
        for a in self.data["agents"]:
            r = a["role"]
            if r not in roles:
                roles[r] = {"c": ROLE_COLORS.get(r) or PALETTE[i % len(PALETTE)]}
                i += 1
        roles.setdefault("Everyone", {"c": "#FFD21E"})
        return roles

    def _emoji_for(self, role: str) -> str:
        return ROLE_EMOJI.get(role, "🌐")

    def _agents_payload(self):
        out = []
        for a in self.data["agents"]:
            out.append({
                "name": a["name"], "role": a["role"], "emoji": self._emoji_for(a["role"]),
                "author": a["author"], "desc": a["description"],
                "skills": [str(s) for s in a.get("skills", [])],
                "tools": [str(t) for t in a.get("tools", [])],
                "capabilities": a.get("capabilities", []), "useCases": a.get("use_cases", []),
                "version": a.get("version", ""), "days": self._days_since(a["last_updated"]),
                "updated": a.get("last_updated", ""),
                "githubUrl": a["github_url"], "usageCli": a["usage_cli"], "usageIde": a["usage_ide"],
            })
        return sorted(out, key=lambda x: x["name"].lower())

    def _skills_payload(self):
        out = []
        for s in self.data["skills"]:
            out.append({
                "name": s["name"], "role": "Everyone", "emoji": "🧠", "isSkill": True,
                "author": s["author"], "desc": s["description"],
                "skills": [], "capabilities": s.get("capabilities", []),
                "usageCount": s.get("usage_count", 0), "usedBy": s.get("used_by", []),
                "days": self._days_since(s["last_updated"]), "githubUrl": s["github_url"],
                "updated": s.get("last_updated", ""),
            })
        return sorted(out, key=lambda x: x["usageCount"], reverse=True)

    def _activity_payload(self):
        """Most-relied-on skills, ranked by how many agents declare them (real data)."""
        ranked = sorted(self.data["skills"], key=lambda s: s["usage_count"], reverse=True)
        ranked = [s for s in ranked if s["usage_count"] > 0][:7]
        return [{"name": s["name"], "role": "skill", "value": s["usage_count"], "unit": "agents"} for s in ranked]

    def _contributors_payload(self):
        out = []
        for i, c in enumerate(self.data["stats"].get("contributors_list", [])):
            items = self._contributor_items_map.get(c["ldap"], [])
            out.append({"name": c["ldap"], "count": c["commits"],
                        "maintainer": (c["ldap"] == self.cfg.get("metadata", {}).get("maintainer", "fuhau.teh")),
                        "items": items})
        return out

    # ---------------------------------------------------------------- render
    def generate_html(self):
        print("🎨 Injecting data into glass template...")
        if not TEMPLATE.exists():
            sys.exit(f"Template not found: {TEMPLATE}")

        colors = self.cfg.get("colors", {})
        tokens = {}
        if colors.get("primary"):   tokens["--red-soft"] = colors["primary"]
        if colors.get("secondary"): tokens["--yellow"] = colors["secondary"]

        activity = self._activity_payload()
        data = {
            "roles": self._role_color_map(),
            "stats": {
                "agents": self.data["stats"]["total_agents"],
                "skills": self.data["stats"]["total_skills"],
                "roles": self.data["stats"]["roles"],
                "contributors": self.data["stats"]["contributors"],
            },
            "agents": self._agents_payload(),
            "skills": self._skills_payload(),
            "activity": activity,
            "activityMeta": {
                "enabled": bool(activity),
                "title": "Most-relied-on skills",
                "tag": "By agent usage",
                "sub": "Ranked by how many agents declare each skill.",
            },
            "contributors": self._contributors_payload(),
            "meta": {
                "project": self.cfg.get("project_name", "GRIT Hub"),
                "repo": self.cfg.get("project_name", "grit-hub"),
                "repoUrl": self.cfg.get("github_repo", ""),
                "updated": datetime.now().strftime(
                    self.cfg.get("timestamp_format", "%d %b %Y, %I:%M %p GMT+8")),
                "defaultTheme": self.cfg.get("default_theme", "light"),
                "ambientOpacity": self.cfg.get("ambient_opacity", 0.34),
                "tokens": tokens,
            },
        }

        template = TEMPLATE.read_text(encoding="utf-8")
        if not PLACEHOLDER.search(template):
            sys.exit("Template missing /*__PORTAL_DATA__*/ … /*__END_PORTAL_DATA__*/ marker.")
        payload = "/*__PORTAL_DATA__*/" + json.dumps(data, ensure_ascii=False) + "/*__END_PORTAL_DATA__*/"
        html = PLACEHOLDER.sub(lambda _: payload, template, count=1)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "index.html").write_text(html, encoding="utf-8")
        (self.output_dir / "data.json").write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        print(f"   ✅ {self.output_dir / 'index.html'}")
        self._copy_assets()

    def _copy_assets(self):
        print("📦 Copying assets...")
        src = SCRIPT_DIR / "assets"
        dest = self.output_dir / "assets"
        if src.exists():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print(f"   ✅ {dest}")
        else:
            print(f"   ⚠️  No assets folder at {src}", flush=True)

    def generate(self):
        print("\n🚀 Starting portal generation (glass edition)...")
        self.scan_agents()
        self.scan_skills()
        self.compute_stats()
        self.generate_html()
        print(f"\n✅ Portal generated at {self.output_dir}/index.html\n")


if __name__ == "__main__":
    import argparse

    # Make the script behave on Windows PowerShell and in containers with UTF-8 logs.
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    p = argparse.ArgumentParser(description="Generate GRIT Hub Portal (glass edition)")
    p.add_argument("--repo-root", default="../../../", help="Path to repo root")
    p.add_argument("--output", default="dist", help="Output directory")
    p.add_argument("--git-metadata", default=None,
                   help="Consume precomputed git metadata (skips all live git calls)")
    p.add_argument("--emit-git-metadata", default=None,
                   help="Write git metadata after generation (run where .git exists)")
    args = p.parse_args()
    gen = PortalGenerator(args.repo_root, args.output, git_metadata=args.git_metadata)
    gen.generate()
    if args.emit_git_metadata:
        gen.emit_git_metadata(args.emit_git_metadata)

