from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from backend.database import Base

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="team")
    documents = relationship("Document", back_populates="team")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    team = relationship("Team", back_populates="users")
    documents = relationship("Document", back_populates="uploader")
    query_logs = relationship("QueryLog", back_populates="user")
    
    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Contributor', 'Viewer')"),
    )

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(50), default='pending')
    total_chunks = Column(Integer, default=0)
    
    team = relationship("Team", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = 'chunks'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")

class QueryLog(Base):
    __tablename__ = 'query_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query_text = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="query_logs")
