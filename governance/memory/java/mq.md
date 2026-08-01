# Java MQ Coding Memory


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
