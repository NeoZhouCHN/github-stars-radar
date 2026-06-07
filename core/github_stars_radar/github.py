import base64
import json
import os
import subprocess
import urllib.error
import urllib.request


class GitHubClient:
    def __init__(self, token=None, api_base="https://api.github.com"):
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or self._gh_token()
        self.api_base = api_base.rstrip("/")

    def _gh_token(self):
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return result.stdout.strip() or None

    def _request_json(self, url):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-stars-radar",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            link = response.headers.get("Link", "")
            return json.loads(response.read().decode("utf-8")), link

    def list_starred_repos(self):
        repos = []
        page = 1
        while True:
            data, link = self._request_json(f"{self.api_base}/user/starred?per_page=100&page={page}")
            repos.extend(data)
            if 'rel="next"' not in link:
                return repos
            page += 1

    def get_readme(self, full_name):
        url = f"{self.api_base}/repos/{full_name}/readme"
        try:
            data, _ = self._request_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return ""
            raise
        content = data.get("content", "")
        if not content:
            return ""
        return base64.b64decode(content).decode("utf-8", errors="replace")
