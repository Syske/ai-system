# AI System — Setup on a New Machine

> 2026-09-10 起无打包命令：`tools/pack.py` 已移除，ai-system 以 **git 远端为备份/迁移载体**（clone + `pip install -e`）。本文档为迁移后的机器安装步骤。

## What's Here

ai-system/ — the full AI Runtime Engine (workflows, skills, governance, CLI)

## Post-Migration Steps

1. Configure the **machine layer** — `~/.config/ai-system/env.yaml` (outside the repo; generated
   on first run by `tools/setup.py`, per platform):
   - workspace.root — absolute path to the new workspace root
   - build.java_home / build.maven_home / build.maven_settings — local tool paths

   The repo-side `ai-system/config/environments/local.yaml.template` is the **optional workspace
   layer** (legacy/compat): its absence is normal and it must never hold machine-level keys — it
   sits inside the repo and is git-ignored, so a repo-level cleanup can delete it.

2. Create or rebuild the projects/ junction:
     mklink /J projects D:\path\to\code-repositories

3. Run python ai-system/tools/path-audit.py to verify all paths resolve

4. Install Python dependencies and register the CLI:
     cd ai-system
     pip install -e .    # editable install; `aic` command available after

5. Verify:
     aic --help          # positional: aic <workflow>
     aic                 # interactive wizard (no arguments)
     python3 tools/path-audit.py

## 迁移载体（2026-09-10 起）

- 克隆 git 远端（github.com:Syske/ai-system）到目标机器，`cd ai-system && pip install -e .`
  即可获得完整引擎；不再生成/拷贝 zip 迁移包（原 `tools/pack.py` 移除，git 远端即备份）。
- `workspaces/` 与工作区级产物不入库，随项目工作区各自维护。
