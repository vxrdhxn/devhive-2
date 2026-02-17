# Design Document: KTP Enterprise MVP Version 2

## Overview

KTP Enterprise MVP Version 2 is an enterprise-grade internal AI Knowledge Platform that enables secure document management, semantic search, and AI-powered question answering. The system replaces the existing Dev-Hive architecture with a modern, scalable solution built on PostgreSQL + pgvector, Groq LLaMA 3, and Next.js.

### Key Design Principles

1. **Unified Storage**: PostgreSQL with pgvector extension provides both relational and vector storage, eliminating external dependencies
2. **Modular Services**: FastAPI microservices with clear separation of concerns (Auth, Ingestion, Search, AI)
3. **Cost Efficiency**: Local embedding generation with SentenceTransformer and Groq API for inference
4. **Enterprise Security**: JWT-based authentication with RBAC and team-based data isolation
5. **Production-Ready Frontend**: Next.js with Tailwind CSS for scalable, maintainable UI

### Migration Strategy

The design transforms Dev-Hive by:
- Replacing Pinecone → PostgreSQL + pgvector
- Replacing OpenAI GPT → Groq LLaMA 3
- Replacing OpenAI embeddings → SentenceTransformer (bge-small)
- Replacing Streamlit → Next.js + Tailwind CSS
- Simplifying Docker/Kubernetes → Service-based FastAPI
- Removing flashcards and overengineered infrastructure

## Architecture

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js + Tailwind UI]
    end
    
    subgraph "API Gateway Layer"
        Gateway[FastAPI Gateway]
    end
    
    subgraph "Service Layer"
        Auth[Auth Service]
        Ingest[Ingestion Service]
        Search[Search Service]
        AI[AI Service]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL + pgvector)]
    end
    
    subgraph "External Services"
        Groq[Groq API - LLaMA 3]
    end
    
    subgraph "ML Models"
        Embed[SentenceTransformer<br/>bge-small]
    end
    
    UI -->|HTTP/REST| Gateway
    Gateway --> Auth
    Gateway --> Ingest
    Gateway --> Search
    Gateway --> AI
    
    Auth --> DB
    Ingest --> DB
    Search --> DB
    
    Ingest --> Embed
    Search --> Embed
    AI --> Groq
    
    Search --> AI
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18
- Tailwind CSS 3
- TypeScript
- Axios for API calls
- React Query for state management

**Backend:**
- Python 3.11+
- FastAPI 0.104+
- Pydantic v2 for validation
- SQLAlchemy 2.0 for ORM
- Alembic for migrations
- python-jose for JWT
- bcrypt for password hashing
- uvicorn as ASGI server

**AI/ML:**
- sentence-transformers 2.2+ (bge-small-en-v1.5)
- groq-python SDK
- PyPDF2 for PDF extraction
- python-docx for DOCX extraction

**Database:**
- PostgreSQL 15+
- pgvector 0.5+ extension

**Infrastructure:**
- Docker for containerization
- Environment-based configuration
- Structured logging (JSON format)

### Deployment Architecture

```
┌─────────────────────────────────────────────┐
│           Load Balancer / Nginx             │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│  Next.js App   │    │  FastAPI Backend│
│  (Port 3000)   │    │  (Port 8000)    │
└────────────────┘    └─────────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐    ┌────────▼────────┐
            │  PostgreSQL    │    │  Groq API       │
            │  + pgvector    │    │  (External)     │
            └────────────────┘    └─────────────────┘
```

## Components and Interfaces

### 1. Authentication Service (Auth Service)

**Responsibilities:**
- User registration and login
- JWT token generation and validation
- Password hashing and verification
- Role and team assignment
- RBAC enforcement

**API Endpoints:**

```python
POST /api/auth/register
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe",
  "team_id": 1
}
Response:
{
  "user_id": 123,
  "email": "user@example.com",
  "role": "Contributor",
  "team_id": 1
}

POST /api/auth/login
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "Contributor",
    "team_id": 1
  }
}

GET /api/auth/me
Headers: Authorization: Bearer <token>
Response:
{
  "id": 123,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "Contributor",
  "team_id": 1
}
```

