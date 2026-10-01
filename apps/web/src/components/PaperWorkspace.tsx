"use client";

import dynamic from "next/dynamic";
import ReactMarkdown from "react-markdown";
import { useEffect, useState } from "react";

import { annotations, apiUrl, brief, paper } from "../lib/api";
import type { Claim, EvidenceSpan, Paper } from "../lib/types";

const PdfViewer = dynamic(
  () => import("./PdfViewer").then(module => module.PdfViewer),
  { ssr: false, loading: () => <div className="pdf">Loading PDF viewer…</div> },
);

export function PaperWorkspace({ initial }: { initial: Paper }) {
  const [current, setCurrent] = useState(initial);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [evidence, setEvidence] = useState<EvidenceSpan[]>([]);
  const [markdown, setMarkdown] = useState("");
  const [selected, setSelected] = useState<string>();

  useEffect(() => {
    if (current.status === "ready" || current.status === "failed") return;
    const timer = setInterval(async () => setCurrent(await paper(current.paperId)), 800);
    return () => clearInterval(timer);
  }, [current]);

  useEffect(() => {
    if (current.status !== "ready") return;
    Promise.all([annotations(current.paperId), brief(current.paperId)]).then(([foundAnnotations, foundBrief]) => {
      setClaims(foundAnnotations.claims);
      setEvidence(foundAnnotations.evidenceSpans);
      setMarkdown(foundBrief.markdown);
    });
  }, [current.paperId, current.status]);

  const selectedClaim = claims.find(claim => claim.evidenceSpanIds.includes(selected ?? ""));

  return <main className="workspace">
    <header><span>{current.filename}</span><span className={current.status}>{current.status} · {current.progress}%{current.ocrPageCount > 0 && <span className="ocr-status"> · OCR used on {current.ocrPageCount} page{current.ocrPageCount === 1 ? "" : "s"}</span>}</span></header>
    {current.failure && <p role="alert">{current.failure.message}</p>}
    <div className="columns">
      <PdfViewer url={apiUrl(`/api/papers/${current.paperId}/file`)} evidence={evidence} onSelect={setSelected} />
      <aside>
        <h2>Annotation</h2>
        {selectedClaim ? <><p>{selectedClaim.statement}</p><p>{selectedClaim.implementationNote}</p></> : <p>Select a highlighted passage once processing completes.</p>}
        <h2>Replication brief</h2>
        <div className="brief"><ReactMarkdown>{markdown || "Generating brief…"}</ReactMarkdown></div>
        <p><a href={apiUrl(`/api/papers/${current.paperId}/brief.md`)}>Markdown</a> · <a href={apiUrl(`/api/papers/${current.paperId}/brief.json`)}>JSON</a></p>
      </aside>
    </div>
  </main>;
}
