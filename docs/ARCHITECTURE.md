# Architecture Diagram - Akhila AI Pipeline

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Web UI     │  │  cURL/CLI    │  │  External    │             │
│  │ (Browser)    │  │              │  │  Apps        │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                 │                  │                      │
│         └─────────────────┼──────────────────┘                      │
│                           │                                         │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                         API LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Application                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │ /ingest  │ │/documents│ │ /search  │ │ /stats   │       │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │   │
│  │       │            │            │            │              │   │
│  └───────┼────────────┼────────────┼────────────┼──────────────┘   │
│          │            │            │            │                  │
└──────────┼────────────┼────────────┼────────────┼──────────────────┘
           │            │            │            │
           │            │            │            │
┌──────────▼────────────▼────────────▼────────────▼──────────────────┐
│                    BUSINESS LOGIC LAYER                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Pipeline Orchestrator                     │   │
│  │  • Validation                                                │   │
│  │  • Orchestration                                             │   │
│  │  • Error Handling                                            │   │
│  └────────┬──────────────────────────────────────┬──────────────┘   │
│           │                                      │                  │
│           │                                      │                  │
│  ┌────────▼──────────┐              ┌───────────▼──────────┐       │
│  │   AI Analyzer     │              │   Database Manager   │       │
│  │  • Multi-provider │              │   • CRUD Operations  │       │
│  │  • Prompt Eng.    │              │   • Transactions     │       │
│  │  • Fallback       │              │   • Queries          │       │
│  └────────┬──────────┘              └───────────┬──────────┘       │
│           │                                      │                  │
└───────────┼──────────────────────────────────────┼──────────────────┘
            │                                      │
            │                                      │
┌───────────▼──────────────────┐      ┌───────────▼──────────────────┐
│    EXTERNAL AI SERVICES      │      │      DATA STORAGE            │
│  ┌────────────────────────┐  │      │  ┌────────────────────────┐  │
│  │  OpenAI (GPT-4o-mini)  │  │      │  │   SQLite Database      │  │
│  │  • Sentiment Analysis  │  │      │  │  ┌──────────────────┐  │  │
│  │  • Entity Extraction   │  │      │  │  │   documents      │  │  │
│  │  • Topic Detection     │  │      │  │  │   analyses       │  │  │
│  │  • Summarization       │  │      │  │  │   entities       │  │  │
│  └────────────────────────┘  │      │  │  └──────────────────┘  │  │
│                               │      │  └────────────────────────┘  │
│  ┌────────────────────────┐  │      │                              │
│  │ Anthropic (Claude)     │  │      │  File: data/pipeline.db      │
│  │  (Alternative)         │  │      │  Mode: WAL                   │
│  └────────────────────────┘  │      │  Indexes: sentiment, entity  │
│                               │      │                              │
│  ┌────────────────────────┐  │      └──────────────────────────────┘
│  │ Ollama (Local)         │  │
│  │  (Fallback)            │  │
│  └────────────────────────┘  │
│                               │
└───────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│   Input     │  Text document from user/API
│   Text      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  1. INGESTION                           │
│  • Receive text via API                 │
│  • Validate (length, encoding)          │
│  • Extract metadata (word count, etc.)  │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  2. STORAGE (Initial)                   │
│  • Insert into documents table          │
│  • Generate document_id                 │
│  • Store timestamp                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  3. AI ANALYSIS                         │
│  • Build structured prompt              │
│  • Call AI provider API                 │
│  • Parse JSON response                  │
│  • Extract: sentiment, entities,        │
│    topics, summary                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  4. STORAGE (Analysis Results)          │
│  • Insert into analyses table           │
│  • Insert entities into entities table  │
│  • Link via document_id                 │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  5. RESPONSE                            │
│  • Return document_id                   │
│  • Include analysis results             │
│  • Status: success/error                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │  Receives processed result
│  Response   │
└─────────────┘
```

## Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                      API Request Flow                        │
└──────────────────────────────────────────────────────────────┘

POST /ingest
    │
    ├─► api.py: ingest_document()
    │       │
    │       └─► pipeline.py: ingest()
    │               │
    │               ├─► Validate input
    │               │
    │               ├─► database.py: insert_document()
    │               │       │
    │               │       └─► SQLite: INSERT INTO documents
    │               │
    │               ├─► ai_analyzer.py: analyze()
    │               │       │
    │               │       ├─► Build prompt
    │               │       │
    │               │       ├─► Call AI API (OpenAI/Anthropic/Ollama)
    │               │       │
    │               │       └─► Parse JSON response
    │               │
    │               ├─► database.py: insert_analysis()
    │               │       │
    │               │       └─► SQLite: INSERT INTO analyses
    │               │
    │               └─► database.py: insert_entities()
    │                       │
    │                       └─► SQLite: INSERT INTO entities
    │
    └─► Return JSON response to client


GET /documents/{id}
    │
    ├─► api.py: get_document()
    │       │
    │       └─► pipeline.py: retrieve()
    │               │
    │               └─► database.py: get_document()
    │                       │
    │                       ├─► SQLite: SELECT FROM documents
    │                       ├─► SQLite: SELECT FROM analyses
    │                       └─► SQLite: SELECT FROM entities
    │
    └─► Return combined JSON response
```

## Database Schema

```
┌─────────────────────────────────────────┐
│           documents                     │
├─────────────────────────────────────────┤
│ id (PK)          INTEGER                │
│ content          TEXT                   │
│ source           VARCHAR(255)           │
│ ingested_at      TIMESTAMP              │
│ word_count       INTEGER                │
│ char_count       INTEGER                │
└──────────┬──────────────────────────────┘
           │
           │ 1:1
           │
┌──────────▼──────────────────────────────┐
│           analyses                      │
├─────────────────────────────────────────┤
│ id (PK)              INTEGER            │
│ document_id (FK)     INTEGER            │
│ sentiment            VARCHAR(20)        │
│ sentiment_confidence REAL               │
│ summary              TEXT               │
│ topics               TEXT (JSON)        │
│ analyzed_at          TIMESTAMP          │
│ ai_model             VARCHAR(50)        │
└─────────────────────────────────────────┘

┌──────────┬──────────────────────────────┐
│          │ 1:N                          │
│          │                              │
┌──────────▼──────────────────────────────┐
│           entities                      │
├─────────────────────────────────────────┤
│ id (PK)          INTEGER                │
│ document_id (FK) INTEGER                │
│ entity_text      VARCHAR(255)           │
│ entity_type      VARCHAR(50)            │
└─────────────────────────────────────────┘

Indexes:
• idx_sentiment ON analyses(sentiment)
• idx_entity_type ON entities(entity_type)
• idx_ingested_at ON documents(ingested_at)
```

## Deployment Architecture (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
└────────┬────────────────────────────────────┬───────────────┘
         │                                    │
    ┌────▼────┐                          ┌────▼────┐
    │  API    │                          │  API    │
    │ Server  │                          │ Server  │
    │  (1)    │                          │  (2)    │
    └────┬────┘                          └────┬────┘
         │                                    │
         └────────────┬───────────────────────┘
                      │
              ┌───────▼────────┐
              │   PostgreSQL   │
              │   (Primary)    │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │   PostgreSQL   │
              │   (Replica)    │
              └────────────────┘

         ┌────────────────────┐
         │   Redis Cache      │
         │  (Analysis Cache)  │
         └────────────────────┘

         ┌────────────────────┐
         │   Message Queue    │
         │  (Async Process)   │
         └────────────────────┘
```


**Document Version:** 1.0  
**Last Updated:** February 20, 2026
