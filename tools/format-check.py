#!/usr/bin/env python3
r"""develop 代码格式与规范泄漏自检（A 层，2026-09-02）。

env 决策（卸载 google-java-format / 停用 pi-lens Java formatter）后，
人工自检升级为脚本辅助自检。纯 python3、无 JDK/Maven 依赖（绕开编译
环境阻断），检查 ai-system 已立规范的可机械判定项。

检查项（FAIL=必须修复，WARN=建议人工核验）：
1. 单行 Javadoc（`/** xxx */`）→ FAIL（documentation.md → Javadoc Format）
2. 中文/Unicode 方法名 → FAIL（testing.md → Naming / documentation.md → Identifiers）
3. 注释内任务编号泄漏（`（T-001）` / T-00x 出现在注释行）→ FAIL（Comment Content）
4. `Map<String, Object>` + `.put("` 手工组装（疑似消息体 payload）→ WARN
   （rocketmq-conventions §4.1，启发式：方法内 Map 后连续 put）
5. 4 空格缩进比例偏低（启发式，阈值宽容）→ WARN
6. `--check-commit`：最近提交 subject 含任务编号时必须为 `<type>(<scope>): T-\d{3}`
   格式，否则 FAIL（Commit Content → governance/standards/common/commit-content.md）

用法：
    python3 tools/format-check.py <src-dir> [--check-commit]
    python3 tools/format-check.py . --check-commit   # 含最近提交 subject 检查
exit code: 0=PASS  1=WARN  2=FAIL
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
ONE_LINE_JAVADOC = re.compile(r"/\*\*[^*]*\*/")          # 同行闭合的单行 Javadoc 块
METHOD_SIG = re.compile(
    r"(?:public|protected|private)\s+[\w<>\[\],\s]+\s+([^\s(]+)\s*\("  # 方法名 token
)
TASK_REF = re.compile(r"T-\d{3}")                              # T-001 等
BRACELESS_CTRL = re.compile(
    r"^\s*(?:(?:if|for|while)\s*\([^)]*\)|else)\s*(?!\{|if\b|$)[^{;]*;"
)
VALUE_ANNOT = re.compile(r'@Value\("\$\{([^"{}:]+)(?::([^"}]*))?\}"\)')
VALUE_FIELD_INIT = re.compile(r'(?:private|public|protected)\s+[^;=]+\s*=\s*[^;]+;')
VALUE_FIELD_DECL = re.compile(r'(?:private|public|protected)\s+[^;]+;')
MAP_DECL = re.compile(r"Map<String,\s*Object>\s+\w+\s*=\s*new\s+HashMap<>\(\)")
PUT_REF = re.compile(r'\.put\("')
COMMIT_TASK_PREFIX = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)\([^)]*\):\s*T-\d{3}")
# 第 7 项：方法显式访问修饰符检查的辅助正则
#   1) 顶层类型声明（见 check_file：仅在 depth==0 时识别，支持 public/abstract/final 前缀；
#      不要求同行 `{`——兼容跨行声明（`public class X\n implements Y {`）
TYPE_DECL_RE = re.compile(
    r"^(?:(?:public|protected|private)\s+)?(?:(?:abstract|final)\s+)?(class|interface|enum|@interface)\b(?:\s.*)?$"
)
#   2) 无访问修饰词的方法声明行：行首非修饰词/注解/控制流/`(`/`=` 等，
#      且形如「<返回类型> <方法名>(…​…) {」——类型段不含 `=`（排除赋值行/字段），
#      名字后紧跟 `(`（排除构造器/单 token 调用/`x.y(`）。
METHOD_NO_MOD_RE = re.compile(
    r"^(?!(?:public|protected|private|static|final|abstract|synchronized|native|default)\s+"
    r"|@|return\b|if\b|for\b|while\b|switch\b|catch\b|throw\b|new\b|break\b|continue\b|else\b|try\b"
    r"|[({})=;?:,])"
    r"(?P<ret>\S[\w<>\[\], .]*?)\s+(?P<name>\w+)\s*\([^;{]*\)[^{;]*(?:\{\s*)?(?://.*)?$"
)
# 生产日志消息：error/warn 必须英文（documentation.md → Log Content）；info 提示
# log.error( "中文" ) / log.warn( "中文" )
LOG_CJK_ERROR = re.compile(r"log\.(error|warn)\(\s*\"[^\"]*[\u4e00-\u9fff]")
LOG_CJK_INFO = re.compile(r"log\.(info|debug)\(\s*\"[^\"]*[\u4e00-\u9fff]")

# 第 10-12 项（java-alibaba.md §String / §Log / §Exception）
STR_EQ_LITERAL = re.compile(r'["\'][\w\s.?!:;+=/\\-]+["\']\s*(?:==|!=)\s*["\']|(?:==|!=)\s*["\'][^"\'\n]*["\']')
LOG_FORBIDDEN = re.compile(r'\.printStackTrace\(\)|System\.out\.println\(')
THROWS_EXCEPTION = re.compile(r'\bthrows\s+Exception\b')

# 第 13-15 项（java-alibaba.md §Optional / §Date / §Thread）
OPTIONAL_FIELD = re.compile(r'(?:private|public|protected|static|final|\s)+Optional<[^>]+>\s+\w+\s*[;=]')
OPTIONAL_PARAM = re.compile(r'\([^)]*\bOptional<[^>]+>\s+\w+')
LEGACY_DATE = re.compile(r'java\.util\.Date|java\.util\.Calendar|(?<![A-Za-z])Calendar\b|new\s+Date\s*\(|SimpleDateFormat|(?<![A-Za-z])Date\b')
NEW_THREAD = re.compile(r'new\s+Thread\s*\(')

# 第 16-17 项（java-alibaba.md §Config / §Collection）
HARDCODE_URL = re.compile(r'(?:=\s*|return\s+|\bput\s*\(|\bset[A-Z]\w*\s*\(\s*"[^"]*"?\s*,\s*)"https?://[^"]*"')
HARDCODE_SECRET = re.compile(r'(?:=\s*|return\s+|\bput\s*\(|\bset[A-Z]\w*\s*\(\s*"[^"]*"?\s*,\s*)"(?=[^"]*?(?:token|secret|password|api[_-]?key|access[_-]?key))[^"$<]{4,}"')
COLL_METHOD_RE = re.compile(r'^\s*(?:public|protected|private|static|final|default|synchronized|\s)+'
                            r'(?:(?:List|Map|Set|Collection|Queue|Deque|Iterable|Stream)\b[^;(]*)\([^)]*\)\s*\{')

# 第 18-19 项（魔法值：裸字符串比较/switch、大数字字面量）
MAGIC_STR_RE = re.compile(r'\.equals\s*\(\s*"[A-Za-z_][A-Za-z0-9_]{2,}"'
                          r'|\bswitch\s*\(\s*[^)]*\s*\)\s*\{\s*case\s*"[A-Za-z_][A-Za-z0-9_]{2,}"')
MAGIC_NUM_RE = re.compile(r'(?<![\w.])([1-9][0-9]{3,})(?![\w.])')

# 第 20-21 项（java-alibaba.md §Lombok / §MQ）
LOMBOK_ANNOT_RE = re.compile(r'^\s*@(Data|Getter|Setter|Builder|Value|NoArgsConstructor|RequiredArgsConstructor)\b')
MANUAL_GETTER_RE = re.compile(r'^\s*public\s+[\w<>\[\],. ]+\s+(get[A-Z]\w*)\s*\(\s*\)\s*\{\s*return\s+\w+\s*;')
MANUAL_SETTER_RE = re.compile(r'^\s*public\s+void\s+(set[A-Z]\w*)\s*\(([^)]*)\)\s*\{\s*this\.\w+\s*=\s*\w+\s*;')
JSONOBJECT_NEW_RE = re.compile(r'\bnew\s+JSONObject\s*\(')
NESTED_STREAM_RE = re.compile(r'\.stream\(\)')


def _is_comment_line(line: str) -> bool:
    s = line.strip()
    return s.startswith(("//", "/*", "*", "/**", "*/"))


def check_file(path: Path, findings):
    """对单个 .java 文件执行可机械判定的检查，结果并入 findings。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()

    # 1. 单行 Javadoc
    for i, ln in enumerate(lines, 1):
        if ONE_LINE_JAVADOC.search(ln):
            findings.append(("FAIL", f"单行 Javadoc（应多行块，documentation.md）: {path}:{i}"))

    # 2. 中文/Unicode 方法名
    for i, ln in enumerate(lines, 1):
        m = METHOD_SIG.search(ln)
        if m and CJK.search(m.group(1)):
            findings.append(("FAIL", f"中文方法名「{m.group(1)}」（testing.md Naming）: {path}:{i}"))

    # 3. 注释内任务编号泄漏
    for i, ln in enumerate(lines, 1):
        if TASK_REF.search(ln) and (_is_comment_line(ln) or "（T-" in ln):
            findings.append(("FAIL", f"注释内任务编号泄漏（Comment Content）: {path}:{i}"))

    # 4. Map 手工组装 payload（启发式 WARN：仅 main 代码——test 中 Map 常为参数构造合法；
    #    Map<String,Object> 声明后 20 行内 ≥2 次 put 提示消息体场景）
    _is_main = "/test/" not in str(path).replace("\\", "/")
    if _is_main:
        for m in MAP_DECL.finditer(src):
            tail = src[m.end():m.end() + 1200]
            if len(PUT_REF.findall(tail)) >= 2:
                line_no = src[:m.start()].count("\n") + 1
                findings.append(("WARN", f"Map 手工组装 payload（§4.1 建议强类型对象）: {path}:{line_no}"))

    # 5. 4 空格缩进比例（启发式：忽略空行/注释行/制表符行）
    non_meet = total = 0
    for ln in lines:
        if not ln.strip() or _is_comment_line(ln) or ln.startswith("\t"):
            continue
        lead = len(ln) - len(ln.lstrip(" "))
        if lead % 4 != 0:
            non_meet += 1
        total += 1
    if total and non_meet / total > 0.15:
        findings.append(("WARN", f"缩进非 4 空格比例 {non_meet}/{total}（启发式，建议人工核验）: {path}"))

    # 6. 生产日志消息语言（error/warn 英文强制；info 提示）
    for i, ln in enumerate(lines, 1):
        if LOG_CJK_ERROR.search(ln):
            findings.append(("FAIL", f"日志消息含中文（error/warn 须英文，Log Content）: {path}:{i}"))
        elif LOG_CJK_INFO.search(ln):
            findings.append(("WARN", f"日志消息含中文（新写代码 info 建议英文）: {path}:{i}"))

    # 7. 方法显式访问修饰符（java-alibaba.md §Visibility；启发式 WARN，仅 main 代码——
    #    JUnit 测试方法有 package-private 存量习惯，另行规范）
    #    类/枚举体内方法声明必须带 public/protected/private；接口体（隐式 public）与
    #    构造器/字段/表达式不检查。误报宁可漏：行级启发 + 注释/含=行排除。
    if _is_main:
        depth = 0
        type_stack = []  # 顶层类型声明栈（'class'/'interface'/'enum'）
        pushed_now = False
        for i, ln in enumerate(lines, 1):
            s = ln.strip()
            if not s or _is_comment_line(s):
                continue
            if depth == 0:
                dt = TYPE_DECL_RE.match(s)
                if dt:
                    type_stack.append(dt.group(1))
                    pushed_now = True  # 跨行声明（本行无 `{`）不得在本行被 depth 归零弹栈
            if type_stack and type_stack[-1] not in ("interface", "@interface"):
                mm = METHOD_NO_MOD_RE.match(s)
                if mm:
                    # §Visibility 例外：同包测试直接调用的 helper 在 Javadoc 首行注明
                    # 「供同包测试直接调用」→ 豁免（合规通道，与规范一致）
                    # 索引注意：i 为 1-based 行号，lines 为 0-based；窗口 26 行覆盖
                    # 多行 Javadoc（含 @param）与上方注释块
                    exempted = any(
                        "供同包测试直接调用" in lines[j]
                        for j in range(max(0, i - 26), i - 1)
                    )
                    if not exempted:
                        findings.append(
                            ("WARN",
                             f"方法「{mm.group(2)}」缺少显式访问修饰符（§Visibility：默认 private，"
                             f"接口实现 public；同包测试直调须 Javadoc 注明）: {path}:{i}"))
            depth += s.count("{") - s.count("}")
            if depth <= 0 and not pushed_now:
                depth = 0
                if type_stack:
                    type_stack.pop()
            pushed_now = False

    # 8. @Value 配置字段（spring.md §Configuration Injection，启发式 WARN）：
    #    a) 双默认——占位符已带默认值仍给字段初始化（漂移源）
    #    b) 缺注释——@Value 字段无行尾注释（用途/默认/单位）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        m = VALUE_ANNOT.search(s)
        if not m:
            continue
        field_j = None
        for j in range(i, min(i + 3, len(lines) + 1)):
            fl = lines[j - 1].strip() if j - 1 < len(lines) else ""
            if not fl:
                continue
            if VALUE_FIELD_DECL.search(fl):
                field_j = (j, fl)
                break
            if not fl.startswith(("@", "private", "public", "protected")):
                break
        if field_j is None:
            continue
        j, fl = field_j
        ctx = " ".join(lines[max(0, i - 4):j])
        dual_exempt = ("测试直构" in ctx) or ("兜底" in ctx)
        if VALUE_FIELD_INIT.search(fl) and not dual_exempt:
            findings.append(
                ("WARN",
                 f"@Value 已带默认值仍字段初始化（spring.md：占位符为唯一默认源，"
                 f"测试直构默认移测试侧）: {path}:{j}"))
        if ("//" not in lines[j - 1]) and ("/**" not in ctx) and ("/*" not in ctx):
            findings.append(
                ("WARN",
                 f"@Value 配置字段缺少注释说明（spring.md：用途/默认/单位）: {path}:{j}"))

    # 9. 单行无大括号控制语句（java-alibaba.md §Braces，启发式 WARN）：
    #    if/else/for/while 单语句必须带大括号（含 lambda 内）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if BRACELESS_CTRL.search(s) and not s.rstrip().endswith("{") and not _is_comment_line(s):
            findings.append(
                ("WARN",
                 f"单行控制语句无大括号（§Braces：if/else/for/while 必须带 {{}}，含 lambda 内）: {path}:{i}"))

    # 10. 字符串字面量 == / != 比较（java-alibaba.md §String：Forbidden ==，须 Objects.equals）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if STR_EQ_LITERAL.search(s) and not _is_comment_line(s):
            findings.append(
                ("WARN",
                 f"字符串 == / != 字面量比较（§String：用 Objects.equals/StringUtils.equals）: {path}:{i}"))

    # 11. 生产日志禁用写法（java-alibaba.md §Log：SLF4J，禁止 printStackTrace/System.out.println，仅 main）
    if _is_main:
        for i, ln in enumerate(lines, 1):
            if LOG_FORBIDDEN.search(ln) and not _is_comment_line(ln):
                findings.append(
                    ("WARN",
                     f"生产日志禁用（§Log：SLF4J；禁 printStackTrace/System.out.println）: {path}:{i}"))

    # 12. throws Exception（java-alibaba.md §Exception：须业务异常）
    for i, ln in enumerate(lines, 1):
        if THROWS_EXCEPTION.search(ln) and not _is_comment_line(ln):
            findings.append(
                ("WARN",
                 f"throws Exception（§Exception：须使用业务异常）: {path}:{i}"))

    # 13. Optional 字段/参数（java-alibaba.md §Optional：禁字段/参数，仅返回值）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if OPTIONAL_FIELD.search(s):
            findings.append(("WARN", f"Optional 作为字段（§Optional：仅用于返回值）: {path}:{i}"))
        if OPTIONAL_PARAM.search(s):
            findings.append(("WARN", f"Optional 作为方法参数（§Optional：仅用于返回值）: {path}:{i}"))

    # 14. 遗留日期 API（java-alibaba.md §Date：统一 java.time，禁 Date/Calendar/SimpleDateFormat）
    for i, ln in enumerate(lines, 1):
        if LEGACY_DATE.search(ln) and not _is_comment_line(ln):
            findings.append(("WARN", f"遗留日期 API（§Date：统一 java.time；禁 Date/Calendar/SimpleDateFormat）: {path}:{i}"))

    # 15. new Thread()（java-alibaba.md §Thread：须用线程池）
    for i, ln in enumerate(lines, 1):
        if NEW_THREAD.search(ln) and not _is_comment_line(ln):
            findings.append(("WARN", f"new Thread()（§Thread：须使用线程池）: {path}:{i}"))

    # 16. 硬编码 URL/Secret（java-alibaba.md §Config：禁硬编码，须外部化）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if HARDCODE_URL.search(s):
            findings.append(("WARN", f"硬编码 URL（§Config：须外部化到配置）: {path}:{i}"))
        elif HARDCODE_SECRET.search(s):
            findings.append(("WARN", f"硬编码密钥（§Config：Token/Secret 须外部化）: {path}:{i}"))

    # 17. 集合方法返回 null（java-alibaba.md §Collection：返回空集合，禁 null）
    depth = 0
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if depth == 0 and COLL_METHOD_RE.match(s):
            depth = 1
            continue
        if depth > 0:
            if re.search(r'\breturn\s+null\s*;', s):
                findings.append(("WARN", f"集合方法返回 null（§Collection：返回空集合）: {path}:{i}"))
            depth += s.count('{') - s.count('}')
            if depth <= 0:
                depth = 0

    # 18. 魔法字符串（java-alibaba.md §String 延伸：裸字符串 equals/switch-case，须提命名常量）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if MAGIC_STR_RE.search(s):
            findings.append(("WARN", f"魔法字符串（裸字符串 equals/switch-case，建议提命名常量）: {path}:{i}"))

    # 19. 魔法数字（4+ 位裸数字字面量；常量声明/@Value/注解行排除）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s) or re.match(r'(?:private|public|protected|static|final|@Value|@[A-Za-z]+)', s):
            continue
        m = MAGIC_NUM_RE.search(s)
        if m:
            findings.append(("WARN", f"魔法数字 {m.group(1)}（建议提命名常量）: {path}:{i}"))

    # 20. Lombok 无意义 getter/setter（java-alibaba.md §Lombok：Prefer @Data；禁无意义手动 getter/setter）
    lombok_on = False
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if s.startswith('}'):
            lombok_on = False
        elif LOMBOK_ANNOT_RE.match(s):
            lombok_on = True
        elif not lombok_on:
            m = MANUAL_GETTER_RE.match(s)
            if m:
                findings.append(("WARN", f"无意义 getter {m.group(1)}（§Lombok：用 @Data/@Getter 或省略）: {path}:{i}"))
            m2 = MANUAL_SETTER_RE.match(s)
            if m2:
                findings.append(("WARN", f"无意义 setter {m2.group(1)}（§Lombok：用 @Data/@Setter 或省略）: {path}:{i}"))

    # 21. JSONObject 组装（java-alibaba.md §MQ：Typed VOs；禁 JSONObject 组装消息）
    for i, ln in enumerate(lines, 1):
        if JSONOBJECT_NEW_RE.search(ln) and not _is_comment_line(ln):
            findings.append(("WARN", f"JSONObject 组装（§MQ：组装消息须 Typed VO；HTTP 组装可忽略）: {path}:{i}"))

    # 22. 复杂嵌套 Stream（java-alibaba.md §Stream：Use judiciously；禁复杂嵌套流）
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if _is_comment_line(s):
            continue
        if len(NESTED_STREAM_RE.findall(s)) >= 2:
            findings.append(("WARN", f"嵌套 Stream（§Stream：禁复杂嵌套流，拆步骤/中间集合）: {path}:{i}"))


