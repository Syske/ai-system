# Design Review Vocabulary

Shared design-review vocabulary for assessing module shape and coupling.
Use these terms exactly during design review; consistent language surfaces
design issues that vague terms ("component", "service", "API") hide.

> **Authoritative copy**: `governance/standards/architecture/module-shape.md`
> (Architecture Standard: Module Shape). This file is the working copy used
> by the design-review skill; the governance standard is the source of truth.
> Keep them in sync when changing shared terms.

## Glossary

**Module** — anything with an interface and an implementation. Scale-agnostic:
a function, class, package, or tier-spanning slice. _Avoid_: unit, component,
service.

**Interface** — everything a caller must know to use the module correctly:
the type signature, plus invariants, ordering constraints, error modes,
required configuration, performance characteristics. _Avoid_: API, signature
(too narrow — they refer only to the type-level surface).

**Implementation** — what's inside a module, its body of code. Distinct from
**Adapter**: a thing can be a small adapter with a large implementation (a
Postgres repo) or a large adapter with a small implementation (an in-memory
fake). Reach for "adapter" when the seam is the topic.

**Depth** — leverage at the interface: behaviour a caller or test can exercise
per unit of interface they must learn. Deep = lots of behaviour behind a small
interface; shallow = interface nearly as complex as the implementation.

**Seam** (Feathers) — a place where you can alter behaviour without editing in
that place; where a module's interface lives. Where to put the seam is its own
design decision. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete thing satisfying an interface at a seam. Describes
role (what slot it fills), not substance.

**Leverage** — what callers get from depth: more capability per unit of
interface learned.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and
verification concentrate in one place. Fix once, fixed everywhere.

## Assessment Principles

- **Depth is a property of the interface, not the implementation.** A deep
  module may be internally composed of small, mockable parts — they just are
  not part of the interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes,
  it was a pass-through. If complexity reappears across N callers, it earns its
  keep.
- **The interface is the test surface.** Callers and tests cross the same seam.
  If you want to test past the interface, the module is the wrong shape.
- **One adapter means a hypothetical seam; two means a real one.** Do not
  introduce a seam unless something actually varies across it.

## Relationship Summary

- A **Module** has exactly one **Interface**.
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.
