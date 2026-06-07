# Claude Code Adapter

This project exposes a stdio MCP server and a generic skill.

Suggested local layout:

```text
github-stars-radar/
  mcp-server/server.py
  skills/github-stars-radar/SKILL.md
```

Add the MCP server to your Claude Code configuration using the local project path:

```json
{
  "mcpServers": {
    "github-stars-radar": {
      "command": "py",
      "args": ["<path-to-github-stars-radar>/mcp-server/server.py"],
      "env": {
        "GITHUB_STARS_RADAR_DB": "<path-to-github-stars-radar>/data/stars.sqlite"
      }
    }
  }
}
```

Install or copy `skills/github-stars-radar/SKILL.md` into the Claude Code skills location used by your environment.

This adapter does not require a UI. It assumes Python and GitHub credentials are available locally.
