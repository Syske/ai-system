# T-{编号}: {任务标题}

<!-- {编号} = **3 位数字**（T-001 / T-011）：commit subject 的 `T-<id>` 即此编号（commit-content.md）。
     文件路径 = `tasks/cards/T-{编号}.md`。
     历史按**计划位置**编号的旧卡（`1.1.md`）不改名（祖父条款），其引用写进 commit body。 -->

**服务**: {服务名}

**Spec引用**: {spec文件}

**契约约束**:
- {契约条目}

**场景约束**:
- {场景描述}

**实现后置确认**: required / skip（P50 触发标记——接口/契约面（RPC/MQ/REST 返回语义、枚举/错误码）、重构/行为变更、跨组件/跨仓契约 = required；机械类（纯 DTO/通道 bean/配置/文档） = skip）

**证据等级**: E1 代码事实 / E2 文档事实 / E3 推断 / E4 假设——完成定义与验收中的技术结论须标注等级；证据不足写 `⚠️ 待确认: {owner}/{deadline}` 占位符，禁止捏造（见 ai-system/governance/standards/common/evidence-levels.md）

**完成定义**:
- [ ] {完成项}

**验收标准**:
- Given {前提} When {动作} Then {预期}

## 代码质量检查

### 基线清单（引用，不逐项展开）
- [ ] 通用 / 安全性 / 语言检查：已按 ai-system/governance/standards/common/task-quality-checklist.md 逐项自检通过（review 将按该清单逐项核验）

### REST 接口（如果涉及）
- [ ] 调用方校验：@VerifyPathGuard + @TenantId session 一致性（跨租户可跳过）
- [ ] 参数校验：入参 @NotNull/@NotBlank/@Valid，返回明确错误码

### 协议：MQ（如果涉及）
- [ ] 消费者幂等：Redis SETNX 锁 + 业务去重键
- [ ] 生产者消息体：字段与 contract 定义一致
- [ ] Topic/Tag：与设计文档一致，不随意新增

### 协议：RPC（如果涉及）
- [ ] Facade 版本：SNAPSHOT（开发期）→ RELEASE（发布时）
- [ ] 接口签名：参数/返回值与 contract 一致

### 性能（如果涉及数据访问或远程调用）
- [ ] 无 N+1：循环内无数据库查询/RPC/HTTP/MQ 调用
- [ ] 批量优先：批量/缓存/分页替代循环单条操作

### 任务类型：新增功能
- [ ] 新增类/方法有明确单一职责
- [ ] 新增配置项已在配置中心（如 Apollo / Nacos）登记

### 任务类型：修改已有代码
- [ ] 修改点最小化，避免无关重构
- [ ] 已有测试全部通过
- [ ] 受影响调用方已检查

### 任务类型：删除
- [ ] 无残留引用（import、配置、文档）
- [ ] 关联数据已处理或确认可废弃
