import argparse
import os
import subprocess
from pathlib import Path


def git(args):
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").strip()


def previous_tag(current_tag):
    tags = git(["tag", "--list", "v*", "--sort=-v:refname"]).splitlines()
    for tag in tags:
        if tag != current_tag:
            return tag
    return ""


def commit_lines(revision_range, target_ref):
    if revision_range:
        output = git(["log", "--pretty=format:%h%x09%s", revision_range])
    else:
        output = git(["log", "--pretty=format:%h%x09%s", "-20", target_ref])
    return [line.split("\t", 1) for line in output.splitlines() if "\t" in line]


def repo_url():
    repo = os.environ.get("GITHUB_REPOSITORY", "NeoZhouCHN/github-stars-radar")
    return f"https://github.com/{repo}"


def render(version, output_path, target_ref="HEAD"):
    current_tag = f"v{version}"
    prev = previous_tag(current_tag)
    revision_range = f"{prev}..{target_ref}" if prev else ""
    commits = commit_lines(revision_range, target_ref)
    base_url = repo_url()

    lines = [f"## What's Changed", ""]
    if not commits:
        lines.append("* No commit changes detected for this release.")
    else:
        for short_sha, subject in commits:
            lines.append(f"* {subject} ([{short_sha}]({base_url}/commit/{short_sha}))")
    lines.append("")

    if prev:
        lines.append(f"**Full Changelog**: {base_url}/compare/{prev}...{current_tag}")
    else:
        lines.append(f"**Commit History**: {base_url}/commits/{current_tag}")

    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--target-ref", default="HEAD")
    args = parser.parse_args()
    render(args.version, args.output, args.target_ref)


if __name__ == "__main__":
    main()
