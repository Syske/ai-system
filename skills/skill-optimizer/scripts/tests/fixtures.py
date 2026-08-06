#!/usr/bin/env python3
"""Shared test fixtures for skill-optimizer (stdlib unittest).

No pytest / external deps required. Run:
    python -m unittest discover -s tests -v
    (from the scripts/ directory)
"""

import json
import pathlib
import sys
import tempfile
import types
import unittest

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def make_core_stub():
    """Stub the `core` module so actions/mutator import without a live LLM."""
    core_stub = types.ModuleType("core")

    class RealLLMClient:
        def __init__(self):
            pass

        def __call__(self, prompt):
            return "stub response"

    core_stub.RealLLMClient = RealLLMClient
    sys.modules["core"] = core_stub
    return core_stub


class FakeMsg:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeChoice:
    def __init__(self, msg):
        self.message = msg


class FakeResp:
    def __init__(self, msg):
        self.choices = [FakeChoice(msg)]


class FakeLLM:
    """Scriptable fake: each call returns the next queued response, or a
    canned tool-call sequence on the first call."""

    def __init__(self, first_tool_calls=None, then_text="Done."):
        self.calls = 0
        self.saw_tools = None
        self.first_tool_calls = first_tool_calls or []
        self.then_text = then_text

    def chat(self, messages, tools=None, temperature=0.2):
        self.calls += 1
        self.saw_tools = tools
        if self.calls == 1 and self.first_tool_calls:
            return FakeResp(FakeMsg("", self.first_tool_calls))
        return FakeResp(FakeMsg(self.then_text))


def make_tool_call(name, arguments):
    return types.SimpleNamespace(
        id=f"call_{name}",
        type="function",
        function=types.SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def make_skill_dir(root=None, frontmatter=True):
    d = pathlib.Path(root or tempfile.mkdtemp())
    skill_dir = d / "test-skill"
    skill_dir.mkdir(exist_ok=True)
    body = (
        "---\nname: test-skill\n---\n\n# Test Skill\n\nSome body.\n"
        if frontmatter
        else "# Test Skill\n\nNo frontmatter.\n"
    )
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return skill_dir


if __name__ == "__main__":
    unittest.main()
