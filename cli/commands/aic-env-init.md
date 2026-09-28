---
description: 初始化/校验环境配置（机器层 ~/.config/ai-system/env.yaml 为权威位置，跨平台按系统生成；workspace config/environments/{env}.yaml 为可选兜底覆盖）— 新环境/首次运行/环境配置丢失时使用
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

   - generates the **machine layer** `~/.config/ai-system/env.yaml` if
     missing — **authoritative** (P29): platform auto-detected
     (windows / wsl / linux), common JDK/Maven locations probed; special
     cases (e.g. WSL `/mnt/d/...`) — the user edits the generated file
     directly
   - generates the **workspace layer** `config/environments/<env>.yaml` if
     missing — **optional fallback override only**; its absence is normal
     (see Guardrails)
   - prints merged resolution (`workspace_root` / `build`) for verification

3. Verify resolution:

   ```bash
   python3 -c "from cli.services.environment import resolve_environment; \
   r = resolve_environment(); print(r['paths']['workspace_root']); \
   print((r.get('build') or {}).get('java_home'))"
   ```

   - `workspace_root` exists; `build` reflects the machine-layer values.

**Output**

- `~/.config/ai-system/env.yaml` (**machine layer — authoritative**,
  created only if missing, platform-detected)
- `config/environments/<env>.yaml` (workspace layer — optional fallback
  override, created only if missing; absence is normal)
- Merged resolution verification result

**Guardrails**

- Never delete or overwrite existing config (idempotent by design).
- Machine-specific paths (`build.*`, `workspace.root` anchor) live in the
  home config, never in the repository.
- The workspace layer is **optional** (P29): it sits inside the repo and is
  git-ignored, so a repo-level cleanup can delete it. Its absence is a
  normal state and is **not** an uninitialized-environment condition —
  `aic` checks the machine layer only for the first-run prompt
  (2026-09-28 fix, see `reports/MAINTENANCE-2026-09-28.md`).
- Workspace-scoped keys (`bugfix.mode`, `layers`) stay in the workspace
  `config/environments/{env}.yaml` — do not move them to the home config
  (cross-platform drift).
- Full provisioning（metrics baseline / 审计等仍属完整 `setup`）；
  但**目录骨架与外部仓库引导自 P36 起由 `env-init` 一并补齐**（幂等、非破坏）
  —— 2026-09-21 外部盲检 T6a C7 同步文档
  config-focused only.
