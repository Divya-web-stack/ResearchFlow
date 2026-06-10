from pathlib import Path
import json
from typing import Any

STORAGE_FILE = Path(__file__).resolve().parents[1] / "memory_store.json"

class MemoryStore:
    def __init__(self):
        self.path = STORAGE_FILE
        if not self.path.exists():
            self.save({"memories": []})

    def load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]):
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_memory(self, item: dict[str, Any]):
        data = self.load()
        data.setdefault("memories", []).append(item)
        self.save(data)

    def list_memory(self) -> list[dict[str, Any]]:
        return self.load().get("memories", [])
