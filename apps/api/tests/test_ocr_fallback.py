from io import BytesIO

import fitz
from PIL import Image, ImageDraw

from tempo.services.extraction import extract_positioned_text


def _scanned_page(document: fitz.Document, text: str = "SCANNED METHODS PAGE") -> None:
    image = Image.new("RGB", (1200, 1600), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((80, 80, 1120, 1520), outline="black", width=10)
    draw.text((140, 300), text, fill="black", font_size=76)
    stream = BytesIO()
    image.save(stream, format="PNG")
    page = document.new_page(width=612, height=792)
    page.insert_image(page.rect, stream=stream.getvalue())


def test_scanned_page_uses_real_tesseract_fallback(tmp_path):
    path = tmp_path / "scanned.pdf"
    document = fitz.open()
    _scanned_page(document)
    document.save(path)

    extraction = extract_positioned_text(path)

    assert extraction["quality"][0]["ocrApplied"] is True
    assert extraction["pages"][0]["blocks"]
    assert all(block["source"] == "ocr" for block in extraction["pages"][0]["blocks"])
    assert "SCANNED" in " ".join(block["text"] for block in extraction["pages"][0]["blocks"])


def test_mixed_document_preserves_native_and_ocr_sources(tmp_path):
    path = tmp_path / "mixed.pdf"
    document = fitz.open()
    document.new_page().insert_text((72, 200), "This native page contains a clean reproducibility statement.")
    _scanned_page(document, "SCANNED APPENDIX")
    document.save(path)

    extraction = extract_positioned_text(path)

    assert extraction["quality"][0]["ocrApplied"] is False
    assert extraction["quality"][1]["ocrApplied"] is True
    assert {block["source"] for block in extraction["pages"][0]["blocks"]} == {"native"}
    assert {block["source"] for block in extraction["pages"][1]["blocks"]} == {"ocr"}
