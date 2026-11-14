-- DevHive database schema (Postgres + pgvector, e.g. Neon).
-- Applied by `npm run db:migrate` (also runs automatically before `npm run build`).
-- Safe to re-run: everything is IF NOT EXISTS.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- Users (replaces Supabase auth.users + public.profiles)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee' CHECK (role IN ('admin', 'manager', 'employee')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'processing',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS documents_uploaded_by_idx ON documents (uploaded_by, created_at DESC);

-- Chunks (vector store; 384 dims = BAAI/bge-small-en-v1.5)
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON chunks (document_id);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);

-- Integrations
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform_name TEXT NOT NULL,
    base_url TEXT,
    api_token TEXT,
    platform_type TEXT DEFAULT 'rest',
    last_synced_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Query logs
CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Shared-workspace features ---------------------------------------------
-- Private documents are visible only to their uploader and admins/managers.
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_private BOOLEAN NOT NULL DEFAULT false;
-- AI answer confidence, used by the analytics dashboard.
ALTER TABLE query_logs ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION;
CREATE INDEX IF NOT EXISTS query_logs_created_at_idx ON query_logs (created_at);
CREATE INDEX IF NOT EXISTS documents_filename_idx ON documents (uploaded_by, filename);
