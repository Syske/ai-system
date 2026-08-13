# Change Proposal: P20 — hotfix-test-doc 发布链护栏增强（校验误报 + 空单元格自动修复）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix (extension tooling) |
| Author | AI Maintainer |
| Created | 2026-08-11 |
| Reference | 实战：AQLD-2088/AQLD-2084 HotFix 转测文档发布（pageId 704017953） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

2026-08-11 通过 `extensions/hotfix-test-doc` 发布 AQLD-2088/AQLD-2084 转测文档时，发布链暴露 3 个缺口：

1. **发布前校验误报（阻断）**：`validate_hotfix_doc.py` 的占位符正则 `\{[a-zA-Z_][a-zA-Z0-9_]*\}` 把正文中合法的接口路径参数（`{enterpriseId}`、`{courseId}`、`{feedId}`）当成未替换模板占位符，发布被拦截；只能手工把接口路径改成 `[eid]` 形式规避，破坏了文档可读性。
2. **`{test_report_link}` 无法满足**：测试报告链接在发布时尚未产生（需测试完成才可填），校验器却强制替换 → 只能填"待测试完成后补充"，发布后仍需人工回填。
3. **发布后校验失败需手工修复**：`publish_markdown_to_confluence.py` 的 `build_html_storage_body` 不做空单元格处理，模板 `|  |` 渲染成 `<td></td>`（本次 49 处），`verify_hotfix_page.py` 校验失败后需手工 `update_page_storage` 逐个替换为 `<td><br /></td>`（发布后版本号 v2→v3）。

## 2. Root-Cause

- `validate_hotfix_doc.py` 占位符检测无上下文/白名单概念，`{}` 是 markdown 中常见的代码/路径语法，与模板占位符冲突。
- 模板把 `{test_report_link}` 定义为必填占位符，但"测试报告链接"在提测阶段客观上不存在，模板语义与流程时序矛盾。
- `build_html_storage_body` 仅做 markdown→storage 渲染，未实现 SKILL.md 声称的 `<td></td> → <td><br /></td>` 防护（SKILL.md 该规则停留在文档层面，未落到代码）。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | 校验器引入**白名单 + 上下文豁免**（行内代码/代码块内的 `{}` 不检测；`test_report_link` 加入可豁免清单），publisher 在 storage 渲染后统一 `td` 空单元格自动填充 `<br />` | 根治 3 个缺口，发布链自动闭环，无需手工改文档/手工修页面 | 需改 2 个脚本 + 模板语义注释 |
| B | 仅改校验器白名单，空单元格继续靠发布后手工修复 | 改动小 | 每次发布都手工修，未根治 |
| C | 转测文档强制不写 `{}` 路径、测试报告链接发布前必须真实填写 | 不改代码 | 违背文档可读性与流程时序，规则不可行 |

## 4. Recommendation

**Option A**：发布链三层自动防护——
1. `validate_hotfix_doc.py`：占位符检测跳过行内代码/代码块（markdown 反引号）内的 `{}`；`test_report_link` 加入豁免清单（允许"待补充"类占位，发布后回填）。
2. `publish_markdown_to_confluence.py` `build_html_storage_body`：渲染后 `re.sub(r"<td></td>", "<td><br /></td>")`（含 `<th>`），发布即合规，`verify_hotfix_page.py` 不再拦截。
3. `template_content.md`：`{test_report_link}` 注释说明"发布时可暂填待补充，测试完成后回填"。

## 5. Proposed Changes

1. `extensions/hotfix-test-doc/scripts/validate_hotfix_doc.py`：
   - 正则检测前先剔除行内代码片段（`` `...` ``）与代码块；
   - `ALLOWABLE_PLACEHOLDERS = {"test_report_link"}` 豁免清单（值含"待补充/待测试完成后补充"即通过）。
2. `extensions/confluence-markdown-publisher/scripts/publish_markdown_to_confluence.py`：
   - `build_html_storage_body` 末尾追加空单元格填充（`<td></td>`/`<th></th>` → `<td><br /></td>`/`<th><br /></th>`）。
3. `extensions/hotfix-test-doc/template_content.md`：`{test_report_link}` 行加注释说明豁免语义。
4. `extensions/hotfix-test-doc/SKILL.md`：更新占位符规则（接口路径可用 `{}`，不再要求改写为 `[]` 形式）。

## 6. Validation Plan

- 用本次实战文档重跑：`validate_hotfix_doc.py` 在保留 `{enterpriseId}` 路径 + `test_report_link=待补充` 情况下应 VALIDATION OK。
- `build_html_storage_body` 单测：含空单元格的 markdown → storage 无 `<td></td>`。
- 发布回归：草稿页发布 + `verify_hotfix_page.py` 一次通过（无需手工修复）。
- `python tools/check.py`（若脚本接入）exit 0。

## 7. Risks

- 白名单豁免可能放过真实未替换占位符（作者新加占位符但未登记豁免清单）。缓解：豁免清单固定且极小（仅 test_report_link），新增占位符必须显式加入。
- publisher 全局替换 `<td></td>` 可能影响非 HotFix 页面渲染语义（Confluence 空单元格 `<td><br /></td>` 是标准兼容写法）。缓解：该函数仅服务 HotFix markdown 发布路径，行为与 verify 校验一致。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-13 |

---

## Implementation Record (2026-08-13)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `validate_hotfix_doc.py`：占位符检测改用等长空格遮蔽行内代码/围栏代码块；新增 `ALLOWABLE_PLACEHOLDERS = {"test_report_link"}` 豁免清单；`{title}` 等真实遗留占位符仍阻断。
2. `publish_markdown_to_confluence.py` `build_html_storage_body`：渲染后统一补齐空单元格（`<td></td>`→`<td><br /></td>`、`<th></th>`→`<th><br /></th>`）。
3. `template_content.md`：`{test_report_link}` 行加注释说明“占位符由测试同学转测后补充，创建/提测时保持原样”。
4. `SKILL.md`：补充占位符规则（接口路径 `{}` 可保留、`{test_report_link}` 由测试同学转测后补充，创建方保持原样）。

**Validation**:
- `py_compile` 两脚本 OK。
- 校验器回归：保留 `` `{enterpriseId}` `` 路径 + `{test_report_link}` 字面量 → `VALIDATION OK`（exit 0）；保留真实 `{title}` 未替换 → 阻断（exit 1）。
- `build_html_storage_body` 单测：含空单元格 markdown → storage 无 `<td></td>`/`<th></th>`，空单元格补齐 `<br />`。
- 发布回归：草稿页发布 + `verify_hotfix_page.py` 一次通过（待实际发布时执行）。
