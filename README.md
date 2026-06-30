# GRIT Hub

GRIT Hub is a shared library of Copilot agents and skills. The default path is simple: start with one plain-language prompt, let `development-coach` route you, and reuse an existing agent before creating a new one.

## Start Here

Use this prompt first:

```text
I want an AI helper for my team. Ask me simple questions and recommend whether to reuse, improve, or create an agent.
```

That is the primary onboarding path for non-technical users.

## Two Journeys

### 1. Non-Technical Onboarding

1. Open Copilot in your IDE or CLI from this repo.
2. Paste the prompt above.
3. Let Development Coach ask a few short questions.
4. Reuse an existing agent when possible. Create a new one only if there is a real gap.

Detailed steps: [ONBOARDING.md](./ONBOARDING.md)

### 2. Admin Validation

Use the simple admin checklist in [admin/README.md](./admin/README.md) when you need to verify agent discovery or custom agents.

## Platform Contract

GRIT Hub uses one discovery model across supported environments:

- Workspace agents: `.github/agents/*.agent.md`
- User/global custom agents: `~/.copilot/agents/*.agent.md`
- Shared global instructions and assets: `~/.copilot/`

`AGENTS.md` is optional reference material only. It is not required for agent discovery.

## Setup

### IDE / Workspace Use

```bash
npm install
```

This runs the repo setup and populates `.github/agents`, `.github/skills`, and shared instructions.

If you want a smaller workspace install:

```bash
node scripts/setup.js --role developer --skip-python
node scripts/setup.js --agent fullstack-engineer --skip-python
```

Then reload your IDE and start with the default prompt.

### Copilot CLI Use

1. Install and sign in to Copilot CLI.
2. Run `npm install` in this repo.
3. Start Copilot from this repo root.
4. Paste the default prompt.

## What This Repo Contains

- `agents/`: source agents grouped by role
- `skills/`: reusable skills
- `scripts/`: setup, cleanup, and removal entrypoints
- `instructions/`: global Copilot instructions
- `admin/`: simple admin validation checks
- `tests/`: CI-only skill and security checks

## Validation

Useful commands:

```bash
node scripts/setup.js --dry-run
```

## More Docs

- [ONBOARDING.md](./ONBOARDING.md)
- [admin/README.md](./admin/README.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
