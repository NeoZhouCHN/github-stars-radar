import json
import os
import subprocess
import sys
import tempfile


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REQUIRED_TOOLS = {
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
}


def send(proc, payload):
    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["GITHUB_STARS_RADAR_DB"] = os.path.join(tmp, "stars.sqlite")
        proc = subprocess.Popen(
            ["py", os.path.join(ROOT, "mcp-server", "server.py")],
            cwd=ROOT,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            init = send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
            tools = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
            call = send(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "get_unanalyzed_stars", "arguments": {"auto_sync": False}},
                },
            )
        finally:
            proc.stdin.close()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.terminate()
                proc.wait(timeout=10)
        if "result" not in init:
            raise SystemExit(f"initialize failed: {init}")
        names = {tool["name"] for tool in tools["result"]["tools"]}
        missing = REQUIRED_TOOLS - names
        if missing:
            raise SystemExit(f"missing MCP tools: {sorted(missing)}")
        if "content" not in call.get("result", {}):
            raise SystemExit(f"tools/call failed: {call}")
    print("MCP smoke test passed")


if __name__ == "__main__":
    main()
