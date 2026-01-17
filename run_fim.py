import logging
import os
import sys
import threading
import time
from datetime import datetime
from watchdog.observers import Observer

from fim.scanner import Scanner
from fim.watcher import EventHandler
from fim.notifier import Notifier
from fim.config import Config
from fim.database import DB


def setup_logging(log_dir, level):
    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(message)s"
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    if not log_dir:
        return

    os.makedirs(log_dir, exist_ok=True)

    start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(log_dir, f"fim-{start_time}.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)


def main():
    cfg = Config("config.json")

    setup_logging(
        cfg.get("logging", {}).get("log_dir"),
        getattr(logging, cfg.get("logging", {}).get("level", "INFO"))
    )

    db_path = cfg.get("database")
    db_exists = os.path.exists(db_path)
    database = DB(cfg.get("database", {}))
    notifier = Notifier(cfg.get("alerts", {}))

    scanner = Scanner(
        cfg.get("paths", []),
        cfg.get("file_masks", []),
        database,
        notifier,
        cfg.get("hash_algorithm", "sha256")
    )
    handler = EventHandler(scanner)

    if not db_exists:
        logging.warning("Database not found, creating new baseline")
        scanner.init_baseline()
    else:
        logging.info("Database found, skipping baseline")

    observer = Observer()
    for path in cfg.get("paths", []):
        observer.schedule(handler, path, recursive=True)
    observer.start()

    logging.info("Watchdog observer started")

    t = threading.Thread(
        target=scanner.run_periodic,
        args=(cfg.get("scan_interval_seconds", 300),),
        daemon=True
    )
    t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
