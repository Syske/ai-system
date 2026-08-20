#!/usr/bin/env python3
"""
deepseek_share_to_md.py — 将 DeepSeek 分享会话链接转换为 Markdown 文档。

原理: 分享链接 (https://chat.deepseek.com/share/<id>) 是公开页面，无需登录。
前端通过公开 API GET /api/v0/share/content?share_id=<id> 获取会话 JSON。
新版响应包含 fragments (REQUEST/RESPONSE/FILE/SEARCH/TIP)，文件片段内嵌
signed_path 签名路径，拼上 https://files.deepseeksvc.com/api 即可下载附件。
零第三方依赖（仅 Python 3 标准库）。

两种使用场景:
  场景1（AI 读取）: 默认将 Markdown 全文输出到 stdout，AI 可直接消费会话内容。
  场景2（用户导出）: 用 -o 或 --dir 写入 md 文件，附件自动下载到附件目录。

用法:
    python3 deepseek_share_to_md.py <share_url_or_id>             # stdout 输出（场景1）
    python3 deepseek_share_to_md.py <share_url_or_id> -o out.md   # 写文件+下载附件（场景2）
    python3 deepseek_share_to_md.py <url> --dir ./exports         # 自动命名写目录
    python3 deepseek_share_to_md.py <url> -o out.md --no-download # 只要 md 不要附件
    python3 deepseek_share_to_md.py <url> --raw-json              # 输出原始 API JSON

示例:
    python3 deepseek_share_to_md.py https://chat.deepseek.com/share/95z1fr6y7rj4q5nmd0
    python3 deepseek_share_to_md.py 95z1fr6y7rj4q5nmd0 -o chat.md
    python3 deepseek_share_to_md.py <url> --dir ./exports
"""

import argparse
import datetime
import html
import json
import os
import re
import sys
import urllib.request
import urllib.error

API_URL = "https://chat.deepseek.com/api/v0/share/content"
FILE_BASE = "https://files.deepseeksvc.com/api"

# 文本扩展名：内容直接内嵌进 md（其余类型只保存本地 + 链接）
TEXT_EXTENSIONS = {".txt", ".log", ".md", ".markdown", ".json", ".csv", ".tsv", ".xml", ".yaml",
                  ".yml", ".toml", ".ini", ".conf", ".cfg", ".properties", ".env", ".sh",
                  ".bash", ".zsh", ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go",
                  ".rs", ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".sql", ".css",
                  ".html", ".htm", ".svg", ".diff", ".patch", ".gradle", ".lock",
                  ".gitignore", ".dockerignore", ".sass", ".scss", ".vue"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".avif"}
# 文件大于该阈值时不内嵌文本内容（避免 md 膨胀），仅保存 + 链接
INLINE_TEXT_MAX_BYTES = 200 * 1024

# 与前端浏览器一致的请求头。x-client-bundle-id=x-client-version 决定响应结构:
#   com.deepseek.chat / 2.3.0 → 新版本结构 (messages[].fragments，含 signed_path)
#   chat-web-prod / 1.0.0     → 老版本结构 (messages[].content + messages[].files 元信息)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0",
    "Referer": "https://chat.deepseek.com/",
    "Accept": "*/*",
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-platform": "web",
    "x-client-version": "2.3.0",
    "x-client-locale": "zh_CN",
    "x-client-timezone-offset": "28800",
}


