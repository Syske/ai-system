# Repository Optimization Report

> Generated: 2026-07-02
> Scope: `.opencode/` under `pywechat-live-2608`
> Objective: Improve maintainability, reusability, and composability without breaking backward compatibility.

---

## 1. Repository Assessment

### 1.1 Current Inventory

| Area | Count | Details |
|---|---|---|
| Skills | 17 | 9 multi-file (modular), 7 single-file (monolithic), 1 meta-skill |
| commands | 4 | All `opsx-*` OpenSpec commands |
| Total files | 52 | Across all skills + commands |
| Directories (`.opencode/`) | 3 | `commands/`, `node_modules/`, `skills/` |

### 1.2 Skills Breakdown

**Multi-file modular Skills (skill.md + workflow.md + ...):**

| Skill | Files | skill.md lines | Total lines | Maturity |
|---|---|---|---|---|
| bugfix | 9 | 61 | 866 | New modular format ✓ |
| implement | 8 | 70 | 757 | New modular format ✓ |
| java-maven | 8 | 63 | 670 | New modular format ✓ |
| mock-test | 8 | 73 | 981 | New modular format ✓ |
| skill-author | 6 | 67 | 574 | New modular format ✓ |

**Single-file monolithic Skills (SKILL.md only):**

| Skill | Lines | Format issue |
|---|---|---|
| openspec-explore | 215 | No frontmatter description |
| openspec-apply-change | 117 | No frontmatter description |
| task-splitter | 148 | No frontmatter description |
| contract-maintainer | 105 | No frontmatter description (+ 322-line Python script) |
| openspec-propose | 86 | No frontmatter description |
| openspec-archive-change | 81 | No frontmatter description |
| spec-updater | 211 | No frontmatter description (+ 184-line Python script) |
| codegraph-helper | 72 | No frontmatter description |
| karpathy-guidelines | 47 | Has description ✓ |

**Minimal Skills:**

| Skill | Lines | Purpose |
|---|---|---|
| grilling | 7 | Interview trigger |
| grill-with-docs | 6 | Interview + docs trigger |

### 1.3 Naming Inconsistency

| Convention | Files | Skills |
|---|---|---|
| `skill.md` | 5 | bugfix, implement, java-maven, mock-test |
| `SKILL.md` | 8 | codegraph-helper, contract-maintainer, karpathy-guidelines, openspec-*, skill-author, spec-updater, task-splitter |

**Impact:** Low — OpenCode resolves both. But inconsistent naming complicates tooling and
automated validation.

### 1.4 Frontmatter Quality

| Quality | Count | Skills affected |
|---|---|---|
| Full YAML frontmatter with description | 6 | bugfix, implement, java-maven, mock-test, skill-author, karpathy-guidelines |
| Minimal/absent description | 8 | All openspec-*, spec-updater, task-splitter, contract-maintainer, codegraph-helper |
| Pure trigger with no workflow | 2 | grilling, grill-with-docs |

---

## 2. Duplication Analysis

### 2.1 Duplication Hotspots (ranked by impact)

| Rank | Topic | Files | Skills | Total occ. | Impact |
|---|---|---|---|---|---|
| 1 | **Maven execution commands** | 21 | bugfix, implement, java-maven, mock-test | 85 | HIGH — same mvn patterns repeated across skills that should delegate to java-maven |
| 2 | **ReflectionTestUtils patterns** | 9 | implement, mock-test, skill-author | 28 | MEDIUM — concentrated in mock-test but leaked to implement |
| 3 | **Mockito diagnostic patterns** | 13 | bugfix, mock-test, java-maven | 27 | MEDIUM — bugfix's Mockito analysis duplicates mock-test's diagnosis |
| 4 | **Spring Boot Test knowledge** | 7 | java-maven, mock-test, skill-author | 14 | MEDIUM — scattered across skills that reference Spring Boot context |
| 5 | **Validation checklists** | 5 | bugfix, implement, java-maven, mock-test, skill-author | ~50 lines each | MEDIUM — each skill defines its own "Validation Checklist" with 80% overlap |
| 6 | **Completion checklists** | 3 | bugfix, implement, skill-author | ~20 lines each | LOW — short, similar structure, minor wording differences |
| 7 | **Retry checklists** | 2 | java-maven, mock-test | ~15 lines each | LOW — similar retry cycle patterns |

### 2.2 Specific Duplication Examples

**Maven commands duplicated across skills:**

bugfix/validation.md:
```
mvn -pl <mod> -am test -Dtest=FailingClass
mvn -pl <mod> -am test
mvn -pl <mod> -amd test
```

implement/validation.md:
```
mvn -pl <mod> -am compile
mvn -pl <mod> -am test -Dtest=...
mvn -pl <mod> -amd test
```

mock-test/workflow.md:
```
mvn -pl <module> -am test -Dtest=<TestClass>
```

**These should all reference java-maven instead of encoding Maven commands.**

**Validation Checklist overlap:**

bugfix/checklists.md — Validation Checklist:
- Exact symptom no longer reproduces ✓
- Failing test passes ✓
- Smallest validation scope chosen ✓
- Validation result documented ✓

implement/checklists.md — Validation Checklist:
- mock-test invoked if test fixtures affected ✓
- java-maven invoked for incremental compilation ✓
- java-maven invoked for incremental testing ✓
- Compilation succeeds ✓
- Affected module tests pass ✓

mock-test/checklists.md — Validation Checklist:
- Rule 1 pass: production-test structure synchronized ✓
- Rule 2 pass: fixtures correct ✓
- Rule 3 pass: mocks updated ✓
- Rule 4 pass: verifications updated ✓
- Rule 5 only if 1-4 confirmed ✓

**Each skill defines "validation" differently, but the core pattern is identical:**
verify fix → verify tests → verify no regression.

---

## 3. Proposed Directory Structure

