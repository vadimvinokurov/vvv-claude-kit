"""Tests for the SessionStart hook that loads the agent rules.

The plugin ships a SessionStart hook whose stdout (the rules file) Claude
Code adds to the session context. The rules live at
common_agent_rules.md in the plugin root.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOKS_JSON = REPO / "hooks" / "hooks.json"
RULES_FILE = REPO / "common_agent_rules.md"


class SessionStartWiringTests(unittest.TestCase):
    """hooks/hooks.json registers a SessionStart hook loading the rules."""

    def setUp(self):
        self.assertTrue(HOOKS_JSON.exists(), "hooks/hooks.json is missing")
        self.data = json.loads(HOOKS_JSON.read_text())

    def test_sessionstart_hook_is_registered(self):
        groups = self.data.get("hooks", {}).get("SessionStart", [])
        self.assertTrue(groups, "no SessionStart hook group in hooks.json")
        commands = []
        for group in groups:
            for hook in group.get("hooks", []):
                commands.append(hook.get("command", ""))
        self.assertTrue(
            any("${CLAUDE_PLUGIN_ROOT}" in cmd for cmd in commands),
            "SessionStart hook does not reference ${CLAUDE_PLUGIN_ROOT}",
        )

    def test_sessionstart_hook_references_existing_rules_file(self):
        groups = self.data.get("hooks", {}).get("SessionStart", [])
        commands = []
        for group in groups:
            for hook in group.get("hooks", []):
                commands.append(hook.get("command", ""))
        joined = " ".join(commands)
        self.assertIn("common_agent_rules.md", joined)

    def test_rules_file_exists_and_is_not_empty(self):
        self.assertTrue(
            RULES_FILE.exists(), "common_agent_rules.md is missing at the plugin root"
        )
        self.assertGreater(len(RULES_FILE.read_text().strip()), 0)


if __name__ == "__main__":
    unittest.main()
