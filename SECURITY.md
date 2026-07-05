# Security Policy

This project touches API keys, Feishu/Lark app credentials, and webhook secrets. Treat it as an automation integration project, not as a static demo.

## Supported versions

Security fixes target the latest `main` branch.

## Credential rules

- Never commit `config/.env` or any real secret.
- Use `config/.env.example` only for variable names and comments.
- Set local credential files to `chmod 600 config/.env` on Linux/macOS.
- Rotate Feishu webhook secrets and LLM API keys if they were exposed.
- Keep Docker port binding on `127.0.0.1` unless you have a reviewed network policy.

## Reporting a vulnerability

Open a private security advisory or contact the maintainer outside public issues if the report contains secrets, internal endpoints, or exploitable details.

For non-sensitive bugs, open a normal GitHub issue using the bug report template.
