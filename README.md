# Ask My PDF 📄
### RAG-Powered Document Intelligence Assistant

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?style=flat&logo=amazonaws&logoColor=white)](https://aws.amazon.com/ec2)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_DB-00599C?style=flat&logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat&logo=chainlink&logoColor=white)](https://langchain.com)
[![Mistral](https://img.shields.io/badge/Mistral_AI-API-FF7000?style=flat&logo=mistral&logoColor=white)](https://mistral.ai)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-BGE_Embeddings-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co)
[![Live](https://img.shields.io/badge/Live-Demo-22c55e?style=flat&logo=googlechrome&logoColor=white)](https://ask-my-pdf.duckdns.org)

A production-grade Retrieval-Augmented Generation (RAG) system that lets you have natural language conversations with your PDF documents. Built with a FastAPI backend, React frontend, and deployed on AWS EC2 with Docker, Nginx, and HTTPS via Let's Encrypt.

**Live Demo:** https://ask-my-pdf.duckdns.org

---

## Features

- **Hybrid Retrieval** — Combines FAISS semantic search with BM25 keyword search using Reciprocal Rank Fusion (RRF) for superior retrieval accuracy
- **Source Citations** — Every answer includes the exact document name and page number it was sourced from
- **Multi-Document Support** — Upload and query across multiple PDFs simultaneously
- **Conversational Memory** — Maintains context across multiple turns in a session
- **Dual LLM Backend** — Supports Mistral API (cloud) and Ollama (fully offline) via a single config flag
- **ChatGPT-style UI** — Dark themed React frontend with drag-and-drop PDF upload
- **Anti-Hallucination** — LLM is strictly instructed to answer only from retrieved context
- **Production Deployment** — Dockerized on AWS EC2 with Elastic IP, Nginx reverse proxy, and SSL/HTTPS

---

## Architecture

```
User Browser (React)
        ↓
   Nginx (port 443 — HTTPS / Let's Encrypt SSL)
   HTTP → HTTPS redirect on port 80
        ↓
 ┌──────────────────────────────────┐
 │         FastAPI Backend          │
 │                                  │
 │  PDF Upload → PyMuPDF Extractor  │
 │       ↓                          │
 │  RecursiveCharacterTextSplitter  │
 │       ↓                          │
 │  BGE Embeddings (BAAI/bge-small) │
 │       ↓                          │
 │  FAISS Vector Store + BM25       │
 │       ↓                          │
 │  Hybrid RRF Retrieval            │
 │       ↓                          │
 │  Mistral API / Ollama LLM        │
 │       ↓                          │
 │  Answer + Source Citations       │
 └──────────────────────────────────┘
        ↓
   Docker Compose
        ↓
   AWS EC2 t3.micro (Elastic IP)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Axios, react-dropzone, react-markdown |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| PDF Parsing | PyMuPDF (fitz) |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | BAAI/bge-small-en-v1.5 (Sentence Transformers) |
| Vector Store | FAISS (CPU) |
| Keyword Search | BM25 (rank-bm25) |
| LLM (Cloud) | Mistral API (mistral-small-latest) |
| LLM (Offline) | Ollama (Mistral 7B) |
| Serving | Nginx reverse proxy + SSL termination |
| TLS | Let's Encrypt via Certbot |
| Containerization | Docker + Docker Compose |
| Deployment | AWS EC2 t3.micro + Elastic IP |

---

## RAG Pipeline

### 1. Ingestion
```
PDF → PyMuPDF → Page text + page numbers → RecursiveCharacterTextSplitter
→ Chunks (500 tokens, 50 overlap) → BGE embeddings → FAISS index + BM25 index
```

### 2. Retrieval (Hybrid)
```
User query → BGE embed → FAISS top-K (semantic)
                       → BM25 top-K (keyword)
                       → Reciprocal Rank Fusion → Fused top-5 chunks
```

### 3. Generation
```
Fused chunks + conversation history → Mistral LLM → Answer + citations
```

---

## Project Structure

```
ask-my-pdf/
├── api/
│   ├── main.py              # FastAPI routes (/ingest, /query, /health)
│   └── schemas.py           # Pydantic request/response models
├── app/
│   ├── ingestion/
│   │   ├── extractor.py     # PyMuPDF text extraction
│   │   └── chunker.py       # RecursiveCharacterTextSplitter
│   ├── embeddings/
│   │   └── embedder.py      # BGE embedding wrapper
│   ├── vectorstore/
│   │   └── faiss_store.py   # FAISS build, save, load, search
│   ├── retrieval/
│   │   ├── semantic.py      # FAISS semantic retrieval
│   │   └── hybrid.py        # BM25 + FAISS fusion (RRF)
│   ├── llm/
│   │   ├── mistral_client.py
│   │   └── ollama_client.py
│   ├── chain/
│   │   └── rag_chain.py     # LangChain chain + memory assembly
│   └── utils/
│       ├── config.py        # Centralized settings
│       └── logger.py        # Structured logging
├── frontend/                # React app
│   └── src/
│       ├── components/      # Chat UI components
│       ├── hooks/           # useChat state management
│       └── services/        # API client (api.js)
├── data/
│   ├── uploads/             # Temporary PDF storage
│   └── vectorstore/         # Persisted FAISS indexes
├── Dockerfile               # Backend container (CPU-only PyTorch)
├── docker-compose.yml
└── requirements.txt
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Mistral API key ([console.mistral.ai](https://console.mistral.ai))

### Backend

```bash
git clone https://github.com/Aishwarya-J05/ask-my-pdf.git
cd ask-my-pdf

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

Create `.env` file:
```env
LLM_BACKEND=mistral_api
MISTRAL_API_KEY=your_key_here
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
UPLOAD_DIR=data/uploads
VECTORSTORE_DIR=data/vectorstore
```

Run backend:
```bash
python -m uvicorn api.main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

App runs at `http://localhost:3000`, API at `http://localhost:8000`.

---

## Docker Deployment

```bash
# Set your API key
export MISTRAL_API_KEY=your_key_here

# Build and run
docker compose up -d --build

# Check status
docker ps
docker logs askpdf-backend
```

Frontend served at port 80, backend at port 8000.

---

## AWS EC2 Deployment (with HTTPS)

### 1. Launch Instance
- Instance type: `t3.micro` (Ubuntu 22.04)
- Assign an **Elastic IP** to avoid IP changes on restart
- Security group inbound rules: `22` (SSH), `80` (HTTP), `443` (HTTPS)
- Do **not** expose port 8000 publicly — backend traffic routes through Nginx

### 2. Install Dependencies

```bash
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP

sudo apt update && sudo apt install docker.io docker-compose nginx certbot python3-certbot-nginx -y
sudo usermod -aG docker ubuntu
newgrp docker
```

### 3. Deploy Application

```bash
git clone https://github.com/Aishwarya-J05/ask-my-pdf.git
cd ask-my-pdf
# Set MISTRAL_API_KEY in docker-compose.yml environment section
docker compose up -d --build
```

### 4. Configure Nginx

```bash
sudo tee /etc/nginx/sites-available/askpdf << 'EOF'
server {
    listen 80;
    server_name your-domain.duckdns.org;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/askpdf /etc/nginx/sites-enabled/askpdf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 5. Enable HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d your-domain.duckdns.org --non-interactive --agree-tos -m your@email.com
```

Certbot automatically updates the Nginx config and sets up auto-renewal. Certificate valid for 90 days, renewed automatically in the background.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service status, documents loaded, vector count |
| POST | `/ingest` | Upload PDFs, run full ingestion pipeline |
| POST | `/query` | Ask a question, returns answer + citations |
| DELETE | `/session/{id}` | Clear conversation memory for a session |

### Example Query

```bash
curl -X POST https://ask-my-pdf.duckdns.org/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?", "session_id": "abc123"}'
```

Response:
```json
{
  "answer": "The key findings include... [Source: report.pdf, Page 4]",
  "citations": ["report.pdf — Page 4", "report.pdf — Page 7"],
  "session_id": "abc123"
}
```

---

## LLM Backend Toggle

Switch between cloud and offline mode via a single environment variable:

```env
LLM_BACKEND=mistral_api   # Cloud (Mistral API)
LLM_BACKEND=ollama        # Fully offline (Mistral 7B via Ollama)
```

For offline mode, install [Ollama](https://ollama.ai) and run:
```bash
ollama pull mistral
ollama serve
```

---

## Key Design Decisions

**Why Hybrid Retrieval (BM25 + FAISS)?**
Semantic search alone misses exact keyword matches — critical for legal/technical documents where precise terminology matters. BM25 catches exact matches while FAISS handles conceptual similarity. RRF fuses both ranked lists without score normalization issues.

**Why BGE over all-MiniLM?**
BAAI/bge-small-en-v1.5 is specifically trained for retrieval tasks (asymmetric search) and consistently ranks top on the MTEB retrieval benchmark. The query prefix technique further improves retrieval quality.

**Why FAISS over a managed vector DB?**
Zero infrastructure cost, no external service dependency, and sufficient performance for document-scale workloads. Index persists to disk — no re-embedding on restart.

---

## Use Cases

- **Legal** — Contract analysis, case law research, policy Q&A
- **Healthcare** — Clinical guidelines, patient record querying
- **Education** — Research paper Q&A, textbook assistant
- **Enterprise** — Internal documentation, HR policy assistant
- **Finance** — Annual report analysis, regulatory documents

---

## Roadmap

- [ ] Re-ranking with cross-encoders (BGE-reranker)
- [ ] HyDE (Hypothetical Document Embeddings) for improved retrieval
- [ ] Async document processing with Celery + Redis
- [ ] Support for Word documents (.docx)
- [ ] S3 integration for document storage

---

## Author

**Aishwarya Joshi**
AI/ML Engineer | BE in Electronics and Communication Engineering

- GitHub: [@Aishwarya-J05](https://github.com/Aishwarya-J05)
- LinkedIn: [aishwaryajoshiaiml](https://linkedin.com/in/aishwaryajoshiaiml)
- HuggingFace: [AishwaryaNJ](https://huggingface.co/AishwaryaNJ)
- Medium: [@aishwaryajoshi554](https://medium.com/@aishwaryajoshi554)

---

## License

MIT License — free to use and modify.
