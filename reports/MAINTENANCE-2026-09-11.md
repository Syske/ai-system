# 系统巡检报告 — 2026-09-11（on-demand：code-review 流程专项）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand（Scope=根据今日日志 review code-review 流程）
- 日期: 2026-09-11

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 29 | Files: 29 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies（715 refs / 0 broken） |
| extensions | Summary: 0 errors, 0 warnings |
| workflow-command-audit | 0 blockers / 0 warnings（15 workflows, 13 commands） |
| proposal-audit | 0 gate error / 0 warn（3 开放提案 + 2 open action items，见 §六） |

补充说明：lint WARN 25 与上期持平（无新增）；delta 自 2026-09-09 起 35 提交 / 81 文件
变化，涉及 cli/config/governance/reports/rfc/skills/templates/tools/workflows —— 本
次为 on-demand 专项，仅按 Scope 跑 code-review 域对应子集 + 全量工具门禁，未跑
extensions-lint 全量（Scope 不含 extensions）。

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期(09-09) | 本期 | 变化 |
|---|---|---|---|
| Skills | 32 | 30 | -2 |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 59 | 59 | = |
| Templates | 22 | 22 | = |

变化归因：apply-openspec / archive-openspec 两个实验性技能随「归档 apply/archive 命令」
提交（639494b）移除，Skills 32→30（repo-metrics 口径，目录计数）；repo-lint 口径 29。
主要技能增量：implement 2399→2445（+46）、repository-maintainer 1137→1163（+26）、
review 160→166（+6）、task-splitter 285→288（+3），均为近 2 日流程/规范修订。

---

## 二、巡检发现（AI 填写，按严重度分级）

专项对象：今日（2026-09-11）code-review 运行 `code-review-20260911-143800`（spec-comparison
模式，Confluence pageId=671776379，三仓 qa_manage/qa_boss/qa_client）+ 相关日志
`review-verify-20260911-1500`，对照 `workflows/code-review.md` 与
`templates/runtime/runtime-code-review.md`。

### 中（结构性，输出建议不直接改）

- **M1 [已修复] code-review.md 节顺序违规**：`workflows/code-review.md` 顶层出现两个非契约节
  —— `## Target Branch Resolution`（夹在 Inputs 与 Context 之间）、
  `## Spec-Comparison Review Mode`（夹在 Outputs 与 Exit Criteria 之间），违反八段契约
  顺序 Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next。
  08-31 已登记、需 L2 审批；用户本次已批准执行：Target Branch Resolution → Context 子节、
  Spec-Comparison Review Mode → Outputs 子节（内容逐字保留，正文 98 行 ≤ RFC-0003 门限），
  执行前先完成 aic code-review 菜单交互流程评估（见 §四 建议 0）。
- **M2 [已修复] runtime-code-review.md「不修改业务实现」声明与 spec-comparison 实际
  执行矛盾**：runtime 声明 "The Runtime does not modify business implementation" 且阶段链
  止于报告生成；但今日运行按用户授权（L1 已登记）执行了 fix-apply + merge master + 三仓
  `git push origin` + Confluence 更新到 v24。该「授权修复扩展路径」只写在 workflow 内联
  文本，runtime 阶段模型未覆盖 → 文档自相矛盾。已按用户确认修复（§四 建议 2）：声明改为
  「默认不修改业务实现，用户显式授权时可扩展」+ 新增 Spec-Comparison Fix-Apply Extension
  阶段（Sync→Fix-Apply→Build/Check→Commit&Push→Record，含授权规则）。
- **M3 [相邻流程学习] review/verify 报告覆盖事故**（源自 review-verify-20260911-1500，
  非 code-review 域但同属评审流程族）：T-011 verify 重跑误覆盖 2026-09-10 初版
  verification-report（workspaces 无 git，原文不可恢复）。根因=context 状态行过期 + 未先
  检查目标文件。建议 review/verify 写报告前加「目标文件存在性检查 + 冲突改名/备份」检查项
  （§四 建议 3）。

