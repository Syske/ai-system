# wayfinder 价值重评估（2026-09-17）

> 触发：08-17 直接吸收（On-Demand 起步）→ 08-25 TRIAL 注入主链（prepare/spec/develop，硬截止
> 08-30）→ 截止逾期未评估。用户要求基于试用事实**重新评估 wayfinder 对本系统的价值**。

## 一、试用事实（证据）

| 证据项 | 结果 |
|---|---|
| OPTIMIZATION_LOG 实战记录（08-25 起强制） | **0 条**（记录区空） |
| `.wayfinder/` 决策图产物 | **0**（全工作区） |
| 被 spec/develop 消费的决策 | **0** |
| TRIAL 注入状态 | 三阶段 `enabled: true` 一直挂着（评估从未执行） |

## 二、价值重评估（针对本系统）

### wayfinder 真正独有的能力（对照 08-17 报告 §3.1）

| 方法论要素 | 本系统已有对应 | 增量价值 |
|---|---|---|
| 迷雾判别测试（能否精确陈述问题） | grilling（需求澄清、决策树访谈） | 低——已覆盖 |
| 决策工单 ≠ 执行工单 | task-splitter（原子任务卡 + 依赖） | 低——已覆盖 |
| HITL/AFK 分类、一次会话一工单 | 确认纪律（一次一问、P50 required/skip）、L1/L2/L3 | 低——已覆盖 |
| 超范围即关闭 | 变更控制（任务边界、L3 防扩） | 低——已覆盖 |
| **持久决策图（.wayfinder/ 跨会话地图）** | **无** | **高——唯一独有能力** |

### 为什么试用零证据（根因分析）

1. **场景低频**：酷学院实际需求以具体 Change Request / TR3/TR4 文档 / 工单进入主链，"大块模糊构想、路线未知、远超单会话"的雾区场景在真实工作流中几乎不出现；
2. **自我抑制**：TRIAL desc 自带"未命中触发条件 → 明确跳过"，AI 遵守后自然不产出；
3. **替代路径**：模糊构想通常当场会话内 grilling 澄清完毕，不需要持久化决策图跨会话交接。

### 结论

- **wayfinder 对本系统 = 低频高价值**：常态价值低（要素大多已被 grilling/task-splitter/确认纪律覆盖），
  独有价值仅"跨会话持久决策图"一项，且只在真实雾区场景出现时才被需要；
- **无真实案例支撑升格**：按 Evolution Principle，不应铺开、不应绑定主链；
- **保留 On-Demand 合理**：skill 本体是成熟方法论资产（来源维护活跃、纯提示词无危险面），
  留作雾区场景备用工具成本极低。

## 三、处置建议

1. **终止 TRIAL**：撤销 main-chain-capabilities.yaml 三处注入（prepare/spec/develop）——与 08-25
   自定判定标准一致（无 ≥1 真实案例 → 移除临时登记）；
2. **保留 On-Demand**：`skills/wayfinder/` 不动（菜单已可达，无需额外登记）；
3. **OPTIMIZATION_LOG 归档**：追加终止结论（零案例，判定"未通过试用，回退 On-Demand"）；
4. **未来触发条件**：出现真实"跨会话大块模糊构想"案例并验证决策图被后续 spec/develop 消费后，
   再评估升格绑定 prepare——不预先引入。

## 四、替代强化（不引入 wayfinder 机制的前提下）

若希望低成本强化"雾区"处理，可将 wayfinder 唯一增量概念**一句话并入 prepare 纪律**：
"需求路线未知时，先画一页决策图（问题/选项/待确认），会话结束保留到
`openspec/changes/<change>/design-notes.md`，跨会话继续"——本质是把 grilling 结论落盘，
不需要完整 wayfinder 工单机制。此条可选项，默认不执行（无实证痛点）。

## 五、第三方仓库复核（2026-09-17，用户要求基于 mattpocock/skills 重评）

### 上游现状（实测）

- 仓库：github.com/mattpocock/skills（活跃，wayfinder 最后一次提交 2026-08-19）
- 08-15~08-19 共 5 次提交，全部为**打磨而非方法论变更**：Skill tool 调用措辞统一
  （`with "name"`）、多 skill 步骤拆分、禁止调用用户级 skill（#453）、全仓 em-dash 清理
- 当前 SKILL.md 核心方法论（Plan-don't-do / Map / Fog of war / 四类工单 / HITL-AFK /
  一次会话一工单 / 100K 规模）与 08-17 吸收时**无实质差异**
- 增量：**Refer by name**（按名称引用，不裸用编号）——可读性纪律，本地副本未含

### 本地副本 vs 上游（对照）

| 上游要素 | 本地副本 | 判定 |
|---|---|---|
| Task 工单类型（做事解阻塞） | 已含 | 同步 |
| 100K 单会话规模 | 已含 | 同步 |
| HITL/AFK 纪律 | 已含 | 同步 |
| Refer by name | **缺失** | 微差（可读性纪律，1 段可补） |
| Skill tool 调用措辞 | 不适用 | 我们不用该工具链，无关 |

### 复核结论

1. **价值结论不变**：基于第三方仓库最新版——wayfinder 仍是高质量、活跃维护的方法论 skill，
   但独特价值仅"雾区持久决策图"一项；其余要素已被 grilling / task-splitter / 指针纪律 /
   变更控制 / pi-worker 子代理分域覆盖；
2. **无新增主链缺口**：上游更新（打磨为主）不产生新能力差；平台差异（issue tracker vs
   本地 .wayfinder/、Skill 子代理 vs pi-worker）已被本地形态等价覆盖；
3. **无需试用/绑定**：上游活跃度不改变触发频率现实（酷学院需求以具体 CR/TR3/TR4 进入，
   雾区场景稀缺）；On-Demand 保留为正确形态；
4. **可选同步**：本地副本补"Refer by name"纪律 1 段（保持 On-Demand 资产最新，成本≈0）。

### 证据

- 上游 SKILL.md 当前版（raw.githubusercontent.com/mattpocock/skills/main/...）
- 上游提交历史（GitHub API commits?path=skills/engineering/wayfinder/SKILL.md，5 次 08-15~08-19）
- 本地副本 skills/wayfinder/SKILL.md（对照）
