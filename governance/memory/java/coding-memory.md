# Java Coding Memory


## [MQ] Typed Message VO Required

Context:

RocketMQ event communication.


Problem:

JSONObject was used as message body.

Field changes caused compatibility issues.


Lesson:

MQ messages are contracts.

Always create typed XxxMqVO.


Scope:

- RocketMQ
- Internal event messages


Related:

- Standard:
  testing.md

- Skill:
  implement


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


## [Integration] WeCom Status 4 Cancel Course Flow

Date: 2026-07-06

Priority: P2

Context:

Knowledge-api MQ consumer handling WeCom live status changes. status=4 means the WeCom live was cancelled.

Problem:

The status=4 handling was a TODO stub. The operation log used generic DELETE_COURSE type and hardcoded "system" as the operator instead of the course creator.

Solution:

Extract the status=4 logic into a dedicated handleWxLiveCancelled() method. Use a new DELETE_LIVE_COURSE audit type for differentiated i18n. Read course.createUser/createUserName from BizCourse entity for accurate operator attribution. Add i18n entries for the new audit type.

Lesson:

MQ consumers have no UserHolder context. For audit operations, read the resource creator from the entity itself. Each meaningful audit scenario (e.g., live course deletion) deserves its own AuditTypeEnum value for proper i18n and filtering.

Scope:

- MQ consumer audit operations
- WeCom live course lifecycle management