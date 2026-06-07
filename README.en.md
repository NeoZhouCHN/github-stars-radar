# GitHub Stars Radar

<p align="center">
  <img src="https://img.shields.io/badge/MCP-stdio-2f6fed?style=flat-square" alt="MCP stdio" />
  <img src="https://img.shields.io/badge/plugin-Codex%20%7C%20Claude%20Code-111827?style=flat-square" alt="Codex and Claude Code plugin" />
  <img src="https://img.shields.io/badge/storage-SQLite-1f8f4c?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/local--first-private-0f766e?style=flat-square" alt="local-first private" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT license" />
</p>

<p align="center">
  <b>Turn your GitHub stars into local memory that AI coding agents can search and reuse.</b>
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/README-ZH-d32f2f?style=for-the-badge" alt="中文" /></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/README-EN-111827?style=for-the-badge" alt="English" /></a>
</p>

## English

**GitHub Stars Radar** turns your GitHub starred repositories into a local knowledge base that AI coding agents can search and reuse.

In plain terms: you have starred many useful repositories, but your coding agent does not know them by default. This project syncs those stars locally, lets agents search them, fetch README content, recommend useful repositories for a task, and save structured analysis so future agents do not repeat the same work.

## Let AI Install It First

Paste this prompt into Codex or Claude Code:

```text
Please install and connect GitHub Stars Radar.
Repository: https://github.com/NeoZhouCHN/github-stars-radar
Local path: <your-project-path>/github-stars-radar
Target client: Codex / Claude Code / OpenClaw / Hermes

Please:
1. Check that Python is available. On Windows, try py first. On macOS/Linux, try python3 first.
2. Check whether .env exists. If not, copy .env.example to .env. Do not read, print, or log my token.
3. Check that GITHUB_TOKEN, GH_TOKEN, or gh auth token is available.
4. For Codex, prefer installing adapters/codex as a Codex plugin. If plugin installation is unavailable, fall back to MCP config.
5. For Claude Code, prefer installing the repository root as a Claude Code plugin with .claude-plugin/plugin.json and .mcp.json. If plugin installation is unavailable, fall back to MCP config.
6. For OpenClaw or Hermes, configure the stdio MCP server with command py or python3, args pointing to mcp-server/server.py, and env.GITHUB_STARS_RADAR_DB set to a local SQLite path.
7. Run scripts/smoke_mcp.py.
8. Tell me which config files changed, whether verification passed, and how to call github-stars-radar next.

Do not commit data/*.sqlite, data/*.json, .env, or any token.
```

## Features

| Feature | Meaning |
| --- | --- |
| Sync GitHub stars | Pull your starred repositories into a local cache |
| SQLite cache | Keep data on your computer |
| Added/removed/updated detection | Track what changed since the last sync |
| Save agent analysis | Store summaries, tags, categories, platforms, and notes |
| TTL auto-sync | Refresh stale cache automatically and fall back to stale data if sync fails |
| MCP tools | Expose a shared toolset to MCP-compatible clients |
| Plugin packaging | Codex and Claude Code can install bundled MCP config and guidance |

## MCP Vs Plugin

The MCP server provides the actual tools: `sync_stars`, `search_stars`, `recommend_stars_for_task`, `get_readme`, `save_analysis`, and more.

Plugins are installation and guidance bundles. Codex and Claude Code can use plugin metadata and skills/instructions. OpenClaw and Hermes should use the generic stdio MCP configuration unless they have a verified plugin format for your environment.

## Setup

Requirements:

- Python 3.11 or newer
- A GitHub token, or an authenticated `gh` CLI
- This project checked out locally

Get a GitHub token:

- Official docs: [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- Fine-grained token page: [https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
- Classic token page: [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

Clone and initialize:

```bash
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
cp .env.example .env
```

On Windows PowerShell:

```powershell
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
copy .env.example .env
```

Set one token variable:

```text
GITHUB_TOKEN=your GitHub token
GH_TOKEN=
GITHUB_STARS_RADAR_DB=./data/stars.sqlite
```

Or:

```text
GITHUB_TOKEN=
GH_TOKEN=your GitHub token
GITHUB_STARS_RADAR_DB=./data/stars.sqlite
```

## Local Verification

Windows:

```powershell
py -m unittest discover -s tests -v
py scripts/smoke_mcp.py
py scripts/check_manifests.py
```

macOS / Linux:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/smoke_mcp.py
python3 scripts/check_manifests.py
```

## Install Routes

Codex:

- Install `adapters/codex` as a Codex plugin.
- If plugin installation is unavailable, copy `adapters/codex/.mcp.json` into your Codex MCP configuration.

Claude Code:

- Install the repository root as a Claude Code plugin.
- It includes `.claude-plugin/plugin.json`, `.mcp.json`, and `skills/github-stars-radar/SKILL.md`.

OpenClaw / Hermes:

- Configure the generic stdio MCP server.

```json
{
  "mcpServers": {
    "github-stars-radar": {
      "command": "python3",
      "args": ["<your-project-path>/github-stars-radar/mcp-server/server.py"],
      "env": {
        "GITHUB_STARS_RADAR_DB": "<your-project-path>/github-stars-radar/data/stars.sqlite"
      }
    }
  }
}
```

On Windows, use `py` if that is your working Python launcher.

## Windows Packaging

This repository includes `.github/workflows/windows-release.yml`.

After updating the project, open **Actions -> Build Windows Package -> Run workflow**. The workflow runs tests, builds a PyInstaller executable, creates a portable zip, optionally builds an Inno Setup installer, and uploads the outputs as workflow artifacts.

## Local Privacy Boundary

The default cache path is `./data/stars.sqlite`. `.gitignore` excludes:

- `data/*.json`
- `data/*.sqlite`
- `data/*.db`
- `.env`
- `.env.*`

These files may contain personal stars, saved agent analysis, or tokens. Do not commit them.

## License

MIT License. See `LICENSE`.
