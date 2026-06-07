# GitHub Star Repository Analysis Prompt

Analyze one GitHub starred repository so Codex, Claude Code, OpenClaw, Hermes, and similar agents can decide whether to use it as local prior art.

Input:

- Repository: `{{full_name}}`
- README: `{{readme}}`
- Metadata: `{{metadata}}`

Return JSON only. Include every field:

```json
{
  "summary": "Explain in 1-3 sentences what the repository solves and why it matters for agent workflows.",
  "tags": ["3-8 short lowercase tags"],
  "category": "one stable category such as agent-tools, mcp, frontend, data-viz, automation, testing, infra",
  "platforms": ["target platforms such as codex, claude-code, openclaw, hermes, generic"],
  "notes": "Fit, non-fit, risks, and next validation step."
}
```

Rules:

- Do not treat README marketing claims as verified facts; place uncertainty in `notes`.
- For architecture, license, deployment, payment, or compliance decisions, recommend comparing at least 3 mature external projects online.
- If the repository is useful only as inspiration and not as a dependency, say so directly.
