# OPTIMIZATION_LOG — wayfinder

<!-- 每次实战使用后在顶部追加一条记录（TRIAL 评估期强制，见
     config/main-chain-capabilities.yaml desc + 维护报告 08-25）。
     字段对齐 extensions/README.md 约定：触发场景/问题清单与根因/改动内容/
     验证结果/影响评估/复现与回归建议；另加 wayfinder 评估专用字段。 -->

## 记录格式（每次触发必填）

```markdown
## YYYY-MM-DD — <effort-name>

- 触发场景: <大块模糊构想/迷雾/路线未知/超单会话 — 简述>
- 触发条件命中: <是/否 — 未命中时 desc 要求跳过，此处记为「未使用」>
- 决策图产物: <.wayfinder/<effort-name>/map.md 是否存在>
- 决策工单: <数量 / 示例>
- 被 spec/develop 消费: <哪个决策被后续 spec/develop 实际引用/采纳>
- 验证结果: <地图清空/路线清晰/交接成功 或 卡点>
- 影响评估: <该案例对主链的价值判断>
- 复现与回归建议: <后续触发与回归注意点>
```

<!-- ===== 记录区（新记录追加在下方，保持最新在上） ===== -->

## 2026-09-17 — TRIAL 终止（归档结论）

- 触发场景: 不适用（TRIAL 评估期 08-25 → 09-17 无任何实战触发）
- 触发条件命中: 否（0 次）
- 决策图产物: 无（全工作区 0 `.wayfinder/`）
- 决策工单: 0
- 被 spec/develop 消费: 0
- 验证结果: **零案例 → 未通过试用**
- 影响评估: wayfinder 对本系统 = 低频高价值；方法论要素大多已被 grilling / task-splitter /
  确认纪律覆盖，独有价值仅「跨会话持久决策图」；无真实雾区案例支撑升格（详见
  reports/wayfinder-value-reevaluation-2026-09-17.md）
- 处置（第一次判定）: 撤销 main-chain-capabilities.yaml 三处 TRIAL 注入（prepare/spec/develop）；
  skill 保留 On-Demand（aic 技能菜单可达，不再绑定主链）
- 处置（最终 2026-09-17 修订，用户决策）: 经第三方仓库复核 + 日常工作价值分析 + 阶段适配评估
  （develop 等执行阶段错配；prepare 为唯一合理候选）后，**接入 prepare**（use-skill 显式触发：
  跨会话雾区构想 → 生成 .wayfinder/ 决策图；具体需求 → 明确跳过）；spec/develop 保持终止不入注入；
  触发方式为显式判断句，非低显式度可选附注
- 复现与回归建议: 未来出现真实「跨会话大块模糊构想」案例并验证决策图被 spec/develop 消费后，
  再评估升格绑定更多阶段；不预先引入
