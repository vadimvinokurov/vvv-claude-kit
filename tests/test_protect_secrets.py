"""Tests for the secrets-protection hook engine.

The hook script lives at scripts/protect-secrets.py. It is a Claude Code
PreToolUse hook: it reads the hook JSON payload from stdin and either
allows the tool call (silently, exit 0) or denies it (JSON decision on
stdout, exit 0).

Protected names (approved design, 2026-11-07):
- files: `.env`, `.env.*`, `*.pem`, `*.key` (any path segment)
- dirs:  `.secrets`, `.secret` (segment itself and everything inside it)
- always allowed: basenames ending in `.example` or `.template` (e.g. `.env.example`)
- `.leng-signing` is explicitly NOT protected.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "protect-secrets.py"
HOOKS_JSON = REPO / "hooks" / "hooks.json"


def load_engine():
    spec = importlib.util.spec_from_file_location("protect_secrets", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def payload(tool_name, tool_input, cwd="/repo/work"):
    return {"tool_name": tool_name, "tool_input": tool_input, "cwd": cwd}


def decide(mod, *args, **kwargs):
    return mod.decide(payload(*args, **kwargs))


def deny(decision):
    return decision.get("decision") == "deny"


class EnginePathTests(unittest.TestCase):
    """decide() on the file-giving tools."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_engine()

    def test_read_dotenv_at_root_is_denied(self):
        result = decide(self.mod, "Read", {"file_path": "/repo/work/.env"})
        self.assertTrue(deny(result), result)

    def test_read_dotenv_in_subdirectory_is_denied(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/packages/app/.env"}
        )
        self.assertTrue(deny(result), result)

    def test_read_dotenv_variants_are_denied(self):
        for name in (".env.local", ".env.production", ".env.development"):
            result = decide(self.mod, "Read", {"file_path": f"/repo/work/{name}"})
            self.assertTrue(deny(result), f"{name}: {result}")

    def test_read_dotenv_example_is_allowed(self):
        result = decide(self.mod, "Read", {"file_path": "/repo/work/.env.example"})
        self.assertFalse(deny(result), result)

    def test_read_dotenv_template_is_allowed(self):
        result = decide(self.mod, "Read", {"file_path": "/repo/work/.env.template"})
        self.assertFalse(deny(result), result)

    def test_read_envrc_is_allowed(self):
        # .envrc is not on the protected list (approved design).
        result = decide(self.mod, "Read", {"file_path": "/repo/work/.envrc"})
        self.assertFalse(deny(result), result)

    def test_read_pem_and_key_files_are_denied(self):
        for p in ("/repo/work/server.pem", "/repo/work/deploy/secret.key"):
            result = decide(self.mod, "Read", {"file_path": p})
            self.assertTrue(deny(result), f"{p}: {result}")

    def test_read_key_example_is_allowed(self):
        result = decide(self.mod, "Read", {"file_path": "/repo/work/server.key.example"})
        self.assertFalse(deny(result), result)

    def test_read_inside_secrets_folder_is_denied(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/.secrets/db/creds.txt"}
        )
        self.assertTrue(deny(result), result)

    def test_read_secret_singular_folder_is_denied(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/.secret/token"}
        )
        self.assertTrue(deny(result), result)

    def test_path_traversal_into_dotenv_is_denied(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/packages/app/../../.env"}
        )
        self.assertTrue(deny(result), result)

    def test_leng_signing_folder_is_not_protected(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/.leng-signing/x.p12"}
        )
        self.assertFalse(deny(result), result)

    def test_ordinary_config_file_is_allowed(self):
        result = decide(
            self.mod, "Read", {"file_path": "/repo/work/config/environment.json"}
        )
        self.assertFalse(deny(result), result)

    def test_relative_path_dotenv_is_denied(self):
        result = decide(self.mod, "Read", {"file_path": "conf/.env"})
        self.assertTrue(deny(result), result)

    def test_write_dotenv_is_denied(self):
        result = decide(self.mod, "Write", {"file_path": "/repo/work/.env", "content": "A=1"})
        self.assertTrue(deny(result), result)

    def test_edit_dotenv_is_denied(self):
        result = decide(self.mod, "Edit", {"file_path": "/repo/work/.env"})
        self.assertTrue(deny(result), result)

    def test_grep_inside_secrets_folder_is_denied(self):
        result = decide(
            self.mod, "Grep", {"pattern": "token", "path": "/repo/work/.secrets"}
        )
        self.assertTrue(deny(result), result)

    def test_grep_pattern_targeting_dotenv_is_denied(self):
        result = decide(self.mod, "Grep", {"pattern": r"\.env", "path": "/repo/work"})
        self.assertTrue(deny(result), result)

    def test_grep_ordinary_search_is_allowed(self):
        result = decide(self.mod, "Grep", {"pattern": "TODO", "path": "/repo/work/src"})
        self.assertFalse(deny(result), result)

    def test_glob_selecting_dotenv_files_is_denied(self):
        result = decide(self.mod, "Glob", {"pattern": "**/.env*", "path": "/repo/work"})
        self.assertTrue(deny(result), result)

    def test_glob_in_secrets_folder_is_denied(self):
        result = decide(self.mod, "Glob", {"pattern": "*", "path": "/repo/work/.secrets"})
        self.assertTrue(deny(result), result)

    def test_glob_ordinary_is_allowed(self):
        result = decide(self.mod, "Glob", {"pattern": "src/**/*.ts", "path": "/repo/work"})
        self.assertFalse(deny(result), result)

    def test_other_tool_names_are_allowed(self):
        result = decide(
            self.mod, "WebFetch", {"url": "file:///repo/work/.env"}
        )
        self.assertFalse(deny(result), result)


