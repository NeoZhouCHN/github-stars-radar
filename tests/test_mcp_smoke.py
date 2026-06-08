import json
import os
import subprocess
import sys
import tempfile
import unittest

from core.github_stars_radar.mcp import build_tool_list, call_tool
from core.github_stars_radar.service import StarsRadarService


class FakeGitHubClient:
    def list_starred_repos(self):
        return [
            {
                "id": 1,
                "full_name": "alpha/one",
                "name": "one",
                "owner": {"login": "alpha"},
                "description": "agent memory",
                "html_url": "https://github.com/alpha/one",
                "language": "Python",
                "topics": ["agent"],
                "stargazers_count": 1,
                "forks_count": 0,
                "updated_at": "2026-01-01T00:00:00Z",
                "pushed_at": "2026-01-01T00:00:00Z",
            }
        ]

    def get_readme(self, full_name):
        return "# readme"


class McpSmokeTest(unittest.TestCase):
    def test_required_tools_are_listed_and_callable(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = StarsRadarService(os.path.join(tmp, "stars.sqlite"), github=FakeGitHubClient())
            try:
                tools = build_tool_list()
                names = {tool["name"] for tool in tools}

                self.assertEqual(
                    {
                        "sync_stars",
                        "list_star_changes",
                        "get_unanalyzed_stars",
                        "list_categories",
                        "get_star",
                        "get_readme",
                        "save_analysis",
                        "search_stars",
                        "recommend_stars_for_task",
                        "export_codex_context",
                    },
                    names,
                )

                response = call_tool(service, "search_stars", {"query": "agent"})
                self.assertEqual(response["content"][0]["type"], "text")
                self.assertIn("alpha/one", response["content"][0]["text"])
            finally:
                service.close()

    def test_sync_stars_schema_rejects_unknown_force_argument(self):
        tools = {tool["name"]: tool for tool in build_tool_list()}

        sync_schema = tools["sync_stars"]["inputSchema"]

        self.assertFalse(sync_schema["additionalProperties"])
        self.assertNotIn("force", sync_schema["properties"])
        with tempfile.TemporaryDirectory() as tmp:
            service = StarsRadarService(os.path.join(tmp, "stars.sqlite"), github=FakeGitHubClient())
            try:
                with self.assertRaisesRegex(ValueError, "Unexpected arguments for sync_stars: force"):
                    call_tool(service, "sync_stars", {"force": True})
            finally:
                service.close()

    def test_server_accepts_standard_mcp_content_length_frames(self):
        def frame(payload):
            body = json.dumps(payload).encode("utf-8")
            return b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body

        def read_frame(stream):
            header = b""
            while b"\r\n\r\n" not in header:
                chunk = stream.read(1)
                if not chunk:
                    raise AssertionError("server closed stdout before sending a frame")
                header += chunk
            length = None
            for line in header.decode("ascii").split("\r\n"):
                if line.lower().startswith("content-length:"):
                    length = int(line.split(":", 1)[1].strip())
            if length is None:
                raise AssertionError(f"missing Content-Length header: {header!r}")
            return json.loads(stream.read(length).decode("utf-8"))

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["GITHUB_STARS_RADAR_DB"] = os.path.join(tmp, "stars.sqlite")
            proc = subprocess.Popen(
                [sys.executable, os.path.join(root, "mcp-server", "server.py")],
                cwd=root,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                proc.stdin.write(
                    frame(
                        {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "stdio-test", "version": "1"},
                            },
                        }
                    )
                )
                proc.stdin.flush()
                response = read_frame(proc.stdout)
                self.assertEqual(response["id"], 1)
                self.assertIn("result", response)
            finally:
                proc.kill()
                proc.wait(timeout=5)
                proc.stdin.close()
                proc.stdout.close()
                proc.stderr.close()


if __name__ == "__main__":
    unittest.main()
