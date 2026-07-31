# Decision Rules

## Activation

| Condition | Decision |
|---|---|
| pom.xml exists in repo AND user goal is build/test/compile/package | Activate |
| pom.xml changed in working tree | Activate |
| Test compilation or execution failed | Activate |
| User asks for Maven help without executing | Do NOT activate |
| No pom.xml found | Stop: "Not a Maven project" |

## Scope Selection

Always choose the smallest scope that achieves the goal:

| Goal | Smallest scope |
|---|---|
| Check compilation | `compile` |
| Check test compilation | `test-compile` |
| Run one test method | `test -Dtest=Class#method` |
| Run one test class | `test -Dtest=Class` |
| Run module tests | `-pl mod -am test` |
| Create artifact | `-pl mod -am package -DskipTests` (if tests already ran) |
| Full quality check | `-pl mod -am verify` |
| Deploy | `deploy` (only when explicitly requested) |

**Escalation rule:** If the scope produces an error unrelated to the goal,
escalate one level and re-run. Otherwise, fix the error and retry at the
same scope.

## Lifecycle Decisions

| Task | Phase | Why not higher |
|---|---|---|
| Verify code compiles | `compile` | `test-compile` would compile test sources unnecessarily |
| Verify tests compile | `test-compile` | `test` would run them unnecessarily |
| Run unit tests | `test` | `verify` would run integration tests |
| Run integration tests | `verify` | `install` would copy artifacts to local repo |
| Publish artifact | `deploy` | Only for release pipelines |

## Clean Build Decisions

Add `clean` only when:

| Condition | Reason |
|---|---|
| `<dependencies>` added/removed/changed | Stale classpath may hide errors |
| Maven plugin version changed | Plugin output may differ |
| Annotation processor config changed | Generated sources must regenerate |
| Build output corrupted (missing classes) | Incremental compilation can't recover |
| User explicitly requests clean build | User knows best |

**Never** default to `clean`. Always explain why `clean` is needed.

## Stopping Conditions

| Condition | Action |
|---|---|
| No pom.xml found | Stop, report "Not a Maven project" |
| Wrapper script not found, mvn not in PATH | Stop, report "Maven not available" |
| Build succeeds | Stop, report success summary |
| Build fails, retry ≥ 3 | Stop, report unresolved |
| User cancels | Stop |
| Dependency cannot be resolved from any repo | Stop, report missing artifact |
