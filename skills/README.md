# Skills Index

## Workflow-Bound Skills (17)

These skills are directly invoked by at least one Workflow Runtime.

| Skill | Bound To | Category |
|---|---|---|
| implement | develop, bugfix | Core |
| bugfix | bugfix | Core |
| review | review | Quality Gate |
| mock-test | develop | Testing |
| java-maven | develop, dev-setup | Language |
| task-splitter | spec | Planning |
| grilling | spec (Phase 2.5, optional) | Design |
| architecture/architecture-base | spec, prepare | Architecture |
| architecture/context-architect | dev-setup | Architecture |
| architecture/design-review | review | Architecture |
| architecture/platform-governor | bootstrap, dev-setup | Architecture |
| architecture/provider-architect | bootstrap | Architecture |
| architecture/runtime-architect | bootstrap | Architecture |
| architecture/workflow-architect | bootstrap | Architecture |
| repository-governor | analysis | Governance |
| repository-maintainer | analysis | Governance |
| contract-maintainer | spec | Governance |

## On-Demand Skills (21)

These skills are useful but are manually invoked. They are NOT bound to any Workflow.

| Skill | Purpose | Invocation |
|---|---|---|
| agent-browser | Web browsing capabilities | Manual |
| agent-debug-diagnosis | Debug diagnosis with knowledge graph | Manual |
| autowork | Autonomous task execution | Manual |
| explore-codebase | Knowledge-graph-driven codebase exploration | Manual |
| debug-issue | Knowledge-graph-driven issue debugging | Manual |
| index-project | Rebuild code semantic index | Manual |
| k8s-logs | K8s 日志/终端排查（原生 kubectl 通道；t2） | Manual |
| open-cli | Web API → CLI adapter generation | Manual |
| spec-updater | 需求变更录入（S1-S3）→ 联动 contract-maintainer（从 methodologies 迁入 2026-09-17） | Manual |
| openspec-archive-change | 归档已完成的 OpenSpec 变更（从 methodologies 迁入 2026-09-17） | Manual |
| openspec-explore | OpenSpec 变更前探索模式（想法/问题/需求澄清，从 methodologies 迁入 2026-09-17） | Manual |
| wayfinder | 大块模糊构想 → 决策图（规划，非执行） | Manual |
| deepseek-share-to-md | DeepSeek 分享会话 → Markdown（stdout 供 AI 读取 / 导出为文件+附件内嵌）。触发词：`deepseek 分享转 md`、`导出 deepseek 对话`、`分享链接转 markdown`、`存档 AI 对话`（`chat.deepseek.com/share/<id>`）。外部 AI 结论进入消息流时优先路由至此拉取文本再核验（配合 P3 外部结论核查）。 | Manual |
| idea-build | Optional IDEA MCP compile backend (`build.backend=idea`) | Config-driven (bugfix), manual |
| handoff | Session handoff summary (compaction / task switch / cross-tool), per CONTEXT_RETENTION Keep/Drop | Manual (before /compact or new session) |
| explore | OpenSpec-aware exploration support (loaded by aic-explore) | Command-loaded (aic-explore) |
| archive-openspec | ~~OpenSpec change archive procedure (archived 2026-09-09, zero usage)~~ | removed |
| propose-openspec | OpenSpec change creation procedure (loaded by aic-propose) | Command-loaded (aic-propose) |
| apply-openspec | ~~OpenSpec implementation procedure, develop contract (archived 2026-09-09, zero usage)~~ | removed |
| memory-capture | Capture verified session experience into Coding Memory (MEMORY_GUIDELINES, dedupe via index) | Session end / explicit request |
| review-changes | (manual / on-demand) | Analysis |

## Optimization & Benchmarking Skills (1)

These skills are for internal AI system optimization. They are NOT part of the development pipeline.

| Skill | Purpose |
|---|---|
| skill-benchmark-generator | Generate routing + outcome benchmarks (merged from routing-/outcome-generators) |

## Skill Creation (1)

| Skill | Purpose |
|---|---|
| skill-author | Author new skills following governance |
