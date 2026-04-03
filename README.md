# 🚀 Knowledge Transfer Platform (KTP) 

### **Enterprise-Grade AI Knowledge Management & Discovery**

KTP is a high-performance **Retrieval-Augmented Generation (RAG)** platform designed for organizations to centralize, search, and synthesize disparate knowledge. It transforms static documents (PDFs, PPTXs, CSVs, etc.) into a live, interactive "Neural Library" that answers complex technical questions with maximum depth and precision.

---

## 🏛️ System Architecture

KTP is built on a modern, asynchronous stack designed for low-latency AI inference and robust data integrity:

*   **Frontend**: Next.js 15 (App Router) + Tailwind CSS + Framer Motion. 
*   **Backend**: FastAPI (Python 3.13) with native `AsyncGroq` integration.
*   **Vector Engine**: Supabase (PostgreSQL) + `pgvector` for high-dimensional similarity search.
*   **AI Synthesis**: Groq Llama 3.1 8B (providing 10x higher rate limits and speed than 70B models).

---

## 🧠 Core Features

### 1. **Dynamic Ingestion Matrix (V2.0)**
*   **Multi-Format Support**: Native extraction for PDF, DOCX, XLSX, CSV, MD, and more.
*   **Auto-Chunking**: Splits documents into ~1000 character segments with overlap to maintain context.
*   **Live Status Monitoring**: Track every document from staging to full vector indexing in real-time.

### 2. **Intelligent Semantic Search**
*   **Beyond Keywords**: Uses deep-learning embeddings (`BAAI/bge-small-en-v1.5`) to understand *meaning*, not just words.
*   **Smart Context Window**: Automatically expands search breadth (Top-K) for "Global Summary" requests (Summarize everything).
*   **Expert Synthesis**: Answers questions with multi-paragraph technical detail, tables, and categorized file breakdowns.

### 3. **Shared Workspace & Active Bridges**
*   **Collaborative Library**: A "Shared Workspace" model where team members can jointly manage and clean up the knowledge base.
*   **Universal Deletion**: Any authenticated user can help "prune" the matrix, with automatic cleanup of AI chunks (CASCADE).
*   **Active Bridges**: Seamless connectivity logs for external platforms like GitHub and Notion.

---

## 🛠️ Technical Implementation

### **The RAG Pipeline**
1.  **Ingestion**: `IngestionService` extracts text and generates high-dimensional vectors.
2.  **Storage**: Vectors are stored in Supabase with metadata (filename, owner, privacy status).
3.  **Retrieval**: `SearchEngine` executes a Postgres RPC (`match_chunks`) to find the most relevant context.
4.  **Synthesis**: `AIGenerator` constructs a "Strict Answer Mode" prompt to generate precise documentation reviews.

### **Role-Based Access (Shared-First)**
*   **Profiles**: Every user has an auto-generated profile (`admin`, `manager`, `employee`).
*   **Visibility**: "Private" documents stay visible only to creator/admins; "Public" documents are available to the entire team.

---

## 🏁 Getting Started

### **Environment Setup**
Create a `.env` file in the root with the following variables:

```env
# Supabase
SUPABASE_URL=your_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
DATABASE_URL=postgresql://postgres:[password]@db...

# AI Services
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Embeddings
HUGGINGFACE_API_KEY=hf_...
```

### **Deployment**
*   **Frontend**: Deploy to **Vercel** (connect the repo and add variables).
*   **Backend**: Deploy to **Render** (use the Python 3.13 runtime).

---

## 📂 Key Links
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)**: Full step-by-step setup walkthrough.
- **[Database Logic](./frontend/api/backend/supabase/SUPABASE_SETUP.sql)**: Core schema and PGVector functions.
- **[Backend Config](./frontend/api/backend/config.py)**: Centralized configuration and validation.

---

© 2026 Knowledge Transfer Platform | **Optimized for High-Speed Discovery**