#!/usr/bin/env python3
r"""C2 eclipse JDT formatter 干跑门禁（机器环境感知版，2026-09-02）。

对指定 Java 源目录执行 eclipse JDT formatter 干跑（不写盘），校验代码是否
与 eclipse-format.xml profile（tab=4 space）一致。与 IDEA 默认 Java 格式化
同源（eclipse jdt 风格族），不改业务仓。

环境策略（按用户需求）：
- JDK 可用性：**自动探测**（JAVA_HOME → ~/.jdks/* → PATH → /usr/lib/jvm/*），
  也接受 `--java <path>` **用户提供**；
- 组件（jdt.core + org.eclipse.text jar、wrapper 编译产物）缺时：
  **交互授权** = [S]etup（下载 jar + javac 编译）/ [p]rovide（提供 jar/javac 路径）
  / [s]kip（跳过本次）/ [a]bort；
- 无 TTY / `--batch`：无法交互 → 跳过仅凭 `--skip` 显式声明，否则 exit 3；
- 配置持久化到机器级 `~/.config/ai-system/env.yaml`（runtime.jdt.*，本工具即 consumer）：
  java / jdt-jar / text-jar / build-dir；首次配置后无需再探测。

退出码：0=PASS（全部一致） 1=WARN（差异 ≤5 文件） 2=FAIL（差异 >5 文件）
        3=ENV 不可用（且未显式跳过）
"""
import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HOME = Path.home()
ENV_YAML = HOME / ".config" / "ai-system" / "env.yaml"
LIB_DIR = HOME / ".local" / "lib" / "jdt-gate"
JDT_CORE_VERSION = "3.13.0"          # JDK8 可运行的 jdt.core（eclipse 2017 系）
TEXT_JAR_VERSION = "3.8.0"           # org.eclipse.text（配套）
MAVEN = "https://repo1.maven.org/maven2"
AI_ROOT = Path(__file__).resolve().parent.parent
XML_DEFAULT = AI_ROOT / "tools" / "jdt-format-gate" / "eclipse-format.xml"
WRAPPER_SRC = AI_ROOT / "tools" / "jdt-format-gate" / "JdtFormatCheck.java"
DIFF_WARN_MAX_FILES = 5

# JDK8 可运行的 eclipse 2017 系运行闭包（实测验证：jdt.core 3.13 需 core.resources/
# core.runtime/osgi 等；classpath 按目录通配 LIB_DIR/* 装载）
JDT_JARS = [
    ("org/eclipse/jdt/org.eclipse.jdt.core/3.13.0/org.eclipse.jdt.core-3.13.0.jar", "org.eclipse.jdt.core-3.13.0.jar"),
    ("org/eclipse/platform/org.eclipse.text/3.8.0/org.eclipse.text-3.8.0.jar", "org.eclipse.text-3.8.0.jar"),
    ("org/eclipse/platform/org.eclipse.core.runtime/3.13.0/org.eclipse.core.runtime-3.13.0.jar", "org.eclipse.core.runtime-3.13.0.jar"),
    ("org/eclipse/platform/org.eclipse.equinox.common/3.9.0/org.eclipse.equinox.common-3.9.0.jar", "org.eclipse.equinox.common-3.9.0.jar"),
    ("org/eclipse/platform/org.eclipse.core.resources/3.12.0/org.eclipse.core.resources-3.12.0.jar", "org.eclipse.core.resources-3.12.0.jar"),
    ("org/eclipse/platform/org.eclipse.core.expressions/3.6.0/org.eclipse.core.expressions-3.6.0.jar", "org.eclipse.core.expressions-3.6.0.jar"),
    ("org/eclipse/platform/org.eclipse.core.filesystem/1.7.0/org.eclipse.core.filesystem-1.7.0.jar", "org.eclipse.core.filesystem-1.7.0.jar"),
    ("org/eclipse/platform/org.eclipse.core.jobs/3.9.0/org.eclipse.core.jobs-3.9.0.jar", "org.eclipse.core.jobs-3.9.0.jar"),
    ("org/eclipse/platform/org.eclipse.osgi/3.12.0/org.eclipse.osgi-3.12.0.jar", "org.eclipse.osgi-3.12.0.jar"),
    ("org/eclipse/platform/org.eclipse.equinox.preferences/3.7.0/org.eclipse.equinox.preferences-3.7.0.jar", "org.eclipse.equinox.preferences-3.7.0.jar"),
    ("org/eclipse/platform/org.eclipse.equinox.registry/3.8.0/org.eclipse.equinox.registry-3.8.0.jar", "org.eclipse.equinox.registry-3.8.0.jar"),
    ("org/osgi/org.osgi.core/6.0.0/org.osgi.core-6.0.0.jar", "org.osgi.core-6.0.0.jar"),
]


