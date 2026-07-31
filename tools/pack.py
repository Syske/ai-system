r"""Pack the ai-system directory for migration to another machine.

Usage:
    python tools/pack.py                          # pack to ../ai-system-pack/
    python tools/pack.py --output D:\migration    # custom output directory
    python tools/pack.py --with-reports           # include reports/
    python tools/pack.py --with-methodologies     # include ../methodologies/
    python tools/pack.py --zip                    # pack + compress to .zip (deletes temp dir)
    python tools/pack.py --with-reports --zip     # combine flags

Excludes: __pycache__, *.pyc, logs/*, node_modules/, archived/ai-runtime/opencode/node_modules/
local.yaml is copied as a .template (absolute paths must be filled in manually).

Output:
    {output}/
    ├── ai-system/              packed ai-system tree
    │   ├── tools/pack.py       self-ships (usable after migration)
    │   └── README_MIGRATION.md migration checklist
    └── methodologies/          (if --with-methodologies, optional)
"""

import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

EXCLUDE_GLOBS = [
    "**/__pycache__",
    "**/*.pyc",
    "logs/*",
    "*.egg-info",
]

EXCLUDE_DIRS = {
    "node_modules",
}

EXCLUDE_FILES = {
    "link.txt",
    "package.json",
    "package-lock.json",
    "nul",
}


def main():

    output, do_zip = _parse_args()

    dest = output / "ai-system"

    if dest.exists():
        shutil.rmtree(dest)

    dest.mkdir(parents=True)

    for entry in ROOT.iterdir():

        if entry.name in EXCLUDE_DIRS:
            continue

        if not entry.is_dir():

            if entry.name in EXCLUDE_FILES:
                continue

            shutil.copy2(entry, dest / entry.name)
            continue

        _copy_dir(entry, dest, entry.name)

    pack_py = dest / "tools" / "pack.py"

    if pack_py.exists():
        pack_py.unlink()

    shutil.copy2(
        HERE / "pack.py",
        pack_py
    )

    _process_local_yaml(dest)

    if "--with-reports" in sys.argv:

        reports_src = ROOT / "reports"

        if reports_src.is_dir():
            shutil.copytree(
                reports_src,
                dest / "reports",
                dirs_exist_ok=True
            )

    if "--with-methodologies" in sys.argv:

        methodologies_src = ROOT.parent / "methodologies"

        if methodologies_src.is_dir():
            shutil.copytree(
                methodologies_src,
                output / "methodologies",
                dirs_exist_ok=True,
                ignore=_ignore_patterns
            )

    _write_readme(output, dest)

    print()
    _count(dest)

    if do_zip:

        zip_path = output.parent / (output.name + ".zip")

        print(f"Compressing to {zip_path} ...")

        _make_zip(output, zip_path)

        shutil.rmtree(output)

        print(f"Compressed: {zip_path} ({_size_str(zip_path)})")
        print("Next: extract and read README_MIGRATION.md")

    else:

        print(f"\nPacked: {output}")
        print("Next: read README_MIGRATION.md in the packed directory")


def _copy_dir(
    src,
    dest,
    rel_path
):

    target = dest / rel_path

    target.mkdir(parents=True, exist_ok=True)

    for entry in src.iterdir():

        sub = f"{rel_path}/{entry.name}"

        if entry.name in EXCLUDE_DIRS:
            continue

        if entry.name in EXCLUDE_FILES:
            continue

        if not entry.is_dir():

            if entry.name in EXCLUDE_FILES:
                continue

            if entry.suffix == ".pyc":
                continue

            shutil.copy2(entry, target / entry.name)
            continue

        if "__pycache__" in sub:
            continue

        if "archived/ai-runtime/opencode/node_modules" in sub:
            continue

        _copy_dir(entry, dest, sub)


def _ignore_patterns(
    directory,
    contents
):

    ignored = set()

    for name in contents:

        if name in EXCLUDE_DIRS:
            ignored.add(name)
            continue

        if name in EXCLUDE_FILES:
            ignored.add(name)
            continue

        if name.endswith(".pyc"):
            ignored.add(name)
            continue

        if name == "__pycache__":
            ignored.add(name)
            continue

    return ignored


