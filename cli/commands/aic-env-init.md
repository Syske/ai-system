---
description: 初始化/校验环境配置（workspace local.yaml + 机器层 ~/.config/ai-system/env.yaml，跨平台按系统生成）— 新环境/首次运行/环境配置丢失时使用
---

Initialize or verify the environment configuration (cross-platform).

Use when: first run on a new machine (WSL / Windows / Linux), environment
config missing or corrupted, or you need to re-provision the machine-layer
config (`~/.config/ai-system/env.yaml`).

**Inputs**: Environment (default: local); Workspace Root (default: workspace,
auto-derived — parent of `ai-system/`, never hardcode).

**Steps**

1. Resolve the workspace root (default: the directory containing
   `ai-system/` — from Environment Context, never hardcode a path).

2. Run (non-destructive, skips existing files):

   ```bash
   python3 tools/setup.py --env-init \
     [--environment <env>] [--workspace <root>]
   ```

   - generates workspace `config/environments/<env>.yaml` if missing
   - generates machine-layer `~/.config/ai-system/env.yaml` if missing:
     platform auto-detected (windows / wsl / linux), common JDK/Maven
     locations probed; special cases (e.g. WSL `/mnt/d/...`) — the user
     edits the generated file directly
   - prints merged resolution (`workspace_root` / `build`) for verification

3. Verify resolution:

   ```bash
   python3 -c "from cli.services.environment import resolve_environment; \
   r = resolve_environment(); print(r['paths']['workspace_root']); \
   print((r.get('build') or {}).get('java_home'))"
   ```

   - `workspace_root` exists; `build` reflects the machine-layer values.

**Output**

- `config/environments/<env>.yaml` (workspace layer, created only if missing)
- `~/.config/ai-system/env.yaml` (machine layer, created only if missing,
  platform-detected)
- Merged resolution verification result

**Guardrails**

- Never delete or overwrite existing config (idempotent by design).
- Machine-specific paths (`build.*`, `workspace.root` anchor) live in the
  home config, never in the repository.
- Workspace-scoped keys (`bugfix.mode`, `layers`) stay in the workspace
  `local.yaml` — do not move them to the home config (cross-platform drift).
- Full provisioning (directory scaffold, repo links, metrics baseline,
  path audit) belongs to `python3 tools/setup.py`; `--env-init` is
  config-focused only.
