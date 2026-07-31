# Examples

Complete end-to-end workflows.

---

## Example 1: NullPointerException — Missing Null Check

**Symptom:** `NullPointerException at LiveService.sendMessage():56`

**Reasoning chain:**

```
Stage 1 — Observe:
  NPE at LiveService.java:56
  message parameter is null

Stage 2 — Collect evidence:
  Stack trace: LiveService.sendMessage(LiveService.java:56)
  Input: message = null
  Recent change: sendMessage() was refactored 2 commits ago

Stage 3 — Expected behavior:
  sendMessage should handle null message gracefully
  (API contract allows null)

Stage 4 — Actual behavior:
  sendMessage calls message.getContent() without null check

Stage 5 — Compare:
  Divergence: missing null guard clause
  Expected: handle null → Actual: throws NPE

Stage 6 — Affected code:
  LiveService.java:56 — message.getContent()
  Callers: sendNotification(), broadcast()

Stage 7 — Hypotheses:
  H1: null check was accidentally removed during refactoring
    → Confirm: git show recent commit shows null check removed
  H2: caller should never pass null
    → Confirm: check caller — is null possible?
  H3: null check exists but was bypassed
    → Refute: line 56 directly dereferences message

Stage 8 — Validate:
  git show HEAD~1: null check was removed in refactoring
  H1 confirmed. H2-H3 eliminated.

Stage 9 — Root cause:
  File: LiveService.java:56
  Category: Missing null check
  Explanation: Refactoring removed the guard clause

Stage 10 — Smallest repair:
  Add null guard clause at method entry

Stage 11 — Implement:
  Add: if (message == null) { return; }

Stage 12 — Validate:
  mvn -pl service -am test -Dtest=LiveServiceTest
  → BUILD SUCCESS (all tests pass)

Stage 13 — Regressions:
  mvn -pl service -am test
  → BUILD SUCCESS (45 tests pass)

Stage 14 — Done.
```

---

## Example 2: Compilation Error — Method Renamed

**Symptom:** `cannot find symbol: method findUserByEmail(String)`

**Reasoning chain:**

```
Stage 1 — Observe:
  Compilation error in XxxService.java
  cannot find symbol: method findUserByEmail(String)

Stage 2 — Evidence:
  Full error: XxxService.java:42, symbol: findUserByEmail(String)
  git diff: UserRepository.findByEmail() renamed to findUserByEmail()
  but XxxService still calls findByEmail()

Stage 3 — Expected:
  Compilation should succeed — method was renamed consistently

Stage 4 — Actual:
  XxxService calls old name findByEmail()

Stage 5 — Compare:
  Divergence: call site uses old method name

Stage 6 — Affected code:
  XxxService.java:42 — old method call
  UserRepository.java — new method declaration

Stage 7 — Hypotheses:
  H1: Call site was missed during rename refactoring
    → Confirm: git show shows only UserRepository was updated
  H2: Method exists but signature is different
    → Refute: both have same parameters

Stage 8 — Validate:
  git show HEAD: only UserRepository.java has the new name
  H1 confirmed. H2 eliminated.

Stage 9 — Root cause:
  File: XxxService.java:42
  Category: API misuse (old method name)

Stage 10 — Repair:
  Change findByEmail → findUserByEmail

Stage 11 — Implement:
  One-character method name update.

Stage 12 — Validate:
  mvn -pl service -am compile → BUILD SUCCESS

Stage 13 — Regressions:
  mvn -pl service -am test → BUILD SUCCESS (all pass)

Stage 14 — Done.
```

---

## Example 3: Mockito WantedButNotInvoked

**Symptom:** `Wanted but not invoked: notificationService.send()`

**Reasoning chain:**

```
This example involves test fixture maintenance.
Invoke mock-test Skill for the detailed Mockito repair.
Main workflow terminates here with delegation.
```

---

## Example 4: Wrong Conditional — Off-by-One

**Symptom:** Pagination returns 21 items when page size is 20.

**Reasoning chain:**

```
Stage 1 — Observe:
  Page 1 returns 21 items with pageSize=20

Stage 2 — Evidence:
  Test: given pageSize=20, page=1, expect 20 items
  Actual: 21 items returned

Stage 3 — Expected:
  query: LIMIT 20 OFFSET 0 → 20 items

Stage 4 — Actual:
  query: LIMIT 21 OFFSET 0 → 21 items

Stage 5 — Compare:
  Divergence: LIMIT value is pageSize+1 instead of pageSize

Stage 6 — Affected code:
  PaginationHelper.java:25 — sql limit calculation

Stage 7 — Hypotheses:
  H1: Page size computation adds 1 (off-by-one)
    → Confirm: LIMIT = pageSize + 1
  H2: Database returns extra row
    → Refute: query string directly shows LIMIT 21

Stage 8 — Validate:
  Read PaginationHelper.java:25
  limit = pageSize + 1;  // ← intentional? No, it's a bug
  H1 confirmed.

Stage 9 — Root cause:
  File: PaginationHelper.java:25
  Category: Boundary condition (off-by-one)

Stage 10 — Repair:
  Change `pageSize + 1` to `pageSize`

Stage 11 — Implement:
  Single character change.

Stage 12 — Validate:
  mvn -pl core -am test -Dtest=PaginationTest
  → BUILD SUCCESS (test passes: 20 items returned)

Stage 13 — Regressions:
  mvn -pl core -am test
  → BUILD SUCCESS (all pagination tests pass)

Stage 14 — Done.
```
