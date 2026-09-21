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

## Enterprise sharded DB: user/department queries MUST switch to the enterprise DB (2026-09-20, verified)

- `sys_department` in the **default main DB** `coolcollege` has the old schema (15 columns, **no** `name_encrypted`); in the **enterprise shard** `coolcollege_enterprise_<eid>` it has the new schema (25 columns, has `name_encrypted`). Platform user/department services (`usercenter`) query against the **enterprise DB schema**.
- Therefore calling `EnterpriseUserService#selectByPrimaryKeys`, station-letter/department resolution, etc. **must** first call `DataSourceHelper.changeToSpecificDataSource(enterpriseId)`, otherwise the query hits the default main DB → `Unknown column 'name_encrypted'` (looks like a platform bug, but is actually the caller not switching the DB).
- General discipline: **every call site that reads enterprise-domain data (users, departments, course resources, categories) must explicitly switch to the enterprise DB and restore the caller context**; do not assume "the platform service switches the DB internally".

## facade DTO inheriting the platform base class: never redeclare fields + cross-repo publish order (2026-09-20, verified)

- The platform `BaseRequest` (`platform-util`) already declares `Long enterpriseId`; `BaseResult` already declares `success/resultCode/message`.
  A facade/RPC DTO that **redeclares** a same-name same-type field makes Lombok `@Setter/@Getter` generate same-name accessors that **shadow** the parent field →
  **cross-service RPC value loss** (caller set succeeds, callee reads null); neither compilation nor mock unit tests signal it, only runtime exposes it.
- Verified on both sides: KA `UploadByUrlRequest` (D-15) and RM `MigrationValidateBatchRequest` (D-9) both lost parameters for this reason.
- Guard: static test comparing "whether a declared field name appears in the parent (including ancestors)" via reflection (KA `FacadeDtoFieldShadowGuardTest`, RM `MigrationValidateFacadeImplTest#testBatchRequestDto_NoShadowedBaseFields`).
- **Publish order**: after a DTO shape change, **the repo owning the facade must publish first** (provide a new snapshot), then dependents rebuild —
  i.e. "DTO lives in the KA facade → KA publishes first (with the facade snapshot) then RM"; the reverse (DTO in the RM facade) means RM publishes first (same D-9 lesson).

## Feature whitelist (function_black_white_list) evaluation and cache (2026-09-20, verified)

- Entry point: `FunctionBlackWhiteListService#getWhiteTypeIsOpen(eid, type)` (provided by enterprise-manage, called by KA via facade).
  The row lives in the **default main DB** `coolcollege.function_black_white_list` (fields `enterprise_id/type/status`); `status='0'` means **open**.
- **Cache**: Redis hash, key = `ENTERPRISE_WHITE_LIST_<type>`, field = enterprise id, value = status, TTL 86400s;
  the DB is re-sourced only when the key is absent or `TTL < 600s`. ⇒ **after DB changes you MUST `DEL` the key, otherwise the decision stays unchanged for up to 24h** (verified: DB change had no effect while TTL was 82595s).
- The key lives in **db 0** (`cool.common.redis.db=0` / `redis.host.uri ...:6379/0`);
  the same instance also has confusingly similar keys such as `quota.redis.host.uri` (**db 90**) — when parsing config, match `^redis.host.uri` exactly, otherwise you may flush the wrong DB.
- Verification points: the **order** of `516201 MIGRATE_BLACKWHITE_DENIED` (outside whitelist) and `516202` (parameter-level): whitelist evaluation precedes parameter validation (verified: after disabling the whitelist, even an "empty list" returns 516201).