**Key Functions:**

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12"""
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    
def create_access_token(user_id: int, role: str, team_id: int) -> str:
    """Generate JWT token with 24-hour expiration"""
    
def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    
def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
```

**Permission Matrix:**

| Action | Admin | Contributor | Viewer |
|--------|-------|-------------|--------|
| Upload Documents | ✓ | ✓ | ✗ |
| Search Documents | ✓ | ✓ | ✓ |
| Manage Users | ✓ | ✗ | ✗ |
| View Query Logs | ✓ | ✗ | ✗ |

### 2. Ingestion Service

**Responsibilities:**
- File upload handling
- Text extraction from PDF, DOCX, TXT
- Text preprocessing and cleaning
- Text chunking with overlap
- Embedding generation
- Vector storage in PostgreSQL

**API Endpoints:**

```python
POST /api/ingest/upload
Headers: Authorization: Bearer <token>
Content-Type: multipart/form-data
Request:
{
  "file": <binary>,
  "filename": "document.pdf"
}
Response:
{
  "document_id": 456,
  "filename": "document.pdf",
  "chunks_created": 42,
  "status": "completed",
  "upload_timestamp": "2024-01-15T10:30:00Z"
}

GET /api/ingest/status/{document_id}
Headers: Authorization: Bearer <token>
Response:
{
  "document_id": 456,
  "status": "processing|completed|failed",
  "progress": 75,
  "chunks_processed": 32,
  "total_chunks": 42
}
```

**Processing Pipeline:**

```python
class IngestionPipeline:
    def process_document(self, file: UploadFile, user_id: int, team_id: int) -> Document:
        """
        Main pipeline:
        1. Validate file format and size
        2. Extract text
        3. Clean and preprocess
        4. Chunk text
        5. Generate embeddings
        6. Store in database
        """
        
    def extract_text(self, file: UploadFile) -> str:
        """Extract text based on file type"""
        
    def clean_text(self, text: str) -> str:
        """Remove excessive whitespace, normalize line breaks"""
        
    def chunk_text(self, text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks at sentence boundaries"""
        
    def generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        """Generate embeddings using SentenceTransformer in batches"""
        
    def store_chunks(self, document_id: int, chunks: List[str], 
                    embeddings: List[np.ndarray], team_id: int) -> None:
        """Store chunks and embeddings in PostgreSQL"""
```

**Text Extraction:**

```python
class TextExtractor:
    def extract_pdf(self, file_path: str) -> str:
        """Use PyPDF2 to extract text from PDF"""
        
    def extract_docx(self, file_path: str) -> str:
        """Use python-docx to extract text from DOCX"""
        
    def extract_txt(self, file_path: str) -> str:
        """Read text file with UTF-8 encoding"""
