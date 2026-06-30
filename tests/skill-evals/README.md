# Skill Readiness Evaluation

Use this folder to test whether GRIT Hub skills are ready for real users.

The evaluator checks every `skills/<skill>/SKILL.md` for:

- metadata quality
- trigger clarity
- when-to-use guidance
- output format guidance
- examples or sample prompts
- security guardrails
- token/length sanity
- optional per-skill prompt cases

## Run all skills

```bash
python tests/skill-evals/run_skill_eval.py --all
```

## Run one skill

```bash
python tests/skill-evals/run_skill_eval.py --skill skill-picker
python tests/skill-evals/run_skill_eval.py --skill skillopt
```

## Strict readiness gate

Use this before release when you want every skill to be production-ready.

```bash
python tests/skill-evals/run_skill_eval.py --all --strict
```

Strict mode requires every skill to score at least 85 and have no critical findings.

## CI-friendly gate

Default mode fails only for critical findings or scores below 70.

```bash
python tests/skill-evals/run_skill_eval.py --all --min-score 70
```

## Optional prompt cases

Add a file at:

```text
skills/<skill>/tests/cases.jsonl
```

Example:

```jsonl
{"prompt":"Which skill should I use for this task?", "should_trigger":true, "must_contain":["Recommended skill set"]}
{"prompt":"Translate this sentence to Chinese", "should_trigger":false}
```

Fields:

- `prompt` — user prompt to test.
- `should_trigger` — whether this skill should match the prompt.
- `must_contain` — terms that must appear in the skill document.
- `must_not_contain` — forbidden terms.

This is a lightweight trigger approximation. It does not replace real LLM eval, but it catches broad descriptions, missing examples, weak safety language, and obvious regression issues.

## Recommended release checklist

```bash
node scripts/setup.js --dry-run --skip-python
git diff --check
python tests/skill-evals/run_skill_eval.py --all --min-score 70
/tmp/grit-hub-venv/bin/python -m pytest tests/security-script -q
```

For high-confidence release:

```bash
python tests/skill-evals/run_skill_eval.py --all --strict
```
