import time

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app_import_start = time.perf_counter()

from app.api import ingest, chat
from app.utils.logger import configure_logging

configure_logging()
logger = structlog.get_logger()

logger.info(
    "main_import_dependencies_loaded",
    seconds=round(time.perf_counter() - app_import_start, 3),
)

app_setup_start = time.perf_counter()

app = FastAPI(
    title="Agentic RAG Backend",
    description="Asynchronous FastAPI backend for document ingestion and agentic RAG-based question answering.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

logger.info(
    "fastapi_app_created",
    seconds=round(time.perf_counter() - app_setup_start, 3),
)


@app.on_event("startup")
async def startup_event():
    logger.info("fastapi_startup_started")

    # Do NOT load vector store or LLM here.
    # This startup event is only for logging.

    logger.info("fastapi_startup_completed")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    start = time.perf_counter()

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )

    logger.info(
        "home_page_rendered",
        path="/",
        seconds=round(time.perf_counter() - start, 3),
    )

    return response


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "agentic-rag-backend",
    }