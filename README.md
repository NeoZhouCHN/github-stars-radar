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
  <a href="#zh"><img src="https://img.shields.io/badge/README-ZH-d32f2f?style=for-the-badge" alt="中文" /></a>
  <a href="#en"><img src="https://img.shields.io/badge/README-EN-111827?style=for-the-badge" alt="English" /></a>
</p>

---

<p align="center">
  <video src="videos/product-launch-final.mp4" controls playsinline width="100%"></video>
</p>

<p align="center">
  <a href="videos/product-launch-final.mp4">观看 30 秒中文介绍视频 / Watch the 30s Chinese intro video</a>
</p>

<h2 id="zh">中文</h2>

**GitHub Stars Radar** 可以把你 GitHub 里点过 Star 的仓库，变成 Codex、Claude Code、OpenClaw、Hermes 等 AI 编程工具能查询的“本地资料库”。

最简单的理解：你以前收藏过很多好项目，但 AI 不知道。这个项目把这些收藏同步到本地，让 AI 能搜索、推荐、保存分析结果，下次遇到类似任务就不用从零开始找资料。

### 先让 AI 帮你安装

如果你正在 Codex 或 Claude Code 里看这个仓库，推荐先把下面这段 prompt 发给 AI。它会按客户端类型选择正确安装方式：

- **Codex**：安装 Codex plugin。
- **Claude Code**：安装 Claude Code plugin。
- **OpenClaw / Hermes**：安装通用 stdio MCP server。

```text
请帮我安装并接入 GitHub Stars Radar。

项目仓库：https://github.com/NeoZhouCHN/github-stars-radar
本地项目路径：<your-project-path>/github-stars-radar
目标客户端：Codex / Claude Code / OpenClaw / Hermes（选择一个或多个）

请你：
1. 检查 Python 是否可用。Windows 优先尝试 py，macOS/Linux 优先尝试 python3。
2. 检查 .env 是否存在；如果不存在，从 .env.example 复制一份。不要读取、打印或记录我的 token。
3. 检查 GITHUB_TOKEN、GH_TOKEN 或 gh auth token 是否至少一种可用。
4. 如果目标客户端是 Codex：优先安装 adapters/codex/.codex-plugin/plugin.json；如果当前 Codex 环境不能安装 plugin，再退回通用 MCP 配置。
5. 如果目标客户端是 Claude Code：优先按仓库根目录的 .claude-plugin/plugin.json 和 .mcp.json 安装 plugin；如果当前 Claude Code 环境不能安装 plugin，再退回通用 MCP 配置。
6. 如果目标客户端是 OpenClaw 或 Hermes：按 stdio MCP server 方式接入，command 使用 py 或 python3，args 指向 mcp-server/server.py，env 设置 GITHUB_STARS_RADAR_DB。
7. 运行 scripts/smoke_mcp.py 做 smoke test。
8. 最后告诉我：修改了哪些配置文件、验证命令是否通过、我下一步应该怎么调用 github-stars-radar。

不要提交 data/*.sqlite、data/*.json、.env 或任何 token。
```

### 功能一览

| 功能 | 小白解释 |
| --- | --- |
| 同步 GitHub Stars | 把你 GitHub 账号里 Star 过的仓库拉到本地 |
| 本地 SQLite 缓存 | 数据保存在你电脑上，不需要服务器 |
| 新增/删除/更新检测 | 知道哪些 Star 是新加的、取消的、信息变了的 |
| 保存 AI 分析 | AI 看过某个仓库后，可以把总结、标签、分类保存下来 |
| 自动刷新缓存 | 缓存太旧时自动同步；同步失败也能继续用旧缓存 |
| MCP 工具调用 | 支持 MCP 的客户端都能调用同一套 tools |
| Plugin 增强 | Codex / Claude Code 可以用 plugin 方式携带 MCP 和使用说明 |

### MCP 和 Plugin 有什么区别

| 形式 | 适合谁 | 说明 |
| --- | --- | --- |
| 通用 MCP | OpenClaw、Hermes、任何支持 stdio MCP 的客户端 | 最通用，只提供工具调用 |
| Codex plugin | Codex | 把 MCP 配置和说明打包起来，安装更方便 |
| Claude Code plugin | Claude Code | 把 MCP 配置、skills/说明一起作为插件安装 |

