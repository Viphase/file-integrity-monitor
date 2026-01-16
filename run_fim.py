import logging
import logging.handlers
import sys
import threading
import time
from watchdog.observers import Observer

from fim.scanner import Scanner
from fim.watcher import EventHandler

from fim.config import Config


def setup_logging(log_file, level):
    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(message)s"
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    root.addHandler(sh)

    if log_file:
        fh = logging.handlers.RotatingFileHandler(log_file)
        fh.setFormatter(fmt)
        root.addHandler(fh)


def main():
    cfg = Config("config.json")

    setup_logging(
        cfg.get("logging", {}).get("log_file"),
        getattr(logging, cfg.get("logging", {}).get("level", "INFO"))
    )

    scanner = Scanner(
        cfg.get("paths", []),
        cfg.get("file_masks", []),
        database...,
        notifier...,
        cfg.get("hash_algorithm", "sha256")
    )

    observer = Observer()
    handler = EventHandler(scanner)
    
    observer.start()
    for path in cfg.get("paths", []):
        observer.schedule(handler, path, recursive=True)

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
