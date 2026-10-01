"use client";
import { useState } from "react";
import { upload } from "../lib/api";
import type { Paper } from "../lib/types";
export function PaperUpload({onUpload}: {onUpload: (paper: Paper) => void}) { const [error, setError] = useState(""); const [busy, setBusy] = useState(false); return <section className="upload"><h1>Tempo</h1><p>Upload a technical paper to build an evidence-grounded replication brief.</p><label className="file"><input type="file" accept="application/pdf" disabled={busy} onChange={async event => { const file = event.target.files?.[0]; if (!file) return; setBusy(true); setError(""); try { onUpload(await upload(file)); } catch (err) { setError(err instanceof Error ? err.message : "Upload failed"); } finally { setBusy(false); }}} />{busy ? "Uploading…" : "Choose a PDF"}</label>{error && <p role="alert">{error}</p>}</section>; }
