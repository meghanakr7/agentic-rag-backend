import json
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.schemas.chat import ChatRequest, ChatResponse, QueryRoute, RetrievedChunk
from app.services.llm import LLMService
from app.services.query_router import QueryRouter
from app.services.vector_store import VectorStoreService

router = APIRouter()
logger = structlog.get_logger()

query_router = QueryRouter()

ESCALATION_LOG_PATH = Path("data/escalations.jsonl")
ESCALATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    return LLMService()


def elapsed_seconds(start_time: float) -> float:
    return round(time.perf_counter() - start_time, 3)


def record_escalation(query: str) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "route": QueryRoute.ESCALATION.value,
        "status": "flagged",
    }

    with ESCALATION_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def conversational_answer(query: str) -> str:
    return (
        "Hello! I am your aerospace systems engineering knowledge assistant. "
        "I can answer greetings directly, flag sensitive requests for escalation, "
        "and answer document-based questions using the uploaded NASA systems engineering handbook."
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    request_start = time.perf_counter()

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    logger.info(
        "chat_request_started",
        query=query,
    )

    route_start = time.perf_counter()
    route = await run_in_threadpool(query_router.route, query)
    route_seconds = elapsed_seconds(route_start)

    logger.info(
        "timing_route",
        query=query,
        route=route.value,
        seconds=route_seconds,
    )

    logger.info(
        "query_routed",
        query=query,
        route=route.value,
    )

    if route == QueryRoute.CONVERSATIONAL:
        total_seconds = elapsed_seconds(request_start)

        logger.info(
            "timing_total_chat",
            query=query,
            route=route.value,
            seconds=total_seconds,
        )

        return ChatResponse(
            route=route,
            answer=conversational_answer(query),
            retrieved_chunks=[],
        )

    if route == QueryRoute.ESCALATION:
        escalation_start = time.perf_counter()
        await run_in_threadpool(record_escalation, query)
        escalation_seconds = elapsed_seconds(escalation_start)

        logger.info(
            "timing_escalation_record",
            query=query,
            seconds=escalation_seconds,
        )

        logger.warning(
            "sensitive_request_escalated",
            query=query,
            route=route.value,
            escalation_log_path=str(ESCALATION_LOG_PATH),
        )

        total_seconds = elapsed_seconds(request_start)

        logger.info(
            "timing_total_chat",
            query=query,
            route=route.value,
            seconds=total_seconds,
        )

        return ChatResponse(
            route=route,
            answer=(
                "I cannot help with sensitive, private, confidential, or unauthorized information. "
                "This request has been flagged for escalation."
            ),
            retrieved_chunks=[],
        )

    try:
        vector_store_start = time.perf_counter()
        vector_store = get_vector_store()
        vector_store_seconds = elapsed_seconds(vector_store_start)

        logger.info(
            "timing_vector_store_load",
            query=query,
            seconds=vector_store_seconds,
        )

        count_start = time.perf_counter()
        total_vectors = await run_in_threadpool(vector_store.count)
        count_seconds = elapsed_seconds(count_start)

        logger.info(
            "timing_vector_count",
            query=query,
            total_vectors=total_vectors,
            seconds=count_seconds,
        )

        if total_vectors == 0:
            total_seconds = elapsed_seconds(request_start)

            logger.info(
                "timing_total_chat",
                query=query,
                route=route.value,
                seconds=total_seconds,
            )

            return ChatResponse(
                route=route,
                answer=(
                    "I could not find any uploaded document content yet. "
                    "Please upload and ingest a PDF or TXT document first."
                ),
                retrieved_chunks=[],
            )

        retrieval_start = time.perf_counter()
        results = await run_in_threadpool(
            vector_store.query,
            query_text=query,
            top_k=3,
        )
        retrieval_seconds = elapsed_seconds(retrieval_start)

        logger.info(
            "timing_retrieval",
            query=query,
            top_k=3,
            seconds=retrieval_seconds,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            total_seconds = elapsed_seconds(request_start)

            logger.info(
                "timing_total_chat",
                query=query,
                route=route.value,
                seconds=total_seconds,
            )

            return ChatResponse(
                route=route,
                answer=(
                    "I could not find relevant context in the uploaded document. "
                    "Please ask a question related to the ingested document."
                ),
                retrieved_chunks=[],
            )

        retrieved_chunks = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            distance = distances[index] if index < len(distances) else None

            retrieved_chunks.append(
                RetrievedChunk(
                    text=document[:1000],
                    source=metadata.get("source"),
                    chunk_index=metadata.get("chunk_index"),
                    distance=distance,
                )
            )

        llm_service_start = time.perf_counter()
        llm_service = get_llm_service()
        llm_service_seconds = elapsed_seconds(llm_service_start)

        logger.info(
            "timing_llm_service_load",
            query=query,
            seconds=llm_service_seconds,
        )

        llm_start = time.perf_counter()
        answer = await run_in_threadpool(
            llm_service.generate_answer,
            query=query,
            context_chunks=documents,
        )
        llm_seconds = elapsed_seconds(llm_start)

        logger.info(
            "timing_llm_generation",
            query=query,
            model=getattr(llm_service, "model", "unknown"),
            seconds=llm_seconds,
        )

        total_seconds = elapsed_seconds(request_start)

        logger.info(
            "rag_answer_generated",
            query=query,
            retrieved_chunks=len(retrieved_chunks),
            total_vectors=total_vectors,
        )

        logger.info(
            "timing_total_chat",
            query=query,
            route=route.value,
            retrieved_chunks=len(retrieved_chunks),
            total_vectors=total_vectors,
            seconds=total_seconds,
        )

        return ChatResponse(
            route=route,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
        )

    except Exception as exc:
        total_seconds = elapsed_seconds(request_start)

        logger.error(
            "chat_query_failed",
            query=query,
            error=str(exc),
            seconds=total_seconds,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat query failed: {str(exc)}",
        )