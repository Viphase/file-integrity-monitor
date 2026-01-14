import argparse
import logging
import logging.handlers
import sys
import time

from watchdog.observers import Observer
from config import Config


def setup_logging(log_file, level):
    root = logging.getLogger()
    root.setLevel(level)
    
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    root.addHandler(sh)
    
    if log_file:
        fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
        fh.setFormatter(fmt)
        root.addHandler(fh)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.json")

    args = parser.parse_args()
    cfg = Config(args.config)
    log_cfg = cfg.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper())

    setup_logging(log_cfg.get("log_file"), level)
    
    observer = Observer()
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()