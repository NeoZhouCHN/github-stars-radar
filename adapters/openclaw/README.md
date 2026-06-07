# OpenClaw Adapter

OpenClaw integration should use the same stdio MCP server plus the generic skill in `skills/github-stars-radar/SKILL.md`.

Bundle contents:

```text
mcp-server/server.py
core/github_stars_radar/
skills/github-stars-radar/SKILL.md
prompts/repo-analysis.zh.md
prompts/repo-analysis.en.md
```

Configure OpenClaw to launch:

```text
py <path-to-github-stars-radar>/mcp-server/server.py
```

Set:

```text
GITHUB_STARS_RADAR_DB=<path-to-github-stars-radar>/data/stars.sqlite
GITHUB_TOKEN=<optional token>
```

No OpenClaw-specific runtime behavior is required beyond stdio MCP support.
