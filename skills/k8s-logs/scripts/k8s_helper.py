#!/usr/bin/env python3
"""
Kubernetes 日志/终端助手 - 支持状态简写过滤和关键词搜索，权限受限时降级手动输入。
用法: ./k8s_helper.py [-n NAMESPACE] [keyword]

调用通道：**WSL 侧原生 `kubectl`**（与 SKILL.md 一致）。未安装 / 未配置时**不静默换通道**
（不回退 `cmd.exe /c`），而是以退出码 2 报出并请求用户授权安装/配置（R4 S2，2026-09-23）。

状态列不是裸 `.status.phase`：`effective_status()` 会把
`containerStatuses[].state.waiting.reason`、`lastState.terminated.reason` 附到相位后
（如 `Running(CrashLoopBackOff)`），否则 CrashLoopBackOff / ImagePullBackOff / OOMKilled
这类故障原因会被 phase 掩盖（外部盲检 R4 §2.3 S3，2026-09-23）。
"""
import argparse
import json
import subprocess
import sys

STATUS_SHORTHAND = {
    'r': 'Running',
    'p': 'Pending',
    's': 'Succeeded',
    'f': 'Failed',
    'u': 'Unknown',
}
SHORTHAND_FOR_STATUS = {v: k.upper() for k, v in STATUS_SHORTHAND.items()}

# lastState.terminated.reason 只在「上一轮死于故障」时才值得上提（OOMKilled / Error）。
# 不收 `state.terminated.reason`：Completed 会盖掉 Succeeded/Failed 的相位语义，反而让
# 状态过滤（-s/-f）失效。
FAILURE_TERMINATION_REASONS = {"OOMKilled", "Error", "ContainerCannotRun"}


def effective_status(pod_status: dict) -> str:
    """由 Pod 的 `.status` 字典算出**可读状态标签**。

    顺序（`state.waiting.reason` → `lastState.terminated.reason` 仅限故障原因）→ 相位：
    - CrashLoopBackOff / ImagePullBackOff 等停滞原因优先（这是 kubectl STATUS 列的本意）；
    - 已重启但现在又在 Running 的容器（lastState 为 OOMKilled/Error）也上提，便于定位；
    - 无原因时退回相位。

    相位本身仍是过滤口径（见 `base_status()`），所以故障 Pod 不会被『Running 过滤』漏掉。
    """
    status = pod_status or {}
    phase = str(status.get("phase") or "Unknown")

    containers: list[dict] = []
    for key in ("initContainerStatuses", "containerStatuses"):
        containers.extend(status.get(key) or [])

    for cs in containers:
        reason = ((cs.get("state") or {}).get("waiting") or {}).get("reason")
        if reason:
            return f"{phase}({reason})"

    for cs in containers:
        reason = ((cs.get("lastState") or {}).get("terminated") or {}).get("reason")
        if reason in FAILURE_TERMINATION_REASONS:
            return f"{phase}({reason})"

    return phase


def base_status(status: str) -> str:
    """状态标签的相位部分（`Running(CrashLoopBackOff)` → `Running`），用于状态过滤。"""
    return str(status).split("(", 1)[0].strip()


KUBECTL_CHANNEL_HELP = (
    "调用通道：WSL 侧原生 kubectl（单一口径，不回退 cmd.exe）。\n"
    "未安装 / 未配置时需你授权后由用户侧完成安装与配置，AI 不自行执行：\n"
    "  1) 安装 kubectl，装后 kubectl version --client 自检；\n"
    "  2) 配置 KUBECONFIG（取 ~/.config/ai-system/env.yaml 的 k8s.kubeconfig-wsl-view），\n"
    "     再以 kubectl get pods -n t2 验证联通；\n"
    "  3) 将 env.yaml 的 k8s.channel 更新为 wsl-native、kubectl-version 更新为 WSL 侧版本。"
)

# kubectl 已装但“未配置/连不上”的典型 stderr（提示用户配置，而非把它当一般错误）
KUBECONFIG_PROBLEM_MARKERS = (
    "no configuration has been provided",
    "Missing or incomplete configuration",
    "invalid configuration",
    "was refused",
    "Unable to connect to the server",
    "no such host",
)


def kubeconfig_hint(stderr: str) -> str:
    """kubectl stderr 命中「未配置/连不上」特征时返回配置提示，否则空串。"""
    text = (stderr or "").lower()
    if any(marker.lower() in text for marker in KUBECONFIG_PROBLEM_MARKERS):
        return ("疑为 kubeconfig 未配置或集群不可达。\n" + KUBECTL_CHANNEL_HELP)
    return ""


