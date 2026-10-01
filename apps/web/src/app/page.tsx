"use client";
import { useState } from "react";
import { PaperUpload } from "../components/PaperUpload";
import { PaperWorkspace } from "../components/PaperWorkspace";
import type { Paper } from "../lib/types";
export default function Home() { const [paper, setPaper] = useState<Paper>(); return paper ? <PaperWorkspace initial={paper}/> : <PaperUpload onUpload={setPaper}/>; }
