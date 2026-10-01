import fitz
import pytest

from tempo.services.pdf_validation import PdfValidationError, validate_pdf


def test_validates_a_pdf(tmp_path):
    path = tmp_path / "paper.pdf"
    document = fitz.open()
    document.new_page().insert_text((72, 72), "A replication-relevant sentence.")
    document.save(path)
    assert validate_pdf(path, 1_000_000, 2).page_count == 1


def test_rejects_non_pdf(tmp_path):
    path = tmp_path / "not-a-paper.txt"
    path.write_text("not a PDF")
    with pytest.raises(PdfValidationError, match="not a PDF"):
        validate_pdf(path, 1_000_000, 2)
