# Hermes Adapter

This is a conservative adapter note. No verified Hermes package or plugin manifest specification is included in this repository.

Use the project through the generic stdio MCP interface if your Hermes environment supports launching local MCP servers:

```text
command: py
args: ["<path-to-github-stars-radar>/mcp-server/server.py"]
env:
  GITHUB_STARS_RADAR_DB: "<path-to-github-stars-radar>/data/stars.sqlite"
```

Also import the generic skill text from:

```text
skills/github-stars-radar/SKILL.md
```

Before publishing a Hermes-specific bundle, verify the current Hermes adapter schema and update this folder with a real manifest.
