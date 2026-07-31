# RocketMQ Configuration Convention

## Purpose

Ensure all projects using the `cool.mq.*` framework document RocketMQ configuration items completely, with consistent naming conventions and proper environment isolation during release preparation.

## Scope

- `runtime-release` — release readiness workflow
- `runtime-develop` — MQ configuration checks during development
- `runtime-review` — MQ configuration compliance in code review

---

## 1. Consumer Four-Field Protocol

Every MQ Consumer MUST document all 4 fields:

| Field | Convention | Example |
|-------|-----------|---------|
| `topic` | business-domain topic name, lowercase + underscore | `live_status_change` |
| `tag` | event category label (multiple tags via `\|\|` or separate rows) | `liveStatusChange` |
| `group-name` | consumer group logical name, PascalCase + `Group` suffix | `liveStatusChangeGroup` |
| `group-id` | `GID_` prefix + topic name + environment suffix (see §3) | `GID_live_status_change_tt` |

### Configuration Format

```properties
# Consumer 4-field spec
cool.mq.bindings.consumer.{channelName}.topic={topic}
cool.mq.bindings.consumer.{channelName}.tag={tag}
cool.mq.bindings.consumer.{channelName}.group-name={groupName}
cool.mq.bindings.groups.{groupName}.group-id={groupId}
```

---

## 2. Channel Naming Convention

### Producer Channel

```properties
cool.mq.bindings.producer.{channelName}.topic={topic}
cool.mq.bindings.producer.{channelName}.tag.{tagName}={tag}
```

`{channelName}`: PascalCase, semantically describing producer purpose, e.g.
`weComWatchDetailFetchProducerChannel`, `liveStatusChangeProducerChannel`.

`{tagName}`: PascalCase or kebab-case, e.g. `weComWatchDetailFetchTag`, `statusTag`.

### Consumer Channel

```properties
cool.mq.bindings.consumer.{channelName}.topic={topic}
cool.mq.bindings.consumer.{channelName}.tag={tag}
cool.mq.bindings.consumer.{channelName}.group-name={groupName}
cool.mq.bindings.groups.{groupName}.group-id={groupId}
```

`{channelName}`: PascalCase, semantically describing consumer purpose, e.g.
`liveStatusChangeConsumerChannel`, `liveProgressRecalcConsumerChannel`.

---

## 3. Environment Isolation

Different environments MUST use independent `group-id` values to prevent consumer conflicts.

| Environment | group-id Suffix | Example |
|-------------|----------------|---------|
| Dev/T2 | `_t2` | `GID_live_status_change_t2` |
| Staging/Pre | `_pre` | `GID_live_status_change_pre` |
| Production | (none) | `GID_live_status_change` |

Topics MAY use environment-suffixed variants for isolation (e.g., `learn_order_t2`), but this is not mandatory.

Tags MAY carry environment suffixes (e.g., `liveProgressRecalcPre`) for isolation.

---

## 4. Topic Message Body Documentation Requirements

Every Topic MUST document:

1. **Topic Metadata**: name, type (normal/ordered/transactional), message consumption mode (concurrent/sequential)
2. **Producer**: which service, which method/scenario emits the message
3. **Consumer(s)**: which service, which Consumer class processes the message
4. **Message Body JSON Structure**:
   ```json
   {
     "fieldName": "type — description"
   }
   ```
5. **At least one complete example payload**
6. **Message Flow Diagram** (Producer → MQ → Consumer arrow diagram)

---

## 5. Pre-Release Checklist

- [ ] Every newly created Topic exists in the RocketMQ console
- [ ] Existing Topics with new tags confirmed that no new Topic creation is needed
- [ ] Consumer 4-field spec (topic/tag/group-name/group-id) is complete
- [ ] `group-id` uses `GID_` prefix
- [ ] Different environments use different `group-id` suffixes
- [ ] Message body structure is documented (JSON example)
- [ ] Consumer method is implemented and tested

---

## 6. Reference

Complete configuration example (see reference output):

```
workspaces/{project}/outputs/release/configuration-mq-topics.md
```

Standard format referenced by:

- `runtime-release.md` Phase 5 — Dependency Validation
