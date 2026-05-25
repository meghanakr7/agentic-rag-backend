from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import ingest, chat
from app.utils.logger import configure_logging

configure_logging()

app = FastAPI(
    title="Agentic RAG Backend",
    description="Asynchronous FastAPI backend for document ingestion and agentic RAG-based question answering.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "agentic-rag-backend",
    }


app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])