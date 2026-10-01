from __future__ import annotations

import re


def analyze_first_claim(extraction: dict) -> dict:
    """Deterministic stand-in for the future structured model provider."""
    block = next((block for page in extraction["pages"] for block in page["blocks"] if len(block["text"].strip()) > 20), None)
    if block is None:
        return {"claims": [], "evidenceSpans": [], "brief": {"sections": []}, "markdown": "# Replication brief\n\nNo extractable text was found."}
    text = block["text"].strip()
    match = re.search(r".+?(?:[.!?](?:\s|$)|$)", text)
    quote = match.group(0).strip() if match else text[:240].strip()
    start = text.find(quote)
    end = start + len(quote)
    words = block["words"]
    # M1 highlights the source block only after choosing its quote from that same stored text.
    rectangles = [block["bbox"]]
    evidence_id = f"e-{block['id']}"
    claim_id = f"c-{block['id']}"
    claim = {
        "id": claim_id, "statement": quote, "category": "method",
        "reproductionImportance": "important", "evidenceSpanIds": [evidence_id],
        "implementationNote": "Stub analysis for the local vertical slice; replace with validated section analysis in Milestone 3.",
        "missingInformation": [], "provenance": "explicit", "confidence": 1.0,
    }
    evidence = {"id": evidence_id, "blockId": block["id"], "exactQuote": quote, "startOffset": start, "endOffset": end, "rectangles": rectangles}
    markdown = f"# Replication brief\n\n## First extracted claim\n\n{quote}\n\nEvidence: `{evidence_id}`\n"
    return {"claims": [claim], "evidenceSpans": [evidence], "brief": {"claims": [claim], "evidence": [evidence]}, "markdown": markdown}
