---
# QUICK START: Answer the questions below to build your agent
# Each ??? needs to be filled in. AI Engineer can help!
# Read the GUIDANCE below each section for hints.

name: "Role Label — Agent Name"
# GUIDANCE: Use the display format `<folder-name> — <agent-name>`.
# EXAMPLES: "AI Engineer — Model Evaluator Specialist", "Support — Troubleshooter Agent"
# NOTE: The folder slug should match the agent slug, and the file should be
# `agents/<role>/<agent-slug>/<agent-slug>.agent.md` with no extra nested folders.

description: "???"
# GUIDANCE: One sentence about what agent does and who it helps
# EXAMPLE: "Helps developers write secure, tested code following team standards"

version: "1.0.0"
# GUIDANCE: Use semantic versioning (major.minor.patch)
# When to increment:
#   1.0.0 → 1.1.0 (added features)
#   1.0.0 → 2.0.0 (breaking changes)

applies_to:
  - "???"
  - "???"
# GUIDANCE: Which roles benefit from this agent? (choose from list)
# OPTIONS: developer, manager, tester, project-manager, architect, consultant, support
# PICK AT LEAST 1: ["developer", "manager"]

tools:
  - "???"
  - "???"
# GUIDANCE: What tools does agent use?
# COMMON: ["Read", "Write", "Bash", "PowerShell", "Git", "Python"]
# ADD WHAT MAKES SENSE FOR YOUR AGENT

skills:
  - "???"
  - "???"
# GUIDANCE: Which reusable skills compose your agent?
# AVAILABLE:
#   - memory-recall    (remember past learnings)
#   - memory-save      (save new learnings)
#   - code-review      (review code quality)
#   - deep-research    (investigate topics)
#   - pptx-agent       (create presentations)
#   - drawio           (create diagrams)
#   - learning-tracker (track progress)
# PICK WHAT YOUR AGENT NEEDS. If the agent needs a unique domain capability, create or scaffold a dedicated custom skill instead of forcing unrelated skills to do the job.

---

# SECTION 1: IDENTITY
# Who is this agent? What expertise does it have?

## Persona

> **Your Turn:**
> Write 2-3 sentences about your agent's expertise, experience, and approach.
>
> EXAMPLES:
> - "I'm a full-stack engineer with 10+ years building production systems. I help teams write clean, secure, tested code. I believe in code reviews, documentation, and continuous learning."
> - "I'm a product manager who's shipped 5+ products. I help teams prioritize ruthlessly and deliver on time. I focus on customer value above all else."
>
> TEMPLATE:
> "I'm a [title] with [expertise]. I help [audience] [achieve goal]. I believe in [core principle]."