### 低 / 信息

- **L1 [已修复] HotFix loop 的 wiki 更新行为过时**：今日 agent 更新远程 wiki 至 v24 后，
  用户决定远程 wiki 由用户自管（agent 仅写本地 `change-summary-wiki.md`）；而
  `workflows/code-review.md` Spec-Comparison 节 HotFix loop 仍写 "update wiki page
  (update_confluence_page.py)" → 已按新决策更新（§四 建议 2b）：移除 agent 更新远程
  wiki 步骤，标注远程 wiki 用户自管 + fix-apply 需显式授权。
- **L2 [工具缺口，可选] workflow-command-audit 未捕获非契约顶层节**：code-review.md 八段
  违规在 0 blocker/0 warning 下通过，说明审计工具不检测契约外顶层节 → 可选增强
  （§四 建议 4）。
- **L3 [环境观察] CRLF 行尾符噪音**：qa_boss/qa_client 工作区 CRLF 噪音改动已 stash 保留
  （未提交未丢失）→ 业务侧建议 .gitattributes/.editorconfig（§四 建议 5，仅建议）。
- **I1 [信息] 运行日志补写正常**：code-review 诊断日志 14:38 建档、wiki 更新（16:00）后
  原地追加，符合日志维护惯例，无异常。

### 正向观察（今日运行的良好实践，建议保持）

- Spec-comparison 12/12 claim 全部逐条实证比对（含 "no behaviour change" 语义核对）；
- merge-base 基线比对，全部 finding 标记 [introduced]/[pre-existing]，行号引用完整；
- 验证链完备（py_compile + mock asyncpg 运行时 + 真实 loguru 开关实测 + push 验证 +
  语言门禁 PASS cjk 0.57/0.52）；
- 未解决项处置明确：M-3→运维确认容量、m-10/m-11/S-1~S-4→登记后续/结构项，无越权实施；
- 输出符合约定 `outputs/code-review/260911-python-db-manage-fix/`（{yyMMdd}-{target}）；
- L1 偏差（用户授权直接修复+推送）已在诊断日志显式登记；config/workflows/code-review.yaml
  保持最小化（name/workflow/runtime）。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

