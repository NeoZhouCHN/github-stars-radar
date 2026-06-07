# GitHub Stars Radar

<p align="center">
  <img src="https://img.shields.io/badge/MCP-stdio-2f6fed?style=flat-square" alt="MCP stdio" />
  <img src="https://img.shields.io/badge/plugin-Codex%20%7C%20Claude%20Code-111827?style=flat-square" alt="Codex and Claude Code plugin" />
  <img src="https://img.shields.io/badge/storage-SQLite-1f8f4c?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/local--first-private-0f766e?style=flat-square" alt="local-first private" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT license" />
</p>

<p align="center">
  <b>把你的 GitHub Stars 变成 AI 编程助手可以搜索和复用的本地记忆库。</b>
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/README-ZH-d32f2f?style=for-the-badge" alt="中文" /></a>
  <a href="README.en.md"><img src="https://img.shields.io/badge/README-EN-111827?style=for-the-badge" alt="English" /></a>
</p>

> 视频文件不直接放在 README 首页里。GitHub 对 README 内嵌 MP4 支持不稳定，大文件也会拖慢主页。推荐把演示视频放到 Releases、B 站、YouTube、抖音或项目官网，再在这里放轻量链接。

## 中文

**GitHub Stars Radar** 可以把你 GitHub 里点过 Star 的仓库，变成 Codex、Claude Code、OpenClaw、Hermes 等 AI 编程工具能查询的“本地资料库”。

简单说：你以前收藏过很多好项目，但写代码时经常想不起来。这个项目会把 Stars 同步到本地，让 AI 能搜索、推荐、读取 README、保存分析结果。下次做选型、找参考实现、推荐工具时，AI 可以先查你收藏过的项目，而不是每次从零开始。

## 先让 AI 帮你安装

如果你正在 Codex 或 Claude Code 里看这个仓库，推荐先把下面这段 prompt 发给 AI。它会按客户端类型选择安装方式：

- **Codex**：优先安装 Codex plugin。
- **Claude Code**：优先安装 Claude Code plugin。
- **OpenClaw / Hermes**：按通用 stdio MCP server 接入。

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

## 功能一览

| 功能 | 小白解释 |
| --- | --- |
| 同步 GitHub Stars | 把你 GitHub 账号里 Star 过的仓库拉到本地 |
| 本地 SQLite 缓存 | 数据保存在你电脑上，不需要服务器 |
| 新增/删除/更新检测 | 知道哪些 Star 是新加的、取消的、信息变了的 |
| 保存 AI 分析 | AI 看过某个仓库后，可以把总结、标签、分类保存下来 |
| 自动刷新缓存 | 缓存太旧时自动同步；同步失败也能继续用旧缓存 |
| MCP 工具调用 | 支持 MCP 的客户端都能调用同一套 tools |
| Plugin 增强 | Codex / Claude Code 可以用 plugin 携带 MCP 和使用说明 |

## MCP 和 Plugin 有什么区别

| 形式 | 适合谁 | 说明 |
| --- | --- | --- |
| 通用 MCP | OpenClaw、Hermes、任何支持 stdio MCP 的客户端 | 最通用，只提供工具调用 |
| Codex plugin | Codex | 把 MCP 配置和说明打包起来，安装更方便 |
| Claude Code plugin | Claude Code | 把 MCP 配置、skills/说明一起作为插件安装 |

核心功能来自 MCP server，所以无论用 plugin 还是 MCP，调用的工具都是同一套：`sync_stars`、`search_stars`、`recommend_stars_for_task`、`get_readme`、`save_analysis` 等。

区别在于：plugin 更像安装包和说明书，MCP 是真正提供工具调用的服务。Skills/说明能不能自动触发，取决于客户端是否支持 plugin/skill 机制；MCP tools 本身是通用的。

## 安装前准备

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

## 下载和初始化

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

## 本地验证

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

## Codex：安装 Plugin

Codex 推荐优先用 plugin 方式安装。本仓库提供：

- `adapters/codex/.codex-plugin/plugin.json`
- `adapters/codex/.mcp.json`

基本步骤：

1. 下载本项目。
2. 配置 `.env` 或环境变量。
3. 把 `adapters/codex` 目录安装为 Codex plugin。
4. 如果你的 Codex 环境暂时不能安装本地 plugin，就把 `adapters/codex/.mcp.json` 里的 MCP 配置复制到 Codex 的 MCP 配置中。
5. 新开一个 Codex 会话，确认能看到 `github-stars-radar` 工具。

可以这样试：

```text
先用 GitHub Stars Radar 搜一下我收藏过的 MCP / agent 项目，推荐 5 个最适合当前任务的仓库，并说明适用原因、不适用原因和下一步验证方式。
```

## Claude Code：安装 Plugin

Claude Code 推荐优先用 plugin 方式安装。本仓库根目录提供：

