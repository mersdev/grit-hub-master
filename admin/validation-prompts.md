# Admin Validation Prompts

Use these prompts to verify discovery, routing, and custom-agent behavior.

## Platform Smoke Tests

1. `What agents are available in this workspace? Group them by role.`
2. `Which agent should handle a change review for authentication code?`
3. `Show me the custom agents visible from my user profile.`

Expected signal:
- Workspace agents are discoverable.
- The router picks a sensible agent for the task.
- User/global agents are listed separately from workspace agents.

## Role Checks

1. `I need help with SQL tuning. Which existing agent should I use?`
2. `I need help with an OpenShift deployment. Which existing agent should I use?`
3. `I need help with slide generation. Which existing agent should I use?`

Expected signal:
- The answer maps to the right role instead of guessing.
- The response names an existing agent when one fits.

## Per-Agent Checks

Use one prompt per shipped agent file:

- `agents/ai-engineer/development-coach/development-coach.agent.md`
  - Prompt: `Help me decide whether to reuse, improve, or create an agent for this task.`
- `agents/ai-engineer/agent-router/agent-router.agent.md`
  - Prompt: `Route this request to the best existing agent.`
- `agents/ai-engineer/skill-discoverer/skill-discoverer.agent.md`
  - Prompt: `Find the best skill for this task and explain why.`

Expected signal:
- The response matches the agent's purpose.
- The agent does not drift into unrelated behavior.

## Custom-Agent Check

1. Add a temporary custom agent to `.github/agents/`.
2. Add another temporary custom agent to `~/.copilot/agents/`.
3. Reload the client.
4. Ask: `List all custom agents you can see, separated by workspace and user scope.`

Expected signal:
- Workspace and user scope are both discovered.
- A user-level agent overrides a workspace agent only when intended.

## Failure Triage

- If setup fails, fix the referenced file and rerun `node scripts/setup.js --dry-run`.
- If routing is wrong, inspect the matching agent frontmatter and descriptions.
- If a custom agent is missing, check the file location and reload the client.
