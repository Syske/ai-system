# AI System Coding Memory

Lessons learned for the AI System itself (workflows, runtimes, prompt templates).


## [AI System] Workflow Main Chain Needs a Single Definition

Context:

ai-system/workflows/README.md showed the main chain starting from bootstrap, while config/menu.yaml and OPERATIONS.md §1.2 started from prepare.

Problem:

The same concept (change lifecycle main chain) was defined inconsistently across three documents, causing ambiguity about the entry point.

Root Cause:

The one-time cold start (bootstrap) was mixed into the same chain as the change lifecycle main chain (starting from prepare).

Solution:

Split the main chain into two parts: Cold start (bootstrap) + Change lifecycle main chain (prepare → spec → dev-setup → develop → review → verify → release), and align all three documents.

Lesson:

The AI System main chain / workflow relationship diagram must be maintained from a single source (workflows/README.md) and cross-checked regularly against menu.yaml and OPERATIONS.md.

Scope:

- ai-system/workflows/
- ai-system/config/menu.yaml
- ai-system/OPERATIONS.md


Related:

- Standard:
  LANGUAGE_CONVENTION.md


## [AI System] Runtime Template Language Boundary: English Control Flow / System Language for User Output

Context:

In ai-system/templates/runtime/ and workflows/, the language boundary between AI control-flow instructions and text presented to the user was unclear.

Problem:

Control-flow instructions and embedded user-facing report templates mixed Chinese and English; questions/choices presented to the user were in English, not matching the system-specified language (config/menu.yaml → locale).

Root Cause:

LANGUAGE_CONVENTION covered reports and comments but did not define the language for interactive questions and choices presented to the user.

Solution:

Apply a three-layer boundary: AI control-flow instructions → English; questions/choices/confirmations presented to the user → system-specified language (config/menu.yaml → locale); user report templates → Chinese. Technical identifiers (workflow names / arguments) stay English. Also added an Interactive prompts rule to LANGUAGE_CONVENTION.

Lesson:

When creating or editing runtime/workflow templates, first classify the text (control flow / user interaction / user report), then choose the language accordingly; interactive questions follow the system locale, never hardcode a language.

Scope:

- ai-system/templates/runtime/
- ai-system/workflows/
- ai-system/templates/prompts/


Related:

- Standard:
  LANGUAGE_CONVENTION.md
