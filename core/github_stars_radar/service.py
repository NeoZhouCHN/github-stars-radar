import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone

from .github import GitHubClient
from .store import StarsStore


PROMPT_VERSION = "repo-analysis-v1"
DEFAULT_CACHE_PATH = os.environ.get("GITHUB_STARS_RADAR_DB", "./data/stars.sqlite")


def _hash_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _terms(text):
    return [part for part in re.split(r"[^a-z0-9]+", text.lower()) if part]


class StarsRadarService:
    def __init__(self, db_path=DEFAULT_CACHE_PATH, github=None):
        self.store = StarsStore(db_path)
        self.github = github or GitHubClient()

    def sync_stars(self, include_removed=True):
        repos = self.github.list_starred_repos()
        run_id, _ = self.store.record_sync("started")
        remote_names = {item["full_name"] for item in repos}
        local_by_name = {item["full_name"]: item for item in self.store.list_repos(include_removed=True)}
        added = removed = updated = 0

        for item in repos:
            normalized = self._normalize_repo(item)
            existing = local_by_name.get(normalized["full_name"])
            metadata_changed = existing is None or existing["metadata_hash"] != normalized["metadata_hash"] or existing["removed"]
            if metadata_changed or not existing.get("readme_hash", ""):
                try:
                    readme = self.github.get_readme(normalized["full_name"])
                except Exception:
                    readme = ""
                normalized["readme_hash"] = _hash_text(readme)
                normalized["readme_text"] = readme
            else:
                normalized["readme_hash"] = existing["readme_hash"]
                normalized["readme_text"] = self.store.get_readme_text(normalized["full_name"])
            if existing is None:
                added += 1
                self.store.add_change(run_id, normalized["full_name"], "added")
                normalized["analysis_stale"] = True
            else:
                changed = (
                    metadata_changed
                    or existing["readme_hash"] != normalized["readme_hash"]
                    or existing["prompt_version"] not in ("", PROMPT_VERSION)
                )
                if changed:
                    updated += 1
                    self.store.add_change(run_id, normalized["full_name"], "updated")
                normalized["analysis_stale"] = changed or existing["analysis_stale"]
            self.store.upsert_repo(normalized)

        if include_removed:
            for full_name, existing in local_by_name.items():
                if full_name not in remote_names and not existing["removed"]:
                    removed += 1
                    self.store.mark_removed(full_name)
                    self.store.add_change(run_id, full_name, "removed")

        message = f"sync: refreshed, added {added}, removed {removed}, updated {updated}"
        self.store.conn.execute(
            "UPDATE sync_runs SET status = ?, added = ?, removed = ?, updated = ?, message = ? WHERE id = ?",
            ("refreshed", added, removed, updated, message, run_id),
        )
        self.store.conn.commit()
        return {"sync": {"status": "refreshed", "added": added, "removed": removed, "updated": updated, "message": message}}

    def list_star_changes(self, limit=50):
        return {"sync": self._sync_status_skipped(), "changes": self.store.list_changes(limit)}

    def get_unanalyzed_stars(self, auto_sync=True, max_cache_age_minutes=360, allow_stale=True, limit=50):
        sync = self._ensure_fresh(auto_sync, max_cache_age_minutes, allow_stale)
        repos = [
            repo for repo in self.store.list_repos()
            if repo["analysis_stale"] or not repo["analysis"]["summary"]
        ]
        return {"sync": sync, "repos": repos[: int(limit)]}

    def get_star(self, full_name):
        repo = self.store.get_repo(full_name)
        if repo:
            return {"sync": self._sync_status_skipped(), "repo": repo}
        sync = self.sync_stars()["sync"]
        return {"sync": sync, "repo": self.store.get_repo(full_name)}

    def get_readme(self, full_name):
        return {"full_name": full_name, "readme": self.github.get_readme(full_name)}

    def save_analysis(self, full_name, summary, tags=None, category="", platforms=None, notes=""):
        repo = self.store.get_repo(full_name)
        if not repo:
            self.sync_stars()
            repo = self.store.get_repo(full_name)
        if not repo:
            raise ValueError(f"Repository not found in local stars: {full_name}")
        self.store.save_analysis(
            full_name,
            summary,
            tags or [],
            category,
            platforms or [],
            notes,
            PROMPT_VERSION,
        )
        return {"repo": self.store.get_repo(full_name)}

    def search_stars(self, query="", category=None, tag=None, language=None, auto_sync=True, max_cache_age_minutes=360, allow_stale=True, limit=20):
        sync = self._ensure_fresh(auto_sync, max_cache_age_minutes, allow_stale)
        q_terms = _terms(query or "")
        results = []
        for repo in self.store.list_repos():
            if category and repo["analysis"]["category"] != category:
                continue
            if tag and tag not in repo["analysis"]["tags"] and tag not in repo["topics"]:
                continue
            if language and repo["language"].lower() != language.lower():
                continue
            haystack = self._repo_text(repo)
            if q_terms and not all(term in haystack for term in q_terms):
                continue
            results.append(repo)
        return {"sync": sync, "results": results[: int(limit)]}

    def recommend_stars_for_task(self, task, auto_sync=True, max_cache_age_minutes=360, allow_stale=True, limit=5):
        sync = self._ensure_fresh(auto_sync, max_cache_age_minutes, allow_stale)
        terms = _terms(task)
        scored = []
        for repo in self.store.list_repos():
            score, breakdown = self._score_repo(repo, terms)
            if self._has_query_match(breakdown):
                item = dict(repo)
                item["score"] = score
                item["score_breakdown"] = breakdown
                item["fit_reason"] = self._fit_reason(breakdown)
                item["not_fit_reason"] = "Validate current README and license before adopting."
                item["next_validation"] = "Open README and run the referenced project locally if it becomes implementation-critical."
                scored.append(item)
        scored.sort(key=lambda item: (-item["score"], item["full_name"]))
        return {"sync": sync, "recommendations": scored[: int(limit)]}

    def list_categories(self, auto_sync=True, max_cache_age_minutes=360, allow_stale=True, limit=50):
        sync = self._ensure_fresh(auto_sync, max_cache_age_minutes, allow_stale)
        counts = {}
        for repo in self.store.list_repos():
            category = repo["analysis"]["category"] or "uncategorized"
            counts[category] = counts.get(category, 0) + 1
        categories = [{"category": key, "count": value} for key, value in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        return {"sync": sync, "categories": categories[: int(limit)]}

    def export_codex_context(self, full_names, task):
        repos = [self.store.get_repo(name) for name in full_names]
        repos = [repo for repo in repos if repo]
        lines = [
            "# GitHub Stars Radar Context",
            "",
            f"Task: {task}",
            "",
            "Use these starred repositories as local prior art. Verify current upstream state before relying on them for major architecture, license, or deployment decisions.",
            "",
        ]
        for repo in repos:
            analysis = repo["analysis"]
            lines.extend(
                [
                    f"## {repo['full_name']}",
                    f"- URL: {repo['html_url']}",
                    f"- Description: {repo['description']}",
                    f"- Summary: {analysis['summary']}",
                    f"- Tags: {', '.join(analysis['tags'])}",
                    f"- Category: {analysis['category']}",
                    f"- Platforms: {', '.join(analysis['platforms'])}",
                    f"- Notes: {analysis['notes']}",
                    "",
                ]
            )
        return {"prompt": "\n".join(lines)}

    def _ensure_fresh(self, auto_sync=True, max_cache_age_minutes=360, allow_stale=True):
        if not auto_sync:
            return self._sync_status_skipped()
        last = self.store.get_last_sync()
        needs_sync = last is None or not self.store.has_any_repo()
        age_minutes = None
        if last:
            started = _parse_time(last["started_at"])
            if started:
                age_minutes = int((datetime.now(timezone.utc) - started).total_seconds() // 60)
                needs_sync = needs_sync or age_minutes > int(max_cache_age_minutes)
        if not needs_sync:
            return self._sync_status_skipped(age_minutes)
        try:
            return self.sync_stars()["sync"]
        except Exception as exc:
            if allow_stale and self.store.has_any_repo():
                return {"status": "failed", "message": f"sync: failed, using stale local cache ({exc})"}
            raise

    def _sync_status_skipped(self, age_minutes=None):
        if age_minutes is None:
            last = self.store.get_last_sync()
            if last:
                started = _parse_time(last["started_at"])
                if started:
                    age_minutes = int((datetime.now(timezone.utc) - started).total_seconds() // 60)
        if age_minutes is None:
            return {"status": "skipped", "message": "sync: skipped, no cache age available"}
        return {"status": "skipped", "message": f"sync: skipped, cache age {age_minutes} minutes", "cache_age_minutes": age_minutes}

    def _normalize_repo(self, item):
        metadata = {
            "full_name": item["full_name"],
            "description": item.get("description") or "",
            "language": item.get("language") or "",
            "topics": item.get("topics") or [],
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),
        }
        owner = item.get("owner") or {}
        return {
            "github_id": item.get("id"),
            "full_name": item["full_name"],
            "name": item.get("name") or item["full_name"].split("/")[-1],
            "owner": owner.get("login") or item["full_name"].split("/")[0],
            "description": metadata["description"],
            "html_url": item.get("html_url") or f"https://github.com/{item['full_name']}",
            "language": metadata["language"],
            "topics": metadata["topics"],
            "stars": metadata["stars"],
            "forks": metadata["forks"],
            "updated_at": metadata["updated_at"],
            "pushed_at": metadata["pushed_at"],
            "metadata_hash": _hash_text(json.dumps(metadata, sort_keys=True, ensure_ascii=False)),
            "prompt_version": PROMPT_VERSION,
        }

    def _repo_text(self, repo):
        analysis = repo["analysis"]
        return " ".join(
            [
                repo["full_name"],
                repo["description"],
                repo["language"],
                " ".join(repo["topics"]),
                analysis["summary"],
                " ".join(analysis["tags"]),
                analysis["category"],
                " ".join(analysis["platforms"]),
                analysis["notes"],
            ]
        ).lower()

    def _score_repo(self, repo, terms):
        text = self._repo_text(repo)
        readme_text = self.store.get_readme_text(repo["full_name"]).lower()
        topics = {topic.lower() for topic in repo["topics"]}
        language = repo["language"].lower()
        breakdown = {
            "text_match": min(sum(text.count(term) for term in terms), 20),
            "topic_match": sum(1 for term in terms if term in topics) * 3,
            "language_match": 5 if language and language in terms else 0,
            "readme_match": min(sum(readme_text.count(term) for term in terms), 20),
            "popularity": min(int(math.log10(max(repo["stars"], 0) + 1) * 3), 10),
            "recency": self._recency_score(repo),
            "analysis_quality": self._analysis_quality_score(repo),
        }
        weights = {
            "text_match": 1,
            "topic_match": 2,
            "language_match": 1,
            "readme_match": 2,
            "popularity": 1,
            "recency": 1,
            "analysis_quality": 1,
        }
        score = sum(breakdown[key] * weights[key] for key in breakdown)
        return score, breakdown

    def _has_query_match(self, breakdown):
        return any(
            breakdown[key] > 0
            for key in ("text_match", "topic_match", "language_match", "readme_match")
        )

    def _fit_reason(self, breakdown):
        labels = {
            "text_match": "metadata/analysis text",
            "topic_match": "GitHub topics",
            "language_match": "language",
            "readme_match": "README",
            "popularity": "stars",
            "recency": "recent activity",
            "analysis_quality": "saved analysis",
        }
        matched = [
            labels[key]
            for key, value in sorted(breakdown.items(), key=lambda item: (-item[1], item[0]))
            if value > 0
        ][:5]
        return f"Strongest signals: {', '.join(matched)}"

    def _recency_score(self, repo):
        timestamp = repo["pushed_at"] or repo["updated_at"]
        parsed = _parse_time(timestamp)
        if not parsed:
            return 0
        days = (datetime.now(timezone.utc) - parsed).days
        if days <= 30:
            return 10
        if days <= 180:
            return 7
        if days <= 365:
            return 4
        return 0

    def _analysis_quality_score(self, repo):
        if repo["analysis_stale"]:
            return 0
        analysis = repo["analysis"]
        score = 0
        score += 2 if analysis["summary"] else 0
        score += min(len(analysis["tags"]), 3)
        score += 2 if analysis["category"] else 0
        score += min(len(analysis["platforms"]), 2)
        score += 2 if analysis["notes"] else 0
        return min(score, 10)

    def close(self):
        self.store.close()
