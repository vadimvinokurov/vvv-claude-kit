"""Tests for the common-rules skill migration.

The plugin's operating rules (formerly common_agent_rules.md at the
plugin root, injected by SessionStart hook) live in the trigger-based
skill skills/common-rules/SKILL.md. The using-skills mandate and its
SessionStart hook were removed; the skill triggers by its description
at conversation start.
"""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_FILE = REPO / "skills" / "common-rules" / "SKILL.md"
OLD_RULES_FILE = REPO / "common_agent_rules.md"


class CommonRulesSkillTests(unittest.TestCase):
    """The rules live as the trigger-based common-rules skill."""

    def test_skill_file_exists_and_is_not_empty(self):
        self.assertTrue(
            SKILL_FILE.exists(), "skills/common-rules/SKILL.md is missing"
        )
        body = SKILL_FILE.read_text().strip()
        self.assertGreater(len(body), 0)

    def test_frontmatter_has_name_and_description(self):
        self.assertTrue(SKILL_FILE.exists(), "skills/common-rules/SKILL.md is missing")
        text = SKILL_FILE.read_text()
        self.assertTrue(text.startswith("---"), "SKILL.md lacks frontmatter")
        fm = text.split("---", 2)[1]
        self.assertIn("name: common-rules", fm)
        self.assertIn("description:", fm)

    def test_old_rules_file_is_removed(self):
        self.assertFalse(
            OLD_RULES_FILE.exists(),
            "common_agent_rules.md should be deleted after the migration"
        )


if __name__ == "__main__":
    unittest.main()
