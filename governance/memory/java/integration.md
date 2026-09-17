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

## knowledge-api i18n messages must be ASCII + \uXXXX escapes

Date: 2026-09-15

Problem:

Station-message i18n text added to `knowledge-web/src/main/resources/i18n/messages*.properties` as raw UTF-8
Chinese rendered as mojibake. These `.properties` files are loaded by `ResourceBundle` (base name
`i18n.messages`), whose default encoding is ISO-8859-1; the project has no `native2ascii` conversion step,
so every non-ASCII character must be written as a Java unicode escape.

Solution:

Write all non-ASCII text as uppercase `\uXXXX` escapes and keep the files pure ASCII (the existing entries in
`messages.properties` / `messages_zh_CN` / `messages_zh_HK` all follow this convention). Parameter placeholders
use `MessageFormat` style `{0}{1}{2}` outside the escapes.

Lesson:

After adding i18n entries, prove them at runtime — load `ResourceBundle.getBundle("i18n.messages", locale)` and
`MessageFormat.format` the value, rather than trusting the file to render correctly in an editor. Raw UTF-8 in a
`.properties` file looks fine in a text editor but breaks at runtime.

Scope:

- knowledge-api i18n resources (`knowledge-web/src/main/resources/i18n/`)
- Any JMS/station-message text routed through `JmsContentParamsVo(I18nMessageKeyEnum, params)`
