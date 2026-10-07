# 🇮🇳 Agentic Government Scheme Recommendation Chatbot

> **A Multilingual, Profile-Aware and Eligibility-Guided Government Scheme Assistance System**

A full-stack AI-powered web application that helps Indian citizens discover government schemes relevant to their profile, understand their eligibility, and get explainable, source-grounded recommendations — in **English, Hindi, and Marathi**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Features](#features)
- [How It Works](#how-it-works)

---

## Overview

Citizens often struggle to identify government schemes relevant to their situation. This platform solves that by:

- Allowing users to describe their needs in **natural language** (English, Hindi, or Marathi)
- Using a **LangGraph AI orchestrator** to understand intent, maintain a user profile, and decide what to do next
- Retrieving relevant schemes via a **Hybrid RAG pipeline** (vector search + BM25 + reranking)
- Checking eligibility through a **deterministic rule engine**
- Returning **explainable recommendations** with benefits, required documents, and official application links

---

## Architecture

```
+----------------------------------------------+
|            React + Vite Web App              |
|  Language Toggle | Chat | MCQ | Scheme Results|
+---------------------+------------------------+
                      |
              HTTP (FastAPI)
                      |
+---------------------v------------------------+
|              FastAPI Backend                 |
|           (localhost:8000)                   |
+---------------------+------------------------+
                      |
+---------------------v------------------------+
|         LangGraph Orchestrator Agent         |
|   Intent -> Profile -> Missing Info -> Route  |
+-------+--------------------------------------+
        |                          |
        v                          v
  Profile Extraction         Hybrid RAG Pipeline
                          +--------+--------+
                          v                 v
                     Vector Search        BM25
                          +--------+--------+
                                   v
                               Reranker
                                   v
                           Eligibility Engine
                                   v
                          Explainable Result
                                   v
                     LLM Response (Selected Language)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, TypeScript, i18next |
| **Backend** | Python, FastAPI, Uvicorn |
| **Agent Workflow** | LangGraph |
| **RAG** | LangChain, BM25 (rank-bm25), in-memory vector store |
| **Eligibility Engine** | Custom Python rule engine |
| **LLM** | Google Gemini API / OpenAI API (configurable) |
| **Vector DB** | Qdrant (configurable; in-memory for dev) |
| **Structured DB** | PostgreSQL / SQLite (dev) |
| **Multilingual** | sentence-transformers multilingual embeddings |

---

## Project Structure

```
gov scheme chatbot/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI app entry point
│       ├── agent/                   # LangGraph orchestrator
│       │   ├── graph.py             # Workflow graph definition
│       │   ├── service.py           # Agent service interface
│       │   ├── state.py             # Conversation state schema
│       │   ├── nodes/               # Graph node implementations
│       │   └── prompts/             # LLM prompt templates
│       ├── core/
│       │   ├── config.py            # App configuration (env-based)
│       │   └── database.py          # DB connection setup
│       ├── eligibility/
│       │   └── engine.py            # Deterministic rule engine
│       ├── models/
│       │   ├── scheme_model.py      # Scheme ORM model
│       │   └── conversation_model.py
│       ├── rag/
│       │   ├── embeddings/          # Multilingual embedding service
│       │   ├── bm25/                # BM25 keyword index
│       │   ├── vector_store/        # In-memory vector store
│       │   ├── reranker/            # Cross-encoder reranker
│       │   ├── fusion/              # Reciprocal Rank Fusion (RRF)
│       │   ├── retriever/           # Hybrid retriever (combines all)
│       │   ├── chunking/            # Scheme document chunking
│       │   └── ingestion/           # Indexing pipeline
│       ├── schemas/                 # Pydantic request/response schemas
│       └── profile/                 # User profile management
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx    # Main chat UI
│   │   │   ├── MessageBubble.tsx    # Chat message component
│   │   │   ├── ProfilePanel.tsx     # User profile sidebar
│   │   │   ├── SchemeResults.tsx    # Scheme recommendation cards
│   │   │   └── LanguageSwitcher.tsx # EN / HI / MR toggle
│   │   ├── i18n/                    # Translation files
│   │   ├── api/                     # Axios API client
│   │   └── types/                   # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── processed/
│   │   └── sample_schemes.json      # Seed scheme data
│   └── raw/                         # Raw scheme source data
├── tests/
│   ├── unit/                        # Unit tests (eligibility, profile)
│   └── retrieval/                   # Retrieval evaluation tests
├── .env.example                     # Environment variable template
├── pytest.ini                       # Test configuration
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

> **Optional (for full production setup):** PostgreSQL 15+, Qdrant (or use Qdrant Cloud)

---

### Backend Setup

1. **Navigate to the project root:**
   ```bash
   cd "gov scheme chatbot"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn langgraph langchain-core rank-bm25 pydantic python-dotenv sqlalchemy qdrant-client google-generativeai openai
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your API keys
   ```

5. **Start the backend server:**
   ```bash
   # Windows
   .venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

   # macOS/Linux
   uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
   ```

   - API: **http://localhost:8000**
   - Swagger UI: **http://localhost:8000/docs**
   - ReDoc: **http://localhost:8000/redoc**

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   Frontend: **http://localhost:5173**

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | Application environment | `development` |
| `API_HOST` | Backend host | `0.0.0.0` |
| `API_PORT` | Backend port | `8000` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_DB` | Database name | `gov_scheme_db` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | *(required)* |
| `QDRANT_HOST` | Qdrant vector DB host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `LLM_PROVIDER` | `gemini` or `openai` | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key | *(required for LLM)* |
| `OPENAI_API_KEY` | OpenAI API key | *(optional)* |
| `LLM_MODEL` | Model name | `gemini-1.5-flash` |
| `EMBEDDING_MODEL_NAME` | Multilingual embedding model | `paraphrase-multilingual-MiniLM-L12-v2` |

> **Note:** The backend works in development mode without PostgreSQL or Qdrant.
> It uses an in-memory vector store and auto-loads `data/processed/sample_schemes.json`.

---

## API Reference

Base URL: `http://localhost:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check + indexed scheme count |
| `GET` | `/api/schemes` | List all loaded schemes |
| `POST` | `/api/retrieve` | Run Hybrid RAG retrieval |
| `POST` | `/api/eligibility` | Check eligibility for a user profile |
| `POST` | `/api/chat` | Main conversational endpoint (agent) |

### Chat Request Example

```json
POST /api/chat
{
  "message": "I am a farmer in Maharashtra with income of 2 lakhs. Which schemes am I eligible for?",
  "session_state": null
}
```

### Retrieve Request Example

```json
POST /api/retrieve
{
  "query": "scheme for farmers in Maharashtra",
  "profile": {
    "occupation": "farmer",
    "state": "Maharashtra",
    "income": 200000
  },
  "top_k": 5,
  "debug": true
}
```

### Eligibility Check Example

```json
POST /api/eligibility
{
  "profile": {
    "age": 25,
    "income": 180000,
    "state": "Maharashtra",
    "occupation": "farmer"
  },
  "scheme_id": "pm_kisan"
}
```

---

## Running Tests

```bash
# From the project root (with .venv activated)
.venv\Scripts\pytest.exe

# Run specific test files
.venv\Scripts\pytest.exe tests/unit/test_eligibility_engine.py -v
.venv\Scripts\pytest.exe tests/retrieval/ -v
```

---

## Features

### Implemented (MVP)
- **Multilingual chat** — English, Hindi, Marathi
- **AI Orchestrator** — LangGraph-based agent controls the full workflow
- **Hybrid RAG** — Vector search + BM25 keyword search + Reciprocal Rank Fusion
- **Deterministic Eligibility Engine** — Rule-based evaluation (Eligible / Not Eligible / Incomplete)
- **Explainable Recommendations** — Matching conditions, missing criteria, benefits, documents, links
- **Optional MCQ Mode** — Guided question-answer mode on user request
- **Language Switcher** — Full UI translation via i18next
- **Profile Panel** — Displays extracted user profile in real-time
- **Scheme Result Cards** — Structured display of recommendation details

### Planned (Advanced Features)
- Scheme comparison
- Document upload & OCR extraction
- Certificate-based eligibility verification
- Personalized scheme dashboard
- Saved user profiles (persistent)
- Additional Indian languages
- Automatic knowledge-base updates

---

## How It Works

1. **User sends a message** in any supported language
2. **LangGraph Orchestrator** detects intent and extracts profile attributes (age, income, state, occupation, etc.)
3. **If information is missing** → Agent asks a follow-up question (text or MCQ)
4. **When enough context is available** → Hybrid RAG retrieves candidate schemes:
   - Metadata filtering narrows the search space
   - Vector search finds semantically similar schemes
   - BM25 matches exact keywords (scheme names, beneficiary categories)
   - RRF combines results; cross-encoder reranker prioritizes the best matches
5. **Eligibility Engine** evaluates each scheme's rules against the user profile deterministically
6. **LLM generates** a natural-language explanation in the user's selected language
7. **Frontend** displays the response, updated profile panel, and scheme result cards

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with tests
4. Submit a pull request

---

## License

This project is developed for educational and public benefit purposes.
