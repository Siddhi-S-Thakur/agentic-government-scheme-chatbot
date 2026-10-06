# Project Context

## 1. Project Overview

### Project Title
**Agentic RAG-Based Government Scheme Recommendation Chatbot**

### Subtitle
**A Multilingual, Profile-Aware and Eligibility-Guided Government Scheme Assistance System**

### Project Summary

This project is a multilingual web-based government scheme assistance platform. Its purpose is to help citizens discover government schemes that may be relevant to their needs and understand their eligibility, benefits, required documents, and application process.

The system will use an **AI orchestrator agent** to control the workflow. The agent will understand the user's request, maintain the user's relevant profile information, decide whether more information is required, trigger the appropriate tools, retrieve relevant government schemes using Hybrid RAG, request eligibility checking, and coordinate the final response.

The chatbot will primarily support normal text-based interaction. **MCQ mode is optional** and will be used only when the user chooses it. The user can switch to a guided MCQ interaction when they prefer predefined options instead of typing answers.

The complete website will support **English, Hindi and Marathi** through a language switcher. The architecture should be designed so additional Indian languages can be added later.

---

## 2. Problem Being Solved

Government schemes are available for different groups of citizens, but users often find it difficult to identify schemes relevant to their situation and understand their eligibility requirements.

A user may need to know:

- Which schemes are relevant to their requirement
- Whether they satisfy the eligibility conditions
- What benefits are provided
- Which documents are required
- How to apply
- Where to find the official information

A simple search or RAG chatbot is not sufficient because the system may need to ask follow-up questions, maintain profile information, check eligibility conditions, and decide what action should happen next.

The project therefore aims to build a **profile-aware, multilingual and agent-controlled scheme assistance system**.

---

## 3. Core Design Principles

### 3.1 Agent is the Controller

The project will use **one main AI orchestrator agent**.

The agent is responsible for deciding what should happen next.

It can:

1. Understand the user's intent.
2. Extract relevant profile information.
3. Check whether enough information is available.
4. Ask for missing information.
5. Continue normal text interaction or use MCQ mode if the user has selected it.
6. Trigger the Hybrid RAG retrieval pipeline.
7. Send candidate schemes to the eligibility engine.
8. Request additional information if required.
9. Coordinate scheme comparison or additional details when needed.
10. Generate/coordinate the final response in the selected language.

The project will **not use multiple independent AI agents** unless a later implementation requirement clearly justifies them.

### 3.2 RAG is a Tool Used by the Agent

RAG is not the agent itself.

- **Agent:** decides what action should happen next.
- **RAG:** retrieves relevant scheme information.
- **Eligibility Engine:** evaluates scheme rules against the user profile.
- **LLM:** understands language and generates/explains responses.
- **PostgreSQL:** stores structured application and user data.

### 3.3 MCQ Mode is Optional

The chatbot should not force users into an MCQ questionnaire.

Default interaction:

> User types naturally → Agent understands → Agent asks follow-up questions when needed.

Optional interaction:

> User chooses MCQ mode → Agent asks relevant questions using predefined options.

MCQ mode is therefore an **interaction method**, not a separate agent.

### 3.4 Language Independence

The system should separate language/presentation from internal processing.

For example:

- English: `Unemployed`
- Hindi: `बेरोज़गार`
- Marathi: `बेरोजगार`

All should map internally to a common structured value such as:

```text
employment_status = "unemployed"
```

This keeps the RAG and eligibility engine language-independent.

---

## 4. Target Users

The primary users are citizens who want to discover and understand government schemes without having to manually search through multiple sources.

The interface should be simple enough for users who may not be technically experienced.

The initial supported website languages are:

- English
- Hindi
- Marathi

The architecture should remain extensible to additional Indian languages.

---

## 5. Main User Flow

The intended high-level flow is:

```text
User
  ↓
Select Website Language
  ↓
Enter Requirement / Start Chat
  ↓
AI Orchestrator
  ↓
Understand Intent + Extract Known Profile Information
  ↓
Is More Information Required?
  ├── YES
  │    ↓
  │  Does User Want MCQ Mode?
  │    ├── YES → Ask MCQ → Update Profile
  │    └── NO  → Ask Normal Text Question → Update Profile
  │
  │  Repeat until enough information is available
  │
  └── NO
       ↓
    Hybrid RAG
       ↓
    Metadata Filtering
       ↓
    Vector Search + BM25
       ↓
    Reranking
       ↓
    Candidate Schemes
       ↓
    Eligibility Engine
       ↓
    Explainable Recommendations
       ↓
    Final Response in Selected Language
```

---

## 6. Agentic Workflow

The orchestrator should operate using state and conditional routing.

A simplified workflow is:

