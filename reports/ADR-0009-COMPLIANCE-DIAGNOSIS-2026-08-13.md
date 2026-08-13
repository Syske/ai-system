# ADR-0009 合规性系统诊断报告

- 日期 / Date: 2026-08-13
- 范围 / Scope: 按 ADR-0009（AI-Operation-First Design）验收标准对 ai-system 全系统做合规性诊断
- 性质 / Nature: 诊断评估（只读，无实施）
- 依据 / Basis: ADR-0009 七条原则 + 新能力验收清单（5 项）

---

## 一、总体结论

**基本合规（12/15 通过）**，发现 **2 个真实问题 + 3 个观察项**。
系统整体符合"AI 自运行自维护、用户仅决策、经 aic 触发"原则，但存在
历史遗留的结构性泄漏（公司规范进通用层）与死资产（废弃命令暴露）。

---

## 二、合规项（通过，15 项检查中 12 项）

| # | 维度 | 检查内容 | 结果 |
|---|------|----------|------|
| 1 | AI 可发现 | 15 workflows / 15 commands 全注册（menu 31 条目，无差异） | ✅ |
| 2 | AI 可执行 | 15/15 命令有 Steps 段；8/15 含可执行命令（其余 7 个为 AI 工作流型命令，设计上不调脚本，符合原则） | ✅ |
| 3 | AI 可验证 | 门禁覆盖 20 个检查函数（compile/imports/menu/registry/ADR/memory/path/repo-lint/bugfix-modes） | ✅ |
| 4 | 配置驱动 | bugfix 2 模式配置化（standard 7 阶段 / hotfix 10 阶段 + parser）；无散落硬编码流程差异 | ✅ |
| 5 | 幂等安全 | 6 个 scaffold/init 工具全部幂等非破坏（refus/exist_ok） | ✅ |
| 6 | 无硬编码路径 | workflows/commands/runtime/config 零环境特定硬编码（仅 local.yaml 机器级） | ✅ |
| 7 | 状态卫生 | bugfix-modes 配置 + 门禁闭环（坏 parser 被 check.py 拦截，已负向验证） | ✅ |
| 8 | 命令→menu→字段 | 15 命令全部有 command_fields 或 default | ✅ |
| 9 | 契约/实现分离 | branch-parser 契约在 runtime，实现在 extensions（hotfix-branch-parser） | ✅ |
| 10 | 文档一致性 | OPERATIONS §1.3.1/1.3.2 与 bugfix-modes.yaml 一致 | ✅ |
| 11 | 门禁自举 | extensions-init/branch-parser-scaffold 均已注册 tools/README.md | ✅ |
| 12 | ADR 完整性 | ADR-0009 含 Context/Decision/Rationale/Consequences，全英文 | ✅ |

---

## 三、发现的问题（按严重度）

### 🔴 P1（结构性，L3，仅建议不实施）— `standards/cool/` 公司规范泄漏到通用层

| 项 | 内容 |
|---|---|
| 位置 | `governance/standards/cool/`（enum-naming / i18n / enum-dml / rocketmq-conventions / rpc-conventions，含 `net.coolcollege.*`） |
| 违反 | ADR-0009 原则 6（两层分离）+ extensions/README.md 定位（公司特有 → extensions 层） |
| 现状 | 被 `standards-loader.md` 与 `runtime-release.md` **正式引用**，是活跃资产 |
| 影响 | 换公司克隆 ai-system 会带上 coolcollege 规范；公司规范变更需改 ai-system 通用层 |
| 建议 | L3 结构性变更：`standards/cool/` 迁至 extensions 层（如 `extensions/company-standards/cool/`），standards-loader 改为可配置路径（类似 layers.skills）。**走变更流程，本次不实施** |

### 🟡 P2（死资产，L1，建议清理）— 2 个 Deprecated 命令仍注册在 menu

| 项 | 内容 |
|---|---|
| 位置 | `aic-skill-launch`、`aic-skill-optimize`（声明 Deprecated 2026-08-08，被 `/aic-skill` 取代） |
| 违反 | ADR-0009 原则 2（能力应可发现；废弃入口不应暴露，AI 可能误触发） |
| 建议 | menu.yaml 移除注册（命令文件保留作历史）。**L1，需确认后实施** |

---

## 四、观察项（记录，暂不动）

| # | 观察 | 说明 |
|---|------|------|
| O1 | 2 个 thin-command 超限（aic-apply 114 / aic-explore 124 行） | P18 已提案，待季度评审 |
| O2 | 25 个 repo-lint warnings（13 英文注释 + 6 skill无workflow + 3 命令Steps中文 + 3 中文文档） | 既有存量债，语言债清单已登记（MAINTENANCE-2026-08-08-language-lint-debt.md） |
| O3 | hotfix-test-doc 的 `codeup.aliyun.com/<org>/<repo>` 占位符 | 已是占位符写法，合规；仅记录 |

---

## 五、修复建议

| # | 动作 | 等级 | 状态 |
|---|------|------|------|
| F1 | menu.yaml 移除 skill-launch / skill-optimize 注册（文件保留） | L1 | 待确认 |
| F2 | standards/cool/ 迁移评估（extensions 层 + 可配置 loader） | L3 | 待评审（本次不实施） |
| F3 | P18 命令瘦身季度评审 | — | 已有提案跟踪 |

---

## 六、诊断方法（可复现）

```text
1. 注册完整性:   check.py (15 workflows / 15 commands)
2. 步骤化:       扫描 cli/commands/*.md 的 **Steps** 与可执行命令
3. 硬编码扫描:   grep 环境特定路径 (D:/ C:/ /home/ 等)
4. 公司内容泄漏: grep cc{date}/服务名/公司名/个人名/Codeup 地址
5. 幂等性:       grep refus/already exists/non-destructive
6. 死资产:       扫描 Deprecated 声明 vs menu 注册
7. 配置驱动:     bugfix-modes.yaml 结构 + 负向测试（坏 parser 被拦截）
```
