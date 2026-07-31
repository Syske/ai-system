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

Example:

1.3.0-SNAPSHOT

---

## Release

Before production release:

Replace SNAPSHOT with Release version.

Example:

1.3.0-RELEASE

Never release a SNAPSHOT artifact.