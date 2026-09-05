---
name: k8s-logs
description: >
  查看 t2/开发环境 Kubernetes 服务日志与排查。
  通过 Windows 侧 kubectl（cmd.exe 通道）执行只读操作：
  Pod 发现、日志查看/跟踪/过滤、事件与崩溃排查；
  附交互式助手脚本（人用）。
---

# K8s Logs Skill

## 用途

查看开发/测试环境（t2 命名空间）服务日志、定位异常与崩溃排查。
只读优先；任何变更类操作（exec 进容器、delete/scale/apply）必须先获用户确认。

## 调用通道与配置文件位置（重要）

**配置单一来源：`~/.config/ai-system/env.yaml` 的 `k8s:` 段**（机器层配置，与其他技能共享同一配置点；换机/改路径只改该文件，本 skill 文档不随环境变化）。使用前先读取该段获取实际值：

| 键 | 说明 | 当前值 |
|---|---|---|
| `channel: wsl-cmd` | 调用方式 = `cmd.exe /c "kubectl ..."`（WSL 未装 kubectl，不要在 WSL 找） | wsl-cmd |
| `kubeconfig-win` | kubeconfig 位置（Windows 默认位置，KUBECONFIG 未设置；WSL 侧无 `~/.kube`） | `<windows-user-kubeconfig>`（Windows 用户默认 kubeconfig，实际值见 env.yaml） |
| `context` | 当前 context（单 context） | <context-id>（实际值见 env.yaml） |
| `namespace` | 默认命名空间 | t2 |
| `t2-gateway` | 测试环境服务入口（连通性验证用） | <t2-gateway-url>（测试环境入口，实际值见 env.yaml） |

RBAC 限制：仅命名空间内资源可操作（`get namespaces` 会 Forbidden——属预期，直接 `-n t2` 操作即可）。

## 快速命令（agent 首选，非交互）

```bash
# Pod 发现（按服务名过滤）
cmd.exe /c "kubectl get pods -n t2 -o wide" 2>/dev/null | grep <service>

# 最近日志（最近 100 行）
cmd.exe /c "kubectl logs <pod> -n t2 --tail=100" 2>/dev/null

# 时间窗日志（最近 10 分钟）
cmd.exe /c "kubectl logs <pod> -n t2 --since=10m" 2>/dev/null

# 实时跟踪（Ctrl+C 终止；agent 谨慎使用，建议加 timeout）
timeout 30 cmd.exe /c "kubectl logs -f <pod> -n t2 --tail=20" 2>/dev/null

# 关键字过滤（错误/异常）
cmd.exe /c "kubectl logs <pod> -n t2 --tail=500" 2>/dev/null | grep -iE "ERROR|Exception"

# 崩溃排查：上一次崩溃的日志（CrashLoopBackOff 必用）
cmd.exe /c "kubectl logs <pod> -n t2 -p --tail=100" 2>/dev/null

# 事件与详情
cmd.exe /c "kubectl get events -n t2 --sort-by=.lastTimestamp" 2>/dev/null | grep <service>
cmd.exe /c "kubectl describe pod <pod> -n t2" 2>/dev/null
```

### 多容器 Pod 注意

t2 环境 Pod 多为 **2/2 容器**（主容器 + sidecar），`kubectl logs` 报
`a container name must be specified` 时用 `-c` 指定主容器（一般与 Pod 名前缀/服务名同名）：

```bash
cmd.exe /c "kubectl logs <pod> -n t2 -c <主容器名> --tail=100" 2>/dev/null
```

## 交互式助手（人用，agent 不使用交互模式）

```bash
python3 <ai-system>/skills/k8s-logs/scripts/k8s_helper.py [-n t2] [keyword]
```

功能：状态简写过滤（r=Running/p=Pending/f=Failed）+ 关键词过滤 → 选择 Pod →
日志跟踪/最近日志/bash/sh 终端。权限受限时自动降级为手动输入 Pod 名。

## 已知环境实况（2026-09-05）

- `bs-integration-service-*`：2/2 Running（本项目服务，刚部署）
- 环境中存在长态异常 Pod（`oneops-java` CrashLoopBackOff、`html2pdf-api` 旧实例 ImagePullBackOff）——
  排查时勿混淆目标服务

## 安全规则

1. 默认只读：get/logs/describe/events 可直接执行
2. `kubectl exec` 进容器：**先向用户确认**
3. 禁止执行：`delete` / `scale` / `apply` / `rollout` / `edit` / `cp`（写方向）——除非用户明确指令
4. 日志可能含敏感信息（token/手机号）：引用到对话时脱敏