def run_kubectl(args: list[str], capture_output: bool = False):
    cmd = ["kubectl"] + args
    try:
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.stdout, result.stderr, result.returncode
        return subprocess.run(cmd).returncode
    except FileNotFoundError:
        # R4 S2：原实现只报「未找到 kubectl 命令」；通道口径为原生 kubectl，缺失时应请用户
        # 授权安装/配置（不静默回退 cmd.exe），退出码 2 与一般失败区分。
        print("错误: WSL 内未找到 kubectl 命令。", file=sys.stderr)
        print(KUBECTL_CHANNEL_HELP, file=sys.stderr)
        sys.exit(2)


def get_all_pods(namespace: str):
    # 改取 `-o json`：状态原因（waiting/terminated/lastState）在 custom-columns 里取不干净，
    # 而仅取 `.status.phase` 正是 S3 的根因。输出不可解析时与获取失败同路降级为手动输入。
    stdout, stderr, code = run_kubectl(
        ["get", "pods", "-n", namespace, "-o", "json"],
        capture_output=True
    )
    if code != 0:
        return [], False, stderr
    try:
        items = (json.loads(stdout) or {}).get("items") or []
    except (json.JSONDecodeError, AttributeError) as exc:
        return [], False, f"kubectl 输出无法解析为 JSON: {exc}"
    pods = []
    for pod in items:
        name = ((pod.get("metadata") or {}).get("name")) or ""
        if not name:
            continue
        pods.append((name, effective_status(pod.get("status") or {})))
    return pods, True, ""


def filter_pods_by_status(pods: list[tuple[str, str]], status_input: str):
    if not status_input:
        return pods
    key = status_input.lower()
    if key in STATUS_SHORTHAND:
        target_status = STATUS_SHORTHAND[key]
    else:
        target_status = status_input.capitalize()
    return [(name, status) for name, status in pods
            if base_status(status).lower() == target_status.lower()]


def filter_pods_by_keyword(pods: list[tuple[str, str]], keyword: str):
    if not keyword:
        return pods
    keyword_lower = keyword.lower()
    return [(name, status) for name, status in pods if keyword_lower in name.lower()]


def print_pod_list(pods: list[tuple[str, str]]):
    if not pods:
        print("  没有匹配的 Pod。")
        return
    print("----------------------------------------")
    print("  编号  Pod 名称 (状态)")
    print("----------------------------------------")
    for idx, (name, status) in enumerate(pods, start=1):
        print(f"  {idx:<4}  {name} ({status})")
    print("----------------------------------------")


def select_pod(pods: list[tuple[str, str]]) -> str:
    while True:
        try:
            choice = input(f"请选择要操作的 Pod 编号 [1-{len(pods)}]: ")
            if not choice:
                continue
            num = int(choice)
            if 1 <= num <= len(pods):
                return pods[num - 1][0]
            print(f"请输入 1 到 {len(pods)} 之间的数字。")
        except ValueError:
            print("请输入有效的数字。")


def select_action() -> list[str]:
    print("\n请选择操作：")
    print("  1) 查看日志 (实时跟踪)")
    print("  2) 查看日志 (最近100行，不跟踪)")
    print("  3) 进入容器终端 (bash)")
    print("  4) 进入容器终端 (sh)")
    while True:
        choice = input("请输入选项 [1-4]: ").strip()
        if choice == "1":
            return ["logs", "-f"]
        if choice == "2":
            return ["logs", "--tail=100"]
        if choice == "3":
            return ["exec", "-it", "--", "/bin/bash"]
        if choice == "4":
            return ["exec", "-it", "--", "/bin/sh"]
        print("无效选项，请输入 1、2、3 或 4。")


def manual_input(namespace: str) -> tuple[str, str]:
    print(f"\n当前命名空间: {namespace}")
    pod = input("请输入 Pod 名称: ").strip()
    while not pod:
        print("Pod 名称不能为空！")
        pod = input("请输入 Pod 名称: ").strip()
    return namespace, pod


def prompt_status_filter() -> str:
    print("\n可用的状态简写 (输入对应字母或完整状态名):")
    for shorthand, full in STATUS_SHORTHAND.items():
        print(f"  {shorthand.upper()} -> {full}")
    default = "Running"
    print(f"  (直接回车则默认: {default})")
    result = input("请输入过滤状态: ").strip()
    return result if result else default


def prompt_keyword_filter() -> str:
    print("\n请输入 Pod 名称关键词进行搜索 (直接回车则跳过):")
    return input("关键词: ").strip()


def build_kubectl_cmd(action_args: list[str], pod_name: str, namespace: str) -> list[str]:
    if action_args[0] == "logs":
        return ["kubectl"] + action_args + [pod_name, "-n", namespace]
    dash_idx = action_args.index("--")
    return ["kubectl"] + action_args[:dash_idx] + [pod_name, "-n", namespace] + action_args[dash_idx:]


