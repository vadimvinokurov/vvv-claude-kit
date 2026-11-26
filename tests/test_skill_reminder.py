"""Tests for the skill-reminder hook engine (PreToolUse, path tools)."""

import importlib.util
import unittest

REPO = os_dir = __import__("pathlib").Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "skill-reminder.py"

spec = importlib.util.spec_from_file_location("skill_reminder", str(SCRIPT))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def decide(tool_input, tool_name="Edit"):
    return mod.decide({"tool_name": tool_name, "tool_input": tool_input})


class SkillReminderTests(unittest.TestCase):
    def test_edit_in_ui_dir_reminds(self):
        line = decide({"file_path": "/proj/ui/src/panel.ts"})
        self.assertIn("ui-development", line)
        self.assertIn("token-economy", line)

    def test_edit_in_ui_design_dir_reminds(self):
        self.assertIn("ui-development", decide({"file_path": "ui_design/ui_components/btn.ts"}))

    def test_write_in_frontend_dir_reminds(self):
        self.assertIn("ui-development", decide({"tool_name": "Write", "file_path": "/x/frontend/app.tsx"}))

    def test_non_ui_path_is_silent(self):
        self.assertIsNone(decide({"file_path": "/proj/core/parser.rs"}))

    def test_read_is_checked_too(self):
        self.assertIn("ui-development", decide({"file_path": "/proj/gui/main.py"}, "Read"))

    def test_segment_must_match_whole_component(self):
        # `gui` matches; `guidance` does not.
        self.assertIsNone(decide({"file_path": "/proj/guidance/x.ts"}))

    def test_no_path_input_is_silent(self):
        self.assertIsNone(decide({"pattern": "ui"}))

    def test_custom_mapping_entry(self):
        # agent-brief is in the shipped mapping (subagent-contract).
        line = mod.reminder_for("/repo/docs/notes/agent-brief.md")
        self.assertIn("subagent-contract", line)

    def test_new_reminder_entries(self):
        self.assertIn("golden-rebaseline", mod.reminder_for("/app/renders/btn.png"))
        self.assertIn("release-gates", mod.reminder_for("/repo/.release-gates/last-run.json"))

    def test_unmapped_path_is_silent(self):
        self.assertIsNone(mod.reminder_for("/repo/src/utils.py"))


if __name__ == "__main__":
    unittest.main()
