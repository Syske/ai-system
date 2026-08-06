#!/usr/bin/env python3
"""Skill Optimizer CLI — main entry point (S1 split).

Core helper functions live in core.py; this module keeps the
workspace orchestration (run_optimizer) and the CLI (main).

CLI contract is unchanged from the pre-split main.py; the only addition
is the optional `--parallel` flag (default off, preserves original
serial behavior).

No dependencies beyond the Python stdlib + the skill-optimizer package.
"""

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from architecture.genome import SkillGenome
from constants import ENV_FILE, GLOBAL_CONFIG_DIR
from core import (
    RealLLMClient,
    build_auto_snapshot_reason,
    extract_referenced_skill_paths,
    integrate_auxiliary_references,
    sanitize_reference_content,
    validate_auxiliary_file,
    validate_skill_file,
)
from engine.report_generator import OptimizationReportGenerator
from optimizer import SkillOptimizer
from skill_insight_api import get_skill_logs
from cli_args import CliArgsError, resolve_human_feedback_content

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _resolve_skill_dir_in_workspace(workspace_dir: Path, skill_name: str) -> Path:
    """Resolve the inner skill directory path within a workspace.

    The workspace has a two-layer structure:
      workspace_dir/           <- outer: snapshots, reports, etc.
        skill-name/            <- inner: pure skill content (SKILL.md + auxiliary files)

    When iterating on an existing workspace (input has snapshots),
    the skill content lives in the workspace root for backward compatibility.
    """
    inner_dir = workspace_dir / skill_name
    if inner_dir.exists() and (inner_dir / "SKILL.md").exists():
        return inner_dir
    if (workspace_dir / "SKILL.md").exists():
        return workspace_dir
    return inner_dir


def _sync_skill_to_inner_dir(skill_dir: Path, inner_dir: Path, skill_name: str):
    """Sync pure skill files from skill_dir to inner_dir within the workspace.

    Only copies SKILL.md and auxiliary files (scripts/, references/),
    excluding snapshots, reports, diagnoses, and other process artifacts.
    """
    import shutil

    inner_dir.mkdir(parents=True, exist_ok=True)

    exclude_names = {
        "snapshots", ".git", "__pycache__", "node_modules",
        ".venv", "venv", ".opt", "diagnoses.json",
        "OPTIMIZATION_REPORT.md", "AUXILIARY_META.json",
    }

    for item in skill_dir.iterdir():
        if item.name in exclude_names:
            continue
        if item.name.startswith("."):
            continue
        dest = inner_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    logger.info(f"Synced pure skill content to inner dir: {inner_dir}")


def _archive_old_skill(skill_name: str, opencode_skills_dir: Path) -> Optional[Path]:
    """Archive an old skill from .opencode/skills/ to ~/.agent-insight/skill-history/.

    Handles name collisions by appending timestamp and optional index suffix.

    Returns:
        Path to the archive directory if archived, None if nothing to archive.
    """
    import shutil
    from pathlib import Path

    old_skill_dir = opencode_skills_dir / skill_name
    if not old_skill_dir.exists():
        return None

    history_base = GLOBAL_CONFIG_DIR / "skill-history"
    history_base.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = history_base / f"{skill_name}-{timestamp}"

    if archive_dir.exists():
        idx = 1
        while (history_base / f"{skill_name}-{timestamp}-{idx}").exists():
            idx += 1
        archive_dir = history_base / f"{skill_name}-{timestamp}-{idx}"

    shutil.move(str(old_skill_dir), str(archive_dir))
    logger.info(f"Archived old skill to: {archive_dir}")
    return archive_dir