class EngineBashTests(unittest.TestCase):
    """decide() on Bash tool calls."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_engine()

    def test_cat_dotenv_is_denied(self):
        result = decide(self.mod, "Bash", {"command": "cat .env"})
        self.assertTrue(deny(result), result)

    def test_cat_dotenv_variant_is_denied(self):
        result = decide(self.mod, "Bash", {"command": "cat .env.local"})
        self.assertTrue(deny(result), result)

    def test_cat_dotenv_example_is_allowed(self):
        result = decide(self.mod, "Bash", {"command": "cat .env.example"})
        self.assertFalse(deny(result), result)

    def test_cat_nested_dotenv_is_denied(self):
        result = decide(self.mod, "Bash", {"command": "cat packages/app/.env"})
        self.assertTrue(deny(result), result)

    def test_grep_inside_secrets_folder_is_denied(self):
        result = decide(self.mod, "Bash", {"command": "grep -r token .secrets/"})
        self.assertTrue(deny(result), result)

    def test_env_file_flag_is_denied(self):
        result = decide(
            self.mod, "Bash", {"command": "npm --env-file=.env run build"}
        )
        self.assertTrue(deny(result), result)

    def test_filename_ending_in_env_plain_is_allowed(self):
        # `app.env` is not `.env` / `.env.*` — not on the protected list.
        result = decide(self.mod, "Bash", {"command": "cat app.env"})
        self.assertFalse(deny(result), result)

    def test_quoted_dotenv_arg_is_denied(self):
        result = decide(self.mod, "Bash", {"command": 'cat ".env"'})
        self.assertTrue(deny(result), result)

    def test_non_git_pipeline_referencing_dotenv_is_denied(self):
        result = decide(self.mod, "Bash", {"command": "ls || cat .env"})
        self.assertTrue(deny(result), result)

    def test_dotenv_word_inside_longer_word_is_not_denied(self):
        # `.environment` is not `.env` — no substring match.
        result = decide(self.mod, "Bash", {"command": "cat .environment"})
        self.assertFalse(deny(result), result)

    def test_command_with_no_secret_reference_is_allowed(self):
        result = decide(self.mod, "Bash", {"command": "npm test"})
        self.assertFalse(deny(result), result)


class EngineGitTests(unittest.TestCase):
    """decide() on git add/commit: check the real index, not command text.

    Runs a real temporary git repository.
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = load_engine()

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
        (self.repo / ".env").write_text("SECRET=1\n")
        (self.repo / "src.txt").write_text("ok\n")

    def _run(self, *args):
        return subprocess.run(
            args, cwd=self.repo, capture_output=True, text=True, check=True
        )

    def _decision(self, command):
        return self.mod.decide(payload("Bash", {"command": command}, cwd=str(self.repo)))

    def test_git_add_dotenv_is_denied(self):
        self.assertTrue(deny(self._decision("git add .env")), self._decision("git add .env"))

    def test_git_add_ordinary_file_is_allowed(self):
        result = self._decision("git add src.txt")
        self.assertFalse(deny(result), result)

    def test_staged_dotenv_makes_git_commit_denied(self):
        self._run("git", "add", ".env")
        result = self._decision('git commit -m "clean up"')
        self.assertTrue(deny(result), result)

    def test_commit_without_staged_secrets_is_allowed_even_if_message_mentions_dotenv(self):
        # The commit message may legitimately mention .env; only the index matters.
        self._run("git", "add", "src.txt")
        result = self._decision('git commit -m "stop reading .env in examples"')
        self.assertFalse(deny(result), result)

    def test_git_add_dotenv_example_is_allowed(self):
        (self.repo / ".env.example").write_text("A=\n")
        result = self._decision("git add .env.example")
        self.assertFalse(deny(result), result)

    def test_git_stash_with_staged_dotenv_is_denied(self):
        self._run("git", "add", ".env")
        result = self._decision("git stash -u")
        self.assertTrue(deny(result), result)

    def test_git_add_wildcard_denies_untracked_dotenv(self):
        result = self._decision("git add .")
        self.assertTrue(deny(result), result)

    def test_git_add_wildcard_allows_only_example_change(self):
        (self.repo / ".env.example").write_text("A=\n")
        result = self._decision("git add .env.example")
        self.assertFalse(deny(result), result)

    def test_git_commit_all_with_modified_tracked_dotenv_is_denied(self):
        self._run("git", "add", ".env")
        self._run("git", "commit", "-q", "-m", "add env")
        (self.repo / ".env").write_text("SECRET=2\n")
        result = self._decision('git commit -a -m "update"')
        self.assertTrue(deny(result), result)


