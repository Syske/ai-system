#!/usr/bin/env python3
"""
idea-mcp — IntelliJ IDEA MCP Server CLI 客户端(通用)

通过 IDEA 内置 MCP Server 调用 build_project(IDE 常驻增量编译器,秒级),
替代 CLI mvnw 冷启动编译(62-70s)。任何 AI agent 可通过 bash 调用。

已验证连接(2026-08-07, IDEA 2026.2.0.1 Ultimate, 见 ai-system/skills/idea-build/SKILL.md):
  SSE:  http://127.0.0.1:64342/sse   (IDEA 内置端口 63342 + 1000)
  Header: IJ_MCP_SERVER_PROJECT_PATH=<项目路径>

用法:
  python idea-mcp.py tools                  # 列出工具
  python idea-mcp.py build <projectPath>    # 编译(增量)
  python idea-mcp.py build --rebuild <path> # 全量重建
  python idea-mcp.py exec <projectPath> <cmd> [args...]   # 终端执行命令(需 Brave Mode 或确认)

环境变量:
  IJ_MCP_SERVER_PORT      # 默认 64342
  IJ_MCP_SERVER_PROJECT_PATH  # 默认取第一个参数或 cwd
"""

import argparse
import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request

DEFAULT_PORT = 64342
# IDEA MCP Server 端口与 IDEA executable 均可由环境变量覆盖(见 ai-system/config/environments/{env}.yaml build.idea.*)
IDEA_EXECUTABLE = __import__("os").environ.get("IJ_MCP_SERVER_EXECUTABLE", "")


def mcp_session(port, project_path, timeout=120):
    """建立 SSE 会话:单条 SSE 连接提供 sessionId + 消息推送,POST 复用该会话。"""
    base = f"http://127.0.0.1:{port}"
    headers = {"IJ_MCP_SERVER_PROJECT_PATH": project_path}
    messages = {}
    session_id = {"value": None}
    stop = threading.Event()
    sse_state = {"error": None}    # SSE 断线原因(供 POST 快速失败时说明)
    post_errors: list[str] = []    # POST 侧真实异常/非 202（不再静默 pass）

    def sse_listener():
        req = urllib.request.Request(base + "/sse", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line:
                        continue
                    m = re.search(r"sessionId=([a-f0-9-]+)", line)
                    if m and session_id["value"] is None:
                        session_id["value"] = m.group(1)
                    if line.startswith("data: "):
                        try:
                            msg = json.loads(line[6:])
                            if msg and msg.get("id") is not None:
                                messages[msg["id"]] = msg
                        except Exception as exc:
                            # 单条消息解析失败不致命，但必须可见
                            print(f"[WARN] SSE 消息解析失败: {exc}", file=sys.stderr)
        except Exception as exc:
            # R4 S4：原实现静默 pass → 下游 POST 空等满 180s 才知道失败
            sse_state["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[WARN] SSE 通道中断: {sse_state['error']}", file=sys.stderr)
        finally:
            stop.set()

    t = threading.Thread(target=sse_listener, daemon=True)
    t.start()

    deadline = time.time() + 10
    while not session_id["value"] and time.time() < deadline and not stop.is_set():
        time.sleep(0.3)

    if not session_id["value"]:
        raise RuntimeError(
            f"IDEA MCP Server 不可达 ({base}/sse)。请确认: "
            "①IDEA 已启用 MCP Server(设置→Tools→MCP Server→Enable MCP Server); "
            f"②目标项目已在 IDEA 中打开(当前: {project_path})"
        )

    def post(payload, wait_ms=180000):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            base + f"/message?sessionId={session_id['value']}",
            data=data, headers={**headers, "Content-Type": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30):
                pass
        except urllib.error.HTTPError as exc:
            # 202 Accepted 是正常路径（响应从 SSE 推送）；其余状态码必须可见
            if exc.code != 202:
                post_errors.append(f"HTTP {exc.code}")
                print(f"[WARN] POST 返回 HTTP {exc.code}（{payload.get('method')}）", file=sys.stderr)
        except Exception as exc:
            post_errors.append(f"{type(exc).__name__}: {exc}")
            print(f"[WARN] POST 发送异常 {post_errors[-1]}（{payload.get('method')}）", file=sys.stderr)
        start = time.time()
        rid = payload.get("id")
        while time.time() - start < wait_ms / 1000:
            if rid in messages:
                return messages[rid]
            if stop.is_set():
                # SSE 已终止 → 推送通道不存在，响应不可能到达：立即失败（原实现空等满 180s）
                why = sse_state["error"] or "SSE 流已结束"
                if post_errors:
                    why += f"；POST 侧异常 {len(post_errors)} 次（最近 {post_errors[-1]}）"
                raise RuntimeError(
                    f"SSE 通道已断开，收不到 {payload.get('method')} 的响应: {why}。"
                    "请确认 IDEA MCP Server 仍在运行且目标项目未关闭")
            time.sleep(0.5)
        raise TimeoutError(f"IDEA MCP 响应超时 ({wait_ms}ms): {payload.get('method')}")

    return post


def rpc(post, method, params=None, _id=1):
    return post({"jsonrpc": "2.0", "id": _id, "method": method, "params": params or {}})


def cmd_tools(port, project):
    post = mcp_session(port, project)
    rpc(post, "initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "idea-mcp-cli", "version": "1.0"},
    })
    result = rpc(post, "tools/list", {}, _id=2)
    tools = result.get("result", {}).get("tools", [])
    print(f"工具数: {len(tools)}")
    for t in tools:
        print(f"  - {t['name']}: {t.get('description', '')[:60]}")


