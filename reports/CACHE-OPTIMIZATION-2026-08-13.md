# Token 缓存命中率优化记录 — 2026-08-13

- 日期 / Date: 2026-08-13
- 范围 / Scope: ai-system prompt 构建链路 + skill-optimizer API 调用的 token 缓存命中率优化
- 性质 / Nature: 优化实施（稳定前缀/动态后缀 + 体积骨架化 + 命中率监控）
- 依据 / Basis: DeepSeek 前缀缓存机制（稳定前缀 → 命中缓存 → 成本降至缓存命中价）

---

## 一、背景

DeepSeek 上下文缓存基于**前缀精确匹配**：不同请求开头有一段完全相同的
提示词即可命中。优化核心 = 静态内容前置、动态内容后置。

ai-system 是 **prompt 生成器**（PromptBuilder 生成 prompt → agent 执行），
唯一直调 API 的是 skill-optimizer。两条轨道分别优化。

---

## 二、优化实施（4 项，全部已提交）

### 轨道 A1：主链模板重排（静态前置/动态后置）

| 项 | 内容 |
|----|------|
| 改动 | `templates/prompts/workflow.md` + `command.md`：Operating Rules/工作流定义（静态）前置，workflow_name/inputs（动态）后置 |
| 效果 | 同一工作流重复调用 **99.5% 前缀稳定**（4894/4919 字符一致，动态仅 25 字符） |
| 风险 | 低（纯结构重排，已门禁验证） |

### 轨道 A2：工作流 prompt 骨架化（体积优化）

| 项 | 内容 |
|----|------|
| 改动 | `prompt_builder._skeletonize_runtime()`：runtime 从全量内嵌改为"Phase 标题 + 每阶段首句 + 源文件引用"，agent 执行时按需读取 |
| 效果 | 15 个工作流 prompt 体积**平均省 ~70%**：release 16.6K→3.4K（省79%）、spec 9.8K→1.8K（省82%）、bugfix 11.5K→3.0K（省74%）≈ token release 4158→866 |
| 确定性 | Phase 标题/顺序逐字保留；runtime 源文件未动 |
| 风险 | ⚠️ agent 需按需读完整 runtime 文件（opencode/pi 支持；需实测是否主动读） |

### 轨道 B：skill-optimizer system/user 拆分

| 项 | 内容 |
|----|------|
| 改动 | `core.py __call__` 新增 `system` 参数（向后兼容）；`actions.py` 3 处 prompt 拆为 system（静态指令）+ user（动态数据） |
| 效果 | system 恒定，跨调用前缀可缓存（SYSTEM_EXAMPLES/VALIDATOR/TUNE_DESC） |
| 风险 | 低（默认 None 保持旧行为） |

### 轨道 C：缓存命中率监控

| 项 | 内容 |
|----|------|
| 改动 | `core.py` 模块级 CACHE_STATS + reset/record/cache_stats_report；`main.py` 会话开始 reset、退出 finally 输出 |
| 指标 | 从 response.usage 累计 `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`，命中率 = hit/(hit+miss) |
| 输出 | `[CacheStats] calls=3 hit_tokens=12000 miss_tokens=1700 hit_rate=87.6%`（模拟验证） |

### 安全确认

- `skills/skill-optimizer/.env` 真实 API key：**未跟踪**（.gitignore `.env`/`**/.env` 已排除）
- `.env.example`：占位符 `your_deepseek_api_key_here`，合规
- 历史无 key 提交

---

## 三、验证

| 门禁 | 结果 |
|------|------|
| check.py（含 prompt build smoke 15 工作流） | ✅ PASS |
| repo-lint | ✅ 0 BLOCKER / 0 ERROR / 25 WARNING |
| path-audit | ✅ BROKEN 0 |
| 骨架化对比 | ✅ release 79% / spec 82% / bugfix 74% / 平均 ~70% |
| 命中率计算 | ✅ 模拟 3 调用 87.6% 正确；None usage 跳过 |

---

## 四、风险与后续

| # | 项 | 状态 |
|---|----|------|
| R1 | 骨架化后 agent 是否主动读 runtime 文件（release 依赖） | ⚠️ 待实测——若不读，对关键工作流回退全量内嵌或加"强制全量"配置开关 |
| R2 | 命中率实际值验证 | 待跑真实 skill-optimizer 观察 hit_rate（预期 70%+） |
| R3 | 主链 agent 侧会话历史压缩（多轮摘要前缀） | agent 自管，ai-system 不干预 |

---

## 五、结论

四步优化形成完整闭环：**模板重排（前缀稳定）→ system 拆分（直调可缓存）→
骨架化（体积 -70%）→ 命中率监控（量化验证）**。未命中时峰值输入 token
降 ~70%，命中时缓存空间降 ~70%，叠加命中价折扣，成本优化显著。

**Modified Files**: `templates/prompts/workflow.md`、`templates/prompts/command.md`、
`cli/services/prompt_builder.py`、`skills/skill-optimizer/scripts/core.py`、
`skills/skill-optimizer/scripts/actions.py`、`skills/skill-optimizer/scripts/main.py`
**New Files**: 无（本次为修改）
**Commits**: `67f0373`（轨道A1+B）、`b721baa`（轨道C）、`7a75756`（轨道A2）
**Validation**: 见 §三
**Deviations**: 无
**Risks**: R1（骨架化 agent 读取行为待实测）为唯一待验证项
**Next Recommendation**: 实测 release 工作流观察 agent 读取行为；跑 skill-optimizer 验证实际命中率
