import json
from pathlib import Path

class Config:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self._load()

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)
