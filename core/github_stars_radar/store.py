import json
import os
import sqlite3
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class StarsStore:
    def __init__(self, path):
        self.path = path
        parent = os.path.dirname(os.path.abspath(path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.migrate()

    def migrate(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS repos (
                full_name TEXT PRIMARY KEY,
                github_id INTEGER,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                description TEXT,
                html_url TEXT,
                language TEXT,
                topics_json TEXT NOT NULL DEFAULT '[]',
                stars INTEGER NOT NULL DEFAULT 0,
                forks INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT,
                pushed_at TEXT,
                metadata_hash TEXT NOT NULL,
                readme_hash TEXT NOT NULL DEFAULT '',
                readme_text TEXT NOT NULL DEFAULT '',
                prompt_version TEXT NOT NULL DEFAULT '',
                analysis_summary TEXT,
                analysis_tags_json TEXT NOT NULL DEFAULT '[]',
                analysis_category TEXT,
                analysis_platforms_json TEXT NOT NULL DEFAULT '[]',
                analysis_notes TEXT,
                analysis_stale INTEGER NOT NULL DEFAULT 1,
                removed INTEGER NOT NULL DEFAULT 0,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                removed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL,
                added INTEGER NOT NULL DEFAULT 0,
                removed INTEGER NOT NULL DEFAULT 0,
                updated INTEGER NOT NULL DEFAULT 0,
                message TEXT
            );
            CREATE TABLE IF NOT EXISTS star_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                change_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self._ensure_column("repos", "readme_text", "TEXT NOT NULL DEFAULT ''")
        self.conn.commit()

    def _ensure_column(self, table, column, definition):
        columns = {row["name"] for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def record_sync(self, status, added=0, removed=0, updated=0, message=""):
        started_at = utc_now()
        cursor = self.conn.execute(
            "INSERT INTO sync_runs (started_at, status, added, removed, updated, message) VALUES (?, ?, ?, ?, ?, ?)",
            (started_at, status, added, removed, updated, message),
        )
        self.conn.commit()
        return cursor.lastrowid, started_at

    def update_sync(self, run_id, status, added=0, removed=0, updated=0, message=""):
        self.conn.execute(
            "UPDATE sync_runs SET status = ?, added = ?, removed = ?, updated = ?, message = ? WHERE id = ?",
            (status, added, removed, updated, message, run_id),
        )
        self.conn.commit()

    def add_change(self, run_id, full_name, change_type):
        self.conn.execute(
            "INSERT INTO star_changes (run_id, full_name, change_type, created_at) VALUES (?, ?, ?, ?)",
            (run_id, full_name, change_type, utc_now()),
        )
        self.conn.commit()

    def get_last_sync(self):
        row = self.conn.execute("SELECT * FROM sync_runs ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def get_last_successful_sync(self):
        row = self.conn.execute("SELECT * FROM sync_runs WHERE status = 'refreshed' ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def set_last_sync_started_at(self, started_at):
        row = self.get_last_sync()
        if row:
            self.conn.execute("UPDATE sync_runs SET started_at = ? WHERE id = ?", (started_at, row["id"]))
            self.conn.commit()

    def upsert_repo(self, data):
        existing = self.get_repo(data["full_name"])
        first_seen = existing["first_seen_at"] if existing else utc_now()
        self.conn.execute(
            """
            INSERT INTO repos (
                full_name, github_id, name, owner, description, html_url, language, topics_json,
                stars, forks, updated_at, pushed_at, metadata_hash, readme_hash, readme_text, prompt_version,
                analysis_summary, analysis_tags_json, analysis_category, analysis_platforms_json,
                analysis_notes, analysis_stale, removed, first_seen_at, last_seen_at, removed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, NULL)
            ON CONFLICT(full_name) DO UPDATE SET
                github_id=excluded.github_id,
                name=excluded.name,
                owner=excluded.owner,
                description=excluded.description,
                html_url=excluded.html_url,
                language=excluded.language,
                topics_json=excluded.topics_json,
                stars=excluded.stars,
                forks=excluded.forks,
                updated_at=excluded.updated_at,
                pushed_at=excluded.pushed_at,
                metadata_hash=excluded.metadata_hash,
                readme_hash=excluded.readme_hash,
                readme_text=excluded.readme_text,
                prompt_version=excluded.prompt_version,
                analysis_stale=excluded.analysis_stale,
                removed=0,
                last_seen_at=excluded.last_seen_at,
                removed_at=NULL
            """,
            (
                data["full_name"],
                data.get("github_id"),
                data["name"],
                data["owner"],
                data.get("description"),
                data.get("html_url"),
                data.get("language"),
                json.dumps(data.get("topics", []), ensure_ascii=False),
                data.get("stars", 0),
                data.get("forks", 0),
                data.get("updated_at"),
                data.get("pushed_at"),
                data["metadata_hash"],
                data.get("readme_hash", ""),
                data.get("readme_text", ""),
                data.get("prompt_version", ""),
                existing.get("analysis", {}).get("summary") if existing else None,
                json.dumps(existing.get("analysis", {}).get("tags", []) if existing else [], ensure_ascii=False),
                existing.get("analysis", {}).get("category") if existing else None,
                json.dumps(existing.get("analysis", {}).get("platforms", []) if existing else [], ensure_ascii=False),
                existing.get("analysis", {}).get("notes") if existing else None,
                1 if data.get("analysis_stale", True) else 0,
                first_seen,
                utc_now(),
            ),
        )
        self.conn.commit()

    def mark_removed(self, full_name):
        self.conn.execute(
            "UPDATE repos SET removed = 1, removed_at = ?, analysis_stale = 1 WHERE full_name = ?",
            (utc_now(), full_name),
        )
        self.conn.commit()

    def save_analysis(self, full_name, summary, tags, category, platforms, notes, prompt_version):
        self.conn.execute(
            """
            UPDATE repos SET
                analysis_summary = ?,
                analysis_tags_json = ?,
                analysis_category = ?,
                analysis_platforms_json = ?,
                analysis_notes = ?,
                prompt_version = ?,
                analysis_stale = 0
            WHERE full_name = ?
            """,
            (
                summary,
                json.dumps(tags, ensure_ascii=False),
                category,
                json.dumps(platforms, ensure_ascii=False),
                notes,
                prompt_version,
                full_name,
            ),
        )
        self.conn.commit()

    def get_repo(self, full_name):
        row = self.conn.execute("SELECT * FROM repos WHERE full_name = ?", (full_name,)).fetchone()
        return self._row_to_repo(row) if row else None

    def get_readme_text(self, full_name):
        row = self.conn.execute("SELECT readme_text FROM repos WHERE full_name = ?", (full_name,)).fetchone()
        return row["readme_text"] if row else ""

    def update_repo_readme(self, full_name, readme_hash, readme_text, analysis_stale):
        self.conn.execute(
            "UPDATE repos SET readme_hash = ?, readme_text = ?, analysis_stale = ? WHERE full_name = ?",
            (readme_hash, readme_text, 1 if analysis_stale else 0, full_name),
        )
        self.conn.commit()

    def list_repos(self, include_removed=False):
        sql = "SELECT * FROM repos"
        if not include_removed:
            sql += " WHERE removed = 0"
        sql += " ORDER BY full_name"
        return [self._row_to_repo(row) for row in self.conn.execute(sql).fetchall()]

    def list_repos_missing_readme(self, limit=25):
        rows = self.conn.execute(
            "SELECT * FROM repos WHERE removed = 0 AND readme_hash = '' ORDER BY full_name LIMIT ?",
            (int(limit),),
        ).fetchall()
        return [self._row_to_repo(row) for row in rows]

    def count_repos_missing_readme(self):
        return self.conn.execute("SELECT COUNT(*) AS count FROM repos WHERE removed = 0 AND readme_hash = ''").fetchone()["count"]

    def has_any_repo(self):
        return self.conn.execute("SELECT 1 FROM repos LIMIT 1").fetchone() is not None

    def list_changes(self, limit=50):
        rows = self.conn.execute(
            "SELECT * FROM star_changes ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        return [dict(row) for row in rows]

    def _row_to_repo(self, row):
        if row is None:
            return None
        return {
            "full_name": row["full_name"],
            "github_id": row["github_id"],
            "name": row["name"],
            "owner": row["owner"],
            "description": row["description"] or "",
            "html_url": row["html_url"] or "",
            "language": row["language"] or "",
            "topics": json.loads(row["topics_json"] or "[]"),
            "stars": row["stars"],
            "forks": row["forks"],
            "updated_at": row["updated_at"],
            "pushed_at": row["pushed_at"],
            "metadata_hash": row["metadata_hash"],
            "readme_hash": row["readme_hash"],
            "prompt_version": row["prompt_version"],
            "analysis": {
                "summary": row["analysis_summary"] or "",
                "tags": json.loads(row["analysis_tags_json"] or "[]"),
                "category": row["analysis_category"] or "",
                "platforms": json.loads(row["analysis_platforms_json"] or "[]"),
                "notes": row["analysis_notes"] or "",
            },
            "analysis_stale": bool(row["analysis_stale"]),
            "removed": bool(row["removed"]),
            "first_seen_at": row["first_seen_at"],
            "last_seen_at": row["last_seen_at"],
            "removed_at": row["removed_at"],
        }

    def close(self):
        self.conn.close()
