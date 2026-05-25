from typing import List


class TextChunker:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        cleaned_text = self._clean_text(text)

        if not cleaned_text:
            raise ValueError("Cannot chunk empty text.")

        chunks = []
        start = 0
        text_length = len(cleaned_text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = cleaned_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks

    @staticmethod
    def _clean_text(text: str) -> str:
        return " ".join(text.split())