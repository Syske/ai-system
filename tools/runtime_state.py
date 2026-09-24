#!/usr/bin/env python3
"""运行时态的路径单一来源（2026-09-24 起）。

运行时态（运行日志、健康指标快照）**一律放在工作区层、仓库之外**：
2026-09-24 事故中，仓库内且被 gitignore 的 `ai-system/logs/` 被一条 `git clean -fdx` 清空
（约 200 份记录不可恢复），根因是**位置**（在仓库工作树内 + 被忽略 = 恰好是 `-x` 的清除目标）。
把运行时态移出所有仓库后，任何仓库的 `git clean` / `checkout` 都结构性碰不到它。

约定 SSOT：
- 日志：`templates/runtime/runtime-diagnostic-log.md`
- 目录职责：`governance/DIRECTORY-RESPONSIBILITY.md`
- 护栏（受保护路径 + 破坏性操作）：`config/protected-paths.yaml` + `governance/AI_OPERATING_RULES.md`

用法（工具脚本内）：
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import runtime_state
    runtime_state.LOG_DIR / runtime_state.METRICS_DIR
"""

import os
from pathlib import Path

AIS = Path(__file__).resolve().parents[1]


def workspace_root():
    """工作区根：默认 = ai-system 的上层目录；可用环境变量覆盖（测试 / 异地布局）。"""
    override = os.environ.get("AI_SYSTEM_WORKSPACE_ROOT")
    return Path(override).resolve() if override else AIS.parent


LOG_DIR = workspace_root() / "logs"
METRICS_DIR = workspace_root() / "metrics"