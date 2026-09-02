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

- **Formatting (manual self-check)**: Java 格式不依赖自动格式化工具（pi-lens 的 Java formatter 已禁用，google-java-format 未安装）。实现完成后按项目管理工具/IDE 风格**人工自检**，review 核验：
  - 缩进为 4 空格（与存量代码/IDEA 风格一致）
  - Javadoc 用标准多行块，不用单行 `/** ... */`（见 `documentation.md` → Javadoc Format）
  - 无未使用 import；import 分组、顺序与既有代码一致（基本目标：`--dry-run` 语义——纯格式差异不引入与本 change 无关的整文件重排）
  - 方法名/变量名为英文 ASCII（中文仅用于注释/文档，见 documentation.md）
- **Unit tests**: JUnit version compatibility (per `repositories/{service_id}.yaml` → `technology.test.framework`). Covers normal, exception, boundary, and null cases.
- **Collections**: Use `isEmpty()` instead of `size()==0`. Ensure thread safety when required.
- **Optional**: Never return null Optional. Do not use Optional as a field type.
- **Lombok**: Prefer `@Data` for DTOs, `@RequiredArgsConstructor` for Services.
- **Transactions**: `@Transactional` only on methods that need transactions. Be aware of propagation behavior.
- **SQL**: Use parameterized queries in WHERE clauses. Avoid full table scans.
- **Constants**: `UPPER_SNAKE_CASE`. Constant classes end with `Const`. Enum classes end with `Enum`.
- **Null safety**: Use `Optional` / `Objects.requireNonNull` / `@NonNull` to guard critical parameters.
- **Resource management**: IO/DB connections use try-with-resources or explicit finally-close.
