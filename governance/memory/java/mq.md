# Java MQ Coding Memory


## [MQ] Typed Message VO Required

Date: 2026-07-06

Priority: P1

Context:

RocketMQ event communication.


Problem:

JSONObject was used as message body.

Field changes caused compatibility issues.


Solution:

Replace JSONObject message bodies with typed `XxxMqVO` classes that define the exact fields shared between producer and consumer. Field changes then surface at compile time instead of silently breaking consumers.


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
