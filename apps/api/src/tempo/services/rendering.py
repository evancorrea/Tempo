from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Protocol
from math import sqrt

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
    stride = max(1, int(sqrt((image.width * image.height) / 30_000)))
    pixels = image.load()
    dark = 0
    checked = 0
    for y in range(0, image.height, stride):
        for x in range(0, image.width, stride):
            dark += sum(pixels[x, y]) / 3 < 235
            checked += 1
    return checked > 0 and dark / checked > 0.002
