# Change Proposal: P46 — tr5 发布债收口 + review/verify 验证标记检查

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Fix + Structural（tr5 发布闸门修复 / 运行时模板机制补充，收口批次） |
| Author | AI Maintainer |
| Created | 2026-09-01 |
| Reference | 全量日志扫描（2026-09-01）：tr5-optimization-exec-20260826-190000（check_tr5 8 FAIL 遗留债，归属未执行的「线上 TR5 --update 同步」）；#5 核查（maintain-R1-20260901-214500）——runtime-review/runtime-verify 无未验证标记形式化检查，develop 编译阻断时验证义务传递靠文本约定；P41/P42（tr5 健壮性）开放关联 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

两项独立、同属「下轮维护收口」的遗留：

**(a) tr5 发布闸门 8 FAIL 遗留债**（8/26 记录，未处理）：
- `check_tr5.py`（发布闸门）→ 8 FAIL：TR3 引用、缺 SVG、§0 过程标注、题图行序号粘连
- 归属「线上 TR5 --update 同步」步骤长期未触发 → 债持续；与开放提案 P41（tr5 脚本健壮性批次）/P42（tr5_template 骨架）同域，适合一波收口

**(b) 验证义务传递缺口**（#5 核查确证，未修）：
- develop 环境阻断（无 Linux JDK）时，日志以「下一步建议：review/verify 补跑 mvn test」文字传递
- `runtime-review.md` / `runtime-verify.md` **无任何「未验证标记」形式化检查**（grep 空）→ 若 review 阶段不记得补验，「编译/单测未跑」的完成定义缺口会静默穿透到发布

## 2. Root-Cause（根因分析）

- (a) tr5 发布门与文档/资源同步分离：check_tr5 的失败项（TR3 引用/SVG/§0 标注/题图）是**文档资产与模板/规范不同步**的产物，「线上 update」步骤无独立排期机制 → 滞后成债。
- (b) 运行时模板未定义「验证状态」这一显式交接字段：验证义务只存在于 develop 日志的文本建议里，链上（review/verify）无字段可查、无步骤强制 → 断档。

两问题同根：**「后置步骤的强制机制」缺失**——tr5 的 update 步骤、链的验证交接步骤都依赖人的记忆而非机器检查。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 合并收口（Recommended）** | (a) tr5 8 FAIL 随下轮 TR5 线上 update 逐一修复，与 P41/P42 决策联动；(b) runtime-review/verify 新增「验证状态核验」步骤——检查开发产物/任务卡是否携带 compile/unittest 验证标记（WARN 级提示） | 一次收口两项；(b) 轻量（模板步骤 + 约定字段）；(a) 复杂度取决于 TR3 引用对齐面 |
| B1. 仅修 tr5 债 | (a) 做、(b) 维持文本约定 | 验证断档风险继续延续 |
| B2. 仅补验证标记 | (b) 做、(a) 继续滞后 | tr5 发布债无限期挂账 |
| C. 维持现状 | 两缺口都保留，季度回顾再议 | 已证伪：债已跨 8/26→9/1，断档风险真实 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**。理由：
1. **同批收口**：两项均为「下轮维护收口」清单项（上轮日志扫描结论），合并执行管理成本最低。
2. **机制补位**：(b) 是「后置步骤强制机制」最小实现——模板新增检查步骤 = 运行时声明级（经 R1 合并机制已能确保进入 prompt），不建新工具。
3. **(a) 与 P41/P42 联动**：tr5 债修复可与 P41（check_spec 健壮性）/P42（tr5_template 骨架）在同一 tr5 批次内一起决（避免三次碰 tr5）。
4. **Evolution Principle**：均由真实运行日志驱动（check_tr5 8 FAIL 实测 + #5 核查），非投机。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，不直接修改；批准后按 OPERATIONS §12 Implement 阶段执行。

1. **(a) tr5 发布债**：随下轮 TR5 线上 update 执行 `check_tr5.py` 8 FAIL 逐项修复——TR3 引用对齐 / 缺 SVG 补齐 / §0 过程标注 / 题图行序号粘连；修复后 check_tr5 0 FAIL 为 update 完成前置。
2. **(b) runtime-review.md**：评审步骤前新增「验证状态核验」——检查目标任务卡/产物是否携带 validation 标记（compile / unittest 状态）；未标记 → 在评审结论显式记录「未验证项」并提示补跑（WARN 级，不阻塞评审本身）。
3. **(b) runtime-verify.md**：发布前置核验中强制执行 same check——存在未验证标记且未补跑 → 视为发布前阻塞项（ERROR 级）。
4. **(b) 约定字段**：LANGUAGE_CONVENTION 不受影响；任务卡/完成报告约定的「验证状态」字段定义写入 runtime-review/verify（一句话约定，不新建文件）。
5. 登记：P41/P42 决策联动（若同一批次实施 tr5，则 P41/P42 状态一并更新）；`tools/README.md` 无新增工具。

## 6. Validation Plan（如何验证）

- (a) `check_tr5.py` → 0 FAIL（发布闸门全绿）为完成标准。
- (b) 渲染验证：`PromptBuilder().build('review', {})` / `build('verify', {})` 骨架含「验证状态核验」步骤（复用 R1 Extends 合并机制，断言命中）；单测追加对应断言。
- 全量 gate：`python3 tools/check.py` / `repo-lint.py` / `path-audit.py` / `unittest cli/tests` 全绿。
- 行为回归：后续 develop 阻断场景（无编译环境）下，review 报告应出现「未验证项」显式记录。

## 7. Risks（风险与缓解）

| 风险 | 缓解 |
|---|---|
| tr5 修复面（TR3 引用对齐）可能涉及多文档一致性问题 | 随线上 update 排期执行；必要时拆 P41 联动批次，不阻塞 (b) |
| 「验证标记」约定无机器校验（靠 AI 填写） | WARN 级先行 + 骨架步骤强制可见（R1 机制已保证）；后续可升级为任务卡字段校验 |
| review 误报（无关未验证项干扰评审） | 核验仅提示未验证标记，不自动判不合格；verify 侧才升级为阻塞 |
| 与 P41/P42 边界重叠 | 提案联动声明：本提案只收 check_tr5 债；P41/P42 的脚本健壮性/模板骨架范畴不动 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-09-01 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）