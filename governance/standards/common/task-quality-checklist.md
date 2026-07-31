# Task Quality Checklist

Per-task quality verification baseline.

Every Task Card applies this checklist through a single reference line.

Review verifies each item against this document (runtime-review Phase 3).

Conditional items (REST / MQ / RPC / performance / task type) stay inside the Task Card.

---

## General (Every Task)

- **Completeness**: Implementation covers all behavior described in the spec.
- **Spec consistency**: Does not deviate from spec scope; no expansion or contraction.
- **Contract compliance**: Interface definitions match the contract exactly.
- **Build passes**: Project compiles without errors.
- **No hardcoding**: Configuration values (URL / Token / Secret) are read from the config center.
- **No magic values**: Numbers and strings are extracted as constants or enums. Literals like `status=="3"` or `bizType.equals("wx_live")` are forbidden.
- **Exception handling**: Exceptions are never swallowed. Logs contain full stack traces and business context.
- **Backward compatibility**: Existing interface signatures and behavior are not modified.
- **Code style**: Follows project language standards for naming and formatting.
- **No redundancy**: No dead code, no unused imports, no commented-out code.
- **Documentation**: New public classes and methods have Javadoc.
- **Code comments**: Key business logic and complex algorithms have explanatory comments. Constants and configuration values have documented meanings.
- **Logging standards**: Logs include business ID / request ID / key parameters. No passwords, tokens, or private data in logs.
- **No leftovers**: No TODO / FIXME / debug code / `printStackTrace` / `System.out.println`.
- **Reuse first**: Extend existing implementations; do not duplicate code. Extract shared capabilities into common components.
- **Self review**: After implementation, verify every item in this checklist before marking the task complete.

---

## Security (Every Task)

- **Input validation**: REST/Facade interface parameters have non-null and format validation, returning explicit error codes.
- **Authorization**: Non-cross-tenant interfaces have session/tenant validation.
- **Data safety**: Logs do not output passwords / tokens / secrets / private data.

---

## Language: Java

- **Unit tests**: JUnit version compatibility (per `repositories/{service_id}.yaml` → `technology.test.framework`). Covers normal, exception, boundary, and null cases.
- **Collections**: Use `isEmpty()` instead of `size()==0`. Ensure thread safety when required.
- **Optional**: Never return null Optional. Do not use Optional as a field type.
- **Lombok**: Prefer `@Data` for DTOs, `@RequiredArgsConstructor` for Services.
- **Transactions**: `@Transactional` only on methods that need transactions. Be aware of propagation behavior.
- **SQL**: Use parameterized queries in WHERE clauses. Avoid full table scans.
- **Constants**: `UPPER_SNAKE_CASE`. Constant classes end with `Const`. Enum classes end with `Enum`.
- **Null safety**: Use `Optional` / `Objects.requireNonNull` / `@NonNull` to guard critical parameters.
- **Resource management**: IO/DB connections use try-with-resources or explicit finally-close.
