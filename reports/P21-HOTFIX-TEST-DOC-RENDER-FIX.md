# Change Proposal: P21 — hotfix-test-doc 模板标题渲染缺陷修复与回填工具

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix (extension tooling) |
| Author | AI Maintainer |
| Created | 2026-08-12 |
| Reference | 实战：HotFix SQL 变更转测文档发布（2026-08-12） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

2026-08-12 发布 HotFix 转测文档（SQL 变更：某清理记录表字段长度扩展）后，Confluence 页面出现渲染缺陷：

1. **三、问题原因 / 五、是否已经造成线上客户数据错误 / 六、技术上解决办法概述** 三节标题渲染为 `<h2>**三、问题原因...`（星号原样保留、标题未加粗），而同模板的 一/二/四/七/八/九 节正常。
2. 首版发布后 46 处空表格单元格 `<td></td>` 在 Confluence 不渲染（空单元格不可见），需二次手工修复（v2→v3）。
3. 既有校验/验证链路**均未拦截以上缺陷**：`validate_hotfix_doc.py` 只检查占位符与 四/五节 marker；`verify_hotfix_page.py` 只检查空 `<td></td>`，不检查标题渲染（storage 残留 `**`）。

## 2. Root-Cause

- **标题渲染缺陷**：模板标题行使用 Setext 格式（`**标题` + 下一行 `---`）。Markdown 将"文本行 + 下划线"整体解析为 `<h2>` 标题，未闭合的 `**`（有开头无结尾）被原样带进 HTML 标题文本；四节标题因有闭合 `**` 而正常渲染为 `<strong>`。受影响的三行在模板 `template_content.md` 中缺少闭合 `**`。
- **空单元格不渲染**：模板 `|  |` 经 `markdown.markdown` 渲染为 `<td></td>`，Confluence 不渲染空单元格；需 `<td><br /></td>`。SKILL.md 已声明该 guardrail，但发布脚本 `build_html_storage_body` 未实现，仅停留在文档层面。
- **校验盲区**：validate/verify 脚本均无标题渲染缺陷检测（未检查 storage 中残留 `**`）。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（采用） | 修复模板源（三行补闭合 `**`）+ 新增发布后回填工具（`fix_empty_td.py` / `republish_storage.py`）+ 页面原位回填 | 根治渲染缺陷；回填工具可复用；guardrail 收口到脚本 | 需维护两个新脚本（规模小） |
| B | 仅手工编辑 Confluence 页面三处标题 | 改动最小 | 模板源仍带病，下次发布必然复现；无防回归 |
| C | 仅修模板、页面不管（下个文档自然修复） | 改动最小 | 当前页面缺陷遗留；无法验证修复效果 |

## 4. Recommendation

**Option A**，与 P20 的发布链护栏方向互补（P20 聚焦 publisher 层自动修复，P21 聚焦模板源修复 + 已发布页面的回填能力）：

1. `template_content.md`：三/五/六节标题补闭合 `**`（根因消除，防复发）。
2. 新增 `fix_empty_td.py`：读取页面 storage，`<td></td>` → `<td><br /></td>`，PUT 回原页面（版本+1）。
3. 新增 `republish_storage.py`：从本地 md 重新渲染 storage（复用 `build_html_storage_body`）+ 空单元格 guardrail + 按版本 PUT 回原页面，用于渲染修复后的原位回填（不新建页面）。

## 5. Proposed Changes

1. `extensions/hotfix-test-doc/template_content.md`：
   - 三、问题原因 / 五、是否已经造成线上客户数据错误 / 六、技术上解决办法概述 三行标题补闭合 `**`。
   - 已用 `grep -vE '\*\*.*\*\*'` 扫描全模板，确认无其他未闭合 `**` 行。
2. 新增 `extensions/hotfix-test-doc/scripts/fix_empty_td.py`（空单元格回填，版本+1）。
3. 新增 `extensions/hotfix-test-doc/scripts/republish_storage.py`（本地 md 重渲染 + 空单元格 guardrail + 原位 PUT 回填）。
4. 已发布页面回填至渲染正确（标题全部 `<h2><strong>…</strong></h2>`）。

## 6. Validation Plan

- `verify_hotfix_page.py` 通过：标题格式 `YYYYMMDD-概述-用户名`、祖先链、无空 `<td></td>` ✅
- 人工抽查 storage 全部 `<h2>` 标题：均含 `<strong>`，无残留 `**` ✅
- 模板 `grep -vE '\*\*.*\*\*'` 无残留未闭合行 ✅

## 7. Risks

- 历史已发布页面若存在同类标题缺陷需逐页回填（本次仅修复当前页面）。缓解：P21 的 `republish_storage.py` 可复用；开放问题 2 评估批量回填。
- `republish_storage.py` 当前以 `attachments={}` 渲染，含本地图片的 md 不适用。缓解：本次文档无图片；含图文档需扩展为上传附件后回填（开放问题 3）。
- 校验/验证脚本仍未检测标题 `**` 残留（本次靠人工抽查）。缓解：开放问题 1/4 补强 validate/verify 脚本。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A**（模板修复 + 回填工具） | 2026-08-12 |

---

## Implementation Record (2026-08-12)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `template_content.md` — 三/五/六节标题补闭合 `**`（Setext 渲染根因消除）。
2. 新增 `scripts/fix_empty_td.py` — 空 `<td></td>` → `<td><br /></td>` 回填，PUT 回原页面（版本+1）。
3. 新增 `scripts/republish_storage.py` — 从本地 md 重渲染 storage + 空单元格 guardrail + 原位更新（不新建页面）。
4. 已发布页面回填：v2→v3（空单元格修复，46 处）→ v4（标题渲染修复重渲染）→ v5（标题脱敏），终态 `VERIFY OK`。

**Validation**: `verify_hotfix_page.py` 通过（标题格式 / 祖先链 / 无空 `<td></td>`）；storage 全部 `<h2>` 标题含 `<strong>`、无残留 `**`（人工抽查）；模板未闭合 `**` 扫描无残留。

**Deviations**: 无。
**Open Items**:
1. `validate_hotfix_doc.py` 增加"未闭合 `**` 行"检查（标题行 `**` 数量为奇数），源头拦截。
2. 历史 HotFix 页是否存在同类标题缺陷、是否批量回填。
3. `republish_storage.py` 支持含本地图片的 md（上传附件后回填）。
4. `verify_hotfix_page.py` 增加"storage 无残留 `**`"断言，闭环验证。
5. P20 的 publisher 层统一收口（`build_html_storage_body` 内置 `<td>` 填充 + 标题清理）实施后，本提案回填工具可作为兜底。
