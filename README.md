# 🇮🇳 Agentic Government Scheme Recommendation Chatbot

> **A Multilingual, Profile-Aware, and Eligibility-Guided Civic Beneficiary Assistance System**

[![Tests](https://img.shields.io/badge/pytest-51%20passed%20(100%25)-brightgreen.svg)](#running-tests)
[![Frontend](https://img.shields.io/badge/React%2019-Vite%20%2B%20TypeScript-blue.svg)](#frontend-setup)
[![Backend](https://img.shields.io/badge/FastAPI-Python%203.11%2B-009688.svg)](#backend-setup)
[![Agent](https://img.shields.io/badge/LangGraph-Single%20AI%20Orchestrator-orange.svg)](#architecture)
[![RAG](https://img.shields.io/badge/RAG-Hybrid%20(Vector%20%2B%20BM25%20%2B%20RRF)-blueviolet.svg)](#hybrid-rag-pipeline)
[![Languages](https://img.shields.io/badge/Languages-English%20%7C%20%E0%A4%B9%E0%A4%BF%E0%A4%82%E0%A4%A6%E0%A4%81%20%7C%20%E0%A4%AE%E0%A4%B0%E0%A4%BE%E0%A4%A0%E0%A5%80-red.svg)](#multilingual-support)

A full-stack, enterprise-grade AI-powered web platform designed to help Indian citizens discover government welfare schemes tailored to their individual profile, assess their eligibility with deterministic precision, and receive source-grounded, explainable recommendations — natively in **English, Hindi (हिंदी), and Marathi (मराठी)**.

---

## 📌 Latest Project Status

| Metric / Component | Status | Details |
|---|---|---|
| **Automated Test Suite** | 🟢 **51 / 51 Passed (100%)** | Unit (42), Integration (2), Retrieval Benchmarks (7) |
| **Frontend Production Build** | 🟢 **Passing (`tsc -b && vite build`)** | Zero TypeScript compilation or bundling errors |
| **Chat-First Guest Flow** | 🟢 **Zero-Barrier Access** | Immediate chat without signup; optional Sign In to persist history |
| **Backend API Engine** | 🟢 **Operational (`FastAPI 0.115`)** | REST endpoints for chat, retrieval, eligibility, auth & sync |
| **AI Orchestrator** | 🟢 **Production Ready** | LangGraph state graph with progressive profile extraction & MCQ mode |
| **Hybrid RAG Pipeline** | 🟢 **Benchmarked & Operational** | Dense vector search + BM25 keyword index + RRF fusion + Reranking |
| **Eligibility Engine** | 🟢 **Deterministic (Python)** | Evaluates income, age, landholding, caste, gender, state without hallucination |
| **LLM Grounding Layer** | 🟢 **Multi-Provider & Fallback** | Gemini 1.5/2.0 Flash + OpenAI GPT-4o-mini + Offline Grounded Fallback |
| **Civic Portal UI** | 🟢 **Full Beneficiary Suite** | Chat Caseworker, Citizen Dashboard, Active Applications, DBT Tracker, DigiLocker |

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
- [Running Tests & Verification](#running-tests--verification)
- [Key Features](#key-features)
- [Supported Schemes](#supported-schemes)
- [How It Works](#how-it-works)
- [Roadmap](#roadmap)

---

## Overview

India administers hundreds of central and state welfare initiatives, yet citizens frequently face information fragmentation, intricate eligibility conditions, language obstacles, and lack of actionable guidance. This platform bridges that gap by providing:

1. **Natural Language Inquiry**: Citizens express their needs in everyday conversational English, Hindi, or Marathi (e.g., *"मी महाराष्ट्रातील शेतकरी आहे, मला कोणती मदत मिळू शकते?"*).
2. **Autonomous LangGraph Orchestrator**: Understands intent, progressively aggregates user demographic attributes into a structured profile, identifies missing criteria, and prompts for clarification or offers guided MCQs.
3. **Hybrid RAG Retrieval**: Combines semantic embeddings (vector search) with lexical matching (BM25) and Reciprocal Rank Fusion (RRF), verified by a deterministic cross-encoder reranker.
4. **Deterministic Rule Engine**: Completely eliminates LLM hallucinations in eligibility determination by evaluating criteria (age, income caps, land size, caste, gender, residency) in pure Python code.
5. **Source-Grounded Explanations**: Generates citations, matched condition breakouts, missing document checklists, and direct official application portal links.
6. **Unified Citizen Suite**: A complete civic portal featuring a real-time Profile Dossier, Citizen Dashboard, Active Applications tracker, Direct Benefit Transfer (DBT) monitor, and DigiLocker document vault.

---

## Architecture

```
+---------------------------------------------------------------------------------------+
|                                REACT 19 + VITE FRONTEND                               |
|                     (Civic Blueprint Material Design 3 Design System)                  |
|                                                                                       |
|  +--------------------+  +----------------------+  +-------------------------------+  |
|  | Agentic Caseworker |  |  Citizen Dashboard   |  |   Recommendations Explorer    |  |
|  | (Chat + MCQ Modes) |  | (Stats, Alerts, DBT) |  | (Search, Filters, Categories) |  |
|  +--------------------+  +----------------------+  +-------------------------------+  |
|  | Active Applications|  |  DigiLocker Dossier  |  |    DBT Disbursements View     |  |
|  | (Status & Stages)  |  | (Verified Doc Vault) |  |   (Direct Transfer Audits)    |  |
|  +--------------------+  +----------------------+  +-------------------------------+  |
|          ^                         ^                               ^                  |
|          |                         |                               |                  |
|          +--- Language Switcher (EN / HI / MR) | Interactive Modals + Dossier --------+  |
+-------------------------------------------+-------------------------------------------+
                                            |
                                 REST API (HTTP / JSON)
                                            |
+-------------------------------------------v-------------------------------------------+
|                                    FASTAPI BACKEND                                    |
|                      (CORS, Lifespan Indexing, Pydantic v2 Models)                    |
+-------------------------------------------+-------------------------------------------+
                                            |
+-------------------------------------------v-------------------------------------------+
|                           LANGGRAPH AI ORCHESTRATOR AGENT                             |
|                                                                                       |
|  1. Understand & Extract      2. Sufficiency Check          3. Route Decision         |
|  - Multilingual Entity Parser - Evaluates Missing Fields    - Clarification (Text/MCQ)|
|  - Devanagari Normalization   - Occupation / State / Income - or Proceed to Retrieval |
+---------------------+---------------------------------------------+-------------------+
                      |                                             |
                      v                                             v
+---------------------+-------------+             +-----------------+-------------------+
|         HYBRID RAG PIPELINE       |             |   DETERMINISTIC ELIGIBILITY ENGINE  |
|                                   |             |                                     |
|  +-----------------------------+  |             |  • Evaluates structured profile     |
|  | Metadata State & Cat Filter |  |             |  • Binary & numeric boundary checks |
|  +--------------+--------------+  |             |  • Categorizes status:              |
|                 |                 |             |    - ELIGIBLE                       |
|        +--------+--------+        |             |    - NOT_ELIGIBLE                   |
|        v                 v        |             |    - INFORMATION_MISSING            |
|  Vector Search      BM25 Index    |             |  • Generates pass/fail condition    |
|   (Dense Embed)    (Lexical BM25) |             |    explanations without LLM bias    |
|        +--------+--------+        |             +-----------------+-------------------+
|                 v                 |                               |
|      Reciprocal Rank Fusion       |                               |
|                 v                 |                               |
|       Cross-Encoder Reranker      |                               |
+-----------------+-----------------+                               |
                  |                                                 |
                  +------------------------+------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                GROUNDED EXPLANATION LAYER                             |
|                                                                                       |
|   • Configurable Provider: Google Gemini API (1.5 / 2.0 Flash) or OpenAI (GPT-4o)     |
|   • Robust Deterministic Fallback: Offline Grounded Generator (zero external API cost)|
|   • Strict Anti-Hallucination Prompting: Grounded solely on retrieved scheme documents|
|   • Multilingual Translation & Response Synthesis (English, Hindi, Marathi)           |
+------------------------------------------+--------------------------------------------+
                                           |
                         +-----------------+-----------------+
                         |                                   |
                         v                                   v
             [Vector Store: Qdrant / Memory]     [Relational DB: SQLite / Postgres]
```

---

## Tech Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Frontend Framework** | **React 19, TypeScript, Vite 8** | High-performance SPA with modern React paradigms |
| **Design System** | **Civic Blueprint (MD3 Vanilla CSS)** | Government-grade design tokens, public-service aesthetics, responsive grid |
| **Typography** | **Public Sans & Inter (Google Fonts)** | Clean, accessible civic readability across desktop and mobile |
| **Internationalization** | **i18next, react-i18next** | Seamless real-time switching between English, Hindi, and Marathi |
| **Backend Framework** | **FastAPI 0.115, Uvicorn, Python 3.11+** | High-throughput asynchronous REST API |
| **Agentic Workflow** | **LangGraph, LangChain Core** | Stateful multi-turn agent graph with conditional routing & feedback loops |
| **Hybrid Retrieval** | **Rank-BM25, Reciprocal Rank Fusion (RRF)** | Combined dense semantics + exact keyword and department name matching |
| **Vector Storage** | **Qdrant Vector DB & InMemoryVectorStore** | Scalable vector search with Qdrant Cloud support & zero-dependency local mode |
| **Eligibility Verification** | **Deterministic Rule Engine (Python)** | High-assurance condition evaluation eliminating hallucination risks |
| **LLM Grounding Layer** | **Google Gemini (`gemini-1.5-flash`), OpenAI** | Grounded explanation synthesis with automatic offline fallback mode |
| **Persistence & Models** | **SQLAlchemy, Pydantic v2, SQLite / PostgreSQL** | Scheme catalogs, citizen profile dossier, and conversation audit trails |
| **Testing & Evaluation** | **Pytest, LangSmith, AnyIO** | 49 automated unit, integration, and retrieval evaluation tests |

---

## Project Structure

```
gov scheme chatbot/
├── backend/
│   └── app/
│       ├── main.py                     # FastAPI application, lifespan indexing & API routes
│       ├── agent/                      # LangGraph multi-turn agentic orchestrator
│       │   ├── graph.py                # StateGraph assembly, conditional routing edges
│       │   ├── service.py              # Orchestrator service wrapper & turn execution
│       │   ├── state.py                # TypedDict state schema definition
│       │   ├── nodes/
│       │   │   └── handlers.py         # Graph node logic (extract, sufficiency, clarify, RAG)
│       │   └── prompts/
│       │       └── templates.py        # Localized clarification prompts & MCQ options
│       ├── core/
│       │   ├── config.py               # Pydantic Settings (.env configuration)
│       │   └── database.py             # SQLAlchemy session and engine management
│       ├── eligibility/                # Deterministic rule engine
│       │   ├── engine.py               # Core condition evaluator (age, income, caste, state)
│       │   ├── models.py               # Evaluation models (ELIGIBLE, NOT_ELIGIBLE, MISSING)
│       │   └── service.py              # Recommendation aggregation service
│       ├── evaluation/                 # Retrieval & RAG quality metrics
│       │   └── metrics.py              # Precision@K, Recall@K, Reciprocal Rank (MRR)
│       ├── llm/                        # Multi-provider LLM grounding layer
│       │   ├── factory.py              # Provider factory (Gemini, OpenAI, Offline fallback)
│       │   ├── gemini.py               # Google Gemini client with structured prompts
│       │   ├── openai.py               # OpenAI GPT-4o integration
│       │   ├── offline.py              # Zero-dependency deterministic offline fallback
│       │   └── prompts.py              # Anti-hallucination grounded system prompts
│       ├── models/                     # Database ORM entities & repositories
│       │   ├── scheme_model.py         # Scheme database model
│       │   ├── profile_model.py        # User profile database model
│       │   ├── conversation_model.py   # Chat session audit model
│       │   └── repositories.py         # SQLAlchemy repositories (CRUD operations)
│       ├── profile/                    # Profile extraction & multilingual parsing
│       │   └── extractor.py            # Devanagari & English rule extractor, numerals & regex
│       ├── rag/                        # Hybrid RAG retrieval pipeline
│       │   ├── bm25/                   # Lexical BM25 index with tokenization
│       │   ├── chunking/               # Scheme document chunker with metadata headers
│       │   ├── embeddings/             # Deterministic multilingual embedding service
│       │   ├── fusion/                 # Reciprocal Rank Fusion (RRF) logic
│       │   ├── ingestion/              # Indexing CLI and indexer utility
│       │   ├── reranker/               # Cross-encoder semantic ranker
│       │   ├── retriever/              # Hybrid retriever & query preprocessor
│       │   └── vector_store/           # Qdrant client store & in-memory vector store
│       └── schemas/                    # Pydantic v2 request/response schemas
│           ├── profile_schema.py       # User profile model & field constraints
│           ├── retrieval_schema.py     # Retrieval requests, evidence chunks & responses
│           └── scheme_schema.py        # Scheme catalog schema & condition specs
├── frontend/
│   ├── public/                         # Public assets, SVGs, favicon
│   ├── src/
│   │   ├── main.tsx                    # React application entry point
│   │   ├── App.tsx                     # Main layout container
│   │   ├── index.css                   # Civic Blueprint design tokens & component styles
│   │   ├── api/
│   │   │   └── client.ts               # Axios API client connecting to FastAPI backend
│   │   ├── components/
│   │   │   ├── Header.tsx              # Portal header, live context indicator & helplines
│   │   │   ├── Sidebar.tsx             # 6-view civic navigation sidebar
│   │   │   ├── ChatInterface.tsx       # Conversational AI assistant with MCQ support
│   │   │   ├── ProfileDossier.tsx      # Real-time citizen profile drawer with completion bar
│   │   │   ├── SchemeCard.tsx          # Scheme card with match badge, criteria & actions
│   │   │   ├── Modals.tsx              # One-click Application, Details, Help & Vault modals
│   │   │   └── views/
│   │   │       ├── CitizenDashboardView.tsx   # Dashboard with subsidy stats & alerts
│   │   │       ├── RecommendationsView.tsx    # Scheme directory with category filters
│   │   │       ├── ActiveApplicationsView.tsx # Application lifecycle & status tracker
│   │   │       ├── DbtDisbursementsView.tsx   # Direct Benefit Transfer audit records
│   │   │       └── DigiLockerView.tsx         # Document locker with verified badges
│   │   ├── i18n/
│   │   │   └── index.ts                # English, Hindi & Marathi UI localization resources
│   │   └── types/
│   │       └── api.ts                  # TypeScript interfaces for API contracts
│   ├── package.json                    # Frontend dependencies & build scripts
│   └── vite.config.ts                  # Vite build & development server configuration
├── data/
│   ├── processed/
│   │   └── sample_schemes.json         # Seed government scheme knowledge base
│   ├── evaluation/
│   │   └── sample_evaluation.json      # Gold-standard benchmark queries for retrieval eval
│   ├── gov_schemes.db                  # Local SQLite database (auto-created for dev)
│   └── raw/                            # Source documents and gazette records
├── tests/
│   ├── unit/                           # 40 Unit tests (API, DB, Engine, LLM, Profile, Agent)
│   ├── integration/                    # 2 End-to-end integration pipeline tests
│   └── retrieval/                      # 7 Hybrid retrieval & multilingual evaluation tests
├── requirements.txt                    # Complete frozen Python dependency manifest
├── .env.example                        # Environment variables template
├── pytest.ini                          # Pytest suite configuration
└── README.md                           # Project documentation
```

---

## Getting Started

### Prerequisites

| Requirement | Recommended Version | Note |
|---|---|---|
| **Python** | `3.11` to `3.14` | Backend environment |
| **Node.js** | `18+` (LTS) | Frontend runtime |
| **npm** | `9+` | Frontend package manager |
| **Git** | `2.x` | Source control |

> **Development Mode Notice**: The platform runs out of the box in zero-setup development mode using SQLite and an in-memory vector store. PostgreSQL and Qdrant instances are entirely optional.

---

### Backend Setup

1. **Clone the repository and enter the directory:**
   ```bash
   git clone https://github.com/Siddhi-S-Thakur/agentic-government-scheme-chatbot.git
   cd "gov scheme chatbot"
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   python -m venv .venv

   # On Windows (PowerShell / Command Prompt):
   .venv\Scripts\activate

   # On macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the sample file:
   cp .env.example .env
   ```
   *(Optionally add your `GEMINI_API_KEY` in `.env`. If omitted, the backend automatically uses the built-in deterministic offline fallback without requiring any external API key.)*

5. **Start the FastAPI backend server:**
   ```bash
   # On Windows:
   .venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000

   # On macOS / Linux:
   uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
   ```

   - **Backend Base URL**: `http://localhost:8000`
   - **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
   - **Alternative API Docs (ReDoc)**: `http://localhost:8000/redoc`
   - **Health Check**: `http://localhost:8000/health`

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Start the Vite development server:**
   ```bash
   npm run dev
   ```

   - Open your browser at: **`http://localhost:5173`**

4. **Verify production build (optional):**
   ```bash
   npm run build
   ```

---

## Environment Variables

Copy `.env.example` to `.env` in the project root. The available configuration keys:

| Variable | Description | Default | Required in Production |
|---|---|---|:---:|
| `APP_ENV` | Application environment (`development` / `production`) | `development` | No |
| `API_HOST` | FastAPI bind address | `0.0.0.0` | No |
| `API_PORT` | FastAPI port | `8000` | No |
| `LLM_PROVIDER` | Active LLM service (`gemini`, `openai`, or `offline`) | `gemini` | No |
| `GEMINI_API_KEY` | Google Gemini API key | `""` | Yes (if Gemini active) |
| `OPENAI_API_KEY` | OpenAI API key | `""` | Yes (if OpenAI active) |
| `LLM_MODEL` | Default model identifier | `gemini-1.5-flash` | No |
| `EMBEDDING_MODEL_NAME` | Embedding transformer model | `paraphrase-multilingual-MiniLM-L12-v2` | No |
| `POSTGRES_HOST` | Production PostgreSQL host | `localhost` | In Prod |
| `POSTGRES_DB` | Production PostgreSQL database | `gov_scheme_db` | In Prod |
| `POSTGRES_USER` | PostgreSQL username | `postgres` | In Prod |
| `POSTGRES_PASSWORD` | PostgreSQL password | `""` | In Prod |
| `QDRANT_HOST` | Production Qdrant vector database host | `localhost` | In Prod |
| `QDRANT_PORT` | Production Qdrant port | `6333` | In Prod |

---

## API Reference

The backend exposes clean, fully-typed REST endpoints:

### Endpoints Overview

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | System health check, active environment & indexed chunk count |
| `GET` | `/api/schemes` | Returns catalog summaries of all loaded government schemes |
| `POST` | `/api/retrieve` | Executes Hybrid RAG pipeline (vector + BM25 + RRF + reranking) |
| `POST` | `/api/eligibility` | Evaluates deterministic eligibility for a profile against scheme rules |
| `POST` | `/api/chat` | Main conversational endpoint (works for both guests & logged-in citizens) |
| `POST` | `/api/auth/register` | Register citizen credentials & optional demographic eligibility profile |
| `POST` | `/api/auth/login` | Authenticate citizen and retrieve existing session |
| `GET` | `/api/auth/me` | Validate session token and return user profile details |
| `GET` | `/api/conversations/{session_id}` | Retrieve persistent chat message history for registered session |
| `DELETE` | `/api/conversations/{session_id}` | Clear message history for a registered session |
| `POST` | `/api/conversations/sync` | Sync in-flight guest messages into an authenticated user account |
| `GET` | `/api/profile/{session_id}` | Retrieve structured citizen eligibility profile |
| `PUT` | `/api/profile/{session_id}` | Update citizen eligibility profile parameters |

---

### Request & Response Examples

#### 1. Conversational Chat (`POST /api/chat`)

**Request (English Discovery):**
```json
{
  "message": "I am a 28 year old farmer from Maharashtra with annual income of 2.4 lakhs. What schemes am I eligible for?",
  "session_state": null
}
```

**Request (Hindi / Marathi Inquiry):**
```json
{
  "message": "मी महाराष्ट्रातील शेतकरी आहे, मला सौर पंपासाठी काही योजना आहे का?",
  "session_state": null
}
```

**Response Structure:**
```json
{
  "response": "Based on verified government records, you are eligible for the following schemes...",
  "detected_language": "en",
  "interaction_mode": "text",
  "needs_clarification": false,
  "mcq_options": null,
  "profile": {
    "age": 28,
    "occupation": "farmer",
    "state": "Maharashtra",
    "annual_income": 240000.0,
    "preferred_language": "en"
  },
  "recommendations": [
    {
      "scheme_id": "pm-kisan",
      "scheme_name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
      "status": "ELIGIBLE",
      "match_percentage": 96.0,
      "effective_benefit": "₹6,000 per year in 3 equal installments",
      "department": "Ministry of Agriculture and Farmers Welfare",
      "matched_conditions": [
        {"condition_name": "Occupation", "status": "passed", "reason": "Farmer qualifies"}
      ],
      "unmatched_conditions": [],
      "missing_conditions": [],
      "required_documents": ["Aadhaar Card", "Land Ownership Record (7/12 extract)", "Bank Account Details"],
      "application_link": "https://pmkisan.gov.in"
    }
  ],
  "source_urls": ["https://pmkisan.gov.in"],
  "session_state": {
    "messages": [...],
    "profile": {...},
    "detected_language": "en",
    "interaction_mode": "text"
  }
}
```

---

#### 2. Hybrid Retrieval (`POST /api/retrieve`)

```json
{
  "query": "solar pump agriculture subsidy Maharashtra",
  "profile": {
    "occupation": "farmer",
    "state": "Maharashtra",
    "annual_income": 240000
  },
  "top_k": 3,
  "debug": true
}
```

#### 3. Deterministic Eligibility Check (`POST /api/eligibility`)

```json
{
  "profile": {
    "age": 28,
    "annual_income": 240000,
    "state": "Maharashtra",
    "occupation": "farmer"
  },
  "scheme_id": "pm-kisan"
}
```

---

## Running Tests & Verification

The project includes an automated test suite across unit, integration, and retrieval evaluation benchmarks.

### Run All Tests
```bash
# From project root with .venv activated:
.venv\Scripts\pytest.exe -v
```

### Run Specific Test Suites
```bash
# 1. Deterministic Eligibility Rule Engine tests:
.venv\Scripts\pytest.exe tests/unit/test_eligibility_engine.py -v

# 2. LangGraph Agent Orchestrator & Multi-Turn tests:
.venv\Scripts\pytest.exe tests/unit/test_orchestrator_graph.py -v

# 3. Multilingual Profile Extractor tests (EN / HI / MR):
.venv\Scripts\pytest.exe tests/unit/test_profile_extractor.py -v

# 4. LLM Service & Anti-Hallucination Grounding tests:
.venv\Scripts\pytest.exe tests/unit/test_llm_service.py -v

# 5. Hybrid RAG Retrieval Benchmarks (Recall@K, MRR):
.venv\Scripts\pytest.exe tests/retrieval/ -v

# 6. End-to-End Integration Pipeline tests:
.venv\Scripts\pytest.exe tests/integration/ -v
```

### Run Frontend Typecheck & Build
```bash
cd frontend
npm run build
```

---

## Key Features

### 🤖 1. Autonomous LangGraph Orchestrator
- **Stateful Multi-Turn Graph**: Maintains conversation context, intent tracking, and profile state.
- **Adaptive Clarification**: If critical criteria (e.g., state or occupation) are missing for broad searches, the agent asks follow-up questions before triggering retrieval.
- **Guided MCQ Mode**: Users can toggle or request MCQ mode to answer targeted questions via interactive buttons.

### 🔎 2. High-Precision Hybrid RAG Pipeline
- **Dual-Retrieval Architecture**: Semantic dense vector search + lexical BM25 keyword search.
- **Reciprocal Rank Fusion (RRF)**: Merges disparate rank lists objectively.
- **Cross-Encoder Reranker**: Reranks top candidates to maximize precision.
- **Metadata Pre-Filtering**: Filters out irrelevant state-specific schemes prior to retrieval.

### ⚖️ 3. Zero-Hallucination Eligibility Engine
- **Deterministic Python Rules**: Eligibility is evaluated via strict code logic, not generative guesswork.
- **Three-Tier Status**: Categorizes schemes into `ELIGIBLE`, `NOT_ELIGIBLE`, or `INFORMATION_MISSING`.
- **Condition Transparency**: Outputs detailed breakdowns of which specific criteria passed or failed.

### 🌐 4. Native Tri-Lingual Support
- **Full Localization**: Complete UI and agent explanations in English, Hindi (हिंदी), and Marathi (मराठी).
- **Devanagari Normalization**: Automatically handles Marathi and Hindi numerals (e.g., `३०` → `30`) and currency notations (`₹१,८०,०००` → `180000`).

### 🏛️ 5. Civic Blueprint Beneficiary Suite
- **Agentic Caseworker**: Interactive conversational interface with prompt suggestions, live telemetry, and evidence inspect drawers.
- **Citizen Dashboard**: Live metric cards, estimated grant aid, priority alerts, and recent subsidy activities.
- **AI Recommendations Explorer**: Comprehensive scheme catalog with category tabs (Agriculture, Education, Healthcare, Social Welfare, Women & Child).
- **Active Applications Tracker**: Live lifecycle tracking of submitted applications with reference numbers and status stages.
- **Direct Benefit Transfer (DBT) Tracker**: Aadhaar-linked bank transfer logs, payment statuses, and disbursement timelines.
- **DigiLocker Dossier Vault**: Secure document locker for verified certificates (Aadhaar, 7/12 Land Extract, Caste, Income, Ration Card) with live verification badges.
- **Interactive Modals**: One-click scheme application generator, document import modal, profile editor, and helpline drawer.

---

## Supported Schemes

The initial knowledge base is seeded with verified government schemes across central and state tiers:

| Scheme Name | Level | Category | Target Beneficiaries | Key Benefit |
|---|---|---|---|---|
| **PM-KISAN** | Central | Agriculture | Small & Marginal Farmers | ₹6,000 / year in 3 installments |
| **PM-KUSUM Component-B** | Central / MH | Agriculture / Energy | Farmers with agricultural land | Up to 90% subsidy on Solar Pumps |
| **Sanjay Gandhi Niradhar** | Maharashtra | Social Welfare | Destitute, Elderly, Disabled | ₹1,500 / month financial assistance |
| **MahaDBT Post-Matric** | Maharashtra | Education | SC / ST / OBC Students | 100% Tuition fee waiver & maintenance |
| **Ayushman Bharat (PM-JAY)**| Central | Healthcare | Low-income families (SECC) | ₹5,00,000 / year cashless health cover |

---

## How It Works

1. **Citizen Inquires**: The citizen types or selects a prompt in English, Hindi, or Marathi.
2. **Profile Extraction**: The engine extracts attributes (age, occupation, income, state, district) using multilingual NLP and regex normalizers.
3. **Sufficiency Check**: The LangGraph agent determines whether sufficient context is available or if follow-up clarification is needed.
4. **Hybrid Retrieval**: Dense vectors and BM25 index retrieve top matching schemes, filtered by jurisdiction.
5. **Deterministic Evaluation**: Each candidate scheme's requirements are evaluated against the citizen's profile attributes.
6. **Grounded Synthesis**: The LLM synthesizes an empathetic, source-grounded response citing official documentation.
7. **Interactive Presentation**: The frontend renders recommendations, updates the Profile Dossier completion index, and displays actionable application buttons.

---

## Roadmap

- [x] LangGraph AI orchestrator with multi-turn progressive dialogue
- [x] Hybrid RAG pipeline (Vector + BM25 + RRF + Reranker)
- [x] Deterministic rule engine for eligibility evaluation
- [x] Multi-provider LLM grounding (Gemini + OpenAI + Offline Fallback)
- [x] React 19 + TypeScript + Vite frontend with Civic Blueprint design system
- [x] Multilingual support (English, Hindi, Marathi) with instant switching
- [x] Citizen Dashboard, Active Applications & DBT Tracker views
- [x] DigiLocker Document Vault integration interface
- [ ] OCR-based document upload & auto-fill for application forms
- [ ] Voice input & speech synthesis for rural accessibility
- [ ] WhatsApp & Telegram bot integration for low-bandwidth access
- [ ] Expansion to additional regional languages (Tamil, Telugu, Bengali, Gujarati)

---

## License

Developed for public benefit and civic empowerment. Distributed under the MIT License.
