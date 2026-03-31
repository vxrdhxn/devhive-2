# Knowledge Transfer Platform (KTP)

An enterprise-grade knowledge management system designed for seamless information sharing and discovery. The platform utilizes AI-driven vector search to provide high-speed, relevant results across organizational documentation.

## 🚀 Key Features

- **AI-Powered Discovery**: Advanced semantic search utilizing `pgvector` and LLaMA 3 (Groq) for contextual information retrieval.
- **Organizational RBAC**: Granular role-based access control with `Admin`, `Manager`, and `Employee` tiers.
- **Shared Workspace**: Persistent document library and platform integrations accessible across the entire organization.
- **System Monitoring**: Comprehensive dashboard for tracking ingestion status, node health, and user activity.
- **Premium Interface**: High-contrast, responsive UI inspired by modern enterprise design standards.

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, React, Tailwind CSS, Framer Motion.
- **Backend**: FastAPI, Python 3.13, Pydantic.
- **Database/Auth**: Supabase (PostgreSQL + pgvector).
- **AI/ML**: Groq API, Sentence-Transformers.

## 🏁 Getting Started

Detailed instructions for setting up the environment and deploying the platform can be found in the [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

### Quick Links
- [Database Schema](./backend/supabase/SUPABASE_SETUP.sql)
- [Backend Configuration](./backend/config.py)
- [Member Management Logic](./frontend/src/components/MemberDirectory.tsx)

---

Developed for high-performance organizational knowledge transfer.