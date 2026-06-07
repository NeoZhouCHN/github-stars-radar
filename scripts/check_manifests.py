import json
import os


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def require(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        raise SystemExit(f"missing required file: {path}")
    return full


def require_text(path, snippets):
    text = open(require(path), "r", encoding="utf-8").read()
    for snippet in snippets:
        if snippet not in text:
            raise SystemExit(f"{path} missing snippet: {snippet}")


def require_json(path):
    with open(require(path), "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    require_text("LICENSE", ["MIT License", "Copyright (c) 2026 NeoZhouCHN"])
    require_text(".gitignore", ["data/*.json", "data/*.sqlite", "data/*.db", ".env"])
    require_text(".env.example", ["GITHUB_STARS_RADAR_DB="])
    require_text("prompts/repo-analysis.zh.md", ["summary", "tags", "category", "platforms", "notes"])
    require_text("prompts/repo-analysis.en.md", ["summary", "tags", "category", "platforms", "notes"])
    require_text("skills/github-stars-radar/SKILL.md", ["search_stars", "recommend_stars_for_task", "3 mature external projects"])

    plugin = require_json("adapters/codex/.codex-plugin/plugin.json")
    if plugin["name"] != "github-stars-radar":
        raise SystemExit("Codex plugin name mismatch")
    if plugin.get("license") != "MIT":
        raise SystemExit("Codex plugin license mismatch")
    if "github-stars-radar" not in plugin.get("mcp_servers", {}):
        raise SystemExit("Codex plugin missing MCP server")

    claude_plugin = require_json(".claude-plugin/plugin.json")
    if claude_plugin["name"] != "github-stars-radar":
        raise SystemExit("Claude Code plugin name mismatch")
    if claude_plugin.get("license") != "MIT":
        raise SystemExit("Claude Code plugin license mismatch")

    mcp = require_json("adapters/codex/.mcp.json")
    if "github-stars-radar" not in mcp.get("mcpServers", {}):
        raise SystemExit("Codex .mcp.json missing server")

    claude_mcp = require_json(".mcp.json")
    if "github-stars-radar" not in claude_mcp.get("mcpServers", {}):
        raise SystemExit("Claude Code .mcp.json missing server")

    require("adapters/claude-code/README.md")
    require("adapters/openclaw/README.md")
    require("adapters/hermes/README.md")
    require_text(
        "README.md",
        [
            "功能一览",
            "先让 AI 帮你安装",
            "Codex：安装 Plugin",
            "Claude Code：安装 Plugin",
            "OpenClaw / Hermes：安装 MCP",
            "给 OpenClaw / Hermes 添加自动调用策略",
            "https://github.com/NeoZhouCHN/github-stars-radar.git",
            "https://github.com/settings/personal-access-tokens/new",
            "MIT License",
            "Local Privacy Boundary",
            "Let AI Install It First",
            "Codex: Install Plugin",
            "Claude Code: Install Plugin",
            "OpenClaw / Hermes: Install MCP",
            "Add Auto-Call Instructions For OpenClaw / Hermes",
        ],
    )
    print("Manifest and release-safety checks passed")


if __name__ == "__main__":
    main()
