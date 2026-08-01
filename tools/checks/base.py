"""Shared infrastructure for check submodules."""

from pathlib import Path

HERE = Path(__file__).resolve().parents[1]

ROOT = HERE.parent


class Checker:

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load_yaml(path):
    import yaml

    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        return {"__error__": str(exc)}
