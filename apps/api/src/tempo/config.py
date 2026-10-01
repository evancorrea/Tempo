from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    max_pdf_bytes: int = 52_428_800
    max_pages: int = 80
    ocr_quality_threshold: float = 0.55

    @property
    def database_path(self) -> Path:
        return self.data_dir / "tempo.db"

    @classmethod
    def from_environment(cls) -> "Settings":
        # The shared project-level .env is intentionally backend-only.
        load_dotenv(Path(__file__).resolve().parents[4] / ".env")
        data_dir = Path(os.getenv("TEMPO_DATA_DIR", "./data")).expanduser().resolve()
        return cls(
            data_dir=data_dir,
            max_pdf_bytes=int(os.getenv("TEMPO_MAX_PDF_BYTES", "52428800")),
            max_pages=int(os.getenv("TEMPO_MAX_PAGES", "80")),
            ocr_quality_threshold=float(os.getenv("TEMPO_OCR_QUALITY_THRESHOLD", "0.55")),
        )
