import os
import tempfile
import unittest

from core.github_stars_radar.service import StarsRadarService


def repo(full_name, pushed_at="2026-01-01T00:00:00Z", description="useful tool"):
    owner, name = full_name.split("/", 1)
    return {
        "id": abs(hash(full_name)) % 1000000,
        "full_name": full_name,
        "name": name,
        "owner": {"login": owner},
        "description": description,
        "html_url": f"https://github.com/{full_name}",
        "language": "Python",
        "topics": ["agent", "mcp"],
        "stargazers_count": 100,
        "forks_count": 10,
        "updated_at": pushed_at,
        "pushed_at": pushed_at,
    }


class FakeGitHubClient:
    def __init__(self):
        self.star_pages = []
        self.readmes = {}
        self.sync_calls = 0
        self.readme_calls = 0
        self.fail_sync = False

    def list_starred_repos(self):
        self.sync_calls += 1
        if self.fail_sync:
            raise RuntimeError("network down")
        return list(self.star_pages)

    def get_readme(self, full_name):
        self.readme_calls += 1
        return self.readmes.get(full_name, f"# {full_name}")


class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "stars.sqlite")
        self.github = FakeGitHubClient()
        self.service = StarsRadarService(self.db_path, github=self.github)

    def tearDown(self):
        self.service.close()
        self.tmp.cleanup()

    def test_sync_detects_added_removed_and_updated_with_soft_delete(self):
        self.github.star_pages = [repo("alpha/one"), repo("beta/two")]
        first = self.service.sync_stars()

        self.assertEqual(first["sync"]["status"], "refreshed")
        self.assertEqual(first["sync"]["added"], 2)
        self.assertEqual(first["sync"]["removed"], 0)

        self.github.star_pages = [
            repo("alpha/one", pushed_at="2026-02-01T00:00:00Z"),
            repo("gamma/three"),
        ]
        second = self.service.sync_stars()

        self.assertEqual(second["sync"]["added"], 1)
        self.assertEqual(second["sync"]["removed"], 1)
        self.assertEqual(second["sync"]["updated"], 1)

        removed = self.service.get_star("beta/two")["repo"]
        changed = self.service.get_star("alpha/one")["repo"]
        self.assertTrue(removed["removed"])
        self.assertTrue(changed["analysis_stale"])

    def test_sync_stars_defers_readme_fetches_to_batch_backfill(self):
        self.github.star_pages = [repo("alpha/one")]
        result = self.service.sync_stars()

        self.assertEqual(result["sync"]["added"], 1)
        self.assertEqual(self.github.readme_calls, 0)
        self.assertEqual(self.service.store.get_repo("alpha/one")["readme_hash"], "")

    def test_sync_readmes_batches_missing_readmes_and_sync_stars_reuses_them(self):
        self.github.star_pages = [repo("alpha/one"), repo("beta/two")]
        self.service.sync_stars()

        first = self.service.sync_readmes(limit=1)

        self.assertEqual(first["sync"]["status"], "readmes_refreshed")
        self.assertEqual(first["sync"]["readmes_synced"], 1)
        self.assertEqual(first["sync"]["remaining"], 1)
        self.assertEqual(self.github.readme_calls, 1)

        second = self.service.sync_stars()

        self.assertEqual(second["sync"]["updated"], 0)
        self.assertEqual(self.github.readme_calls, 1)

    def test_started_sync_run_does_not_make_ttl_cache_fresh(self):
        self.github.star_pages = [repo("alpha/one")]
        self.service.sync_stars()
        self.service.store.set_last_sync_started_at("2000-01-01T00:00:00Z")
        self.service.store.record_sync("started", message="interrupted")

        self.github.star_pages = [repo("alpha/one"), repo("beta/two")]
        refreshed = self.service.search_stars("beta", max_cache_age_minutes=360)

        self.assertEqual(refreshed["sync"]["status"], "refreshed")
        self.assertEqual(refreshed["sync"]["added"], 1)
        self.assertEqual(refreshed["results"][0]["full_name"], "beta/two")

    def test_failed_sync_is_recorded_without_becoming_fresh_cache(self):
        self.github.fail_sync = True

        with self.assertRaises(RuntimeError):
            self.service.sync_stars()

        last = self.service.store.get_last_sync()
        self.assertEqual(last["status"], "failed")
        self.assertIn("network down", last["message"])

    def test_save_analysis_clears_stale_state_and_list_categories_uses_it(self):
        self.github.star_pages = [repo("alpha/one")]
        self.service.sync_stars()
        result = self.service.save_analysis(
            "alpha/one",
            summary="Local agent memory helper",
            tags=["agent", "memory"],
            category="agent-tools",
            platforms=["codex", "claude-code"],
            notes="Good fit for local-first workflows.",
        )

        self.assertEqual(result["repo"]["analysis"]["category"], "agent-tools")
        self.assertFalse(result["repo"]["analysis_stale"])

        categories = self.service.list_categories(auto_sync=False)
        self.assertEqual(categories["categories"][0]["category"], "agent-tools")
        self.assertEqual(categories["categories"][0]["count"], 1)

    def test_ttl_auto_sync_refreshes_stale_cache_and_falls_back_to_old_cache(self):
        self.github.star_pages = [repo("alpha/one")]
        self.service.sync_stars()

        skipped = self.service.search_stars("alpha")
        self.assertEqual(skipped["sync"]["status"], "skipped")
        self.assertEqual(skipped["results"][0]["full_name"], "alpha/one")

        self.service.store.set_last_sync_started_at("2000-01-01T00:00:00Z")
        self.github.star_pages = [repo("alpha/one"), repo("beta/two")]
        refreshed = self.service.search_stars("beta", max_cache_age_minutes=360)
        self.assertEqual(refreshed["sync"]["status"], "refreshed")
        self.assertEqual(refreshed["sync"]["added"], 1)
        self.assertEqual(refreshed["results"][0]["full_name"], "beta/two")

        self.service.store.set_last_sync_started_at("2000-01-01T00:00:00Z")
        self.github.fail_sync = True
        stale = self.service.search_stars("alpha", allow_stale=True)
        self.assertEqual(stale["sync"]["status"], "failed")
        self.assertIn("using stale local cache", stale["sync"]["message"])
        self.assertEqual(stale["results"][0]["full_name"], "alpha/one")

    def test_get_star_syncs_only_when_missing_and_get_readme_never_syncs(self):
        self.github.star_pages = [repo("alpha/one")]
        self.service.sync_stars()
        sync_calls = self.github.sync_calls

        existing = self.service.get_star("alpha/one")
        self.assertEqual(existing["sync"]["status"], "skipped")
        self.assertEqual(self.github.sync_calls, sync_calls)

        self.github.star_pages = [repo("alpha/one"), repo("beta/two")]
        missing = self.service.get_star("beta/two")
        self.assertEqual(missing["sync"]["status"], "refreshed")
        self.assertEqual(missing["repo"]["full_name"], "beta/two")

        before_readme_sync_calls = self.github.sync_calls
        readme = self.service.get_readme("beta/two")
        self.assertEqual(readme["full_name"], "beta/two")
        self.assertTrue(readme["readme"].startswith("# beta/two"))
        self.assertEqual(self.github.sync_calls, before_readme_sync_calls)

    def test_unanalyzed_search_recommend_and_export_context(self):
        self.github.star_pages = [
            repo("alpha/agent-kit", description="agent sdk prompt orchestration"),
            repo("beta/chart-lib", description="visual charts dashboard"),
        ]
        self.service.sync_stars()
        self.service.save_analysis(
            "alpha/agent-kit",
            summary="Agent SDK examples",
            tags=["agent", "sdk"],
            category="agent-tools",
            platforms=["codex"],
            notes="Useful for tool calling.",
        )

        unanalyzed = self.service.get_unanalyzed_stars(auto_sync=False)
        self.assertEqual([item["full_name"] for item in unanalyzed["repos"]], ["beta/chart-lib"])

        search = self.service.search_stars("agent", auto_sync=False)
        self.assertEqual(search["results"][0]["full_name"], "alpha/agent-kit")

        recs = self.service.recommend_stars_for_task("build an agent tool", auto_sync=False)
        self.assertEqual(recs["recommendations"][0]["full_name"], "alpha/agent-kit")
        self.assertIn("fit_reason", recs["recommendations"][0])

        context = self.service.export_codex_context(["alpha/agent-kit"], "build an agent")
        self.assertIn("alpha/agent-kit", context["prompt"])
        self.assertIn("Agent SDK examples", context["prompt"])

    def test_recommendations_include_score_breakdown_from_repo_metadata_and_analysis(self):
        self.github.star_pages = [
            repo("alpha/minimal-agent", pushed_at="2020-01-01T00:00:00Z", description="agent tool"),
            repo("beta/rich-agent", pushed_at="2999-01-01T00:00:00Z", description="agent tool"),
        ]
        self.github.star_pages[0]["stargazers_count"] = 10
        self.github.star_pages[0]["topics"] = []
        self.github.star_pages[1]["stargazers_count"] = 1000
        self.github.star_pages[1]["topics"] = ["agent", "mcp"]
        self.github.readmes = {
            "alpha/minimal-agent": "basic helper",
            "beta/rich-agent": "agent mcp memory helper",
        }
        self.service.sync_stars()
        self.service.sync_readmes(limit=10)
        self.service.save_analysis(
            "beta/rich-agent",
            summary="Agent memory helper",
            tags=["agent", "memory"],
            category="agent-tools",
            platforms=["codex"],
            notes="Useful for MCP tool recommendations.",
        )

        recs = self.service.recommend_stars_for_task("agent mcp python memory", auto_sync=False)

        top = recs["recommendations"][0]
        self.assertEqual(top["full_name"], "beta/rich-agent")
        self.assertGreater(top["score"], 0)
        self.assertEqual(
            sorted(top["score_breakdown"].keys()),
            [
                "analysis_quality",
                "language_match",
                "popularity",
                "readme_match",
                "recency",
                "text_match",
                "topic_match",
            ],
        )
        self.assertGreater(top["score_breakdown"]["readme_match"], 0)
        self.assertGreater(top["score_breakdown"]["topic_match"], 0)
        self.assertGreater(top["score_breakdown"]["analysis_quality"], 0)
        self.assertEqual(
            top["score_summary"],
            "Score 62. Top signals: GitHub topics 12, metadata/analysis text 11, recent activity 10.",
        )
        self.assertEqual(top["display_name"], "Score 62 - beta/rich-agent")
        self.assertTrue(top["fit_reason"].startswith("Score 62."))


if __name__ == "__main__":
    unittest.main()
