# GitHub Star 仓库分析 Prompt

请分析一个 GitHub starred repository，目标是帮助 Codex、Claude Code、OpenClaw、Hermes 等 agent 在后续任务中判断是否值得优先参考。

输入信息：

- 仓库名：`{{full_name}}`
- README：`{{readme}}`
- metadata：`{{metadata}}`

请只输出 JSON，不要输出 Markdown。字段必须完整：

```json
{
  "summary": "用 1-3 句话说明这个仓库解决什么问题，以及它对 agent 工作流的价值。",
  "tags": ["3-8 个短标签，小写短语"],
  "category": "一个稳定分类，例如 agent-tools、mcp、frontend、data-viz、automation、testing、infra",
  "platforms": ["适用平台，例如 codex、claude-code、openclaw、hermes、generic"],
  "notes": "适用原因、不适用原因、风险、下一步验证。"
}
```

判断规则：

- 不要把 README 的营销词当成事实；把未验证的信息写进 `notes`。
- 如果仓库涉及架构、License、部署、支付或合规路线，必须建议联网对比至少 3 个成熟外部项目。
- 如果仓库只适合做灵感，不适合作为依赖，要直接说明。
