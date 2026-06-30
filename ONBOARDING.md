# Onboarding Guide

GRIT Hub has one default onboarding path for end users and a simple admin checklist in `admin/`.

## Default Prompt

Start here if you are not sure which agent, skill, or folder you need:

```text
I want an AI helper for my team. Ask me simple questions and recommend whether to reuse, improve, or create an agent.
```

This routes through Development Coach. It should keep the conversation in plain language and prefer reuse before creation.

## Non-Technical User Journey

### IDE

1. Open this repo.
2. Run `npm install`.
3. Reload your IDE.
4. Open Copilot Chat.
5. Paste the default prompt.

If you only want one role or one agent in the workspace:

```bash
node scripts/setup.js --role developer --skip-python
node scripts/setup.js --agent fullstack-engineer --skip-python
```

### Copilot CLI

1. Install and sign in to Copilot CLI.
2. Open a terminal in this repo.
3. Run `npm install`.
4. Start `copilot`.
5. Paste the default prompt.

### What Should Happen

- The first response should ask a few simple intake questions.
- The system should recommend reuse, improve, or create new.
- You should not need to know agent names up front.

## Discovery Model

Use these locations consistently:

- Workspace agents: `.github/agents/*.agent.md`
- User/global custom agents: `~/.copilot/agents/*.agent.md`
- Shared global instructions and assets: `~/.copilot/`

`AGENTS.md` is optional documentation. It is not part of the required discovery path.

## Quick Verification

### End User Check

Ask:

```text
I want an AI helper for my team. Ask me simple questions and recommend whether to reuse, improve, or create an agent.
```

Success looks like:

- Development Coach behavior
- plain-language questions
- reuse before create

### Workspace Check

Ask:

```text
What agents are available in this workspace? Group them by role and tell me the default starting point.
```

Success looks like:

- agents grouped by role
- Development Coach identified as the front door

## Troubleshooting

### Agents not showing in the IDE

1. Run `node scripts/setup.js --dry-run` and confirm it references `.github/agents`.
2. Reload the IDE window.
3. Ask Copilot to list available workspace agents again.

### CLI not picking up shared assets

1. Confirm `~/.copilot/copilot-instructions.md` exists.
2. Confirm `~/.copilot/skills/` exists.
3. Restart Copilot CLI from the repo root.

## Next Step

Go back to the default prompt and keep the flow simple: reuse first, improve second, create last.

If you are validating the repo, use [admin/README.md](./admin/README.md).