def log(msg):
    print(f"[jdt-gate] {msg}")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------- 环境探测 ----------

def _read_env_yaml():
    if not ENV_YAML.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(ENV_YAML.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _write_env_yaml(cfg, entries):
    """把 runtime.jdt.* 条目并入机器级 env.yaml（P29：仅当有 consumer 时写入）。"""
    try:
        import yaml
        cfg.setdefault("runtime", {}).setdefault("jdt", {}).update(entries)
        ENV_YAML.parent.mkdir(parents=True, exist_ok=True)
        ENV_YAML.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        log(f"env 已持久化: {ENV_YAML} (runtime.jdt.{', '.join(entries)})")
    except Exception as e:
        log(f"env 持久化失败（不影响本次运行）: {e}")


def find_java(explicit):
    if explicit:
        return Path(explicit) if Path(explicit).exists() else None
    cfg = _read_env_yaml()
    for cand in [
        cfg.get("runtime", {}).get("jdt", {}).get("java"),
        os.environ.get("JAVA_HOME", "") and str(Path(os.environ["JAVA_HOME"]) / "bin" / "java"),
        *[str(j / "bin" / "java") for j in sorted(HOME.glob(".jdks/*"))],
        shutil.which("java") or "",
    ]:
        if cand and Path(cand).exists() and os.access(cand, os.X_OK):
            return Path(cand)
    for j in sorted(Path("/usr/lib/jvm").glob("*/bin/java")) if Path("/usr/lib/jvm").is_dir() else []:
        if j.exists():
            return j
    return None


def find_lib_dir(explicit_jar):
    """返回 (lib_dir, build_dir)。jdt 闭包 jar 统一放 LIB_DIR，classpath 用通配。"""
    cfg = _read_env_yaml().get("runtime", {}).get("jdt", {})
    lib = Path(cfg.get("lib-dir") or LIB_DIR)
    build = Path(cfg.get("build-dir") or AI_ROOT / "tools" / "jdt-format-gate" / "build")
    if explicit_jar:
        return Path(explicit_jar).parent, build
    return lib, build


def _closure_ready(lib):
    """闭包完整性：所有必需 jar 都在 lib 目录。"""
    if not lib.is_dir():
        return False
    names = {p.name for p in lib.glob("*.jar")}
    return all(Path(url).name in names for url, _ in JDT_JARS)


# ---------- 干跑 ----------

def dry_run(java, lib_dir, build_dir, xml, src_dir):
    lib_dir = Path(lib_dir)
    build_dir = Path(build_dir)
    cp = f"{lib_dir}/*:{build_dir}"   # 闭包 jar 目录通配
    cls = build_dir / "JdtFormatCheck.class"
    if not cls.exists():
        log("编译 wrapper（javac）...")
        r = run([str(Path(java).parent / "javac"), "-cp", cp,
                 "-d", str(build_dir), str(WRAPPER_SRC)])
        if r.returncode != 0:
            log(f"javac 失败: {r.stderr.strip()[:300]}")
            return 3
    r = run([str(java), "-cp", cp, "JdtFormatCheck", str(xml), str(src_dir)])
    # rc 0=一致 / 1=有差异 均为 wrapper 正常输出；其余（含 stdout 无 files=）判失败
    if r.returncode not in (0, 1) or "files=" not in r.stdout:
        log(f"wrapper 运行失败（rc={r.returncode}）: {r.stderr.strip()[:300] or r.stdout.strip()[:300]}")
        return 3
    log(r.stdout.strip())
    differ = 0
    for line in r.stdout.splitlines():
        if "differ=" in line:
            try:
                differ = int(line.split("differ=")[1].split()[0])
            except Exception:
                pass
    return 0 if differ == 0 else (1 if differ <= DIFF_WARN_MAX_FILES else 2)


# ---------- setup（授权配置环境） ----------

def setup_environment(java):
    """下载 JDT 运行闭包（JDT_JARS）到 LIB_DIR 并编译 wrapper。返回 (lib, build)。"""
    LIB_DIR.mkdir(parents=True, exist_ok=True)
    build = AI_ROOT / "tools" / "jdt-format-gate" / "build"
    build.mkdir(parents=True, exist_ok=True)
    for url, fname in JDT_JARS:
        target = LIB_DIR / fname
        if target.exists():
            continue
        log(f"下载 {fname} <- {MAVEN}/{url}")
        try:
            urllib.request.urlretrieve(f"{MAVEN}/{url}", str(target))
        except Exception as e:
            log(f"下载失败（网络/公司源？）: {e}")
            return None
    if build and not (build / "JdtFormatCheck.class").exists():
        cp = f"{LIB_DIR}/*"
        r = run([str(Path(java).parent / "javac"), "-cp", cp, "-d", str(build),
                 str(WRAPPER_SRC)])
        if r.returncode != 0:
            log(f"javac 失败: {r.stderr.strip()[:300]}")
            return None
    _write_env_yaml(_read_env_yaml(), {
        "java": str(java), "lib-dir": str(LIB_DIR), "build-dir": str(build),
    })
    log("环境就绪（已持久化到 env.yaml）")
    return LIB_DIR, build


# ---------- 交互 ----------

def interact(prompt, options):
    while True:
        ans = input(f"[jdt-gate] {prompt} [{options}] ").strip().lower()
        if ans:
            return ans[0]


def main(argv=None):
    ap = argparse.ArgumentParser(description="eclipse JDT formatter 干跑门禁（C2）")
    ap.add_argument("src_dir", help="Java 源目录")
    ap.add_argument("--xml", default=str(XML_DEFAULT))
    ap.add_argument("--java", default=None, help="JDK java 可执行文件（用户提供）")
    ap.add_argument("--jar", default=None, help="jdt.core jar（用户提供）")
    ap.add_argument("--setup", action="store_true", help="直接执行环境配置（不跑检查）")
    ap.add_argument("--skip", action="store_true", help="显式跳过本次检查（环境不可用时）")
    ap.add_argument("--batch", action="store_true", help="非交互模式（无 TTY 时）")
    args = ap.parse_args(argv)

    if not Path(args.src_dir).is_dir():
        log(f"ERROR: 源目录不存在: {args.src_dir}")
        return 2

    if args.setup:
        java = find_java(args.java)
        if not java:
            log("未找到 JDK（可 --java <路径> 提供，或安装后重试）")
            return 3
        ok = setup_environment(java)
        return 0 if ok else 3

    java = find_java(args.java)
    if not java:
        log("JDK 不可用（探测路径：JAVA_HOME / ~/.jdks/* / PATH / /usr/lib/jvm/*）")
        if args.batch:
            log("非交互模式：可用 --java <java 路径> 提供，或 --skip 跳过本次")
            return 3 if not args.skip else 0
        while True:
            c = interact("JDK 未找到：提供路径 [p]/跳过本次 [s]/终止 [a]？", "p/s/a")
            if c == "p":
                p = input("[jdt-gate] java 完整路径: ").strip()
                java = find_java(p)
                if java:
                    break
                log("路径无效，请重试或选其他项")
            elif c == "s":
                log("已跳过本次 JDT 格式检查（用户选择）")
                return 0
            else:
                return 3
        _write_env_yaml(_read_env_yaml(), {"java": str(java)})

    lib, build = find_lib_dir(args.jar)
    if not _closure_ready(lib):
        log("JDT 组件不完整（lib 目录缺 jar：" + str(lib) + "）")
        if args.batch:
            log("非交互模式：--setup 自动配置（下载 JDT 闭包），或 --skip 跳过本次")
            return 3 if not args.skip else 0
        while True:
            c = interact("组件缺失：自动配置 [s(etup)]/跳过 [k]/终止 [a]？", "s/k/a")
            if c == "s":
                res = setup_environment(java)
                if res:
                    lib, build = res
                    break
                log("配置失败，请检查网络或手动放置 jar 到 ~/.local/lib/jdt-gate/")
            elif c == "k":
                log("已跳过本次 JDT 格式检查（用户选择）")
                return 0
            else:
                return 3

    return dry_run(java, lib, build, Path(args.xml), Path(args.src_dir))


if __name__ == "__main__":
    sys.exit(main())