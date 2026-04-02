"""
Tests for PostgreSQL + pgvector database setup
Validates Requirements: 8.2, 20.6
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from backend.config import get_settings
from backend.database import init_db, engine, SessionLocal


class TestDatabaseSetup:
    """Test database connection and pgvector extension"""
    
    def test_database_connection(self):
        """Test that database connection is successful"""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_pgvector_extension_installed(self):
        """Test that pgvector extension is installed and enabled"""
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
            )
            extension = result.fetchone()
            
            assert extension is not None, "pgvector extension not found"
            assert extension[0] == 'vector', "Extension name mismatch"
            assert extension[1] is not None, "Extension version not found"
    
    def test_vector_data_type_support(self):
        """Test that vector data type is supported"""
        with engine.connect() as conn:
            # Create a temporary table with vector column
            conn.execute(text("""
                CREATE TEMP TABLE test_vectors (
                    id SERIAL PRIMARY KEY,
                    embedding vector(384)
                )
            """))
            conn.commit()
            
            # Insert a test vector
            conn.execute(text("""
                INSERT INTO test_vectors (embedding) 
                VALUES (array_fill(0.5, ARRAY[384])::vector)
            """))
            conn.commit()
            
            # Query the vector
            result = conn.execute(text("SELECT embedding FROM test_vectors"))
            vector = result.fetchone()[0]
            
            # Verify vector was stored and retrieved
            assert vector is not None
            assert len(vector) == 384 or '[' in str(vector)  # pgvector returns string representation
    
    def test_connection_pool_configuration(self):
        """Test that connection pool is configured correctly (pool size: 20)"""
        settings = get_settings()
        
        # Verify pool configuration
        assert engine.pool.size() == settings.db_pool_size, \
            f"Expected pool size {settings.db_pool_size}, got {engine.pool.size()}"
        assert settings.db_pool_size == 20, "Pool size should be 20 as per requirements"
        
        # Verify pool class
        assert isinstance(engine.pool, QueuePool), "Should use QueuePool"
    
    def test_connection_pool_functionality(self):
        """Test that connection pooling works correctly"""
        # Get multiple connections from pool
        connections = []
        for _ in range(5):
            conn = engine.connect()
            connections.append(conn)
            
            # Verify connection works
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        
        # Close all connections (return to pool)
        for conn in connections:
            conn.close()
        
        # Verify we can still get new connections
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_init_db_function(self):
        """Test that init_db() function works correctly"""
        # This should not raise any exceptions
        init_db()
    
    def test_session_creation(self):
        """Test that database sessions can be created"""
        db = SessionLocal()
        try:
            # Execute a simple query
            result = db.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
        finally:
            db.close()
    
    def test_vector_operations(self):
        """Test basic vector operations (cosine similarity)"""
        with engine.connect() as conn:
            # Create temporary table
            conn.execute(text("""
                CREATE TEMP TABLE test_vector_ops (
                    id SERIAL PRIMARY KEY,
                    embedding vector(384)
                )
            """))
            conn.commit()
            
            # Insert test vectors
            conn.execute(text("""
                INSERT INTO test_vector_ops (embedding) VALUES
                (array_fill(1.0, ARRAY[384])::vector),
                (array_fill(0.5, ARRAY[384])::vector)
            """))
            conn.commit()
            
            # Test cosine similarity operator (<=>)
            result = conn.execute(text("""
                SELECT 1 - (embedding <=> array_fill(1.0, ARRAY[384])::vector) as similarity
                FROM test_vector_ops
                ORDER BY similarity DESC
                LIMIT 1
            """))
            
            similarity = result.fetchone()[0]
            assert similarity is not None
            assert 0.0 <= similarity <= 1.0, "Similarity should be between 0 and 1"


class TestDatabaseConfiguration:
    """Test database configuration settings"""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        settings = get_settings()
        
        assert settings.database_url is not None
        assert settings.db_pool_size == 20
        assert settings.db_max_overflow >= 0
        assert settings.db_pool_timeout > 0
        assert settings.db_pool_recycle > 0
    
    def test_pool_size_requirement(self):
        """Test that pool size meets requirement 20.6 (pool size: 20)"""
        settings = get_settings()
        assert settings.db_pool_size == 20, \
            "Pool size must be 20 as per requirement 20.6"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
