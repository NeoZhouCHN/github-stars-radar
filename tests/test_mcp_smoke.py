import os
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


if __name__ == "__main__":
    unittest.main()