def execute_and_exit(action_args: list[str], pod_name: str, namespace: str) -> None:
    final_cmd = build_kubectl_cmd(action_args, pod_name, namespace)
    print(f"\n执行命令: {' '.join(final_cmd)}\n")
    subprocess.run(final_cmd)
    sys.exit(0)


def try_manual_fallback(namespace: str) -> None:
    print("\n你可以选择手动输入 Pod 信息（适用于已知 Pod 名称的情况）。")
    choice = input("是否手动输入？ [y/N]: ").strip().lower()
    if choice in ('y', 'yes'):
        ns, pod_name = manual_input(namespace)
        action_args = select_action()
        execute_and_exit(action_args, pod_name, ns)
    print("已退出。")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Kubernetes 日志/终端助手（状态简写 + 关键词搜索）")
    parser.add_argument("-n", "--namespace", default="t2",
                        help="Kubernetes 命名空间 (默认: t2)")
    parser.add_argument("keyword", nargs="?", default=None,
                        help="Pod 名称关键词（快捷模式：直接筛选并自动选择最后一个 Pod）")
    args = parser.parse_args()

    namespace = args.namespace
    print(f"使用命名空间: {namespace}")

    all_pods, success, error_msg = get_all_pods(namespace)
    if not success:
        print(f"\n无法获取命名空间 [{namespace}] 的 Pod 列表: {error_msg.strip()}")
        hint = kubeconfig_hint(error_msg)
        if hint:
            print(hint, file=sys.stderr)
        try_manual_fallback(namespace)

    if not all_pods:
        print(f"\n命名空间 [{namespace}] 下没有任何 Pod。")
        try_manual_fallback(namespace)

    status_counts: dict[str, int] = {}
    for _, status in all_pods:
        status_counts[status] = status_counts.get(status, 0) + 1
    print(f"\n命名空间 [{namespace}] 中共有 {len(all_pods)} 个 Pod，各状态分布:")
    for st, cnt in status_counts.items():
        shorthand = SHORTHAND_FOR_STATUS.get(st, '')
        if shorthand:
            print(f"  {st} ({shorthand}): {cnt}")
        else:
            print(f"  {st}: {cnt}")

    if args.keyword:
        filtered = filter_pods_by_status(all_pods, "Running")
        filtered = filter_pods_by_keyword(filtered, args.keyword)
        if not filtered:
            print(f"\n没有匹配关键词 '{args.keyword}' 的 Running 状态 Pod。")
            choice = input("是否显示所有 Pod 并继续？ [y/N]: ").strip().lower()
            if choice in ('y', 'yes'):
                filtered = all_pods
            else:
                try_manual_fallback(namespace)

        if len(filtered) == 1:
            pod_name = filtered[0][0]
            print(f"\n自动选择 Pod: {pod_name}")
        else:
            print(f"\n匹配到 {len(filtered)} 个 Pod:")
            print_pod_list(filtered)
            pod_name = select_pod(filtered)
            print(f"你选择了 Pod: {pod_name}")

        action_args = select_action()
        execute_and_exit(action_args, pod_name, namespace)
        return

    status_filter = prompt_status_filter()
    filtered_by_status = filter_pods_by_status(all_pods, status_filter)
    if not filtered_by_status:
        display = status_filter.upper() if status_filter.lower() in STATUS_SHORTHAND else status_filter
        print(f"\n没有状态为 '{display}' 的 Pod。")
        choice = input("是否显示所有 Pod 并继续？ [y/N]: ").strip().lower()
        if choice in ('y', 'yes'):
            current_pods = all_pods
        else:
            try_manual_fallback(namespace)
    else:
        current_pods = filtered_by_status

    keyword = prompt_keyword_filter()
    if keyword:
        filtered_by_keyword = filter_pods_by_keyword(current_pods, keyword)
        while not filtered_by_keyword:
            print(f"\n没有 Pod 名称包含关键词 '{keyword}'。")
            choice = input("是否显示所有 Pod（放弃关键词过滤）？ [y/N]: ").strip().lower()
            if choice in ('y', 'yes'):
                filtered_by_keyword = current_pods
                break
            retry = input("是否重新输入关键词？ [y/N]: ").strip().lower()
            if retry in ('y', 'yes'):
                keyword = prompt_keyword_filter()
                filtered_by_keyword = filter_pods_by_keyword(current_pods, keyword)
            else:
                try_manual_fallback(namespace)
    else:
        filtered_by_keyword = current_pods

    print(f"\n最终 Pod 列表 (共 {len(filtered_by_keyword)} 个):")
    print_pod_list(filtered_by_keyword)
    pod_name = select_pod(filtered_by_keyword)
    print(f"你选择了 Pod: {pod_name}")

    action_args = select_action()
    execute_and_exit(action_args, pod_name, namespace)


if __name__ == "__main__":
    main()
