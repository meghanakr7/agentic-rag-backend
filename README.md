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
## Architectural Choices

This project is organized as a modular FastAPI backend. FastAPI was chosen because it provides asynchronous API support, automatic request validation through Pydantic, and built-in Swagger documentation. Uvicorn is used as the ASGI server to run the application locally.

The code is separated into API, service, schema, template, static, and utility layers. The API layer contains the ingestion and chat routes. The service layer contains the core business logic for document loading, text chunking, vector storage, query routing, and LLM response generation. This separation makes the application easier to test, debug, and extend.

ChromaDB is used as the vector database because it is lightweight, easy to run locally, and supports persistent vector storage. The vector database stores document chunks, metadata, and embeddings so that user questions can retrieve the most relevant document context.

OpenAI is used for query routing and final response generation. The router classifies the user query into conversational, RAG, or escalation. The final LLM response is generated only after relevant document chunks are retrieved from ChromaDB.

## Chunking Strategy

Uploaded PDF or TXT files are first parsed into raw text. The text is cleaned by removing extra whitespace and then split into overlapping chunks.

The current chunking configuration uses:

- Chunk size: 1200 characters
- Chunk overlap: 200 characters

Chunking is necessary because large documents cannot be efficiently embedded or passed fully into an LLM prompt. Smaller chunks allow the system to retrieve only the most relevant parts of the uploaded document.

The overlap helps preserve context across chunk boundaries. If an important explanation is split between two chunks, the overlap reduces the chance that useful context is lost.

## Vector Embedding Choice

This project uses a local Sentence Transformers embedding model through ChromaDB:

`all-MiniLM-L6-v2`

This model converts each text chunk into a numerical vector representation. Similar pieces of text have similar vectors, which allows semantic search over the uploaded document.

A local embedding model was chosen because it is lightweight, works well for local development, avoids per-request embedding API cost, and keeps document embedding generation inside the application environment.

ChromaDB uses the configured embedding function to automatically generate embeddings when chunks are added to the collection. During chat, the user query is also embedded and compared with stored chunk vectors to retrieve the most relevant context.

## Agentic Routing Strategy

The chat endpoint uses an agentic query router before answering the user. The router classifies every query into one of three routes:

1. Conversational
2. RAG
3. Escalation

Conversational queries include greetings, small talk, and basic assistant-introduction questions. These are answered directly without retrieval.

RAG queries are safe document-related questions. For these queries, the backend retrieves the top relevant chunks from ChromaDB and sends them to the LLM to generate a grounded answer.

Escalation queries include sensitive, private, unsafe, confidential, unauthorized, or security-related requests. These are declined and recorded in `data/escalations.jsonl`.

The routing system uses a safety-first approach. Obvious escalation requests are detected before retrieval. Then an LLM-based router classifies the query. If the LLM router fails, fallback rules classify the query using local checks. This ensures the system can still handle greetings, document questions, and sensitive requests even if the LLM router is unavailable.

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