class IndexScanTests(unittest.TestCase):
    """The porcelain scanner used for git add/commit decisions."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_engine()

    def test_detects_dotenv_in_status_output(self):
        out = "?? .env\nM  README.md\n"
        self.assertTrue(self.mod.index_has_protected_files(out))

    def test_ignores_dotenv_example(self):
        out = "?? .env.example\n"
        self.assertFalse(self.mod.index_has_protected_files(out))

    def test_detects_secrets_folder_path(self):
        out = "?? path/to/.secrets/db.txt\n"
        self.assertTrue(self.mod.index_has_protected_files(out))

    def test_ignores_ordinary_paths(self):
        out = "M  src/main.ts\n?? notes.txt\n"
        self.assertFalse(self.mod.index_has_protected_files(out))


class ScriptEndToEndTests(unittest.TestCase):
    """The script itself: stdin JSON in, decision JSON or silence out."""

    def run_script(self, stdin_text):
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=stdin_text,
            capture_output=True,
            text=True,
        )

    def test_deny_payload_produces_decision_json(self):
        payload = {"tool_name": "Read", "tool_input": {"file_path": "/repo/.env"}}
        proc = self.run_script(json.dumps(payload))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(
            out["hookSpecificOutput"]["permissionDecision"], "deny"
        )
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_allow_payload_produces_no_output(self):
        payload = {"tool_name": "Read", "tool_input": {"file_path": "/repo/README.md"}}
        proc = self.run_script(json.dumps(payload))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_malformed_stdin_fails_open_silently(self):
        proc = self.run_script("not json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "")


class WiringTests(unittest.TestCase):
    """hooks/hooks.json points at the script with the right matcher."""

    def test_hooks_json_registers_pretooluse_hook(self):
        self.assertTrue(HOOKS_JSON.exists(), "hooks/hooks.json is missing")
        data = json.loads(HOOKS_JSON.read_text())
        groups = data.get("hooks", {}).get("PreToolUse", [])
        matchers = [g.get("matcher", "") for g in groups]
        joined = "|".join(matchers)
        for tool in ("Read", "Grep", "Glob", "Write", "Edit", "Bash"):
            self.assertIn(tool, joined)
        for group in groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                self.assertIn("${CLAUDE_PLUGIN_ROOT}", cmd)
                script_ref = cmd.replace('"', "").strip().replace(
                    "${CLAUDE_PLUGIN_ROOT}", str(REPO)
                )
                self.assertTrue(
                    Path(script_ref).exists(),
                    f"hook command references a missing file: {cmd}",
                )


if __name__ == "__main__":
    unittest.main()