def _changed_java_files(src_dir):
    """git status 驱动的本 change 改动 .java 文件（develop 完成时语义）。

    非 git 仓 / git 不可用 → None（调用方回退全量）。
    """
    try:
        top = subprocess.check_output(
            ["git", "-C", str(src_dir), "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
        out = subprocess.check_output(
            ["git", "-C", top, "status", "--porcelain"], text=True
        )
        base = Path(src_dir).resolve()
        top = Path(top).resolve()
        res = []
        for ln in out.splitlines():
            if not ln.strip():
                continue
            path = ln[3:].strip().strip('"')
            p = (top / path).resolve()
            if p.suffix == ".java" and p.exists() and base in p.parents:
                res.append(p)
        return res
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="develop 格式与规范泄漏自检（A 层）")
    ap.add_argument("src_dir", nargs="?", default=".", help="Java 源目录（默认 .）")
    ap.add_argument("--changed", action="store_true",
                    help="仅查本 change（git status）改动的 .java，排除存量债噪音")
    ap.add_argument("--check-commit", action="store_true", help="额外检查最近提交 subject")
    args = ap.parse_args(argv)

    root = Path(args.src_dir)
    if not root.is_dir():
        print(f"format-check: ERROR — 源目录不存在: {root}", file=sys.stderr)
        return 2

    files = None
    if args.changed:
        files = _changed_java_files(root)
        if files is None:
            print("format-check: WARN — 非 git 仓，回退全量扫描", file=sys.stderr)
        elif not files:
            print("format-check: PASS（本 change 无改动 .java 文件）")
            return 0

    findings = []
    if files is not None:
        for p in sorted(files):
            check_file(p, findings)
    else:
        for p in sorted(root.rglob("*.java")):
            check_file(p, findings)

    if args.check_commit:
        try:
            subj = subprocess.check_output(
                ["git", "log", "-1", "--format=%s"], text=True, cwd=str(root)
            ).strip()
            if "T-" in subj and not COMMIT_TASK_PREFIX.match(subj):
                findings.append(("FAIL",
                                 f"最近提交 subject 含任务编号但不符合 type(scope): T-xxx 格式"
                                 f"（commit-content.md）: {subj}"))
        except Exception:
            pass  # 非 git 目录或 git 不可用：跳过

    if not findings:
        print("format-check: PASS（无格式/规范泄漏）")
        return 0

    has_fail = any(s == "FAIL" for s, _ in findings)
    has_warn = any(s == "WARN" for s, _ in findings)
    for sev, msg in findings:
        print(f"[{sev}] {msg}")
    print(f"format-check: {'FAIL' if has_fail else 'WARN' if has_warn else 'PASS'} "
          f"（FAIL={sum(1 for s,_ in findings if s=='FAIL')} "
          f"WARN={sum(1 for s,_ in findings if s=='WARN')}）")
    return 2 if has_fail else (1 if has_warn else 0)


if __name__ == "__main__":
    sys.exit(main())