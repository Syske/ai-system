#!/usr/bin/env python3
"""
idea-mcp — IntelliJ IDEA MCP Server CLI 客户端(通用)

通过 IDEA 内置 MCP Server 调用 build_project(IDE 常驻增量编译器,秒级),
替代 CLI mvnw 冷启动编译(62-70s)。任何 AI agent 可通过 bash 调用。

已验证连接(2026-08-07, IDEA 2026.2.0.1 Ultimate, 见 ai-system/skills/java-maven/idea-build.md):
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
                        except Exception:
                            pass
        except Exception:
            pass
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
            urllib.request.urlopen(req, timeout=30)
        except Exception:
            pass  # 202 Accepted;响应从 SSE 推送
        start = time.time()
        rid = payload.get("id")
        while time.time() - start < wait_ms / 1000:
            if rid in messages:
                return messages[rid]
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


def cmd_build(port, project, rebuild=False):
    post = mcp_session(port, project)
    rpc(post, "initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "idea-mcp-cli", "version": "1.0"},
    })
    result = rpc(post, "tools/call", {
        "name": "build_project",
        "arguments": {"projectPath": project, "rebuild": rebuild},
    }, _id=3)
    content = result.get("result", {}).get("content", [])
    text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
    print(text)
    # 退出码:isError 或编译失败返回非 0
    if result.get("result", {}).get("isError"):
        sys.exit(1)
    sys.exit(0)


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
    args = parser.parse_args()

    port = int(__import__("os").environ.get("IJ_MCP_SERVER_PORT", DEFAULT_PORT))
    project = args.target or __import__("os").environ.get("IJ_MCP_SERVER_PROJECT_PATH") or "."

    try:
        if args.command == "tools":
            cmd_tools(port, project)
        elif args.command == "build":
            cmd_build(port, project, rebuild=args.rebuild)
        elif args.command == "exec":
            if not args.rest:
                print("用法: idea-mcp.py exec <projectPath> <command> [args...]", file=sys.stderr)
                sys.exit(2)
            cmd_exec(port, project, args.rest[0], args.rest[1:])
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        print("回退: CLI 离线编译 mvnw -s <settings> -pl <mod> -am compile -o"
              "(见 ai-system/skills/java-maven/build-speed.md)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
