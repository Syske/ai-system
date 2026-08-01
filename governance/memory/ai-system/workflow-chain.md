# AI System Workflow Chain Memory


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
