from pathlib import Path
from pypdf import PdfReader


class DocumentLoader:
    @staticmethod
    async def load_document(file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() == ".pdf":
            return DocumentLoader._load_pdf(path)

        if path.suffix.lower() == ".txt":
            return DocumentLoader._load_txt(path)

        raise ValueError("Unsupported file type. Only PDF and TXT files are allowed.")

    @staticmethod
    def _load_pdf(path: Path) -> str:
        reader = PdfReader(str(path))
        pages_text = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"\n\n[Page {page_number}]\n{text}")

        full_text = "\n".join(pages_text).strip()

        if not full_text:
            raise ValueError("No readable text found in the PDF.")

        return full_text

    @staticmethod
    def _load_txt(path: Path) -> str:
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            raise ValueError("Uploaded text file is empty.")

        return text