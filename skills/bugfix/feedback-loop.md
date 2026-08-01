# Feedback Loop Discipline

Hard-bug diagnosis discipline. Skip phases only when explicitly justified.
Derived from the diagnosing-bugs methodology; adapted to this skill's pipeline.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Symptom fixes are failure. If Phase 1 (feedback loop) has not been completed,
a fix cannot be proposed. This applies to every bug — simple bugs have root
causes too, and under time pressure guessing is most tempting and most likely
to cause rework.

## Phase 1 — Build a feedback loop (highest priority)

**This is the core.** If you have a **tight pass/fail signal** for the bug — one
that goes red on *this* bug — you will find the cause; bisection,
hypothesis-testing, and instrumentation all just consume it. Without one, no
amount of staring at code will save you.

Spend disproportionate effort here. Be aggressive, be creative, refuse to give up.

### Ways to construct a loop (try in roughly this order)

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **HTTP / CLI invocation** with a fixture input, diffing output against a known-good snapshot.
3. **Headless browser script** — drives the UI, asserts on DOM/console/network.
4. **Replay a captured trace** — save a real payload/log, replay it through the code path in isolation.
5. **Throwaway harness** — minimal subset of the system (one service, mocked deps) exercising the bug path.
6. **Property / fuzz loop** — for "sometimes wrong output", run many random inputs and look for the failure mode.
7. **Bisection harness** — if the bug appeared between two known states, automate "boot at state X, check, repeat" for `git bisect run`.
8. **Differential loop** — run the same input through old vs new version and diff outputs.
9. **HITL script** — last resort; if a human must interact, drive them with a structured loop script.

### Tighten the loop

- **Faster?** Cache setup, skip unrelated init, narrow scope.
- **Sharper signal?** Assert on the specific symptom, not "didn't crash".
- **More deterministic?** Pin time, seed RNG, isolate filesystem, freeze network.

A 30-second flaky loop is barely better than no loop; a 2-second deterministic
one is a debugging superpower.

### Non-deterministic bugs

Goal is not a clean repro but a **higher reproduction rate**. Loop 100×,
parallelise, add stress, narrow timing windows. A 50%-flake bug is debuggable;
1% is not — keep raising the rate.

### When you genuinely cannot build a loop

Stop and say so. List what you tried. Ask for: (a) access to the reproducing
environment, (b) a captured artifact (log dump, trace, screen recording), or
(c) permission for temporary production instrumentation. **Do not hypothesise
without a loop.**

### Completion criterion

Phase 1 is done when you can name **one command** you have already run at least
once that is:

- **Red-capable** — drives the actual bug path and asserts the user's exact symptom.
- **Deterministic** — same verdict every run (flaky: pinned high reproduction rate).
- **Fast** — seconds, not minutes.
- **Agent-runnable** — runnable unattended.

If you catch yourself reading code to build a theory before this command exists,
**stop** — jumping straight to a hypothesis is the exact failure this discipline
prevents.

## Phase 2 — Reproduce + minimise

Run the loop; watch it go red. Confirm the loop produces the **user's** failure
mode (not a nearby different failure), then shrink the repro to the **smallest
scenario that still goes red**. Cut inputs/callers/config/data one at a time,
re-running after each cut. Done when every remaining element is load-bearing.

## Phase 3 — Hypothesise (ranked, falsifiable)

Generate **3–5 ranked hypotheses** before testing any. Each must be falsifiable:

> "If <X> is the cause, then <changing Y> will make the bug disappear / make it worse."

Show the ranked list to the user before testing — domain knowledge re-ranks
quickly. Proceed with your ranking if the user is unavailable.

## Phase 4 — Instrument

Each probe maps to a specific prediction. **Change one variable at a time.**

1. Debugger / REPL inspection if supported (one breakpoint beats ten logs).
2. Targeted logs at boundaries that distinguish hypotheses.
3. Never "log everything and grep". Tag every debug log with a unique prefix
   (e.g. `[DEBUG-a4f2]`) so cleanup is a single grep.

For performance regressions: establish a baseline measurement first, then bisect.
Measure first, fix second.

## Phase 5 — Fix + regression test

Write the regression test **before the fix**, but only if a **correct seam**
exists — one where the test exercises the real bug pattern as it occurs at the
call site. If no correct seam exists, that itself is a finding: the architecture
prevents locking the bug down; flag it.

If a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail → apply the fix → watch it pass.
3. Re-run the original (un-minimised) scenario.

## Phase 6 — Cleanup + post-mortem

Before declaring done:

- [ ] Original repro no longer reproduces (re-run the Phase 1 loop)
- [ ] Regression test passes (or absence of seam documented)
- [ ] All `[DEBUG-...]` instrumentation removed
- [ ] Throwaway prototypes deleted
- [ ] The correct hypothesis is stated in the commit/PR message

Then ask: **what would have prevented this bug?** If architectural (no good test
seam, tangled callers), record it as a recommendation — after the fix, not before.
