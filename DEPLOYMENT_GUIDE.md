# 🚀 KTP Enterprise: Deployment Guide

Follow these steps to take your project from local development to a professional production environment using **Render**, **Vercel**, and **Supabase**.

---

## 🏗️ Phase 1: Database Setup (Supabase)

1.  Log in to your [Supabase Dashboard](https://supabase.com).
2.  Open your project and go to the **SQL Editor**.
3.  Copy the contents of [SUPABASE_SETUP.sql](backend/supabase/SUPABASE_SETUP.sql) and run it.
4.  This will create all tables, RBAC roles, and security policies.

---

## ⚙️ Phase 2: Backend Deployment (Render)

1.  Log in to [Render](https://render.com).
2.  Click **New +** > **Web Service**.
3.  Connect your GitHub repository.
4.  **Configure the Service**:
    -   **Name**: `ktp-backend`
    -   **Environment**: `Python 3`
    -   **Root Directory**: `backend`
    -   **Build Command**: `pip install -r requirements.txt && python pre_download.py`
    -   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**:
    Click **Advanced** > **Add Environment Variable**:
    -   `SUPABASE_URL`: (From Supabase API settings)
    -   `SUPABASE_SERVICE_ROLE_KEY`: (From Supabase API settings)
    -   `DATABASE_URL`: (From Supabase Database > Connection String > URI)
    -   `GROQ_API_KEY`: (Your Groq Key)
    -   `PYTHONPATH`: `.` (Required to find the backend package)
    -   `PYTHONUNBUFFERED`: `1` (Ensures logs appear in Render dashboard)
    -   `CORS_ORIGINS`: `https://your-frontend-url.vercel.app` (You will update this after Phase 3)

---

## 🎨 Phase 3: Frontend Deployment (Vercel)

1.  Log in to [Vercel](https://vercel.com).
2.  Click **Add New** > **Project**.
3.  Connect your GitHub repository.
4.  **Configure the Project**:
    -   **Framework Preset**: `Next.js`
    -   **Root Directory**: `frontend`
5.  **Environment Variables**:
    Add the following:
    -   `NEXT_PUBLIC_SUPABASE_URL`: (Same as backend)
    -   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (The **Anon/Public** key from Supabase)
6.  Click **Deploy**.

---

## 🔗 Phase 4: Connecting the Dots

1.  Once Vercel finishes, copy your **Production URL** (e.g., `https://ktp-frontend.vercel.app`).
2.  Go back to **Render** Settings:
    -   Update `CORS_ORIGINS` to your Vercel URL.
3.  Go to **Vercel** Settings:
    -   Add `NEXT_PUBLIC_BACKEND_URL`: `https://ktp-backend.onrender.com`
4.  Redeploy/Refresh both services.

---

### ✅ Post-Deployment Checks
- [ ] Visit your Vercel URL and try to sign up.
- [ ] Upload a small PDF to verify the "Neural Matrix" connectivity.
- [ ] Check the **System Overview** to ensure the "Member Directory" loads correctly.

**Your Enterprise Knowledge Platform is now Live!**
