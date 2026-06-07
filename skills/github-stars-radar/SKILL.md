---
name: github-stars-radar
description: Use local GitHub starred repositories as agent memory before recommending libraries, examples, MCP servers, plugins, or implementation references.
---

# GitHub Stars Radar

Use this skill when a task may benefit from the user's own starred repositories: library selection, MCP/plugin discovery, prompt/tool examples, reference implementations, or prior art for Codex, Claude Code, OpenClaw, and Hermes.

## When To Search Local Stars First

- The user asks for reusable projects, libraries, plugins, MCP servers, or example repos.
- The task resembles something the user may have already saved for later.
- You need a shortlist of candidates before broader web research.
- You want to avoid repeating analysis already saved in local agent memory.

Call `search_stars` for keyword lookup, `recommend_stars_for_task` for task-based ranking, and `get_star` for one known repo.

## When External Research Is Still Required

For major route decisions, do not rely only on local stars. You must search the web and compare at least 3 mature external projects when the decision affects:

- architecture shape
- repository structure
- commercialization or distribution
- license
- payment or account systems
- deployment, compliance, or security route

Local stars are a memory aid, not proof of current best practice.

## Output Shape

When recommending repos, include:

- repository name
- why it fits
- why it may not fit
- cost or risk
- next verification step

If local sync fails but stale cache is available, keep working and disclose the stale-cache status from the tool result.
