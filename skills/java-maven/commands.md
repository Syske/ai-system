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

### Fast compile (offline, warmed cache)

When the local repository is already warmed (all SNAPSHOTs present), prefer
offline mode — real-world measurement on a 7-module knowledge service:
online 70.07s → offline 62.98s (1.11x), and offline avoids network flakes:

```shell
<exec> -f <pom> -s <settings> -pl <module> -am compile -o
```

### Fast compile (no snapshot update, occasional new deps)

`-nsu` skips SNAPSHOT metadata checks while still allowing new artifact pulls:

```shell
<exec> -f <pom> -s <settings> -pl <module> -am compile -nsu
```

### Daemon-backed compile (mvnd)

For repeated CLI builds, `mvnd` (Maven Daemon) keeps a warm JVM — the same
reason IDEA incremental builds feel fast. Requires `scoop install mvnd` (or
package-manager equivalent) and its own `-s`:

```shell
mvnd -s <settings> compile -pl <module> -am -o -T 4
```

> `-T 4` parallelizes multi-module builds; combine with `-o` for max speed.

## Speed Strategy (measured)

From `knowledge-api-compile-optimization` real-world benchmarks, the three
real bottlenecks are (in order):

1. **JVM cold start** — every CLI run boots a fresh JVM and parses all poms
   (~5s fixed); use `mvnd` to keep a resident daemon.
2. **Network SNAPSHOT probing** — significant only on deep, SNAPSHOT-heavy
   modules; use `-o` offline (best) or `-nsu`.
3. **Cold local repository** — first build on a new machine is slow; warm the
   local repo (shared cache) or symlink it.

See `build-speed.md` for the full analysis.

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