def _process_local_yaml(dest):

    env_config = (
        dest
        / "config"
        / "environments"
        / "local.yaml"
    )

    if not env_config.exists():
        return

    text = env_config.read_text(encoding="utf-8")

    env_config.rename(
        str(env_config) + ".template"
    )

    context = (
        dest
        / "config"
        / "environments"
        / "context.yaml"
    )

    if context.exists():
        context.unlink()

    print()
    print("local.yaml  saved as local.yaml.template")
    print("            Fill in absolute paths (workspace.root, repository_root,")
    print("            build.java_home, build.maven_home, build.maven_settings)")
    print("            then rename to local.yaml")


def _write_readme(output, dest):

    lines = [
        "# AI System — Migration Package",
        "",
        "## What's Here",
        "",
        "ai-system/ — the full AI Runtime Engine (workflows, skills, governance, CLI)",
        "",
    ]

    if (output / "methodologies").is_dir():
        lines.append(
            "methodologies/ — methodology providers (OpenSpec templates and assets)"
        )
        lines.append("")

    lines += [
        "## Post-Migration Steps",
        "",
        "1. Edit ai-system/config/environments/local.yaml.template:",
        "   - workspace.root — absolute path to the new workspace root",
        "   - workspace.repository_root — path to cloned code repositories (can be a junction)",
        "   - build.java_home / build.maven_home / build.maven_settings — local tool paths",
        "   - Rename to local.yaml",
        "",
        "2. Create or rebuild the projects/ junction:",
        '     mklink /J projects D:\\path\\to\\code-repositories',
        "",
        '3. Run python ai-system/tools/path-audit.py to verify all paths resolve',
        "",
        "4. Install Python dependencies and register the CLI:",
        "     cd ai-system",
        "     pip install -e .    # editable install; `aic` command available after",
        "",
        "5. Verify:",
        "     aic --help          # positional: aic <workflow>",
        "     aic                 # interactive wizard (no arguments)",
        "     python tools/path-audit.py",
        "",
        "## Packed On",
        "",
        "{date}",
        "",
        "## Included Directories",
        "",
        "{dirs}",
        "",
        "## Excluded",
        "",
        "- logs/, metrics/, .egg-info, __pycache__, *.pyc",
        "- node_modules/, package*.json, link.txt",
        "- archived/ai-runtime/opencode/node_modules/",
        "- local.yaml (saved as .template — contains absolute paths)",
        "",
        "Run tools/pack.py on the new machine after the first migration to create",
        "subsequent migration packages.",
    ]

    included = []

    for d in sorted(dest.iterdir()):

        if d.is_dir():
            included.append(f"  {d.name}/")

    readme = (
        "\n".join(lines)
        .replace("{date}", _today())
        .replace("{dirs}", "\n".join(included))
    )

    (dest / "README_MIGRATION.md").write_text(
        readme,
        encoding="utf-8"
    )


def _today():

    from datetime import date

    return date.today().isoformat()


def _count(root):

    files = 0
    dirs = 0

    for entry in root.rglob("*"):

        if entry.name == "__pycache__":
            continue

        if entry.is_dir():
            dirs += 1

        else:
            files += 1

    print(f"files: {files}  dirs: {dirs}")


def _parse_args():

    output = None
    do_zip = False

    for i, arg in enumerate(sys.argv):

        if arg == "--output" and i + 1 < len(sys.argv):
            output = Path(sys.argv[i + 1])

        elif arg == "--zip":
            do_zip = True

        elif arg == "--with-reports":
            pass

        elif arg == "--with-methodologies":
            pass

    if output is None:
        output = ROOT.parent / "ai-system-pack"

    return output, do_zip


def _make_zip(
    src,
    dest
):

    with zipfile.ZipFile(
        dest,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zf:

        root_dir = src.resolve()

        for f in sorted(root_dir.rglob("*")):

            arcname = f.relative_to(root_dir)

            if f.is_dir():

                zf.write(
                    f,
                    f"{arcname}/"
                )

            else:

                zf.write(f, arcname)


def _size_str(path):

    size = path.stat().st_size

    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.0f} KB"

    return f"{size / (1024 * 1024):.1f} MB"


if __name__ == "__main__":
    main()
