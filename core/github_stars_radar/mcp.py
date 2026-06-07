import json


TOOL_NAMES = [
    "sync_stars",
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


def build_tool_list():
    return [
        {
            "name": name,
            "description": _description(name),
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": True},
        }
        for name in TOOL_NAMES
    ]


def call_tool(service, name, arguments=None):
    arguments = arguments or {}
    if name not in TOOL_NAMES:
        raise ValueError(f"Unknown tool: {name}")
    method = getattr(service, name)
    result = method(**arguments)
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False, indent=2),
            }
        ]
    }


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
        "sync_stars": "Force sync current user's starred repositories from GitHub.",
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