| # | 检查项 | 结论 |
|---|---|---|
| 1 | workflows/*.md 八段齐全且顺序正确 | **PASS（修复后）**：code-review.md 八段顶层契约顺序恢复（Target Branch Resolution → Context 子节、Spec-Comparison Review Mode → Outputs 子节）；其余 14 个 + workflow-command-audit 0 blocker |
| 2 | 术语与 workflows/README.md 选择表一致 | PASS（code-review 行含 spec-comparison + HotFix loop 描述一致） |
| 3 | config/workflows/code-review.yaml 注册表最小化 | PASS（仅 name/workflow/runtime，无回潮） |
| 4 | 引用路径存在 / 链接健康 | PASS（path-audit 715 refs 0 broken；junction/symlink 无异常） |
| 5 | Doc-vs-reality：AGENTS.md 结构图 / 契约架构图 / OPERATIONS 入口 vs 实际目录 | **PASS（修复后）**：code-review runtime 声明已与 spec-comparison 实际执行对齐（M2 闭环）；目录布局无漂移 |
| 6 | 状态卫生：workspaces/.aic-state.yaml 引用存在 | PASS（4 个 project 引用在 workspaces/ 下均存在；projects/ 目录为服务仓非 project-id，非引用失效） |
| 7 | Run-log 覆盖：未提交 git 改动 vs 诊断日志 | PASS（ai-system git 干净；今日 code-review 运行有对应诊断日志） |
| 8 | 提案盘面（proposal-audit） | PASS（0 gate error；P41/P42/P46 开放 defer 季度回顾；P26/P28 action items 保持开放） |

---

## 四、修复动作与建议清单（AI 填写）

本专项 read-first，除已批准/确认执行项外未做其他就地修改；已执行项标注 [已执行]，其余输出建议待决策。

1. **建议 1 [已执行（L2 批准）]**：code-review.md 节归位 —— `Target Branch Resolution` 降为
   Context 子节、`Spec-Comparison Review Mode` 降为 Outputs 子节，恢复八段顶层契约顺序。
   08-31 遗留；本次获用户 L2 批准执行，前置完成菜单交互流程评估（建议 0）。验证：
   workflow-command-audit 0/0、check.py PASS（2 个提案自归因 WARN）、repo-lint 0/0/25、
   path-audit OK、quick-check OK。

2. **建议 2 [已执行（用户确认）] runtime/loop 文档修正（M2 + L1）**：
   a) `templates/runtime/runtime-code-review.md` —— 声明改为「默认不修改业务实现，spec-comparison
      模式用户显式授权时可扩展修复落地」；新增 `## Spec-Comparison Fix-Apply Extension
      (user-authorized)` 阶段（Sync→Fix-Apply→Build/Check→Commit&Push→Record），授权规则
      （未经显式授权永不运行 + L1 偏差登记 + 未解决项记录不静默实施）；
   b) `workflows/code-review.md` HotFix loop —— 移除 agent 更新远程 wiki 步骤，改为
      「远程 wiki 用户自管，agent 仅写本地 change-summary-wiki.md；fix-apply 需显式授权」。
      为满足 RFC-0003 ≤100 行门限，同步压缩 Projects bullet 说明行（frontmatter↔正文一致性
      检查通过）。验证：check.py PASS、audit 0/0、lint 0/0/25、path OK、quick-check OK、
      正文 99 行。

3. **建议 3 [已执行（用户确认）] review/verify 报告写前冲突保护**：`templates/runtime/
   runtime-review.md` + `runtime-verify.md` 的 Outputs 新增 `## Report-Write Guard
   (overwrite protection)` —— 写报告前检查目标文件是否已存在（T-011 事故防护，workspaces 无
   git 不可恢复），冲突时不静默覆盖：展示旧文件 → 改名/备份后写 → 诊断日志记录。验证：check.py
   PASS、audit 0/0、lint 0/0/25。

0. **建议 0 [评估完成，交互层建议待决策] aic code-review 菜单交互流程评估**（执行建议 1
   前置项，用户指示）：
   入口链路：`launch/opencode.ps1` → `aic` wizard（menu.yaml flow_analysis「代码分析」
   → 选 code-review）→ `wizard/fields.py` 读 workflow frontmatter `workflow.inputs`
   （required: Projects 多选；optional: Target Theme / Branch Mapping / Base Branch 默认
   master / Review Focus / Output Directory / Confluence Spec Page Id）→
   `prompt_builder.py` 构建 prompt（八段正文 + 骨架化 runtime + 语言纪律）→ 剪贴板 →
   opencode 会话 → AI 按 runtime Phase 1 分支解析 → 评审 → 报告 + P45 语言门禁。
   评估发现（按交互摩擦排序，均建议、不直接改）：
   - P1 [i18n 缺口]「Target Theme」「Confluence Spec Page Id」无 field_note；
     「Output Directory」field_note 默认值「../ai-system-pack」来自其他命令，与 code-review
     的 `outputs/code-review/{yyMMdd}-{target}/` 不符（字段名共享导致备注错配，会误导用户）。
   - P2 [双重询问] 分支解析两段式：wizard 收集 Target Theme/Branch Mapping 后，AI Phase 1
     仍 fuzzy-match 并再展示候选让用户选/再 ask —— 多项目时存在重复询问摩擦。
   - P3 [可发现性] flow_main.review（🔍，主链质量门禁）与 flow_analysis.code-review（🔎，
     任意代码评审）双条目 icon/名称近似，仅分组标题区分，用户易混淆。
   - P4 [候选可推导] Target Theme / Branch Mapping 可提供动态候选（dev_branch/本地分支，
     同 scan 的 Branch provider），但无 provider —— 未利用 P37「可推导→不让用户填」。
   建议处置：P1 为 i18n 单点补齐（minor doc，待确认后可就地修）；P2-P4 为交互层结构建议
   （需变更管理评估，不属本次执行范围）。

**Review Focus 优化 [已执行（用户确认）]**：
   - `config/menu.yaml`：field_choices 新增 10 项预置候选（性能/安全/正确性/并发/兼容性/错误处理/
     日志/资源管理/标准合规/代码质量，与 runtime Phase 3 维度对齐）+ multi_select_fields 加入
     Review Focus（空格多选）
   - `workflows/code-review.md`：frontmatter `default: 全面审查`（跳过时默认全选=全面审查，显式
     进入 prompt）；正文 Inputs 同步 `(default: 全面审查)`（frontmatter↔正文一致性通过）
   - `config/i18n/zh.yaml`：Review Focus 备注更新（多选；默认全选=全面审查，可反选收窄）
   - 说明：choose_many 无默认全选参数（起手 `selected=set()`），字面全勾选需 wizard 代码改动
     （交互层，变更管理项）；配置层以「跳过→默认全面审查」实现等价语义
   - 验证：check.py PASS、audit 0/0、lint 0/0/25、quick-check OK、YAML 可解析、正文 99 行

**输入简化包其余项 [已执行（用户确认 ① ② ③ 5c）]**：
   ① P1-i18n 补齐：i18n field_notes 新增 Target Theme + Confluence Spec Page Id 备注；menu.yaml
      field_icons 新增 Target Theme 🌿 / Confluence Spec Page Id 📄（Output Directory 备注错配随 ② 移除）
   ② 移除 Output Directory 输入：输出位置为固定约定（frontmatter outputs.base 已声明），frontmatter+
      正文 Inputs 同步移除，可选输入 6→5 个（frontmatter↔正文一致性通过）
   ③ 减少分支解析双重询问：Branch Mapping 显式覆盖直接采用不再二次展示候选；Target Theme 唯一命中
      直接采用、仅 0/多命中才展示选择；workflow Context/Target Branch Resolution + runtime Phase 1
      「Target Branch by theme」同步改写
   5c runtime Phase 3：注明「用户 focus 项获得评审优先级，其余维度仍覆盖；默认全面审查=全维度」
   验证：check.py PASS、audit 0/0、lint 0/0/25、path OK、quick-check OK、正文 99 行

**F2 [已执行] 可配置技能源目录（用户需求驱动）**：
   - 背景：aic-skill 菜单 core 组只能识别 2 个技能（`core_skills` 白名单仅 deepseek-share-to-md +
     wayfinder），ai-system/skills 下 30 个技能中 29 个叶子技能不可达
   - 设计：`config/skill-groups.yaml` 新增 `skill_roots`（配置驱动发现）—— key=来源标记、
     value=目录（占位符 {ai_system_root}/{workspace_root}）；需要新增技能目录时登记即可，无需改代码
   - 配置：先配置 `core: {ai_system_root}/skills` + `extensions: {workspace_root}/extensions`；
     extensions 未登记时回退 env layers.skills（per-env 灵活）；内置源 global/local 不变
   - 改动：`skill_scan.py` `_core_skills`（白名单）→ `_skill_roots`（配置目录扫描，str/Path 兼容）；
     `skill-groups.yaml` `core_skills` 白名单退役
   - 验证：扫描 core 29 + extensions 9（共 38）；`architecture/` 分组容器正确跳过；launcher 菜单
     core 组 29 项全量可达；全 CLI 单测 259 OK；check.py PASS、lint 0/0/25、path OK、quick-check OK

**F6 [已修复] aic 菜单输入中文过滤崩溃（UnicodeDecodeError）**（用户实测驱动）：
   - 症状：`aic` 向导菜单（skill 选择等）输入中文过滤字符时崩溃 —— `keys.py _read_raw`
     单字节 `os.read(fd,1).decode()`，raw 模式下 UTF-8 多字节字符首字节（如 0xe3）单独解码失败
   - 修复：`_read_raw` 按 UTF-8 lead byte 补齐续字节（0xC0→2、0xE0→3、0xF0→4，配合
     `_data_ready` 0.1s 超时避免阻塞）后再 decode；异常字节回退 latin-1（不崩溃）；ESC 序列
     检测路径不受影响（0x1b < 0xC0 单字节）
   - 回归：`test_menu_package.py` 新增 4 用例（CJK 解码/ASCII/ESC/孤立 lead byte 不崩溃）
   - 验证：全 CLI 单测 263 OK（+4）、compile OK、check.py PASS、lint 0/0/25、quick-check OK

**F7 [已执行] 非开发主链菜单体检（用户需求驱动）**：
   - A1 [修复] `env-init` command_fields 重复「Workspace Root」字段（向导会重复询问）→ 去重
   - A2 [修复] 缺失字段备注/图标补齐：extensions-init（Remote URL/Committer Email/Committer Name）、
     propose（Change Name）、skill（Agent）、skill-source（Report Name）、env-init（Workspace Root）
     —— field_notes + field_icons 全部补齐（0 缺失）
   - A3 [已修复] 交互层英文文案本地化（用户确认）：skill_launcher（选择技能/已选技能/描述/用法/触发/
     任务/提示词摘要/技能启动报告等）、agent_picker（选择代理/未启用任何代理）、wizard/output.py
     （输出标题/复制到剪贴板/保存到/结束（不启动）/在 ai-workspace 打开 X）—— 全部本地化为 zh，
     内部返回值（copy/print/save 等 token）保持不变；全 CLI 单测 263 OK
   - A4 [信息] Review Focus field_choices 值本身为中文自解释，多选菜单不渲染 option_descriptions，无需补
   - A5 [通过] 菜单注册完备：无 fallback 其他流程/其他命令残留；sections 标题 i18n 全覆盖；条目图标齐全
   - A6 [通过] skill 命令无双重询问（fields_for 对 skill 返回空，launcher 全权处理）；check.py 菜单
     引用完整性 PASS
   - 验证：字段 i18n 覆盖 0 缺失；check.py PASS、lint 0/0/25、quick-check OK、全 CLI 单测 263 OK

**F5 [已执行（修订 3）] skill 菜单选中样式 + 分组顺序**（用户需求驱动）：
   - 选中行字体黑色：新增 `selected_black`（\e[30;47m 黑字白底）；`_paint_many` 选中分支整行
     统一选中样式（勾选标记/名称/描述不再单独着色，字体色随 selected 主题）；skill launcher 传
     `selected_theme="selected_black"`；`marker_box`/`marker_theme` 移除（无使用方）
   - 每屏限制 max_visible=20（用户需求）；非选中行无背景（勾选标记纯文本）
   - 分组顺序：`skill-groups.yaml` 公司技能（extensions）组提前一级 ——
     常用组合 → 公司技能 → 核心按需技能 → 全局 → 项目
   - 最终效果：选中行=黑字白底整行高亮；非选中=纯文本无背景；公司技能位于第 2 组
   - 验证：渲染模拟正确（选中黑字白底/非选中无背景/默认菜单反显保留）、分组顺序正确、
     全 CLI 单测 263 OK、compile OK

**F4 [已执行] aic 向导项目菜单置顶无项目入口**（用户需求驱动）：
   - `cli/services/wizard/selection.py` `_select_project`：💻 system（no project）+ 🤖 AI 引导
     （无项目任务）两个无项目入口由列表末尾置顶到前两项，项目列表后置
   - 索引映射同步：idx 0→None（system）、idx 1→__AI_GUIDE__、idx≥2→projects[idx-2]；
     默认项仍停在最近项目（index+2 偏移），无最近项目则默认第一个项目
   - 验证：索引映射模拟正确（含默认偏移）、全 CLI 单测 259 OK、compile OK、check.py PASS、
     lint 0/0/25、quick-check OK

**F3 [已执行] skill 菜单分组高亮 + 每屏 10 项可筛选 + 长描述截断**（用户需求驱动）：
   - `config/ui.yaml` + `cli/utils/menu/theme.py`：新增 `section` 主题色（\e[1;36m 粗体青，与现有
     name/divider 配色一致，用户要求保持配色统一）
   - `cli/utils/menu/select.py` + `multi.py`：Section 分组头渲染由 `note`（暗色）→ `section`（高亮）
   - `cli/services/skill_launcher.py`：`_step_pick_skills` 的 choose_many 增 `max_visible=10`
     （每屏最多 10 项，输入关键字过滤全量列表；分组头在截断时始终可见）
   - `cli/services/skill_launcher.py`：`_skill_label` 描述截断 `_DESC_MAX=50`（长描述技能如
     agent-browser 925 字符不再撑爆菜单行，38/38 技能描述超限均截断）+ `_preview_skills`
     预览步骤展示完整描述（选中后可见全文）
   - 验证：标签最大行宽 ≤88 字符（原最大 1000+）、截断/预览模拟正确、全 CLI 单测 259 OK、
     compile OK、check.py PASS、lint 0/0/25、path OK、quick-check OK

**F1 [已修复] skill 加载缺陷 —— extension skill 描述块标量解析错误**（用户报告驱动）：
   - 症状：`aic-skill` 菜单中 hotfix-test-doc / release-config-review / release-env-matrix /
     yapi-openapi 等扩展技能描述显示为 `— >`（而非真实描述）；10+ ai-system core 技能同受影响
   - 根因：`cli/services/skill_scan.py` `_read_frontmatter` 用单行正则
     `^description:\s*(.+)$` 解析 frontmatter，遇 `description: >`（YAML 折叠块标量）把 `>`
     当描述值；未复用共享 YAML 解析器 `cli/services/frontmatter.py`（P25 单一解析器）
   - 修复：`_read_frontmatter` 改用共享 `read_frontmatter`（PyYAML，正确处理 `>`/`|` 块标量、
     引号、多行），无 frontmatter 块时回退旧单行正则；usage/trigger 收敛为 `_single_line_field`
     （保留 `triggers?` 复数兼容）；清理死代码
   - 验证：扫描 11 技能描述全部正确加载（0 残留 `>`）；skill 单测 14/14 OK；全 CLI 单测
     259 OK；compile OK；check.py PASS、lint 0/0/25、quick-check OK
   - 说明：嵌套子技能（如 hotfix-test-doc/skills/create、skills/update）不入 launcher 菜单属
     设计行为（router 主技能调度 executor 子技能），非缺陷
4. **建议 4（可选，工具增强）**：workflow-command-audit 增「非契约顶层节」检测（当前八段
   违规不报警）。
5. **建议 5（信息，业务侧）**：qa_boss/qa_client 等 python 仓补 .gitattributes 行尾符规范，
   消除 CRLF 噪音 stash 摩擦。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-09 | OK | 0 |
| 2026-09-11 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 3 开放提案 / 2 open action items
  - 开放: P41-TR5-SECTION1-SEMANTICS.md
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P46-TR5-DEBT-VALIDATION-MARKER.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P28-CHANGE-ID-GENERATION.md:46 D：AI 可选生成（skill 层落点）——触发条件未到（不引入 wizard LLM，Evolution Principle）

处置：P41/P42/P46 保持 defer 季度回顾（TR5 家族，与上期一致）；P26/P28 开放项无新触发，
维持现状。
