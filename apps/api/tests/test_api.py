import time

import fitz
from fastapi.testclient import TestClient

from tempo.config import Settings
from tempo.main import create_app


def test_upload_processes_and_exports_grounded_annotation(tmp_path):
    pdf = tmp_path / "paper.pdf"
    document = fitz.open()
    document.new_page().insert_text((72, 72), "The experiment fixes the random seed to seven.")
    document.save(pdf)
    app = create_app(Settings(data_dir=tmp_path / "data"))
    with TestClient(app) as client:
        response = client.post("/api/papers", files={"file": ("paper.pdf", pdf.read_bytes(), "application/pdf")})
        assert response.status_code == 202
        paper_id = response.json()["paperId"]
        for _ in range(100):
            status = client.get(f"/api/papers/{paper_id}").json()
            if status["status"] in {"ready", "failed"}:
                break
            time.sleep(0.05)
        assert status["status"] == "ready"
        annotations = client.get(f"/api/papers/{paper_id}/annotations").json()
        assert annotations["claims"][0]["evidenceSpanIds"] == [annotations["evidenceSpans"][0]["id"]]
        assert client.get(f"/api/papers/{paper_id}/brief.md").status_code == 200
