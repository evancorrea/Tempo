import fitz

from tempo.services.extraction import extract_positioned_text
from tempo.services.stub_analysis import analyze_first_claim


def test_extraction_keeps_normalized_geometry_and_stub_evidence(tmp_path):
    path = tmp_path / "paper.pdf"
    document = fitz.open()
    document.new_page().insert_text((72, 72), "This method uses a fixed deterministic seed.")
    document.save(path)
    extraction = extract_positioned_text(path)
    block = extraction["pages"][0]["blocks"][0]
    assert 0 <= block["bbox"]["x"] <= 1
    analysis = analyze_first_claim(extraction)
    assert analysis["evidenceSpans"][0]["blockId"] == block["id"]
