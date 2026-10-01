from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from tempo.schemas import AnnotationResponse, BriefResponse, Failure, PaperResponse

router = APIRouter(prefix="/api/papers", tags=["papers"])


def _paper_response(record: dict) -> PaperResponse:
    failure = Failure(code=record["error_code"], message=record["error_message"]) if record["error_code"] else None
    return PaperResponse(paperId=record["id"], filename=record["filename"], status=record["status"], stage=record["stage"], progress=record["progress"], pageCount=record["page_count"], failure=failure)


def _paper_or_404(request: Request, paper_id: str) -> dict:
    record = request.app.state.db.get_paper(paper_id)
    if not record:
        raise HTTPException(404, "Paper not found")
    return record


@router.post("", status_code=202, response_model=PaperResponse)
async def upload_paper(request: Request, file: UploadFile) -> PaperResponse:
    if not file.filename:
        raise HTTPException(422, "A PDF file is required")
    content = await file.read(request.app.state.settings.max_pdf_bytes + 1)
    if len(content) > request.app.state.settings.max_pdf_bytes:
        raise HTTPException(413, "PDF exceeds the configured upload limit")
    digest = hashlib.sha256(content).hexdigest()
    existing = request.app.state.db.get_by_hash(digest)
    if existing:
        return _paper_response(existing)
    paper_id = str(uuid.uuid4())
    path: Path = request.app.state.storage.original_path(paper_id)
    path.write_bytes(content)
    record = request.app.state.db.create_paper(paper_id, Path(file.filename).name, digest)
    request.app.state.runner.submit(paper_id, request.app.state.settings)
    return _paper_response(record)


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(request: Request, paper_id: str) -> PaperResponse:
    return _paper_response(_paper_or_404(request, paper_id))


@router.get("/{paper_id}/file")
def get_file(request: Request, paper_id: str) -> FileResponse:
    record = _paper_or_404(request, paper_id)
    path = request.app.state.storage.original_path(record["id"])
    if not path.exists():
        raise HTTPException(404, "Original file not found")
    return FileResponse(path, media_type="application/pdf", filename=record["filename"])


@router.get("/{paper_id}/annotations", response_model=AnnotationResponse)
def annotations(request: Request, paper_id: str) -> AnnotationResponse:
    _paper_or_404(request, paper_id)
    analysis = request.app.state.db.get_artifact(paper_id, "analysis") or {"claims": [], "evidenceSpans": []}
    return AnnotationResponse(claims=analysis["claims"], evidenceSpans=analysis["evidenceSpans"])


@router.get("/{paper_id}/brief", response_model=BriefResponse)
def brief(request: Request, paper_id: str) -> BriefResponse:
    _paper_or_404(request, paper_id)
    analysis = request.app.state.db.get_artifact(paper_id, "analysis") or {"brief": {"claims": []}, "markdown": ""}
    return BriefResponse(brief=analysis["brief"], markdown=analysis["markdown"])


@router.get("/{paper_id}/brief.md")
def brief_markdown(request: Request, paper_id: str) -> PlainTextResponse:
    return PlainTextResponse(brief(request, paper_id).markdown, headers={"Content-Disposition": f'attachment; filename="{paper_id}-brief.md"'})


@router.get("/{paper_id}/brief.json")
def brief_json(request: Request, paper_id: str) -> JSONResponse:
    payload = brief(request, paper_id)
    return JSONResponse(payload.model_dump(), headers={"Content-Disposition": f'attachment; filename="{paper_id}-brief.json"'})
