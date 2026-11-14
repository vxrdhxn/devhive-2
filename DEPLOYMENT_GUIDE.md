# 🚀 DevHive: Deployment Guide

The whole app — UI, API, auth, document processing and AI search — is a single
**Next.js** project in `frontend/`, deployed to **Vercel**. Data lives in **Neon**
(Postgres + pgvector). There is no separate backend server.

| Piece | Where it runs |
| --- | --- |
| Pages + API routes (`src/app/api/*`) | Vercel (Node.js functions) |
| Auth (email/password, bcrypt, JWT in httpOnly cookie) | Vercel |
| Text extraction (PDF, DOCX, PPTX, XLSX, RTF, CSV, TXT, MD) | Vercel |
| Embeddings (BAAI/bge-small-en-v1.5, ONNX, no API key) | Vercel |
| AI answers | Groq / any OpenAI-compatible API / Neon AI Gateway |
| Database + vector search | Neon |

> **The first account that signs up becomes the workspace admin.**

---

## 🏗️ 1. Database (Neon)

The repo is already linked to a Neon project (`neon.ts`, `.neon`). To get the
connection strings into the repo-root `.env`:

```bash
neon env pull
```

The schema in [`frontend/db/schema.sql`](frontend/db/schema.sql) is applied
automatically before every build (`npm run build` runs `npm run db:migrate`).

---

## 🎨 2. Vercel

1. Vercel project → **Settings → General → Root Directory**: `frontend`
   (Framework preset: Next.js).
2. **Settings → Environment Variables** (Production + Preview):

   | Key | Value |
   | --- | --- |
   | `DATABASE_URL` | Neon **pooled** URL (from the root `.env`) |
   | `DATABASE_URL_UNPOOLED` | Neon **direct** URL (from the root `.env`) |
   | `JWT_SECRET` | long random string (copy from your `.env`) |
   | `GROQ_API_KEY` | from console.groq.com (or set `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`) |

   Remove the old `NEXT_PUBLIC_SUPABASE_*` and `BACKEND_URL` variables.
3. Deploy (push to the production branch, or **Redeploy**).

Upload and search functions use up to 300 s (`maxDuration`), which requires
Fluid compute — on by default for new Vercel projects.

---

## 💻 Local development

```bash
cd frontend
npm install
npm run env:sync     # copy DATABASE_URL etc. from ../.env into .env.local
npm run dev
```

---

### ✅ Post-deployment checks
- [ ] Visit the site and sign up (first account = admin).
- [ ] Upload a small PDF and watch it reach **completed** in the processing panel.
- [ ] Search for something in it.
- [ ] Open **System Overview** and check the Member Directory.
