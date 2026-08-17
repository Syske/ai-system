#!/usr/bin/env python3
"""Tests for the native agentic mutation loop (P12 rewrite).

Verifies: tool-call parsing, chunk assembly, changelog recording,
missing-chunk retry, and fallback-to-parent on incomplete output.
"""

import sys
import unittest

from fixtures import (
    FakeLLM,
    FakeMsg,
    FakeResp,
    make_tool_call,
    SCRIPTS_DIR,  # noqa: F401
)
from engine.mutator import DiagnosticMutator

import architecture.genome as genome_mod


def make_parent(name="demo"):
    return genome_mod.SkillGenome.from_markdown(
        f"---\nname: {name}\n---\n\n# Demo\n\nOriginal body.\n"
    )


class TestAgenticMutationLoop(unittest.TestCase):
    def test_single_chunk_write_and_record_fix(self):
        fake = FakeLLM(
            first_tool_calls=[
                make_tool_call(
                    "write_file_chunk",
                    {
                        "path": "SKILL.md",
                        "index": 1,
                        "total": 1,
                        "content": "---\nname: demo\n---\n\n# Demo\n\nFixed content.\n",
                    },
                ),
                make_tool_call(
                    "record_fix",
                    {
                        "diagnosis_index": 1,
                        "description": "fixed body",
                        "changed_sections": "Body",
                    },
                ),
            ],
            then_text="Done fixing.",
        )
        mutator = DiagnosticMutator(model_client=fake)
        result = mutator._mutate_with_tools(make_parent(), "Fix body")
        self.assertEqual(len(result), 1)
        self.assertIn("Fixed content", result[0].raw_text)
        self.assertEqual(len(result[0].changelog), 1)
        self.assertEqual(result[0].changelog[0]["diagnosis_index"], "1")

    def test_multiple_chunks_assembled_in_order(self):
        fake = FakeLLM(
            first_tool_calls=[
                make_tool_call(
                    "write_file_chunk",
                    {
                        "path": "SKILL.md",
                        "index": 1,
                        "total": 2,
                        "content": "---\nname: demo\n---\n\n# Demo\n\nPart ONE.",
                    },
                ),
                make_tool_call(
                    "write_file_chunk",
                    {
                        "path": "SKILL.md",
                        "index": 2,
                        "total": 2,
                        "content": "Part TWO.\n",
                    },
                ),
            ],
            then_text="Done.",
        )
        mutator = DiagnosticMutator(model_client=fake)
        result = mutator._mutate_with_tools(make_parent(), "Fix")
        self.assertEqual(len(result), 1)
        self.assertIn("Part ONE.Part TWO.", result[0].raw_text)

    def test_unknown_tool_returns_error_not_crash(self):
        fake = FakeLLM(
            first_tool_calls=[
                make_tool_call("nonexistent_tool", {"a": 1}),
            ],
            then_text="Done.",
        )
        mutator = DiagnosticMutator(model_client=fake)
        result = mutator._mutate_with_tools(make_parent(), "Fix")
        # unknown tool -> error recorded, loop continues to text turn
        self.assertEqual(len(result), 1)
        self.assertIn("Original body", result[0].raw_text)

    def test_no_skill_chunks_falls_back_to_parent(self):
        fake = FakeLLM(
            first_tool_calls=[
                make_tool_call(
                    "record_fix",
                    {
                        "diagnosis_index": 1,
                        "description": "x",
                        "changed_sections": "Body",
                    },
                ),
            ],
            then_text="I did nothing.",
        )
        mutator = DiagnosticMutator(model_client=fake)
        result = mutator._mutate_with_tools(make_parent(), "Fix")
        # no SKILL.md chunks written -> parent fallback
        self.assertEqual(len(result), 1)
        self.assertIn("Original body", result[0].raw_text)

    def test_bounded_edits_caps_diagnoses(self):
        # Q1: SKILL_OPT_MUTATOR_MAX_DIAGNOSES caps how many diagnoses are
        # addressed in one mutation round.
        import os
        from architecture.scoring import Diagnosis

        old = os.environ.get("SKILL_OPT_MUTATOR_MAX_DIAGNOSES")
        os.environ["SKILL_OPT_MUTATOR_MAX_DIAGNOSES"] = "2"
        try:
            fake = FakeLLM(then_text="Done.")
            mutator = DiagnosticMutator(model_client=fake)
            diags = [
                Diagnosis(dimension="structure", issue_type="t", severity="high",
                          description=f"issue {i}", evidence="e")
                for i in range(5)
            ]
            result = mutator.mutate(make_parent(), diags)
            self.assertEqual(len(result), 1)
        finally:
            if old is None:
                os.environ.pop("SKILL_OPT_MUTATOR_MAX_DIAGNOSES", None)
            else:
                os.environ["SKILL_OPT_MUTATOR_MAX_DIAGNOSES"] = old

    def test_no_cap_by_default(self):
        from architecture.scoring import Diagnosis

        fake = FakeLLM(then_text="Done.")
        mutator = DiagnosticMutator(model_client=fake)
        diags = [
            Diagnosis(dimension="structure", issue_type="t", severity="high",
                      description=f"issue {i}", evidence="e")
            for i in range(5)
        ]
        result = mutator.mutate(make_parent(), diags)
        self.assertEqual(len(result), 1)  # no exception; cap off

    def test_legacy_path_when_no_chat(self):
        class PlainCallable:
            def __call__(self, prompt, system=None):
                class R:
                    content = "---\nname: demo\n---\n\n# Demo\n\nLegacy fix.\n"
                return R()

        from architecture.scoring import Diagnosis

        mutator = DiagnosticMutator(model_client=PlainCallable())
        diag = Diagnosis(
            dimension="structure", issue_type="layout", severity="high",
            description="body too short", evidence="body",
            suggested_fix="expand body",
        )
        result = mutator.mutate(make_parent(), [diag])
        self.assertEqual(len(result), 1)
        self.assertIn("Legacy fix", result[0].raw_text)


if __name__ == "__main__":
    unittest.main()
