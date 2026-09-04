# Change Proposal: P48 — 配置默认值治理（@Value 单一默认源 + 对象化路线）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix + Structural（规范与门禁收口 L1 已实施；L2 配置对象化为本提案主体，触及新代码范式） |
| Author | AI Maintainer |
| Created | 2026-09-04 |
| Reference | 用户报告（2026-09-04）：AI 代码 `@Value("${key:3}")` 仍字段初始化 `= 3`（双默认）+ 配置字段缺注释；bs-integration 真实存量（git/Windows 通道定真）：双默认 12、缺注释 15 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状 / 缺口）

| 现象 | 存量实例 | 影响 |
|---|---|---|
| 双默认值 | `@Value("${…:3}")` + `private int x = 3;`（12 处） | Apollo 默认变更时两处漂移；Spring 注入运行期覆盖字段初值 → 初始化仅遮蔽非 Spring 构造 |
| 测试直构默认散落 | @InjectMocks/反射直构绕过 Spring 注入，默认值依赖生产字段初始化 | 默认逻辑散落生产字段，测试与生产两套默认来源 |
| 配置字段缺注释 | @Value 字段无用途/单位说明（15 处） | 配置键是部署期接口，未注释不可维护 |

## 2. Root-Cause（根因分析）

- **多默认源**：占位符冒号默认 + 字段初始化 = 两个载体，无单一事实源。
- **测试范式**：@InjectMocks/反射直构（非 Spring context）→ 需要非 Spring 渠道提供默认 → 生成代码把"测试兜底"写进生产字段（动机合理但位置错误）。
- **约束缺失**：规范/门禁均无「@Value 默认唯一源」「字段必注释」要求 → AI 生成即入库。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **L1 规范收口（已实施 36d19e9）** | spring.md §Configuration Injection：占位符冒号=唯一默认源、字段禁初始化、测试直构默认移测试侧（applyDefaults）、过渡豁免须 Javadoc 标注、字段必带注释；format-check 第 8 项 WARN（双默认/缺注释） | 止血：单源 + 集中 + 门禁；但仍靠纪律同步（测试默认与生产默认分处） |
| **L2 配置对象化（本提案主体，Recommended）** | 同类 @Value 收敛为 `@ConfigurationProperties` 配置 POJO：默认值集中 POJO 字段一处；`new Properties()` 自带默认供测试直构显式传入 → **测试默认 = 生产默认同源**；字段 final 杜绝双写；新代码默认范式写入 spring.md | 根治多源（Spring 推荐范式）；成本中（配置类收敛 + 存量迁移）；季度窗口 |
| L3 测试范式演进（远期） | Spring test slice / 配置文件加载的测试基准替代反射直构+手塞默认 | 最高根治度；属团队测试基础设施决策，成本高 |

**横切（无论哪层）**：配置不可信防御——批尺寸/循环计数入口校验（`batchSize <= 0` 拦截），杜绝 `i += 0` 死循环。

## 4. Recommendation（推荐方案 + 理由）

1. **L1 已落地**（2026-09-04，`36d19e9`）：规范 + 门禁第 8 项 + 测试 6 用例（全量 205 OK）；存量修复提示词已交付任务会话（12 双默认 + 15 缺注释 + 批尺寸防御）。
2. **L2（季度窗口）**：reconcile 系试点 `@ConfigurationProperties` 对象化——默认同源同处、测试直构显式传 POJO；通过后写为新代码默认范式（spring.md 更新）。
3. **L3（远期）**：随团队测试基础设施演进评估。
4. 批尺寸防御纳入存量修复清单（独立推进，不依赖 L2）。

## 5. Implementation Record（实施记录）

- 2026-09-04：L1 规范 + 门禁（spring.md §Configuration Injection；format-check 第 8 项）→ `36d19e9`；L2 待办入档 → `6788fb4`
- L2：Pending（季度窗口）。