def extract_share_id(url_or_id: str) -> str:
    """从分享链接或裸 ID 中提取 share_id。"""
    s = url_or_id.strip()
    m = re.search(r"share/([A-Za-z0-9_-]+)", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{6,64}", s):
        return s
    raise ValueError(
        f"无法从输入中识别 DeepSeek 分享 ID: {url_or_id!r}\n"
        "请输入形如 https://chat.deepseek.com/share/<id> 的链接或裸 ID。"
    )


def fetch_share(share_id: str, cookie: str = "") -> dict:
    """调用 DeepSeek 公开分享 API，返回 biz_data。"""
    headers = dict(HEADERS)
    if cookie:
        headers["Cookie"] = cookie
    url = f"{API_URL}?share_id={share_id}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"分享内容不存在或已被删除 (share_id={share_id})") from e
        raise RuntimeError(f"API 请求失败: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络请求失败: {e.reason}") from e

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError("API 响应不是合法 JSON") from e

    if payload.get("code") != 0:
        raise RuntimeError(f"API 返回错误: code={payload.get('code')} msg={payload.get('msg')}")
    data = payload.get("data") or {}
    if data.get("biz_code") != 0:
        raise RuntimeError(f"业务错误: biz_code={data.get('biz_code')} msg={data.get('biz_msg')}")
    return data.get("biz_data") or {}


def parse_messages(biz_data: dict) -> list:
    """兼容新旧两种消息结构，统一为内部格式:
    [{role, time, model, status, incomplete, text, thinking,
      files:[{name, size, signed_path, is_image, local_path}], search:{queries, results}}]
    """
    out = []
    for m in biz_data.get("messages") or []:
        item = {
            "role": (m.get("role") or "").upper(),
            "time": m.get("inserted_at"),
            "model": m.get("model") or "",
            "status": m.get("status") or "FINISHED",
            "incomplete": m.get("incomplete_message"),
            "text": "",
            "thinking": None,
            "files": [],
            "search": None,
        }

        fragments = m.get("fragments")
        if fragments:
            # 新版结构：fragments[]
            for frag in fragments:
                ftype = (frag.get("type") or "").upper()
                if ftype in ("REQUEST", "RESPONSE", "TEXT") and frag.get("content"):
                    item["text"] += ("\n\n" if item["text"] else "") + str(frag["content"])
                elif ftype == "THINKING" and frag.get("content"):
                    item["thinking"] = (item["thinking"] or "") + str(frag["content"])
                elif ftype == "FILE":
                    for f in frag.get("files") or []:
                        item["files"].append({
                            "name": f.get("file_name") or f.get("fileName") or "file",
                            "size": f.get("file_size"),
                            "signed_path": f.get("signed_path") or "",
                            "is_image": bool(f.get("is_image")),
                        })
                elif ftype == "SEARCH":
                    results = []
                    for r in frag.get("results") or []:
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "snippet": r.get("snippet", "") or r.get("content", ""),
                            "cite_index": r.get("cite_index"),
                        })
                    item["search"] = {"queries": frag.get("queries") or [], "results": results}
        else:
            # 老版结构：content + files + thinking_content + search_results
            item["text"] = parse_content(m.get("content"))
            item["thinking"] = parse_content(m.get("thinking_content")) or None
            for f in m.get("files") or []:
                item["files"].append({
                    "name": f.get("file_name") if isinstance(f, dict) else str(f),
                    "size": f.get("file_size") if isinstance(f, dict) else None,
                    "signed_path": "",
                    "is_image": bool(f.get("is_image")) if isinstance(f, dict) else False,
                })
            sr = m.get("search_results")
            if sr:
                results = sr if isinstance(sr, list) else [sr]
                item["search"] = {"queries": [], "results": [
                    {"title": r.get("title", "") if isinstance(r, dict) else str(r),
                     "url": r.get("url", "") if isinstance(r, dict) else "",
                     "snippet": r.get("snippet", "") if isinstance(r, dict) else "",
                     "cite_index": r.get("cite_index") if isinstance(r, dict) else None}
                    for r in results]}
        out.append(item)
    return out


def parse_content(content) -> str:
    """消息 content 可能是纯文本，也可能是多模态 JSON 字符串。"""
    if content is None:
        return ""
    if isinstance(content, str):
        stripped = content.strip()
        if stripped.startswith(("[", "{")):
            try:
                return _extract_text_from_parts(json.loads(stripped))
            except json.JSONDecodeError:
                pass
        return content
    if isinstance(content, (dict, list)):
        return _extract_text_from_parts(content)
    return str(content)


