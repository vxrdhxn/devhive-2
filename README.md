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
    *   **Inference**: Groq `openai/gpt-oss-20b` by default, or any OpenAI-compatible API / the Neon AI Gateway.

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
*   A [Neon](https://neon.tech) account and the Neon CLI (`npm i -g neonctl`, then `neon auth`)
*   Optional: a [Groq API key](https://console.groq.com/keys) (free tier) for AI answers. Search works without it.

### **2. Database (Neon Postgres + pgvector)**
The repo is linked to a Neon project through [`neon.ts`](./neon.ts) and the `.neon` file (git-ignored).

*   **Using the linked project:** run `neon env pull` in the repo root. It writes `DATABASE_URL` (pooled) and `DATABASE_URL_UNPOOLED` (direct) to the root `.env`.
*   **Using your own project:** create one in the Neon console and copy both connection strings from **Connect** (pooled and direct) into `frontend/.env.local` yourself.

You don't need to set up tables by hand. [`frontend/db/schema.sql`](./frontend/db/schema.sql) enables `vector` and `pgcrypto` and creates every table and index. `npm run db:migrate` applies it, and it is safe to re-run.

> **No Neon account?** `docker compose up -d db` starts a local Postgres with pgvector. Set both database URLs to `postgresql://devhive:devhive@localhost:5432/devhive`.

### **3. Environment Configuration**
Copy the Neon variables from the root `.env` into `frontend/.env.local` (the file Next.js reads):

```powershell
cd frontend
npm run env:sync
```

Then add the rest. [`frontend/.env.example`](./frontend/.env.example) lists every option.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | ✅ | Neon **pooled** URL (`-pooler` in the host), used by the app at runtime |
| `DATABASE_URL_UNPOOLED` | ✅ | Neon **direct** URL, used by `db:migrate` |
| `JWT_SECRET` | ✅ | Signs login sessions: `node -e "console.log(require('crypto').randomBytes(48).toString('base64url'))"` |
| `GROQ_API_KEY` | — | AI answers via Groq |
| `GROQ_MODEL` | — | Overrides the default `openai/gpt-oss-20b` |
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | — | Any OpenAI-compatible API instead of Groq |
| `NEON_AI_GATEWAY_BASE_URL` / `NEON_AI_GATEWAY_TOKEN` | — | Neon AI Gateway (written by `neon env pull` when enabled) |

### **4. Run**
```powershell
cd frontend
npm install
npm run db:migrate   # creates/updates tables (also runs before every build)
npm run dev
```

Open http://localhost:3000 and click **Request Access** to sign up. **The first account becomes the workspace Admin**, and later sign-ups are Employees. Accounts live in Neon's `users` table, so old Supabase logins don't carry over.

---

## 🚀 Deployment (Vercel + Neon)

The whole app (UI, API routes, auth, document processing and embeddings) is a single Next.js project on Vercel. All data lives in Neon, and there is no separate backend.

1.  **Root Directory:** `frontend` (framework preset: Next.js).
2.  **Environment Variables:** `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `JWT_SECRET`, plus `GROQ_API_KEY` (or another AI provider from the table above).
3.  **Deploy:** push to `main`. The build runs `db:migrate` first, so schema changes reach Neon before the new code goes live.

Notes:
*   Vercel and local dev can share the same Neon database, so an account created in one works in the other. For an isolated database, make a Neon branch (`neon checkout <name>`). New non-default branches expire after 7 days, as set in `neon.ts`.
*   Embeddings run on ONNX Runtime's CPU build. `next.config.ts` ships only the linux-x64 CPU binaries so the upload function stays under Vercel's 250 MB limit. Keep that in mind when changing `outputFileTracingIncludes`.

Full checklist: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

---

## 📂 System Manifest
*   **[Core Logic](./frontend/src/lib/server/)**: Ingestion, text extraction, embeddings, AI answers and integration adapters.
*   **[API Routes](./frontend/src/app/api/)**: Auth, documents, search, integrations, admin and analytics endpoints.
*   **[Schema Definitions](./frontend/db/schema.sql)**: Database schema, applied by `npm run db:migrate`.

---

© 2026 DevHive Enterprise | **Designed for High-Speed Knowledge Discovery**

