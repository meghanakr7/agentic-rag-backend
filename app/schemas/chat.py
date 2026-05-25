from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class QueryRoute(str, Enum):
    RAG = "rag"
    CONVERSATIONAL = "conversational"
    ESCALATION = "escalation"


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="User question or message.",
        examples=["What is verification in NASA systems engineering?"],
    )


class RetrievedChunk(BaseModel):
    text: str
    source: Optional[str] = None
    chunk_index: Optional[int] = None
    distance: Optional[float] = None


class ChatResponse(BaseModel):
    route: QueryRoute
    answer: str
    retrieved_chunks: List[RetrievedChunk] = []