import type { Claim, EvidenceSpan, Paper } from "./types";
const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const apiUrl = (path: string) => `${base}${path}`;
export async function upload(file: File): Promise<Paper> { const form = new FormData(); form.append("file", file); const response = await fetch(apiUrl("/api/papers"), { method: "POST", body: form }); if (!response.ok) throw new Error(await response.text()); return response.json(); }
export async function paper(id: string): Promise<Paper> { const response = await fetch(apiUrl(`/api/papers/${id}`)); if (!response.ok) throw new Error("Could not load paper"); return response.json(); }
export async function annotations(id: string): Promise<{claims: Claim[]; evidenceSpans: EvidenceSpan[]}> { const response = await fetch(apiUrl(`/api/papers/${id}/annotations`)); return response.json(); }
export async function brief(id: string): Promise<{markdown: string}> { const response = await fetch(apiUrl(`/api/papers/${id}/brief`)); return response.json(); }
