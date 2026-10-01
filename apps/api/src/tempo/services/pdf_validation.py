from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


class PdfValidationError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class ValidatedPdf:
    page_count: int


def validate_pdf(path: Path, max_bytes: int, max_pages: int) -> ValidatedPdf:
    if path.stat().st_size > max_bytes:
        raise PdfValidationError("file_too_large", f"PDF exceeds the {max_bytes:,}-byte upload limit.")
    with path.open("rb") as file:
        if file.read(5) != b"%PDF-":
            raise PdfValidationError("not_pdf", "The uploaded file is not a PDF.")
    try:
        with fitz.open(path) as document:
            if document.needs_pass:
                raise PdfValidationError("encrypted_pdf", "Password-protected PDFs are not supported.")
            if document.page_count == 0:
                raise PdfValidationError("empty_pdf", "The PDF contains no pages.")
            if document.page_count > max_pages:
                raise PdfValidationError("too_many_pages", f"PDF exceeds the {max_pages}-page limit.")
            return ValidatedPdf(page_count=document.page_count)
    except PdfValidationError:
        raise
    except Exception as error:
        raise PdfValidationError("unreadable_pdf", "The PDF could not be read.") from error
