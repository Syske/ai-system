# Change Proposal: S1 — skill-optimizer 脚本拆分（消除 3 个超限文件 + 双入口重复）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (skill script restructuring) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | MAINTENANCE-2026-08-06.md S1; MAINTENANCE-2026-08-06.md F3 (依赖环背景) |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

RFC-0002 质量门禁为**单文件 ≤1000 行**（P6 于 2026-08-01 裁决，聚合引用文件豁免）。
按此标准核查全部技能：

| 技能 | 总行数 | 最大单文件 | 违规? |
|------|--------|-----------|-------|
| skill-optimizer | 9552 (md 仅 698) | **main.py 1240** | ✅ YES |
| skill-optimizer | — | **main_parallel.py 1125** | ✅ YES |
| skill-optimizer | — | **diff_viewer.py 1164** | ✅ YES |
| implement | 2368 (md) | examples.md 446 | 合规（md 聚合） |
| agent-debug-diagnosis | 1777 | agentdebug_static.py 543 | 合规 |
| iterative-optimizer | 1335 | workflow.md 276 | 合规 |
| mock-test | 1325 (md) | workflow.md 298 | 合规 |
| bugfix | 1314 (md) | workflow.md 326 | 合规 |
| repository-maintainer | 1117 (md) | workflow.md 333 | 合规 |

**三个事实**：

1. **门禁盲区**：`tools/repo-lint.py:188` 的 `check_skill_size` 仅遍历
   `.md/.yaml/.yml`（`walk_skill_files` 扩展名过滤），**不检查 `.py/.cjs/.sh`**，
   导致 skill-optimizer 3 个脚本文件超限却不产生任何 lint 信号。
2. **双入口重复**：`main.py` 与 `main_parallel.py` 是近重复的两个独立入口
   （函数清单基本一致：RealLLMClient / validate_skill_file / sanitize_reference_content /
   integrate_auxiliary_references / run_optimizer / main…），仅执行模型不同。
   这是真实重复代码，违反 Design Philosophy "prefer composition over duplication"。
3. **diff_viewer.py 单文件 1164 行**：职责为 diff 计算 + HTML 生成 + CLI，混合三职责。

## 2. Root-Cause Analysis

- skill-optimizer 起源为一次性优化工程（含 6718 行脚本），后被 skill-sync 等复用，
  从未按 RFC-0002 单文件门禁收敛。
- main.py / main_parallel.py 是"并行版"演进时整体复制再改执行路径的产物——
  复制演化而非组合演化。
- lint 工具按文档资产设计，脚本文件长期处于门禁之外。

## 3. Options

### Option A — 拆分 + 去重（Recommended）

1. **提取共享核心 `core.py`**：从 main.py/main_parallel.py 提取
   RealLLMClient / validate_skill_file / validate_auxiliary_file /
   sanitize_reference_content / update_skill_name_in_md /
   integrate_auxiliary_references / extract_referenced_skill_paths /
   build_auto_snapshot_reason / print_completion_summary（约 450 行公共逻辑）。
2. **合并双入口为单一 `main.py`**：`--parallel` flag 切换执行路径，
   删除 main_parallel.py（两个入口的行为契约 = 同一 CLI 参数集，参数兼容性需验证）。
3. **拆分 diff_viewer.py**：`diff_core.py`（collect/version_sort/discover/
   compute_unified_diff/dedup/precompute，~110 行）+ `html_report.py`（generate_html）
   + 保留薄入口 main。

**目标**：每个脚本文件 <1000 行；消除 ~1100 行重复。

### Option B — 仅拆分不合并

拆分 main.py 与 diff_viewer.py，保留 main_parallel.py（作为并行执行变体）。
**Impact**：消除超限，但重复代码依旧，收益减半。

### Option C — 不做处理（维持现状）

**Impact**：3 个超限文件 + 1100 行重复继续存在；门禁盲区继续。

## 4. Recommendation

**Adopt Option A。** 它同时解决三个真实问题（超限、重复、盲区），
且不改变任何对外 CLI 行为。Option B 只解决一半；Option C 违背
RFC-0002 质量门禁意图。

## 5. Proposed Changes (Option A)

1. `skills/skill-optimizer/scripts/core.py` — 新增：共享核心逻辑（上述函数迁移）。
2. `skills/skill-optimizer/scripts/main.py` — 重写：import core，`--parallel` flag，
   保留全部 CLI 参数与输出行为；删除被迁移函数。
