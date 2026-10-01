from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PaperStatus = Literal["uploaded", "validating", "extracting", "ocr", "analyzing", "ready", "failed"]


class Failure(BaseModel):
    code: str
    message: str


class PaperResponse(BaseModel):
    paperId: str
    filename: str
    status: PaperStatus
    stage: str
    progress: int = Field(ge=0, le=100)
    pageCount: int | None = None
    ocrPageCount: int = Field(default=0, ge=0)
    failure: Failure | None = None


class BoundingBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)


class EvidenceSpan(BaseModel):
    id: str
    blockId: str
    exactQuote: str
    startOffset: int
    endOffset: int
    rectangles: list[BoundingBox]


class Claim(BaseModel):
    id: str
    statement: str
    category: str
    reproductionImportance: str
    evidenceSpanIds: list[str]
    implementationNote: str
    missingInformation: list[str]
    provenance: str
    confidence: float


class AnnotationResponse(BaseModel):
    claims: list[Claim]
    evidenceSpans: list[EvidenceSpan]


class BriefResponse(BaseModel):
    markdown: str
    brief: dict
