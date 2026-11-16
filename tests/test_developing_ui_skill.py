"""Wiring tests for the developing-ui skill.

The using-skills SessionStart injection hard-routes /developing-ui (see
tests/test_using_skills_hook.py); the skill itself must exist in the
plugin with the expected contents.
"""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_FILE = REPO / "skills" / "developing-ui" / "SKILL.md"


class DevelopingUiSkillTests(unittest.TestCase):
    def test_skill_file_exists_and_is_not_empty(self):
        self.assertTrue(SKILL_FILE.exists(), "skills/developing-ui/SKILL.md is missing")
        self.assertGreater(SKILL_FILE.stat().st_size, 0, "SKILL.md is empty")

    def test_skill_has_valid_frontmatter(self):
        if not SKILL_FILE.exists():
            self.skipTest("skill file missing")
        text = SKILL_FILE.read_text()
        self.assertTrue(text.startswith("---"), "SKILL.md has no frontmatter")
        self.assertIn("name: developing-ui", text)
        self.assertIn("description:", text)

    def test_skill_frontmatter_triggers_on_ui_requests(self):
        if not SKILL_FILE.exists():
            self.skipTest("skill file missing")
        text = SKILL_FILE.read_text()
        self.assertIn("description:", text)
        self.assertIn("UI", text)


if __name__ == "__main__":
    unittest.main()
