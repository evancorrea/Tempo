from __future__ import annotations

from pathlib import Path


class Storage:
    def __init__(self, data_dir: Path):
        self.root = data_dir / "papers"
        self.root.mkdir(parents=True, exist_ok=True)

    def original_path(self, paper_id: str) -> Path:
        directory = self.root / paper_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "original.pdf"
