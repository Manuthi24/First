# Customer Support Copilot (E-commerce FAQ Chatbot)

Great choice — yes, we should do **Customer Support Copilot**.
This repository now includes a working implementation you can run locally and deploy with Docker.

## What this project demonstrates (CV/LinkedIn value)

- Production-style API using **FastAPI**
- Chat UI using **Streamlit**
- FAQ retrieval with confidence scoring and fallback policy
- Source citations in chatbot responses
- Unit/API tests with `pytest`
- Deployment-ready setup with **Docker Compose**

## Architecture

1. **Frontend (`frontend/app.py`)**
   - Streamlit chat interface
   - Sends user questions to backend API

2. **Backend (`backend/main.py`)**
   - `/chat` endpoint for support Q&A
   - `/health` endpoint for health checks
   - `/admin/reload` endpoint to reload FAQ data
   - Retrieval engine based on cosine similarity over tokenized FAQ questions

3. **Knowledge Base (`data/faqs.json`)**
   - Structured FAQ documents (shipping, returns, payments, orders)

4. **Testing (`tests/test_api.py`)**
   - Health check test
   - Known-question success case
   - Unknown-question fallback case

## Quick Start (Local)

### 1) Create environment and install deps

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Run frontend (new terminal)

```bash
API_BASE_URL=http://localhost:8000 streamlit run frontend/app.py
```

Open:
- API docs: `http://localhost:8000/docs`
- Chat app: `http://localhost:8501`

## Run Tests

```bash
pytest -q
```

## Deployment (Docker Compose)

```bash
docker compose up --build
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

## API Examples

### Health

```bash
curl http://localhost:8000/health
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"How can I track my order?","top_k":3}'
```

### Reload FAQ index

```bash
curl -X POST http://localhost:8000/admin/reload
```

## How to make this truly industry-level (next upgrades)

1. Replace lexical retrieval with embedding-based vector search (FAISS/Chroma/Pinecone)
2. Add LLM generation layer for better natural responses
3. Add authentication + role-based admin controls
4. Add observability (latency, token/cost, trace IDs)
5. Add CI/CD pipeline for tests + container image publishing
6. Add evaluation dataset + automated quality metrics (precision@k, groundedness)

## Resume bullet ideas

- Built and deployed a **Customer Support Copilot** with FastAPI + Streamlit, including confidence-aware fallback and source citations.
- Designed and tested a retrieval engine for e-commerce FAQs, improving response consistency and reducing repetitive support queries.
- Containerized multi-service chatbot app with Docker Compose and API health/testing workflows.