```
.opencode/
  commands/             # [EXISTING] Keep as-is
  skills/               # [EXISTING] Keep as-is — do not move or rename
    bugfix/
    codegraph-helper/
    contract-maintainer/
    grill-with-docs/
    grilling/
    implement/
    java-maven/
    karpathy-guidelines/
    mock-test/
    openspec-apply-change/
    openspec-archive-change/
    openspec-explore/
    openspec-propose/
    skill-author/
    spec-updater/
    task-splitter/
  workflows/            # [NEW] Repository-level orchestration
    develop/            # implement → mock-test → java-maven → review
    bugfix/             # bugfix → mock-test → java-maven → review
    review/             # review workflow (orchestrates code review)
    release/            # release workflow (build → test → deploy)
    openspec/           # OpenSpec lifecycle (propose → apply → archive)
  playbooks/            # [NEW] Reusable engineering knowledge
    maven.md            # Maven lifecycle, commands, best practices
    mockito.md          # Mockito patterns, matchers, anti-patterns
    spring-boot-test.md # Spring Boot test patterns, slices, context
    reflection-test-utils.md  # ReflectionTestUtils field/private testing
    junit.md            # JUnit 4/5 patterns, assertions, conventions
    testing.md          # General testing strategy, coverage, TDD
  knowledge/            # [NEW] Project-specific reference material
    architecture.md     # Service architecture, module boundaries
    domain-terms.md     # Domain-specific terminology
    coding-conventions.md     # Code style, naming, package structure
    contract-conventions.md   # Contract format, fields, validation rules
  templates/            # [NEW] Reusable document templates
    implementation-report.md  # Template for implement completion report
    bug-report.md       # Template for bugfix completion report
    review-report.md    # Template for code review report
    acceptance-report.md     # Template for acceptance verification
    task-summary.md     # Template for task card summary
  checklists/           # [NEW] Shared checklists (canonical versions)
    validation.md       # Shared validation checklist
    completion.md       # Shared completion checklist
    retry.md            # Shared retry checklist
    review.md           # Shared review checklist
    release.md          # Shared release checklist
```

---

## 4. Migration Plan

### Phase A — Create Directories (additive, zero risk)

Create the five new directories:

```powershell
New-Item -ItemType Directory -Path .opencode/workflows -Force
New-Item -ItemType Directory -Path .opencode/playbooks -Force
New-Item -ItemType Directory -Path .opencode/knowledge -Force
New-Item -ItemType Directory -Path .opencode/templates -Force
New-Item -ItemType Directory -Path .opencode/checklists -Force
```

**Risk:** None — additive only. No existing behavior changes.

### Phase B — Extract Playbooks (knowledge extraction)

For each playbook, extract reusable knowledge from Skills:

| Playbook | Source skills | Extraction |
|---|---|---|
| `maven.md` | java-maven, bugfix, implement, mock-test | Maven lifecycle selection, flag usage, wrapper support, multi-module commands |
| `mockito.md` | mock-test, bugfix | Matcher selection guide, stubbing patterns, verification patterns, ArgumentCaptor |
| `spring-boot-test.md` | mock-test, java-maven | @SpringBootTest patterns, @MockBean/@SpyBean, context configuration |
| `reflection-test-utils.md` | mock-test, implement, skill-author | setField patterns, private method testing, static mocking |
| `junit.md` | mock-test | JUnit 4 vs 5 differences, extension model, parameterized tests |
| `testing.md` | bugfix, mock-test | Test strategy, coverage guidelines, TDD workflow |

**Risk:** Low — additive files. Skills reference them by path. No removal from skills yet.

### Phase C — Simplify Skills (remove embedded knowledge)

For each affected Skill, replace embedded engineering knowledge with playbook references:

| Skill | Remove | Replace with |
|---|---|---|
| `bugfix/analysis.md` | Mockito diagnostic patterns | Reference `playbooks/mockito.md` |
| `bugfix/examples.md` | Maven command examples | Reference `workflows/bugfix.md` + `playbooks/maven.md` |
| `bugfix/repair.md` | Maven delegation commands | Reference `playbooks/maven.md` |
| `bugfix/validation.md` | Maven command snippets | Reference `playbooks/maven.md` |
| `implement/validation.md` | Maven command snippets | Reference `playbooks/maven.md` |
| `implement/examples.md` | ReflectionTestUtils patterns | Reference `playbooks/reflection-test-utils.md` |
| `mock-test/fixture.md` | ReflectionTestUtils details | Extract to `playbooks/reflection-test-utils.md`, leave summary |
| `mock-test/mockito.md` | Matcher selection guide | Extract to `playbooks/mockito.md`, leave summary |
| `mock-test/examples.md` | Spring Boot test examples | Reference `playbooks/spring-boot-test.md` |
| `mock-test/diagnosis.md` | Maven retry commands | Reference `playbooks/maven.md` |
| `skill-author/design.md` | JUnit/Mockito/Spring reference | Reference `playbooks/` |

**Risk:** Medium — each edit must preserve the skill's workflow integrity. Changes are
reductive (removing duplicate knowledge, keeping orchestration logic). Revertable.

### Phase D — Standardize Frontmatter

For the 8 Skills with missing/weak descriptions:

| Skill | Current | Target |
|---|---|---|
| `openspec-explore/SKILL.md` | Chinese description only | Add English + Chinese, add trigger phrases |
| `openspec-propose/SKILL.md` | Chinese description only | Add English + Chinese |
| `openspec-apply-change/SKILL.md` | Chinese description only | Add English + Chinese |
| `openspec-archive-change/SKILL.md` | Chinese description only | Add English + Chinese |
| `spec-updater/SKILL.md` | Minimal description | Add trigger phrases |
| `task-splitter/SKILL.md` | Minimal description | Add trigger phrases |
| `contract-maintainer/SKILL.md` | Minimal description | Add trigger phrases |
| `codegraph-helper/SKILL.md` | Minimal description | Add trigger phrases |

**Risk:** Low — frontmatter edits only. No behavioral change.

### Phase E — Unify Entrypoint Naming

Rename `SKILL.md` → `skill.md` for the 8 Skills using the old convention.

**Exception:** `skill-author/SKILL.md` may remain as SKILL.md if the meta-skill's
validation scripts expect that exact filename.

**Risk:** Low — OpenCode resolves both cases. Update symlinks if any.

### Phase F — Create Workflows (orchestration)

