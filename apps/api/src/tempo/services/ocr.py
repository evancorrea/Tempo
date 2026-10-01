from __future__ import annotations

from collections import defaultdict
from io import BytesIO
from typing import Protocol

from PIL import Image
import pytesseract
from pytesseract import Output

from tempo.services.rendering import RenderedPage


class OcrUnavailableError(RuntimeError):
    pass


class OcrProvider(Protocol):
    def extract(self, rendered: RenderedPage) -> list[dict]: ...


class TesseractOcrProvider:
    def extract(self, rendered: RenderedPage) -> list[dict]:
        try:
            data = pytesseract.image_to_data(Image.open(BytesIO(rendered.png)), output_type=Output.DICT)
        except (pytesseract.TesseractNotFoundError, OSError) as error:
            raise OcrUnavailableError("OCR is required for this page, but Tesseract is unavailable.") from error
        words: list[dict] = []
        for index, text in enumerate(data["text"]):
            text = text.strip()
            confidence = float(data["conf"][index])
            if not text or confidence < 0:
                continue
            words.append({
                "id": f"p{rendered.page_number}-ocr-w{index}", "pageNumber": rendered.page_number, "text": text,
                "bbox": {"x": data["left"][index] / rendered.width, "y": data["top"][index] / rendered.height,
                         "width": data["width"][index] / rendered.width, "height": data["height"][index] / rendered.height},
                "source": "ocr", "confidence": round(confidence / 100, 3),
                "blockKey": f"ocr-{data['block_num'][index]}-{data['par_num'][index]}",
            })
        return words


def blocks_from_ocr_words(words: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for word in words:
        grouped[word["blockKey"]].append(word)
    return list(grouped.values())
