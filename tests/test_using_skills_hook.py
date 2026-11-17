"""Wiring tests for the using-skills injection (SessionStart hook).

Mirrors superpowers: a SessionStart hook injects the using-skills skill
content every session, so the generic skill mandate (and the hard routes
to this plugin's skills, including /common-rules) lives in the injected
content. The hook injects only using-skills; the operating rules live in
the trigger-based common-rules skill.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOKS_JSON = REPO / "hooks" / "hooks.json"
SKILL_FILE = REPO / "skills" / "using-skills" / "SKILL.md"


def sessionstart_commands():
    data = json.loads(HOOKS_JSON.read_text())
    commands = []
    for group in data.get("hooks", {}).get("SessionStart", []):
        for hook in group.get("hooks", []):
            commands.append(hook.get("command", ""))
    return commands


class UsingSkillsInjectionTests(unittest.TestCase):
    def test_skill_file_exists_and_is_not_empty(self):
        self.assertTrue(SKILL_FILE.exists(), "skills/using-skills/SKILL.md is missing")
        self.assertGreater(SKILL_FILE.stat().st_size, 0, "SKILL.md is empty")

    def test_skill_has_valid_frontmatter(self):
        text = SKILL_FILE.read_text()
        self.assertTrue(text.startswith("---"), "SKILL.md has no frontmatter")
        self.assertIn("name: using-skills", text)
        self.assertIn("description:", text)

    def test_sessionstart_hook_injects_using_skills(self):
        joined = " ".join(sessionstart_commands())
        self.assertIn("using-skills/SKILL.md", joined,
                      "SessionStart hook does not inject skills/using-skills/SKILL.md")

    def test_sessionstart_hook_injects_only_using_skills(self):
        commands = [c for c in sessionstart_commands() if c.strip()]
        self.assertEqual(
            commands,
            ['cat "${CLAUDE_PLUGIN_ROOT}/skills/using-skills/SKILL.md"'],
            "SessionStart hook should inject only skills/using-skills/SKILL.md")


class SkillMandateContentTests(unittest.TestCase):
    """The injected content carries the mandates once kept in the rules."""

    def setUp(self):
        text = SKILL_FILE.read_text()
        self.assertIn("1% chance", text,
                      "using-skills lacks the even-1%-chance invocation mandate")
        self.assertIn("/building-testable-apps", text,
                      "using-skills does not hard-route to /building-testable-apps")
        self.assertIn("test-driven-development", text,
                      "using-skills does not carry the TDD mandate")
        self.assertIn("subagent", text.lower(),
                      "using-skills lacks the subagent exemption")

    def test_using_skills_routes_to_common_rules(self):
        text = SKILL_FILE.read_text()
        self.assertIn("/common-rules", text,
                      "using-skills does not hard-route every conversation to /common-rules")


if __name__ == "__main__":
    unittest.main()
