# Change Proposal: P60 — 门禁自校验（Gate Self-Verification）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (tool gates + standards) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | `reports/EXTERNAL-BLIND-REVIEW-2026-09-21.md`（持久记录；本次运行原始产出未入库）+ 用户指示立项 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

本次外部盲检（独立第三方模型双评委）暴露出一类**系统性缺陷：门禁/守卫自身静默失效，且没有任何机制能发现它**。共 5 例同族：

| # | 失效的门禁 | 实测表现 | 内部门禁是否可见 |
|---|---|---|---|
| 1 | 测试收集（unittest 约定） | 5 个 `def test_` 定义在模块级 `if __name__ == "__main__":` 块内 → **永不定义、永不收集**（声明 336 / 收集 331） | ❌ 全不可见（unittest/check.py/repo-lint 均无信号） |
| 2 | `tools/repo-lint.py` 工作流关键词豁免 | 相邻 raw 字符串拼成 `…Workflow)\\b` → raw 串中 `\\b` 是字面反斜杠 → **该豁免永不匹配**、静默降级 | ❌ 不可见（不报错，只是豁免失效） |
| 3 | `tools/quick-check.py` 严重度采集 | 白名单无 `[BLOCKER]` → **存在 blocker 时 verdict 仍可能 OK** | ❌ 不可见（反而输出"健康"） |
| 4 | `tools/checks/workflow.py` 注册表校验 | 缺 `workflow:`/`runtime:` 键时 `ROOT / ""` == ROOT（目录，`exists()` 恒真）→ **fail-open 静默通过** | ❌ 不可见 |
| 5 | 危险命令守卫（agent-debug-diagnosis） | 外层 `\b` 使 `rm -rf /` 分支不可达 → **最危险模式漏检** | ❌ 不可见（安全守卫无声失效） |

另有 1 例相邻类：`skills/open-cli/SKILL.md` 引用 `./references/CLI-ONESHOT.md` 等**不存在的文件**，
`path-audit` 未报 broken（其路径正则只锚定仓库顶层目录名，技能内相对引用不在覆盖范围）。

（上述 1–5 与 open-cli 已在 2026-09-21 批次修复：`5da9f1c` `e30113e` `f8c984a` `1eafe15`；
**本提案解决的是"如何防止同类再次发生"**，不是修复本身。）

## 2. Root-Cause

1. **无元校验（meta-verification）**：现有门禁检查"被检查对象"，但没有任何门禁检查"门禁自己是否还在工作"。
2. **声明式规则无自测**：正则、白名单、键名这类规则写错即静默失效——运行时不报错，日志不留痕，只有"该报的没报"。
3. **"声明 vs 生效"之间缺一致性校验**：测试的"写出来"与"被收集"是两个世界，二者从未比对。
4. **路径审计的锚定假设**：`path-audit` 只解析以仓库顶层目录（`governance/`、`tools/` 等）开头的引用，
   技能内相对引用（`./references/x.md`）需要以技能目录为基准解析，当前无此行。

## 3. Options

| 选项 | 说明 | 成本 | 覆盖 |
|---|---|---|---|
| **A. 维持现状（仅本次修复）** | 不加门禁 | 0 | 同类缺陷必然复发（本次已 5 例同族） |
| **B. 三条具体校验（推荐）** | ① 声明 vs 收集测试数一致性 ② 关键声明式规则正反例自测 ③ 技能内相对引用存在性 | 低（分别落在既有 `check.py` / 单测 / `path-audit` 内） | 覆盖本次全部已知失效形态 |
| C. 通用"门禁自测框架" | 每条规则强制正反例 + 覆盖率度量 | 高 | 最彻底，但易过度工程、拖慢每次提交 |

## 4. Recommendation

**采纳 B**。理由：

- 三条校验各自都是**小改**，且都落在**既有门禁**之内（不新增运行时层、不引入反向依赖）；
- 命中的是本次**全部**已知失效形态（覆盖 5/5 + open-cli 1 例），且都是"能防御未来同类"的通用检查；
- 与架构原则一致：能力应落在最低可能层——校验工具属 `tools/`，规则表述属 `governance/standards/`。

同时把一条原则写入标准层：**门禁失效必须响亮**（fail loud）——任何校验规则的"未命中/未生效"
都应能被另一条检查发现，禁止静默降级。

## 5. Proposed Changes

1. **声明 vs 收集测试数校验**（新增 `tools/checks/tests_collected.py`，接线 `tools/checks/__init__.py` + `tools/check.py`）
   - 逐 `cli/tests/test_*.py`：`^\s*def test_` 声明数 vs `unittest` 收集数，不一致 → **ERROR**
   - 额外检出"模块级 `if __name__` 块内定义测试方法"形态 → **ERROR**（根因形态，直接定位）
   - 输出可比数字（声明/收集/差异），异常时列出未收集方法名
2. **关键声明式规则正反例自测**（补入 `cli/tests/`）
   - `repo-lint` 工作流关键词豁免：`Purpose:`/`Workflow`/`Runtime` 命中，`# Purpose`/`not-a-keyword` 不命中
   - `quick-check` 严重度采集：`[BLOCKER]`/`[ERROR]` 计为 findings、`[WARNING ]` 仅计数（T4 已部分覆盖，需补齐并登记"关键规则清单"）
   - 危险命令守卫：正例（`rm -rf /`、`rm -rf /tmp`、`git push --force`…）+ 负例（`ls -la`、`xmkfs`）
3. **技能内相对引用存在性**（扩展 `tools/path-audit.py`）
   - 以技能目录为基准解析 `./x`、`x/y.md` 形态的引用（如 `SKILL.md` 里的 `./references/*.md`）
   - 缺失 → broken；保持既有 placeholders / known-debt 机制以抑制误报
4. **标准层**：在 `governance/standards/`（或 `governance/repo-lint.md` 增一节）写明
   "门禁失效必须响亮 + 声明式规则需正反例 + 声明与生效需一致性校验"
5. 索引登记：`reports/PROPOSALS.md` + `reports/README.md`

## 6. Validation Plan

- 三条各做**"故意制造缺陷 → 门禁必须报"**的实证：
  - ① 在临时副本里把某个 `def test_` 移入 `if __name__` 块 → 校验报 ERROR 且列出方法名
  - ② 把豁免正则改回 `\\b` → 自测失败；把白名单改回 `[WARN]` → 采集自测失败
  - ③ 删除 `skills/open-cli/references/` 下的被引用文件 → path-audit 报 broken
- 恢复后：全量单测 + `check.py` + `repo-lint` + `path-audit` + `quick-check` 全绿、无新增 WARN
- 与既有门禁不冲突：新增校验只增 ERROR/统计，不改既有严重度语义

## 7. Risks

| 风险 | 缓解 |
|---|---|
| ① 被误读为"测试数量崇拜" | 校验的是**声明与收集的一致性**，不是数量阈值；数量本身不作判据 |
| ② 相对引用解析引入误报 | 沿用现有 placeholders 与 known-debt 机制；先以 WARN 观察一个周期再升级 ERROR（可调） |
| ③ 新增检查拖慢每次提交 | ①③ 均为纯静态扫描（毫秒级）；② 属单测，随既有套件运行 |
| ④ 校验自身又写错 | 每条校验都带正反例自测（本条即"自校验"原则的落地） |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户于 2026-09-21 指示立项） | 2026-09-21 |