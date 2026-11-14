# 🛰️ DevHive: Enterprise Knowledge Discovery & RAG Platform

### **The Neural Engine for High-Performance Knowledge Retrieval and Synthesis**

**DevHive** is an advanced **Retrieval-Augmented Generation (RAG)** platform designed to transform static data into a high-speed, interactive intelligence hub. Engineered for enterprise-scale knowledge management, it enables teams to centralize documentation across multiple formats and platforms, delivering precise, context-aware answers in seconds.

---

## 🏗️ Technical Architecture

DevHive uses a decoupled, high-concurrency architecture optimized for sub-second vector retrieval and AI inference:

*   **App**: Next.js 16 (App Router + API routes, one Vercel project) • TypeScript • Framer Motion (Premium UI/UX) • Recharts (Neural Analytics).
*   **Auth**: Built-in email/password auth (bcrypt + JWT in an httpOnly cookie) with Admin / Manager / Employee roles.
*   **Vector Database**: Neon (PostgreSQL) • `pgvector` • HNSW indexing for O(log n) similarity search.
*   **AI Stack**: 
    *   **Embeddings**: `BAAI/bge-small-en-v1.5`, run inside the app with ONNX Runtime (no API key).
    *   **Inference**: Groq Llama 3.1 8B by default, or any OpenAI-compatible API.

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
*   **Live Status**: Each upload reports its stage (extracting, chunking, embedding, storing) in the processing matrix.
*   **Private Documents**: Uploads can be restricted to the uploader plus Managers/Admins.

### 4. **Granular RBAC System**
Secure, role-based access control protecting enterprise data:
*   **Admin**: Full system visibility, analytics access, and global document management.
*   **Manager**: Integration management and document synchronization rights.
*   **Employee**: Workspace access and private document management.

---

## 🛠️ Installation & Setup

### **1. Prerequisites**
*   Node.js 20+
*   A Neon project (Postgres with `pgvector`) — the repo is linked via `neon.ts`

### **2. Environment Configuration**
Pull the database URLs from Neon into the root `.env`, then copy them into `frontend/.env.local`:

```powershell
neon env pull
cd frontend
npm run env:sync
```

`frontend/.env.local` needs (see [`frontend/.env.example`](./frontend/.env.example)):

```env
DATABASE_URL=postgresql://...-pooler...neon.tech/neondb?sslmode=require
DATABASE_URL_UNPOOLED=postgresql://...neon.tech/neondb?sslmode=require
JWT_SECRET=a-long-random-string
GROQ_API_KEY=gsk_...
```

### **3. Run**
```powershell
cd frontend
npm install
npm run db:migrate   # creates/updates tables (also runs before every build)
npm run dev
```

The first account that signs up becomes the workspace **Admin**.

---

## 🚀 Deployment Strategy

### **Frontend & Backend (Vercel)**
The entire application — UI, API, auth, document processing and embeddings — is a single Next.js project deployed to Vercel (Root Directory: `frontend`), with data in Neon. See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

---

## 📂 System Manifest
*   **[Core Logic](./frontend/src/lib/server/)**: Ingestion, text extraction, embeddings, AI answers and integration adapters.
*   **[API Routes](./frontend/src/app/api/)**: Auth, documents, search, integrations, admin and analytics endpoints.
*   **[Schema Definitions](./frontend/db/schema.sql)**: Database schema, applied by `npm run db:migrate`.

---

© 2026 DevHive Enterprise | **Designed for High-Speed Knowledge Discovery**# devhive-2

