# Command Generation

## Executable Selection

| Condition | Command |
|---|---|
| `mvnw` found (Linux/macOS) | `./mvnw` |
| `mvnw.cmd` found (Windows) | `mvnw.cmd` |
| Custom script `build.cmd` found | `<custom-script>` |
| No wrapper, `mvn` in PATH | `mvn` |
| No wrapper, no `mvn` | Stop: "Maven not available" |

## Command Templates

### Single test method (highest priority)

```shell
<exec> -f <pom> -pl <module> -am test -Dtest=<Class>#<method>
```

### Single test class

```shell
<exec> -f <pom> -pl <module> -am test -Dtest=<Class>
```

### Module test (all tests)

```shell
<exec> -f <pom> -pl <module> -am test
```

### Module compile

```shell
<exec> -f <pom> -pl <module> -am compile
```

### Module test-compile

```shell
<exec> -f <pom> -pl <module> -am test-compile
```

### Module package (skip tests)

```shell
<exec> -f <pom> -pl <module> -am package -DskipTests
```

### Module verify

```shell
<exec> -f <pom> -pl <module> -am verify
```

### Full repository

```shell
<exec> -f <pom> clean verify
```

**Only use `clean` when justified (see `decision.md`).**

## Flag Selection

| Flag | When to use |
|---|---|
| `-f <pom>` | pom.xml is not in current directory |
| `-pl <module>` | Multi-module, building a specific module |
| `-am` (also-make) | Build module + its dependencies |
| `-amd` (also-make-dependents) | Build module + modules depending on it |
| `-Dtest=<pattern>` | Running specific tests |
| `-DskipTests` | Skipping tests during compile/package |
| `-T <n>` | Parallel build (multi-module only, n = threads) |
| `-P <profile>` | Activate a profile |
| `-s <settings.xml>` | Custom settings file |
| `--batch-mode` or `-B` | Non-interactive execution (always add this) |
| `-q` | Quiet mode (errors only) |
| `-Dmaven.test.failure.ignore=true` | Collect all test results before failing |

## Lifecycle Phase Selection

| Phase | Includes | Use when |
|---|---|---|
| `compile` | validate, compile | Checking compilation only |
| `test-compile` | + test-compile | Checking test sources compile |
| `test` | + test (run surefire) | Running unit tests |
| `package` | + package (jar/war) | Creating artifact |
| `verify` | + integration-test, verify | Full quality gate |
| `install` | + install to ~/.m2 | Downstream modules need the artifact |
| `deploy` | + deploy to remote | Publishing to repository |

**Rule:** Use the earliest phase that achieves the goal. Never use `install`
when `test` is sufficient.

## Multi-Module Command Generation

| Scenario | Command |
|---|---|
| Single module affected | `<exec> -f <root> -pl <mod> -am <phase>` |
| Multiple modules affected | `<exec> -f <root> -pl <mod1>,<mod2> -am <phase>` |
| All modules need verification | `<exec> -f <root> verify` |
| Module + dependents need verification | `<exec> -f <root> -pl <mod> -amd verify` |

## Explaining Command Before Execution

Before running any Maven command, explain:

```
Running: mvnw -pl service -am compile
Why:     Only service module changed.
         Compile is sufficient (no tests needed).
         No clean (no dependency changes).
Scope:   module=service, phase=compile, clean=false
```

This explanation is **required** — not optional.
