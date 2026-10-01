from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

import fitz

from tempo.services.ocr import OcrProvider, TesseractOcrProvider
from tempo.services.quality import score_page
from tempo.services.rendering import PageRenderer, PyMuPDFRenderer


def _box(x0: float, y0: float, x1: float, y1: float, width: float, height: float) -> dict[str, float]:
    return {
        "x": round(max(0, x0) / width, 6), "y": round(max(0, y0) / height, 6),
        "width": round(max(0, min(width, x1) - max(0, x0)) / width, 6),
        "height": round(max(0, min(height, y1) - max(0, y0)) / height, 6),
    }


def _block(block_id: str, page_number: int, words: list[dict], order: int, source: str) -> dict:
    words = sorted(words, key=lambda word: (word.get("line", 0), word["bbox"]["y"], word["bbox"]["x"]))
    left = min(word["bbox"]["x"] for word in words)
    top = min(word["bbox"]["y"] for word in words)
    right = max(word["bbox"]["x"] + word["bbox"]["width"] for word in words)
    bottom = max(word["bbox"]["y"] + word["bbox"]["height"] for word in words)
    return {
        "id": block_id, "pageNumber": page_number, "text": " ".join(word["text"] for word in words),
        "bbox": {"x": left, "y": top, "width": right - left, "height": bottom - top},
        "wordIds": [word["id"] for word in words], "words": words, "blockType": "paragraph",
        "readingOrder": order, "source": source,
    }


def _native_pages(path: Path) -> list[dict]:
    pages: list[dict] = []
    with fitz.open(path) as document:
        for number, page in enumerate(document, start=1):
            width, height = page.rect.width, page.rect.height
            grouped: dict[int, list[dict]] = defaultdict(list)
            for index, entry in enumerate(page.get_text("words", sort=False)):
                x0, y0, x1, y1, text, block_number, line_number, word_number = entry
                if not text.strip():
                    continue
                grouped[block_number].append({
                    "id": f"p{number}-b{block_number}-w{index}", "pageNumber": number, "text": text,
                    "bbox": _box(x0, y0, x1, y1, width, height), "source": "native",
                    "line": line_number, "word": word_number,
                })
            blocks = [_block(f"p{number}-b{block_number}", number, words, index, "native") for index, (block_number, words) in enumerate(grouped.items())]
            pages.append({"pageNumber": number, "width": width, "height": height, "rotation": page.rotation, "blocks": blocks})
    return pages


def _reorder_page(blocks: list[dict]) -> None:
    full_width = [block for block in blocks if block["bbox"]["width"] >= 0.62]
    columns = [block for block in blocks if block not in full_width]
    left = [block for block in columns if block["bbox"]["x"] + block["bbox"]["width"] / 2 < 0.5]
    right = [block for block in columns if block["bbox"]["x"] + block["bbox"]["width"] / 2 >= 0.5]
    if len(left) >= 2 and len(right) >= 2:
        first_column_y = min(block["bbox"]["y"] for block in columns)
        prefix = [block for block in full_width if block["bbox"]["y"] < first_column_y]
        suffix = [block for block in full_width if block not in prefix]
        ordered = sorted(prefix, key=lambda item: item["bbox"]["y"]) + sorted(left, key=lambda item: item["bbox"]["y"]) + sorted(right, key=lambda item: item["bbox"]["y"]) + sorted(suffix, key=lambda item: item["bbox"]["y"])
    else:
        ordered = sorted(blocks, key=lambda item: (item["bbox"]["y"], item["bbox"]["x"]))
    blocks[:] = ordered
    for index, block in enumerate(blocks):
        block["readingOrder"] = index


def _remove_repeated_headers_and_footers(pages: list[dict]) -> None:
    candidates: list[str] = []
    for page in pages:
        for block in page["blocks"]:
            box = block["bbox"]
            if box["y"] < 0.12 or box["y"] + box["height"] > 0.88:
                normalized = " ".join(block["text"].lower().split())
                if 2 <= len(normalized) <= 160:
                    candidates.append(normalized)
    repeated = {text for text, count in Counter(candidates).items() if count >= 2}
    for page in pages:
        page["blocks"] = [block for block in page["blocks"] if " ".join(block["text"].lower().split()) not in repeated]
        _reorder_page(page["blocks"])


def _ocr_blocks(page_number: int, grouped_words: list[list[dict]]) -> list[dict]:
    return [_block(f"p{page_number}-ocr-b{index}", page_number, words, index, "ocr") for index, words in enumerate(grouped_words) if words]


def extract_positioned_text(
    path: Path,
    quality_threshold: float = 0.55,
    renderer: PageRenderer | None = None,
    ocr_provider: OcrProvider | None = None,
    on_ocr: Callable[[], None] | None = None,
) -> dict:
    """Extract native words and replace low-quality visible pages with OCR words."""
    renderer = renderer or PyMuPDFRenderer()
    ocr_provider = ocr_provider or TesseractOcrProvider()
    pages = _native_pages(path)
    quality_records: list[dict] = []
    for page in pages:
        native_words = [word for block in page["blocks"] for word in block["words"]]
        rendered = renderer.render(path, page["pageNumber"], dpi=300) if len("".join(word["text"] for word in native_words)) < 400 else None
        from tempo.services.rendering import visually_nonempty
        quality = score_page(native_words, visually_nonempty(rendered) if rendered else True)
        record = {"pageNumber": page["pageNumber"], **quality.as_dict(), "ocrApplied": False}
        if quality.score < quality_threshold and quality.rendered_nonempty:
            if on_ocr:
                on_ocr()
            rendered = rendered or renderer.render(path, page["pageNumber"], dpi=300)
            words = ocr_provider.extract(rendered)
            from tempo.services.ocr import blocks_from_ocr_words
            page["blocks"] = _ocr_blocks(page["pageNumber"], blocks_from_ocr_words(words))
            record["ocrApplied"] = True
        quality_records.append(record)
    _remove_repeated_headers_and_footers(pages)
    return {"pages": pages, "quality": quality_records}
