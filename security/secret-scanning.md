---
name: "secret-scanning"
version: "1.0.0"
description: "Guardrail preventing secrets, API keys, tokens, and credentials from being committed to source control or included in generated output."
---

# Security: Secret Scanning

## Rules

1. **Never generate real secrets** — use `<YOUR_API_KEY>` or `process.env.SECRET_NAME`
2. **Flag hardcoded secrets** — if you see tokens/keys in code, flag them immediately
3. **Use environment variables** — always suggest env vars or secret managers
4. **Check before commit** — remind users to run secret scanning before pushing

## Patterns to Flag

- API keys (long alphanumeric strings, especially prefixed: `sk-`, `ghp_`, `AKIA`)
- Connection strings with passwords
- Private keys (BEGIN RSA PRIVATE KEY, etc.)
- OAuth tokens
- JWT secrets
- Database passwords in config files

## Recommended Response

```
🔒 This appears to contain a secret/credential. Never commit secrets to source control.

Recommended:
1. Store in environment variable: process.env.MY_SECRET
2. Use a secrets manager (Azure Key Vault, AWS Secrets Manager)
3. Add the file to .gitignore if it must contain secrets locally
4. Rotate the credential if it was ever exposed
```
