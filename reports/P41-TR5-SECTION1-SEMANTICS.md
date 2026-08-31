# Change Proposal: P41 — tr5 脚本健壮性批次（§1 语义 + 工时校验 + 服务名正则 + tr4_url 条件化）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix（脚本契约矛盾） |
| Author | AI Maintainer |
| Created | 2026-08-26 |
| Reference | 202610-qa-housekeeping-optimization tr5-design/review run（Gate 4 前置验证踩坑 + review 人工发现） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`generate_tr5_data.py` 与 `validate_tr5.py` 对 TR5 文档 **Section 1** 的内容归属约定相反，导致每次构建后 Gate 4 前置校验必失败、需手工回填：

- `generate_tr5_data.py` 末尾**强制清空** `data["sections"]["1"] = ""`（设计意图：§1 内容进 `background/problem/value/tr4_url` 结构化字段，与 `tr5_storage.xml` 的 `{{section_1_background}}` 等发布占位符对应）；其 merge 逻辑在重建时只保留结构化字段，sections["1"] 每次丢失。
- `validate_tr5.py` 检查 `range(1, 20)` 所有 section 非空 → 必报 `"section 1 is empty"` 错误。

实际后果（本次 run 实测）：build → generate → validate 报错 → 手工 python 回填 sections[1] → 再 validate 才通过。流程脆弱且不可复现（下次 generate 又丢）。

> **追加证据（2026-08-28 spec 传播轮）**：本项目重建 data.json 后 `sections["1"]` 再次丢失，按上述临时手段（手工 python 回填）恢复。同一 generate/validate 链路的 0_x 槽位解析缺陷（inline 正文不识别 → 发布页 §0 露引导占位符）已另立 **P43**。

**追加（2026-08-26 review 阶段发现，经用户确认并入本批次）**：

- **P41-b（N2）工时 4-8h 约束无自动校验**：O9 要求单任务 4h≤工时≤8h，本次 §18 出现 3h/2h 任务靠人工 review 发现。validate_tr5.py 应解析 §18 工时表自动校验。
- **P41-c（N3）check_spec.py 服务名正则误匹配**：`^\| (服务名)` 会误命中图表清单等任意以服务名开头的表格行（本次 `| qa_manage 写入优化链路图 |` 被计为服务行），应收紧为服务名后跟 `\s*\|`。
- **P41-d（N4）tr4_url 空对技改项目报 warning 噪音**：技改无 TR4 是常态；当 tr3_url 存在且 tr4_url 为空时应降级为 info。

## 2. Root-Cause

两个脚本对「§1 内容的权威存放位置」各自独立实现，未对齐：generate 按 storage 模板的结构化字段语义写，validate 按通用"19 节全非空"规则写。缺少一个共同的权威约定。

## 3. Options

| 选项 | 做法 | 权衡 |
|------|------|------|
| A. validate 放行 §1，改查结构化字段 | `validate_tr5.py` 对 sec_id=1 特判：不查 `sections["1"]`，改查 `background/problem/value` 非空；两者皆空才报 error | 与发布链路一致（publish 渲染 §1 用的是结构化字段，sections["1"] 本就不被消费）；改动集中在 validate 单点 |
| B. generate 不再清空 sections[1] | 删除 `data["sections"]["1"] = ""` 行，§1 内容同时存在于 markdown 节与结构化字段 | validate 无需改；但同一内容双份存放，publish 只渲染结构化字段——markdown 版成为死数据，有漂移风险 |

## 4. Recommendation

**A**（validate 特判 §1，改查 background/problem/value）。

理由：§1 内容的唯一消费方是 publish 时的结构化字段占位符（tr5_storage.xml `{{section_1_*}}`），sections["1"] 在发布链路中不被读取——validate 校验一个不被消费的字段是伪门禁。B 会引入双份内容的漂移风险。

## 5. Proposed Changes

1. `extensions/tr5/scripts/validate_tr5.py`：
   - 循环检查 2..19 非空不变；
   - sec_id=1 特判：若 `background+problem+value` 合计非空 → PASS；否则报 `"section 1 content missing in background/problem/value"`；
   - 可选：sections["1"] 非空时降级为 warning（提示双份内容待清理）。
2. `extensions/tr5/skills/tr5-design/SKILL.md` Gate 3 清单「Section 1 留空（结构化字段填充）」处补一行：validate 对 §1 校验的是结构化字段。
3. `extensions/tr5/scripts/test_tr5_scripts.py`：补 §1 特判用例（background 空 → error；background 有值 + sections["1"] 空 → PASS）。
4. **（P41-b）** `validate_tr5.py` 增加工时校验：解析 sections["18"] 工时表行，单任务 <4h 或 >8h 报 error。
5. **（P41-c）** `check_spec.py` 服务计数正则 `^\| (svc)\b` 收紧为 `^\| (svc)\s*\|`（服务名后必须紧跟表格列分隔）。
6. **（P41-d）** `validate_tr5.py` tr4_url 检查条件化：`tr3_url` 非空且 `tr4_url` 空时降级 info（技改常态），两者皆空才保留 warning。

## 6. Validation Plan

- `python extensions/tr5/scripts/test_tr5_scripts.py` 全绿；
- 用本项目 `workspaces/202610-qa-housekeeping-optimization/tr5/tr5_data.json` 实测：generate 重建后直接 validate 通过（无需手工回填）；
- （P41-b）本项目 §18 表（4-8h）应 0 error；构造含 3h 任务的样例应报 error；
- （P41-c）本项目 check_spec.py 服务计数 spec=2/openspec=2 不再受图表清单行干扰；
- （P41-d）本项目 validate 输出 tr4_url 相关降级为 info。

## 7. Risks

| 风险 | 应对 |
|------|------|
| 既有项目依赖"sections[1] 非空"的手工回填习惯 | SKILL.md 同步说明；旧行为下回填无害（仅多 warning） |
| 结构化字段被误清空后 §1 无校验拦截 | 特判逻辑覆盖三字段合计非空，仍兜底 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（已批准立项起草 + 2026-08-26 确认扩展为脚本健壮性批次 P41-b/c/d；实施待批） | 2026-08-26 |
