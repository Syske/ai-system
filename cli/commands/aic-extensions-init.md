---
description: 初始化/校验 extensions 扩展目录（独立 git 仓库脚手架）— 新环境或新公司接入时使用
---

Initialize or verify the extensions directory as a standalone git repository.

Use when: onboarding a new environment/company, extensions/ is missing or
uninitialized, or you need to check whether extensions/ is properly set up.

**Inputs**: Remote URL (optional, company git remote like Codeup); Committer
Email / Name (optional, repo-local only); Workspace Root (default: workspace).

**Steps**

1. Ensure the workspace root is known (default: the directory containing
   `ai-system/` — resolve from Environment Context, never hardcode a path).

2. Check current state (non-destructive):

   ```bash
   python tools/extensions-init.py --workspace <root> --check
   ```

   - exit 0 → extensions/ already initialized; skip to Step 6.
   - exit 1 → continue with Step 3.

3. Initialize the extensions directory (idempotent, never overwrites):

   ```bash
   python tools/extensions-init.py --workspace <root> \
     [--remote <git-url>] [--email <email>] [--name <name>]
   ```

   This writes `.gitignore` + `README.md` (only if missing), runs
   `git init -b main`, sets repo-local committer identity, and scaffolds an
   `example-hello/` skeleton (SKILL.md + OPTIMIZATION_LOG.md templates).

4. When `--remote` is provided: the tool binds `origin`, creates the initial
   commit (if any uncommitted files exist), and pushes `-u origin main`.

5. Post-init (AI performs after confirmation):
   - Adjust `.gitignore` for company-specific sensitive/debug artifacts.
   - Verify committer identity matches the remote platform account
     (e.g. Codeup requires author email == push user email).
   - Remove or rename the `example-hello/` skeleton into real skills.

6. Verify:

   ```bash
   python tools/extensions-init.py --workspace <root> --check   # exit 0
   git -C <root>/extensions remote -v                           # origin set
   git -C <root>/extensions config user.name                    # identity
   ```

**Output**

- extensions/ directory with `.gitignore`, `README.md`, git repository
- Optional: remote bound and first push completed
- Verification result (exit 0/1)

**Guardrails**

- Never delete or overwrite existing files / git config (idempotent by design).
- Company-specific content (branch conventions, remote URLs, credentials,
  specific ignore rules) is NOT embedded — providers supply per environment.
- Commit identity is set at repo level only; never touch global git config.
