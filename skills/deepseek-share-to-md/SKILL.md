---
name: deepseek-share-to-md
description: >
  将 DeepSeek 分享会话链接（chat.deepseek.com/share/<id>）导出为结构化的 Markdown 文档。
  直接调用 DeepSeek 公开分享 API（GET /api/v0/share/content），无需登录、
  无需浏览器渲染、零第三方依赖（纯 Python 3 标准库）。
  完整保留对话标题、角色（用户/DeepSeek）、消息时间、深度思考过程（折叠块）、
  联网搜索来源引用与截断提示；附件自动下载保存到本地，文本内容直接内嵌进 md
  （不依赖远程 URL），图片以相对路径引用。
  两种场景：AI 读取（stdout 全文输出）与用户导出（md 文件 + 附件目录）。
  触发词：deepseek 分享转 md、导出 deepseek 对话、分享链接转 markdown、存档 AI 对话。
  不处理：ChatGPT / Claude / Gemini / 豆包等平台的分享链接；需要登录的私有会话
  （chat.deepseek.com/chat/... 无分享 ID 的场景）。
---

# DeepSeek Share → Markdown

将 DeepSeek 的分享会话页面（`https://chat.deepseek.com/share/<id>`）转换为 Markdown 文档。

## 原理

分享链接是**公开**页面，无需登录。前端通过公开 API `GET /api/v0/share/content?share_id=<id>`
取回完整会话 JSON。请求头（`x-client-bundle-id: com.deepseek.chat` + `x-client-version: 2.3.0`）
决定响应结构：新版响应中消息体为 `fragments[]`（REQUEST / RESPONSE / FILE / SEARCH / TIP
五类片段），**文件片段内嵌 `signed_path` 签名路径**，拼上 `https://files.deepseeksvc.com/api`
即可直接下载附件（签名 URL 公开可访问、无需登录）。

## 用法

```bash
python3 scripts/deepseek_share_to_md.py <分享链接或 share_id> [选项]
```

| 选项 | 说明 |
|---|---|
| （无） | 场景1：Markdown 全文输出到 stdout（AI 直接消费） |
| `-o <path>` | 场景2：写入指定文件，附件下载到文件旁的 `attachments/` |
| `--dir <目录>` | 场景2：写入目录，按标题自动命名，附件下载到 `<目录>/attachments/` |
| `--no-inline` | 附件内容不内嵌进 md（仅保存本地 + 链接） |
| `--no-download` | 跳过附件下载（只导出对话文本） |
| `--no-frontmatter` | 不输出 YAML frontmatter |
| `--raw-json` | 输出原始 API JSON 到 stdout（调试 / 高级场景） |
| `--cookie` | 可选 WAF 会话 cookie（默认无需，被风控时才提供） |

命令示例：

```bash
python3 scripts/deepseek_share_to_md.py https://chat.deepseek.com/share/95z1fr6y7rj4q5nmd0      # AI 读取
python3 scripts/deepseek_share_to_md.py 95z1fr6y7rj4q5nmd0 -o 对话存档.md                    # 用户导出
python3 scripts/deepseek_share_to_md.py <链接> --dir ./exports                               # 目录导出
python3 scripts/deepseek_share_to_md.py <链接> -o out.md --no-inline                          # 只要链接不要内嵌
```

输出文件名缺省时取自会话标题（自动清洗非法字符）；无标题时回退为 `deepseek-<share_id>.md`。

## 工作流

### Stage 1: 解析输入

1. 从用户输入中提取 share_id（支持完整 URL、`share/<id>` 片段、裸 ID）。
2. 输入既非 URL 也非合法 ID → 提示用户提供正确格式，终止。

**分支:** 用户给的是 `chat.deepseek.com/chat/...` 私有链接 → 告知此 Skill 仅支持
分享链接（`/share/`），无法导出登录态会话，终止。

### Stage 2: 抓取分享数据

1. 调用 API `GET https://chat.deepseek.com/api/v0/share/content?share_id=<id>`，
   携带 `x-client-*` 系列请求头（`com.deepseek.chat` / `2.3.0`，触发新版 fragments 结构）。
2. 校验响应：HTTP 非 2xx / `code != 0` / `biz_code != 0` → 报具体错误并终止。

**失败分支:**
- HTTP 404 → 分享不存在或已删除
- 网络错误 → 检查网络后重试
- 被 WAF 风控 → 从浏览器复制 Cookie 传入 `--cookie` 重试

