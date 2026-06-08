import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.github_stars_radar.mcp import handle_request
from core.github_stars_radar.service import StarsRadarService
from core.github_stars_radar.env import load_env_file


def _read_message(stream):
    while True:
        first = stream.read(1)
        if not first:
            return None, None
        if first.strip():
            break

    if first == b"C":
        header = first
        while b"\r\n\r\n" not in header:
            chunk = stream.read(1)
            if not chunk:
                return None, None
            header += chunk
        content_length = None
        for line in header.decode("ascii").split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":", 1)[1].strip())
        if content_length is None:
            raise ValueError("Missing Content-Length header")
        body = stream.read(content_length)
        if len(body) != content_length:
            raise ValueError("Incomplete MCP frame body")
        return json.loads(body.decode("utf-8")), "frame"

    line = first + stream.readline()
    return json.loads(line.decode("utf-8").strip()), "line"


def _write_message(stream, response, mode):
    body = json.dumps(response, ensure_ascii=False).encode("utf-8")
    if mode == "frame":
        stream.write(b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body)
    else:
        stream.write(body + b"\n")
    stream.flush()


def main():
    load_env_file(os.path.join(ROOT, ".env"))
    if getattr(sys, "frozen", False):
        load_env_file(os.path.join(os.path.dirname(sys.executable), ".env"))
    db_path = os.environ.get("GITHUB_STARS_RADAR_DB") or os.environ.get("GITHUB_STARS_RADAR_CACHE") or "./data/stars.sqlite"
    service = StarsRadarService(db_path)
    try:
        stream_in = sys.stdin.buffer
        stream_out = sys.stdout.buffer
        while True:
            request, mode = _read_message(stream_in)
            if request is None:
                break
            response = handle_request(service, request)
            if response is not None:
                _write_message(stream_out, response, mode)
    finally:
        service.close()


if __name__ == "__main__":
    main()
