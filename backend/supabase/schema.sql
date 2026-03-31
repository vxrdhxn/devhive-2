-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles / Users (Linked to auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    role TEXT DEFAULT 'viewer',
    team_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Documents
CREATE TABLE public.documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_by UUID REFERENCES public.profiles(id),
    team_id UUID,
    status TEXT DEFAULT 'processing',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Chunks (Vector Store)
CREATE TABLE public.chunks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(384), -- BAAI/bge-small-en-v1.5 corresponds to 384 dimensions
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create HNSW index for faster similarity searches (L2 distance)
CREATE INDEX ON public.chunks USING hnsw (embedding vector_l2_ops);

-- Query Logs
CREATE TABLE public.query_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id),
    query TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS (Row Level Security)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.query_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Profiles: Users can read their own profile
CREATE POLICY "Users can view own profile" 
    ON public.profiles FOR SELECT 
    USING (auth.uid() = id);

-- Documents: Users can read and create documents uploaded by themselves
CREATE POLICY "Users can view their own documents" 
    ON public.documents FOR SELECT 
    USING (auth.uid() = uploaded_by);

CREATE POLICY "Users can insert their own documents" 
    ON public.documents FOR INSERT 
    WITH CHECK (auth.uid() = uploaded_by);

-- Chunks: Read chunks of documents the user has access to
CREATE POLICY "Users can view and edit chunks of their documents" 
    ON public.chunks FOR ALL 
    USING (EXISTS (
        SELECT 1 FROM public.documents d 
        WHERE d.id = chunks.document_id 
        AND d.uploaded_by = auth.uid()
    ));

-- Query Logs: Users can view and create their own history
CREATE POLICY "Users can view their own query logs" 
    ON public.query_logs FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own query logs" 
    ON public.query_logs FOR INSERT 
    WITH CHECK (auth.uid() = user_id);


-- Set up Supabase matching function utilizing pgvector
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(384),
    match_threshold float,
    match_count int,
    user_id uuid
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        chunks.id,
        chunks.document_id,
        chunks.content,
        1 - (chunks.embedding <=> query_embedding) AS similarity
    FROM chunks
    JOIN documents ON documents.id = chunks.document_id
    WHERE 1 - (chunks.embedding <=> query_embedding) > match_threshold
      AND documents.uploaded_by = user_id -- Safely restricts cross-tenant vector matches
    ORDER BY chunks.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Integrations (Connected Platforms)
CREATE TABLE public.integrations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    platform_name TEXT NOT NULL,
    base_url TEXT, -- Optional for some platforms
    api_token TEXT, -- Stores the connector's API key/token
    platform_type TEXT DEFAULT 'rest', -- e.g. 'notion', 'jira', 'github'
    last_synced_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own integrations" 
    ON public.integrations FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own integrations" 
    ON public.integrations FOR INSERT 
    WITH CHECK (auth.uid() = user_id);


-- TRIGGER: Automatically create a profile when a new user signs up in auth.users
-- This ensures that the 'profiles' table always has a record for 'documents.uploaded_by'
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, role)
    VALUES (new.id, new.email, 'viewer');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- The trigger must be on the auth.users table in the auth schema
-- Note: You may need to run this as a superuser/service-role in Supabase SQL Editor
-- CREATE TRIGGER on_auth_user_created
--     AFTER INSERT ON auth.users
--     FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