### Stage 3: 生成 Markdown

逐消息转换，规则：

| 源结构 | Markdown 输出 |
|---|---|
| `title` | `# 标题` + frontmatter（title/source/exported_at/message_count） |
| 消息 `role` | `## 👤 用户` / `## 🤖 DeepSeek` |
| `inserted_at` | 元信息行 `🕐 2026-08-19 20:27:22`（本地时区） |
| `model` / `status` | 元信息行 🧠 / ⚠️；`incomplete_message` 转截断提示 |
| REQUEST / RESPONSE 片段 | 正文原样保留（本身即 Markdown） |
| 深度思考片段 | `<details><summary>💭 深度思考过程</summary>` 折叠引用块 |
| FILE 片段（附件） | 见下方《附件处理》 |
| SEARCH 片段 | `<details><summary>🔍 联网搜索来源</summary>` 编号引用列表（标题/URL/摘要） |

**附件处理（FILE 片段，每次下载）:**
1. 用 `https://files.deepseeksvc.com/api + signed_path` 下载原始字节
   （非图片且 URL 无 `ty` 参数时补 `&ty=r`）。
2. 保存到 `attachments/` 目录（与 md 同级），文件名取原文文件名。
3. 按类型嵌入 md：
   - **文本文件**（.txt/.log/.md/.json/.csv/.yaml 等，≤200KB）：内容直接内嵌为
     折叠代码块 `<details><summary>📄 文件名</summary>```<lang>...```</details>`，
     并附本地副本链接 —— md 自包含，不依赖远程 URL。
   - **图片**（.png/.jpg/.webp 等）：保存本地，md 用相对路径 `![](attachments/xx.png)` 引用。
   - **二进制 / 超大文本**：保存本地 + 本地路径链接；超大文本附提示说明未内嵌。
4. 内嵌用 UTF-8 解码（失败回退 GBK），二进制内容跳过内嵌。

### Stage 4: 写出文件 / 输出

1. 场景2：写出 md + 附件目录，打印结果摘要（消息数、附件数、路径）。
2. 场景1：全文写 stdout（进度/错误信息走 stderr，不污染输出）。
3. 写失败 → 报错退出码 1。

**出口条件:** 文件写入成功并校验非空。

## 校验清单

- [ ] frontmatter 包含 title / source / exported_at / message_count
- [ ] 每条消息有角色标题，REQUEST/RESPONSE 顺序与原文一致
- [ ] 思考过程位于折叠块内不打断正文阅读
- [ ] 消息正文的代码块、表格、引用未被破坏
- [ ] 搜索来源引用完整保留
- [ ] 附件已保存到本地，文本内容已内嵌（或按策略存为链接）
- [ ] md 中不含依赖 DeepSeek 远程 URL 的图片/文件引用（本地路径或内嵌）
- [ ] 文件编码为 UTF-8，标题无非法文件名字符

## 反模式

- ❌ 不抓取结果自动交给 LLM 总结/重写 —— 本 Skill 只做**保真转换**
- ❌ 不修改消息正文内容（含错误拼写、格式瑕疵）
- ❌ 不尝试登录或携带 Cookie 导私有会话（超出 `/share/` 公开范围）
- ❌ 不为其他平台（ChatGPT/Claude/Gemini）的分享链接兜底
- ❌ 不硬编码输出路径 —— 始终由参数或用户目录决定
- ❌ 不在 md 中嵌入附件远程 URL —— 附件必须落地到本地（内嵌或本地链接）

## 维护备注

- 若 DeepSeek 前端改版导致 API 失效：重新抓取
  `https://fe-static.deepseek.com/chat/static/main.<hash>.js`，
  用 `grep -oE '"/api/v0/[a-z_/]*share[a-z_/]*"'` 定位新的分享接口路径。
- 响应结构版本由 `x-client-bundle-id` + `x-client-version` 决定：`com.deepseek.chat`
  + `2.3.0` 返回新版 fragments（含 signed_path）；`chat-web-prod` + `1.0.0` 返回
  老版结构（messages[].content + files 元信息）。脚本同时兼容两种结构。
- 文件服务器域名默认 `files.deepseeksvc.com`（开发/测试环境为
  files-dev / files-test 子域），签名路径为相对路径，拼域名前缀后下载。