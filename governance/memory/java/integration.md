# Java Integration Coding Memory


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