| Workflow | Skills orchestrated |
|---|---|
| `workflows/develop/workflow.md` | implement → mock-test → java-maven → review → finish |
| `workflows/bugfix/workflow.md` | bugfix → mock-test → java-maven → review → finish |
| `workflows/review/workflow.md` | review orchestration |
| `workflows/release/workflow.md` | build → test → deploy orchestration |
| `workflows/openspec/workflow.md` | explore → propose → apply → archive |

**Risk:** Low — additive files. Each workflow references existing Skills by their
activation triggers.

### Phase G — Create Shared Checklists

| Checklist | Consolidates from |
|---|---|
| `checklists/validation.md` | bugfix, implement, java-maven, mock-test, skill-author |
| `checklists/completion.md` | bugfix, implement, skill-author |
| `checklists/retry.md` | java-maven, mock-test |

Simplify each skill's `checklists.md` to reference shared checklists instead of
duplicating their content:

```markdown
## Validation Checklist

Core validation items are in `.opencode/checklists/validation.md`.
Skill-specific additions:
- [ ] Mockito stubbing synchronized with production
- [ ] No UnnecessaryStubbingException
```

**Risk:** Low — additive + reductive. No behavior change.

---

## 5. Duplicated Content Mapping

| Content | Currently in | Should live in | Consolidation plan |
|---|---|---|---|
| Maven command templates | bugfix/validation.md, bugfix/examples.md, bugfix/repair.md, implement/validation.md, implement/planning.md, mock-test/workflow.md, mock-test/diagnosis.md | `java-maven/commands.md` (authoritative) + `playbooks/maven.md` (reference) | Remove from all non-java-maven skills. Replace with "Invoke java-maven" |
| ReflectionTestUtils.setField() patterns | mock-test/fixture.md (10 occ), mock-test/examples.md (5), implement/examples.md (2), skill-author/design.md (1) | `playbooks/reflection-test-utils.md` | Extract from fixture.md, leave concise rule summary |
| Mockito matcher selection | mock-test/mockito.md, bugfix/analysis.md, java-maven/diagnosis.md | `playbooks/mockito.md` | Extract to playbook, reference from skills |
| Spring Boot test patterns | mock-test/examples.md, mock-test/fixture.md, mock-test/workflow.md, java-maven/skill.md, skill-author/design.md | `playbooks/spring-boot-test.md` | Extract to playbook |
| Validation checklists | bugfix/checklists.md, implement/checklists.md, java-maven/checklists.md, mock-test/checklists.md, skill-author/checklists.md | `checklists/validation.md` | Create shared, simplify per-skill |
| Completion checklists | bugfix/checklists.md, implement/checklists.md, skill-author/checklists.md | `checklists/completion.md` | Create shared |
| Retry checklists | java-maven/checklists.md, mock-test/checklists.md | `checklists/retry.md` | Create shared |

---

## 6. Suggested Playbooks

### 6.1 `playbooks/maven.md`

Content:
- Maven lifecycle phases and what each includes
- When to use clean (dependency/plugin/generated-source changes)
- Multi-module flag guide (`-pl`, `-am`, `-amd`, `-f`)
- Wrapper detection and preference
- Common failure patterns and diagnosis
- settings.xml, profiles, and enterprise configuration

Source: Extracted from `java-maven/commands.md`, `java-maven/diagnosis.md`,
`java-maven/discovery.md`, duplicated fragments in bugfix and implement.

### 6.2 `playbooks/mockito.md`

Content:
- Matcher selection guide (eq, any, nullable, isNull, argThat)
- Stubbing patterns (when, doReturn, doThrow, doAnswer)
- Verification patterns (times, never, atLeastOnce, InOrder, timeout)
- ArgumentCaptor usage
- Lenient vs strict decisions
- Common Mockito exceptions and diagnosis

Source: Extracted from `mock-test/mockito.md`, `bugfix/analysis.md`.

### 6.3 `playbooks/spring-boot-test.md`

Content:
- @SpringBootTest configuration
- Test slices (@WebMvcTest, @DataJpaTest, etc.)
- @MockBean and @SpyBean patterns
- @TestPropertySource and dynamic properties
- @ContextConfiguration usage
- Spring context failure diagnosis

Source: Extracted from `mock-test/fixture.md`, `mock-test/examples.md`,
`java-maven/diagnosis.md`.

### 6.4 `playbooks/reflection-test-utils.md`

Content:
- setField for @Value, @Autowired, @Resource
- Private method testing with ReflectionTestUtils
- Static field manipulation
- Common pitfalls (wrong field name, type mismatch, null values)

Source: Extracted from `mock-test/fixture.md`, `mock-test/examples.md`.

### 6.5 `playbooks/junit.md`

Content:
- JUnit 4 vs 5 differences
- Extension model (@ExtendWith vs @RunWith)
- Parameterized tests
- Assertions (AssertJ, Hamcrest, JUnit)
- Test lifecycle (@Before, @BeforeEach)
- @Nested tests and test ordering

Source: Extracted from `mock-test/skill.md`, `mock-test/mockito.md`.

### 6.6 `playbooks/testing.md`

Content:
- Unit vs integration vs end-to-end testing strategy
- Coverage guidelines
- TDD workflow
- Test file organization
- Fixture management best practices

Source: Extracted from `bugfix/analysis.md`, `bugfix/examples.md`,
`mock-test/examples.md`.

---

## 7. Suggested Workflows

### 7.1 `workflows/develop/workflow.md`

```
Implement task card (implement)
  → Update test fixtures if needed (mock-test)
  → Compile and run tests (java-maven)
  → Request code review (review)
  → Finish
```

### 7.2 `workflows/bugfix/workflow.md`

```
Diagnose and fix (bugfix)
  → Update test fixtures if needed (mock-test)
  → Compile and run tests (java-maven)
  → Request code review (review)
  → Finish
```

### 7.3 `workflows/review/workflow.md`

```
Review code changes (review skill)
  → Provide feedback
  → Approve or request changes
  → Finish
```

### 7.4 `workflows/release/workflow.md`

```
Run full build (java-maven)
  → Run integration tests (java-maven verify)
  → Create release artifacts
  → Deploy
  → Finish
```

