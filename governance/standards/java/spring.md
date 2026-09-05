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

---

## Configuration Properties (@ConfigurationProperties)

**L2 target paradigm (P48)** — for NEW code, prefer grouping related `@Value`
fields into a typed configuration POJO. This is the Spring-recommended way to
eliminate multi-default drift (P48 / L1 keeps legacy `@Value` compliant via
check #8).

- **Group related keys**: fields sharing a `prefix` live in one POJO annotated
  `@ConfigurationProperties(prefix = "...")` (registered via
  `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`).
- **Field defaults are the single source**: the POJO field initializer IS the
  default (there is no placeholder-colon carrier) — legal here, unlike the
  `@Value` dual-default case.
- **Test construction shares the same defaults**: tests build
  `new MyProperties()` and override per-case — test default == production
  default by construction (same physical location), which L1's
  "defaults live in tests" cannot guarantee.
- **Field Javadoc**: every field carries a comment — use the multi-line
  Javadoc structure (`/**` line / ` * description` / ` */` line), never the
  single-line block `/** ... */` (documentation.md Comment Rules).
- **Consumption**: inject the POJO via constructor, not per-field `@Value`.
- **Boundary**: legacy `@Value` fields are NOT force-migrated; they stay L1
  compliant (check #8). POJO-ization is a new-code paradigm + pilot.