import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_release_notes.py"
SPEC = importlib.util.spec_from_file_location("generate_release_notes", MODULE_PATH)
generate_release_notes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generate_release_notes)


class GenerateReleaseNotesTests(unittest.TestCase):
    def test_render_uses_github_like_fallback_style(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "notes.md"
            with (
                mock.patch.object(generate_release_notes, "previous_tag", return_value="v0.1.1"),
                mock.patch.object(
                    generate_release_notes,
                    "commit_lines",
                    return_value=[
                        ("83e394e", "fix: split star and readme sync"),
                        ("121fc90", "ci: support release notes for existing tags"),
                    ],
                ),
                mock.patch.object(generate_release_notes, "repo_url", return_value="https://github.com/example/project"),
            ):
                generate_release_notes.render("0.1.2", output, "HEAD")

            text = output.read_text(encoding="utf-8")

        self.assertIn("## What's Changed\n\n", text)
        self.assertIn("* fix: split star and readme sync ([83e394e](https://github.com/example/project/commit/83e394e))", text)
        self.assertIn("* ci: support release notes for existing tags ([121fc90](https://github.com/example/project/commit/121fc90))", text)
        self.assertIn("**Full Changelog**: https://github.com/example/project/compare/v0.1.1...v0.1.2", text)
        self.assertNotIn("### Fixes", text)
        self.assertNotIn("## Release Assets", text)


if __name__ == "__main__":
    unittest.main()