### 7.5 `workflows/openspec/workflow.md`

```
Explore and clarify (openspec-explore)
  → Propose change (openspec-propose)
  → Implement tasks (implement)
  → Archive completion (openspec-archive-change)
  → Finish
```

---

## 8. Suggested Shared Checklists

### 8.1 `checklists/validation.md`

```markdown
# Validation Checklist (Shared)

- [ ] The exact symptom no longer reproduces
- [ ] The failing test passes
- [ ] All tests in the affected module pass
- [ ] All tests in dependent modules pass (if API changed)
- [ ] Compilation succeeds
- [ ] No new warnings introduced
- [ ] Validation scope was the smallest appropriate
```

### 8.2 `checklists/completion.md`

```markdown
# Completion Checklist (Shared)

- [ ] Root cause documented
- [ ] Changes scoped to affected files only
- [ ] All acceptance criteria satisfied
- [ ] No pre-existing failures were silently fixed
- [ ] No unrelated refactoring performed
- [ ] Validation results documented
- [ ] User notified of completion
```

### 8.3 `checklists/retry.md`

```markdown
# Retry Checklist (Shared)

- [ ] Single blocking issue identified (not batch)
- [ ] Fix applied to correct location
- [ ] Smallest retry scope selected
- [ ] If passes: scope expanded
- [ ] If fails: re-diagnosed before next retry
- [ ] Max retries respected (3/cycle)
- [ ] Stopping condition checked before each retry
```

---

## 9. Suggested Shared Templates

| Template | Purpose | Source |
|---|---|---|
| `templates/implementation-report.md` | Post-implementation summary | `implement/workflow.md` Stage 13 |
| `templates/bug-report.md` | Bug fix completion summary | `bugfix/workflow.md` Stage 14 |
| `templates/review-report.md` | Code review findings | Not yet defined (future) |
| `templates/acceptance-report.md` | Acceptance criteria verification | `implement/validation.md` |
| `templates/task-summary.md` | Task card summary for planning | `implement/planning.md` |

---

## 10. Recommended Simplifications for Each Existing Skill

### bugfix (9 files, 866 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Embedding Maven commands in 3 files | Replace with "Invoke java-maven" references | Low |
| Embedding Mockito diagnostic patterns | Reference `playbooks/mockito.md` | Low |
| validation.md duplicates shared validation patterns | Reference `checklists/validation.md` | Low |
| Embedded Maven examples in examples.md | Reference workflow level + java-maven | Low |

**Simplified target:** ~650 lines (removing ~216 lines of duplicated knowledge).

### implement (8 files, 757 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Embedding Maven commands in validation.md | Replace with "Invoke java-maven" | Low |
| Embedding ReflectionTestUtils in examples.md | Reference `playbooks/reflection-test-utils.md` | Low |
| validation.md duplicates shared validation | Reference `checklists/validation.md` | Low |

**Simplified target:** ~680 lines.

### java-maven (8 files, 670 lines)

**Note:** java-maven is the authoritative Maven skill. Keep it intact as the source
of truth. No simplification needed — it should be the canonical reference.

| Issue | Recommendation | Effort |
|---|---|---|
| None | This is the source skill. Keep as-is. | None |

### mock-test (8 files, 981 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| fixture.md embeds ReflectionTestUtils knowledge | Extract detailed patterns to `playbooks/reflection-test-utils.md`, leave rule summaries | Medium |
| mockito.md embeds matcher selection guide | Extract to `playbooks/mockito.md`, leave workflow-specific decision rules | Medium |
| diagnosis.md references Maven retry commands | Reference java-maven or `playbooks/maven.md` | Low |
| examples.md duplicates Spring Boot knowledge | Reference `playbooks/spring-boot-test.md` | Low |
| Maven command in workflow.md | Reference java-maven invocation | Low |

**Simplified target:** ~700 lines (removing ~280 lines of extracted knowledge).

### skill-author (6 files, 574 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| design.md embeds JUnit/Mockito/Spring reference | Reference `playbooks/` section | Low |
| Lists framework names as reference points | Keep — this is meta-knowledge about what skills should reference | None |

**Simplified target:** ~540 lines.

### openspec-explore (1 file, 215 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Single monolithic file | Consider splitting: skill.md (entry) + workflow.md | Medium |
| No English description in frontmatter | Add English description + trigger phrases | Low |

### openspec-apply-change (1 file, 117 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Single monolithic file | Consider splitting into skill.md + workflow.md | Low |
| No frontmatter description | Add description | Low |

### openspec-propose (1 file, 86 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Single file — acceptable | May stay as-is (compact enough) | None |
| No frontmatter description | Add description | Low |

### openspec-archive-change (1 file, 81 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Single file — acceptable | May stay as-is | None |
| No frontmatter description | Add description | Low |

### spec-updater (1 file, 211 lines + 184-line script)

| Issue | Recommendation | Effort |
|---|---|---|
| Single monolithic skill file | Split into skill.md + workflow.md | Medium |
| No frontmatter description | Add description with trigger phrases | Low |

### task-splitter (1 file, 148 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Single file — borderline | Consider splitting if 148 lines grows | Low |
| No frontmatter description | Add description | Low |

### contract-maintainer (1 file, 105 lines + 322-line script + 4-line YAML)

| Issue | Recommendation | Effort |
|---|---|---|
| Python script (322 lines) is external — keep as-is | Acceptable as-is | None |
| No frontmatter description | Add description | Low |

### codegraph-helper (1 file, 72 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Compact — acceptable as-is | Keep | None |
| No frontmatter description | Add description | Low |

### karpathy-guidelines (1 file, 47 lines)

| Issue | Recommendation | Effort |
|---|---|---|
| Compact — acceptable as-is | Keep | None |
| Has description ✓ | Good | None |

### grilling / grill-with-docs (7 lines each)

| Issue | Recommendation | Effort |
|---|---|---|
| Minimal trigger skills — keep as-is | Keep | None |

---

## 11. Summary of Recommendations

### Phase A — Create (zero risk, immediate)

