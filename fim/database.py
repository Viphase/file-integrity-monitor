import sqlite3
from pathlib import Path
import threading

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    hash TEXT NOT NULL,
    mtime REAL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    type TEXT,
    path TEXT,
    old_hash TEXT,
    new_hash TEXT,
    note TEXT
);
"""

class DB:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.lock = threading.Lock()
        
        self._init_schema()

    def _init_schema(self):
        with self.lock:
            c = self.conn.cursor()
            c.executescript(SCHEMA)
            self.conn.commit()

    def all_files(self):
        with self.lock:
            c = self.conn.cursor()
            c.execute("SELECT path, hash FROM files")
            
            return dict(c.fetchall())

    def upsert_file(self, path, hash_, mtime):
        with self.lock:
            c = self.conn.cursor()
            c.execute(
                "INSERT INTO files(path, hash, mtime) VALUES(?,?,?) ON CONFLICT(path) DO UPDATE SET hash=excluded.hash, mtime=excluded.mtime",(path, hash_, mtime))
            self.conn.commit()

    def delete_file(self, path):
        with self.lock:
            c = self.conn.cursor()
            c.execute("DELETE FROM files WHERE path = ?", (path,))
            self.conn.commit()

    def insert_event(self, ts, type_, path, old_hash, new_hash, note=None):
        with self.lock:
            c = self.conn.cursor()
            c.execute(
                "INSERT INTO events(ts, type, path, old_hash, new_hash, note) VALUES(?,?,?,?,?,?)",(ts, type_, path, old_hash, new_hash, note))
            self.conn.commit()
