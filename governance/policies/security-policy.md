# Security Policy

This document defines security constraints for all layers of the AI Operating System.

---

## Principles

1. **Never commit secrets.** API keys, tokens, passwords, and private certificates must never appear in source code, configuration, or reports.
2. **Least privilege.** Access to systems, repositories, and credentials is limited to what a task requires.
3. **No secret logging.** Logs must not contain credentials, tokens, or PII.
4. **External input is untrusted.** Validate and sanitize all external input before use.

---

## Rules

### Secrets

- Use environment variables or a secrets manager; never hardcode secrets.
- `.env` files are not committed. See `skills/skill-optimizer/.env.example` for shape (example values only).
- Production error messages avoid leaking internal details (encoding-safe English, per `LANGUAGE_CONVENTION.md`).

### Code

- No hardcoded project paths or credentials in AI System assets (enforced by `governance/repo-lint.md`).
- No absolute local paths (`C:\`, `/home/`, `/usr/`) in reusable assets.

### Prompts and Workflows

- Workflows never inject secrets into prompt context.
- User-provided content is treated as data, never as instructions beyond the declared input contract.

### Release

- Release readiness checks include a secret scan (`governance/review-standard.md`).
- New user-facing copy is confirmed by the product owner (`governance/standards/common/copy-review.md`).

---

## Violations

Security violations are classified as **BLOCKER** (see `governance/violation-rules.md`) and must be fixed before merge or release.

---

## Scope

Applies to all AI System assets: workflows, skills, templates, tools, configuration, and generated reports.
