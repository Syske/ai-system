# Outputs Directory Convention

Version: 1.0

Defines how project-less (non-operational) commands and workflows organize
their generated artifacts. Operational maintenance artifacts belong in
`ai-system/reports/` (see OPERATIONS.md §1.7); this convention covers
business-facing analysis outputs under the workspace root `outputs/`.

Language: Governance-layer document (MUST be English per
LANGUAGE_CONVENTION).

---

## 1. Two-layer structure

```
<workspace-root>/outputs/
└── <domain>/                       # fixed per command/workflow (kebab-case)
    └── {YYYY-MM-DD}-{descriptor}[-N]/   # per-session directory
        ├── <domain>-report.md      # main report (mandatory)
        └── <domain>-report.json    # optional: machine-readable result
```

- **domain**: the command/workflow name (e.g. `scan`, `trace`, `bugfix`,
  `change-impact`, `code-review`, `proposal`, `skill-source`).
- **descriptor**: kebab-case session theme, ≤ 30 chars, summarizing WHAT
  this session is about (e.g. `thread-leak`, `live-api-timeout`). The AI
  derives it from the task target; when the command has no explicit target,
  use the command's default scope word (e.g. `full-scan`).
- **-N suffix**: same-day rerun on the same descriptor appends `-2`, `-3`.

## 2. Why per-session directories

- Each run's artifacts (report + intermediates + logs) stay together and
  do not pollute other runs.
- The directory name itself is the session overview — no need to open it
  to know what it contains.
- Historical data is preserved; renaming/migration of old flat files is
  NOT required (existing files stay as-is).

## 3. Report file format (minimum)

Every main report starts with this header:

```
# <Domain> Report — {YYYY-MM-DD}

- 日期 / Date: ...
- 范围 / Scope: ...                 # session theme (= descriptor)
- 结论 / Conclusion: ...            # one-line conclusion
- 建议 / Recommendations: ...       # findings / next steps
```

Report language follows LANGUAGE_CONVENTION: user-facing reports in
Chinese.

## 4. Enforcement

- NOT a strict check.py gate (outputs are runtime artifacts, not
  repo assets). Conventions are enforced by command/workflow docs that
  reference this file, which the AI follows when executing (ADR-0009:
  doc-as-contract, AI-executable).
- `outputs/` is outside both git repositories (ai-system and extensions)
  and is gitignored by default.

## 5. Scope

| Domain | Convention reference |
|--------|---------------------|
| scan / trace / bugfix | this file (command/workflow docs) |
| change-impact / code-review / proposal | already aligned; this file standardizes wording |

Operational maintenance (maintain / analysis / extensions-init /
extensions-lint) records to `ai-system/reports/`, NOT `outputs/`.
`skill-source` (third-party skill source assessment) is also operational —
it records to `reports/skill-source-{date}-{descriptor}/` under the
ai-system root, aligned with `analysis` (NOT `outputs/`).