def run_optimizer(
    mode: str,
    input_path: Path,
    project_dir: Path,
    human_feedback: Optional[str] = None,
    trajectories: Optional[Path] = None,
    open_diff: bool = True,
    parallel: bool = False,
) -> List[Path]:
    """
    Main entry point for function calls.

    Args:
        mode: 'static' or 'dynamic' or 'feedback' or 'traces'
        input_path: Path to input directory or file
        project_dir: Project root directory for creating the optimized workspace
        human_feedback: Optional human feedback content to guide optimization
        open_diff: Whether to open diff in browser
        parallel: If True and multiple SKILL.md files are found, process them
            concurrently with a ThreadPoolExecutor (default False = original
            serial behavior).

    Returns:
        List[Path]: List of paths to the optimized skill directories (inner skill dirs)
    """

    load_dotenv(ENV_FILE)

    # 1. Initialize Components
    try:
        llm_client = RealLLMClient()
    except ValueError as e:
        logger.error(str(e))
        return []

    # Use Factory Method to create optimizer with all dependencies wired up
    optimizer = SkillOptimizer.from_llm_client(llm_client)
    report_generator = OptimizationReportGenerator(llm_client)

    # 2. Resolve Paths
    input_path = Path(input_path).resolve()
    input_dir = input_path.parent if input_path.is_file() else input_path

    # E3/P15 guard: one run = one skill. Count SKILL.md under the source dir
    # (excluding snapshots/.opt) BEFORE creating any workspace, so a
    # multi-skill directory is refused without side effects.
    source_skill_count = len([
        f for f in input_dir.rglob("SKILL.md")
        if f.exists()
        and "snapshots" not in f.parts
        and ".opt" not in f.parts
    ]) if input_dir.is_dir() else 1
    if source_skill_count > 1:
        logger.error(
            f"Found {source_skill_count} SKILL.md files under {input_dir}; "
            f"run_optimizer supports exactly one skill per run. "
            f"Optimize each skill separately (pass its own directory/file)."
        )
        return []

    # Determine the skill name from the input directory
    # For iteration on existing workspaces, try to find the inner skill dir first
    skill_name = input_dir.name
    if (input_dir / "snapshots").exists():
        # This is an existing workspace - look for inner skill dir
        for sub in input_dir.iterdir():
            if sub.is_dir() and (sub / "SKILL.md").exists() and sub.name != "snapshots":
                skill_name = sub.name
                break

    # Check if input_dir already looks like a workspace (has snapshots)
    if (input_dir / "snapshots").exists():
        workspace_dir = input_dir
    else:
        base_dir = Path(project_dir).resolve()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace_dir = base_dir / f"{input_dir.name}-optimized-{timestamp}"

    # Determine if this is a new workspace (first-time optimization) or iteration
    is_new_workspace = workspace_dir != input_dir and not workspace_dir.exists()

    # Initialize workspace if it's new
    # Two-layer structure: workspace_dir/ (outer) -> skill_name/ (inner, pure skill)
    if is_new_workspace:
        import shutil
        inner_skill_dir = workspace_dir / skill_name

        def ignore_patterns(d, contents):
            return ['snapshots', '.git', '__pycache__', 'node_modules', '.venv', 'venv', '.opt']
        shutil.copytree(input_dir, inner_skill_dir, ignore=ignore_patterns)
        logger.info(f"Created new workspace: {workspace_dir}")
        logger.info(f"Inner skill directory: {inner_skill_dir}")
    else:
        inner_skill_dir = _resolve_skill_dir_in_workspace(workspace_dir, skill_name)
        # Ensure inner skill dir exists for iteration on existing workspaces
        if not inner_skill_dir.exists() or not (inner_skill_dir / "SKILL.md").exists():
            # Backward compat: if workspace root has SKILL.md, create inner dir
            if (workspace_dir / "SKILL.md").exists():
                _sync_skill_to_inner_dir(workspace_dir, inner_skill_dir, skill_name)

    # 3. Locate SKILL.md - search in the inner skill directory
    skill_files = []
    explicit_skill_file = input_path.is_file() and input_path.name.lower() == "skill.md"
    if explicit_skill_file:
        skill_files.append(inner_skill_dir / "SKILL.md")
    else:
        skill_files = list(inner_skill_dir.rglob("SKILL.md"))

    if explicit_skill_file:
        skill_files = [f for f in skill_files if f.exists()]
    else:
        skill_files = [
            f
            for f in skill_files
            if f.exists() and "snapshots" not in f.parts and ".opt" not in f.parts
        ]
    skill_files.sort()

    if not skill_files:
        logger.error(f"No SKILL.md found in {inner_skill_dir}")
        return []

    # E3 guard (P15): one workspace = one skill. Multiple SKILL.md files would
    # share a single inner_skill_dir and overwrite each other via revert_to.
    # Refuse rather than silently corrupt the workspace.
    if len(skill_files) > 1:
        logger.error(
            f"Found {len(skill_files)} SKILL.md files under {inner_skill_dir}; "
            f"run_optimizer supports exactly one skill per run. "
            f"Optimize each skill separately (pass its own directory/file)."
        )
        return []

    logger.info(f"Found {len(skill_files)} skill(s) to process in workspace {workspace_dir}.")

    optimized_paths = []
    diff_open_payload = None

    # 4. Per-skill processing (shared by serial and parallel paths)
    def process_skill_file(skill_file):
        """Process one SKILL.md; returns a payload dict on success, None on skip."""
        logger.info(f"Processing: {skill_file}")
        logger.info(f"Mode: {mode}")

        try:
            # Initialize variables
            optimized_genome = None
            diagnoses = []

            # Load Genome initially (try from directory for context)
            try:
                initial_genome = SkillGenome.from_directory(skill_file.parent)
            except Exception as e:
                logger.warning(f"Failed to load from directory: {e}. Fallback to file.")
                with open(skill_file, "r", encoding="utf-8") as f:
                    initial_genome = SkillGenome.from_markdown(f.read())

            if mode == "static":
                logger.info("Mode: Static (Cold Start)")
                logger.info("⏳ [进度] 正在执行静态评估...")
                logger.info("⏳ [进度] 预计需要 1-3 分钟，请耐心等待...")
                logger.info("⏳ [进度] LLM 调用中...")
                optimized_genome, diagnoses = optimizer.optimize_static(
                    skill_file
                )

            elif mode == "feedback":
                logger.info("Mode: Feedback (User Revision)")
                logger.info("⏳ [进度] 正在执行反馈改写（基于你的修改意见）...")
                logger.info("⏳ [进度] 预计需要 1-3 分钟，请耐心等待...")
                logger.info("⏳ [进度] LLM 调用中...")
                optimized_genome, diagnoses = optimizer.optimize_feedback(
                    skill_file, human_feedback=human_feedback
                )

            elif mode == "dynamic":
                logger.info("Mode: Dynamic (Experience Crystallization)")
                logger.info("⏳ [进度] 正在获取历史执行记录...")
                try:
                    report_items = get_skill_logs(skill=initial_genome.name, limit=3)
                except ValueError as e:
                    logger.warning(str(e))
                    print("\n" + "=" * 60)
                    print("⚠️ Agent Insight 平台配置不可用，无法获取执行日志。")
                    print("动态优化需要执行日志中的优化建议，请先配置 Agent Insight 平台。")
                    print("配置方式：在 ~/.agent-insight/.env 中设置 AGENT_INSIGHT_HOST 和 AGENT_INSIGHT_API_KEY")
                    print("=" * 60)
                    return None

                if not report_items:
                    print("\n" + "=" * 60)
                    print("⚠️ 未获取到执行日志，无法进行动态优化。")
                    print(f"Skill: {initial_genome.name}")
                    print("可能原因：该 Skill 尚未在 Insight 平台上运行过，没有历史执行记录。")
                    print("建议：先运行该 Skill 产生执行日志，或改用 static 模式进行优化。")
                    print("=" * 60)
                    return None

                suggestion_count = 0
                for item in report_items:
                    issues = item.get("skill_issues")
                    if isinstance(issues, list):
                        for issue in issues:
                            if isinstance(issue, dict) and issue.get("improvement_suggestion"):
                                suggestion_count += 1

                if suggestion_count == 0:
                    print("\n" + "=" * 60)
                    print("⚠️ 执行日志中未包含优化建议（improvement_suggestion），无法进行动态优化。")
                    print(f"Skill: {initial_genome.name}")
                    print(f"获取到 {len(report_items)} 条执行日志，但其中没有包含 improvement_suggestion 优化建议。")
                    print("建议：改用 static 模式进行优化。")
                    print("=" * 60)
                    return None

                logger.info(f"📊 获取到 {len(report_items)} 条执行日志，共 {suggestion_count} 条优化建议。")
                logger.info("⏳ [进度] 正在执行动态优化...")
                logger.info("⏳ [进度] 预计需要 3-5 分钟，请耐心等待...")
                logger.info("⏳ [进度] LLM 调用中...")
                optimized_genome, diagnoses = optimizer.optimize_dynamic(
                    genome=initial_genome, report_items=report_items
                )

            elif mode == "hybrid":
                logger.info("Mode: Hybrid (Static + Dynamic)")
                logger.info("⏳ [进度] 正在获取历史执行记录...")
                try:
                    report_items = get_skill_logs(skill=initial_genome.name, limit=3)
                except ValueError as e:
                    logger.warning(str(e))
                    logger.warning("Agent Insight 配置不可用，降级为 static 模式。")
                    print("\n" + "=" * 60)
                    print("⚠️ Agent Insight 平台配置不可用，降级为静态优化模式。")
                    print("=" * 60)
                    optimized_genome, diagnoses = optimizer.optimize_static(skill_file)
                else:
                    if not report_items:
                        logger.warning("未获取到执行日志，降级为静态优化模式。")
                        print("\n" + "=" * 60)
                        print("⚠️ 未获取到执行日志，降级为静态优化模式。")
                        print(f"Skill: {initial_genome.name}")
                        print("建议：先运行该 Skill 产生执行日志后再尝试混合优化。")
                        print("=" * 60)
                        optimized_genome, diagnoses = optimizer.optimize_static(skill_file)
                    else:
                        suggestion_count = 0
                        for item in report_items:
                            issues = item.get("skill_issues")
                            if isinstance(issues, list):
                                for issue in issues:
                                    if isinstance(issue, dict) and issue.get("improvement_suggestion"):
                                        suggestion_count += 1

                        if suggestion_count == 0:
                            logger.warning("执行日志中未包含优化建议，降级为静态优化模式。")
                            print("\n" + "=" * 60)
                            print("⚠️ 执行日志中未包含优化建议（improvement_suggestion），降级为静态优化模式。")
                            print(f"Skill: {initial_genome.name}")
                            print(f"获取到 {len(report_items)} 条执行日志，但其中没有包含 improvement_suggestion 优化建议。")
                            print("=" * 60)
                            optimized_genome, diagnoses = optimizer.optimize_static(skill_file)
                        else:
                            logger.info(f"📊 获取到 {len(report_items)} 条执行日志，共 {suggestion_count} 条优化建议。")
                            logger.info("⏳ [进度] 正在执行混合优化（静态 + 动态）...")
                            logger.info("⏳ [进度] 预计需要 5-8 分钟，请耐心等待...")
                            logger.info("⏳ [进度] LLM 调用中...")
                            optimized_genome, diagnoses = optimizer.optimize_hybrid(
                                skill_path=skill_file,
                                report_items=report_items,
                            )

            elif mode == "trace":
                logger.info("Mode: Trace (Trajectory-Driven Optimization)")
                if not trajectories:
                    print("\n" + "=" * 60)
                    print("⚠️ 轨迹目录未提供，无法进行轨迹优化。")
                    print("请使用 --trajectories 参数指定轨迹目录。")
                    print("=" * 60)
                    return None

                trajectory_path = Path(trajectories)
                if not trajectory_path.exists():
                    print("\n" + "=" * 60)
                    print(f"⚠️ 轨迹目录不存在: {trajectory_path}")
                    print("=" * 60)
                    return None

                logger.info(f"📂 轨迹目录: {trajectory_path}")
                logger.info("⏳ [进度] 正在执行轨迹分析...")
                logger.info("⏳ [进度] 预计需要 5-10 分钟，请耐心等待...")
                logger.info("⏳ [进度] LLM 调用中...")
                optimized_genome, diagnoses = optimizer.optimize_trace(
                    skill_path=skill_file,
                    trajectories=trajectory_path,
                    project_path=workspace_dir,
                )

            # 5. Save Result
            from snapshot_manager import SnapshotManager
            workspace_snapshots_dir = workspace_dir / "snapshots"
            sm = SnapshotManager(inner_skill_dir, snapshots_dir=workspace_snapshots_dir)
            sm.create_v0_if_needed()
            base_for_diff = (
                sm.get_current_base_version()
                or sm.get_latest_base_version()
                or "v0"
            )

            is_feedback = mode == "feedback"
            if is_feedback:
                reason = f"用户反馈: {human_feedback[:50]}..."
                source = "user"
            else:
                reason = build_auto_snapshot_reason(mode, diagnoses)
                source = "auto"

            new_version = sm.create_snapshot(
                mode=mode,
                reason=reason,
                source=source,
                is_feedback=is_feedback
            )

            skill_save_dir = sm.snapshots_dir / new_version

            # Save SKILL.md
            if optimized_genome:
                new_content = optimized_genome.to_markdown()
                if not new_content or len(new_content) < 50:
                    logger.warning(
                        "Optimized SKILL.md content is suspiciously short or empty!"
                    )

                referenced = extract_referenced_skill_paths(new_content)
                if referenced:
                    initial_referenced = initial_genome.referenced_files
                    missing = []
                    for p in referenced:
                        if p in optimized_genome.files:
                            continue
                        if p in initial_genome.files:
                            optimized_genome.files[p] = initial_genome.files[p]
                            if p in initial_genome.file_meta and p not in optimized_genome.file_meta:
                                optimized_genome.file_meta[p] = initial_genome.file_meta[p]
                            continue
                        if p in initial_referenced:
                            logger.info(f"Referenced file {p} was missing in original SKILL.md, skipping validation")
                            continue
                        missing.append(p)
                    if missing:
                        logger.warning(f"Optimized SKILL.md references missing files. Falling back to original. Missing: {missing}")
                        optimized_genome = initial_genome
                        new_content = optimized_genome.to_markdown()

                new_content = integrate_auxiliary_references(
                    new_content, optimized_genome.files, optimized_genome.file_meta
                )

                save_file = skill_save_dir / "SKILL.md"
                with open(save_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info(f"Optimized skill saved to: {save_file}")

                is_valid, error_msg = validate_skill_file(save_file)
                if not is_valid:
                    logger.warning(f"SKILL.md 验证失败: {error_msg}")
                else:
                    logger.info(f"SKILL.md 验证通过: {save_file}")

                # Save Auxiliary Files (scripts, references, etc.)
                # optimized_genome.files contains relative paths -> content
                if not optimized_genome.files:
                    logger.warning(
                        "No auxiliary files found in optimized genome! (Scripts/References may be missing)"
                    )

                for rel_path, file_content in optimized_genome.files.items():
                    if rel_path.startswith(("snapshots/", ".opt/")):
                        continue
                    if rel_path in {
                        "AUXILIARY_META.json",
                        "diagnoses.json",
                        "OPTIMIZATION_REPORT.md",
                        "meta.json",
                    }:
                        continue
                    dest_path = skill_save_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    if rel_path.startswith("references/"):
                        file_content = sanitize_reference_content(file_content)
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(file_content)
                    logger.info(f"Saved auxiliary file: {rel_path}")

                    is_valid, error_msg = validate_auxiliary_file(dest_path)
                    if not is_valid:
                        logger.warning(f"辅助文件验证失败: {error_msg}")
                    else:
                        logger.info(f"辅助文件验证通过: {rel_path}")

                try:
                    import json

                    meta_out: dict[str, str] = {}
                    for rel_path in sorted(optimized_genome.files.keys()):
                        if rel_path.startswith(("snapshots/", ".opt/")):
                            continue
                        if rel_path in {
                            "AUXILIARY_META.json",
                            "diagnoses.json",
                            "OPTIMIZATION_REPORT.md",
                            "meta.json",
                        }:
                            continue
                        if not (
                            rel_path.startswith("scripts/")
                            or rel_path.startswith("references/")
                        ):
                            continue
                        meta_out[rel_path] = (optimized_genome.file_meta.get(rel_path) or "").strip()

                    snapshot_meta_path = skill_save_dir / "AUXILIARY_META.json"
                    with open(snapshot_meta_path, "w", encoding="utf-8") as f:
                        json.dump(meta_out, f, indent=2, ensure_ascii=False)
                    logger.info(f"Saved auxiliary meta: {snapshot_meta_path}")

                    skill_opt_dir = skill_file.parent / ".opt"
                    skill_opt_dir.mkdir(parents=True, exist_ok=True)
                    cache_meta_path = skill_opt_dir / "auxiliary_meta.json"
                    with open(cache_meta_path, "w", encoding="utf-8") as f:
                        json.dump(meta_out, f, indent=2, ensure_ascii=False)
                    logger.info(f"Saved auxiliary meta cache: {cache_meta_path}")
                except Exception as e:
                    logger.warning(f"Failed to save auxiliary meta: {e}")
            else:
                logger.warning("Optimization returned None. Skipping save.")

            # Save Diagnoses
            if diagnoses:
                import json

                diagnoses_file = skill_save_dir / "diagnoses.json"
                diagnoses_data = [
                    {
                        "dimension": d.dimension,
                        "issue_type": d.issue_type,
                        "severity": d.severity,
                        "description": d.description,
                        "suggested_fix": d.suggested_fix,
                    }
                    for d in diagnoses
                ]
                with open(diagnoses_file, "w", encoding="utf-8") as f:
                    json.dump(diagnoses_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved diagnoses to: {diagnoses_file}")
                logger.info(f"Total diagnoses: {len(diagnoses)}")

            # Generate and Save Optimization Report
            if optimized_genome and diagnoses:
                report_content = report_generator.generate_report(
                    original=initial_genome,
                    optimized=optimized_genome,
                    diagnoses=diagnoses,
                )
                report_file = skill_save_dir / "OPTIMIZATION_REPORT.md"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report_content)
                logger.info(f"Saved optimization report to: {report_file}")

            # Also update the actual skill directory to match the latest snapshot
            sm.revert_to(new_version)

            # Copy optimization report to workspace root for easy access
            if optimized_genome and diagnoses:
                snapshot_report = skill_save_dir / "OPTIMIZATION_REPORT.md"
                if snapshot_report.exists():
                    import shutil
                    workspace_report = workspace_dir / "OPTIMIZATION_REPORT.md"
                    shutil.copy2(snapshot_report, workspace_report)
                    logger.info(f"Copied optimization report to workspace root: {workspace_report}")

            diff_open_payload = {
                "snapshots_dir": sm.snapshots_dir,
                "title": initial_genome.name,
                "default_base": base_for_diff,
                "default_current": new_version,
                "skill_dir": inner_skill_dir,
            }

            # Record successful optimization path (inner skill dir for loading/uploading)
            optimized_paths.append(inner_skill_dir)
            logger.info(f"Optimization completed for: {skill_file}. New version: {new_version}")
            logger.info(f"Inner skill directory (for loading): {inner_skill_dir}")
            logger.info(f"Workspace directory (for iteration): {workspace_dir}")

            print("\n" + "=" * 60)
            print(f"✅ 优化完成！已生成新版本: {new_version}")
            print(f"📁 工作区目录（含快照与报告）: {workspace_dir}")
            print(f"📁 Skill 目录（可加载到 .opencode/skills）: {inner_skill_dir}")
            print("👉 Diff 页面将在本次运行结束后生成（必要时自动打开）。")
            print("👉 下一步选择：满意就继续下一步 / 不满意先改 / 到此为止")
            print("=" * 60 + "\n")

            return {
                "inner_skill_dir": inner_skill_dir,
                "diff_payload": diff_open_payload,
            }

        except Exception as e:
            logger.error(f"Optimization failed for {skill_file}: {e}")
            import traceback

            traceback.print_exc()
            return None

    # 5. Execute: serial (default) or parallel
    if parallel and len(skill_files) > 1:
        import concurrent.futures
        from concurrent.futures import ThreadPoolExecutor

        logger.info(f"Starting parallel processing of {len(skill_files)} skill(s)...")

        # Use ThreadPoolExecutor for I/O bound operations (LLM calls, file I/O)
        max_workers = min(10, len(skill_files))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_skill = {
                executor.submit(process_skill_file, skill_file): skill_file
                for skill_file in skill_files
            }
            for future in concurrent.futures.as_completed(future_to_skill):
                skill_file = future_to_skill[future]
                try:
                    result = future.result()
                    if result:
                        diff_open_payload = result["diff_payload"]
                    else:
                        logger.error(f"❌ Optimization skipped/failed for {skill_file}")
                except Exception as e:
                    logger.error(f"❌ Unexpected error processing {skill_file}: {e}")
                    import traceback

                    traceback.print_exc()
    else:
        for skill_file in skill_files:
            process_skill_file(skill_file)

    if diff_open_payload:
        try:
            import subprocess
            import webbrowser

            diff_script = Path(__file__).parent / "diff_viewer.py"
            diff_out = diff_open_payload["skill_dir"] / ".opt" / "diff.html"
            subprocess.run(
                [
                    sys.executable,
                    str(diff_script),
                    "--snapshots",
                    str(diff_open_payload["snapshots_dir"]),
                    "--title",
                    diff_open_payload["title"],
                    "--default-base",
                    diff_open_payload["default_base"],
                    "--default-current",
                    diff_open_payload["default_current"],
                    "--no-open",
                    "--output",
                    str(diff_out),
                ],
                check=False,
            )
            logger.info(f"Diff HTML written to: {diff_out}")
            if open_diff and len(skill_files) == 1:
                webbrowser.open(diff_out.resolve().as_uri())
        except Exception as e:
            logger.error(f"Failed to generate/open diff viewer: {e}")

    return optimized_paths


# --- CLI Entry Point ---


def main():
    parser = argparse.ArgumentParser(description="Skill Optimizer CLI")

    parser.add_argument(
        "--action",
        choices=["optimize", "accept", "revert", "augment", "validate", "tune-description"],
        default="optimize",
        help="Action to perform. Default is 'optimize'.",
    )
    parser.add_argument(
        "--mode",
        choices=["static", "dynamic", "feedback", "trace"],
        help="Optimization mode: static (cold), dynamic (trace-based), feedback (human revision), or trace (Trace2Skill). Required for 'optimize' action.",
    )
    parser.add_argument(
        "--trajectories",
        "-t",
        type=str,
        help="Path to trajectories directory. Required for --mode trace.",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Input path (directory containing SKILL.md or file path)",
    )
    parser.add_argument(
        "--project-dir",
        "-p",
        type=str,
        required=True,
        help="Project root directory where the optimized workspace will be created.",
    )
    parser.add_argument(
        "--no-open-diff",
        action="store_true",
        help="Generate diff HTML but do not open it in the browser.",
    )
    parser.add_argument(
        "--feedback",
        "-f",
        type=str,
        help="Path to feedback file or inline feedback text. Only allowed with --mode feedback.",
    )
    parser.add_argument(
        "--target-version",
        type=str,
        help="Target version to revert to (e.g. 'v1'). Required for 'revert' action.",
    )
    parser.add_argument(
        "--demos",
        type=str,
        help="Path to demos.json (array of {task, approach, result}) for 'augment' action.",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        help="Path to benchmark.json (array of {task, expected_outcome}) for 'validate' action.",
    )
    parser.add_argument(
        "--routing-report",
        type=str,
        help="Path to routing benchmark report for 'tune-description' action (optional).",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Process multiple SKILL.md files concurrently (default: serial).",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    # P11 absorbed actions: augment / validate / tune-description
    from actions import run_augment, run_tune_description, run_validate

    if args.action == "augment":
        demos_path = Path(args.demos) if args.demos else None
        raise SystemExit(run_augment(input_path, demos_path))

    if args.action == "validate":
        benchmark_path = Path(args.benchmark) if args.benchmark else None
        raise SystemExit(run_validate(input_path, benchmark_path))

    if args.action == "tune-description":
        routing_path = Path(args.routing_report) if args.routing_report else None
        raise SystemExit(run_tune_description(input_path, routing_path))

    if args.action == "accept":
        from snapshot_manager import SnapshotManager
        skill_dir = input_path.parent if input_path.is_file() else input_path
        snapshots_dir = skill_dir / "snapshots"
        inner_skill_dir = None
        if snapshots_dir.exists():
            # Two-layer workspace: snapshots in workspace root, find inner skill dir
            for sub in skill_dir.iterdir():
                if sub.is_dir() and sub.name != "snapshots" and (sub / "SKILL.md").exists():
                    inner_skill_dir = sub
                    break
            if inner_skill_dir is None:
                # Single-layer workspace (backward compat): skill_dir has SKILL.md directly
                if (skill_dir / "SKILL.md").exists():
                    inner_skill_dir = skill_dir
        else:
            # Single-layer workspace: snapshots inside skill dir
            for sub in skill_dir.iterdir():
                if sub.is_dir() and (sub / "SKILL.md").exists() and (sub / "snapshots").exists():
                    inner_skill_dir = sub
                    snapshots_dir = sub / "snapshots"
                    break
            if inner_skill_dir is None:
                if (skill_dir / "SKILL.md").exists():
                    inner_skill_dir = skill_dir
        if not snapshots_dir.exists():
            logger.error(f"❌ 目录 {skill_dir} 中没有 snapshots。请确保你在已优化的工作区中执行 accept。")
            return
        sm = SnapshotManager(inner_skill_dir, snapshots_dir=snapshots_dir if snapshots_dir != inner_skill_dir / "snapshots" else None)
        new_ver = sm.accept_latest()
        if new_ver:
            sm.revert_to(new_ver)
            logger.info(f"✅ 成功接受优化，已保存为新基线版本: {new_ver}")
        else:
            logger.error("❌ 没有可接受的版本。")
        return

    if args.action == "revert":
        if not args.target_version:
            parser.error("--target-version is required for 'revert' action")
        from snapshot_manager import SnapshotManager
        skill_dir = input_path.parent if input_path.is_file() else input_path
        snapshots_dir = skill_dir / "snapshots"
        inner_skill_dir = None
        if snapshots_dir.exists():
            for sub in skill_dir.iterdir():
                if sub.is_dir() and sub.name != "snapshots" and (sub / "SKILL.md").exists():
                    inner_skill_dir = sub
                    break
            if inner_skill_dir is None:
                if (skill_dir / "SKILL.md").exists():
                    inner_skill_dir = skill_dir
        else:
            for sub in skill_dir.iterdir():
                if sub.is_dir() and (sub / "SKILL.md").exists() and (sub / "snapshots").exists():
                    inner_skill_dir = sub
                    snapshots_dir = sub / "snapshots"
                    break
            if inner_skill_dir is None:
                if (skill_dir / "SKILL.md").exists():
                    inner_skill_dir = skill_dir
        if not snapshots_dir.exists():
            logger.error(f"❌ 目录 {skill_dir} 中没有 snapshots。请确保你在已优化的工作区中执行 revert。")
            return
        sm = SnapshotManager(inner_skill_dir, snapshots_dir=snapshots_dir if snapshots_dir != inner_skill_dir / "snapshots" else None)
        if sm.revert_to(args.target_version):
            logger.info(f"✅ 成功回滚到版本: {args.target_version}")
        else:
            logger.error(f"❌ 找不到指定的版本: {args.target_version}")
        return

    if not args.mode:
        parser.error("--mode is required for 'optimize' action")

    trajectories_path = Path(args.trajectories) if args.trajectories else None

    try:
        human_feedback_content = resolve_human_feedback_content(args.mode, args.feedback)
    except CliArgsError as e:
        parser.error(str(e))
    except OSError as e:
        parser.error(f"Failed to read feedback file: {e}")

    optimized_paths = run_optimizer(
        args.mode,
        input_path,
        project_dir=Path(args.project_dir),
        human_feedback=human_feedback_content,
        trajectories=trajectories_path,
        open_diff=not args.no_open_diff,
        parallel=args.parallel,
    )

    if optimized_paths:
        logger.info(
            f"Optimization completed. Modified skill paths: {[str(p) for p in optimized_paths]}"
        )


if __name__ == "__main__":
    main()
