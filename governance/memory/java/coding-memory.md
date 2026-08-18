# Java Coding Memory

General Java coding experience.


## [Java] Strategy Pattern Over BizType Branching

Date: 2026-07-06

Priority: P1

Context:

LiveInfoFacadeImpl handled live platform differences (DingTalk/WeCom/Polyv) via if (BizTypeEnum.WX_LIVE_COURSE.equals()) branching, duplicating ecosystem-specific logic across deleteByBizId and modifyByBizId.

Problem:

BizType if-else branching scattered ecosystem-specific logic across the Facade layer. Adding a new ecosystem required modifying multiple methods. Bugs occurred when the order of operations differed (e.g., cancel API before vs after DB delete), as the branching logic was error-prone and hard to review.

Solution:

Extract ecosystem-specific logic into a LiveService strategy interface with default no-op methods. Delete and modify operations delegate to LiveService.deleteByBizId() and LiveService.modifyByBizId(), with the Facade layer handling only common operations (local DB update/delete). New ecosystems implement only their specific logic without touching Facade code.

Lesson:

Cross-ecosystem operations should use the Strategy pattern with a shared interface. Ecosystem-agnostic common logic stays in the Facade; ecosystem-specific pre/post operations live in strategy implementations. Avoid if-else on bizType in the dispatch layer.

Scope:

- Multi-platform service design
- SOFA RPC Facade implementations
- All live platform integrations (DingTalk/WeCom/Polyv/HD)


## [Java] Order of Operations in Delete-then-API Pattern

Date: 2026-07-06

Priority: P1

Context:

LiveInfoFacadeImpl.deleteByBizId() required calling WeCom cancel API before deleting the local DB record.

Problem:

The code deleted the local DB record first, then tried to query the same record to get the feedId for the cancel API call. Since the record was already deleted, the query returned null, making the cancel API call dead code. WeCom livings remained active on the WeCom side after local deletion.

Root Cause:

The delete operation (liveInfoService.deleteByBizId()) was called before the ecosystem-specific pre-logic. The subsequent query for the feedId would always return null because the record no longer existed.

Solution:

Reorder: query the record first → extract feedId → call ecosystem pre-logic (cancel API) → delete local DB. Extract the pre-logic into LiveService.deleteByBizId() strategy method to ensure consistent ordering.

Lesson:

When implementing a "delete + call external API" pattern, always query the required data before deletion. The data needed for the external API call must be obtained while the record still exists in the database.

Scope:

- All delete operations that require external API calls before deletion
- Any pattern where record data is needed by strategy logic


## Category Files

Category files, split by topic:

- `java/mq.md` — MQ-related experience
- `java/integration.md` — integration (WeCom, etc.) experience
- `java/spring.md` — Spring experience

