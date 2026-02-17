# PostgreSQL + pgvector Database Setup

This document describes the PostgreSQL database setup with pgvector extension for KTP Enterprise MVP Version 2.

## Overview

The system uses PostgreSQL 15+ with the pgvector extension for unified storage of both relational data and vector embeddings. This replaces the previous Pinecone vector database architecture.

**Validates Requirements:**
- 8.2: Vector Storage in PostgreSQL
- 20.6: Connection pooling with pool size of 20

## Components

### 1. Docker Compose Configuration

The `docker-compose.yml` file provides a containerized PostgreSQL instance with pgvector:

- **Image**: `pgvector/pgvector:pg15`
- **Database**: `ktp_db`
- **User**: `ktp_user`
- **Port**: 5432
- **Features**:
  - Persistent data storage via Docker volume
  - Health checks for connection monitoring
  - Automatic initialization script execution

### 2. Database Initialization

The `init-db.sql` script runs automatically on first container startup:

- Enables the pgvector extension
- Verifies extension installation
- Tests vector functionality

### 3. Database Configuration

The `backend/config.py` file manages all database settings:

- **Connection URL**: PostgreSQL connection string
- **Pool Size**: 20 connections (as per requirement 20.6)
- **Max Overflow**: 10 additional connections
- **Pool Timeout**: 30 seconds
- **Pool Recycle**: 3600 seconds (1 hour)

### 4. Database Connection Module

The `backend/database.py` file provides:

- SQLAlchemy engine with connection pooling
- Session management for database operations
- Database initialization and verification
- Slow query logging (queries > 5 seconds)
- Connection health monitoring

## Quick Start

### 1. Start PostgreSQL

```bash
# Start the database container
docker-compose up -d postgres

# Check container status
docker-compose ps

# View logs
docker-compose logs postgres
```

### 2. Verify Installation

```bash
# Connect to the database
docker-compose exec postgres psql -U ktp_user -d ktp_db

# Check pgvector extension
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

# Exit psql
\q
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# The default DATABASE_URL should work with docker-compose
```

### 4. Run Tests

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run database setup tests
pytest tests/test_database_setup.py -v
```

## Connection Pooling

The database uses SQLAlchemy's QueuePool with the following configuration:

- **Pool Size**: 20 connections (requirement 20.6)
- **Max Overflow**: 10 additional connections (total 30 max)
- **Timeout**: 30 seconds to get connection from pool
- **Recycle**: Connections recycled after 1 hour
- **Pre-ping**: Connections verified before use

This configuration supports at least 50 concurrent users (requirement 20.4) with efficient connection reuse.

## Vector Operations

The pgvector extension provides:

- **Vector Data Type**: `vector(384)` for 384-dimensional embeddings
- **Similarity Search**: Cosine similarity using `<=>` operator
- **Indexing**: IVFFlat index for efficient similarity search
- **Operations**: Distance calculations, nearest neighbor search

Example vector operations:

```sql
-- Create table with vector column
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    embedding vector(384)
);

-- Insert vector
INSERT INTO chunks (embedding) 
VALUES (array_fill(0.5, ARRAY[384])::vector);

-- Cosine similarity search
SELECT id, 1 - (embedding <=> query_vector) as similarity
FROM chunks
ORDER BY embedding <=> query_vector
LIMIT 5;
```

## Monitoring

### Health Checks

The database includes health check endpoints:

```bash
# Docker health check
docker-compose ps

# Application health check
curl http://localhost:8000/health/db
```

### Performance Monitoring

The system logs:

- Slow queries (> 5 seconds)
- Connection pool usage
- Database connection failures
- Query execution times

### Connection Pool Status

Monitor connection pool usage:

```python
from backend.database import engine

# Get pool status
pool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

## Troubleshooting

### Connection Refused

If you get "connection refused" errors:

```bash
# Check if container is running
docker-compose ps

# Check container logs
docker-compose logs postgres

# Restart container
docker-compose restart postgres
```

### pgvector Extension Not Found

If pgvector is not installed:

```bash
# Recreate container with fresh initialization
docker-compose down -v
docker-compose up -d postgres

# Verify extension
docker-compose exec postgres psql -U ktp_user -d ktp_db -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

### Pool Exhaustion

If you get "pool exhausted" errors:

- Check for connection leaks (unclosed sessions)
- Increase `DB_MAX_OVERFLOW` in .env
- Monitor slow queries that hold connections
- Verify connection recycling is working

### Slow Queries

If queries are slow:

- Check query execution plans: `EXPLAIN ANALYZE <query>`
- Verify indexes are created (Task 1.3)
- Monitor connection pool usage
- Check database resource usage

## Security

### Production Checklist

- [ ] Change default database password
- [ ] Use strong JWT_SECRET
- [ ] Enable SSL/TLS for database connections
- [ ] Restrict database port access (firewall)
- [ ] Use environment variables for secrets
- [ ] Enable database connection encryption
- [ ] Regular backups of postgres_data volume
- [ ] Monitor for SQL injection attempts

### Connection String Security

Never commit database credentials to version control:

- Use `.env` file (gitignored)
- Use environment variables in production
- Rotate credentials regularly
- Use least-privilege database users

## Backup and Recovery

### Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U ktp_user ktp_db > backup.sql

# Backup with compression
docker-compose exec postgres pg_dump -U ktp_user ktp_db | gzip > backup.sql.gz
```

### Restore

```bash
# Restore from backup
docker-compose exec -T postgres psql -U ktp_user ktp_db < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U ktp_user ktp_db
```

## Next Steps

After completing Task 1.1, proceed to:

- **Task 1.2**: Create database schema with Alembic migrations
- **Task 1.3**: Create database indexes for performance
- **Task 1.4**: Write property test for foreign key integrity

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- Requirements: 8.2, 20.6
- Design Document: Database Schema section