def _extract_text_from_parts(obj) -> str:
    """从多模态 content 结构中递归提取可读文本。"""
    parts = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            t = node.get("type")
            if t in ("text", "input_text", "output_text") and node.get("text"):
                parts.append(node["text"])
            elif t in ("image", "image_url") and node.get("image_url"):
                parts.append(f"[图片: {node['image_url']}]")
            elif t == "tool_use":
                parts.append(f"**工具调用: {node.get('name', '')}**\n```json\n"
                             f"{json.dumps(node.get('input', {}), ensure_ascii=False, indent=2)}\n```")
            elif t == "tool_result":
                parts.append(f"**工具结果**\n```\n{node.get('content', '')}\n```")
            else:
                for value in node.values():
                    if isinstance(value, (dict, list)):
                        walk(value)
                    elif isinstance(value, str) and value.strip():
                        parts.append(value)

    walk(obj)
    return "\n\n".join(p for p in parts if p.strip()) or str(obj)


def download_file(signed_path: str, fname: str) -> bytes:
    """按签名路径下载附件，返回原始字节（失败返回 b''）。"""
    if not signed_path:
        return b""
    url = signed_path if signed_path.startswith("http") else FILE_BASE + signed_path
    if "ty=" not in url:
        url += "&ty=r"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except Exception as e:
        print(f"⚠️ 附件下载失败 {fname}: {e}", file=sys.stderr)
        return b""


def save_file(data: bytes, dest_dir: str, fname: str) -> str:
    """保存附件字节到本地，返回相对所在目录上一级的路径（失败返回 ''）。"""
    try:
        os.makedirs(dest_dir, exist_ok=True)
        local = os.path.join(dest_dir, fname)
        with open(local, "wb") as f:
            f.write(data)
        return os.path.relpath(local, os.path.dirname(dest_dir))
    except OSError as e:
        print(f"⚠️ 附件保存失败 {fname}: {e}", file=sys.stderr)
        return ""


def is_binary(data: bytes) -> bool:
    """检测是否二进制内容（含 NUL 或大量不可解码字节）。"""
    if not data:
        return False
    if b"\x00" in data[:4096]:
        return True
    sample = data[:4096].decode("utf-8", errors="ignore")
    return len(sample) / max(len(data[:4096]), 1) < 0.9


def inline_file(data: bytes, fname: str) -> str:
    """文本内容转折叠代码块（UTF-8/Gbk 自动识别），二进制返回空串。"""
    if is_binary(data):
        return ""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("gbk")
        except UnicodeDecodeError:
            return ""
    ext = os.path.splitext(fname)[1].lower()
    lang = ext.lstrip(".") if ext else "text"
    block = [f"<details>", f"<summary>📄 {fname}（{len(data)} 字节）</summary>", "",
             f"```{lang}", text.rstrip(), "```", "", "</details>"]
    return "\n".join(block)


def format_search(frag: dict) -> str:
    """联网搜索片段 → Markdown 折叠引用块。"""
    results = frag.get("results") or []
    if not results:
        return ""
    block = ["<details>", "<summary>🔍 联网搜索来源</summary>", ""]
    for r in results:
        line = f"- **{r['title']}**"
        if r["url"]:
            line = f"- **[{r['title']}]({r['url']})**" if False else f"- **{r['title']}** — {r['url']}"
        block.append(line)
        if r["snippet"]:
            block.append(f"  > {r['snippet']}")
        block.append("")
    block.append("</details>")
    return "\n".join(block)


