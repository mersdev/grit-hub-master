---
# Memory Schema Template for Your Agent
# This file defines WHAT your agent remembers and WHY
# Memory is persistent context that makes agents smarter over time
---

# [Agent Name] — Memory Schema

> Memory is what makes agents improve with use.
> This schema defines what your agent learns from interactions and stores for future use.

---

## Overview

> **Why does this agent need memory?**
>
> Answer: [Why does your agent benefit from persistent context?]
>
> EXAMPLES:
> - "So it can remember which tests fail often and suggest preventative fixes"
> - "So it learns team conventions and applies them automatically"
> - "So it tracks past issues and avoids re-solving the same problem"

[Why memory matters for your agent]

---

## Memory Tiers (Choose What You Need)

Your agent can use 1, 2, or all 3 tiers. Identify which apply to your agent:

---

## Tier 1: Episodic Memory
### (Events & Milestones)

> **What events/milestones does your agent remember?**
>
> Episodic memory is about WHAT HAPPENED. Examples of events:
> - User shipped a feature
> - Bug was discovered and fixed
> - Team meeting occurred
> - Code review feedback came in
> - Test suite was updated
>
> STRUCTURE:
> - **Event Type**: [What kind of event]
>   - **What triggers capture**: [When does agent save this?]
>   - **What gets saved**: [What specific data?]
>   - **Why it matters**: [How does agent use this memory?]
>   - **Privacy**: [Does it store PII? No. Examples only: event_id, anonymized_date]
>
> EXAMPLE:
> - **Event Type**: Test failure pattern
>   - **Triggers**: When test fails 3+ times
>   - **Saved**: test_name, error_pattern, timestamp, pass_count_before_fix
>   - **Why**: So agent recognizes pattern and suggests root cause next time
>   - **Privacy**: No PII; uses test identifiers only

### Event Type 1: [Name]
- **Triggers**: [When captured]
- **Saved**: [What data]
- **Why**: [How used]
- **Privacy**: [Safe? Y/N, explain]

### Event Type 2: [Name]
- **Triggers**: [When captured]
- **Saved**: [What data]
- **Why**: [How used]
- **Privacy**: [Safe? Y/N, explain]

### Event Type 3: [Name]
- **Triggers**: [When captured]
- **Saved**: [What data]
- **Why**: [How used]
- **Privacy**: [Safe? Y/N, explain]

---

## Tier 2: Semantic Memory
### (Facts & Knowledge)

> **What facts does your agent learn about the world?**
>
> Semantic memory is about KNOWLEDGE & CONVENTIONS. Examples:
> - Tech stack used by team (React, Node.js, etc.)
> - Team coding standards & linting rules
> - Common file structures & naming patterns
> - Known limitations of APIs/libraries
> - Team preferences (tabs vs spaces, etc.)
> - System architecture & component relationships
>
> STRUCTURE:
> - **Knowledge Type**: [What kind of fact]
>   - **How agent learns it**: [From what interaction?]
>   - **How agent uses it**: [When/why does agent apply it?]
>   - **Update frequency**: [Does it change often or rarely?]
>   - **Accuracy**: [How does agent know this is correct?]
>   - **Privacy**: [Personal data? No. Examples only: standards, patterns]
>
> EXAMPLE:
> - **Knowledge Type**: Team coding standards
>   - **Learned from**: Code review feedback, linting configs
>   - **Used by**: Agent checks new code against standards
>   - **Updates**: When team updates .eslintrc or code guide
>   - **Accurate?**: Cross-referenced with config files
>   - **Privacy**: No personal data; standards & conventions only

### Knowledge Type 1: [Name]
- **Learned from**: [How acquired]
- **Used for**: [How applied]
- **Updates**: [Change frequency]
- **Accuracy**: [How verified]
- **Privacy**: [Safe? Y/N, explain]

### Knowledge Type 2: [Name]
- **Learned from**: [How acquired]
- **Used for**: [How applied]
- **Updates**: [Change frequency]
- **Accuracy**: [How verified]
- **Privacy**: [Safe? Y/N, explain]

