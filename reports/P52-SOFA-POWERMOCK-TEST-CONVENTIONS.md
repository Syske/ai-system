# Change Proposal: P52 — SOFA/PowerMock/jacoco 测试兼容性纪律 + 全量回归环境性基线登记

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Standards（spring.md 测试节 + 回归基线附录） |
| Author | AI Maintainer |
| Created | 2026-09-09 |
| Reference | T-011（@Resource 与 domain.Resource 同名 → lombok log 连锁误报）；T-012（jacoco-online × PowerMock 双重插桩 IllegalClassFormatException；离线缺 surefire-junit4:2.22.2 → 参数覆盖；jacoco 重复运行需 clean）；T-013（PowerMock javassist 转换下 Sort.forEach Iterable 默认方法不可解析 → 显式迭代器）；三卡完成报告「过程教训」；用户决策 2026-09-09（P52 立档，弱候选「全量回归环境性基线失败」并入） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

同一项目（security-migration）连续三卡踩入测试框架兼容性坑，且标准/技能层无任何 SOFA/PowerMock/jacoco 指引（grep 实证：governance/standards、skills/java-maven、skills/idea-build 均无），教训以「过程教训」散落各完成报告、无法复用：

- **T-011**：初版 `@Resource`（javax 注入注解）与 `domain.Resource` 实体类**同名冲突** → 连锁 lombok `log` 误报 → 改 `@Autowired` 才通过编译；
- **T-012**：全量回归 jacoco-online × PowerMock **双重插桩冲突** `IllegalClassFormatException`（环境性既有失败）；离线仓库缺 `surefire-junit4:2.22.2` → `-Dmaven-surefire-plugin.version=2.22.1` 参数覆盖；jacoco 0.8.2 插桩后重复运行 test 需 `clean`；
- **T-013**：PowerMock javassist 转换下 `Sort.forEach`（Iterable 默认方法）**不可解析** → 改显式迭代器循环。

另：全量回归的「环境性基线失败」每次靠 `git stash` 基线复跑证明与本次无关（T-012/T-013 均 3 errors，重复甄别）。

## 2. Root-Cause

- 测试框架兼容性知识（同名冲突/双插桩互斥/javassist 限制）无文档化载体——每次踩坑、每次自愈、每次重演。
- 无统一测试环境纪律（离线构建参数覆盖、jacoco clean、WSL 路径）——同问题跨卡重报。
- 环境性基线失败无登记机制——每次回归都要重跑基线证明，成本重复。

## 3. Options

| 选项 | 内容 | 评估 |
|---|---|---|
| **A（推荐）** | spring.md 新增 Test Conventions 节收录 3 实证坑 + 构建/clean 纪律；弱候选「全量回归环境性基线失败登记」并入为附录基线清单 | 单一落点、实证驱动；基线清单免重复 stash 复跑 |
| B | 仅收 3 坑（不含构建/回归基线） | 缺构建纪律与基线机制，T-012 类成本仍重复 |
| C | 新建独立测试纪律文档 | 过重——spring.md 已承载 Spring 系标准，测试节内聚即可 |

## 4. Recommendation

**方案 A**。理由：① 三案同源于 Spring 系测试栈（SOFA/PowerMock/jacoco/javassist），spring.md 是唯一相关标准载体；② 弱候选（回归基线）与测试环境纪律同层，并入避免另立文档；③ 实证驱动，只收录已发生（≥1 次）的坑，不做投机扩充（演进原则）。

## 5. Proposed Changes

1. **`governance/standards/java/spring.md` 新增「## Test Conventions (SOFA/PowerMock)」节**：
   - **同名注入规避**：javax `@Resource` 与实体类同名（如 `domain.Resource`）引发连锁误报 → 注入用 `@Autowired` 或显式限定名；
   - **双插桩互斥**：jacoco-online（`-javaagent` 插桩）与 PowerMock 不同时启用；冲突 `IllegalClassFormatException` → 分跑或 `clean` 后单跑；
   - **javassist 限制**：PowerMock javassist 转换下 Iterable 默认方法（如 `Sort.forEach`）不可解析 → 用显式迭代器循环；
   - **离线构建纪律**：离线仓缺 surefire 版本 → `-Dmaven-surefire-plugin.version=<已有版本>` 参数覆盖（不改 pom）；jacoco 插桩后重复跑 test 前先 `clean`。
2. **`skills/java-maven/SKILL.md`**：引用该节一行（Test conventions 见 spring.md §Test Conventions）。
3. **附录：全量回归「环境性基线失败」登记模板**（spring.md 测试节内）：
   - 登记项：失败测试类/现象/根因（环境性）/复跑证据/失效条件；
   - 实证 3 项：jacoco×PowerMock 双插桩、logback 写 `/data/log/resource-manager/`（WSL 缺目录）、VodServiceTest mock NPE（基线同错）；
   - 使用规则：回归时按清单对比，命中清单项不再 stash 复跑；修复后移除（带失效条件）。

## 6. Validation Plan

- 三案回放：按新增节条目逐条对照 T-011/012/013 过程教训，确认均可命中且表述一致。
- 门禁：check.py / repo-lint / path-audit 全绿（spring.md 为英文纪律区，条目英文表述）；unittest 全量。
- 语言门禁：本提案为英文纪律区资产（spring.md/java-maven），gate 对英文资产 FAIL 为既有预期（非回归）。

## 7. Risks

- **环境差异**：离线依赖/WSL 路径为公司本机事实，CI 或他机可能不同——条目标注「已知环境事实」+ 本机 vs CI 差异提示。
- **基线清单过期**：登记项修复后不撤销会误导——登记必带复跑证据与失效条件，维护 run 巡检时校验（对齐格式债基线登记先例）。
- **范围膨胀**：仅收已实证坑；新坑出现时按「≥1 次实证」再增补（演进原则），不预收投机条目。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-09-09 |
