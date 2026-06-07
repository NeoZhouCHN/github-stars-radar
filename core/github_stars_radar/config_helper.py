import argparse
import json
import os
import sys
from pathlib import Path


APP_NAME = "github-stars-radar"


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def server_command(base_dir=None):
    base = Path(base_dir) if base_dir else app_dir()
    for binary_name in ["github-stars-radar.exe", "github-stars-radar"]:
        exe = base / binary_name
        if exe.exists():
            return str(exe), []
    return "py", [str(base / "mcp-server" / "server.py")]


def write_env(base_dir, token="", db_path=None):
    base = Path(base_dir)
    target = base / ".env"
    db_value = db_path or str(base / "data" / "stars.sqlite")
    lines = [
        "# GitHub Stars Radar local configuration",
        "# Keep this file private. Do not commit it.",
        f"GITHUB_TOKEN={token.strip()}",
        "GH_TOKEN=",
        f"GITHUB_STARS_RADAR_DB={db_value}",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def mcp_config(base_dir, token_in_env=False):
    base = Path(base_dir)
    command, args = server_command(base)
    env = {
        "GITHUB_STARS_RADAR_DB": str(base / "data" / "stars.sqlite"),
    }
    if token_in_env:
        env["GITHUB_TOKEN"] = "${GITHUB_TOKEN}"
    return {
        "mcpServers": {
            APP_NAME: {
                "command": command,
                "args": args,
                "env": env,
            }
        }
    }


def write_mcp_config(base_dir):
    base = Path(base_dir)
    output_dir = base / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "github-stars-radar.mcp.json"
    target.write_text(json.dumps(mcp_config(base), indent=2), encoding="utf-8")
    return target


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="Configure GitHub Stars Radar locally.")
    parser.add_argument("--base-dir", default=str(app_dir()), help="Installed GitHub Stars Radar directory.")
    parser.add_argument("--token", default="", help="GitHub token to write into .env.")
    parser.add_argument("--write-env", action="store_true", help="Write .env.")
    parser.add_argument("--write-mcp", action="store_true", help="Write generated/github-stars-radar.mcp.json.")
    args = parser.parse_args(argv)

    if not args.write_env and not args.write_mcp:
        return run_gui(args.base_dir)

    written = []
    if args.write_env:
        written.append(write_env(args.base_dir, args.token))
    if args.write_mcp:
        written.append(write_mcp_config(args.base_dir))
    for path in written:
        print(path)
    return 0


def run_gui(base_dir):
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception as exc:
        print(f"GUI unavailable: {exc}", file=sys.stderr)
        print("Use --write-env and --write-mcp from a terminal.", file=sys.stderr)
        return 2

    root = tk.Tk()
    root.title("GitHub Stars Radar Config")
    root.geometry("720x430")

    token_var = tk.StringVar()
    base = Path(base_dir)

    tk.Label(root, text="GitHub Stars Radar Config", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=(24, 8))
    tk.Label(root, text=f"Install directory: {base}", wraplength=660, justify="left").pack(anchor="w", padx=24)
    tk.Label(root, text="Paste a GitHub token if you want this helper to create .env. Leave blank to create only MCP config.", wraplength=660, justify="left").pack(anchor="w", padx=24, pady=(18, 4))
    entry = tk.Entry(root, textvariable=token_var, show="*", width=86)
    entry.pack(anchor="w", padx=24, pady=(0, 12))

    output = tk.Text(root, height=8, width=86)
    output.pack(anchor="w", padx=24, pady=(8, 12))

    def generate():
        written = []
        token = token_var.get().strip()
        if token:
            written.append(write_env(base, token))
        written.append(write_mcp_config(base))
        output.delete("1.0", tk.END)
        output.insert(tk.END, "Generated files:\n")
        for path in written:
            output.insert(tk.END, f"- {path}\n")
        output.insert(tk.END, "\nAdd generated/github-stars-radar.mcp.json to your MCP-compatible client.\n")
        messagebox.showinfo("GitHub Stars Radar", "Configuration files generated.")

    tk.Button(root, text="Generate Config Files", command=generate).pack(anchor="w", padx=24)
    root.mainloop()
    return 0


def main():
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
