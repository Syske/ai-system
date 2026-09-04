# Spring Boot Standard (Extension Reserved)

## Configuration Injection (@Value)

Single default source: `@Value("${key:default}")` — the colon default is the
sole carrier of the runtime default.

- **No field initializer**: a field bound by `@Value` MUST NOT also declare an
  initializer (`private int x = 3;`). Duplicated defaults drift when the
  Apollo/property default changes; at runtime Spring injection always overrides
  the field initializer, so the initializer only masks non-Spring construction.
- **Test construction defaults live in tests**: @InjectMocks / reflection
  construction bypasses Spring — supply defaults on the test side (a shared
  `applyDefaults(...)` helper in the test base or per-test setup), never in the
  production field.
- **Transition exception** (legacy fields only): a field that must keep the
  initializer while being migrated MUST carry a Javadoc/first-line annotation:
  `测试直构兜底，与 @Value 默认一致`.
- **Comment required**: every `@Value` field needs a trailing comment stating
  purpose/unit — config keys are a deployment-time interface; uncommented keys
  are unmaintainable.
- The A-layer format gate (format-check.py check #8) warns on: field
  initializer under `@Value` (dual default) and `@Value` fields without a
  trailing comment.