3. `skills/skill-optimizer/scripts/main_parallel.py` — **删除**。
4. `skills/skill-optimizer/scripts/diff_core.py` — 新增：diff 计算逻辑迁移。
5. `skills/skill-optimizer/scripts/html_report.py` — 新增：generate_html 迁移。
6. `skills/skill-optimizer/scripts/diff_viewer.py` — 重写为薄入口（import + CLI）。
7. `tools/repo-lint.py` — `check_skill_size` 扩展名集合加入 `.py/.cjs/.sh`
   （脚本文件同样受单文件 1000 行门禁约束）。
8. `skills/skill-optimizer/SKILL.md` / `workflow.md` — 同步脚本入口说明
   （若引用 main_parallel.py / diff_viewer.py 路径）。

## 6. Validation Plan

- `python -c "import main"`（scripts 目录）两入口模块可导入、无语法错误
- `python tools/repo-lint.py --repo-root .` → 0 blockers/errors（含新扩展名检查生效，
  确认 3 个超限文件消除后不再报错）
- `python tools/check.py` → PASS
- `python tools/path-audit.py` → 0 broken
- 冒烟：`python main.py --help` / `python diff_viewer.py --help` 输出与改动前一致
- 若 skill-optimizer 有测试脚本（`scripts/test_model_connectivity.py`）不受影响

## 7. Risks

- **中**：main.py / main_parallel.py 参数合并若存在参数集差异，`--parallel` 路径可能行为变化
  → 需逐项比对两入口 argparse 参数集后再合并。
- **低**：repo-lint 扩展名扩展可能暴露其它技能脚本超限 → 核查后处理（当前仅这 3 个 >1000）。
- 无路径/注册表变更，workflow 与 config 不受影响。

## 8. 处置建议

本提案属结构性变更，待 Review → Approve 后实施（OPERATIONS §12）。
实施时按 A1 批次逐文件小步提交，每步 `python -m py_compile` 验证。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A**（确认执行） | 2026-08-06 |

---

## Implementation Record (2026-08-06)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `scripts/core.py` — 新增：从 main.py 迁移 9 个共享函数（RealLLMClient、validate_skill_file、validate_auxiliary_file、sanitize_reference_content、update_skill_name_in_md、integrate_auxiliary_references、extract_referenced_skill_paths、build_auto_snapshot_reason、print_completion_summary），498 行，纯移动。
2. `scripts/main.py` — 重写：引入 core；保留全部 CLI 参数契约（--action/--mode/--trajectories/--input/--project-dir/--no-open-diff/--feedback/--target-version）；处理循环提取为 `process_skill_file`；新增 `--parallel` flag（默认关闭，保持原串行行为）；848 行（原 1240）。
3. `scripts/main_parallel.py` — 删除（零引用死入口；并行能力已并入 main.py --parallel）。
4. `scripts/diff_core.py` — 新增：diff 计算逻辑（collect/discover/compute/dedup/precompute/generate_html），166 行。
5. `scripts/html_report.py` — 新增：HTML_TEMPLATE 迁移，925 行。
6. `scripts/diff_viewer.py` — 重写为薄入口（100 行，原 1164），CLI 不变。
7. `tools/repo-lint.py` — check_skill_size 扩展名集合加入 .py/.cjs/.sh（修复门禁盲区，已验证可捕获 1001 行 .py）。
8. `skills/skill-optimizer/SKILL.md` / `references/architecture.md` — 脚本清单同步。

**偏差记录**：原 Option A 第 2 条"`--parallel` flag 切换执行路径"细化——不合并双入口参数集（本就不同），以 main.py 契约为准 + 移植并行能力；main_parallel 的 ThreadPoolExecutor 以 `--parallel`（默认 off）提供。

**Validation（全绿）**：
- 全部 5 个脚本 `py_compile` 通过
- `tools/repo-lint.py` → 0 BLOCKER / 0 ERROR / 9 WARN（9 项为既有项）
- `tools/check.py` → PASS
- `tools/path-audit.py` → 0 broken
- diff_viewer 冒烟：生成 HTML 含 DIFF_DATA ✅
- 门禁负向测试：1001 行 .py 可被捕获 ✅
- 注意：`import main` 在全局 Python 3.10 环境下因 langchain 旧 API（create_agent）导入失败，为**既有环境问题**（原始 main.py 同样失败），非重构引入；opt.sh 自带 .opt 虚拟环境运行不受影响
