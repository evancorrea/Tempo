from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor

from tempo.config import Settings
from tempo.jobs.process_paper import process_paper_task


class JobRunner:
    def submit(self, paper_id: str, settings: Settings) -> None:
        raise NotImplementedError


class InProcessJobRunner(JobRunner):
    def __init__(self) -> None:
        # A single local process retains the MVP's serial semantics while isolating
        # native PDF parsing from the FastAPI process.
        self.executor = ProcessPoolExecutor(max_workers=1)

    def submit(self, paper_id: str, settings: Settings) -> None:
        self.executor.submit(process_paper_task, paper_id, settings)
