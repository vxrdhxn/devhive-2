"""
Database connection and session management
Configures SQLAlchemy with connection pooling for PostgreSQL + pgvector
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create SQLAlchemy engine with connection pooling
# Pool size: 20 connections as per requirements 8.2, 20.6
engine = create_engine(
    str(settings.database_url),
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,  # 20 connections
    max_overflow=settings.db_max_overflow,  # Additional 10 connections
    pool_timeout=settings.db_pool_timeout,  # 30 seconds timeout
    pool_recycle=settings.db_pool_recycle,  # Recycle after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
)


# Event listener to log slow queries (> 5 seconds)
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault("query_start_time", []).append(
        __import__("time").time()
    )


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total = __import__("time").time() - conn.info["query_start_time"].pop()
    if total > 5.0:  # Log queries taking more than 5 seconds
        logger.warning(
            f"Slow query detected: {total:.2f}s - {statement[:100]}..."
        )


# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
            pass
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database connection and verify pgvector extension
    Should be called on application startup
    """
    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection successful")
            
            # Verify pgvector extension is installed
            result = conn.execute(
                __import__("sqlalchemy").text(
                    "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
                )
            )
            extension = result.fetchone()
            
            if extension:
                logger.info(f"pgvector extension verified: version {extension[1]}")
            else:
                logger.error("pgvector extension not found! Please install it.")
                raise RuntimeError("pgvector extension not installed")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def close_db() -> None:
    """
    Close database connections
    Should be called on application shutdown
    """
    engine.dispose()
    logger.info("Database connections closed")
