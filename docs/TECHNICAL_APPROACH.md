# Technical Approach Document
## AI-Assisted Text Processing Pipeline

**Author:** Yagnesh Panchal  
**Date:** February 20, 2026  
**Challenge:** Akhila Labs Software Engineering Commander


## 1. Executive Summary

This document outlines a minimal, production-ready text processing pipeline that ingests documents, applies AI-driven analysis, and provides queryable insights. The system prioritizes clarity, maintainability, and responsible AI integration over feature completeness.

**Primary Data Type:** Text (documents, articles, user feedback)  
**Core Value:** Automated content analysis with sentiment detection, entity extraction, and summarization


## 2. System Architecture

### 2.1 Architecture Diagram

```
┌─────────────────┐
│   Data Source   │ (Simulated: files, API, manual input)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              INGESTION LAYER                        │
│  - File upload / API endpoint                       │
│  - Validation & sanitization                        │
│  - Metadata extraction (timestamp, source, size)    │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│            PROCESSING LAYER                         │
│  - Text normalization                               │
│  - Chunking (for large documents)                   │
│  - Pre-processing pipeline                          │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              AI ANALYSIS LAYER                      │
│  - Sentiment Analysis                               │
│  - Named Entity Recognition (NER)                   │
│  - Key Topic Extraction                             │
│  - Summary Generation                               │
│  Provider: OpenAI GPT-4 / Anthropic Claude          │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              STORAGE LAYER                          │
│  - SQLite database                                  │
│  - Schema: documents, analyses, entities            │
│  - Indexed for fast retrieval                       │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              API / QUERY LAYER                      │
│  - REST API (FastAPI)                               │
│  - Endpoints: ingest, query, retrieve, stats        │
│  - Simple web UI for visualization                  │
└─────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Ingest:** Text document arrives via API or file upload
2. **Validate:** Check format, size limits, encoding
3. **Process:** Clean text, extract metadata, chunk if needed
4. **Analyze:** Send to AI model for insights
5. **Store:** Save document + analysis results to database
6. **Retrieve:** Query via API with filters (date, sentiment, entities)


## 3. Technology Choices & Trade-offs

### 3.1 Core Stack

| Component | Technology | Rationale | Trade-off |
|-----------|-----------|-----------|-----------|
| **Language** | Python 3.11+ | Rich AI/ML ecosystem, rapid development | Not as performant as Go/Rust for high throughput |
| **API Framework** | FastAPI | Modern, async, auto-docs, type hints | Overkill for tiny projects, but scales well |
| **Database** | SQLite | Zero-config, portable, sufficient for prototype | Not suitable for high-concurrency production |
| **AI Provider** | OpenAI API (GPT-4o-mini) | Reliable, cost-effective, good quality | External dependency, API costs, latency |
| **Alternative AI** | Anthropic Claude | Better for long documents | Similar trade-offs |
| **Local Fallback** | Ollama (llama3) | No API costs, privacy | Requires local setup, slower, lower quality |

### 3.2 Why NOT Other Options

- **PostgreSQL/MySQL:** Over-engineering for prototype; SQLite sufficient
- **Microservices:** Unnecessary complexity for this scope
- **Kubernetes/Docker:** Not required for demo; can add later
- **React/Vue Frontend:** Time sink; simple HTML + htmx sufficient
- **Message Queues:** No async processing needed at this scale


## 4. AI Integration Strategy

### 4.1 AI in Development (Tools Used)

- **Code Generation:** GitHub Copilot / Claude for boilerplate
- **Debugging:** AI-assisted error analysis
- **Documentation:** AI-generated docstrings, refined manually
- **Architecture Review:** Discussed trade-offs with AI assistant

### 4.2 AI in Product (Analysis Pipeline)

**Prompt Engineering Approach:**
- Structured prompts with clear instructions
- JSON output format for parsing
- Temperature: 0.3 (deterministic, factual)
- Fallback handling for API failures

**Example Analysis Prompt:**
```
Analyze the following text and return JSON with:
1. sentiment: positive/negative/neutral (with confidence 0-1)
2. entities: list of people, organizations, locations
3. topics: 3-5 key topics/themes
4. summary: 2-sentence summary

Text: {document_text}
```

### 4.3 Responsible AI Practices

- **Cost Control:** Token limits, caching, rate limiting
- **Privacy:** No PII sent to external APIs without consent
- **Transparency:** Log all AI calls with timestamps
- **Fallback:** Graceful degradation if AI unavailable
- **Validation:** Human-reviewable outputs, confidence scores


## 5. Database Schema

```sql
-- Core document storage
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    source VARCHAR(255),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    char_count INTEGER
);

