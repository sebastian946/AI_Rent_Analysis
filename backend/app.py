"""Backend FastAPI: expone el analisis como trabajos asincronos y sirve el frontend."""

import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config.config import settings
from model.agents_model import AgentAnalysis
from model.tools_model import Listing, WebSearchTool
from services.analysis import NoListingsFound, run_analysis

logger = logging.getLogger("ai_rent_analysis")

# Build de Vite (frontend/dist). En desarrollo usa `npm run dev` con proxy a /api.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
JobStatus = Literal["queued", "scraping", "analyzing", "done", "error"]


class Job(BaseModel):
    id: str
    status: JobStatus = "queued"
    message: str = "En cola"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    search: WebSearchTool
    listings_count: Optional[int] = None
    listings: Optional[List[Listing]] = None
    result: Optional[AgentAnalysis] = None
    error: Optional[str] = None


class JobCreated(BaseModel):
    id: str
    status: JobStatus


# El scraper usa la API sincrona de Playwright: debe correr fuera del event loop.
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="analysis")
_jobs: Dict[str, Job] = {}
_lock = threading.Lock()


def _update(job_id: str, **fields) -> None:
    with _lock:
        job = _jobs[job_id]
        for key, value in fields.items():
            setattr(job, key, value)


def _run_job(job_id: str) -> None:
    job = _jobs[job_id]

    def progress(msg: str) -> None:
        status: JobStatus = "analyzing" if "Analizando" in msg else "scraping"
        _update(job_id, status=status, message=msg)

    try:
        _update(job_id, status="scraping", message="Iniciando busqueda...")
        listings, analysis = run_analysis(job.search, headless=True, on_progress=progress)
        _update(
            job_id,
            status="done",
            message="Analisis completado",
            listings=listings,
            listings_count=len(listings),
            result=analysis,
        )
    except NoListingsFound as exc:
        _update(job_id, status="error", message=str(exc), error=str(exc))
    except Exception as exc:  # noqa: BLE001 - se reporta al cliente
        logger.exception("Job %s fallo", job_id)
        _update(job_id, status="error", message="Error interno", error=str(exc))


app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug_mode)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.post("/api/analyses", response_model=JobCreated, status_code=202)
def create_analysis(search: WebSearchTool) -> JobCreated:
    job_id = uuid.uuid4().hex
    with _lock:
        _jobs[job_id] = Job(id=job_id, search=search)
    _executor.submit(_run_job, job_id)
    return JobCreated(id=job_id, status="queued")


@app.get("/api/analyses/{job_id}", response_model=Job)
def get_analysis(job_id: str) -> Job:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    return job


@app.get("/api/analyses", response_model=List[JobCreated])
def list_analyses() -> List[JobCreated]:
    with _lock:
        return [JobCreated(id=j.id, status=j.status) for j in _jobs.values()]


if FRONTEND_DIR.is_dir():

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
else:

    @app.get("/", include_in_schema=False)
    def index_missing() -> dict:
        return {
            "detail": "Frontend no compilado. Ejecuta `npm run build` en frontend/ "
            "o usa `npm run dev` para desarrollo."
        }