def cmd_build(port, project, rebuild=False, files=None):
    post = mcp_session(port, project)
    rpc(post, "initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "idea-mcp-cli", "version": "1.0"},
    })
    args = {"projectPath": project, "rebuild": rebuild}
    if files:
        args["files"] = files
    result = rpc(post, "tools/call", {
        "name": "build_project",
        "arguments": args,
    }, _id=3)
    content = result.get("result", {}).get("content", [])
    text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    print(text)
    # 退出码:isError 或编译失败返回非 0。
    # SKILL.md 记载 build_project 返回 {"isSuccess":true,"problems":[...]}，
    # 原实现只查 isError（契约未提及该字段）→ 编译失败(isSuccess=false)会静默 exit 0
    # （2026-09-21 外部盲检 T4）。此处按文档契约补判 isSuccess（兼容结构化字段与 JSON 文本）。
    res = result.get("result", {})
    failed = bool(res.get("isError"))
    if not failed:
        payload = res
        if isinstance(text, str) and text.strip().startswith("{"):
            try:
                payload = json.loads(text)
            except ValueError:
                payload = res
        if isinstance(payload, dict) and payload.get("isSuccess") is False:
            failed = True
    sys.exit(1 if failed else 0)


def cmd_exec(port, project, command, args):
    post = mcp_session(port, project)
    rpc(post, "initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "idea-mcp-cli", "version": "1.0"},
    })
    result = rpc(post, "tools/call", {
        "name": "execute_terminal_command",
        "arguments": {"command": command, "args": args},
    }, _id=3)
    content = result.get("result", {}).get("content", [])
    print("\n".join(c.get("text", "") for c in content if c.get("type") == "text"))


def main():
    parser = argparse.ArgumentParser(description="IDEA MCP CLI")
    parser.add_argument("command", choices=["tools", "build", "exec"])
    parser.add_argument("target", nargs="?", help="项目路径(默认当前目录)")
    parser.add_argument("rest", nargs="*", help="exec: command 及其参数; build: --rebuild 标志")
    parser.add_argument("--rebuild", action="store_true", help="build: 全量重建")
    parser.add_argument("--files", action="append", default=[], help="build: 指定编译文件(可多次, IDEA 项目内路径)")
    args = parser.parse_args()

    port = int(__import__("os").environ.get("IJ_MCP_SERVER_PORT", DEFAULT_PORT))
    project = args.target or __import__("os").environ.get("IJ_MCP_SERVER_PROJECT_PATH") or "."

    try:
        if args.command == "tools":
            cmd_tools(port, project)
        elif args.command == "build":
            cmd_build(port, project, rebuild=args.rebuild, files=args.files)
        elif args.command == "exec":
            if not args.rest:
                print("用法: idea-mcp.py exec <projectPath> <command> [args...]", file=sys.stderr)
                sys.exit(2)
            cmd_exec(port, project, args.rest[0], args.rest[1:])
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        print("回退: 使用环境配置 build.java_home / build.maven_home 执行 CLI 离线编译 "
              "(JAVA_HOME=<java_home> <maven_home>/bin/mvn -s <settings> -pl <mod> -am compile -o; "
              "配置来源: 由 AI_SYSTEM_ROOT/上溯定位 ai-system 后, 读取 "
              "config/environments/{env}.yaml 的 build.*; 见 "
              "ai-system/skills/idea-build/SKILL.md 的 Configuration/JDK-Maven compatibility)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
