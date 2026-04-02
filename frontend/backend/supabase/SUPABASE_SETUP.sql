-- [KTP ENTERPRISE: FULL DATABASE SETUP]
-- Run this in your Supabase SQL Editor to initialize the entire system

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. TABLES
-- Profiles: Organizational Hierarchy
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT,
    role TEXT DEFAULT 'employee' CHECK (role IN ('admin', 'manager', 'employee')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Documents: Shared Knowledge Base
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_by UUID REFERENCES auth.users(id), -- Linked directly to auth for shared access
    status TEXT DEFAULT 'processing',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Chunks: Vector Store (384 dimensions for BAAI/bge-small-en-v1.5)
CREATE TABLE IF NOT EXISTS public.chunks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384), 
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Integrations: Shared Bridge Connections
CREATE TABLE IF NOT EXISTS public.integrations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    platform_name TEXT NOT NULL,
    base_url TEXT,
    api_token TEXT,
    platform_type TEXT DEFAULT 'rest',
    last_synced_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Query Logs: System Interaction History
CREATE TABLE IF NOT EXISTS public.query_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    query TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. INDEXES
CREATE INDEX ON public.chunks USING hnsw (embedding vector_l2_ops);

-- 4. SECURITY (ROW LEVEL SECURITY)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.query_logs ENABLE ROW LEVEL SECURITY;

-- [POLICIES: PROFILES]
CREATE POLICY "Authenticated users can see all profiles" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Admins can update any profile" ON public.profiles FOR UPDATE USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
);

-- [POLICIES: SHARED WORKSPACE (DOCUMENTS & INTEGRATIONS)]
-- Everyone authenticated can see files/connections
CREATE POLICY "Shared read access" ON public.documents FOR SELECT USING (true);
CREATE POLICY "Shared integration access" ON public.integrations FOR SELECT USING (true);

-- Everyone can contribute
CREATE POLICY "All roles can upload" ON public.documents FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "All roles can connect" ON public.integrations FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Admin/Manager or Owner can delete
CREATE POLICY "Admin/Manager deletion on documents" ON public.documents FOR DELETE USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('admin', 'manager')) OR uploaded_by = auth.uid()
);
CREATE POLICY "Admin/Manager deletion on integrations" ON public.integrations FOR DELETE USING (
  EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('admin', 'manager')) OR user_id = auth.uid()
);

-- [POLICIES: CHUNKS & LOGS]
CREATE POLICY "Shared chunk access" ON public.chunks FOR SELECT USING (true);
CREATE POLICY "Users can see all query logs" ON public.query_logs FOR SELECT USING (true);
CREATE POLICY "Internal log insertion" ON public.query_logs FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- 5. FUNCTIONS & SEARCH
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        chunks.id, chunks.document_id, chunks.content,
        1 - (chunks.embedding <=> query_embedding) AS similarity
    FROM chunks
    WHERE 1 - (chunks.embedding <=> query_embedding) > match_threshold
    ORDER BY chunks.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 6. AUTOMATED TRIGGERS
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, role)
    VALUES (new.id, new.email, 'employee');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
