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

## knowledge-api Mapper XML must be at `mapper/` top level (non-recursive scan)

Date: 2026-09-18

Problem:

New mapper XML placed in a subdirectory (`knowledge-dao/src/main/resources/mapper/migration/*.xml`) was never
scanned at runtime: `mybatis.mapper-locations = classpath:mapper/*.xml` uses a single `*` (non-recursive), so
every statement in those files stayed unregistered. Symptoms appear only at runtime, as
`org.apache.ibatis.binding.BindingException: Invalid bound statement (not found)` for each custom method,
while unit tests pass because they mock the mapper interfaces.

Solution:

Keep every mapper XML directly under `knowledge-dao/src/main/resources/mapper/` (alongside the ~95 existing
files). Do not introduce feature subdirectories there unless `mapper-locations` is changed to a recursive
pattern in all environments (Apollo + local), which is a config change spread across three environments.

Lesson:

Mapper XML binding is invisible to mocked unit tests, so verify it in a deployed environment — trigger the real
path once and read the service log, or add a lint test asserting the resources directory layout.

Scope:

- knowledge-api `knowledge-dao` mapper resources
- Any new MyBatis mapper XML in this repository

## knowledge-api cross-database table ownership measured on t2 (2026-09-18)

| Table | Database | Evidence |
| --- | --- | --- |
| `biz_course_resource` / `biz_resource_classify` | **enterprise shard** (`coolcollege_enterprise_<eid>`) | default main DB has no `privatization` column; enterprise DB does |
| `upload_resource_monitor` | **default main DB `coolcollege`** | absent in `t2_cool_course` and enterprise DBs |
| `biz_resource_replace_record` | **default main DB `coolcollege`** (has `enterprise_id`) | enterprise DB same-name table has **no** `enterprise_id`; production `BizCourseResourceService#isResourceReplace` calls `DataSourceHelper.reset()` first, then queries |
| `biz_migration_batch(_item)` | **central DB `cool_course`** (t2: `t2_cool_course`) | DDL landing location |

**Discipline**: cross-database reads go through `MigrationResourceReader` uniformly (enterprise shard: `changeToSpecificDataSource(eid)`; default DB: `DataSourceHelper.reset()`), then **restore the caller context** after reading; central DB reads use `changeToPolardb()`. **Never guess the database by table name** — conclude only from three evidence classes: DDL / production call precedent / runtime SQL error.

**Another trap (RPC DTO field shadowing)**: if an RM facade request DTO re-declares a field already present on the platform `BaseRequest` (e.g. `enterpriseId`), serialization writes the same-named field twice and the receiver reads null from the parent class — surfacing as "lost parameter". Guard test: RM `MigrationValidateFacadeImplTest#testBatchRequestDto_NoShadowedBaseFields`.
