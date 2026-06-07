import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.github_stars_radar.mcp import handle_request
from core.github_stars_radar.service import StarsRadarService
from core.github_stars_radar.env import load_env_file


def main():
    load_env_file(os.path.join(ROOT, ".env"))
    if getattr(sys, "frozen", False):
        load_env_file(os.path.join(os.path.dirname(sys.executable), ".env"))
    db_path = os.environ.get("GITHUB_STARS_RADAR_DB") or os.environ.get("GITHUB_STARS_RADAR_CACHE") or "./data/stars.sqlite"
    service = StarsRadarService(db_path)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = handle_request(service, json.loads(line))
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
    finally:
        service.close()


if __name__ == "__main__":
    main()