### Knowledge Type 3: [Name]
- **Learned from**: [How acquired]
- **Used for**: [How applied]
- **Updates**: [Change frequency]
- **Accuracy**: [How verified]
- **Privacy**: [Safe? Y/N, explain]

---

## Tier 3: Procedural Memory
### (How-to & Processes)

> **What processes does your agent follow?**
>
> Procedural memory is about HOW-TO. Examples:
> - Deployment workflow (test → stage → prod)
> - Code review checklist
> - Debugging process
> - How to structure PRs
> - How to write good test cases
> - Team's onboarding process
>
> STRUCTURE:
> - **Process**: [Name of process]
>   - **Steps**: [Ordered list of steps]
>   - **When used**: [When does agent execute this?]
>   - **Variations**: [Are there different paths?]
>   - **Validation**: [How does agent know process succeeded?]
>   - **Privacy**: [Personal data? No. Steps only: actions, not people]
>
> EXAMPLE:
> - **Process**: Code review
>   - **Steps**: 1) Check types 2) Check tests 3) Check security 4) Check style
>   - **When used**: When PR opened for review
>   - **Variations**: Different checklist for docs vs code
>   - **Success**: Agent finds no critical issues or flags them clearly
>   - **Privacy**: No personal data; process steps only

### Process 1: [Name]
- **Steps**: [1) ... 2) ... 3) ...]
- **When used**: [Context]
- **Variations**: [Different paths?]
- **Success**: [How to know it worked]
- **Privacy**: [Safe? Y/N, explain]

### Process 2: [Name]
- **Steps**: [1) ... 2) ... 3) ...]
- **When used**: [Context]
- **Variations**: [Different paths?]
- **Success**: [How to know it worked]
- **Privacy**: [Safe? Y/N, explain]

### Process 3: [Name]
- **Steps**: [1) ... 2) ... 3) ...]
- **When used**: [Context]
- **Variations**: [Different paths?]
- **Success**: [How to know it worked]
- **Privacy**: [Safe? Y/N, explain]

---

## Privacy Guardrails (MANDATORY)

> **Memory is powerful but dangerous. These guardrails are NON-NEGOTIABLE:**

- [ ] **No real PII**: Never store real names, emails, phone numbers, addresses
- [ ] **No secrets**: Never store API keys, passwords, tokens, credentials
- [ ] **No financial data**: Never store salary, cost, payment info
- [ ] **No personal preferences**: Never store user's favorite coffee, commute, family info
- [ ] **Anonymize when possible**: Use IDs instead of names, dates instead of "yesterday"
- [ ] **Audit access**: Who can read this memory? Should be user only or team-wide?

---

## Memory Storage & Lifecycle

> **How long does memory last? Where is it stored?**