```text
START
  ↓
Understand User Request
  ↓
Extract / Update Profile
  ↓
Check Required Information
  ↓
Enough Information?
  ├── NO → Ask User
  │          ↓
  │      User Responds
  │          ↓
  │      Update State/Profile
  │          ↓
  │      Check Again
  │
  └── YES
       ↓
    Retrieve Schemes
       ↓
    Rerank Results
       ↓
    Check Eligibility
       ↓
    Generate/Explain Result
       ↓
    END
```

LangGraph is recommended for implementing this workflow because it supports state, conditional branching and loops.

---

## 7. Hybrid RAG Strategy

### Selected RAG Type

**Hybrid RAG** will be used.

It combines:

- Semantic/vector retrieval
- Keyword retrieval using BM25
- Metadata filtering
- Reranking

### Why Hybrid RAG?

Government scheme information contains both natural-language descriptions and strict terms such as:

- Scheme names
- State names
- Occupations
- Income limits
- Age limits
- Beneficiary categories
- Document names
- Specific eligibility phrases

Vector search helps understand the meaning of natural-language queries.

BM25 helps match important exact terms.

Metadata filtering can narrow the search using structured information such as state or scheme category.

Reranking can then prioritize the most relevant retrieved schemes.

### Retrieval Pipeline

```text
User Query + User Profile
          ↓
Metadata Filtering
          ↓
 ┌────────┴─────────┐
 ↓                  ↓
Vector Search      BM25
 ↓                  ↓
 └────────┬─────────┘
          ↓
       Combine
          ↓
       Rerank
          ↓
 Relevant Schemes
```

---

## 8. Knowledge Base

The knowledge base will contain government scheme information collected from reliable/official sources.

Important fields include:

- Scheme name
- Scheme description
- Government department
- Central/State classification
- State
- Target beneficiaries
- Benefits
- Eligibility criteria
- Age requirements
- Income requirements
- Occupation requirements
- Education requirements where relevant
- Required documents
- Application procedure
- Official application URL
- Official source
- Last updated information

The data should be cleaned and divided into meaningful semantic/section-based chunks.

Metadata should be attached to chunks to improve retrieval.

---

## 9. Eligibility Engine

Eligibility checking should be handled primarily through a **Python-based rule engine**, rather than asking the LLM to make the final eligibility decision.

Example:

```text
Scheme Rules:
Age >= 18
Income <= ₹5,00,000
State = Maharashtra
Occupation = Farmer

User:
Age = 21
Income = ₹3,00,000
State = Maharashtra
Occupation = Farmer

Result:
Eligible
```

The engine should be able to distinguish between:

- Eligible
- Not eligible
- Information missing / cannot determine yet

The LLM can explain the result, but the rule engine should perform the actual structured comparison wherever possible.

---

## 10. Explainable Recommendations

The system should not simply return a list of scheme names.

For each recommended scheme, it should explain:

- Why the scheme is relevant
- Eligibility conditions
- Which user conditions match
- Which conditions are missing or unmet
- Benefits
- Required documents
- Application procedure
- Official source/application link

The response should be grounded in retrieved scheme information.

---

## 11. Multilingual Design

The entire website should change according to the selected language.

The language switch should affect:

- Navigation
- Buttons
- Labels
- Profile fields
- Chatbot interface
- MCQ questions
- MCQ options
- Scheme information
- Eligibility explanations
- Document checklist
- Application instructions
- Error/help messages

Initial languages:

```text
English
Hindi
Marathi
```

The system should be designed for future expansion to more Indian languages.

The backend should use language-neutral structured values rather than storing separate logical values for every language.

---

## 12. Recommended Technology Stack

### Frontend

- React
- Vite
- Tailwind CSS
- i18n library for multilingual UI

### Backend

- Python
- FastAPI

### Agent Workflow

- LangGraph

### RAG

- LangChain
- Qdrant for vector search
- BM25 for keyword retrieval
- BGE Reranker or another suitable reranking model

### LLM

- Gemini API or OpenAI API

The final provider should be selected based on API availability, cost, performance, multilingual capability and project constraints.

### Database

- PostgreSQL

PostgreSQL is intended for structured application data such as user profiles, conversations, metadata and application state.

Qdrant is intended for vector retrieval rather than replacing PostgreSQL.

### Embeddings

A multilingual embedding model suitable for English, Hindi and Marathi.

### Document Processing - Advanced Feature

- PyMuPDF for PDF extraction
- OCR for scanned/image documents

### Development and Collaboration

- Git
- GitHub
- Antigravity / VS Code

---

## 13. Suggested System Architecture

