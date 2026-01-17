import os
from datetime import datetime
from watchdog.events import FileSystemEventHandler
from .hash import compute_hash

class EventHandler(FileSystemEventHandler):
    def __init__(self, scanner):
        self.scanner = scanner

    def on_created(self, event):
        if event.is_directory or not self.scanner.ready:
            return
        self.handle_change("created", event.src_path)

    def on_modified(self, event):
        if event.is_directory or not self.scanner.ready:
            return
        self.handle_change("modified", event.src_path)

    def on_deleted(self, event):
        if event.is_directory or not self.scanner.ready:
            return
        self.handle_delete(event.src_path)

    def handle_change(self, kind, path):
        if not self.scanner.match(path) or not self.scanner.ready:
            return
        
        try:
            new_hash = compute_hash(path, self.scanner.hash)
            mtime = os.path.getmtime(path)
        except Exception:
            return
        
        old_hash = self.scanner.db.all_files().get(path)
        now = datetime.utcnow().isoformat()
        
        if old_hash != new_hash:
            self.scanner.db.upsert_file(path, new_hash, mtime)
            self.scanner.db.insert_event(now, kind, path, old_hash, new_hash)
            self.scanner.notifier.notify(f"FIM: file {kind}", f"Path: {path}\nNew: {new_hash}")

    def handle_delete(self, path):
        if not self.scanner.match(path) or not self.scanner.ready:
            return
       
        old_hash = self.scanner.db.all_files().get(path)
        now = datetime.utcnow().isoformat()
        
        self.scanner.db.delete_file(path)
        self.scanner.db.insert_event(now, "deleted", path, old_hash, None)
        self.scanner.notifier.notify("FIM: file deleted", f"Path: {path}\nOld: {old_hash}")