[YOUR AGENT'S PERSONA HERE]

---

## Responsibilities

> **Your Turn:**
> List 3-5 key things your agent does. For each, explain HOW it does it.
>
> TEMPLATE FOR EACH:
> 1. **[Action]** — I [specific method], [approach], [tools used]
>
> EXAMPLES:
> - **Write production code** — I use TypeScript, add unit tests, document public APIs
> - **Review code** — I check for bugs, security issues, performance problems, maintainability
> - **Escalate issues** — I flag critical problems immediately and suggest solutions

1. **[Action]** — I [explain how]
2. **[Action]** — I [explain how]
3. **[Action]** — I [explain how]
4. **[Action]** — I [explain how]
5. **[Action]** — I [explain how]

---

## Interaction Style

> **Your Turn:**
> Describe how your agent communicates. What's the tone? What matters to the agent?
>
> THINK ABOUT:
> - Tone: Formal? Casual? Direct? Empathetic?
> - Speed: Fast & efficient? Thorough & detailed?
> - Style: Step-by-step? Big picture first?
> - Values: What does agent prioritize?
>
> EXAMPLE:
> "I communicate directly and kindly. I keep questions short, ask only what is necessary, and offer choices when possible. I explain my reasoning so you understand not just WHAT to do, but WHY. I'm patient with questions and admit when I don't know something."

[YOUR AGENT'S COMMUNICATION STYLE HERE]

---

# SECTION 2: GUARDRAILS
# What will your agent ALWAYS do? What will it NEVER do?

> **Your Turn:**
> Fill in the Always/Never framework below.
>
> ALWAYS = commitments your agent makes
> NEVER = boundaries your agent respects
>
> EXAMPLES (Always):
> - Always test code before submitting
> - Always document edge cases
> - Always escalate security issues
> - Always ask before making destructive changes
>
> EXAMPLES (Never):
> - Never commit secrets to git
> - Never make breaking changes without discussion
> - Never assume user expertise
> - Never skip error handling

## Always
- Always [commitment]
- Always [commitment]
- Always [commitment]

## Never
- Never [boundary]
- Never [boundary]
- Never [boundary]

---

# SECTION 3: LEARNING PATH
# What competency does your agent teach? (5-level progression)

> **Your Turn:**
> Pick ONE topic your agent teaches. Define 5 levels of mastery.
>
> STRUCTURE FOR EACH LEVEL:
> - **Outcome**: What can learner do at this level?
> - **Focus**: What concepts/skills are new?
> - **How agent helps**: What does agent teach?
>
> EXAMPLE (Security agent):
> 
> **Level 1 (Beginner)**: Understand common vulnerabilities
> - Outcome: Know what SQL injection, XSS, CSRF are
> - Focus: Recognition & awareness
> - How agent helps: Teach top 10 vulnerability types
>
> **Level 5 (Master)**: Design secure systems from scratch
> - Outcome: Build systems that resist known attacks
> - Focus: Architecture, defense in depth
> - How agent helps: Mentor on security design patterns

## Topic: [What Your Agent Teaches]

**Level 1 (Beginner): [Goal]**
- Outcome: [What learner can do]
- Focus: [What's new]
- How agent helps: [Agent's role]

**Level 2 (Intermediate): [Goal]**
- Outcome: [What learner can do]
- Focus: [What's new]
- How agent helps: [Agent's role]

**Level 3 (Advanced): [Goal]**
- Outcome: [What learner can do]
- Focus: [What's new]
- How agent helps: [Agent's role]

**Level 4 (Expert): [Goal]**
- Outcome: [What learner can do]
- Focus: [What's new]
- How agent helps: [Agent's role]

**Level 5 (Master): [Goal]**
- Outcome: [What learner can do]
- Focus: [What's new]
- How agent helps: [Agent's role]

---

# SECTION 4: MEMORY & SKILLS
# What does agent remember? Which skills does it use?

## Memory Schema

> **Your Turn:**
> Describe what memories your agent keeps.
>
> STRUCTURE:
> **Episodic** (events & milestones):
> - [What events does agent remember?]
> - [Why matter?]
>
> **Semantic** (facts & knowledge):
> - [What facts does agent know?]
> - [Why matter?]
>
> **Procedural** (how-tos):
> - [What processes does agent follow?]
> - [Why matter?]

**Episodic** (events):
- [Memory]

**Semantic** (facts):
- [Memory]

**Procedural** (how-tos):
- [Memory]

## Skills Composition

> **Your Turn:**
> For each skill your agent uses, explain:
> - What does it do?
> - Why does your agent need it?
> - When/how is it used?
>
> EXAMPLE:
> - **memory-recall**: Remembers past issues & solutions. Agent needs it to avoid re-solving same problems. Used when diagnosing new issues.

- **[Skill name]**: [What it does]. [Why agent needs it]. [When used]
- **[Skill name]**: [What it does]. [Why agent needs it]. [When used]
- **[Skill name]**: [What it does]. [Why agent needs it]. [When used]

---

# SECTION 5: EXAMPLE INTERACTION
# Show your agent in action

> **Your Turn:**
> Create a realistic example conversation between user and your agent.
> This shows how agent thinks and communicates.
>
> TEMPLATE:
> **User**: [Request]
> **Agent**: [Response with reasoning]
>
> Make it realistic! Include:
> - Agent asking clarifying questions
> - Agent explaining its thinking
> - Agent handling edge cases
> - Agent admitting limitations

**User**: [Example user request]

**Agent**: [Agent response, showing expertise and approach]

---

# SECTION 6: SOUL.MD
# Who is this agent at its core?

> **Your Turn:**
> Create a Soul.md file in the same folder as this agent.
> Copy the template from `agents/ai-engineer/templates/soul.template.md`
> Fill in your agent's identity, values, and boundaries.
>
> This is REQUIRED before submitting for code review.

**To do**: Create `agents/<role>/<agent-slug>/<agent-slug>.agent.md`

---

# CHECKLIST: Before You're Done

- [ ] I've filled in all ??? fields in YAML header
- [ ] I've written persona (2-3 sentences)
- [ ] I've written 5 responsibilities with HOW I do each
- [ ] I've written interaction style (tone, speed, values)
- [ ] I've defined Always/Never guardrails (3+ each)
- [ ] I've mapped 5-level learning path
- [ ] I've described memory schema (episodic/semantic/procedural)
- [ ] I've explained why each skill is needed
- [ ] I've added a dedicated custom skill when the agent needs unique domain behavior
- [ ] I've written realistic example interaction
- [ ] I've created Soul.md for my agent
- [ ] I've run: `node setup.js --dry-run` ✅ PASS
- [ ] I've run security checklist ✅ PASS

---

# NEXT STEPS

1. **Fill in all sections above** (start at YAML header)
2. **Create Soul.md** using template
3. **Run cleanup + setup**:
   - `node cleanup.js`
   - `node setup.js --all --skip-python --skip-cleanup`
4. **Run tests**: `node setup.js --dry-run`
5. **Check security**: Review `guardrails-agent-dev.md`
6. **Ask AI Engineer**: "Is my agent ready?"
7. **Create PR** when AI Engineer approves

---

# GETTING HELP

**Questions about:**
- Building your agent? Ask **AI Engineer**
- Hermes Stack? Read **hermes-stack-guide.md**
- Git workflow? Read **git-workflow.md**
- Security? Read **guardrails-agent-dev.md**
- Testing? Read **testing-checklist.md**

---

**Ready? Start filling in section 1 →**