### Where Stored
- [ ] Local (user's machine only)
- [ ] Team shared (stored securely, accessible to team)
- [ ] Cloud (specify provider)

### Retention
- [ ] Forever (accumulates indefinitely)
- [ ] Time-limited (delete after X months)
- [ ] Size-limited (keep only recent N items)

### Backups
- [ ] Automatic backups? (Y/N)
- [ ] User can export? (Y/N)
- [ ] User can delete? (Y/N)

### Privacy Controls
- [ ] Memory is encrypted? (Y/N)
- [ ] User controls who sees memory? (Y/N)
- [ ] Regular audit logs? (Y/N)

---

## Memory Growth Over Time

> **How does memory improve with use?**
>
> When your agent uses memory well, it should:
> - Learn faster (requires fewer explanations)
> - Make better decisions (references past context)
> - Adapt to team (applies learned conventions)
> - Improve suggestions (personalized to team's needs)
>
> EXPECTED IMPROVEMENT CURVE:
> - Day 1: Generic agent (no memory)
> - Day 7: Familiar with team patterns (episodic + semantic)
> - Day 30: Anticipates needs (procedural memory guides decisions)
> - Day 90: Feels like experienced team member (full context)

Describe how your agent should improve over a 90-day period:

[Your agent's improvement curve]

---

## Memory Interactions (Examples)

> **Show memory in action. How does agent USE what it remembers?**
>
> Give 2-3 realistic scenarios where memory changes agent behavior.
>
> STRUCTURE:
> - **Scenario**: [Situation]
> - **Without memory**: [Generic response]
> - **With memory**: [Personalized response using memory]
> - **Memory used**: [Which episodic/semantic/procedural]
>
> EXAMPLE:
> - **Scenario**: User submits new code for review
> - **Without**: "This code has style issues"
> - **With**: "This code has style issues. Last 3 PRs, you preferred short functions. This function is 80 lines — consider breaking it up?"
> - **Memory**: Semantic (team preference) + Episodic (last 3 PRs)

### Interaction 1: [Scenario]
- **Without memory**: [Generic]
- **With memory**: [Personalized]
- **Memory used**: [Which tiers]

### Interaction 2: [Scenario]
- **Without memory**: [Generic]
- **With memory**: [Personalized]
- **Memory used**: [Which tiers]

### Interaction 3: [Scenario]
- **Without memory**: [Generic]
- **With memory**: [Personalized]
- **Memory used**: [Which tiers]

---

## Data Schema (Technical)

> **How is memory stored technically?**
>
> This is for developers implementing memory persistence.
>
> EXAMPLE SCHEMA (JSON):
> ```json
> {
>   "episodic": [
>     {
>       "event_type": "test_failure",
>       "event_id": "evt_abc123",
>       "test_name": "AuthService",
>       "error_pattern": "timeout",
>       "timestamp": "2024-01-15T10:30:00Z",
>       "user_id": "user_abc"
>     }
>   ],
>   "semantic": [
>     {
>       "knowledge_type": "tech_stack",
>       "tech": "react",
>       "version": "18.0+",
>       "learned_from": "config.json",
>       "confidence": 0.95
>     }
>   ],
>   "procedural": [
>     {
>       "process_name": "deploy",
>       "steps": [...],
>       "last_used": "2024-01-15",
>       "success_rate": 0.98
>     }
>   ]
> }
> ```

[Your agent's memory data schema]

---

## Testing Memory (How to Verify)

> **How will you know memory is working correctly?**
>
> Tests for memory systems:
> - [ ] Memory persists across sessions
> - [ ] Agent retrieves correct past events
> - [ ] Agent applies learned conventions
> - [ ] Memory doesn't grow unbounded
> - [ ] Privacy guardrails are enforced
> - [ ] User can clear memory if desired

For your agent, write 3-5 specific tests:

1. [Test name]: [What it verifies]
2. [Test name]: [What it verifies]
3. [Test name]: [What it verifies]

---

## Risks & Mitigations

> **What could go wrong with memory? How will you prevent it?**
>
> COMMON RISKS:
> - Memory is stale (old info is outdated)
> - Memory is wrong (agent learned incorrect pattern)
> - Memory is biased (remembers failures more than successes)
> - Memory is leaky (contains PII)
> - Memory is too big (slows agent down)

### Risk 1: [Risk name]
- **Problem**: [What goes wrong]
- **Mitigation**: [How to prevent]

### Risk 2: [Risk name]
- **Problem**: [What goes wrong]
- **Mitigation**: [How to prevent]

### Risk 3: [Risk name]
- **Problem**: [What goes wrong]
- **Mitigation**: [How to prevent]

---

## Checklist: Is Your Memory Schema Ready?

Before submitting agent for code review:

- [ ] I've defined which memory tiers my agent uses (episodic/semantic/procedural)
- [ ] For each tier, I've listed specific data types with clear purpose
- [ ] I've verified NO real PII will ever be stored
- [ ] I've verified NO secrets will be stored
- [ ] I've documented privacy controls (encryption, access, deletion)
- [ ] I've shown 2-3 realistic scenarios where memory improves agent behavior
- [ ] I've defined how memory persists (local/team/cloud)
- [ ] I've written technical schema for data storage
- [ ] I've identified risks and mitigations
- [ ] I've identified how to test memory works

---

## Questions?

Ask **AI Engineer**:
- "How should I design memory for my agent?"
- "Is this memory schema secure?"
- "What privacy risks am I missing?"

AI Engineer can help you get this right! ✨

---

**Ready? Integrate this memory schema with your agent and test it works!**

