# Maven Build Speed — Bottleneck Analysis & Practices

> Source: `knowledge-api-compile-optimization.md` real-world benchmarks
> (2026-08-07, 7-module Java 8 service, 40+ internal `*-facade` SNAPSHOT deps)

## Benchmark Summary

| Mode | knowledge-biz (-am) | knowledge-common | Note |
|---|---|---|---|
| Online full `compile` | 70.07s | 6.73s | probes SNAPSHOTs every run |
| Offline `compile -o` | 62.98s | 6.56s | skips network, 1.11x |
| Online `-nsu` | 67.47s | — | no snapshot update, between |

## Three Real Bottlenecks (in order)

### 1. JVM cold start (~5s fixed)

Every CLI Maven run boots a fresh JVM and parses all reactor poms +
40+ facades. IDEA feels fast because its compile process is resident.

**Fix:** `mvnd` (Maven Daemon) keeps a warm JVM:
```shell
scoop install mvnd
mvnd -s <settings> compile -pl <mod> -am -o -T 4
```

### 2. Network SNAPSHOT probing

Only significant on deep modules with many `-SNAPSHOT` deps. Each build
asks nexus for SNAPSHOT metadata unless told otherwise.

**Fix (priority order):**
- `-o` offline — best, but requires a warmed local repo
- `-nsu` — skip snapshot update, still allows new artifact pulls
- settings `<snapshots><updatePolicy>never</updatePolicy></snapshots>` — fixes
  it at the source, so even online builds don't probe

### 3. Cold local repository

First build on a fresh machine is dominated by downloading. On warm machines
it's negligible.

**Fix:**
- Warm the local repo (fetch all internal facade SNAPSHOTs once)
- Share a single local repository across CI/AI runs, e.g. point
  `~/.m2/repository` at a shared cache (Windows: a `mvn_repo`-style directory
  via Junction)
- Symlink/Junction preserves the Maven wrapper's own dists

## Recommended Command

```shell
mvnd -s <settings-with-updatePolicy-never> compile -pl <mod> -am -o -T 4
```

- `-s` → settings with `updatePolicy=never`
- `-o` → offline (warmed repo)
- `-T 4` → parallel multi-module
- `mvnd` → resident daemon (no JVM cold start)

## Operational Notes

- IDEA incremental remains the daily driver; CLI is for final verification.
- Warm script pattern: `mvnw-fast.ps1 warm` / `fast` / `bench` / `raw`
  (see `knowledge-api/mvnw-fast.ps1`).
- `-o` failure `not downloaded from it before` → run online once, then warm.
- Never `-U` unless the user explicitly wants latest SNAPSHOTs.
