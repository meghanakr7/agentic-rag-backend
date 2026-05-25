import shutil
from pathlib import Path

import structlog
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.chunker import TextChunker
from app.services.document_loader import DocumentLoader

router = APIRouter()
logger = structlog.get_logger()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported.",
        )

    saved_path = UPLOAD_DIR / file.filename

    try:
        with saved_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(
            "document_uploaded",
            filename=file.filename,
            saved_path=str(saved_path),
            content_type=file.content_type,
        )

        text = await DocumentLoader.load_document(str(saved_path))

        chunker = TextChunker(chunk_size=1200, chunk_overlap=200)
        chunks = chunker.chunk_text(text)

        logger.info(
            "document_chunked",
            filename=file.filename,
            total_characters=len(text),
            total_chunks=len(chunks),
        )

        from app.services.vector_store import VectorStoreService

        vector_store = VectorStoreService()

        stored_chunks = vector_store.add_chunks(
            chunks=chunks,
            source_filename=file.filename,
        )

        total_vectors = vector_store.count()

        logger.info(
            "document_stored_in_vector_db",
            filename=file.filename,
            stored_chunks=stored_chunks,
            total_vectors=total_vectors,
        )

        return {
            "status": "success",
            "filename": file.filename,
            "total_characters": len(text),
            "total_chunks": len(chunks),
            "stored_chunks": stored_chunks,
            "total_vectors_in_store": total_vectors,
            "preview_first_chunk": chunks[0][:500],
        }

    except ValueError as exc:
        logger.error("document_ingestion_validation_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        logger.error("document_ingestion_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(exc)}",
        )