| Action | Files |
|---|---|
| Create `.opencode/workflows/` | 1 directory |
| Create `.opencode/playbooks/` | 1 directory |
| Create `.opencode/knowledge/` | 1 directory |
| Create `.opencode/templates/` | 1 directory |
| Create `.opencode/checklists/` | 1 directory |
| Create `playbooks/maven.md` | 1 file |
| Create `playbooks/mockito.md` | 1 file |
| Create `playbooks/spring-boot-test.md` | 1 file |
| Create `playbooks/reflection-test-utils.md` | 1 file |
| Create `playbooks/junit.md` | 1 file |
| Create `playbooks/testing.md` | 1 file |
| Create `checklists/validation.md` | 1 file |
| Create `checklists/completion.md` | 1 file |
| Create `checklists/retry.md` | 1 file |
| Create `workflows/develop/workflow.md` | 1 file |
| Create `workflows/bugfix/workflow.md` | 1 file |
| Create `workflows/review/workflow.md` | 1 file |
| Create `workflows/release/workflow.md` | 1 file |
| Create `workflows/openspec/workflow.md` | 1 file |
| Create `templates/implementation-report.md` | 1 file |
| Create `templates/bug-report.md` | 1 file |
| Create `templates/acceptance-report.md` | 1 file |

### Phase B — Simplify (low risk, reversible)

| Action | Skills affected |
|---|---|
| Replace embedded Maven commands with java-maven references | bugfix, implement, mock-test |
| Extract Mockito knowledge to playbook | bugfix, mock-test |
| Extract ReflectionTestUtils to playbook | mock-test, implement |
| Extract Spring Boot to playbook | mock-test, java-maven |
| Simplify checklists with shared references | bugfix, implement, java-maven, mock-test, skill-author |

### Phase C — Standardize (low risk)

| Action | Skills affected |
|---|---|
| Add frontmatter descriptions | 8 skills |
| Rename SKILL.md → skill.md | 8 skills |

### Phase D — Split (medium risk, optional)

| Action | Skills affected |
|---|---|
| Split monolithic SKILL.md files | openspec-explore, openspec-apply-change, spec-updater |

---

## 12. Backward Compatibility Guarantee

| Change type | Compatible? | Reason |
|---|---|---|
| Adding `.opencode/workflows/` | Yes — additive, no existing code references it |
| Adding `.opencode/playbooks/` | Yes — additive |
| Adding `.opencode/knowledge/` | Yes — additive |
| Adding `.opencode/templates/` | Yes — additive |
| Adding `.opencode/checklists/` | Yes — additive |
| Adding files to existing skills | Yes — additive |
| Simplifying skill content | Yes — workflow logic preserved, knowledge extracted |
| Renaming SKILL.md → skill.md | Yes — OpenCode resolves both case variants |
| Updating frontmatter descriptions | Yes — no behavioral change |
| Splitting monolithic skills | Yes — new files loaded automatically, old entrypoint remains |

**No destructive operations are proposed.**
**No existing skill is moved or removed.**
**No invocation semantics change.**

---

## 13. Skill Dependency Graph

### 13.1 Dependency Map

```
                          ┌─────────────────────────────────────────────┐
                          │              Foundation Layer              │
                          │                                             │
                          │  java-maven     codegraph-helper            │
                          │  (Maven exec)   (code analysis)             │
                          │                                             │
                          │  karpathy-guidelines                        │
                          │  (coding principles)                        │
                          └──────────────────────┬──────────────────────┘
                                                 │
                          ┌──────────────────────┴──────────────────────┐
                          │             Test Maintenance Layer         │
                          │                                             │
                          │  mock-test                                  │
                          │  delegates to: java-maven                   │
                          └──────────────────────┬──────────────────────┘
                                                 │
                          ┌──────────────────────┴──────────────────────┐
                          │           Orchestration Layer              │
                          │                                             │
                          │  bugfix                implement            │
                          │  delegates to:         delegates to:        │
                          │    ├─ mock-test          ├─ mock-test       │
                          │    ├─ java-maven         ├─ java-maven      │
                          │    ├─ review*            ├─ review*         │
                          │    └─ spec               └─ contract*       │
                          │                                             │
                          │  * = skill not yet created                 │
                          └──────────────────────┬──────────────────────┘
                                                 │
                          ┌──────────────────────┴──────────────────────┐
                          │           OpenSpec Lifecycle Layer         │
                          │                                             │
                          │  openspec-explore     (standalone)          │
                          │  openspec-propose     (standalone)          │
                          │  openspec-apply-change(standalone)          │
                          │  openspec-archive-change(standalone)         │
                          │                                             │
                          │  spec-updater                              │
                          │  triggers: contract-maintainer              │
                          │                                             │
                          │  task-splitter                             │
                          │  depends on: spec-updater,                  │
                          │              contract-maintainer            │
                          │                                             │
                          │  contract-maintainer  (standalone)          │
                          └──────────────────────┬──────────────────────┘
                                                 │
                          ┌──────────────────────┴──────────────────────┐
                          │               Meta Layer                   │
                          │                                             │
                          │  skill-author        (standalone)           │
                          │  grilling            (standalone)           │
                          │  grill-with-docs     (standalone)           │
                          └─────────────────────────────────────────────┘
```

### 13.2 Dependency Table

