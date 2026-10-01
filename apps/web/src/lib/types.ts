export type BoundingBox = { x: number; y: number; width: number; height: number };
export type EvidenceSpan = { id: string; blockId: string; exactQuote: string; rectangles: BoundingBox[] };
export type Claim = { id: string; statement: string; category: string; reproductionImportance: string; evidenceSpanIds: string[]; implementationNote: string; missingInformation: string[]; provenance: string; confidence: number };
export type Paper = { paperId: string; filename: string; status: string; stage: string; progress: number; pageCount?: number; failure?: { code: string; message: string } };
