"""Tests for the release-tag-gate hook engine (PreToolUse, Bash tag pushes).

Runs a real temporary git repository: a tag is published only after the
release-gates marker (.release-gates/last-run.json) carries ok:true for the
current HEAD.
"""

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "release-tag-gate.py"

spec = importlib.util.spec_from_file_location("release_tag_gate", str(SCRIPT))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReleaseTagGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self._run("git", "init", "-q")
        self._run("git", "config", "user.email", "t@example.com")
        self._run("git", "config", "user.name", "t")
        (self.repo / "README.md").write_text("ok\n")
        self._run("git", "add", "README.md")
        self._run("git", "commit", "-q", "-m", "init")
        self._run("git", "tag", "v0.1.0")

    def _run(self, *args):
        return subprocess.run(args, cwd=self.repo, capture_output=True, text=True, check=True)

    def _write_marker(self, ok, sha=None):
        sha = sha or self._run("git", "rev-parse", "HEAD").stdout.strip()
        marker_dir = self.repo / ".release-gates"
        marker_dir.mkdir(exist_ok=True)
        (marker_dir / "last-run.json").write_text(
            json.dumps({"sha": sha, "ok": ok})
        )

    def _decide(self, command, cwd=None):
        return mod.decide(
            {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd or self.repo)}
        )

    def test_tag_push_without_marker_is_denied(self):
        self.assertEqual(self._decide("git push origin v0.1.0"), "deny")

    def test_marker_for_old_commit_does_not_satisfy(self):
        self._write_marker(ok=True, sha="0" * 40)
        self.assertEqual(self._decide("git push origin v0.1.0"), "deny")

    def test_marker_ok_false_does_not_satisfy(self):
        self._write_marker(ok=False)
        self.assertEqual(self._decide("git push origin v0.1.0"), "deny")

    def test_fresh_ok_marker_allows_the_push(self):
        self._write_marker(ok=True)
        self.assertEqual(self._decide("git push origin v0.1.0"), "check")

    def test_tags_flag_push_is_checked_on_the_same_terms(self):
        self.assertEqual(self._decide("git push origin --tags"), "deny")
        self._write_marker(ok=True)
        self.assertEqual(self._decide("git push origin --tags"), "check")

    def test_refs_tags_refspec_publishes_tags(self):
        self.assertEqual(self._decide("git push origin refs/tags/v0.1.0"), "deny")

    def test_branch_push_does_not_need_gates(self):
        self.assertIsNone(self._decide("git push origin main"))

    def test_local_tag_creation_is_not_publication(self):
        self.assertIsNone(self._decide("git tag v0.2.0"))

    def test_tag_list_is_not_publication(self):
        self.assertIsNone(self._decide("git tag -l"))

    def test_non_git_directory_fails_open(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(self._decide("git push origin --tags", cwd=plain))

    def test_compound_command_with_tag_push_is_gated(self):
        self.assertEqual(
            self._decide("npm test && git push origin v0.1.0"), "deny"
        )


if __name__ == "__main__":
    unittest.main()
