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

### 5.1 规则子集建议（从 A 层 7 项 + 团队现状提炼，~20 条，severity 分级）

| 检查 | 级别 | 备注 |
|---|---|---|
| `UnusedImports` / `AvoidStarImport` | error | 与 C2 removeUnusedImports 互补（imports 规范） |
| `MethodName` / `TypeName` / `ParameterName` / `LocalVariableName` | error | 驼峰；存量例外用泛化（如 `s->` 单字母在 lambda 由 SuppressWarnings 覆盖可改用 `FinalParameters=off`） |
| `AbbreviationAsWordInName` | warn | 存量缩写多（DTO/VO/API），先 warn 后收紧 |
| `JavadocType`（public 类） / `JavadocMethod`（public 方法，允许缺省报告） | warn | 团队已有 Javadoc 习惯（A 层单行 Javadoc 检查互补：此处查结构不查格式） |
| `LineLength`（120，非 import/package） | error | 与 profile lineSplit=120 对齐 |
| `EmptyLineSeparator`（package/import/类型/方法间） | warn | 空行结构；存量多不合，从 warn 起步 |
| `EqualsHashCode` / `DefaultComesLast` / `NeedBraces`（if/else/for/while 多语句） | error | 低争议正确性类 |
| `CyclomaticComplexity`（阈值 20） | warn | 仅报告不拦（消化道） |
| `MagicNumber` | 不开 | 业务常量多，误报高；A 层不覆盖 |
| `CustomImportOrder` / `AvoidInlineConditionals` / `FinalLocalVariable` | 不开 | 与团队现状冲突或收益低 |

> 原则：**先基线后收紧**——以 severity 分级起步（error=正确性类、warn=风格类），
> 运行 1-2 周收集真实违反分布后再决定具体项升级。规则集与存量对齐优先（A 层 format-check
> 同类检查保留，不重复拦截）。

### 5.2 CLI 承载示例（零业务仓配置）

```bash
# 规则/jar 由主链或 CI 脚本持有（checkstyle VERSION 选稳定版，company maven 镜像可拉）
java -cp checkstyle-<V>-all.jar com.puppycrawl.tools.checkstyle.Main \
    -c checkstyle.xml -p suppressions.xml <repo>/src  # 存量超限用 suppressions 白名单
```

- `suppressions.xml`：baseline 阶段对已知违反（行级/文件级）临时抑制，随治理进度逐步移除
- 与 format-baseline 同批：先格式基线（token 校验零逻辑），再规范基线（suppress 存量）

### 5.3 集成点

- CI/发布链脚本步骤（不改 pom）；主链 evaluate：develop gate 可选跑 Checkstyle（warn 收集）
- 报告：拒绝/警告计数进 review/verify 检查项（与 C2 对齐）
- 归属：仍为 Business-side recommendation；规则集 XML 初稿可在 ai-system 侧起草待业务确认

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
- ai-system 侧工具链已入库（c7eef0b profile 定稿 / b5e9f70 边界机制 / ef8cdf3 规则集修订 / b095ebc 存量抑制工作流）

## 9. 试点执行单（业务侧落地）

> 试点仓建议 **platform-api**（预演/C2 实测数据现成）；主干 master 执行；全程零 pom 改动。

### Step 0 拍板（业务侧，30 分钟）
- [ ] 确认目标风格 = 已定稿 profile（IDEA 默认系 375 条，4 空格/120）与规则集（error=正确性/warn=风格）
- [ ] 确认试点仓（platform-api）+ 试点窗口（建议 1-2 周）
- [ ] 确认门禁接入位置：先本地/命令自检（观察期）还是直接 CI（若 CI 可加脚本步骤）

### Step 1 C2 格式基线（master，约 1 小时）
```bash
# 在 master（非任务分支）且 worktree 干净
python3 ~/ws/ai-workspace/ai-system/tools/format-baseline.py <platform-api>
# 脚本自校验：token 级零变化（log 中「token 级不一致 0」）→ 通过
# 人工抽审 5-10 个 diff 文件 → 独立 style: 提交（可整体 revert）
# 完成后：git log 保留独立 style 提交；任务分支 rebase 后 continue
```

### Step 2 Checkstyle 存量抑制（master 同基线，约 30 分钟）
```bash
JAVA=~/.local/jre17/bin/java; JAR=~/.local/lib/checkstyle/checkstyle-10.23.0-all.jar
XML=~/ws/ai-workspace/ai-system/tools/checkstyle/checkstyle.xml
$JAVA -jar $JAR -g -o suppressions.xml -c $XML <platform-api>/src   # 生成 XPath baseline
# suppressions.xml + checkstyle.xml 放仓根（非构建配置，CLI 引用）
$JAVA -jar $JAR -c $XML <platform-api>/src     # 观察期自检：期望 0 违反（存量全抑制）
# 挂载：checkstyle.xml 的 TreeWalker 内加 SuppressionXpathFilter（file=仓内 suppressions.xml 或参数化）
```

### Step 3 门禁接入与观察（1-2 周）
- [ ] 主链 develop gate：C2 `format-jdt-gate --check`（可选精确门禁，基线后 differ=0）
- [ ] 新代码自检命令（供开发者）：`$JAVA -jar $JAR -c $XML -x '' <改动文件>`（增量范围）
- [ ] 收集误报/规则争议 → 微调 checkstyle.xml（反馈闭环）
- [ ] 验收指标：新改动无新增违反 & C2 0 differ & 误报率低

### Step 4 铺开（试点通过后）
- [ ] user-center-api / bs-integration / cmdb-api + security 两仓（knowledge-api / resource-manager）同流程
- [ ] CI（若允许）加脚本步骤：C2 check + checkstyle（存量抑制后的新违反阻断）

### Step 5 回滚
- style 提交：`git revert <style-commit>`（全仓还原一行）
- 门禁：移除 CI 步骤 / 关闭 develop gate 开关即可（零残留配置）

### 职责分工
- 业务侧：拍板/窗口/门禁位置/误报反馈/最终铺开
- AI 侧（可代跑 Step 1-2，已在 platform-api 实测过两阶段）
- 工具资产：ai-system tools（format-baseline/format-jdt-gate/checkstyle）+ 机器级 ~/.local（jar/JRE17）