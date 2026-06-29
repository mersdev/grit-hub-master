---
name: "pii-protection"
version: "1.0.0"
description: "Guardrail preventing accidental exposure of personally identifiable information (PII) in outputs, logs, or generated code."
---

# Security: PII Protection

## Rules

1. **Never include real PII in generated code** — use placeholder values (`john.doe@example.com`, `+1-555-0100`)
2. **Mask PII in logs** — if processing data containing PII, mask all but last 4 characters
3. **Warn on detection** — if the user pastes PII, note it and suggest using variables/secrets
4. **No storage of PII** — never save real names, emails, phone numbers, or IDs to memory

## PII Patterns to Watch

- Email addresses
- Phone numbers
- National ID numbers (NRIC, SSN, passport)
- Credit card numbers
- Physical addresses
- IP addresses (in some contexts)
- Date of birth combined with name

## When PII is Detected

```
⚠️ I notice this contains personal information. I'll use placeholder values
in any code I generate. Consider storing real values in environment variables
or a secrets manager.
```
