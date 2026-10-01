"use client";
import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import type { EvidenceSpan } from "../lib/types";
pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();
export function PdfViewer({url, evidence, onSelect}: {url: string; evidence: EvidenceSpan[]; onSelect: (id: string) => void}) { const [pages, setPages] = useState(0); return <div className="pdf"><Document file={url} onLoadSuccess={({numPages}: {numPages: number}) => setPages(numPages)} loading="Rendering original PDF…">{Array.from({length: pages}, (_, index) => { const pageNumber = index + 1; const hits = evidence.filter(item => item.blockId.startsWith(`p${pageNumber}-`)); return <div className="page" key={pageNumber}><Page pageNumber={pageNumber} width={720} renderTextLayer renderAnnotationLayer />{hits.flatMap(hit => hit.rectangles.map((rect, rectIndex) => <button aria-label={`Evidence: ${hit.exactQuote}`} className="highlight" key={`${hit.id}-${rectIndex}`} style={{left: `${rect.x * 100}%`, top: `${rect.y * 100}%`, width: `${rect.width * 100}%`, height: `${rect.height * 100}%`}} onClick={() => onSelect(hit.id)} />))}</div>; })}</Document></div>; }
