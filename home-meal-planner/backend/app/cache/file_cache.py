"""HTTP response file cache with TTL."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from app.config import HTTP_CACHE_TTL_SECONDS, MEAL_CACHE_DIR


class FileCache:
    def __init__(self, cache_dir: Optional[Path] = None, ttl_seconds: int = HTTP_CACHE_TTL_SECONDS) -> None:
        self.cache_dir = cache_dir or MEAL_CACHE_DIR
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get(self, key: str) -> Optional[Any]:
        path = self._path_for_key(key)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - payload.get("_cached_at", 0) > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            return payload.get("data")
        except (json.JSONDecodeError, OSError, KeyError):
            return None

    def set(self, key: str, data: Any) -> None:
        path = self._path_for_key(key)
        payload = {"_cached_at": time.time(), "data": data}
        path.write_text(json.dumps(payload), encoding="utf-8")
