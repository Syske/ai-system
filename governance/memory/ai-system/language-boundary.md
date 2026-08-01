# AI System Language Boundary Memory


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
