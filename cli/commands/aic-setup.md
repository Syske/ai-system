---
description: 初始化 AI 系统环境 - 生成环境配置、脚手架目录、链接代码仓库
---

初始化或重建 AI 系统运行环境：环境配置、工作区基础目录、代码仓库链接与路径校验。

**输入**：可选 Workspace Root（工作区根目录，默认 `ai-system` 父目录）；可选 Environment（默认 `local`）。

**步骤**

1. **确认当前目录**：必须是 ai-system 根目录（存在 `tools/setup.py`）。

2. **执行初始化**

   ```bash
   python tools/setup.py [--workspace "<workspace root>"] [--environment <name>]
   ```

   - 未提供 Workspace Root → 不加 `--workspace`（默认 `ai-system` 父目录）
   - 交互式填写 `build.java_home` / `build.maven_home` / `build.maven_settings`

3. **核对生成结果**

   - `config/environments/{environment}.yaml` 已生成，`workspace.root` / `repository_root` 正确
   - `workspaces/`、`projects/`、`repositories/`、`methodologies/` 目录已就绪
   - 代码仓库已链接进 `projects/`（junction / symlink），无 `.git` 等标记的目录已确认或跳过
   - `tools/path-audit.py` 校验通过，无 BLOCKER

4. **收尾**

   - 未安装 CLI 时执行 `pip install -e .`
   - 汇报环境上下文（workspace_root、repository_root、各层路径）与后续入口（`aic`）

**输出**

## Setup Report

- 环境配置路径与关键字段
- 目录脚手架结果（新建/已存在）
- 仓库链接清单（已链接 / 跳过及原因）
- 校验结果

**护栏**

- 非破坏性：只创建缺失的目录与链接，绝不删除源文件、不覆盖已有 `local.yaml`、不移动已有仓库
- 敏感路径（java_home / maven）确认后再写入配置
- 链接目标必须是目录，不得指向外部敏感位置
