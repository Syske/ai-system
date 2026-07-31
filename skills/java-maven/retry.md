# Retry Strategy

## Core Principle

Never blindly rerun Maven. Each retry must follow:
**Fix → Retry smallest scope → Observe → Expand → Stop**

## Retry Flow

```
Build fails
  ↓
Stage 7: Diagnose failure
  ↓
Fix ONE blocking issue (not batch fixes)
  ↓
Retry at the SMALLEST possible scope for the fix
  ↓
  ├─ Pass → Expand scope to verify fix doesn't break dependents
  │           ├─ Pass → Done
  │           └─ Fail → Diagnose new failure → Fix → Retry
  │
  └─ Fail → Diagnose new failure
              ├─ Same issue? → Fix wasn't correct → Re-fix → Retry
              └─ New issue?  → Fix introduced new problem → Revert → Re-diagnose
```

## Scope Expansion Progression

After a fix passes at the smallest scope, expand gradually:

```
Round 1:  mvn -pl <mod> -am compile            (fix compilation)
Round 2:  mvn -pl <mod> -am test               (run module tests)
Round 3:  mvn -pl <mod> -amd test              (run dependents' tests)
Round 4:  mvn -f <root> test                    (run full test suite — optional)
```

Each round only proceeds if the previous round passes.

## Retry Cycle Rules

| Rule | Value |
|---|---|
| Max retries per module | 3 |
| Max retries per project | 5 |
| Fixes per retry | Exactly 1 |
| Scope per retry | Smallest possible for the fix |
| First action on retry | Re-diagnose (don't assume same issue) |

## Stopping Conditions

| Condition | Action |
|---|---|
| Build succeeds fully | Report success summary |
| 3 retries on same module | Report unresolved, stop |
| 5 retries across project | Report unresolved, stop |
| Dependency cannot be resolved | Report missing artifact, stop |
| User cancels | Stop |
| Fix requires production code change | Report recommendation, stop |

## Retry Report Template

```
Retry round: 2/3
Issue:       cannot find symbol: process(String, String)
Fix:         Added import for NewType
Scope:       mvn -pl service -am compile
Result:      BUILD SUCCESS
Next:        Expanding to: mvn -pl service -am test
```
