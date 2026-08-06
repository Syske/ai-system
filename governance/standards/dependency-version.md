# Dependency Version Standard

## RPC Facade

Whenever a public Facade interface is modified, the Facade artifact version MUST be updated.

Changes include:

- Add Interface
- Remove Interface
- Modify Method
- Modify Request
- Modify Result
- Modify Enum
- Modify DTO exposed by Facade

Internal implementation changes do NOT require a Facade version update.

---

## Development

During development:

Version MUST use SNAPSHOT.

SNAPSHOT is limited to integration within the same iteration. It is NOT a
long-term dependency state (see SNAPSHOT Lifecycle below).

Example:

1.3.0-SNAPSHOT

---

## SNAPSHOT Lifecycle

SNAPSHOT is for same-iteration integration and verification only. Cross-service
dependencies must not drift on mutable SNAPSHOT artifacts.

### Usage Boundary

- Same-iteration cross-service integration where interfaces may still change: SNAPSHOT allowed.
- Cross-service Facades MUST NOT depend on SNAPSHOT across iterations or for
  longer than the current iteration.
- Once interfaces stabilize (integration complete), publish RELEASE and switch
  consumers immediately.

### Drift Control (consumer obligations)

- A service depending on SNAPSHOT MUST pin the **timestamped version** it was
  validated against; unconditionally pulling the latest SNAPSHOT makes builds
  non-reproducible.
- After the upstream publishes a new SNAPSHOT, consumers MUST verify
  compatibility before upgrading.
- Upstream reverting a field/method in the SNAPSHOT window counts as
  **breaking** — the upstream MUST notify all consumers synchronously.

### Exit Conditions

- Integration complete → publish RELEASE → consumers switch version in pom/build.
- Entering production release → all SNAPSHOTs in the dependency tree must be
  resolved to RELEASE (existing gate, maintained).

---

## Release

Before production release:

Replace SNAPSHOT with Release version.

Example:

1.3.0-RELEASE

Never release a SNAPSHOT artifact.