核心功能来自 MCP server，所以无论用 plugin 还是 MCP，调用的工具都是同一套：`sync_stars`、`search_stars`、`recommend_stars_for_task`、`get_readme`、`save_analysis` 等。

区别在于：**plugin 更像安装包和说明书，MCP 是真正提供工具调用的服务。** Skills/说明能不能自动触发，取决于客户端是否支持 plugin/skill 机制；MCP tools 本身是通用的。

### 安装前准备

你需要：

- Python 3.11 或更高版本
- 一个 GitHub Token，或已经登录好的 `gh` CLI
- 本项目源码

`GITHUB_TOKEN` 和 `GH_TOKEN` 都是环境变量名，用来存放 GitHub Personal Access Token。你只需要填其中一个；如果两个都填，项目会优先读取 `GITHUB_TOKEN`。`GH_TOKEN` 这个名字常见于 GitHub CLI 和自动化脚本。

获取 token：

- GitHub 官方说明：[Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- Fine-grained token 创建页：[https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
- Classic token 创建页：[https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

只同步公开 star 时，GitHub Token 通常不需要额外权限。若要读取 private starred repositories，token 需要能读取这些 private repositories。创建后只复制一次，像密码一样保存，不要发给 AI，也不要提交到 GitHub。

### 下载和初始化

把 `<your-project-path>` 换成你自己电脑上的项目目录。

Windows PowerShell：

```powershell
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
copy .env.example .env
```

macOS / Linux：

```bash
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
cp .env.example .env
```

编辑 `.env`，二选一填入 token：

```text
GITHUB_TOKEN=你的 GitHub token
GH_TOKEN=
GITHUB_STARS_RADAR_DB=./data/stars.sqlite
```

或者：

```text
GITHUB_TOKEN=
GH_TOKEN=你的 GitHub token
GITHUB_STARS_RADAR_DB=./data/stars.sqlite
```

如果你已经安装并登录 `gh` CLI，也可以不填 token：

```powershell
gh auth login
gh auth token
```

### 本地测试

Windows：

```powershell
py -m unittest discover -s tests -v
py scripts/smoke_mcp.py
py scripts/check_manifests.py
```

macOS / Linux：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/smoke_mcp.py
python3 scripts/check_manifests.py
```

### Codex：安装 Plugin

Codex 优先使用 plugin 方式。仓库里已经有：

- `adapters/codex/.codex-plugin/plugin.json`
- `adapters/codex/.mcp.json`

安装思路：

1. 下载本项目。
2. 配置 `.env` 或系统环境变量。
3. 在 Codex 中安装 `adapters/codex` 这个 plugin 目录。
4. 如果你的 Codex 环境不能直接安装本地 plugin，就把 `adapters/codex/.mcp.json` 的内容加入 Codex MCP 配置。
5. 新开 Codex 会话，确认能看到 `github-stars-radar` tools。

接入后可以问：

```text
先用 GitHub Stars Radar 搜一下我收藏过的 MCP / agent 项目，推荐 5 个最适合当前任务的仓库，并说明适用原因、不适用原因和下一步验证方式。
```

### Claude Code：安装 Plugin

Claude Code 优先使用 plugin 方式。仓库根目录已经有：

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/github-stars-radar/SKILL.md`

安装思路：

1. 下载本项目。
2. 配置 `.env` 或系统环境变量。
3. 在 Claude Code 中把仓库根目录作为 plugin 安装。
4. Claude Code plugin 会读取 `.mcp.json` 启动 `mcp-server/server.py`，并发现 `skills/` 下的使用说明。
5. 如果当前 Claude Code 环境不能安装 plugin，就退回通用 MCP 配置。

接入后可以问：

```text
请调用 github-stars-radar，先 sync_stars，然后找出还没有分析过的 starred repositories。每次选 5 个，读取 README 后按 summary/tags/category/platforms/notes 保存分析结果。
```

### OpenClaw / Hermes：安装 MCP

OpenClaw 和 Hermes 这里采用保守的通用 MCP 方案。只要客户端支持 stdio MCP server，就填写同一组核心配置：

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

Windows 可以把 `command` 改成 `py`。

如果 Hermes 或 OpenClaw 的实际配置格式不是 `mcpServers`，请保留这三个核心信息并按客户端自己的格式填写：

- `command`: `python3` 或 `py`
- `args`: `["<your-project-path>/github-stars-radar/mcp-server/server.py"]`
- `env.GITHUB_STARS_RADAR_DB`: 本地 SQLite 缓存路径

接入后可以问：

```text
请调用 github-stars-radar，搜索我 Star 过的 agent、MCP、automation 项目，按当前任务推荐最值得参考的仓库。
```

#### 给 OpenClaw / Hermes 添加自动调用策略

纯 MCP 安装只提供 tools，不保证 AI 会自动想起来调用。Codex / Claude Code 的 plugin 可以携带 skills 或 instructions；OpenClaw / Hermes 如果只按 MCP 接入，就建议再把下面这段放到客户端的 system prompt、project instructions、agent rules 或类似配置里：

```text
当用户任务涉及以下场景时，优先调用 github-stars-radar：
- 查找开源项目、库、工具、MCP server、plugin、agent 项目或参考实现
- 技术选型、方案对比、架构调研、自动化工具推荐
- 用户提到“我收藏过的项目”“GitHub Stars”“找之前看过的仓库”
- 当前任务可能受益于复用用户已经 Star 过的仓库

推荐调用顺序：
1. 先用 recommend_stars_for_task 按当前任务找候选仓库。
2. 如果用户给了关键词，用 search_stars 搜索本地 stars。
3. 对重要候选仓库，用 get_star 查看本地分析。
4. 需要最新信息时，用 get_readme 获取当前 README。
5. 如果完成了仓库分析，用 save_analysis 保存 summary/tags/category/platforms/notes，避免下次重复分析。

如果本地缓存过期，允许工具按默认 TTL 自动同步。若同步失败但有旧缓存，可以继续使用旧缓存，并把 stale cache 状态告诉用户。
```

### 常用 MCP Tools

| Tool | 用途 |
| --- | --- |
| `sync_stars` | 强制同步当前用户 starred repositories |
| `search_stars` | 按关键词搜索本地 stars |
| `recommend_stars_for_task` | 按当前任务推荐相关 stars |
| `get_unanalyzed_stars` | 找出还没被 AI 分析过的 stars |
| `get_star` | 查看单个仓库的本地信息和分析结果 |
| `get_readme` | 直接读取 GitHub 当前 README |
| `save_analysis` | 保存 AI 对仓库的结构化分析 |
| `list_categories` | 查看已有分类统计 |
| `list_star_changes` | 查看新增、删除、更新记录 |
| `export_codex_context` | 导出给 Codex 使用的上下文 prompt |

默认缓存策略：

- `auto_sync=true`
- `max_cache_age_minutes=360`
- `allow_stale=true`

### 本地隐私边界

默认缓存位置是 `./data/stars.sqlite`。`.gitignore` 已排除：

- `data/*.json`
- `data/*.sqlite`
- `data/*.db`
- `.env`
- `.env.*`

这些文件通常包含你的个人 stars、AI 分析结果或 token，不应该提交到公开仓库。

### Repo Analysis Prompts

- `prompts/repo-analysis.zh.md`
- `prompts/repo-analysis.en.md`

两个 prompt 都要求结构化输出：`summary`、`tags`、`category`、`platforms`、`notes`。

### License

MIT License. See `LICENSE`.

---

<h2 id="en">English</h2>

**GitHub Stars Radar** turns your GitHub starred repositories into a local knowledge base that AI coding agents can search and reuse.

Short version: you save useful repositories with GitHub stars, but your AI coding tool does not know why you saved them. This project syncs those stars locally, lets agents search them, and stores reusable analysis for future tasks.

### Let AI Install It First

If you are reading this inside Codex or Claude Code, paste this prompt first. It tells the agent which installation route to use:

- **Codex**: install the Codex plugin.
- **Claude Code**: install the Claude Code plugin.
- **OpenClaw / Hermes**: install the generic stdio MCP server.

```text
Please install and connect GitHub Stars Radar.

Repository: https://github.com/NeoZhouCHN/github-stars-radar
Local project path: <your-project-path>/github-stars-radar
Target client: Codex / Claude Code / OpenClaw / Hermes

Please:
1. Check that Python works. On Windows try py first; on macOS/Linux try python3 first.
2. Ensure .env exists. If it does not exist, copy it from .env.example. Do not read, print, or record my token.
3. Check that GITHUB_TOKEN, GH_TOKEN, or gh auth token is available.
4. If the target client is Codex: prefer installing adapters/codex/.codex-plugin/plugin.json. If local plugin install is unavailable, fall back to generic MCP config.
5. If the target client is Claude Code: prefer installing the repository root as a plugin using .claude-plugin/plugin.json and .mcp.json. If plugin install is unavailable, fall back to generic MCP config.
6. If the target client is OpenClaw or Hermes: connect it as a stdio MCP server. Use py or python3 as command, point args to mcp-server/server.py, and set GITHUB_STARS_RADAR_DB.
7. Run scripts/smoke_mcp.py.
8. Tell me which config files changed, which verification commands passed, and how to call github-stars-radar next.

Do not commit data/*.sqlite, data/*.json, .env, or any token.
```

### Features

| Feature | Plain-English meaning |
| --- | --- |
| GitHub Stars sync | Pull your starred repositories into a local cache |
| Local SQLite cache | Store data on your own machine |
| Added/removed/updated detection | Track new stars, unstarred repos, and changed metadata |
| Agent analysis storage | Save summaries, tags, categories, platforms, and notes |
| TTL auto-sync | Refresh stale cache, but keep using old cache if sync fails |
| MCP tools | Let any MCP client call the same tool set |
| Plugin packaging | Codex and Claude Code can install a plugin wrapper |

### MCP vs Plugin

| Form | Best for | Meaning |
| --- | --- | --- |
| Generic MCP | OpenClaw, Hermes, any stdio MCP client | Most portable; exposes tools |
| Codex plugin | Codex | Packages MCP config and usage guidance |
| Claude Code plugin | Claude Code | Packages MCP config and skills/instructions |

The core functionality comes from the MCP server. Plugin mode and MCP mode call the same tools: `sync_stars`, `search_stars`, `recommend_stars_for_task`, `get_readme`, `save_analysis`, and others.

The difference is that a plugin is an installer/packaging layer. Skills or instructions may auto-trigger only when the client supports that plugin/skill mechanism. MCP tools themselves are portable.

### Requirements

- Python 3.11 or newer
- A GitHub token, or an authenticated `gh` CLI
- This project checked out locally

`GITHUB_TOKEN` and `GH_TOKEN` are environment variable names for a GitHub Personal Access Token. You only need to set one of them. If both are set, this project reads `GITHUB_TOKEN` first. `GH_TOKEN` is common in GitHub CLI and automation workflows.

Get a token:

- Official GitHub docs: [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- Fine-grained token page: [https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
- Classic token page: [https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)

For public stars, a classic GitHub token usually needs no extra scopes. For private starred repositories, the token must be able to read those private repositories. Copy the token once, treat it like a password, do not paste it into AI chats, and do not commit it.

### Download And Initialize

Replace `<your-project-path>` with your local project directory.

macOS / Linux:

```bash
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
cp .env.example .env
```

Windows PowerShell:

```powershell
git clone https://github.com/NeoZhouCHN/github-stars-radar.git
cd <your-project-path>/github-stars-radar
copy .env.example .env
```

Edit `.env` and set one token variable:

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

If you already use GitHub CLI:

```bash
gh auth login
gh auth token
```

### Local Verification

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

### Codex: Install Plugin

Codex should prefer plugin installation. This repository includes:

- `adapters/codex/.codex-plugin/plugin.json`
- `adapters/codex/.mcp.json`

Basic route:

1. Download this project.
2. Configure `.env` or environment variables.
3. Install the `adapters/codex` directory as a Codex plugin.
4. If local plugin installation is unavailable, copy `adapters/codex/.mcp.json` into your Codex MCP config.
5. Start a new Codex session and check that `github-stars-radar` tools are available.

Try this in Codex:

```text
Use GitHub Stars Radar to search my starred MCP and agent projects. Recommend 5 repositories for the current task, with fit reason, non-fit reason, and next validation step.
```

### Claude Code: Install Plugin

Claude Code should prefer plugin installation. The repository root includes:

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/github-stars-radar/SKILL.md`

Basic route:

1. Download this project.
2. Configure `.env` or environment variables.
3. Install the repository root as a Claude Code plugin.
4. Claude Code reads `.mcp.json` to start `mcp-server/server.py` and discovers usage guidance under `skills/`.
5. If plugin installation is unavailable, fall back to generic MCP config.

Try this in Claude Code:

```text
Call github-stars-radar. First run sync_stars, then list unanalyzed starred repositories. Pick 5 repos, read their README, and save analysis with summary/tags/category/platforms/notes.
```

### OpenClaw / Hermes: Install MCP

OpenClaw and Hermes use the conservative generic MCP route. If the client supports stdio MCP servers, configure:

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

If the client uses a different config schema, keep these three values and map them into that schema:

- `command`: `python3` or `py`
- `args`: `["<your-project-path>/github-stars-radar/mcp-server/server.py"]`
- `env.GITHUB_STARS_RADAR_DB`: local SQLite cache path

Try this:

```text
Use github-stars-radar to search my starred agent, MCP, and automation projects. Recommend the most useful repositories for the current task.
```

#### Add Auto-Call Instructions For OpenClaw / Hermes

Plain MCP installation exposes tools, but it does not guarantee that the AI will automatically remember to call them. Codex and Claude Code plugins can carry skills or instructions. If OpenClaw or Hermes is connected only through MCP, add the following text to the client's system prompt, project instructions, agent rules, or equivalent configuration:

```text
Prefer calling github-stars-radar when the user's task involves:
- finding open-source projects, libraries, tools, MCP servers, plugins, agent projects, or reference implementations
- technical selection, solution comparison, architecture research, or automation tool recommendations
- mentions of "my starred repos", "GitHub Stars", or previously saved repositories
- tasks that may benefit from reusing repositories the user has already starred

Recommended call order:
1. Use recommend_stars_for_task to find candidate repositories for the current task.
2. Use search_stars when the user provides keywords.
3. Use get_star to inspect local analysis for important candidates.
4. Use get_readme when current upstream README content is needed.
5. Use save_analysis after analyzing a repository, storing summary/tags/category/platforms/notes so future agents do not repeat the work.

If the local cache is stale, allow the tool's default TTL auto-sync. If sync fails but stale cache exists, continue with stale local cache and disclose that status to the user.
```

### Common MCP Tools

| Tool | Purpose |
| --- | --- |
| `sync_stars` | Force sync your starred repositories |
| `search_stars` | Search local stars |
| `recommend_stars_for_task` | Recommend repos for a task |
| `get_unanalyzed_stars` | Find stars without saved analysis |
| `get_star` | Read one local repo |
| `get_readme` | Fetch the current README from GitHub |
| `save_analysis` | Save structured agent analysis |
| `list_categories` | Show category counts |
| `list_star_changes` | Show added, removed, and updated records |
| `export_codex_context` | Export a Codex-ready context prompt |

Default cache policy:

- `auto_sync=true`
- `max_cache_age_minutes=360`
- `allow_stale=true`

### Local Privacy Boundary

The default cache path is `./data/stars.sqlite`. `.gitignore` excludes:

- `data/*.json`
- `data/*.sqlite`
- `data/*.db`
- `.env`
- `.env.*`

These files may contain personal stars, agent analysis, or tokens and should not be committed to a public repository.

### Repo Analysis Prompts

- `prompts/repo-analysis.zh.md`
- `prompts/repo-analysis.en.md`

Both prompts require structured output fields: `summary`, `tags`, `category`, `platforms`, and `notes`.

### License

MIT License. See `LICENSE`.
