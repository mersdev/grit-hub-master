# Admin Validation

Use this when you need to confirm that GRIT Hub still routes to the right agents and that custom agents are visible in the expected locations.

## What To Check

- Workspace agents live in `.github/agents/*.agent.md`
- User/global custom agents live in `~/.copilot/agents/*.agent.md`
- Shared instructions live in `~/.copilot/copilot-instructions.md`

`AGENTS.md` is optional. It is not part of the discovery path.

## Quick Checks

1. Run `node scripts/setup.js --dry-run`.
2. Open Copilot in the repo.
3. Start with the default prompt from [README.md](../README.md).
4. Ask: `What agents are available in this workspace? Group them by role.`
5. Ask: `I need help reviewing an authentication change. Which agent should handle it?`

## Custom Agent Check

1. Add a test agent to `.github/agents/`.
2. Add the same or another test agent to `~/.copilot/agents/`.
3. Reload Copilot.
4. Ask: `List custom agents from the workspace and from my user profile.`
5. Invoke the test agent by name and verify the response matches the file you expected.

## If Something Fails

- If setup fails, fix the referenced file path and rerun `node scripts/setup.js --dry-run`.
- If an agent is missing, check the source file in `agents/<role>/<agent>/<agent>.agent.md`.
- If a custom agent is not visible, reload the client and try the workspace query again.
