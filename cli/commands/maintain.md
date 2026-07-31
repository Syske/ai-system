---
description: AI 系统维护 - repo-lint 校验 + repository-maintainer 巡检 + 治理一致性抽查
---

对 ai-system 与工作流体系执行例行维护：工具校验、按模式巡检、契约一致性抽查，产出维护报告。

**输入**：Mode（weekly / monthly / quarterly / on-demand，默认 weekly）；可选 Scope（on-demand 时限定范围，如 workflows / runtime / skills / governance / cli）。

**步骤**

1. **工具校验**（在 ai-system 目录执行）

   ```bash
   python tools/repo-lint.py --repo-root .
   python tools/repo-metrics.py --repo-root . --snapshot metrics/maintain-{date}.json
   python tools/path-audit.py
   ```

   修复 BLOCKER / ERROR 前不得进入后续步骤（只报告，不擅自修）。

2. **按模式巡检**（依据 skills/repository-maintainer 与 OPERATIONS.md 第 9 节）
   - weekly：重复度报告、依赖图、孤儿资产、健康分
   - monthly：架构评审、能力矩阵、生命周期报告、演进建议
   - quarterly：workflow 重设计评估、能力重组、Playbook 合并、知识清理
   - on-demand：按 Scope 执行上述对应项

3. **治理一致性抽查**（每次必做，防既往问题复发）
   - workflows/*.md：八段齐全且顺序一致（Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next）；术语符合 README 术语表；Runtime 引用文件存在；Preconditions/Next 链路闭合
   - config/workflows/*.yaml：保持注册表最小三字段（name/workflow/runtime），未重新膨胀出 inputs/outputs/next（防 A1 复发）
   - 引用路径实存：governance/standards/、loaders/、templates/prompts/、cli/commands/ 中引用的文件全部存在（防 stangards / runtime-workspace 类断链复发）
   - 链接健康：projects/ 等 junction/软连接的目标目录存在且可访问（`Get-Item -Force` 校验 LinkType 与 Target）
   - 文档-现实一致：AGENTS.md 工作区结构图、AI_DEVELOPMENT_CONTRACT 架构图、OPERATIONS 入口章节与目录现实一致
   - 状态卫生：workspaces/.aic-state.yaml 中的项目/变更引用仍然存在

4. **报告落盘**
   - 写入 ai-system/reports/MAINTENANCE-{date}.md：发现清单（按严重度）、修复建议、指标对比（与上次 snapshot）
   - 轻微问题（拼写、断链、文档漂移）可在确认后就地修复并记录
   - 结构性变更（目录调整、模块合并、契约修改）**只输出建议**，走 OPERATIONS 第 11 节变更管理流程（Analyze → Propose → Review → Approve）

**输出**

## Maintenance Report

- 工具校验结果（lint BLOCKER/ERROR/WARN 计数、指标变化）
- 巡检发现（按严重度分级）
- 一致性抽查结论（逐项通过/失败）
- 修复动作与建议清单

**护栏**

- 遵循 AI_DEVELOPMENT_CONTRACT：不重设计架构、不跨模块搬职责、结构性变更禁止直接实施
- 每一批修复前确认（Change Control）
- 巡检只读优先；修改仅限确认后的轻微修复
