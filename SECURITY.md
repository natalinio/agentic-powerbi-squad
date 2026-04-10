# Security Policy

## Supported Branch

Security fixes are handled on the default branch of this repository.

## Reporting a Vulnerability

If you identify a security issue:

- do not publish secrets, tokens, credentials, tenant identifiers, or exploit details in a public issue
- use GitHub private reporting features if available for the repository
- otherwise contact the maintainer through GitHub and provide a minimal reproduction without sensitive data

## Secret Handling Rules

- Never commit credentials, API keys, tokens, connection strings, or local environment files.
- Use placeholders such as `<TENANT_ID>`, `<CLIENT_ID>`, `<CLIENT_SECRET>`, and `<KEY_VAULT_NAME>` in examples.
- Sanitize screenshots, logs, and sample payloads before sharing them in issues or pull requests.

## Scope Notes

This repository contains prompts, instructions, scripts, templates, and documentation for Power BI development workflows. Reported issues should focus on repository content, unsafe guidance, accidental secret exposure, or automation behavior that could cause unsafe modifications.