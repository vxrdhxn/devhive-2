# 🚀 DevHive: Deployment Guide

Follow these steps to take your project from local development to a professional production environment using **Vercel** and **Supabase**.

---

## 🏗️ Phase 1: Database Setup (Supabase)

1.  Log in to your [Supabase Dashboard](https://supabase.com).
2.  Open your project and go to the **SQL Editor**.
3.  Copy the contents of [schema.sql](./frontend/api/backend/supabase/schema.sql) and run it.
4.  This will create all tables, RBAC roles, and security policies.

---

## ⚙️ Phase 2: Deployment (Vercel)

1.  Log in to [Vercel](https://vercel.com).
2.  Click **Add New** > **Project**.
3.  Connect your GitHub repository.
4.  **Configure the Project**:
    -   **Framework Preset**: `Next.js`
    -   **Root Directory**: `frontend`
5.  **Environment Variables**:
    Add the following:
    -   `NEXT_PUBLIC_SUPABASE_URL`: (From Supabase settings)
    -   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (From Supabase settings)
    -   `SUPABASE_URL`: (Same as above)
    -   `SUPABASE_SERVICE_ROLE_KEY`: (From Supabase settings)
    -   `DATABASE_URL`: (Your Postgres URI)
    -   `GROQ_API_KEY`: (Your Groq Key)
    -   `HUGGINGFACE_API_KEY`: (Your HF Key)
6.  Click **Deploy**.

---

## 🔗 Phase 3: Post-Deployment Config

1.  Once Vercel finishes, go to **Settings > Functions**.
2.  Ensure your backend is correctly serving from the `/api` route (handled by `vercel.json`).
3.  Test the health check at `https://your-url.vercel.app/api/health`.

---

### ✅ Post-Deployment Checks
- [ ] Visit your Vercel URL and try to sign up.
- [ ] Upload a small PDF to verify the "Neural Matrix" connectivity.
- [ ] Check the **System Analytics** to ensure metrics are being logged correctly.

**Your Enterprise Knowledge Platform is now Live!**
