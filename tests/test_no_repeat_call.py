"""Tests for the no-repeat-call hook engine (PostToolUse, Bash)."""

import importlib.util
import json
import os
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "no-repeat-call.py")

spec = importlib.util.spec_from_file_location("no_repeat_call", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def payload(command, response, session="s1"):
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_response": response,
        "session_id": session,
    }


class NoRepeatTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.saved = mod.STATE_DIR
        mod.STATE_DIR = self.dir

    def tearDown(self):
        mod.STATE_DIR = self.saved

    def call(self, command, response, session="s1"):
        return mod.decide(payload(command, response, session))

    def test_first_run_is_silent(self):
        self.assertIsNone(self.call("npm test", {"stdout": "3 passed"}))

    def test_identical_rerun_is_flagged(self):
        self.call("npm test", {"stdout": "3 passed"})
        self.assertIn("no new information", self.call("npm test", {"stdout": "3 passed"}))

    def test_changed_output_resets_and_is_silent(self):
        self.call("npm test", {"stdout": "3 passed"})
        self.assertIsNone(self.call("npm test", {"stdout": "5 passed\nFAIL"}))
        # the new output's rerun is now the flagged one
        self.assertIn(
            "no new information", self.call("npm test", {"stdout": "5 passed\nFAIL"})
        )

    def test_changed_command_resets(self):
        self.call("npm test", {"stdout": "3 passed"})
        self.assertIsNone(self.call("npm run lint", {"stdout": "3 passed"}))

    def test_non_bash_tool_is_ignored(self):
        p = {"tool_name": "Read", "tool_input": {"file_path": "x.py"},
             "tool_response": {"stdout": "x"}, "session_id": "s1"}
        self.assertIsNone(mod.decide(p))

    def test_malformed_payload_is_silent(self):
        self.assertIsNone(mod.decide({"tool_name": "Bash", "tool_input": {}}))

    def test_sessions_are_isolated(self):
        self.call("npm test", {"stdout": "3 passed"}, session="a")
        self.assertIsNone(self.call("npm test", {"stdout": "3 passed"}, session="b"))


class ScriptEndToEndTests(unittest.TestCase):
    def run_script(self, stdin_text):
        import subprocess
        import sys
        return subprocess.run(
            [sys.executable, SCRIPT], input=stdin_text,
            capture_output=True, text=True,
        )

    def test_repeat_produces_additional_context(self):
        env = dict(os.environ, TMPDIR=tempfile.mkdtemp())
        with_two = json.dumps(payload("cd /x && make", {"stdout": "fail"}))
        import subprocess
        import sys
        for _ in range(2):
            proc = subprocess.run(
                [sys.executable, SCRIPT], input=with_two,
                capture_output=True, text=True, env=env,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("no new information", out["hookSpecificOutput"]["additionalContext"])

    def test_malformed_stdin_fail_opens(self):
        proc = self.run_script("not json")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")


if __name__ == "__main__":
    unittest.main()