-- AI analysis results
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    sentiment VARCHAR(20),
    sentiment_confidence REAL,
    summary TEXT,
    topics TEXT, -- JSON array
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ai_model VARCHAR(50),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Extracted entities
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    entity_text VARCHAR(255),
    entity_type VARCHAR(50), -- PERSON, ORG, LOCATION, etc.
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE INDEX idx_sentiment ON analyses(sentiment);
CREATE INDEX idx_entity_type ON entities(entity_type);
CREATE INDEX idx_ingested_at ON documents(ingested_at);
```


## 6. API Endpoints

### 6.1 Core Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/ingest` | Submit document | `{text, source}` | `{document_id, status}` |
| GET | `/documents` | List all documents | Query params: limit, offset | `{documents: [...]}` |
| GET | `/documents/{id}` | Get document + analysis | - | `{document, analysis, entities}` |
| GET | `/search` | Query by filters | `sentiment, entity, date_range` | `{results: [...]}` |
| GET | `/stats` | Dashboard metrics | - | `{total_docs, sentiment_breakdown}` |
| GET | `/health` | System health check | - | `{status, db_ok, ai_ok}` |


## 7. Risk Assessment & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **AI API Downtime** | High | Medium | Retry logic, fallback to cached results, queue for later |
| **API Cost Overrun** | Medium | Medium | Token limits per request, rate limiting, monitoring |
| **Large Document Handling** | Medium | High | Chunk documents >4000 tokens, process in batches |
| **Database Corruption** | High | Low | Regular backups, write-ahead logging (WAL mode) |
| **Malicious Input** | Medium | Medium | Input sanitization, size limits, content filtering |
| **Slow AI Response** | Low | High | Async processing, timeout handling, user feedback |


## 8. Scope Boundaries

### ✅ In Scope
- Text ingestion via API
- AI-powered sentiment, entities, topics, summary
- SQLite storage with queryable schema
- REST API with 5-6 core endpoints
- Sample data and outputs
- Basic error handling

### ❌ Out of Scope (Explicitly Deferred)
- User authentication/authorization
- Real-time streaming processing
- Multi-language support
- Advanced NLP (custom models)
- Production deployment (Docker, CI/CD)
- Comprehensive test coverage (only critical paths)
- Polished UI (API-first, simple HTML demo)


## 9. Success Metrics

**For This Challenge:**
1. ✅ Pipeline runs end-to-end without errors
2. ✅ AI analysis produces meaningful, accurate results
3. ✅ API responds in <2 seconds for typical documents
4. ✅ Code is readable, modular, well-documented
5. ✅ Sample outputs demonstrate value clearly

**For Production (Future):**
- Throughput: 100+ documents/minute
- Accuracy: >85% sentiment classification
- Uptime: 99.5%
- Cost: <$0.01 per document analyzed


## 10. Development Timeline (Estimated)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Architecture & Design | 1 hour | This document |
| Database Setup | 30 min | Schema, migrations |
| Ingestion Layer | 1 hour | API endpoint, validation |
| AI Integration | 1.5 hours | Prompt engineering, parsing |
| Storage & Retrieval | 1 hour | CRUD operations |
| API Endpoints | 1 hour | FastAPI routes |
| Testing & Samples | 1 hour | Sample data, outputs |
| Documentation | 1 hour | README, usage guide |
| **Total** | **8 hours** | Working prototype |


## 11. AI Usage in This Challenge

### Tools Used
- **Claude/GPT-4:** Architecture brainstorming, code generation, documentation
- **GitHub Copilot:** Boilerplate code, function implementations
- **AI-Assisted Debugging:** Error analysis, optimization suggestions

### How AI Influenced Development
- **Faster Prototyping:** 40-50% time saved on boilerplate
- **Better Prompts:** Iterated on AI analysis prompts with AI assistance
- **Documentation Quality:** AI-generated first drafts, human-refined
- **Trade-off Analysis:** Discussed pros/cons of tech choices with AI

### What AI Couldn't Do
- **Architectural Decisions:** Required human judgment on scope, trade-offs
- **Domain Context:** Understanding Akhila Labs' IoT platform needs
- **Risk Assessment:** Business and operational risk evaluation
- **Final Review:** Code quality, security, maintainability checks


## 12. Conclusion

This design prioritizes **clarity over cleverness** and **completeness over perfection**. The architecture is intentionally simple, allowing for rapid iteration and easy understanding. Every technology choice has a clear rationale, and scope boundaries are explicitly defined.

The system demonstrates:
- Sound engineering judgment (right-sized solutions)
- Responsible AI integration (cost-aware, transparent, fallback-ready)
- Production thinking (error handling, monitoring, scalability path)
- Clear communication (documented decisions, trade-offs, risks)

**Next Steps:** Implement prototype following this blueprint, validate with sample data, iterate based on results.
