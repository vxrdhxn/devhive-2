-- Initialize PostgreSQL database with pgvector extension
-- This script runs automatically when the container is first created

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Create a test table to verify vector functionality
CREATE TABLE IF NOT EXISTS vector_test (
    id SERIAL PRIMARY KEY,
    embedding vector(384)
);

-- Insert a test vector
INSERT INTO vector_test (embedding) VALUES (array_fill(0.0, ARRAY[384])::vector);

-- Clean up test table
DROP TABLE IF EXISTS vector_test;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension successfully enabled';
END $$;
