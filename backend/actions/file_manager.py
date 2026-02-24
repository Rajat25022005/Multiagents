"""
File manager for saving agent outputs.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from core.config import get_settings

settings = get_settings()


class FileManager:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.output_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: str, filename: str | None = None, ext: str = "txt") -> str:
        if not filename:
            filename = f"{uuid.uuid4().hex[:8]}.{ext}"
        path = self.base_dir / filename
        path.write_text(content, encoding="utf-8")
        return str(path)

    def save_bytes(self, data: bytes, filename: str) -> str:
        path = self.base_dir / filename
        path.write_bytes(data)
        return str(path)

    def read(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        max_bytes = settings.max_file_size_mb * 1024 * 1024
        if p.stat().st_size > max_bytes:
            raise ValueError(f"File too large (max {settings.max_file_size_mb}MB)")
        return p.read_text(encoding="utf-8")

    def list_outputs(self) -> list[str]:
        return [str(p) for p in self.base_dir.iterdir() if p.is_file()]

    def delete(self, path: str):
        p = Path(path)
        if p.exists() and p.parent == self.base_dir:
            p.unlink()
