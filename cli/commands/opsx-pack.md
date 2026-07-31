---
description: 打包 AI 系统 - 生成迁移包（tools/pack.py）
---

打包当前 ai-system 目录以便迁移到新机器，产物包含完整的运行时引擎与迁移清单。

**输入**：可选 Output Directory（目标目录，默认 `../ai-system-pack`）；可选 Zip（`yes` = 生成 .zip 并删除临时目录）。

**步骤**

1. **确认位置**：当前目录必须是 ai-system 根目录（存在 `tools/pack.py`）。

2. **执行打包**

   ```bash
   python tools/pack.py [--output "<output directory>"] [--zip]
   ```

   - 未提供 Output Directory → 不加 `--output`（默认 `../ai-system-pack`）
   - Zip 为 `yes` → 追加 `--zip`
   - 按需追加 `--with-reports` / `--with-methodologies`，先确认再执行

3. **校验产物**

   - 目标目录生成 `ai-system/` 且含 `README_MIGRATION.md`
   - `config/environments/local.yaml` 已保存为 `local.yaml.template`
   - 无 `node_modules` / `__pycache__` / `*.pyc` 混入

4. **汇报**：迁移包路径、文件/目录统计、新机器落地步骤（填 `local.yaml.template` 绝对路径、重建 `projects/` junction、`pip install -e .`）。

**输出**

## Pack Report

- 迁移包路径与统计
- 校验结果（逐项通过/失败）
- 新机器落地清单

**护栏**

- 打包只复制，绝不删除源文件
- 敏感/绝对路径内容（local.yaml）必须以 `.template` 保留，不得原样打包
- 大目录（node_modules、archived/ai-runtime/opencode/node_modules）必须排除
