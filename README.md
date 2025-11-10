# 🧠 RAG Pipeline — FastAPI + Azure OpenAI + Azure Search + Azure Blob Storage

This project implements a Retrieval-Augmented Generation (RAG) pipeline where users can **upload documents**, which are stored in **Azure Blob Storage**, indexed in **Azure Cognitive Search**, and queried using **Azure OpenAI** models through a **FastAPI** interface.

---

## 🚀 Features
- 📤 Upload documents via API (PDF/Text)
- 💾 Store files in Azure Blob Storage
- 🔍 Create and query Azure Cognitive Search index
- 🧠 Use Azure OpenAI for embeddings & GPT responses
- ⚙️ Built with FastAPI, easily deployable to Azure App Service or Docker

---

## 🧱 Architecture
User → FastAPI → Azure Blob → Azure Cognitive Search → Azure OpenAI

- `/upload` → Uploads file → Extracts text → Generates embeddings → Indexes to Azure Search  
- `/query` → Embeds question → Performs vector search → Uses GPT to generate contextual answer

---

## ⚙️ Environment Variables (`.env`)
```bash
AZURE_STORAGE_CONNECTION_STRING=your_storage_conn_string
AZURE_BLOB_CONTAINER=documents

AZURE_SEARCH_ENDPOINT=https://<your-search>.search.windows.net
AZURE_SEARCH_KEY=<your-search-key>
AZURE_SEARCH_INDEX=documents-index

AZURE_OPENAI_ENDPOINT=https://<your-openai>.openai.azure.com
AZURE_OPENAI_KEY=<your-openai-key>
AZURE_OPENAI_EMBED_MODEL=text-embedding-3-small
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini

HOST=0.0.0.0
PORT=8080

# 1. Clone repository
git clone https://github.com/<your-username>/rag-fastapi-azure.git
cd rag-fastapi-azure

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create Azure Search index
python scripts/create_index.py

# 5. Run API
uvicorn app.main:app --reload --port 8080
