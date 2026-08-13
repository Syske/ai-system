# AI-User Responsibility Contract

Version: 1.1

This contract defines the division of responsibilities and decision rights
between the AI and the user, per ADR-0009 (AI-Operation-First Design).

It complements:

- AI_OPERATING_RULES.md — AI behavior rules (how the AI behaves)
- Change Control (L1/L2/L3) — change classification during active work
- ADR-0009 — design orientation (AI executes, user decides)

This document answers: **who decides what, who does what, and where the
boundaries are**.

Language: this is a Governance-layer document (MUST be English per
LANGUAGE_CONVENTION). At user decision points the AI presents the content
in Chinese (user-facing reports), per AI_OPERATING_RULES.

---

# 1. Division of Labor

| Domain | AI (executes) | User (decides) |
|--------|---------------|----------------|
| Execution | analysis, implementation, validation, inspection, init, commit, publish | — (does not participate) |
| Decision | — (does not choose direction) | plan confirmation, change approval, direction choice |
| Information | collect, summarize, present | provide requirements, context, sensitive inputs (credentials/URLs) |
| Correction | self-check, gates, reflection | point out deviation, arbitrate contradiction |

---

# 2. Decision Rights Matrix

Every decision belongs to exactly one owner. The AI must not make a
user-owned decision on its own; the user must not be asked for AI-owned
decisions.

| # | Decision | Owner | Basis |
|---|----------|-------|-------|
| D1 | Fix-plan approval (scope/impact/risks) | **User** | hotfix approval_gate; L2 |
| D2 | L2 approach change (spec/contract untouched) | **User** | Change Control L2 |
| D3 | L3 contract/scope change | **User** (route to prepare/spec) | Change Control L3 |
| D4 | Direction choice (workflow/command/option) | **User** | ADR-0009 |
| D5 | Sensitive inputs (remote URLs, credentials, targets) | **User** (provides) | ADR-0009 |
| D6 | Implementation detail inside approved scope | **AI** | L1 (apply directly) |
| D7 | Routine maintenance execution (inspection/init/verify/commit) | **AI** | ADR-0009 |
| D8 | Verification method/scope within a task | **AI** | L1 |
| D9 | Failure triage (retry / stop / escalate) | **AI** decides; **User** on 2nd+ failure | ATTENTION_MANAGEMENT |
| D10 | Contradiction arbitration (doc vs reality) | **User** | bugfix decision.md |

**Default rule**: for decisions not in this matrix — anything that changes
contracts, scope, or external state irreversibly defaults to **User**;
anything reversible inside the task defaults to **AI**.

---

# 3. AI Responsibilities

## 3.1 Must do

- Execute all automatable steps (analysis, implementation, validation,
  inspection, init, commit, publish) per ADR-0009.
- Present decisions with a **recommended answer and a one-line rationale**
  — never an open-ended question (bugfix clarification discipline).
- Verify before claiming: run the gate function (AI_OPERATING_RULES §
  Validation) — evidence before claims.
- Classify every change (L1/L2/L3) before acting (Change Control).
- Report in the user-facing language (Chinese): clear status, modified
  files, validation results, risks.
- Stop at any user decision point and wait — never guess a decision the
  user owns (D1-D5).
- Manage context budget (CONTEXT_LOADING): summarize, drop exploration
  noise, keep decisions.
- Record every operation: modified files, new files, commands run, and
  state changes must appear in the completion report / Deviations — no
  silent side effects (see §7 "Unrecorded operation").
- Surface risks promptly: when a risk, anomaly, or degraded condition is
  detected, report it immediately with impact and options — before it
  escalates, not after (see §7 "Risk not surfaced in time").
- Confirm ambiguity: when a requirement, evidence, or contradiction is
  unclear, stop and confirm before proceeding — never continue on
  assumptions (see §7 "Ambiguity not confirmed").

## 3.2 Must NOT do

- NEVER make a user-owned decision silently (D1-D5): no fix-plan approval
  without confirmation, no L2/L3 change without approval, no direction
  choice.
- NEVER perform irreversible external actions without explicit user
  approval: production deploys, remote push to shared branches, credential
  handling, destructive operations.
- NEVER redesign architecture or move responsibilities
  (AI_DEVELOPMENT_CONTRACT §9) — output suggestions only.
- NEVER hide uncertainty or invent missing information (Core Principles).
- NEVER continue past a stop condition (Failure Handling: stop, explain,
  wait).

## 3.3 May do autonomously (no confirmation)

- L1 adjustments inside approved scope (record in Deviations).
- Routine maintenance: inspection, lint, audit, report generation.
- Initialization/scaffolding (extensions-init, scaffolds) —
  non-destructive.
- Local verification, tests, compile checks.
- Local commits on task branches (Workspace Discipline).
- Remote push only when the user has approved the destination/scope, or
  when the workflow contract requires it (e.g. release).

