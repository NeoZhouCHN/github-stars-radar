import argparse
import os
import subprocess
from pathlib import Path


CATEGORIES = [
    ("Features", ("feat", "feature", "enhancement")),
    ("Fixes", ("fix", "bug", "bugfix")),
    ("Documentation", ("docs", "doc", "documentation")),
    ("Packaging And CI", ("ci", "build", "packaging", "release")),
    ("Maintenance", ("chore", "refactor", "test", "tests")),
]


def git(args):
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()


def previous_tag(current_tag):
    tags = git(["tag", "--list", "v*", "--sort=-v:refname"]).splitlines()
    for tag in tags:
        if tag != current_tag:
            return tag
    return ""


def commit_lines(revision_range):
    output = git(["log", "--pretty=format:%h%x09%s", revision_range]) if revision_range else git(["log", "--pretty=format:%h%x09%s", "-20"])
    return [line.split("\t", 1) for line in output.splitlines() if "\t" in line]


def category_for(subject):
    lowered = subject.lower()
    prefix = lowered.split(":", 1)[0].split("(", 1)[0].strip()
    for title, prefixes in CATEGORIES:
        if prefix in prefixes:
            return title
    return "Other Changes"


def repo_url():
    repo = os.environ.get("GITHUB_REPOSITORY", "NeoZhouCHN/github-stars-radar")
    return f"https://github.com/{repo}"


def render(version, output_path):
    current_tag = f"v{version}"
    prev = previous_tag(current_tag)
    revision_range = f"{prev}..HEAD" if prev else ""
    commits = commit_lines(revision_range)
    grouped = {title: [] for title, _ in CATEGORIES}
    grouped["Other Changes"] = []
    base_url = repo_url()

    for short_sha, subject in commits:
        grouped[category_for(subject)].append(f"- {subject} ([{short_sha}]({base_url}/commit/{short_sha}))")

    lines = [f"## What's Changed", ""]
    if not commits:
        lines.append("- No commit changes detected for this release.")
    else:
        for title in [item[0] for item in CATEGORIES] + ["Other Changes"]:
            items = grouped[title]
            if items:
                lines.extend([f"### {title}", "", *items, ""])

    lines.extend([
        "## Release Assets",
        "",
        f"- `GitHubStarsRadar-{version}-windows-x64.zip`",
        f"- `GitHubStarsRadarSetup-{version}.exe`",
        f"- `GitHubStarsRadar-{version}-macos-x64.tar.gz`",
        f"- `GitHubStarsRadar-{version}-linux-x64.tar.gz`",
        "- `SHA256SUMS.txt` and per-platform checksum files",
        "",
    ])
    if prev:
        lines.append(f"**Full Changelog**: {base_url}/compare/{prev}...{current_tag}")
    else:
        lines.append(f"**Commit History**: {base_url}/commits/{current_tag}")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render(args.version, args.output)


if __name__ == "__main__":
    main()
