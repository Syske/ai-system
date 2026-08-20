"""Chain (积木组合) registry + run context / manifest.

A chain is an ordered list of building blocks (workflow | command | skill)
that runs as one scenario-driven task.

Design (loose coupling + explicit handoff record): every run creates a run
context under outputs/chain/{yyMMdd}-{desc}/ holding chain-manifest.yaml,
which records each block's produced artifact so downstream blocks can locate
upstream artifacts without hardcoding paths.
"""

from datetime import datetime
from pathlib import Path

from cli.utils.yaml import load_yaml, save_yaml

CHAINS_FILE = "config/chains.yaml"
RUN_ROOT_NAME = "chain"


def load_chains(root):
    """Load builtin chains from config/chains.yaml (a list, or [])."""

    path = Path(root) / CHAINS_FILE

    if not path.exists():
        return []

    data = load_yaml(path)

    if not isinstance(data, dict):
        return []

    chains = data.get("chains", [])

    return chains if isinstance(chains, list) else []


def resolve_chain(text, chains):
    """Match free text against a chain's label/scenario/name (or block names).

    Zero-dependency keyword match. Returns the chain dict or None.
    """

    low = (text or "").lower()

    for chain in chains:

        for key in ("label", "scenario", "name"):

            value = str(chain.get(key, "")).lower()

            if value and value in low:
                return chain

        # 块名也参与匹配：如 "scan 发布" / "bugfix 转测"
        for b in chain.get("blocks", []):

            bname = str(b.get("name", "")).lower()

            if bname and bname in low:

                return chain

    return None


def block_names(chain):
    """Ordered block names of a chain."""

    return [
        b.get("name")
        for b in chain.get("blocks", [])
    ]


def create_chain_run(root, chain, outputs_root=None, desc=None):
    """Create a per-run context dir + chain-manifest.yaml.

    Returns (run_dir: Path, manifest_path: Path).
    """

    now = datetime.now()

    descriptor = (desc or chain.get("name") or "chain")[:30]

    run_dir = (
        Path(outputs_root or (Path(root) / "outputs"))
        / RUN_ROOT_NAME
        / f"{now.strftime('%y%m%d')}-{descriptor}"
    )

    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_at": now.isoformat(timespec="seconds"),
        "chain": chain.get("name"),
        "label": chain.get("label"),
        "blocks": [
            {
                "type": b.get("type"),
                "name": b.get("name"),
                "args": b.get("args") or {},
                "artifact": None,
            }
            for b in chain.get("blocks", [])
        ],
    }

    manifest_path = run_dir / "chain-manifest.yaml"

    save_yaml(manifest_path, manifest)

    return run_dir, manifest_path


def record_artifact(manifest_path, block_name, artifact_path):
    """Record a block's produced artifact into the manifest.

    Returns the updated manifest, or None if the manifest/block is missing.
    """

    manifest = load_yaml(Path(manifest_path))

    if not isinstance(manifest, dict):
        return None

    for b in manifest.get("blocks", []):

        if b.get("name") == block_name:

            b["artifact"] = str(artifact_path)

            save_yaml(Path(manifest_path), manifest)

            return manifest

    return None


def read_manifest(manifest_path):
    """Read a chain-manifest.yaml. Returns dict or {}."""

    manifest = load_yaml(Path(manifest_path))

    return manifest if isinstance(manifest, dict) else {}
