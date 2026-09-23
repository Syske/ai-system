---
name: k8s-logs
description: >
  查看 t2/开发环境 Kubernetes 服务日志与排查。
  通过 WSL 侧原生 kubectl 执行只读操作（未安装/未配置时先请用户授权安装配置）：
  Pod 发现、日志查看/跟踪/过滤、事件与崩溃排查；
  附交互式助手脚本（人用）。
---

# K8s Logs Skill

## 用途

查看开发/测试环境（t2 命名空间）服务日志、定位异常与崩溃排查。
只读优先；任何变更类操作（exec 进容器、delete/scale/apply）必须先获用户确认。

## 调用通道与配置文件位置（重要）

**调用通道：WSL 侧原生 `kubectl`**（唯一口径，SKILL 与 `scripts/k8s_helper.py` 一致）。

**配置单一来源：`~/.config/ai-system/env.yaml` 的 `k8s:` 段**（机器层配置，与其他技能共享同一配置点；换机/改路径只改该文件，本 skill 文档不随环境变化）。使用前先读取该段获取实际值：

| 键 | 说明 |
|---|---|
| `channel` | 期望值 `wsl-native`（WSL 内直接执行 `kubectl`）。历史值 `wsl-cmd`（`cmd.exe /c`）已**不再使用**——遇到即视为待迁移配置 |
| `kubeconfig-wsl-view` | WSL 可见的 kubeconfig 路径（形如 `/mnt/c/Users/<win-user>/.kube/config`），配置 `KUBECONFIG` 用 |
| `kubeconfig-win` | Windows 侧 kubeconfig（迁移/对照用） |
| `context` / `namespace` | 当前 context / 默认命名空间（t2） |
| `t2-gateway` | 测试环境服务入口（连通性验证用） |

RBAC 限制：仅命名空间内资源可操作（`get namespaces` 会 Forbidden——属预期，直接 `-n t2` 操作即可）。

### kubectl 缺失或未配置时（**不要静默换通道**）

WSL 内 `command -v kubectl` 为空，或 `kubectl` 报出 kubeconfig 缺失 / 连不上集群时，**停下来向用户请求授权**，
由用户决定是否安装/配置（安装属机器级变更，AI 不得自行执行）：

1. 安装：在 WSL 内安装 kubectl（发行版包管理器或官方二进制），装后 `kubectl version --client` 自检；
2. 配置：导出 `KUBECONFIG=<env.yaml 的 kubeconfig-wsl-view>`（或软链到 `~/.kube/config`），
   再以 `kubectl get pods -n t2` 验证联通；
3. 把 `env.yaml` 的 `k8s.channel` 更新为 `wsl-native`、`kubectl-version` 更新为 WSL 侧版本。

**明确不做**：不自动回退到 `cmd.exe /c "kubectl ..."`；不自动安装或改配置。

## 快速命令（agent 首选，非交互）

```bash
# Pod 发现（按服务名过滤）
kubectl get pods -n t2 -o wide 2>/dev/null | grep <service>

# 最近日志（最近 100 行）
kubectl logs <pod> -n t2 --tail=100 2>/dev/null

# 时间窗日志（最近 10 分钟）
kubectl logs <pod> -n t2 --since=10m 2>/dev/null

# 实时跟踪（Ctrl+C 终止；agent 谨慎使用，建议加 timeout）
timeout 30 kubectl logs -f <pod> -n t2 --tail=20 2>/dev/null

# 关键字过滤（错误/异常）
kubectl logs <pod> -n t2 --tail=500 2>/dev/null | grep -iE "ERROR|Exception"

# 崩溃排查：上一次崩溃的日志（CrashLoopBackOff 必用）
kubectl logs <pod> -n t2 -p --tail=100 2>/dev/null

# 事件与详情
kubectl get events -n t2 --sort-by=.lastTimestamp 2>/dev/null | grep <service>
kubectl describe pod <pod> -n t2 2>/dev/null
```

### 多容器 Pod 注意

t2 环境 Pod 多为 **2/2 容器**（主容器 + sidecar），`kubectl logs` 报
`a container name must be specified` 时用 `-c` 指定主容器（一般与 Pod 名前缀/服务名同名）：

```bash
kubectl logs <pod> -n t2 -c <主容器名> --tail=100 2>/dev/null
```

## 交互式助手（人用，agent 不使用交互模式）

```bash
python3 <ai-system>/skills/k8s-logs/scripts/k8s_helper.py [-n t2] [keyword]
```

功能：状态简写过滤（r=Running/p=Pending/f=Failed）+ 关键词过滤 → 选择 Pod →
日志跟踪/最近日志/bash/sh 终端。权限受限时自动降级为手动输入 Pod 名。

## 环境探活（每次实时探测，**不写时间点快照**）

Pod 名单、容器数与 Pod 状态随部署变化，文档里的时间点快照必然过期，一律实时探测：

```bash
kubectl get pods -n t2 -o wide 2>/dev/null                     # 全量现状
kubectl get pods -n t2 --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c   # 状态分布
```

判读要点：`CrashLoopBackOff` / `ImagePullBackOff` / `OOMKilled` 等**原因**不在
`.status.phase` 里（phase 可能仍是 Running/Pending）——用 `kubectl describe pod <pod> -n t2`
或 `kubectl get pod <pod> -n t2 -o jsonpath='{.status.containerStatuses[*].state.waiting.reason}'`
取原因；`scripts/k8s_helper.py` 的状态列已内置该解析（`Running(CrashLoopBackOff)` 形态）。

## 安全规则

1. 默认只读：get/logs/describe/events 可直接执行
2. `kubectl exec` 进容器：**先向用户确认**
3. 禁止执行：`delete` / `scale` / `apply` / `rollout` / `edit` / `cp`（写方向）——除非用户明确指令
4. 日志可能含敏感信息（token/手机号）：引用到对话时脱敏
