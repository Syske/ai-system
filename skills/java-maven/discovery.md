# Discovery

## Stage 1: Repository Discovery

**Goal:** Find the Maven project root and executable.

### Step 1.1 — Find repository root

Walk upward from the current directory looking for `.git/`. If not found, look
for any directory containing a `pom.xml` with `<modules>` or `<parent>`.

```
From: /workspace/project/service/core/
  Walk: /workspace/project/service/core/  → no .git
  Walk: /workspace/project/service/       → no .git
  Walk: /workspace/project/               → .git found
  Root: /workspace/project/
```

### Step 1.2 — Find root pom.xml

First, check the repository root for `pom.xml`. If absent, search for any
`pom.xml` that declares `<modules>` (aggregator) or has `<parent>` that
references a sibling module.

```shell
# Check root
ls repository-root/pom.xml

# Check for aggregator pom
grep -l "<modules>" repository-root/**/pom.xml 2>/dev/null
```

**Output:** `rootPom: <path>`

### Step 1.3 — Find Maven wrapper

Check for wrapper scripts in order of preference:

| Priority | Script | Check |
|---|---|---|
| 1 | Custom wrapper | `ls <root>/*.cmd`, `ls <root>/*.sh` — look for known patterns |
| 2 | `mvnw` | `<root>/mvnw` exists and is executable |
| 3 | `mvnw.cmd` | `<root>/mvnw.cmd` exists (Windows) |
| 4 | `.mvn/wrapper/maven-wrapper.properties` | Contains wrapper configuration |
| 5 | Raw `mvn` | `mvn --version` succeeds |

If a wrapper is found, also check for:

- `<root>/.mvn/jvm.config` — JVM arguments
- `<root>/.mvn/maven.config` — Default Maven arguments
- `<root>/.mvn/extensions.xml` — Build extensions

**Output:** `executable: <path>`, `config: {jvm, maven, extensions}`

### Step 1.4 — Detect JAVA_HOME

```shell
echo $JAVA_HOME
java --version
```

If JAVA_HOME is not set, check `.mvn/jvm.config` for a `JAVA_HOME` reference,
or check if the wrapper script sets it.

**Output:** `javaVersion: <version>`

---

## Stage 2: Module Discovery

**Goal:** Determine the project's module structure.

### Step 2.1 — Detect project type

Read the root `pom.xml`:

```xml
<modules>
  <module>core</module>
  <module>service</module>
</modules>
```

| pom.xml has `<modules>`? | pom.xml has `<parent>`? | Type |
|---|---|---|
| Yes | Maybe | Multi-module aggregator |
| No | Yes | Child module (part of multi-module, or standalone with parent) |
| No | No | Single-module |

### Step 2.2 — Map module structure

For multi-module projects, read each module's `pom.xml` and build a tree:

```
/workspace/project/
  pom.xml              (aggregator: core, service, web)
  core/
    pom.xml            (artifactId: core)
    src/
  service/
    pom.xml            (artifactId: service, depends on core)
    src/
  web/
    pom.xml            (artifactId: web, depends on service)
    src/
```

### Step 2.3 — Identify current module

Determine the current module from:
1. Working directory — which `pom.xml` is nearest
2. Change context — which file changed, which module contains it
3. User input — explicit module name

### Step 2.4 — Identify affected modules

If a specific file changed, map it to its module:

```
src/main/java/com/x/service/XxxService.java
  → Module: service

src/main/java/com/x/web/XxxController.java
  → Module: web
```

If pom.xml changed, the affected module is the module that owns the pom.xml
plus any modules that depend on it.

**Output:** `{type, modules[], currentModule, affectedModule, tree}`
