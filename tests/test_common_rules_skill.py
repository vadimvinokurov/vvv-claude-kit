"""Tests for the common-rules skill migration.

The plugin's operating rules (formerly common_agent_rules.md at the
plugin root, injected by SessionStart hook) now live in the skill
skills/common-rules/SKILL.md. The skill is trigger-based: the injected
using-skills skill routes every conversation to it, and the SessionStart
hook injects only using-skills itself.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOKS_JSON = REPO / "hooks" / "hooks.json"
SKILL_FILE = REPO / "skills" / "common-rules" / "SKILL.md"
USING_SKILLS_FILE = REPO / "skills" / "using-skills" / "SKILL.md"
OLD_RULES_FILE = REPO / "common_agent_rules.md"


class HookInjectionTests(unittest.TestCase):
    """The SessionStart hook injects only the using-skills skill."""

    def setUp(self):
        self.assertTrue(HOOKS_JSON.exists(), "hooks/hooks.json is missing")
        self.data = json.loads(HOOKS_JSON.read_text())

    def sessionstart_commands(self):
        groups = self.data.get("hooks", {}).get("SessionStart", [])
        commands = []
        for group in groups:
            for hook in group.get("hooks", []):
                commands.append(hook.get("command", ""))
        return commands

    def test_sessionstart_hook_injects_using_skills(self):
        joined = " ".join(self.sessionstart_commands())
        self.assertIn("using-skills/SKILL.md", joined)

    def test_sessionstart_hook_does_not_inject_rules_file(self):
        joined = " ".join(self.sessionstart_commands())
        self.assertNotIn("common_agent_rules", joined)
        self.assertNotIn("common-rules", joined)


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


class UsingSkillsRoutingTests(unittest.TestCase):
    """using-skills hard-routes every conversation to common-rules."""

    def test_using_skills_routes_to_common_rules(self):
        self.assertTrue(USING_SKILLS_FILE.exists(), "using-skills/SKILL.md is missing")
        text = USING_SKILLS_FILE.read_text()
        self.assertIn("/common-rules", text)


if __name__ == "__main__":
    unittest.main()
