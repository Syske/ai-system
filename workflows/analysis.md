# Workflow: Analysis

## Purpose

Analyze AI System structure, quality and consistency.

## Runtime

- ai-system/templates/runtime/runtime-analysis.md

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Analysis Target

Optional:

- Analysis Scope
- Existing Reports

## Context

Load only:

- The declared Analysis Target within the declared Analysis Scope
- Existing reports when provided

Never load content outside the analysis scope.

## Outputs

- analysis-report.md
- dependency-report.md
- consistency-report.md
- recommendations.md

Reports are written to `reports/analysis-{date}-{target}-{scope}/` under the AI System root.

## Exit Criteria

Success:

- Analysis reports generated with recommendations

Stop:

- Analysis Target cannot be resolved → report and stop

## Next

- Collect reusable findings into knowledge (governance/memory/) via the Knowledge workflow
- Recommendations feed future changes through prepare and spec
