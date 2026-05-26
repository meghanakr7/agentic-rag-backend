# Agentic RAG Backend

A FastAPI-based backend for an Agentic Retrieval-Augmented Generation (RAG) document chat application.

This project allows users to upload documents, process them into searchable chunks, store them in a vector database, and ask questions about the uploaded content through a chat interface.

The application also includes basic query routing so that different types of user messages are handled correctly.

## Project Purpose

This project was built as part of a backend assignment to demonstrate:

- FastAPI API development
- Asynchronous backend design
- Document ingestion
- PDF/text processing
- Chunking and embedding preparation
- Vector database usage
- Retrieval-Augmented Generation
- LLM-based response generation
- Query routing
- Sensitive request handling
- Basic frontend integration
- Logging and error handling
- Safe GitHub project setup

## Main Features

- Upload PDF or text documents
- Extract document text
- Split document content into chunks
- Store document chunks in a vector database
- Ask questions about uploaded documents
- Route user queries into different categories
- Handle greetings separately from document questions
- Handle sensitive or unsupported requests safely
- Serve a simple frontend from FastAPI
- Use environment variables for configuration
- Keep secrets and local files out of GitHub

## Query Routes

The chat system supports three main routes:

### 1. Conversational Route

Used for simple greetings or general small talk.

Example:

```text
User: Hello
Assistant: Hello! Ask me about the uploaded document.
```
### 2. RAG Route

Used when the user asks questions related to uploaded documents.

Example:

```text
User: What is this document about?
Assistant: The document is about ...
```

### 3. Escalation Route

Used when the user asks sensitive, unsafe, or unsupported questions.

Example:

```text
User: Give me confidential information.
Assistant: I cannot help with that request.
```

## Tech Stack

- Python
- FastAPI
- Uvicorn
- ChromaDB
- OpenAI / LLM integration
- HTML
- CSS
- JavaScript

## Project Structure

```text
agentic-rag-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── ingest.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── document_loader.py
│   │   ├── llm.py
│   │   ├── query_router.py
│   │   └── vector_store.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/iammeghana/agentic-rag-backend.git
cd agentic-rag-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

For macOS/Linux:

```bash
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` with your real values.

Example:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./data/chroma
```

Do not commit the real `.env` file.

## Running the Application

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Ingest Document

```text
POST /ingest
```

This endpoint uploads and processes a document.

Expected behavior:

- Accepts a PDF or text file
- Extracts text from the file
- Splits text into smaller chunks
- Stores chunks in the vector database
- Makes the document available for chat questions

### Chat

```text
POST /chat
```

This endpoint accepts a user question and returns a response.

Expected behavior:

- Greetings are answered conversationally
- Document-related questions use RAG
- Sensitive requests are declined or escalated

## Example Usage

1. Start the server.
2. Open the frontend in the browser.
3. Upload a PDF document.
4. Ask a question about the uploaded document.
5. Review the response.
6. Test greetings and sensitive questions.

Example questions:

```text
Hello
What is this document about?
Summarize the uploaded document.
What are the key points?
Give me confidential information.
```

## Validation Checklist

Use this checklist to confirm the application works correctly.

### Startup Validation

- The server starts without errors.
- The frontend page loads.
- `/docs` opens correctly.
- No missing import errors appear.

### Upload Validation

- A PDF can be uploaded.
- Text is extracted from the PDF.
- Chunks are created.
- Vector database files are created locally.
- The upload does not crash the server.

### Chat Validation

- Greetings return conversational responses.
- Document questions return document-based answers.
- Irrelevant questions are handled gracefully.
- Sensitive questions are rejected or escalated.
- Empty questions do not crash the app.

### RAG Validation

- The answer is based on uploaded document content.
- The system retrieves relevant document chunks.
- The system does not invent answers when context is missing.
- The response is clear and useful.

### Security Validation

- `.env` is not committed.
- API keys are not committed.
- Local vector database files are not committed.
- Uploaded documents are not committed.
- Virtual environment files are not committed.

## Files Not Pushed to GitHub

The following files and folders are intentionally ignored:

```text
.env
venv/
__pycache__/
data/
data/chroma/
data/uploads/
data/escalations.jsonl
app/api/key
debug_run.py
sample_docs/
```

These files are ignored because they may contain secrets, local data, uploaded files, generated database files, or machine-specific files.

## GitHub Notes

Before pushing, check the status:

```bash
git status
```

Safe files to push:

```text
README.md
.gitignore
.env.example
requirements.txt
app/
```

Do not push:

```text
.env
venv/
data/
app/api/key
debug_run.py
sample_docs/
__pycache__/
```

## Future Improvements

- Add unit tests
- Add Docker support
- Add better frontend upload progress
- Add source citations for retrieved chunks
- Add user sessions for multiple documents
- Add better error messages
- Add production authentication
- Add deployment instructions
- Add evaluation scripts for RAG quality

## Author

Meghana