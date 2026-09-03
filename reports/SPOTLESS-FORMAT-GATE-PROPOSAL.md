# 业务仓 Java 格式与规范治理建议（CLI 路线版，v2 2026-09-03）

> 类型：业务仓改进建议（非 ai-system 变更提案，不进 PROPOSALS.md）
> 日期：v1 2026-09-02（Maven Spotless 路线）/ v2 2026-09-03（**用户裁定不改项目 pom → 改 CLI 路线**）
> 关联：env-google-java-format-20260902（卸载 gjf/停用 pi-lens）；A 层 format-check.py；C2 format-jdt-gate（profile 已校准）

---

## 1. 决策链（v1 → v2）

- 2026-09-02：google-java-format 与项目 4 空格约定不可调和 → 卸载 + 格式化改工作流校验。
- v1（Spotless）：建议 `spotless-maven-plugin` + eclipse formatter 作业务仓机械闸门。
- **2026-09-03 修正**：用户裁定**业务仓不改 pom** → Maven 插件路线作废；
  同时 C2（eclipse JDT 干跑）profile 已完成校准（团队 IDEA 默认系展开 375 条目，
  platform-api 实测 apply 后 check 0 差异）→ **格式基线/门禁全部由主链 CLI 承载**，
  业务仓零构建配置。

## 2. 方案对比（终版）

| 方案 | 业务仓改动 | 强校验 | 状态 |
|---|---|---|---|
| ~~Spotless maven 插件~~ | 改 pom（否决） | — | 作废（用户裁定） |
| **CLI 路线（采纳）**：`format-jdt-gate.py <src> --apply/--check` + eclipse-format.xml（同源 375 条目） | **零配置** | ✅ 精确格式化（JDT 干跑） | 已交付 + 校准定稿（c7eef0b/b5e9f70） |
| Checkstyle（CLI）——规范闸门（候选） | 零配置（规则文件 + jar 由主链/CI 调用） | ✅ 命名/Javadoc/imports/复杂度 | 候选中（与 C2 同批评估） |
| A 层 format-check.py | 零配置 | 软约束（规范泄漏快检） | 已接入 develop gate |

## 3. 校准结论（C2，2026-09-03）

- **profile**：`ai-system/tools/jdt-format-gate/eclipse-format.xml` = 团队 IDEA 默认系展开（375 条目，tab=space/4、lineSplit=120）
- **实测**（platform-api worktree，1690 文件）：`--apply` 721 文件 26s；`git diff -w` + token 级对比 = 零逻辑改动；apply 后 check **0 差异**
- **边界**：`known-ignore.txt` 登记 1 个无 fixpoint 文件（eclipse formatter 对合振荡，EnterpriseProvider.java）；门禁按「排除后 0」判定
- **apply 语义**：迭代至 fixpoint（最多 5 轮）保证 writeback 干净；安全校验 = `git diff -w --numstat` 非零=0

## 4. 业务仓格式基线执行方案（待业务侧拍板，一行命令级）

1. 试点仓（建议 platform-api）**主干（master，非任务分支）**：
   ```bash
   python3 ai-system/tools/format-jdt-gate.py <repo>/src --apply --ignore-file <known-ignore.txt>
   git diff -w --numstat | awk '$1+$2>0'   # 应 0（内容零变化证明）
   git status/抽样 diff 人工审 → 独立 `style: apply format baseline（Cool4Space profile）` 提交
   ```
2. 铺开：user-center-api / bs-integration / cmdb-api（security 任务涉及仓可同批）
3. 门禁：CI/发布链脚本调用 `format-jdt-gate.py <src> [--ignore-file]`（不改 pom）；
   主链 develop gate 已接入（可选精确门禁，基线后 differ=0 生效）
4. 日常：开发者 IDEA 按 4 空格；不合规由 check 报告，`--apply` 单文件修

## 5. Checkstyle（规范闸门，候选；若业务侧要）

- 定位：命名/Javadoc/imports/行宽/复杂度等**规范检查**（格式化之后第二道）
- 承载同 CLI：规则文件 `checkstyle.xml`（从存量反推+约定，先 baseline 后收紧）+ jar 由主链/CI 调用，
  **业务仓不改 pom**
- 与 C2 的关系：格式（C2/IDEA 4 空格）+ 规范（Checkstyle）两层；A 层软约束保留作提交前快检
- 建议与 master 基线同批评估（业务侧一块拍板投入）

## 6. 风险与缓解

| 风险 | 缓解 |
|---|---|
| baseline 大 diff（一次 700+ 文件） | 独立 style: 提交可整体 revert；diff -w=0 机器证明 + 抽样人工 |
| 无 fixpoint 边界文件 | known-ignore 名单（先人工 IDEA 格式化再出名单） |
| 业务仓共享仓大提交协作 | 选低流量时段 + 分支先行（style 分支合入 master） |
| CI 改动约束 | 仅加脚本步骤（不改构建配置）；不允则主链环节兜底 |
| 开发者日常不感知 | 定义清楚：IDEA 4 空格手写 → check 兜底 → apply 修复 |

## 7. 结论

CLI 路线已就绪且经验证（零业务仓配置、同源 profile、安全校验齐备）；
**唯一待决 = 业务侧拍板 master baseline 执行与 Checkstyle 是否引入**（可与 spotless v1 尾款一起定性）。

## 8. 登记

- 本建议入 `reports/README.md`（评估与评审报告表，类型=Business-side recommendation / Pending）
- ai-system 侧工具链已入库（c7eef0b profile 定稿 / b5e9f70 边界机制）