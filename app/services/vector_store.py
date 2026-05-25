from typing import List

import chromadb
import structlog
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = structlog.get_logger()


class VectorStoreService:
    def __init__(self, persist_directory: str = "data/chroma"):
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="nasa_systems_engineering",
            embedding_function=self.embedding_function,
            metadata={"description": "NASA Systems Engineering Handbook knowledge base"},
        )

    def add_chunks(self, chunks: List[str], source_filename: str) -> int:
        if not chunks:
            raise ValueError("No chunks provided to store.")

        self._delete_existing_chunks_for_source(source_filename)

        ids = [
            f"{source_filename}::chunk-{index}"
            for index, _ in enumerate(chunks)
        ]

        metadatas = [
            {
                "source": source_filename,
                "chunk_index": index,
            }
            for index, _ in enumerate(chunks)
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )

        logger.info(
            "chunks_stored_in_vector_db",
            source=source_filename,
            total_chunks=len(chunks),
        )

        return len(chunks)

    def _delete_existing_chunks_for_source(self, source_filename: str) -> None:
        existing = self.collection.get(
            where={"source": source_filename},
            include=[],
        )

        existing_ids = existing.get("ids", [])

        if existing_ids:
            self.collection.delete(ids=existing_ids)

            logger.info(
                "existing_chunks_deleted_for_source",
                source=source_filename,
                deleted_chunks=len(existing_ids),
            )

    def query(self, query_text: str, top_k: int = 3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        return results

    def count(self) -> int:
        return self.collection.count()