def format_message(item: dict, attach_dir: str, download: bool, inline: bool = True) -> str:
    """单条消息 → Markdown 段落。"""
    role = item["role"]
    heading = "## 👤 用户" if role == "USER" else ("## 🤖 DeepSeek" if role == "ASSISTANT" else f"## {role}")

    lines = [heading]

    meta = []
    if item["time"]:
        try:
            dt = datetime.datetime.fromtimestamp(float(item["time"])).strftime("%Y-%m-%d %H:%M:%S")
            meta.append(f"🕐 {dt}")
        except (ValueError, OSError):
            pass
    if item["model"]:
        meta.append(f"🧠 {item['model']}")
    if item["status"] != "FINISHED":
        meta.append(f"⚠️ 状态: {item['status']}")
    if meta:
        lines.append("> " + " ｜ ".join(meta))
        lines.append("")

    # 深度思考
    if item["thinking"]:
        lines.append("<details>")
        lines.append("<summary>💭 深度思考过程</summary>")
        lines.append("")
        lines.append("> " + "\n> ".join(item["thinking"].splitlines()))
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # 附件：保存到本地 + 内容直接内嵌 / 链接
    if item["files"]:
        for f in item["files"]:
            fname = f["name"]
            ext = os.path.splitext(fname)[1].lower()
            data = b""
            local = ""
            if download and f["signed_path"]:
                data = download_file(f["signed_path"], fname)
                if data:
                    local = save_file(data, attach_dir, fname)

            if data and inline and ext in IMAGE_EXTENSIONS:
                # 图片：本地保存 + 相对路径引用（md 与附件目录一起分发）
                lines.append(f"**附件: 📎 {fname}**")
                if local:
                    lines.append(f"![]({local})")
                lines.append("")
            elif data and inline and ext in TEXT_EXTENSIONS and len(data) <= INLINE_TEXT_MAX_BYTES:
                # 文本：内容直接内嵌 + 本地也保存一份（双保险，不依赖远程 URL）
                lines.append(f"**附件: 📎 {fname}**")
                inlined = inline_file(data, fname)
                if inlined:
                    lines.append(inlined)
                else:
                    lines.append("（内容无法内嵌，已保存至本地）")
                if local:
                    lines.append(f"📄 本地副本: [{fname}]({local})")
                lines.append("")
            else:
                # 二进制 / 超大文本 / 未下载：保存 + 链接（不依赖远程 URL）
                desc = f"**附件: 📎 {fname}**"
                if f["size"]:
                    desc += f"（{f['size']} 字节）"
                if local:
                    desc += f" — [本地文件]({local})"
                elif data:
                    desc += "（已下载）"
                lines.append(desc)
                if data and len(data) > INLINE_TEXT_MAX_BYTES and ext in TEXT_EXTENSIONS:
                    lines.append(f"> 提示: 文件超过 {INLINE_TEXT_MAX_BYTES // 1024}KB，内容未内嵌，已保存至本地。")
                lines.append("")

    # 正文
    if item["text"]:
        lines.append(item["text"])
        lines.append("")

    if item["incomplete"]:
        lines.append(f"> ⚠️ *消息被截断: {item['incomplete']}*")
        lines.append("")

    if item["search"]:
        s = format_search(item["search"])
        if s:
            lines.append(s)

    return "\n".join(lines)


def safe_filename(title: str, fallback: str) -> str:
    """清洗 Windows/Linux 均不适用的文件名字符。"""
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", title).strip(" .")
    return cleaned[:120] or fallback


