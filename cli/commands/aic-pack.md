---
description: 打包 AI 系统 - 生成迁移包（tools/pack.py）
---

Pack the current ai-system directory for migration to a new machine. The artifact contains the complete runtime engine and migration checklist.

**Inputs**: Optional Output Directory (target dir, default `../ai-system-pack`); optional Zip (`yes` = generate .zip and remove the temp dir).

**Steps**

1. **Confirm location**: Current directory must be the ai-system root (contains `tools/pack.py`).

2. **Run packaging**

   ```bash
   python3 tools/pack.py [--output "<output directory>"] [--zip]
   ```

   - No Output Directory → omit `--output` (default `../ai-system-pack`)
   - Zip = `yes` → append `--zip`
   - Append `--with-reports` / `--with-methodologies` as needed, after confirmation

3. **Verify artifacts**

   - Target dir contains `ai-system/` with `README_MIGRATION.md`
   - `config/environments/local.yaml` saved as `local.yaml.template`
   - No `node_modules` / `__pycache__` / `*.pyc` mixed in

4. **Report**: migration package path, file/dir statistics, new-machine landing steps (fill absolute path of `local.yaml.template`, recreate `projects/` junction, `pip install -e .`).

**Output**

## Pack Report

- 迁移包路径与统计
- 校验结果（逐项通过/失败）
- 新机器落地清单

**Guardrails**

- Packing only copies, never deletes source files
- Sensitive/absolute-path content (local.yaml) must be preserved as `.template`, never packed as-is
- Large dirs (node_modules, archived/ai-runtime/opencode/node_modules) must be excluded
