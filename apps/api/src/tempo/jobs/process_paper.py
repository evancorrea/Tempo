from __future__ import annotations

from tempo.config import Settings
from tempo.db import Database
from tempo.services.extraction import extract_positioned_text
from tempo.services.ocr import OcrUnavailableError
from tempo.services.pdf_validation import PdfValidationError, validate_pdf
from tempo.services.storage import Storage
from tempo.services.stub_analysis import analyze_first_claim


def process_paper(paper_id: str, settings: Settings, db: Database, storage: Storage) -> None:
    try:
        db.update_paper(paper_id, status="validating", stage="validating", progress=10)
        validated = validate_pdf(storage.original_path(paper_id), settings.max_pdf_bytes, settings.max_pages)
        db.update_paper(paper_id, status="extracting", stage="extracting", progress=35, page_count=validated.page_count)
        extraction = extract_positioned_text(
            storage.original_path(paper_id),
            quality_threshold=settings.ocr_quality_threshold,
            on_ocr=lambda: db.update_paper(paper_id, status="ocr", stage="ocr", progress=60),
        )
        db.save_artifact(paper_id, "extraction", extraction)
        db.update_paper(paper_id, status="analyzing", stage="analyzing", progress=75)
        analysis = analyze_first_claim(extraction)
        db.save_artifact(paper_id, "analysis", analysis)
        db.update_paper(paper_id, status="ready", stage="ready", progress=100)
    except (PdfValidationError, OcrUnavailableError) as error:
        db.update_paper(paper_id, status="failed", stage="failed", progress=100, error_code=getattr(error, "code", "ocr_unavailable"), error_message=str(error))
    except Exception:
        db.update_paper(paper_id, status="failed", stage="failed", progress=100, error_code="processing_failed", error_message="The paper could not be processed. Please try another PDF.")


def process_paper_task(paper_id: str, settings: Settings) -> None:
    """Pickle-safe entry point used by the isolated PDF worker process."""
    process_paper(paper_id, settings, Database(settings.database_path), Storage(settings.data_dir))