def build_markdown(biz_data: dict, share_id: str, messages: list, frontmatter: bool = True) -> tuple[str, str]:
    """生成 Markdown 文档，返回 (md_text, suggested_filename)。"""
    title = (biz_data.get("title") or "").strip() or f"DeepSeek 分享对话 {share_id}"

    lines = []
    if frontmatter:
        lines.append("---")
        lines.append(f'title: "{html.escape(title, quote=True)}"')
        lines.append(f"source: https://chat.deepseek.com/share/{share_id}")
        lines.append(f"exported_at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"message_count: {len(messages)}")
        lines.append("---")
        lines.append("")

    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> 来源: [DeepSeek 分享链接](https://chat.deepseek.com/share/{share_id})")
    lines.append("")

    for item in messages:
        lines.append(format_message(item, "", download=False))
        lines.append("")

    return "\n".join(lines), safe_filename(title, f"deepseek-{share_id}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="DeepSeek 分享会话 → Markdown（stdout 或文件+附件）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n  python3 deepseek_share_to_md.py https://chat.deepseek.com/share/95z1fr6y7rj4q5nmd0\n"
               "  python3 deepseek_share_to_md.py 95z1fr6y7rj4q5nmd0 -o chat.md\n"
               "  python3 deepseek_share_to_md.py <url> --dir ./exports",
    )
    parser.add_argument("share", help="DeepSeek 分享链接 (chat.deepseek.com/share/<id>) 或裸 share_id")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", "--output", help="输出文件路径（场景2：用户导出）")
    group.add_argument("--dir", default=None, help="输出目录，按标题自动命名写文件")
    parser.add_argument("--no-frontmatter", action="store_true", help="不输出 YAML frontmatter")
    parser.add_argument("--raw-json", action="store_true", help="输出原始 API JSON 到 stdout")
    parser.add_argument("--no-download", action="store_true", help="导出文件时跳过附件下载")
    parser.add_argument("--no-inline", action="store_true", help="附件内容不内嵌到 md（仅保存本地 + 链接）")
    parser.add_argument("--cookie", default="", help="可选：WAF 会话 cookie（默认无需，失败时再提供）")
    args = parser.parse_args(argv)

    try:
        share_id = extract_share_id(args.share)
        print(f"⏳ 正在获取分享内容: {share_id} ...", file=sys.stderr)
        biz_data = fetch_share(share_id, args.cookie)
        messages = parse_messages(biz_data)

        if args.raw_json:
            print(json.dumps(biz_data, ensure_ascii=False, indent=2))
            return 0

        if args.output or args.dir:
            # 场景2：用户导出为文件（含附件）
            if args.output:
                out_path = args.output
                base_dir = os.path.dirname(os.path.abspath(out_path))
            else:
                default_name = build_markdown(biz_data, share_id, messages, False)[1]
                out_path = f"{args.dir.rstrip('/')}/{default_name}.md"
                base_dir = os.path.abspath(args.dir)

            attach_dir = os.path.join(base_dir, "attachments")
            lines = ["---",
                     f'title: "{html.escape((biz_data.get("title") or "").strip(), quote=True)}"',
                     f"source: https://chat.deepseek.com/share/{share_id}",
                     f"exported_at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                     f"message_count: {len(messages)}",
                     "---", ""]
            title = (biz_data.get("title") or "").strip() or f"DeepSeek 分享对话 {share_id}"
            lines += [f"# {title}", "", f"> 来源: [DeepSeek 分享链接](https://chat.deepseek.com/share/{share_id})", ""]
            for item in messages:
                lines.append(format_message(item, attach_dir, download=not args.no_download, inline=not args.no_inline))
                lines.append("")
            md = "\n".join(lines)

            os.makedirs(base_dir, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)
            n_files = sum(len(m["files"]) for m in messages)
            if n_files and not args.no_download:
                mode = "+内容内嵌" if not args.no_inline else ""
                print(f"✅ 已导出 {len(messages)} 条消息、{n_files} 个附件{mode} → {out_path}（附件目录: {attach_dir}）", file=sys.stderr)
            else:
                print(f"✅ 已导出 {len(messages)} 条消息 → {out_path}", file=sys.stderr)
            return 0

        # 场景1：AI 读取，全文输出到 stdout
        md, _ = build_markdown(biz_data, share_id, messages, frontmatter=not args.no_frontmatter)
        sys.stdout.write(md)
        if not md.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    except (ValueError, RuntimeError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"❌ 写入失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())