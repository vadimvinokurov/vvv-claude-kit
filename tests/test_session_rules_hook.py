"""Wiring tests for the session-rules injection (SessionStart hook).

Two SessionStart hooks inject the per-session rules into every session:
common-rules (operating policy) and token-economy (cost rules and the
spawn protocol). The rules are guaranteed present rather than
probabilistically triggered; no legacy files return.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SESSION_RULES = ["common-rules", "token-economy"]


class SessionStartInjectionTests(unittest.TestCase):
    """The SessionStart hooks inject the session-rules skills."""

    def setUp(self):
        hooks = REPO / "hooks" / "hooks.json"
        self.data = json.loads(hooks.read_text())

    def hooks_for(self, event):
        return [
            hook.get("command", "")
            for group in self.data["hooks"].get(event, [])
            for hook in group.get("hooks", [])
        ]

    def test_sessionstart_injects_session_rules(self):
        joined = " ".join(self.hooks_for("SessionStart"))
        for skill in SESSION_RULES:
            self.assertIn(f"skills/{skill}/SKILL.md", joined)

    def test_no_legacy_injections(self):
        joined = " ".join(self.hooks_for("SessionStart"))
        self.assertNotIn("using-skills", joined)
        self.assertNotIn("common_agent_rules", joined)

    def test_skill_files_exist(self):
        for skill in SESSION_RULES:
            self.assertTrue(
                (REPO / "skills" / skill / "SKILL.md").is_file(),
                f"skills/{skill}/SKILL.md is missing",
            )


if __name__ == "__main__":
    unittest.main()
