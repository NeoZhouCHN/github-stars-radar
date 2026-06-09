import json


TOOL_NAMES = [
    "sync_stars",
    "sync_readmes",
    "list_star_changes",
    "get_unanalyzed_stars",
    "list_categories",
    "get_star",
    "get_readme",
    "save_analysis",
    "search_stars",
    "recommend_stars_for_task",
    "export_codex_context",
]


TOOL_SCHEMAS = {
    "sync_stars": {
        "type": "object",
        "properties": {"include_removed": {"type": "boolean", "default": True}},
        "additionalProperties": False,
    },
    "sync_readmes": {
        "type": "object",
        "properties": {"limit": {"type": "integer", "default": 25, "minimum": 1}},
        "additionalProperties": False,
    },
    "list_star_changes": {
        "type": "object",
        "properties": {"limit": {"type": "integer", "default": 50, "minimum": 1}},
        "additionalProperties": False,
    },
    "get_unanalyzed_stars": {
        "type": "object",
        "properties": {
            "auto_sync": {"type": "boolean", "default": True},
            "max_cache_age_minutes": {"type": "integer", "default": 360, "minimum": 0},
            "allow_stale": {"type": "boolean", "default": True},
            "limit": {"type": "integer", "default": 50, "minimum": 1},
        },
        "additionalProperties": False,
    },
    "list_categories": {
        "type": "object",
        "properties": {
            "auto_sync": {"type": "boolean", "default": True},
            "max_cache_age_minutes": {"type": "integer", "default": 360, "minimum": 0},
            "allow_stale": {"type": "boolean", "default": True},
            "limit": {"type": "integer", "default": 50, "minimum": 1},
        },
        "additionalProperties": False,
    },
    "get_star": {
        "type": "object",
        "properties": {"full_name": {"type": "string"}},
        "required": ["full_name"],
        "additionalProperties": False,
    },
    "get_readme": {
        "type": "object",
        "properties": {"full_name": {"type": "string"}},
        "required": ["full_name"],
        "additionalProperties": False,
    },
    "save_analysis": {
        "type": "object",
        "properties": {
            "full_name": {"type": "string"},
            "summary": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "category": {"type": "string"},
            "platforms": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["full_name", "summary"],
        "additionalProperties": False,
    },
    "search_stars": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "default": ""},
            "category": {"type": "string"},
            "tag": {"type": "string"},
            "language": {"type": "string"},
            "auto_sync": {"type": "boolean", "default": True},
            "max_cache_age_minutes": {"type": "integer", "default": 360, "minimum": 0},
            "allow_stale": {"type": "boolean", "default": True},
            "limit": {"type": "integer", "default": 20, "minimum": 1},
        },
        "additionalProperties": False,
    },
    "recommend_stars_for_task": {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "auto_sync": {"type": "boolean", "default": True},
            "max_cache_age_minutes": {"type": "integer", "default": 360, "minimum": 0},
            "allow_stale": {"type": "boolean", "default": True},
            "limit": {"type": "integer", "default": 5, "minimum": 1},
        },
        "required": ["task"],
        "additionalProperties": False,
    },
    "export_codex_context": {
        "type": "object",
        "properties": {
            "full_names": {"type": "array", "items": {"type": "string"}},
            "task": {"type": "string"},
        },
        "required": ["full_names", "task"],
        "additionalProperties": False,
    },
}


def build_tool_list():
    return [
        {
            "name": name,
            "description": _description(name),
            "inputSchema": TOOL_SCHEMAS[name],
        }
        for name in TOOL_NAMES
    ]


def call_tool(service, name, arguments=None):
    arguments = arguments or {}
    if name not in TOOL_NAMES:
        raise ValueError(f"Unknown tool: {name}")
    _validate_arguments(name, arguments)
    method = getattr(service, name)
    result = method(**arguments)
    if name == "recommend_stars_for_task":
        return {
            "content": [
                {
                    "type": "text",
                    "text": _render_recommendation_markdown(result),
                },
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2),
                },
            ]
        }
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2),
            }
        ]
    }


def _validate_arguments(name, arguments):
    schema = TOOL_SCHEMAS[name]
    allowed = set(schema.get("properties", {}))
    unexpected = sorted(set(arguments) - allowed)
    if unexpected:
        raise ValueError(f"Unexpected arguments for {name}: {', '.join(unexpected)}")
    missing = [key for key in schema.get("required", []) if key not in arguments]
    if missing:
        raise ValueError(f"Missing required arguments for {name}: {', '.join(missing)}")


def _render_recommendation_markdown(result):
    lines = ["# Recommendation shortlist", ""]
    sync = result.get("sync") or {}
    if sync.get("status") == "failed":
        lines.extend([f"Sync: {sync.get('message', 'failed')}", ""])
    recommendations = result.get("recommendations") or []
    if not recommendations:
        lines.append("No matching starred repositories found.")
        return "\n".join(lines)
    for index, repo in enumerate(recommendations, 1):
        analysis = repo.get("analysis") or {}
        summary = analysis.get("summary") or repo.get("description") or "No summary saved yet."
        lines.extend(
            [
                f"{index}. {repo.get('full_name')} - {repo.get('score_summary', 'Score unavailable.')}",
                f"   - Why: {summary}",
                f"   - Fit: {repo.get('fit_reason', '')}",
                f"   - Watch: {repo.get('not_fit_reason', '')}",
                f"   - Next: {repo.get('next_validation', '')}",
            ]
        )
    return "\n".join(lines)


def handle_request(service, request):
    method = request.get("method")
    request_id = request.get("id")
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "github-stars-radar", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            }
        elif method == "tools/list":
            result = {"tools": build_tool_list()}
        elif method == "tools/call":
            params = request.get("params") or {}
            result = call_tool(service, params.get("name"), params.get("arguments") or {})
        elif method == "notifications/initialized":
            return None
        else:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}}


def _description(name):
    descriptions = {
        "sync_stars": "Force a fast metadata sync of current user's starred repositories from GitHub.",
        "sync_readmes": "Backfill missing README cache entries in small batches.",
        "list_star_changes": "List recent added, removed, and updated star changes.",
        "get_unanalyzed_stars": "List local stars without saved analysis or with stale analysis.",
        "list_categories": "List category counts from saved analysis and fallback uncategorized state.",
        "get_star": "Read one local star; sync once only when missing locally.",
        "get_readme": "Fetch the current README directly from GitHub.",
        "save_analysis": "Save structured agent analysis for a starred repository.",
        "search_stars": "Search local starred repositories with TTL auto-sync.",
        "recommend_stars_for_task": "Rank local stars that may help with a task.",
        "export_codex_context": "Render selected stars as a task-ready Codex research prompt.",
    }
    return descriptions[name]
