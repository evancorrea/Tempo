from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tempo.config import Settings
from tempo.db import Database
from tempo.jobs.runner import InProcessJobRunner
from tempo.routes.papers import router as papers_router
from tempo.services.storage import Storage


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.db = Database(settings.database_path)
        app.state.storage = Storage(settings.data_dir)
        app.state.runner = InProcessJobRunner()
        yield
        app.state.runner.executor.shutdown(wait=False, cancel_futures=True)

    app = FastAPI(title="Tempo API", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(papers_router)
    return app


app = create_app()
