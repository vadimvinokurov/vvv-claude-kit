"""Tests for the shell-edit-limit hook engine (PreToolUse, Bash)."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "shell-edit-limit.py"

spec = importlib.util.spec_from_file_location("shell_edit_limit", str(SCRIPT))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ShellEditLimitTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.saved = mod.STATE_DIR
        mod.STATE_DIR = self.dir
        (Path(self.dir) / "app.py").write_text("x = 1\n")
        self.cwd = self.dir
        self.session = "s1"

    def tearDown(self):
        mod.STATE_DIR = self.saved

    def hit(self, command):
        return mod.count_and_decide(command, self.cwd, self.session)

    def denied(self, result):
        return result is not None and result.get("decision") == "deny"

    def test_first_sed_edit_is_allowed(self):
        self.assertIsNone(self.hit(f"sed -i 's/1/2/' {self.dir}/app.py"))

    def test_second_is_allowed_third_is_denied(self):
        self.hit(f"sed -i 's/1/2/' {self.dir}/app.py")
        self.assertIsNone(self.hit(f"sed -i 's/2/3/' {self.dir}/app.py"))
        self.assertTrue(self.denied(self.hit(f"sed -i 's/3/4/' {self.dir}/app.py")))

    def test_denial_names_editing_tools(self):
        self.hit(f"sed -i 's/1/2/' {self.dir}/app.py")
        self.hit(f"sed -i 's/2/3/' {self.dir}/app.py")
        result = self.hit(f"sed -i 's/3/4/' {self.dir}/app.py")
        self.assertIn("Write/Edit", result["reason"])

    def test_redirect_to_existing_file_counts(self):
        self.hit(f"echo hi > {self.dir}/app.py")
        self.hit(f"echo hi2 > {self.dir}/app.py")
        self.assertTrue(self.denied(self.hit(f"echo hi3 > {self.dir}/app.py")))

    def test_creating_new_file_via_redirect_is_allowed_forever(self):
        for i in range(5):
            self.assertIsNone(self.hit(f"echo x > {self.dir}/new_{i}.py"))

    def test_reading_is_not_counted(self):
        for _ in range(5):
            self.assertIsNone(self.hit(f"cat {self.dir}/app.py"))

    def test_allowlist_bypasses_the_limit(self):
        os.mkdir(os.path.join(self.dir, ".claude"))
        with open(os.path.join(self.dir, ".claude", "shell-edits-allowlist"), "w") as f:
            f.write("app.py\n")
        for i in range(5):
            self.assertIsNone(self.hit(f"sed -i 's/{i}/{i+1}/' {self.dir}/app.py"))

    def test_tee_to_existing_file_counts(self):
        self.hit(f"echo a | tee {self.dir}/app.py")
        self.hit(f"echo b | tee {self.dir}/app.py")
        self.assertTrue(self.denied(self.hit(f"echo c | tee {self.dir}/app.py")))

    def test_sessions_are_isolated(self):
        self.hit(f"sed -i 's/1/2/' {self.dir}/app.py")
        old = self.session
        self.session = "s2"
        self.assertIsNone(self.hit(f"sed -i 's/1/2/' {self.dir}/app.py"))
        self.session = old


if __name__ == "__main__":
    unittest.main()
