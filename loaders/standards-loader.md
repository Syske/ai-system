### Standards Loader

Purpose

根据当前 Runtime、技术栈和任务类型，动态加载最相关的研发规范。

目标：

* 减少 Prompt 长度

* 提高规则命中率

* 避免无关规范干扰

* 支持多语言、多框架、多领域扩展

### Loading Order

标准加载顺序（优先级从高到低）

1. AI Operating Rules

2. Source of Truth (governance/SOURCE_OF_TRUTH.md)

3. Context Loading (governance/CONTEXT_LOADING.md)

4. Repository First (governance/REPOSITORY_FIRST.md)

5. Reflection Rules (governance/REFLECTION_RULES.md)

6. AI Coding Rules

7. Karpathy Guidelines

8. Runtime Required Standards

9. Language Standards

10. Framework Standards

11. Domain Standards

12. Task-Type Standards

13. Project Memory / Historical Rules

### Runtime Required Standards

### Always Load

* governance/AI_OPERATING_RULES.md

* governance/SOURCE_OF_TRUTH.md

* governance/CONTEXT_LOADING.md

* governance/REPOSITORY_FIRST.md

* governance/REFLECTION_RULES.md

* governance/LANGUAGE_CONVENTION.md

* governance/standards/common/ai-coding-rules.md

### For runtime-develop

* governance/standards/common/code-quality.md

* governance/standards/common/clean-code.md

* governance/standards/common/task-quality-checklist.md

### For runtime-release

* governance/standards/common/cross-project-sync.md

* governance/standards/common/copy-review.md

### For runtime-spec

* governance/standards/common/chinese-documentation.md

### Language Standards

### Java Project

* governance/standards/java/java-alibaba.md

* governance/standards/common/documentation.md

### Python Project

* governance/standards/python/pep8.md

* governance/standards/common/documentation.md

### Go Project

* governance/standards/go/go-style.md

* governance/standards/common/documentation.md

### Framework Standards

### Spring Boot

* governance/standards/java/spring.md

### MyBatis

* governance/standards/java/mybatis.md

### Domain Standards

### MQ Related Task

* governance/standards/mq/rocketmq.md

### REST API Task

* governance/standards/api/rest.md

### Database Task

* governance/standards/java/mybatis.md

* governance/standards/database/sql.md

### Cool College Project

* governance/standards/cool/enum-naming.md

* governance/standards/cool/i18n.md

* governance/standards/cool/enum-dml.md

### Task-Type Standards

### Unit Test Task

* governance/standards/common/testing.md

### Review Task

* governance/standards/common/review-checklist.md

* governance/standards/common/task-quality-checklist.md

### Documentation Task

* governance/standards/common/documentation.md

### Project Memory

### Load Only Relevant Rules

从 coding-memory.md 中只加载与当前任务相关的规则。

例如：

* MQ 任务 → MQ 相关规则

* VO 改造 → VO/Javadoc 相关规则

* 企微接口 → 官方文档优先规则

禁止：

每次加载全部历史规则。

### Example: Java + Spring + MQ Task

Loaded Standards

* AI_OPERATING_RULES.md

* SOURCE_OF_TRUTH.md

* CONTEXT_LOADING.md

* REPOSITORY_FIRST.md

* REFLECTION_RULES.md

* ai-coding-rules.md

* code-quality.md

* clean-code.md

* java-alibaba.md

* documentation.md

* spring.md

* rocketmq.md

* testing.md

* review-checklist.md

* coding-memory.md（仅 MQ 部分）

### Loading Principle

### Must

* 只加载当前任务真正需要的标准

* 优先加载高优先级规则

* 保持 Runtime Prompt 简洁

### Never

* 一次性加载所有规范

* 将历史经验全部注入 Context

* 在 Runtime 中硬编码大量规则

### 如何在 runtime-develop.md 中使用

然后你的 runtime-develop.md 只需要一句：

Runtime Initialization

Load standards according to loaders/standards-loader.md.

### UX 视角的关键收益

* 主 Prompt 变短：Agent 更容易关注核心任务。

* 规则更可发现：开发者能快速找到对应标准。

* 扩展成本低：新增 redis.md、kafka.md 不需要修改 Runtime。

* 多语言友好：Java、Go、Python 可以共用同一套 Workflow。

* 历史经验不会污染所有任务：只在相关场景加载。
