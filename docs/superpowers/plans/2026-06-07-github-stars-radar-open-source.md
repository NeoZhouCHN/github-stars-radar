# GitHub Stars Radar Open Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first GitHub starred repository memory service for Codex, Claude Code, OpenClaw, and Hermes.

**Architecture:** Use Python standard library only: GitHub sync through API or `gh auth token`, local SQLite cache, a small service layer, and a stdio MCP server. No UI, no dashboard, no star management workflow.

**Tech Stack:** Python 3.11+, SQLite, unittest, stdio JSON-RPC MCP protocol.

---

## File Structure

- `core/github_stars_radar/`: importable Python package with SQLite store, GitHub client, service tools, and MCP protocol helpers.
- `mcp-server/server.py`: stdio entrypoint used by agent clients.
- `tests/`: unittest coverage for sync diffing, TTL behavior, analysis persistence, search/recommend, README fetching, and MCP smoke behavior.
- `scripts/`: local smoke and manifest checks.
- `prompts/`: structured repo analysis prompts in Chinese and English.
- `skills/github-stars-radar/SKILL.md`: cross-agent usage guidance.
- `adapters/`: Codex, Claude Code, OpenClaw, and Hermes integration docs/manifests.
- `README.md`, `.env.example`, `.gitignore`: open-source setup and safety boundary.

## Tasks

### Task 1: RED Tests For Core Behavior

**Files:**
- Create: `tests/test_service.py`
- Create: `tests/test_mcp_smoke.py`

- [ ] **Step 1: Write failing tests**

Tests must cover:
- Added, removed, and updated repositories are detected; removed repos are soft-deleted.
- `save_analysis` stores structured agent analysis and clears stale analysis state.
- `search_stars`, `recommend_stars_for_task`, `get_unanalyzed_stars`, and `list_categories` perform TTL auto-sync and return sync status.
- `get_star` syncs only when a repo is missing locally.
- `get_readme` reads GitHub current README without local sync.
- MCP `tools/list` exposes the required 9 tools and `tools/call` can run `search_stars`.

- [ ] **Step 2: Run tests to verify RED**

Run: `python -m unittest discover -s tests -v`

Expected: FAIL because `core.github_stars_radar` does not exist yet.

### Task 2: GREEN Core Implementation

**Files:**
- Create: `core/github_stars_radar/__init__.py`
- Create: `core/github_stars_radar/store.py`
- Create: `core/github_stars_radar/github.py`
- Create: `core/github_stars_radar/service.py`
- Create: `core/github_stars_radar/mcp.py`
- Create: `mcp-server/server.py`

- [ ] **Step 1: Implement SQLite store**

Use three tables: `repos`, `sync_runs`, and `star_changes`. Store repo metadata, README hash, analysis fields, stale flag, soft-delete status, and timestamps.

- [ ] **Step 2: Implement GitHub client**

Use `GITHUB_TOKEN`, `GH_TOKEN`, or `gh auth token`. Fetch `/user/starred` pages and README content through the GitHub API.

- [ ] **Step 3: Implement service tools**

Expose the 9 required tool functions. Default cache policy:
`auto_sync=true`, `max_cache_age_minutes=360`, `allow_stale=true`.

- [ ] **Step 4: Implement MCP stdio server**

Support `initialize`, `tools/list`, and `tools/call`, returning JSON content blocks.

- [ ] **Step 5: Run tests to verify GREEN**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

### Task 3: Docs, Prompts, Skills, And Adapters

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `.gitignore`
- Create: `prompts/repo-analysis.zh.md`
- Create: `prompts/repo-analysis.en.md`
- Create: `skills/github-stars-radar/SKILL.md`
- Create: `adapters/codex/.codex-plugin/plugin.json`
- Create: `adapters/codex/.mcp.json`
- Create: `adapters/claude-code/README.md`
- Create: `adapters/openclaw/README.md`
- Create: `adapters/hermes/README.md`

- [ ] **Step 1: Write structured prompts**

Both prompts must require `summary`, `tags`, `category`, `platforms`, and `notes`.

- [ ] **Step 2: Write cross-agent skill**

Document when to search local stars first, when to compare 3 mature external projects, and how to present recommendations.

- [ ] **Step 3: Write adapter manifests/docs**

Codex gets concrete manifests. Claude Code and OpenClaw get install layout docs. Hermes gets conservative docs that state the interface is unverified.

- [ ] **Step 4: Expand README**

Include what this is and is not, installation, token permissions, privacy boundary, commands, and MCP tool examples.

### Task 4: Verification And Release Safety

**Files:**
- Create: `scripts/smoke_mcp.py`
- Create: `scripts/check_manifests.py`

- [ ] **Step 1: Run unit tests**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 2: Run MCP smoke test**

Run: `python scripts/smoke_mcp.py`

Expected: PASS and required tools are listed.

- [ ] **Step 3: Run manifest check**

Run: `python scripts/check_manifests.py`

Expected: PASS and `.gitignore`, `.env.example`, prompts, skill, and adapters are present.

- [ ] **Step 4: Completion audit**

Check every numbered requirement in the user goal against files and command output before claiming completion.
