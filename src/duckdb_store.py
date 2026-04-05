from pathlib import Path
import json
import duckdb

DB_PATH = Path(__file__).resolve().parent / "data" / "solitaire.duckdb"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS kv_store(
    key TEXT PRIMARY KEY,
    value_json TEXT
)
"""


def _connect():
    con = duckdb.connect(str(DB_PATH))
    con.execute(CREATE_SQL)
    return con


def db_get(key):
    con = _connect()
    try:
        row = con.execute("SELECT value_json FROM kv_store WHERE key = ?", [key]).fetchone()
        if not row:
            return None
        return json.loads(row[0])
    finally:
        con.close()


def db_set(key, value):
    con = _connect()
    try:
        value_json = json.dumps(value, ensure_ascii=False)
        con.execute(
            "INSERT INTO kv_store(key, value_json) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
            [key, value_json],
        )
    finally:
        con.close()