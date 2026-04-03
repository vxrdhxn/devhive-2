# 🛰️ DevHive: Enterprise Knowledge Discovery & RAG Platform

### **The Neural Engine for High-Performance Knowledge Retrieval and Synthesis**

**DevHive** is an advanced **Retrieval-Augmented Generation (RAG)** platform designed to transform static data into a high-speed, interactive intelligence hub. Engineered for enterprise-scale knowledge management, it enables teams to centralize documentation across multiple formats and platforms, delivering precise, context-aware answers in seconds.

---

## 🏗️ Technical Architecture

DevHive uses a decoupled, high-concurrency architecture optimized for sub-second vector retrieval and AI inference:

*   **Frontend**: Next.js 15 (App Router) • TypeScript • Framer Motion (Premium UI/UX) • Recharts (Neural Analytics).
*   **Backend**: FastAPI (Python 3.13) • AnyIO (Asynchronous Concurrency) • Pydantic V2 (Validation).
*   **Vector Database**: Supabase (PostgreSQL) • `pgvector` • HNSW indexing for O(log n) similarity search.
*   **AI Stack**: 
    *   **Embeddings**: `BAAI/bge-small-en-v1.5` via HuggingFace Inference API.
    *   **Inference**: Groq Llama 3.1 8B (providing 450+ tokens/sec for rapid synthesis).

---

## 🧠 Enterprise Features

### 1. **Neural Analytics Dashboard**
A mission-control center for administrators to monitor system performance:
*   **Query Velocity**: Real-time tracking of search patterns over a 30-day timeline.
*   **System Confidence**: Continuous monitoring of AI synthesis quality scores.
*   **Active Intelligence**: Tracking of top intent patterns and most-searched technical terms.

### 2. **Recursive Cloud Adapters**
Deep integration with version control and collaboration tools:
*   **Recursive GitHub Sync**: Full-tree indexing of repositories, including nested directories and documentation nodes.
*   **Bridge Management**: Centralized hub for managing external API connectors (Notion, Jira, GitHub).

### 3. **Smart Ingestion Pipeline (V2.1)**
A robust multi-stage pipeline for document processing:
*   **Content Deduplication**: Automatic similarity checks (0.95 threshold) to prevent redundant knowledge indexing.
*   **Global Format Support**: Native parsing for `PDF`, `DOCX`, `PPTX`, `XLSX`, `CSV`, `RTF`, `TXT`, and `MD`.
*   **Background Processing**: Heavy text extraction and embedding generation are offloaded to background threads to ensure zero-latency UI interaction.

### 4. **Granular RBAC System**
Secure, role-based access control protecting enterprise data:
*   **Admin**: Full system visibility, analytics access, and global document management.
*   **Manager**: Integration management and document synchronization rights.
*   **Employee**: Workspace access and private document management.

---

## 🛠️ Installation & Setup

### **1. Prerequisites**
*   Python 3.13+
*   Node.js 20+
*   Supabase Project (with PGVector enabled)

### **2. Environment Configuration**
Create a `.env` file in the root directory:

```env
# --- Supabase Configuration ---
NEXT_PUBLIC_SUPABASE_URL=your_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_URL=your_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# --- AI Intelligence ---
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_KEY=hf_...

# --- Platform Settings ---
NEXT_PUBLIC_BACKEND_URL=https://your-project.vercel.app/api
```

### **3. Backend Setup**
```powershell
pip install -r requirements.txt
python -m uvicorn frontend.api.index:app --reload --port 8000
```

### **4. Frontend Setup**
```powershell
npm install
npm run dev
```

---

## 🚀 Deployment Strategy

### **Frontend & Backend (Vercel)**
DevHive is optimized for the Vercel edge network. The entire application (Next.js frontend and FastAPI backend) can be deployed directly to Vercel for a seamless, unified experience.

---

## 📂 System Manifest
*   **[Core Logic](file:///c:/Users/Vardhan/OneDrive/Desktop/projects/Dev-Hive-main%20-%20Copy/frontend/api/backend/services/)**: Ingestion services, search engines, and AI generators.
*   **[Schema Definitions](file:///c:/Users/Vardhan/OneDrive/Desktop/projects/Dev-Hive-main%20-%20Copy/frontend/api/backend/supabase/schema.sql)**: Database migrations and RLS policies.
*   **[Analytics Module](file:///c:/Users/Vardhan/OneDrive/Desktop/projects/Dev-Hive-main%20-%20Copy/frontend/api/backend/routers/analytics.py)**: Backend metrics aggregation and processing.

---

© 2026 DevHive Enterprise | **Designed for High-Speed Knowledge Discovery**