| Skill | Depends on | Delegates to | Invoked by |
|---|---|---|---|
| bugfix | — | mock-test, java-maven, review*, spec* | user, workflow/bugfix |
| implement | spec, contracts, tasks, sequence | mock-test, java-maven, review*, contract* | user, workflow/develop |
| mock-test | — | java-maven | bugfix, implement |
| java-maven | — | — | bugfix, implement, mock-test, workflow/* |
| skill-author | — | — | user (meta-skill) |
| spec-updater | — | contract-maintainer | user |
| task-splitter | spec-updater, contract-maintainer | — | user |
| contract-maintainer | — | — | spec-updater, user |
| openspec-explore | — | — | user |
| openspec-propose | — | — | user |
| openspec-apply-change | — | — | user |
| openspec-archive-change | — | — | user |
| codegraph-helper | — | — | user |
| karpathy-guidelines | — | — | user (behavioral overlay) |
| grilling | — | — | user |
| grill-with-docs | — | grilling | user |

*\* = planned/recommended skill, not yet created.*

### 13.3 Dependency Rules

| Rule | Enforcement |
|---|---|
| No circular dependencies | Dependency graph must remain a DAG |
| Foundation skills never depend on orchestration | java-maven must never depend on bugfix or implement |
| Orchestration skills never depend on OpenSpec | bugfix and implement must never depend on openspc-* |
| Test skills depend only on foundation | mock-test must only depend on java-maven |
| Meta skills depend on nothing | skill-author must remain standalone |

### 13.4 Missing Skills (Gaps in the Graph)

| Missing skill | Would be used by | Priority |
|---|---|---|
| review | bugfix, implement, workflow/develop, workflow/bugfix | HIGH — no code review Skill exists |
| release/deploy | workflow/release | MEDIUM — no release orchestration |
| rollback | workflow/release (failure path) | LOW — no rollback Skill |
| performance-analysis | bugfix (when bug is performance-related) | LOW — no perf Skill |

---

## 14. Workflow Inventory

### 14.1 Current (Ad-hoc) Workflows

| Workflow | Trigger | Steps | Pain points |
|---|---|---|---|
| Feature development | User describes feature | explore → propose → apply → (manual Maven) → archive | Maven/test/validation done ad-hoc; no structured delegation to java-maven/mock-test |
| Bugfix | User reports bug | (manual debug) → fix → (manual test) | No diagnostic workflow; test maintenance manual; no regression check |
| Code review | User request | (manual diff review) → comments | No structured review Skill or workflow |
| Release | User request | (manual build) → (manual deploy) | Entirely manual; no orchestration |

### 14.2 Proposed Orchestrated Workflows

**Workflow: develop** — Feature development

```
Start
  ↓
implement (read task card → plan → WAIT → implement)
  ↓
[mock-test invoked if production signatures changed]
  ↓
[java-maven invoked for incremental compile + test]
  ↓
review (request code review of the change)
  ↓
[If review approves → finish]
  ↓
[If review requests changes → return to implement]
  ↓
Finish
```

**Workflow: bugfix** — Bug resolution

```
Start
  ↓
bugfix (observe → collect evidence → analyze → repair → validate)
  ↓
[mock-test invoked if production signatures changed]
  ↓
[java-maven invoked for incremental compile + test]
  ↓
review (request code review of the fix)
  ↓
[If review approves → finish]
  ↓
[If review requests changes → return to bugfix]
  ↓
Finish
```

**Workflow: review** — Code review

```
Start
  ↓
Load diff of the change
  ↓
Check against coding conventions (.opencode/knowledge/coding-conventions.md)
  ↓
Check against architecture rules (.opencode/knowledge/architecture.md)
  ↓
Check against testing patterns (.opencode/playbooks/testing.md)
  ↓
Produce review report (.opencode/templates/review-report.md)
  ↓
Finish
```

**Workflow: release** — Release pipeline

```
Start
  ↓
java-maven (full repository verify)
  ↓
[java-maven runs integration tests]
  ↓
[Create release artifacts]
  ↓
[Deploy to target environment]
  ↓
[Run smoke tests]
  ↓
Finish
```

**Workflow: openspec** — OpenSpec lifecycle

```
Start
  ↓
openspec-explore (clarify requirements)
  ↓
openspec-propose (generate proposal/design/tasks)
  ↓
spec-updater (if spec changes needed)
  ↓
contract-maintainer (generate/update contracts)
  ↓
task-splitter (split into task cards)
  ↓
[For each task card: invoke workflow/develop]
  ↓
openspec-archive-change (archive completed change)
  ↓
Finish
```

### 14.3 Workflow vs Skill Responsibility Matrix

| Activity | Workflow (orchestration) | Skill (execution) |
|---|---|---|
| Task understanding | develop | implement (Stage 1-3) |
| Fix diagnosis | bugfix | bugfix (Stage 1-9) |
| Test maintenance | develop, bugfix | mock-test |
| Maven execution | develop, bugfix, release | java-maven |
| Code review | develop, bugfix | review (proposed) |
| Release build | release | java-maven |
| Deploy | release | deploy (proposed) |
| Spec change | openspec | spec-updater |
| Contract generation | openspec | contract-maintainer |
| Task decomposition | openspec | task-splitter |

---

## 15. Capability Matrix

### 15.1 Capability Inventory

| Capability | Owner Skill | Shared? | Duplicated in? | Missing? |
|---|---|---|---|---|
| Maven command generation | java-maven | No — intended as sole owner | bugfix (3 files), implement (2 files), mock-test (2 files) | — |
| Maven failure diagnosis | java-maven | No | mock-test (diagnosis.md) | — |
| Test fixture maintenance | mock-test | No — sole owner | — | — |
| Mockito analysis | mock-test | Partial | bugfix (analysis.md) | — |
| ReflectionTestUtils | mock-test | Partial | implement (examples.md) | — |
| Stack trace triage | bugfix | No | — | — |
| Root cause analysis | bugfix | No | — | — |
| Repair design | bugfix | No | — | — |
| Incremental retry | java-maven | No | mock-test (workflow.md) | — |
| Code review | — | — | — | **MISSING** |
| Release pipeline | — | — | — | **MISSING** |
| Deploy | — | — | — | **MISSING** |
| Rollback | — | — | — | **MISSING** |
| Performance analysis | — | — | — | **MISSING** |
| Security review | — | — | — | **MISSING** |
| Spec management | spec-updater | No | — | — |
| Contract generation | contract-maintainer | No | — | — |
| Task decomposition | task-splitter | No | — | — |
| Skill generation | skill-author | No | — | — |
| Codebase exploration | codegraph-helper | No | — | — |
| Design questioning | grilling | No | — | — |

### 15.2 Capability Distribution

```
                    ┌──────────────────────────────────────────┐
                    │        LAYER 1: FOUNDATION              │
                    │                                          │
                    │  Maven  │  Code    │  Git     │  JUnit   │
                    │  exec   │  graph   │  diff    │  basics  │
                    │  ─────  │  ─────   │  ─────   │  ─────  │
                    │  java-  │  code-   │  built-  │  (know- │
                    │  maven  │  graph-  │  in to   │  ledge)  │
                    │         │  helper  │  tools   │          │
                    └──────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
     ┌────────────────────────────┐  ┌────────────────────────────┐
     │   LAYER 2: TEST           │  │   LAYER 2: ANALYSIS       │
     │                            │  │                            │
     │  Fixture  │  Mockito  │   │  │  Stack    │  Root    │     │
     │  sync     │  maint    │   │  │  trace    │  cause   │     │
     │  ──────── │  ───────  │   │  │  ───────  │  ──────  │     │
     │  mock-    │  mock-    │   │  │  bugfix   │  bugfix  │     │
     │  test     │  test     │   │  │           │          │     │
     └────────────────────────────┘  └────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
     ┌────────────────────────────┐  ┌────────────────────────────┐
     │   LAYER 3: ORCHESTRATION  │  │   LAYER 3: OPENSEPC       │
     │                            │  │                            │
     │  Bug     │  Feature  │    │  │  Spec    │  Contract  │   │
     │  fix     │  develop  │    │  │  update  │  generate  │   │
     │  ─────   │  ────────  │    │  │  ─────   │  ────────  │   │
     │  bugfix  │  implement │    │  │  spec-   │  contract- │   │
     │          │            │    │  │  updater │  maintainer│   │
     └────────────────────────────┘  └────────────────────────────┘
```

### 15.3 Missing Capabilities (Gap Analysis)

| Capability | Impact | Workaround | Recommended action |
|---|---|---|---|
| Code review | HIGH — no structured review process | Manual ad-hoc review | Create `review` Skill |
| Release pipeline | MEDIUM — no repeatable release | Manual steps | Create `release` Skill |
| Deploy automation | MEDIUM — no deploy orchestration | Manual deploy | Create `deploy` Skill |
| Rollback | LOW — no rollback process | Manual rollback | Create `rollback` Skill (future) |
| Performance analysis | LOW — no perf regression detection | Manual profiling | Create `performance` Skill (future) |
| Security review | LOW — no security audit | Manual review | Create `security` Skill (future) |

---

## 16. Shared Asset Matrix

### 16.1 Asset Classification Framework

| Asset type | Content | Characteristics | Location |
|---|---|---|---|
| Playbook | Engineering best practices, diagnostic patterns, common pitfalls | Reusable across projects, language-level knowledge | `.opencode/playbooks/` |
| Checklist | Verifiable item lists for quality gates | Mechanical, can be executed step-by-step | `.opencode/checklists/` |
| Template | Document structure with placeholders | Fill-in-the-blank format for reports | `.opencode/templates/` |
| Knowledge | Project-specific description, architecture, terminology | Descriptive, not procedural; project-bound | `.opencode/knowledge/` |

### 16.2 Asset Extraction Candidates

| Source (current location) | Content | Best suited as | Reason |
|---|---|---|---|
| `java-maven/commands.md` | Lifecycle phases, flag selection, wrapper usage | `playbooks/maven.md` | Language-level knowledge, reusable across all Java projects |
| `java-maven/diagnosis.md` | Compilation, Surefire, dependency failure patterns | `playbooks/maven.md` | Diagnostic knowledge, reusable |
| `java-maven/discovery.md` | Repository root, module, wrapper discovery | `playbooks/maven.md` | Procedural knowledge for Maven projects |
| `mock-test/mockito.md` | Matcher selection, stubbing patterns, verification | `playbooks/mockito.md` | Framework-level knowledge, reusable |
| `mock-test/fixture.md` | ReflectionTestUtils.setField patterns | `playbooks/reflection-test-utils.md` | Utility knowledge, reusable |
| `mock-test/examples.md` | Spring Boot test configuration | `playbooks/spring-boot-test.md` | Framework knowledge, reusable |
| `mock-test/fixture.md` | @MockBean, @SpyBean, @TestPropertySource | `playbooks/spring-boot-test.md` | Framework knowledge, reusable |
| `mock-test/skill.md` | JUnit 4/5 environment listing | `playbooks/junit.md` | Framework reference, reusable |
| `bugfix/analysis.md` | Stack trace analysis patterns | `playbooks/testing.md` | Diagnostic knowledge, reusable |
| `bugfix/examples.md` | Test failure diagnosis flows | `playbooks/testing.md` | Diagnostic knowledge, reusable |
| `bugfix/checklists.md` (Validation) | Validation checklist items | `checklists/validation.md` | Shared quality gate |
| `implement/checklists.md` (Validation) | Validation checklist items | `checklists/validation.md` | Shared quality gate |
| `mock-test/checklists.md` (Validation) | Validation checklist items | `checklists/validation.md` | Shared quality gate |
| `java-maven/checklists.md` (Retry) | Retry checklist items | `checklists/retry.md` | Shared process |
| `mock-test/checklists.md` (Retry) | Retry checklist items | `checklists/retry.md` | Shared process |
| `bugfix/checklists.md` (Completion) | Completion checklist | `checklists/completion.md` | Shared process |
| `implement/checklists.md` (Completion) | Completion checklist | `checklists/completion.md` | Shared process |
| `implement/workflow.md` (Stage 13) | Implementation report format | `templates/implementation-report.md` | Reusable document format |
| `bugfix/workflow.md` (Stage 14) | Bugfix report format | `templates/bug-report.md` | Reusable document format |
| `implement/validation.md` | Acceptance report format | `templates/acceptance-report.md` | Reusable document format |
| `AGENTS.md` | Project architecture, services, conventions | `knowledge/architecture.md`, `knowledge/coding-conventions.md` | Project-specific, descriptive |
| `source/clarification-record.md` | Domain terms, decisions | `knowledge/domain-terms.md` | Project-specific reference |

### 16.3 Asset Ownership After Extraction

| Asset | Authoritative source | Can be referenced by |
|---|---|---|
| `playbooks/maven.md` | java-maven (commands.md, diagnosis.md, discovery.md) | bugfix, implement, mock-test, workflow/* |
| `playbooks/mockito.md` | mock-test (mockito.md) | bugfix, mock-test |
| `playbooks/reflection-test-utils.md` | mock-test (fixture.md) | mock-test, implement |
| `playbooks/spring-boot-test.md` | mock-test (fixture.md, examples.md) | mock-test, java-maven |
| `playbooks/junit.md` | mock-test | mock-test, skill-author |
| `playbooks/testing.md` | bugfix (analysis.md, examples.md) | bugfix, mock-test |
| `checklists/validation.md` | Shared (extracted from 5 skills) | All skills that need validation |
| `checklists/completion.md` | Shared (extracted from 3 skills) | bugfix, implement, skill-author |
| `checklists/retry.md` | Shared (extracted from 2 skills) | java-maven, mock-test |
| `templates/implementation-report.md` | implement (workflow.md) | implement |
| `templates/bug-report.md` | bugfix (workflow.md) | bugfix |
| `templates/acceptance-report.md` | implement (validation.md) | implement |
| `knowledge/architecture.md` | AGENTS.md, project resources | All skills |
| `knowledge/domain-terms.md` | Clarification records, specs | All skills |
| `knowledge/coding-conventions.md` | Project conventions, existing code | review (proposed), bugfix, implement |

### 16.4 Reference Pattern

When a Skill references a shared asset, use this pattern:

```markdown
## Maven Execution

For Maven lifecycle selection and command generation, see:
`.opencode/playbooks/maven.md`

For this specific task:
- Invoke java-maven with scope: `mvn -pl <mod> -am compile`
- See playbooks/maven.md §Multi-Module for flag selection
```

This ensures the Skill remains concise while the detailed knowledge lives in the playbook.

---

## 17. Repository Evolution Roadmap

### 17.1 Principles for Adding New Skills

Every new Skill added to this repository must follow these rules:

| Principle | Enforcement |
|---|---|
| **Single responsibility** | The Skill must do one thing. Test: can you describe it in one sentence without "and"? |
| **No capability overlap** | Search existing skills before creating. If overlap > 30%, extend existing; if > 60%, refuse. |
| **Proper layering** | Foundation skills (Layer 1) must not depend on orchestration skills (Layer 3). |
| **No circular deps** | Dependency graph must remain acyclic. Run `codegraph-helper` to verify. |
| **Dependency declaration** | Every skill's frontmatter description must mention skills it delegates to. |
| **skill.md entrypoint** | Use `skill.md` (not `SKILL.md`). Follow the modular convention. |
| **YAML frontmatter** | Must include `name`, `description` with trigger phrases AND anti-triggers. |
| **Playbook-first knowledge** | If content exceeds 5 lines of reusable knowledge, extract to `.opencode/playbooks/`. |
| **Template-first reports** | If the skill produces a report, reference `.opencode/templates/` for the format. |
| **Checklist-first validation** | If the skill validates outcomes, reference `.opencode/checklists/` for shared items. |

### 17.2 New Skill Request Template

When proposing a new Skill, the request must include:

```markdown
## New Skill Proposal

Name: <kebab-case-name>
Layer: foundation | test | orchestration | openspec | meta
Purpose: <one sentence>

Trigger patterns:
  - "<phrase 1>"
  - "<phrase 2>"

Delegates to: [skills this skill will call]
Depends on:   [skills that must exist first]
Overlap check: [search terms used, skills found, overlap %]

Files:
  skill.md
  workflow.md (if >5 stages)
  decision.md (if >5 decision points)
  checklists.md (skill-specific items; shared items go in .opencode/checklists/)
```

### 17.3 Priority-Ranked Future Skills

| Priority | Skill | Layer | Prerequisites | Rationale |
|---|---|---|---|---|
| **P0** | `review` | orchestration | bugfix, implement | No code review capability exists. Required for completing develop/bugfix workflows. |
| **P1** | `release` | orchestration | java-maven | No release pipeline. Required for deploy automation. |
| **P1** | `deploy` | orchestration | release | No deploy orchestration. Required for production releases. |
| **P2** | `rollback` | orchestration | deploy | Low priority — emergency use only. |
| **P3** | `performance` | test | java-maven | Low priority — no perf regression detection today. |
| **P3** | `security` | analysis | codegraph-helper | Low priority — no security audit automation. |

### 17.4 Naming Convention Enforcement

All Skills must follow:

| Aspect | Convention | Example |
|---|---|---|
| Directory name | kebab-case, one word preferred | `bugfix`, `java-maven`, `mock-test` |
| Entrypoint file | `skill.md` | `skill.md` |
| Workflow file | `workflow.md` | `workflow.md` |
| Decision file | `decision.md` | `decision.md` |
| Checklist file | `checklists.md` | `checklists.md` |
| Anti-patterns file | `anti-patterns.md` | `anti-patterns.md` |
| Examples file | `examples.md` | `examples.md` |
| YAML frontmatter name | matches directory name exactly | `name: bugfix` |

### 17.5 Migration Path for Existing Monolithic Skills

For the 7 single-file Skills, a two-phase migration:

**Phase 1 (immediate, compatible):**
1. Add proper YAML frontmatter with description and trigger phrases
2. Rename `SKILL.md` to `skill.md`

**Phase 2 (when the skill exceeds ~150 lines):**
1. Extract workflow stages to `workflow.md`
2. Extract decision tables to `decision.md`
3. Keep `skill.md` as the concise entrypoint

### 17.6 Quality Gate for New Skills

Before a new Skill is accepted into the repository, it must pass:

- [ ] No overlap with existing skills (search `.opencode/skills/`)
- [ ] `skill.md` exists with YAML frontmatter
- [ ] `name:` matches directory name
- [ ] `description:` includes triggers and anti-triggers
- [ ] Single responsibility confirmed (one-sentence test)
- [ ] Dependency graph remains acyclic
- [ ] No Maven commands hardcoded (use java-maven delegation)
- [ ] No test fixture logic hardcoded (use mock-test delegation)
- [ ] No embedded checklists that duplicate `checklists/` files
- [ ] No embedded templates that duplicate `templates/` files
- [ ] No project-specific assumptions (use `.opencode/knowledge/` for those)
- [ ] Follows the modular convention (split across files by responsibility)
