import json
import os
import tempfile
import unittest
from pathlib import Path

from core.github_stars_radar.config_helper import mcp_config, write_env, write_mcp_config
from core.github_stars_radar.env import load_env_file


class ConfigHelperTest(unittest.TestCase):
    def test_write_env_and_load_without_overriding_existing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = write_env(tmp, "test-token")
            old = os.environ.get("GITHUB_TOKEN")
            os.environ["GITHUB_TOKEN"] = "existing"
            try:
                loaded = load_env_file(env_path)
                self.assertEqual(os.environ["GITHUB_TOKEN"], "existing")
                self.assertIn("GITHUB_STARS_RADAR_DB", loaded)
            finally:
                if old is None:
                    os.environ.pop("GITHUB_TOKEN", None)
                else:
                    os.environ["GITHUB_TOKEN"] = old

    def test_write_mcp_config_uses_packaged_exe_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "github-stars-radar.exe").write_text("", encoding="utf-8")
            path = write_mcp_config(tmp)
            data = json.loads(path.read_text(encoding="utf-8"))
            server = data["mcpServers"]["github-stars-radar"]
            self.assertTrue(server["command"].endswith("github-stars-radar.exe"))
            self.assertEqual(server["args"], [])
            self.assertIn("GITHUB_STARS_RADAR_DB", server["env"])

    def test_write_mcp_config_uses_packaged_binary_without_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "github-stars-radar").write_text("", encoding="utf-8")
            path = write_mcp_config(tmp)
            data = json.loads(path.read_text(encoding="utf-8"))
            server = data["mcpServers"]["github-stars-radar"]
            self.assertTrue(server["command"].endswith("github-stars-radar"))
            self.assertEqual(server["args"], [])

    def test_source_mcp_config_falls_back_to_python_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = mcp_config(tmp)
            server = config["mcpServers"]["github-stars-radar"]
            self.assertEqual(server["command"], "py")
            self.assertTrue(server["args"][0].endswith(str(Path("mcp-server") / "server.py")))


if __name__ == "__main__":
    unittest.main()
