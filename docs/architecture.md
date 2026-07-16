# Architecture

Feedback Finder AI is split into domain-neutral platform services and domain-specific packs.

## Platform Core

- Source connectors collect permitted public feedback and normalize payloads.
- Ingestion cleans text, masks personal information, removes duplicates, and validates records.
- AI analysis detects company, product, sentiment, emotion, topics, root causes, and priority signals.
- Analytics aggregates sentiment, topic distribution, priority queues, and competitor comparison.
- Search and retrieval locate supporting evidence for grounded stories and Q&A.
- Vector storage embeds analyzed feedback for semantic retrieval across social, review, complaint, and community sources.
- Notifications turn priority signals into analyst-facing alerts.
- The web dashboard reads API contracts rather than reaching directly into services.

## Domain Packs

Domain packs live under `domain-packs/{domain}/domain.json` and define companies, products, complaint categories, journey stages, priority rules, and vocabulary. Telecom is implemented first, with insurance and e-commerce starter packs included to prove the separation.

## First Sprint Boundary

The current implementation uses:

- In-memory storage.
- Seeded sample public-feedback connector.
- Mock-mode social/community connectors for LinkedIn, Facebook, Instagram, X, Truth Social, Reddit, and telecom community forums.
- Local deterministic vector storage under `data/vector_store.json`.
- Heuristic AI classifiers.
- Static dashboard served by FastAPI.

Production iterations should add PostgreSQL, Redis-backed workers, OpenSearch, vector storage, Ollama/Hugging Face model integrations, connector credentials, RAG grounding, user auth, and alert workflow persistence.
