# Runtime: HotFix Test Doc

Extends:

- runtime-base.md

---

## Purpose

Generate a HotFix test document (转测文档) on Confluence from a committed
hotfix branch.

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

# Responsibilities

- Extract git branch/commit info from the hotfix branch
- Gather fix details from the user (发布内容, 影响范围, 测试记录)
- Resolve parent page hierarchy (YY.MM Hotfix 一页纸)
- Fill the HotFix 一页纸 template from extensions/hotfix-test-doc/
- Validate before publish (extensions/hotfix-test-doc/scripts/validate_hotfix_doc.py)
- Create the Confluence page with an exact title
- Verify after publish (extensions/hotfix-test-doc/scripts/verify_hotfix_page.py)

The extension (hotfix-test-doc) owns the template, validator, publisher, and
verifier. This Runtime only orchestrates the document lifecycle.

---

# Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Applied Standards

Provided by BugFix Runtime (hotfix mode):

- Branch Name (from Phase 4.6)
- Fix Summary (Root Cause / Repair / Validation)

Resolved by this Runtime:

- Document content
- Parent page id
- Published page id

---

# Phase 1 — Extract Branch Facts

- Read current branch: `git branch --show-current`
- Parse date from branch name: `cc(\d{8})` pattern (hotfix-test-doc contract)
- Resolve compare URL: `https://codeup.aliyun.com/<org>/<repo>/branches/compare/<base>...<branch>`
- Determine base branch via `git symbolic-ref refs/remotes/origin/HEAD`
  (fall back to master; never hardcode private-cloud)

---

# Phase 2 — Gather Details

Ask the user for (concisely; do not ask what is auto-extracted):

- Document title (auto-generate: `YYYYMMDD-概述-用户名`)
- 预计发布时间 (format `YYYY-MM-DD HH:00`, default 22:00)
- 影响租户和用户范围
- 是否造成线上客户数据错误
- 发布内容: services, clusters (default blue+bgy), build branch, version
- 问题来源 / 问题地址 / 问题发现时间 (when available)

Do NOT ask for: 代码比对链接 (auto), Review人 (left for post-deploy),
版本 (blank unless pom upgraded).

---

# Phase 3 — Resolve Parent Page

- Query: `get_confluence_page_tree.py --page-title "YY.MM Hotfix" --space-key "CoolAcademy" --view tree`
- Find child `YY.MM <用户名>`; use its id as parent_id
- Create the child directory when missing and the user authorizes
- Encoding guardrail: create pages containing Chinese via Python
  (urllib + ensure_ascii=False, UTF-8 body). Never git-bash curl with
  Chinese JSON (Confluence returns HTTP 500).

---

# Phase 4 — Fill Template

- Read template: `<this-extension>/template_content.md` (canonical copy)
- Fill `{placeholder}` markers with user-provided or git-extracted values
- Section 四: replace `*单租户/多租户(大概租户个数)/全租户*` line via regex
- Section 五: only replace `是/否` in section 五 region; keep post-release
  `*是/否*` markers intact
- Test/review tables: keep placeholder names and `是/否` unchanged
- 巡检服务列: fill from project service name (from git remote URL)
- Empty cells: template markdown uses `|  |`; publisher converts
  `<td></td>` → `<td><br /></td>` (P20)
- `{test_report_link}`: reserved for the test teammate after 转测 — leave
  as-is at publish; validator exempts it
- Markdown structure: keep a blank line between paragraphs and lists
  (CommonMark lazy continuation merges lists into the previous <p>)

---

# Phase 5 — Validate Before Publish (mandatory)

```powershell
python "<this-extension>/scripts/validate_hotfix_doc.py" "<doc_file_path>"
```

Blocks on: leftover `{placeholder}` markers (except test_report_link),
Section 四/五 markers not replaced, missing mandatory sections, list-hanging.
Exit code 1 = fix and re-run.

---

# Phase 6 — Create Confluence Page (exact title)

```powershell
python "<confluence-publisher>/scripts/publish_markdown_to_confluence.py" `
  --markdown-path "<doc_file_path>" `
  --parent-page-id <parent_id> `
  --exact-title "<YYYYMMDD-概述-用户名>"
```

Always use `--exact-title` — the default `-<mode>` suffix corrupts the
`YYYYMMDD-概述-用户名` title format.

---

# Phase 7 — Verify After Publish (mandatory)

```powershell
python "<this-extension>/scripts/verify_hotfix_page.py" <page_id>
```

Asserts: title matches `YYYYMMDD-概述-用户名`, ancestor chain contains
`YY.MM Hotfix 一页纸` and `YY.MM <用户名>`, no empty `<td></td>`.

Report URL to user. Save local file on failure.

---

# Outputs

- HotFix test document (转测文档) on Confluence
- 转测文档 markdown (local copy when Confluence API fails)

---

# Reflection

Before declaring completion, execute Reflection according to
governance/REFLECTION_RULES.md.

Record the Reflection Report in the Completion output.
