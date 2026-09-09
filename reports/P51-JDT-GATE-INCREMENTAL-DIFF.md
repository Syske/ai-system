# Change Proposal: P51 — format-jdt-gate 增量差分语义（hunk × 改动行交集）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Tools（format-jdt-gate 增量语义增强，C2 门禁） |
| Author | AI Maintainer |
| Created | 2026-09-09 |
| Reference | T-011 dev run（develop-20260909-105848.md：MigrationValidateFacadeImpl.java HEAD 独立跑亦 differ=49，本次 4 处 diff hunk 全为存量换行风格，手工甄别后放行）；maintain-jdt-gate-20260902（1010/1690 文件 differ，profile 校准前仅作体检）；09-05 格式债基线登记（format-check --changed 增量语义复验通过：存量豁免 + 新增拦截）；用户决策 2026-09-09（P51 立档） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

C2（format-jdt-gate）`--changed` 现语义为「git status 有改动 .java → **整文件全量扫描**」。存量格式债文件一旦被本次改动触碰，门禁仍报该文件**全部** diff（含未触碰的存量差异），无法区分「本次新增的 diff」与「既有的基线 diff」：

- T-011：`MigrationValidateFacadeImpl.java` HEAD 独立跑 JDT 亦 differ=49；本次改动后 4 处 diff hunk 均为存量换行风格——**靠人工逐 hunk 甄别**才确认非新增、保留原风格放行。
- C2 校准前真实 worktree 1010/1690 文件 differ（110652 行），存量债常态化；**每改一个存量债文件都要人工做 hunk 归属甄别**，重复劳动且易漏/易误判（放行了真新增、或误拦了存量）。

对比：`format-check.py --changed` 已有成熟增量语义（09-05 复验：存量仓无改动 PASS、新增行精确拦截、存量豁免 + 新增拦截机制成立）。C2 缺同一能力。

## 2. Root-Cause

- JDT wrapper 按**整文件**格式化并统计 differ/diffLines，**不输出差异行归属**（仅 `--dump-dir` 写 formatted 文件，无行号级 unified diff）。
- 门禁只做「文件有 diff → 报」，未与「本 change 实际改动行」求交——存量债文件与新增行混在同一份 diff 里。

## 3. Options

| 选项 | 内容 | 评估 |
|---|---|---|
| **A（推荐）** | **hunk × 改动行交集**：对改动文件 `--dump-dir` 输出 formatted → `git diff -w` 对比工作区源取 hunks → 与本 change 实际改动行（`git diff` 工作区/暂存）求交集——存量 hunk 豁免（基线，记录摘要），仅新增行命中 diff 拦截 | 粒度最准（行级），对齐 format-check 先例；存量豁免 + 新增拦截 |
| B | known-ignore 基线文件（清单列存量债文件，改动时整文件跳过） | 简单，但**整文件豁免**——同一文件的新增行也不拦，漏检 |
| C | 文件级基线快照（存每文件 baseline differ 数，改动后比较增量） | 粒度中，需维护快照且无法定位「哪一行是新增」，实现复杂 |

## 4. Recommendation

**方案 A（hunk × 改动行交集）**。理由：① 行级精度是「存量豁免 + 新增拦截」成立的前提；② 复用 format-check 的改动行提取成熟逻辑，无新机制；③ 与 C2 profile 校准（业务侧 IDEA 导出）**并行**——P51 是工具语义，校准是业务侧数据；校准前 C2 保持体检定位、不转硬门禁（对齐既有风险处置）。

## 5. Proposed Changes

1. `tools/format-jdt-gate.py`：`--changed` 增强——对改动文件清单内的文件：
   - `--dump-dir` 输出 formatted 结果；
   - `git diff -w`（源 vs dumped）解析 hunks（行范围）；
   - `git diff`（工作区 + 暂存，即 HEAD 对比）取实际改动行范围；
   - 求交集：新增行命中 → WARN/FAIL；纯存量 hunk → PASS 并记录「存量基线摘要」（differ=N 中 M 行为存量）到诊断日志。
2. 门禁语义保持 exit 0/1/2/3 不变；`--check-commit` 对齐 format-check（提交后 subject 校验）。
3. `templates/runtime/runtime-develop.md` C2 gate 描述同步：增量语义 + 存量豁免说明（一行）。
4. `cli/tests/test_format_jdt_gate.py` 新增用例：纯存量文件改动（应 PASS）、新增行命中（应 WARN/FAIL）、混合场景、非 git 回退。

## 6. Validation Plan

- 单测：构造存量 diff 文件、新增行命中、混合、非 git 四类场景，断言 exit 映射正确。
- 回放：T-011 场景——对含 4 处存量换行 hunk 的改动跑 `--changed`，应 PASS（存量豁免）且诊断日志含基线摘要。
- 门禁：check.py / repo-lint / path-audit 全绿；unittest 全量跑。
- 校准前回归：存量仓无改动 → PASS（不因新增逻辑误报）；新增行 → 精确拦截。

## 7. Risks

- **dump 与 git diff -w 等价性**：JDT 输出与源可能仅换行/空白差异——用 `-w` 忽略空白归并。
- **改动行范围准确性**：未提交 + 已暂存混合态——统一以 `git diff HEAD`（工作区+暂存）取范围。
- **误放行**：新增行恰好落在存量 hunk 内——交集按**行级**判定（非 hunk 级），新增行必被识别。
- **增量口径的语义回归**：`--changed` 从「有改动全量扫」改为「hunk 交集」，与既有存量债登记（09-05）的「门禁 --changed 增量语义」表述需核对一致。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（确认方案 A：hunk × 改动行交集） | 2026-09-09 |

---

## Implementation Record (2026-09-09)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `tools/format-jdt-gate.py`：新增 `_parse_hunk_ranges` / `_changed_line_ranges` / `_jdt_diff_hunks` / `_overlaps` / `dry_run_incremental`（hunk × 改动行交集：存量豁免 BASELINE + 新增拦截 NEW-DIFF，退出码按新增差异文件数映射）；`dry_run` 增 `--dump-dir` 透传；`--changed` 路由到增量差分（非 apply 时），`--changed --apply` 仅对改动文件写回；`--changed` 描述更新。
2. `cli/tests/test_format_jdt_gate.py`：新增 9 用例（hunk 解析 / 交集 / 改动行范围 3 态 / 增量出口映射 4 态）。
3. `templates/runtime/runtime-develop.md` C2 gate 描述同步（增量语义 + 存量豁免）；`tools/README.md` 登记。

**L1 偏差（实施修正，均已核）**：
- **去除 `-w`**（提案原述 git diff -w）：缩进/空白是格式债主类，`-w` 会滤掉全部缩进 hunks 使门禁失效；行级交集判定已防存量噪音误拦，无需 `-w`。
- **未加 `--check-commit`**（提案 §5.2）：format-check-a（必查）已独占提交 subject 校验，C2（可选）重复属违反 Single Source of Truth。
- **修复潜伏 bug**：`_changed_java_files` 原返回仓库根相对路径，src_dir≠仓库根时 `--files-file`/dump 全部解析失败（files=0）——已归一化为 src_dir 相对（真实回放暴露并修复）。

**Validation**：unittest 251 OK（+9）；真实回放 4 场景全对——① 纯存量豁免 PASS(0) ② 新文件违规 NEW-DIFF WARN(1) ③ 真实新增违规拦截(1) ④ 混合（存量豁免 + 新文件拦截）；repo-lint 0/0/26；path-audit OK；check.py PASS（3 已知 WARN）。
