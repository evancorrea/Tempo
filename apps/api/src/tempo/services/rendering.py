from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol

import fitz
from PIL import Image


@dataclass(frozen=True)
class RenderedPage:
    page_number: int
    width: int
    height: int
    png: bytes


class PageRenderer(Protocol):
    def render(self, path: Path, page_number: int, dpi: int = 300) -> RenderedPage: ...


class PyMuPDFRenderer:
    """Rendering adapter that can later be replaced by a Poppler implementation."""

    def render(self, path: Path, page_number: int, dpi: int = 300) -> RenderedPage:
        scale = dpi / 72
        with fitz.open(path) as document:
            pixmap = document.load_page(page_number - 1).get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            return RenderedPage(page_number, pixmap.width, pixmap.height, pixmap.tobytes("png"))


def visually_nonempty(rendered: RenderedPage) -> bool:
    """Cheap luminance sampling used only when native PDF text is sparse."""
    image = Image.open(BytesIO(rendered.png)).convert("RGB")
    pixels = list(image.getdata())
    stride = max(1, len(pixels) // 30_000)
    sampled = pixels[::stride]
    dark = sum(sum(pixel) / 3 < 235 for pixel in sampled)
    return bool(sampled) and dark / len(sampled) > 0.002
