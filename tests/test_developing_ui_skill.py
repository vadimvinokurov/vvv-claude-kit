"""Wiring tests for the developing-ui skill (plugin rule 7).

The agent rules reference the /developing-ui skill; the skill must exist
in the plugin with the expected contents.
"""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RULES_FILE = REPO / "common_agent_rules.md"
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

    def test_rules_reference_the_skill(self):
        if not RULES_FILE.exists():
            self.skipTest("rules file missing")
        text = RULES_FILE.read_text()
        self.assertIn("/developing-ui", text, "rules do not reference /developing-ui")
        self.assertNotIn("/ui-verify-loop", text, "stale /ui-verify-loop reference")


if __name__ == "__main__":
    unittest.main()