```

**Chunking Strategy:**

- Maximum chunk size: 512 tokens (approximately 384 words)
- Overlap: 50 tokens between consecutive chunks
- Split at sentence boundaries using NLTK sentence tokenizer
- Preserve semantic coherence within chunks
- Include metadata: chunk_index, total_chunks, document_id

### 3. Search Service

**Responsibilities:**
- Query embedding generation
- Vector similarity search
- Team-based filtering
- Result ranking and retrieval
- Query logging

**API Endpoints:**

```python
POST /api/search/query
Headers: Authorization: Bearer <token>
Request:
{
  "query": "What is the company's remote work policy?",
  "top_k": 5,
  "min_similarity": 0.3
}
Response:
{
  "query": "What is the company's remote work policy?",
  "results": [
    {
      "chunk_id": 789,
      "document_id": 456,
      "filename": "hr_policies.pdf",
      "chunk_text": "Remote work is permitted...",
      "similarity_score": 0.87,
      "chunk_index": 5,
      "total_chunks": 42
    }
  ],
  "answer": {
    "text": "According to the HR policies...",
    "sources": [
      {
        "document": "hr_policies.pdf",
        "relevance": 0.87
      }
    ]
  }
}
```

**Search Implementation:**

```python
class SemanticSearch:
    def __init__(self, embedding_model: SentenceTransformer, db: Database):
        self.embedding_model = embedding_model
        self.db = db
        
    def search(self, query: str, team_id: int, top_k: int = 5, 
              min_similarity: float = 0.3) -> List[SearchResult]:
        """
        1. Generate query embedding
        2. Perform cosine similarity search with team filter
        3. Rank results by similarity
        4. Return top_k results above threshold
        """
        
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate normalized embedding for query"""
        
    def vector_search(self, query_embedding: np.ndarray, team_id: int, 
                     top_k: int) -> List[SearchResult]:
        """
        Execute pgvector similarity search:
        SELECT chunk_id, chunk_text, document_id, filename,
               1 - (embedding <=> query_embedding) as similarity
        FROM chunks
        WHERE team_id = ?
        ORDER BY embedding <=> query_embedding
        LIMIT top_k
        """
```

### 4. AI Service

**Responsibilities:**
- Prompt construction
- Groq API integration
- Answer generation
- Response parsing and formatting
- Error handling and retries

**API Endpoints:**

```python
POST /api/ai/generate-answer
Headers: Authorization: Bearer <token>
Request:
{
  "query": "What is the company's remote work policy?",
  "context_chunks": [
    {
      "text": "Remote work is permitted...",
      "source": "hr_policies.pdf"
    }
  ]
}
Response:
{
  "answer": "According to the HR policies...",
  "sources": [
    {
      "document": "hr_policies.pdf",
      "relevance": 0.87
    }
  ],
  "model": "llama3-70b-8192",
  "tokens_used": 450
}
```

**Answer Generation:**

```python
class AnswerGenerator:
    def __init__(self, groq_client: Groq):
        self.groq_client = groq_client
        self.model = "llama3-70b-8192"
        
    def generate_answer(self, query: str, context_chunks: List[dict]) -> dict:
        """
        1. Construct prompt with query and context
        2. Call Groq API with retry logic
        3. Parse response
        4. Format answer with sources
        """
        
    def construct_prompt(self, query: str, context_chunks: List[dict]) -> str:
        """
        Build prompt:
        
        You are a helpful AI assistant. Answer the question based on the provided context.
        
        Context:
        [Document 1: hr_policies.pdf]
        Remote work is permitted...
        
        [Document 2: benefits.pdf]
        Employees can work remotely...
        
        Question: What is the company's remote work policy?
        
        Provide a clear, concise answer based only on the context provided.
        Include references to source documents.
        """
        
    def call_groq_api(self, prompt: str, max_retries: int = 2) -> str:
        """Call Groq API with exponential backoff retry"""
        
    def parse_response(self, response: str, sources: List[dict]) -> dict:
        """Extract answer and format with source references"""
```

**Retry Strategy:**

- Initial timeout: 30 seconds
- Max retries: 2
- Backoff: Exponential (1s, 2s, 4s)
- Circuit breaker: Open after 5 consecutive failures

### 5. Frontend Application

**Responsibilities:**
- User authentication UI
- Document upload interface
- Search interface
- Results display
- Error handling and user feedback

**Page Structure:**

```
/
├── /login
├── /register
├── /dashboard
│   ├── /upload
│   └── /search
└── /admin
    ├── /users
    └── /logs
```

**Key Components:**

```typescript
// Authentication
interface LoginForm {
  email: string;
  password: string;
}

interface RegisterForm extends LoginForm {
  name: string;
  confirmPassword: string;
}

// Document Upload
interface UploadComponent {
  onFileSelect: (file: File) => void;
  onUpload: () => Promise<void>;
  uploadProgress: number;
  uploadStatus: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
}

// Search
interface SearchComponent {
  query: string;
  onSearch: (query: string) => Promise<void>;
  results: SearchResult[];
  answer: Answer | null;
  isLoading: boolean;
}

interface SearchResult {
  chunkId: number;
  documentId: number;
  filename: string;
  chunkText: string;
  similarityScore: number;
}

interface Answer {
  text: string;
  sources: Source[];
}

interface Source {
  document: string;
  relevance: number;
}
```

**State Management:**

```typescript
// Using React Query for server state
const useAuth = () => {
  const login = useMutation(loginUser);
  const logout = useMutation(logoutUser);
  const { data: user } = useQuery('currentUser', getCurrentUser);
  return { user, login, logout };
};

const useSearch = () => {
  const search = useMutation(searchQuery);
  return { search };
};

const useUpload = () => {
  const upload = useMutation(uploadDocument);
  return { upload };
};
```

## Data Models

### Database Schema

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Admin', 'Contributor', 'Viewer')),
    team_id INTEGER NOT NULL REFERENCES teams(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_team ON users(team_id);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    uploaded_by INTEGER NOT NULL REFERENCES users(id),
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending',
    total_chunks INTEGER DEFAULT 0
);

CREATE INDEX idx_documents_team ON documents(team_id);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);

-- Chunks table with vector embeddings
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    chunk_index INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_chunks_team ON chunks(team_id);

-- Create IVFFlat index for vector similarity search
CREATE INDEX idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Query logs table
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    query_text TEXT NOT NULL,
    results_count INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_query_logs_user ON query_logs(user_id);
CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);
```

### SQLAlchemy Models

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime

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
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=255)
    team_id: int
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    team_id: int
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400
    user: UserResponse

# Document schemas
class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    chunks_created: int
    status: str
    upload_timestamp: datetime

class DocumentStatus(BaseModel):
    document_id: int
    status: str
    progress: int
    chunks_processed: int
    total_chunks: int

# Search schemas
class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.3, ge=0.0, le=1.0)

class SearchResultItem(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    chunk_text: str
    similarity_score: float
    chunk_index: int
    total_chunks: int

class Source(BaseModel):
    document: str
    relevance: float

class Answer(BaseModel):
    text: str
    sources: List[Source]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    answer: Optional[Answer] = None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Authentication and Authorization Properties

**Property 1: Password Security**
*For any* valid user registration, the stored password must be hashed (not plaintext) and verifiable using bcrypt with cost factor 12.
**Validates: Requirements 1.1, 15.1**

**Property 2: JWT Token Claims**
*For any* successful login, the generated JWT token must contain valid user_id, role, and team_id claims that match the authenticated user's data.
**Validates: Requirements 1.2**

**Property 3: Invalid Credentials Rejection**
*For any* login attempt with invalid credentials (wrong password, non-existent email, or malformed input), the system must reject the request with an appropriate error message.
**Validates: Requirements 1.3**

**Property 4: Password Complexity Enforcement**
*For any* password input, the system must reject passwords that don't meet complexity requirements (minimum 8 characters, at least one uppercase, one lowercase, one number) and accept passwords that do meet these requirements.
**Validates: Requirements 1.4**

**Property 5: JWT Expiration**
*For any* generated JWT token, the expiration claim (exp) must be set to exactly 24 hours from the token creation time.
**Validates: Requirements 1.5**

**Property 6: Authentication Enforcement**
*For any* request to a protected endpoint without a valid JWT token (missing, expired, or invalid signature), the system must reject the request with a 401 Unauthorized status.
**Validates: Requirements 1.6, 15.4**

**Property 7: Role Assignment**
*For any* created user, the user must have exactly one role from the set {Admin, Contributor, Viewer}.
**Validates: Requirements 2.1**

**Property 8: Admin Authorization**
*For any* user with Admin role, user management operations (create, update, delete users) must be permitted.
**Validates: Requirements 2.2**

**Property 9: Contributor Upload Authorization**
*For any* user with Contributor role, document upload operations must be permitted.
**Validates: Requirements 2.3**

**Property 10: Viewer Upload Restriction**
*For any* user with Viewer role, document upload attempts must be rejected with a 403 Forbidden status.
**Validates: Requirements 2.4**

**Property 11: Non-Admin Management Restriction**
*For any* user with Contributor or Viewer role, user management operations must be rejected with a 403 Forbidden status.
**Validates: Requirements 2.5**

### Team Isolation Properties

**Property 12: User Team Assignment**
*For any* created user, the user must be assigned to exactly one team (team_id must be non-null and reference a valid team).
**Validates: Requirements 3.1**

**Property 13: Document Team Association**
*For any* uploaded document, the document's team_id must match the uploader's team_id.
**Validates: Requirements 3.2**

**Property 14: Search Team Isolation**
*For any* search query performed by a user, all returned results must only include chunks where chunk.team_id equals user.team_id (no cross-team data leakage).
**Validates: Requirements 3.3, 3.5, 9.4**

**Property 15: Chunk Team Metadata**
*For any* stored chunk, the chunk must include a team_id field that matches its parent document's team_id.
**Validates: Requirements 3.4**

### Document Upload and Processing Properties

**Property 16: Supported File Format Acceptance**
*For any* file with extension .pdf, .docx, or .txt, the ingestion service must accept the upload (assuming file size is valid).
**Validates: Requirements 4.1**

**Property 17: Unsupported File Format Rejection**
*For any* file with an extension other than .pdf, .docx, or .txt, the ingestion service must reject the upload with a descriptive error message.
**Validates: Requirements 4.2**

**Property 18: Unique Document Identifiers**
*For any* two successful document uploads, the returned document_id values must be unique.
**Validates: Requirements 4.4**

**Property 19: Document Metadata Storage**
*For any* uploaded document, the system must store the original filename and upload timestamp in the database.
**Validates: Requirements 4.5**

**Property 20: UTF-8 Text Handling**
*For any* TXT file with valid UTF-8 encoding, the system must correctly read and preserve all characters including non-ASCII Unicode characters.
**Validates: Requirements 5.3, 5.6**

**Property 21: Whitespace Normalization**
*For any* extracted text, the system must remove excessive whitespace (multiple consecutive spaces/newlines) and normalize line breaks to a consistent format.
**Validates: Requirements 5.4**

### Text Chunking Properties

**Property 22: Maximum Chunk Size**
*For any* generated chunk, the chunk must not exceed 512 tokens in length.
**Validates: Requirements 6.1, 6.3**

**Property 23: Sentence Boundary Preservation**
*For any* generated chunk, the chunk must not split in the middle of a sentence (must end at a sentence boundary).
**Validates: Requirements 6.2, 6.3**

**Property 24: Chunk Overlap**
*For any* two consecutive chunks from the same document, the chunks must share approximately 50 tokens of overlapping content.
**Validates: Requirements 6.4**

**Property 25: Chunk Metadata Completeness**
*For any* stored chunk, the chunk must include: chunk_text, embedding, document_id, team_id, chunk_index, and total_chunks fields.
**Validates: Requirements 6.5, 6.6, 8.3**

### Embedding Generation Properties

**Property 26: Embedding Generation**
*For any* document chunk, an embedding must be generated using the SentenceTransformer model.
**Validates: Requirements 7.1**

**Property 27: Embedding Dimensionality**
*For any* generated embedding, the embedding vector must have exactly 384 dimensions.
**Validates: Requirements 7.2**

**Property 28: Embedding Normalization**
*For any* generated embedding, the vector must be normalized to unit length (L2 norm approximately equal to 1.0).
**Validates: Requirements 7.3**

**Property 29: Embedding Storage Round-Trip**
*For any* generated embedding, storing it in PostgreSQL and retrieving it must produce a vector with the same dimensionality and values (within floating-point precision).
**Validates: Requirements 8.1**

**Property 30: Atomic Chunk Storage**
*For any* document upload, either all chunks must be successfully stored in the database, or none must be stored (no partial uploads due to transaction rollback on failure).
**Validates: Requirements 8.6**

### Semantic Search Properties

**Property 31: Query Embedding Generation**
*For any* search query, the system must generate a query embedding using the same SentenceTransformer model used for document embeddings.
**Validates: Requirements 9.1**

**Property 32: Query Embedding Normalization**
*For any* query embedding, the vector must be normalized to unit length (L2 norm approximately equal to 1.0).
**Validates: Requirements 9.2**

**Property 33: Cosine Similarity Search**
*For any* search operation, the system must rank results using cosine similarity (not Euclidean distance or other metrics).
**Validates: Requirements 9.3**

**Property 34: Top-K Results**
*For any* search query, the system must return at most 5 results, ranked by cosine similarity score in descending order.
**Validates: Requirements 9.5, 19.4**

**Property 35: Similarity Threshold**
*For any* search query, results with cosine similarity below 0.3 must be filtered out and not returned.
**Validates: Requirements 9.6, 19.2**

**Property 36: Search Result Completeness**
*For any* returned search result, the result must include: chunk_text, document_id, filename, similarity_score, chunk_index, and total_chunks.
**Validates: Requirements 9.7**

**Property 37: Result Ranking**
*For any* search query returning multiple results, the results must be sorted by similarity_score in descending order (highest similarity first).
**Validates: Requirements 19.1**

**Property 38: Document Context in Results**
*For any* search result, the response must include document metadata (filename, document_id) to provide context.
**Validates: Requirements 19.3**

### AI Answer Generation Properties

**Property 39: Prompt Construction**
*For any* answer generation request, the prompt sent to the LLM must include both the user's query and the retrieved context chunks.
**Validates: Requirements 10.1**

**Property 40: Structured Response Format**
*For any* LLM response, the parsed output must include both an "answer" field (string) and a "sources" field (array of source references).
**Validates: Requirements 10.3, 10.4**

### Query Logging Properties

**Property 41: Query Log Completeness**
*For any* submitted search query, a log entry must be created with user_id, query_text, and timestamp fields.
**Validates: Requirements 11.1**

**Property 42: Query Log Filtering**
*For any* admin request for query logs with filters (date range, user_id), the returned logs must match all specified filter criteria.
**Validates: Requirements 11.5**

### API and Error Handling Properties

**Property 43: Request Validation**
*For any* API request with invalid schema (missing required fields, wrong types, out-of-range values), the system must reject the request with a 400 status code and field-level error details.
**Validates: Requirements 13.4**

**Property 44: Consistent Error Format**
*For any* error response across all services, the response must follow a consistent format with status code, error message, and optional details fields.
**Validates: Requirements 13.5**

**Property 45: Request Logging**
*For any* API request, the system must log the request with timestamp, endpoint, user_id (if authenticated), and response status code.
**Validates: Requirements 13.7**

**Property 46: Foreign Key Integrity**
*For any* database operation attempting to insert a record with an invalid foreign key (referencing a non-existent parent record), the database must reject the operation.
**Validates: Requirements 14.7**

**Property 47: SQL Injection Prevention**
*For any* user input containing SQL injection attempts (e.g., '; DROP TABLE users; --), the system must safely handle the input without executing malicious SQL.
**Validates: Requirements 15.3**

**Property 48: Sensitive Data Exclusion from Logs**
*For any* log entry, the log must not contain sensitive information such as passwords, JWT tokens, or API keys.
**Validates: Requirements 15.5**

**Property 49: Unexpected Error Handling**
*For any* unexpected error (uncaught exception), the system must return a 500 status code with a generic error message (not exposing internal details).
**Validates: Requirements 16.1**

**Property 50: Validation Error Handling**
*For any* validation error, the system must return a 400 status code with specific field-level error details indicating which fields failed validation and why.
**Validates: Requirements 16.2**

**Property 51: Error Logging with Stack Traces**
*For any* error (expected or unexpected), the system must log the error with a complete stack trace for debugging purposes.
**Validates: Requirements 16.4**

### Workflow Integration Properties

**Property 52: End-to-End Upload Workflow**
*For any* valid document upload, the system must successfully complete all steps (extraction, chunking, embedding, storage) and return a response with the number of chunks created.
**Validates: Requirements 18.1, 18.3**

**Property 53: Upload Workflow Rollback**
*For any* document upload where any processing step fails, the system must rollback all database changes (no partial chunks stored) and return an error.
**Validates: Requirements 18.2**

### Performance Properties

**Property 54: Batch Embedding Generation**
*For any* document with multiple chunks, the system must generate embeddings in batches of 32 chunks (not one at a time) for optimal throughput.
**Validates: Requirements 20.1**

## Error Handling

### Error Categories

**1. Authentication Errors (401)**
- Missing JWT token
- Expired JWT token
- Invalid JWT signature
- Malformed JWT token

**2. Authorization Errors (403)**
- Insufficient permissions for operation
- Attempting to access resources from another team
- Role-based access control violations

**3. Validation Errors (400)**
- Invalid request schema
- Missing required fields
- Out-of-range values
- Unsupported file formats
- File size exceeds limit
- Password complexity violations

**4. Not Found Errors (404)**
- Document not found
- User not found
- Team not found

**5. External Service Errors (503)**
- Groq API unavailable
- Groq API timeout
- Groq API rate limit exceeded

**6. Internal Server Errors (500)**
- Unexpected exceptions
- Database connection failures
- Embedding generation failures
- Text extraction failures

### Error Response Format

All error responses follow a consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Specific field-level error (for validation errors)",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Retry Strategies

**Embedding Generation:**
- Max retries: 3
- Backoff: None (local operation)
- Fallback: Return error after 3 failures

**Groq API Calls:**
- Max retries: 2
- Backoff: Exponential (1s, 2s, 4s)
- Timeout: 30 seconds per attempt
- Circuit breaker: Open after 5 consecutive failures (5-minute cooldown)

**Database Connections:**
- Max retries: 5
- Backoff: Exponential (1s, 2s, 4s, 8s, 16s)
- Connection pool: 20 connections
- Idle timeout: 300 seconds

### Logging Strategy

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages (API requests, successful operations)
- WARNING: Potentially harmful situations (slow queries, retry attempts)
- ERROR: Error events that might still allow the application to continue
- CRITICAL: Severe errors causing application failure

**Structured Logging Format (JSON):**

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "service": "ingestion-service",
  "endpoint": "/api/ingest/upload",
  "user_id": 123,
  "team_id": 1,
  "message": "Document uploaded successfully",
  "duration_ms": 1250,
  "metadata": {
    "document_id": 456,
    "chunks_created": 42
  }
}
```

**Sensitive Data Exclusion:**
- Never log passwords (plain or hashed)
- Never log JWT tokens
- Never log API keys
- Mask email addresses in logs (show only domain)

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests:**
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, special characters)
- Error conditions (invalid inputs, service failures)
- Integration points between components
- UI component rendering and interactions

**Property-Based Tests:**
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Minimum 100 iterations per property test
- Each property test references its design document property

### Property-Based Testing Configuration

**Library Selection:**
- Python: Hypothesis
- TypeScript/JavaScript: fast-check

**Test Configuration:**
```python
# Python example with Hypothesis
from hypothesis import given, strategies as st, settings

@settings(max_examples=100)
@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=128),
    name=st.text(min_size=1, max_size=255)
)
def test_user_registration_password_hashing(email, password, name):
    """
    Feature: ktp-enterprise-mvp-migration
    Property 1: Password Security
    
    For any valid user registration, the stored password must be hashed
    (not plaintext) and verifiable using bcrypt.
    """
    # Test implementation
```

**Test Tagging Format:**
Each property-based test must include a comment with:
- Feature name: ktp-enterprise-mvp-migration
- Property number and title from design document
- Property statement

### Test Coverage Requirements

**Backend Services (Python):**
- Minimum 80% code coverage
- 100% coverage of critical paths (authentication, authorization, team isolation)
- All 54 correctness properties implemented as property-based tests
- Unit tests for error handling, edge cases, and integration points

**Frontend (TypeScript/React):**
- Component unit tests using React Testing Library
- Integration tests for user flows (login, upload, search)
- Accessibility tests (WCAG compliance checks)
- Responsive design tests (desktop, tablet viewports)

**Database:**
- Migration tests (up and down migrations)
- Constraint tests (foreign keys, check constraints)
- Index performance tests (query execution plans)

### Testing Environments

**Local Development:**
- Docker Compose with PostgreSQL + pgvector
- Mock Groq API for faster tests
- In-memory database for unit tests

**CI/CD Pipeline:**
- Automated test execution on every commit
- Property-based tests with 100 iterations
- Integration tests with real PostgreSQL instance
- End-to-end tests with Playwright

**Staging:**
- Full integration testing with real Groq API
- Load testing (50 concurrent users)
- Security testing (OWASP Top 10)
- Performance testing (search latency, upload throughput)

### Test Data Generation

**Property-Based Test Generators:**

```python
# User generators
@st.composite
def valid_user(draw):
    return {
        "email": draw(st.emails()),
        "password": draw(valid_password()),
        "name": draw(st.text(min_size=1, max_size=255)),
        "team_id": draw(st.integers(min_value=1, max_value=1000))
    }

@st.composite
def valid_password(draw):
    """Generate passwords meeting complexity requirements"""
    # At least 8 chars, 1 upper, 1 lower, 1 digit
    return draw(st.from_regex(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'))

# Document generators
@st.composite
def document_text(draw):
    """Generate realistic document text"""
    num_paragraphs = draw(st.integers(min_value=1, max_value=50))
    paragraphs = [
        draw(st.text(min_size=100, max_size=1000))
        for _ in range(num_paragraphs)
    ]
    return "\n\n".join(paragraphs)

# Search query generators
@st.composite
def search_query(draw):
    """Generate realistic search queries"""
    return draw(st.text(
        min_size=3,
        max_size=200,
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))
    ))
```

### Critical Test Scenarios

**Security Tests:**
1. Team isolation: Verify users cannot access other teams' documents
2. SQL injection: Test with malicious SQL in all input fields
3. JWT tampering: Test with modified token signatures
4. Password security: Verify bcrypt hashing and cost factor
5. Rate limiting: Verify authentication endpoint rate limits

**Functional Tests:**
1. End-to-end upload: Upload document → verify searchable
2. Search accuracy: Verify relevant results returned
3. Answer generation: Verify LLM integration works
4. Role-based access: Verify RBAC enforcement
5. Error handling: Verify graceful degradation

**Performance Tests:**
1. Search latency: 95th percentile < 2 seconds
2. Upload throughput: Process 10 documents concurrently
3. Concurrent users: 50 users searching simultaneously
4. Large documents: Handle 50MB files
5. Database queries: No queries > 5 seconds

**Integration Tests:**
1. Frontend → Backend: All API endpoints
2. Backend → PostgreSQL: All database operations
3. Backend → Groq: LLM answer generation
4. Authentication flow: Login → JWT → Protected endpoints
5. Upload workflow: File → Extraction → Chunking → Embedding → Storage → Search

## Deployment Considerations

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ktp_db

# Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Groq API
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-70b-8192
GROQ_TIMEOUT_SECONDS=30

# File Upload
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=/tmp/uploads

# Embedding Model
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_BATCH_SIZE=32

# Search
SEARCH_TOP_K=5
SEARCH_MIN_SIMILARITY=0.3

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Database Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy application
COPY . .

# Build
RUN npm run build

# Start server
CMD npm start
```

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: ktp_db
      POSTGRES_USER: ktp_user
      POSTGRES_PASSWORD: ktp_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://ktp_user:ktp_password@postgres:5432/ktp_db
      JWT_SECRET: ${JWT_SECRET}
      GROQ_API_KEY: ${GROQ_API_KEY}
    depends_on:
      - postgres
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### Monitoring and Observability

**Health Checks:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ktp-backend",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/db")
async def database_health():
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

**Metrics to Track:**
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (p50, p95, p99)
- Database connection pool usage
- Groq API latency and error rate
- Document upload success rate
- Search query latency
- Active users (concurrent sessions)

### Security Hardening

**Production Checklist:**
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set secure HTTP headers (HSTS, CSP, X-Frame-Options)
- [ ] Implement rate limiting on all endpoints
- [ ] Enable CORS with specific origins (no wildcards)
- [ ] Rotate JWT secrets regularly
- [ ] Use environment variables for all secrets
- [ ] Enable database connection encryption
- [ ] Implement API request signing for service-to-service calls
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable audit logging for sensitive operations
- [ ] Implement automated security scanning (SAST, DAST)
- [ ] Regular dependency updates and vulnerability scanning
