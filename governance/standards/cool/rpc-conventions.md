# RPC Convention

## Purpose

Ensure RPC/facade dependency changes are fully documented and backward-compatible during release.

## Scope

- `runtime-release` — RPC dependency verification
- `runtime-develop` — facade version management during development

---

## 1. Facade Naming Convention

Every service that exposes RPC interfaces MUST provide a dedicated facade module.

| Artifact | Convention | Example |
|----------|-----------|---------|
| Facade module | `{service-name}-api-facade` | `live-api-facade` |
| Facade interface | `I{BizDomain}Facade` | `IBizCourseFacade` |
| Facade implementation | `{BizDomain}Service` or `{BizDomain}FacadeImpl` | `BizCourseService` |

The facade module MUST stay in the same repository as the service, published as a Maven/Gradle dependency.

---

## 2. Version Management

### 2.1 SNAPSHOT Ban

- **Production releases MUST NOT depend on SNAPSHOT versions**
- Every SNAPSHOT dependency in the dependency tree MUST be resolved to a RELEASE version before deployment

### 2.2 Facade Version Bump

When the facade interface changes (new methods, changed signatures, new DTO fields):

1. Bump the facade module version (patch/minor per semver)
2. Publish the RELEASE version to the artifact repository
3. Update all consumer services' `pom.xml` / `build.gradle` to reference the new RELEASE version
4. Deploy the facade RELEASE **before** deploying any consumer service

### 2.3 Backward Compatibility

- Adding new fields to a DTO/RVO is backward-compatible (consumers must tolerate unknown fields)
- Removing or renaming fields is **breaking** — requires coordinated deployment
- Changing method signatures is **breaking** — requires coordinated deployment
- Adding new methods to an existing facade interface is backward-compatible

---

## 3. RPC Dependency Matrix

Every release MUST produce a per-service RPC dependency matrix:

| Service | Facade Dependency | Consumer(s) | Version Constraint |
|---------|-------------------|-------------|-------------------|
| live-api | `live-api-facade` | knowledge-api, incentive-api | >= 1.2.6 |
| incentive-api | `live-api-facade` | — | >= 1.2.6 |

### Validation

- [ ] Each downstream consumer facade version is updated
- [ ] No consumer references an older facade version that lacks required methods
- [ ] Facade RELEASE is published before consumer deployment

---

## 4. Deployment Order Constraint

RPC changes imply a strict deployment order:

```text
1. Facade module: publish RELEASE to artifact repository
2. Producer service (facade implementation owner): deploy first
3. Consumer service(s): deploy after facade version is available
```

If the RPC change is **backward-compatible** (new fields only), producers and consumers MAY be deployed in any order.

If the RPC change is **breaking** (renamed/removed fields, changed signatures), ALL consumers MUST be updated and deployed within the same release window.

---

## 5. Pre-Release Checklist

- [ ] Facade version bumped and published as RELEASE
- [ ] All SNAPSHOT dependencies resolved to RELEASE
- [ ] RPC dependency matrix completed (who depends on which facade)
- [ ] Breaking changes identified and consumer deployment verified
- [ ] Deployment order documented in dependency-checklist.md

---

## 6. Facade Request/Result Contract

All facade request objects MUST extend:

```text
net.coolcollege.platform.util.model.BaseRequest
```

All facade result objects MUST extend:

```text
net.coolcollege.platform.util.model.BaseResult
```

Facade interfaces MUST use:

- `BaseRequest` subclasses as parameters.
- `BaseResult` subclasses as return types.

### Never

Do not use as request/result:

- POJO
- Map
- Object
- List directly

unless explicitly approved by architecture.