- `.claude-plugin/plugin.json`
- `.mcp.json`
- `skills/github-stars-radar/SKILL.md`

基本步骤：

1. 下载本项目。
2. 配置 `.env` 或环境变量。
3. 把仓库根目录安装为 Claude Code plugin。
4. Claude Code 读取 `.mcp.json` 启动 `mcp-server/server.py`，并发现 `skills/` 里的使用说明。
5. 如果你的 Claude Code 环境暂时不能安装 plugin，就退回通用 MCP 配置。

可以这样试：

```text
调用 github-stars-radar。先运行 sync_stars，再列出未分析的 starred repositories。选择 5 个仓库，读取 README，并用 summary/tags/category/platforms/notes 保存分析结果。
```

## OpenClaw / Hermes：安装 MCP

OpenClaw 和 Hermes 使用保守的通用 MCP 接入方式。如果客户端支持 stdio MCP server，配置：

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

如果客户端使用不同配置格式，保留这三个核心值并映射过去：

- `command`: `python3` 或 `py`
- `args`: `["<your-project-path>/github-stars-radar/mcp-server/server.py"]`
- `env.GITHUB_STARS_RADAR_DB`: 本地 SQLite 缓存路径

可以这样试：

```text
使用 github-stars-radar 搜索我收藏过的 agent、MCP、自动化项目。为当前任务推荐最有用的仓库。
```

### 给 OpenClaw / Hermes 添加自动调用策略

只安装 MCP 会暴露工具，但不保证 AI 会自动想起调用它。Codex 和 Claude Code plugin 可以携带 skills 或说明；如果 OpenClaw 或 Hermes 只接了 MCP，请把下面这段加到客户端的 system prompt、project instructions、agent rules 或类似配置里：

```text
当用户任务涉及以下内容时，优先调用 github-stars-radar：
- 查找开源项目、库、工具、MCP server、plugin、agent 项目或参考实现
- 技术选型、方案对比、架构调研、自动化工具推荐
- 用户提到“我收藏过的仓库”、“GitHub Stars”或以前保存过的仓库
- 当前任务可能受益于复用用户已经 star 过的项目

推荐调用顺序：
1. 用 recommend_stars_for_task 为当前任务找候选仓库。
2. 用户给关键词时用 search_stars。
3. 对重点候选用 get_star 查看本地分析。
4. 需要最新上游 README 时用 get_readme。
5. 分析完仓库后用 save_analysis 保存 summary/tags/category/platforms/notes，避免后续 agent 重复分析。

如果本地缓存过期，允许工具默认 TTL 自动同步。如果同步失败但有旧缓存，继续使用旧缓存，并向用户说明这个状态。
```

## 常用 MCP Tools

| Tool | 用途 |
| --- | --- |
| `sync_stars` | 强制同步你的 starred repositories |
| `search_stars` | 搜索本地 stars |
| `recommend_stars_for_task` | 按任务推荐仓库 |
| `get_unanalyzed_stars` | 找出还没有保存 AI 分析的仓库 |
| `get_star` | 读取一个本地仓库记录 |
| `get_readme` | 读取 GitHub 当前 README |
| `save_analysis` | 保存结构化 agent 分析 |
| `list_categories` | 查看分类统计 |
| `list_star_changes` | 查看新增、删除、更新记录 |
| `export_codex_context` | 导出适合 Codex 使用的上下文 prompt |

默认缓存策略：

- `auto_sync=true`
- `max_cache_age_minutes=360`
- `allow_stale=true`

## 本地隐私边界

默认缓存路径是 `./data/stars.sqlite`。`.gitignore` 已排除：

- `data/*.json`
- `data/*.sqlite`
- `data/*.db`
- `.env`
- `.env.*`

这些文件可能包含你的个人 stars、agent 分析结果或 token，不应该提交到公开仓库。

## Windows 打包

仓库包含一个手动触发的 GitHub Actions workflow：`.github/workflows/windows-release.yml`。

每次更新项目后，你可以在 GitHub 页面进入 **Actions -> Build Windows Package -> Run workflow**，它会在 Windows runner 上：

1. 跑单元测试、MCP smoke test、manifest 校验。
2. 用 PyInstaller 打包 `github-stars-radar.exe`。
3. 生成 portable zip。
4. 如果 Inno Setup 可用，生成 `GitHubStarsRadarSetup-<version>.exe` 安装包。
5. 把 zip、安装包和 SHA256 校验文件上传为 workflow artifacts。

如果你要正式发布版本，可以下载 artifacts 后手动上传到 GitHub Releases；后续也可以再加自动创建 Release 的步骤。

## Repo 分析 Prompts

- `prompts/repo-analysis.zh.md`
- `prompts/repo-analysis.en.md`

两个 prompt 都要求结构化输出：`summary`、`tags`、`category`、`platforms`、`notes`。

## License

MIT License. See `LICENSE`.
