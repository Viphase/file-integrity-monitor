import os
import time
import fnmatch
import logging
from datetime import datetime
from .hash import compute_hash

log = logging.getLogger(__name__)

class Scanner:
    def __init__(self, paths, masks, db, notifier, hash):
        self.paths = paths
        self.masks = masks
        self.db = db
        self.notifier = notifier
        self.hash = hash
        self.ready = False

    def match(self, path_or_name):
        name = os.path.basename(path_or_name)
        for m in self.masks:
            if fnmatch.fnmatch(name, m):
                return True
            return False

    def scan_once(self):
        current = {}
        for base in self.paths:
            if not os.path.exists(base):
                continue
            
            for root, _, files in os.walk(base):
                for name in files:
                    if not self.match(name):
                        continue
                    
                    path = os.path.join(root, name)
                    try:
                        h = compute_hash(path, self.hash)
                        mtime = os.path.getmtime(path)
                        current[path] = (h, mtime)
                    
                    except Exception:
                        continue
        stored = self.db.all_files()
        now = datetime.utcnow().isoformat()
        
        for path, (h, mtime) in current.items():
            old = stored.get(path)
            
            if old is None:
                log.warning("added %s", path)
                self.db.upsert_file(path, h, mtime)
                self.db.insert_event(now, "added", path, None, h)
                self.notifier.notify("FIM: file added", f"Path: {path}\nHash: {h}")
            
            elif old != h:
                log.warning("modified %s", path)
                self.db.upsert_file(path, h, mtime)
                self.db.insert_event(now, "modified", path, old, h)
                self.notifier.notify("FIM: file modified", f"Path: {path}\nOld: {old}\nNew: {h}")
        
        for path in set(stored) - set(current):
            old = stored[path]
            log.warning("deleted %s", path)
            
            self.db.delete_file(path)
            self.db.insert_event(now, "deleted", path, old, None)
            self.notifier.notify("FIM: file deleted", f"Path: {path}\nOld: {old}")

    def init_baseline(self):
        log.info("initial baseline scan started")

        for base in self.paths:
            if not os.path.exists(base):
                continue

            for root, _, files in os.walk(base):
                for name in files:
                    if not self.match(name):
                        continue

                    path = os.path.join(root, name)
                    try:
                        h = compute_hash(path, self.hash)
                        mtime = os.path.getmtime(path)
                        self.db.upsert_file(path, h, mtime)
                    except Exception:
                        continue

        self.ready = True
        log.info("initial baseline scan completed")

    def run_periodic(self, interval_seconds):
        log.info("periodic scan start %s", interval_seconds)
        while True:
            try:
                self.scan_once()
            except Exception:
                log.exception("scan error")
            time.sleep(interval_seconds)