```text
┌─────────────────────────────────────────────┐
│              React + Vite Web App           │
│                                             │
│ Language Toggle | Chat | Optional MCQ       │
│ Profile | Scheme Results | Comparison       │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│                 FastAPI                     │
│                  Backend                    │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│           LangGraph Orchestrator            │
│                                             │
│ Intent | Profile | Missing Info | Routing   │
└─────────────┬───────────┬──────────┬────────┘
              │           │          │
              ↓           ↓          ↓
       Profile/Query   Question   Hybrid RAG
         Processing      Tool       Pipeline
                                      │
                              ┌───────┴────────┐
                              ↓                ↓
                           Vector             BM25
                           Search             Search
                              └───────┬────────┘
                                      ↓
                                  Reranker
                                      ↓
                              Candidate Schemes
                                      ↓
                              Eligibility Engine
                                      ↓
                              Explainable Result
                                      ↓
                              LLM Response Layer
                                      ↓
                           Selected User Language

                  ┌───────────────────────────┐
                  │        PostgreSQL         │
                  │ Profiles | Conversations  │
                  │ Metadata | Application     │
                  │ State                     │
                  └───────────────────────────┘
```

---

## 14. What Makes the System Agentic?

The project should not claim to be agentic merely because it uses LangGraph or an LLM.

The agentic behavior comes from the orchestrator's ability to make workflow decisions.

Examples:

### Case 1: Missing Information

```text
User asks for a scheme
        ↓
Agent checks profile
        ↓
Required information missing
        ↓
Agent asks for it
```

### Case 2: Optional MCQ Mode

```text
Information missing
        ↓
Agent checks interaction preference
        ↓
MCQ selected
        ↓
Ask MCQ
```

### Case 3: Enough Information

```text
Profile sufficient
        ↓
Agent triggers Hybrid RAG
```

### Case 4: Eligibility

```text
Relevant schemes found
        ↓
Agent sends candidates
to Eligibility Engine
```

### Case 5: More Evidence Required

```text
Eligibility cannot be determined
        ↓
Agent requests the missing information
        ↓
Update profile
        ↓
Continue workflow
```

Therefore:

> **The agent decides what action should happen next, while the individual tools perform specialized tasks.**

---

## 15. Advanced Features

The following features are considered extensions and should not block the basic MVP:

1. Scheme comparison
2. Document requirement detection
3. Document upload
4. OCR/document extraction
5. Certificate information extraction
6. Verification through an available official verification mechanism
7. Additional Indian languages
8. Automatic knowledge-base updates
9. Personalized scheme dashboard
10. Saved user profile
11. Notifications/reminders
12. WhatsApp interface using the same backend

### Important scope decision

Voice interaction is **not part of the core project**.

The project will remain text-based with optional MCQ interaction.

WhatsApp is also **not the primary interface**. The dedicated web application is the primary product. A WhatsApp interface can be considered later as an additional client for the same backend.

---

## 16. Document Verification Scope

If implemented, document verification should not claim that an AI model can independently determine whether a government certificate is genuine.

A safer architecture is:

```text
User uploads document
        ↓
Extract text/data
        ↓
Read:
Name
Certificate Number
Income
Date
Authority
        ↓
Use official verification mechanism
where available
        ↓
Compare extracted information
        ↓
Verified / Mismatch / Unable to Verify
```

This is an advanced feature and should only be implemented where a reliable official verification mechanism is actually available.

---

## 17. MVP Scope

The first working version should focus on:

1. React/Vite multilingual website
2. English + Hindi + Marathi
3. User profile
4. Text-based chatbot
5. Optional MCQ mode
6. Single orchestrator agent
7. LangGraph workflow
8. Hybrid RAG
9. Metadata filtering
10. Reranking
11. Eligibility rule engine
12. Explainable recommendations
13. Official source links
14. PostgreSQL for structured data
15. Qdrant for vector retrieval

The advanced document verification workflow should come after the core recommendation system works reliably.

---

## 18. Evaluation

The system should be evaluated using:

### Retrieval

- Precision@K
- Recall@K
- MRR

### Response

- Relevance
- Faithfulness
- Context relevance
- Hallucination rate

### Eligibility

- Eligibility accuracy
- Correct handling of missing information
- Correct handling of conflicting conditions

### System

- Response latency
- Multilingual response quality
- User interaction success rate

---

## 19. Important Constraints

The system should:

- Prefer official/verified government sources.
- Avoid inventing eligibility criteria.
- Avoid inventing benefits.
- Avoid inventing documents.
- Avoid inventing deadlines.
- Avoid inventing application URLs.
- Clearly indicate when information is missing or cannot be verified.
- Use retrieved evidence when generating scheme-specific answers.
- Keep eligibility logic as deterministic as possible.
- Avoid forcing MCQ mode on users.
- Keep voice interaction outside the core scope.
- Keep WhatsApp outside the core MVP.

---

## 20. Key Project Statement

The project can be summarized as:

> **A multilingual, profile-aware government scheme assistance platform in which a single AI orchestrator dynamically controls user interaction, information gathering, Hybrid RAG retrieval and eligibility checking to provide explainable, source-grounded scheme recommendations.**

### Core distinction

```text
Agent       → Decides what to do next
RAG         → Retrieves relevant scheme information
Reranker    → Prioritizes retrieved information
Eligibility → Checks scheme rules against the profile
LLM         → Understands and communicates information
PostgreSQL  → Stores structured application data
React       → Provides the user interface
```
