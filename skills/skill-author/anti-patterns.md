# Anti-Patterns

---

## 1. Giant Monolithic Skill

**Pattern:** A single SKILL.md contains workflow, decisions, checklists,
examples, background knowledge, and scripts all in one file.

**Why it fails:**
- AI wastes context on irrelevant sections
- Hard to navigate and maintain
- Violates single responsibility principle
- Cannot compose with other Skills cleanly

**Instead:** Split into focused files. SKILL.md is only the entrypoint.
Extract workflow, decisions, checklists into separate files.

---

## 2. Documentation-Style Skill

**Pattern:** The Skill reads like a user manual. It describes concepts,
gives background, explains terminology — but never defines a workflow.

**Why it fails:**
- AI cannot execute it deterministically
- No stages, no outputs, no decisions
- The AI must invent the workflow, defeating the purpose

**Instead:** Every Skill must have a workflow. Stages, steps, outputs,
conditional branches. Not prose — executable instructions.

---

## 3. Prompt Template Skill

**Pattern:** The Skill contains text like "You are an expert in X.
Your task is to Y. Always follow Z." — i.e., prompt templates for
LLM consumption.

**Why it fails:**
- The Skill is already consumed by an LLM — adding meta-prompts wastes context
- Mixes two layers: the Skill instruction and the prompt the Skill should
  generate

**Instead:** Define what the AI should DO (workflow, decisions, checks),
not what the AI should SAY. The AI is the executor, not the prompter.

---

## 4. Unbounded Scope

**Pattern:** "This Skill helps with all things related to building
microservices" — covering architecture, testing, deployment, monitoring.

**Why it fails:**
- Impossible to trigger precisely
- Impossible to validate completeness
- Overlaps with every other Skill

**Instead:** "This Skill generates Dockerfiles for Spring Boot microservices."
One thing. Narrow. Precise. Composable with other Skills.

---

## 5. No Stopping Conditions

**Pattern:** The Skill defines what to do but never when to stop.

**Why it fails:**
- AI loops indefinitely when conditions aren't met
- No graceful failure path
- User must interrupt manually

**Instead:** Every Skill must answer: "What makes this complete?" and
"What if it cannot complete?" Define stopping conditions explicitly.

---

## 6. Project-Specific Hardcoding

**Pattern:** `docker build -t my-company/my-service:latest` or
`cd /home/jenkins/workspace/project-x`

**Why it fails:**
- Skill cannot be reused across projects
- Wrong path causes silent failures
- Violates the "generic, reusable" requirement

**Instead:** Use discovery (find the pom.xml, find the Dockerfile).
Never assume directory or project name.

---

## 7. Violating Priority Order

**Pattern:** A Skill with decision rules that lists priorities, but the
workflow jumps directly to the lowest-priority action.

**Example:** `mock-test` priority says "never relax matchers before
fixing fixtures" but the workflow first suggests `nullable()`.

**Why it fails:**
- Weakened test quality
- Inconsistent behavior
- User loses trust

**Instead:** The workflow must strictly follow the declared priority order.
If exceptions exist, document them explicitly.

---

## 8. Running Before Thinking

**Pattern:** Stage 1 is "Run command X" instead of "Analyze what happened."

**Why it fails:**
- Wasted execution time on wrong scope
- Cannot explain why the command is correct
- Violates Think → Plan → Execute order

**Instead:** Every Skill must have an analysis or planning stage before
any execution stage.

---

## 9. Duplicating Other Skills

**Pattern:** A new Skill for "running Java tests" that re-implements
Maven invocation, test scope selection, and Surefire analysis — all
already in `java-maven`.

**Why it fails:**
- Two Skills maintain the same logic
- Inconsistencies emerge
- Fixes in one don't propagate to the other

**Instead:** Reference the existing Skill in the description. Chain
Skills by mentioning trigger phrases. Never re-implement.

---

## 10. Ignoring Validation

**Pattern:** The Skill generates output but includes no validation stage.

**Why it fails:**
- Errors are not caught
- User discovers issues only when using the output
- No quality feedback loop

**Instead:** Every Skill must validate its own output. If it generates
a file, verify the file. If it runs a command, verify the exit code.
Validation is part of the workflow, not optional.