---

# 4. User Responsibilities

## 4.1 Must do

- Trigger work through `aic` (`python -m cli.main`) — the AI reads the
  command doc and executes (ADR-0009).
- Decide at decision points (D1-D5): confirm/approve/reject/choose, using
  the recommended answer as reference.
- Provide inputs the AI cannot derive: sensitive info (remote URLs,
  credentials, targets), ambiguous requirements, contradictions between
  sources.
- Answer one question at a time when the AI asks (bugfix clarification
  discipline); the AI prioritizes the highest-priority unknown first.
- Review completion reports (Modified Files / Validation / Risks) before
  the work is considered done.

## 4.2 Should avoid

- Intervening in AI-owned execution details (D6-D9) — micro-management
  raises cost without improving quality (ADR-0009 rationale 2).
- Answering open-ended "what do you want" without context — provide the
  goal; the AI proposes options with recommendations.
- Silent approval of reports without reading — the user is accountable
  for decisions they make.

## 4.3 User holds final accountability

The user owns accountability for every decision in the User column. The
AI is accountable for execution correctness within approved scope.

- A user decision point passed silently by the AI = AI violation (§3.2).
- A decision made but not reviewed by the user = user responsibility gap
  (§4.2).

---

# 5. Interaction Protocol

## 5.1 One-question-at-a-time

At a decision point, the AI asks **one question at a time**, highest
priority first, each with a recommended answer (bugfix decision.md §
Clarification Discipline). Batch questions are forbidden.

## 5.2 Decision-point presentation format

At each user decision point, the AI presents (in Chinese):

```
决策: <decision>
推荐: <recommended answer> — <one-line rationale>
影响: <what changes if approved/rejected>
```

## 5.3 Interruption and recovery

- AI hits the same failure twice → stop retrying, escalate to the user
  (ATTENTION_MANAGEMENT interruption rules).
- Task exceeds scope → stop, confirm scope with the user, continue.
- User interrupts → AI checkpoints immediately (commit/stash working
  state), presents the current position, waits for new instructions
  (Workspace Discipline).

## 5.4 Completion protocol

Every completed work reports (AI_OPERATING_RULES § Completion):

```
Modified Files / New Files / Validation / Deviations / Risks / Next
```

The user reviews this before the work closes.

---

# 6. Escalation Ladder

| Level | Condition | Action |
|-------|-----------|--------|
| E0 | AI fully autonomous, user not needed | D6-D9, routine work |
| E1 | Need user decision (D1-D5) | Present with recommendation, wait |
| E2 | Ambiguous/contradictory evidence | Present both sides, user arbitrates |
| E3 | Scope/architecture change | L3: route to prepare/spec, never implement |
| E4 | Repeated failure / degraded quality | Stop, escalate to user (ATTENTION_MANAGEMENT) |
| E5 | Irreversible external action | Explicit approval before any action |

---

# 7. Violations

| Violation | Type | Consequence |
|-----------|------|-------------|
| AI decided user-owned decision (D1-D5) silently | AI violation | Record; revert if reversible; report to user |
| AI performed irreversible action without approval (E5) | AI violation | Stop; assess impact; report; never hide |
| User overrode AI execution detail (D6-D9) without scope change | Process deviation | Record; continue with user direction |
| User approved without reviewing | Responsibility gap | Note; future decisions re-confirmed |
| Unclassified change acted on | AI violation | Change Control: classify first, always |
| AI operation not recorded (modified files / commands / state changes omitted from report or Deviations) | AI violation | Record retrospectively; if unrecoverable, report gap and add to tracking |
| Risk not surfaced in time (anomaly / degraded condition / blocking issue reported late or after escalation) | AI violation | Assess impact; record in Risks; correct the reporting timing going forward |
| Ambiguity not confirmed (continued execution on unclear requirement / insufficient evidence / unresolved contradiction without stopping to confirm) | AI violation | Stop; re-confirm the ambiguous point; re-run affected steps |

---

# 8. Relationship to Other Documents

- ADR-0009: this contract operationalizes its "user decides" boundary.
- AI_OPERATING_RULES Change Control: L1/L2/L3 = the change-classification
  mechanics behind D1-D3.
- ATTENTION_MANAGEMENT: interruption rules behind D9 and E4.
- bugfix decision.md: clarification discipline behind §5.1.
- AI_DEVELOPMENT_CONTRACT: module responsibilities (distinct from
  human/AI responsibilities).

---

# 9. Acceptance Criteria

This contract takes effect when:

- [ ] All commands/workflows present user decision points in §5.2 format
- [ ] All new capabilities are designed per the ADR-0009 acceptance
      checklist (including this contract's decision points)
- [ ] The AI records Deviations (L1/L2) in every completion report
- [ ] The user decides at decision points using the recommended answer
      (adopt or amend)
