# Implementation Plan: KTP Enterprise MVP Version 2

## Overview

This implementation plan transforms the existing Dev-Hive application into KTP Enterprise MVP Version 2, an enterprise-grade AI Knowledge Platform. The migration involves replacing Pinecone with PostgreSQL + pgvector, OpenAI with Groq LLaMA 3, and Streamlit with Next.js, while implementing comprehensive RBAC and team-based access control.

The implementation follows a bottom-up approach: database schema → backend services → frontend → integration → testing.

## Tasks

- [ ] 1. Database setup and schema creation
  - [-] 1.1 Set up PostgreSQL with pgvector extension
    - Install PostgreSQL 15+ and pgvector extension
    - Create database and enable vector extension
    - Configure connection pooling (pool size: 20)
    - _Requirements: 8.2, 20.6_
  
  - [~] 1.2 Create database schema with Alembic migrations
    - Initialize Alembic for migration management
    - Create teams table (id, name, created_at)
    - Create users table (id, email, password_hash, name, role, team_id, created_at, last_login)
    - Create documents table (id, filename, file_size, file_type, team_id, uploaded_by, upload_timestamp, processing_status, total_chunks)
    - Create chunks table with vector column (id, document_id, chunk_text, embedding vector(384), chunk_index, total_chunks, team_id, created_at)
    - Create query_logs table (id, user_id, query_text, results_count, timestamp)
    - Add foreign key constraints and check constraints
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.7_
  
  - [~] 1.3 Create database indexes for performance
    - Create indexes on users (email, team_id)
    - Create indexes on documents (team_id, uploaded_by)
    - Create indexes on chunks (document_id, team_id)
    - Create IVFFlat index on chunks.embedding for vector similarity search
    - Create indexes on query_logs (user_id, timestamp)
    - _Requirements: 8.4, 8.5, 20.3_
  
  - [~] 1.4 Write property test for foreign key integrity
    - **Property 46: Foreign Key Integrity**
    - **Validates: Requirements 14.7**

- [ ] 2. Authentication Service implementation
  - [ ] 2.1 Implement password hashing and verification
    - Create hash_password() function using bcrypt with cost factor 12
    - Create verify_password() function for password verification
    - _Requirements: 1.1, 15.1_
  
  - [ ] 2.2 Write property test for password security
    - **Property 1: Password Security**
    - **Validates: Requirements 1.1, 15.1**
  
  - [ ] 2.3 Implement JWT token generation and validation
    - Create create_access_token() function with 24-hour expiration
    - Create verify_token() function for JWT validation
    - Include user_id, role, and team_id in JWT claims
    - _Requirements: 1.2, 1.5_
  
  - [ ] 2.4 Write property tests for JWT functionality
    - **Property 2: JWT Token Claims**
    - **Property 5: JWT Expiration**
    - **Validates: Requirements 1.2, 1.5**
  
  - [ ] 2.5 Implement user registration endpoint
    - Create POST /api/auth/register endpoint
    - Validate email format and password complexity
    - Hash password and store user in database
    - Assign user to team
    - _Requirements: 1.1, 1.4, 2.1, 3.1_
  
  - [ ] 2.6 Write property tests for registration
    - **Property 4: Password Complexity Enforcement**
    - **Property 7: Role Assignment**
    - **Property 12: User Team Assignment**
    - **Validates: Requirements 1.4, 2.1, 3.1**
  
  - [ ] 2.7 Implement user login endpoint
    - Create POST /api/auth/login endpoint
    - Verify credentials and generate JWT token
    - Update last_login timestamp
    - Return token and user information
    - _Requirements: 1.2, 1.3_
  
  - [ ] 2.8 Write property tests for login
    - **Property 2: JWT Token Claims**
    - **Property 3: Invalid Credentials Rejection**
    - **Validates: Requirements 1.2, 1.3**
  
  - [ ] 2.9 Implement authentication middleware
    - Create JWT verification middleware for protected endpoints
    - Extract user information from token
    - Reject requests with missing, expired, or invalid tokens
    - _Requirements: 1.6, 15.4_
  
  - [ ] 2.10 Write property test for authentication enforcement
    - **Property 6: Authentication Enforcement**
    - **Validates: Requirements 1.6, 15.4**
  
  - [ ] 2.11 Implement RBAC authorization middleware
    - Create check_permission() function for role-based access
    - Implement permission decorators for endpoints
    - Define permission matrix (Admin, Contributor, Viewer)
    - _Requirements: 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 2.12 Write property tests for RBAC
    - **Property 8: Admin Authorization**
    - **Property 9: Contributor Upload Authorization**
    - **Property 10: Viewer Upload Restriction**
    - **Property 11: Non-Admin Management Restriction**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5**
  
  - [ ] 2.13 Implement GET /api/auth/me endpoint
    - Return current user information from JWT token
    - _Requirements: 1.2_

- [ ] 3. Checkpoint - Ensure authentication tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Text extraction and preprocessing
  - [ ] 4.1 Implement PDF text extraction
    - Create extract_pdf() function using PyPDF2
    - Preserve paragraph structure
    - Handle extraction errors gracefully
    - _Requirements: 5.1, 5.5_
  
  - [ ] 4.2 Implement DOCX text extraction
    - Create extract_docx() function using python-docx
    - Extract headers and body text
    - Handle extraction errors gracefully
    - _Requirements: 5.2, 5.5_
  
  - [ ] 4.3 Implement TXT text extraction
    - Create extract_txt() function with UTF-8 encoding
    - Handle encoding errors gracefully
    - _Requirements: 5.3_
  
  - [ ] 4.4 Write property test for UTF-8 text handling
    - **Property 20: UTF-8 Text Handling**
    - **Validates: Requirements 5.3, 5.6**
  
  - [ ] 4.5 Implement text preprocessing
    - Create clean_text() function
    - Remove excessive whitespace
    - Normalize line breaks
    - Handle special characters and non-ASCII text
    - _Requirements: 5.4, 5.6_
  
  - [ ] 4.6 Write property test for whitespace normalization
    - **Property 21: Whitespace Normalization**
    - **Validates: Requirements 5.4**

- [ ] 5. Text chunking implementation
  - [ ] 5.1 Implement text chunking with sentence boundaries
    - Create chunk_text() function
    - Use NLTK sentence tokenizer for sentence boundaries
    - Implement maximum 512 token limit per chunk
    - Create 50-token overlap between consecutive chunks
    - Include chunk metadata (chunk_index, total_chunks)
    - _Requirements: 6.1, 6.2, 6.4, 6.5_
  
  - [ ] 5.2 Write property tests for chunking
    - **Property 22: Maximum Chunk Size**
    - **Property 23: Sentence Boundary Preservation**
    - **Property 24: Chunk Overlap**
    - **Validates: Requirements 6.1, 6.2, 6.4**

- [ ] 6. Embedding generation implementation
  - [ ] 6.1 Initialize SentenceTransformer model
    - Load BAAI/bge-small-en-v1.5 model
    - Configure for local inference (no external API)
    - _Requirements: 7.1, 7.5_
  
  - [ ] 6.2 Implement embedding generation with batching
    - Create generate_embeddings() function
    - Process chunks in batches of 32
    - Normalize embeddings to unit length
    - Handle generation failures with retry logic (3 attempts)
    - _Requirements: 7.1, 7.3, 7.4, 7.6, 20.1_
  
  - [ ] 6.3 Write property tests for embeddings
    - **Property 26: Embedding Generation**
    - **Property 27: Embedding Dimensionality**
    - **Property 28: Embedding Normalization**
    - **Property 54: Batch Embedding Generation**
    - **Validates: Requirements 7.1, 7.2, 7.3, 20.1**

- [ ] 7. Ingestion Service implementation
  - [ ] 7.1 Implement file upload validation
    - Validate file format (PDF, DOCX, TXT only)
    - Validate file size (max 50MB)
    - Return descriptive errors for invalid uploads
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ] 7.2 Write property tests for file validation
    - **Property 16: Supported File Format Acceptance**
    - **Property 17: Unsupported File Format Rejection**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ] 7.3 Implement document upload endpoint
    - Create POST /api/ingest/upload endpoint
    - Accept multipart/form-data file uploads
    - Store original filename and upload timestamp
    - Associate document with uploader's team
    - Return unique document_id
    - _Requirements: 4.4, 4.5, 3.2_
  
  - [ ] 7.4 Write property tests for document upload
    - **Property 18: Unique Document Identifiers**
    - **Property 19: Document Metadata Storage**
    - **Property 13: Document Team Association**
    - **Validates: Requirements 4.4, 4.5, 3.2**
  
  - [ ] 7.5 Implement end-to-end ingestion pipeline
    - Create process_document() orchestration function
    - Extract text based on file type
    - Clean and preprocess text
    - Chunk text with overlap
    - Generate embeddings in batches
    - Store chunks with embeddings in database
    - Implement atomic transaction (all-or-nothing)
    - Return processing results (chunks_created count)
    - _Requirements: 18.1, 18.2, 18.3_
  
  - [ ] 7.6 Write property tests for ingestion workflow
    - **Property 25: Chunk Metadata Completeness**
    - **Property 30: Atomic Chunk Storage**
    - **Property 52: End-to-End Upload Workflow**
    - **Property 53: Upload Workflow Rollback**
    - **Validates: Requirements 6.5, 6.6, 8.3, 8.6, 18.1, 18.2, 18.3**
  
  - [ ] 7.7 Implement document status endpoint
    - Create GET /api/ingest/status/{document_id} endpoint
    - Return processing status and progress
    - _Requirements: 18.5_
  
  - [ ] 7.8 Write property test for embedding storage
    - **Property 29: Embedding Storage Round-Trip**
    - **Validates: Requirements 8.1**

- [ ] 8. Checkpoint - Ensure ingestion tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Search Service implementation
  - [ ] 9.1 Implement query embedding generation
    - Create generate_query_embedding() function
    - Use same SentenceTransformer model as document embeddings
    - Normalize query embedding to unit length
    - _Requirements: 9.1, 9.2_
  
  - [ ] 9.2 Write property tests for query embeddings
    - **Property 31: Query Embedding Generation**
    - **Property 32: Query Embedding Normalization**
    - **Validates: Requirements 9.1, 9.2**
  
  - [ ] 9.3 Implement vector similarity search
    - Create vector_search() function using pgvector
    - Use cosine similarity (not Euclidean distance)
    - Filter results by user's team_id
    - Apply minimum similarity threshold (0.3)
    - Return top 5 results ranked by similarity
    - Include all required fields in results
    - _Requirements: 9.3, 9.4, 9.5, 9.6, 9.7, 3.3_
  
  - [ ] 9.4 Write property tests for search
    - **Property 14: Search Team Isolation**
    - **Property 33: Cosine Similarity Search**
    - **Property 34: Top-K Results**
    - **Property 35: Similarity Threshold**
    - **Property 36: Search Result Completeness**
    - **Property 37: Result Ranking**
    - **Property 38: Document Context in Results**
    - **Validates: Requirements 3.3, 9.3, 9.4, 9.5, 9.6, 9.7, 19.1, 19.3**
  
  - [ ] 9.4 Implement query logging
    - Log all queries with user_id, query_text, timestamp, results_count
    - Handle logging failures gracefully (don't block query)
    - _Requirements: 11.1, 11.3_
  
  - [ ] 9.5 Write property test for query logging
    - **Property 41: Query Log Completeness**
    - **Validates: Requirements 11.1**

- [ ] 10. AI Service implementation
  - [ ] 10.1 Initialize Groq client
    - Configure Groq API client with API key
    - Set model to llama3-70b-8192
    - Configure 30-second timeout
    - _Requirements: 10.2, 10.7_
  
  - [ ] 10.2 Implement prompt construction
    - Create construct_prompt() function
    - Include user query and retrieved context chunks
    - Format with clear structure and source references
    - _Requirements: 10.1_
  
  - [ ] 10.3 Write property test for prompt construction
    - **Property 39: Prompt Construction**
    - **Validates: Requirements 10.1**
  
  - [ ] 10.4 Implement LLM answer generation
    - Create generate_answer() function
    - Call Groq API with constructed prompt
    - Implement retry logic (2 retries with exponential backoff)
    - Implement circuit breaker (5 consecutive failures)
    - Parse response into structured format (answer, sources)
    - Handle API failures gracefully
    - _Requirements: 10.2, 10.3, 10.4, 10.5, 10.6, 16.6_
  
  - [ ] 10.5 Write property test for response structure
    - **Property 40: Structured Response Format**
    - **Validates: Requirements 10.3, 10.4**
  
  - [ ] 10.6 Implement POST /api/ai/generate-answer endpoint
    - Accept query and context chunks
    - Generate answer using LLM
    - Return structured response with sources
    - _Requirements: 10.1, 10.3, 10.4_

- [ ] 11. Unified search endpoint implementation
  - [ ] 11.1 Implement POST /api/search/query endpoint
    - Accept search query from user
    - Generate query embedding
    - Perform vector similarity search with team filtering
    - Pass top results to AI service for answer generation
    - Log query
    - Return search results with AI-generated answer
    - _Requirements: 9.1, 9.3, 9.4, 9.5, 10.1, 11.1_

- [ ] 12. Admin endpoints implementation
  - [ ] 12.1 Implement user management endpoints
    - Create GET /api/admin/users endpoint (list users)
    - Create POST /api/admin/users endpoint (create user)
    - Create PUT /api/admin/users/{id} endpoint (update user)
    - Create DELETE /api/admin/users/{id} endpoint (delete user)
    - Require Admin role for all endpoints
    - _Requirements: 2.2, 2.5_
  
  - [ ] 12.2 Implement query logs endpoint
    - Create GET /api/admin/logs endpoint
    - Support filtering by date range and user_id
    - Require Admin role
    - _Requirements: 11.5_
  
  - [ ] 12.3 Write property test for query log filtering
    - **Property 42: Query Log Filtering**
    - **Validates: Requirements 11.5**

- [ ] 13. API middleware and error handling
  - [ ] 13.1 Implement request validation middleware
    - Use Pydantic models for request schema validation
    - Return 400 with field-level errors for invalid requests
    - _Requirements: 13.4, 16.2_
  
  - [ ] 13.2 Write property tests for validation
    - **Property 43: Request Validation**
    - **Property 50: Validation Error Handling**
    - **Validates: Requirements 13.4, 16.2**
  
  - [ ] 13.3 Implement error handling middleware
    - Catch all exceptions and return consistent error format
    - Return 500 for unexpected errors with generic message
    - Return 503 for external service failures
    - Log all errors with stack traces
    - Exclude sensitive data from logs
    - _Requirements: 16.1, 16.3, 16.4, 15.5_
  
  - [ ] 13.4 Write property tests for error handling
    - **Property 44: Consistent Error Format**
    - **Property 48: Sensitive Data Exclusion from Logs**
    - **Property 49: Unexpected Error Handling**
    - **Property 51: Error Logging with Stack Traces**
    - **Validates: Requirements 13.5, 15.5, 16.1, 16.4**
  
  - [ ] 13.5 Implement request logging middleware
    - Log all API requests with timestamp, endpoint, user_id, status
    - Use structured JSON logging format
    - _Requirements: 13.7_
  
  - [ ] 13.6 Write property test for request logging
    - **Property 45: Request Logging**
    - **Validates: Requirements 13.7**
  
  - [ ] 13.7 Implement CORS middleware
    - Configure allowed origins from environment variable
    - Set appropriate CORS headers
    - _Requirements: 13.6_
  
  - [ ] 13.8 Implement rate limiting middleware
    - Add rate limiting to authentication endpoints (5 attempts/minute/IP)
    - Return 429 when rate limit exceeded
    - _Requirements: 15.7_
  
  - [ ] 13.9 Implement health check endpoints
    - Create GET /health endpoint (basic health)
    - Create GET /health/db endpoint (database connectivity)
    - _Requirements: 13.3_

- [ ] 14. Security hardening
  - [ ] 14.1 Write property test for SQL injection prevention
    - **Property 47: SQL Injection Prevention**
    - **Validates: Requirements 15.3**
  
  - [ ] 14.2 Write unit tests for security features
    - Test expired JWT token rejection
    - Test rate limiting enforcement
    - Test CORS configuration
    - _Requirements: 15.6, 15.7, 13.6_

- [ ] 15. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Frontend project setup
  - [ ] 16.1 Initialize Next.js project with TypeScript
    - Create Next.js 14 project with App Router
    - Configure TypeScript
    - Install and configure Tailwind CSS
    - Set up project structure (pages, components, lib, hooks)
    - _Requirements: 12.9_
  
  - [ ] 16.2 Set up API client and state management
    - Install Axios for API calls
    - Install React Query for server state management
    - Create API client with base URL configuration
    - Implement request/response interceptors for JWT tokens
    - _Requirements: 12.1, 12.2_
  
  - [ ] 16.3 Create authentication context
    - Implement useAuth hook
    - Store JWT token in localStorage
    - Provide login, logout, and user state
    - _Requirements: 12.1, 12.2_

- [ ] 17. Frontend authentication pages
  - [ ] 17.1 Implement login page
    - Create login form with email and password fields
    - Validate inputs client-side
    - Call POST /api/auth/login on submit
    - Store JWT token and redirect to dashboard on success
    - Display error messages on failure
    - _Requirements: 12.1, 12.7_
  
  - [ ] 17.2 Implement registration page
    - Create registration form with email, password, name fields
    - Validate password complexity client-side
    - Call POST /api/auth/register on submit
    - Redirect to login on success
    - Display error messages on failure
    - _Requirements: 12.1, 12.7_
  
  - [ ] 17.3 Implement protected route wrapper
    - Create ProtectedRoute component
    - Check authentication status
    - Redirect to login if not authenticated
    - _Requirements: 12.1_

- [ ] 18. Frontend dashboard and navigation
  - [ ] 18.1 Implement dashboard layout
    - Create navigation bar with user info and logout button
    - Display available actions based on user role
    - Show upload and search options
    - _Requirements: 12.2_
  
  - [ ] 18.2 Implement role-based UI rendering
    - Show admin panel link for Admin users only
    - Show upload button for Admin and Contributor users only
    - Show search interface for all authenticated users
    - _Requirements: 12.2_

- [ ] 19. Frontend document upload interface
  - [ ] 19.1 Implement file upload component
    - Create drag-and-drop file upload area
    - Validate file format and size client-side
    - Display file preview before upload
    - _Requirements: 12.3_
  
  - [ ] 19.2 Implement upload progress and status
    - Show upload progress bar
    - Display processing status (uploading, processing, completed)
    - Poll GET /api/ingest/status/{document_id} for status updates
    - Show success message with chunks created count
    - Display error messages on failure
    - _Requirements: 12.4, 12.7, 18.5, 18.6_

- [ ] 20. Frontend search interface
  - [ ] 20.1 Implement search component
    - Create search input field and search button
    - Call POST /api/search/query on submit
    - Display loading state during search
    - _Requirements: 12.5_
  
  - [ ] 20.2 Implement search results display
    - Display AI-generated answer prominently at top
    - Show source references below answer
    - Display individual chunk results with similarity scores
    - Show document names and chunk positions
    - Handle empty results gracefully
    - _Requirements: 12.6, 12.7_

- [ ] 21. Frontend admin panel
  - [ ] 21.1 Implement user management interface
    - Create user list table
    - Implement create user form
    - Implement edit user form
    - Implement delete user confirmation
    - Restrict access to Admin role only
    - _Requirements: 2.2_
  
  - [ ] 21.2 Implement query logs interface
    - Create query logs table
    - Implement date range filter
    - Implement user filter
    - Display query text, user, and timestamp
    - Restrict access to Admin role only
    - _Requirements: 11.5_

- [ ] 22. Frontend styling and responsiveness
  - [ ] 22.1 Apply Tailwind CSS styling
    - Style all components with Tailwind classes
    - Ensure consistent color scheme and spacing
    - Implement hover and focus states
    - _Requirements: 12.9_
  
  - [ ] 22.2 Implement responsive design
    - Test on desktop viewports (1920px, 1440px, 1024px)
    - Test on tablet viewports (768px)
    - Adjust layouts for smaller screens
    - _Requirements: 12.8_

- [ ] 23. Frontend error handling
  - [ ] 23.1 Write unit tests for frontend components
    - Test login form validation
    - Test registration form validation
    - Test file upload validation
    - Test search input validation
    - Test error message display
    - _Requirements: 12.7_

- [ ] 24. Checkpoint - Ensure frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 25. Environment configuration
  - [ ] 25.1 Create environment configuration files
    - Create .env.example with all required variables
    - Document each environment variable
    - Create separate .env files for development, staging, production
    - _Requirements: 17.1, 17.2, 17.4_
  
  - [ ] 25.2 Implement configuration validation
    - Check for required environment variables on startup
    - Fail with clear error message if variables missing
    - _Requirements: 17.2, 17.3_

- [ ] 26. Docker containerization
  - [~] 26.1 Create backend Dockerfile
    - Use Python 3.11 slim base image
    - Install dependencies from requirements.txt
    - Pre-download SentenceTransformer model
    - Copy application code
    - Set up entrypoint with migrations and server start
    - _Requirements: 18.1_
  
  - [~] 26.2 Create frontend Dockerfile
    - Use Node 18 alpine base image
    - Install dependencies
    - Build Next.js application
    - Set up entrypoint to start server
    - _Requirements: 12.1_
  
  - [~] 26.3 Create docker-compose.yml
    - Define PostgreSQL service with pgvector
    - Define backend service with environment variables
    - Define frontend service with API URL
    - Set up volume for PostgreSQL data persistence
    - Configure service dependencies
    - _Requirements: 8.1, 8.2_

- [ ] 27. Integration testing
  - [~] 27.1 Write integration tests for authentication flow
    - Test registration → login → access protected endpoint
    - Test invalid credentials rejection
    - Test expired token handling
    - _Requirements: 1.1, 1.2, 1.3, 1.6_
  
  - [~] 27.2 Write integration tests for upload workflow
    - Test file upload → extraction → chunking → embedding → storage
    - Test upload with different file formats (PDF, DOCX, TXT)
    - Test upload failure rollback
    - Test team association
    - _Requirements: 4.1, 18.1, 18.2, 3.2_
  
  - [~] 27.3 Write integration tests for search workflow
    - Test query → embedding → vector search → answer generation
    - Test team isolation (users only see their team's documents)
    - Test empty results handling
    - _Requirements: 9.1, 9.3, 9.4, 10.1, 3.3_
  
  - [~] 27.4 Write integration tests for RBAC
    - Test Admin can manage users
    - Test Contributor can upload documents
    - Test Viewer cannot upload documents
    - Test non-Admin cannot manage users
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [ ] 28. End-to-end testing
  - [~] 28.1 Write E2E tests for user journeys
    - Test complete user registration and login flow
    - Test document upload and search flow
    - Test admin user management flow
    - Use Playwright or Cypress for browser automation
    - _Requirements: 12.1, 12.2, 12.3, 12.5, 12.6_

- [ ] 29. Performance testing
  - [~] 29.1 Write performance tests
    - Test search latency (target: 95th percentile < 2 seconds)
    - Test concurrent uploads (10 documents simultaneously)
    - Test concurrent searches (50 users simultaneously)
    - Test large file handling (50MB files)
    - _Requirements: 20.2, 20.4_

- [ ] 30. Security testing
  - [~] 30.1 Write security tests
    - Test SQL injection attempts on all input fields
    - Test JWT token tampering
    - Test cross-team data access attempts
    - Test rate limiting on auth endpoints
    - Test CORS configuration
    - _Requirements: 15.3, 15.4, 3.3, 15.7, 13.6_

- [ ] 31. Documentation
  - [~] 31.1 Create API documentation
    - Document all API endpoints with request/response examples
    - Include authentication requirements
    - Include error response formats
    - Use OpenAPI/Swagger specification
    - _Requirements: 13.1, 13.5_
  
  - [~] 31.2 Create deployment documentation
    - Document environment variables
    - Document database setup and migrations
    - Document Docker deployment steps
    - Document monitoring and health checks
    - _Requirements: 17.1, 17.2, 17.4_
  
  - [~] 31.3 Create user documentation
    - Document user registration and login
    - Document document upload process
    - Document search functionality
    - Document admin features
    - _Requirements: 12.1, 12.3, 12.5_

- [ ] 32. Final checkpoint - Complete system verification
  - Run all tests (unit, property, integration, E2E)
  - Verify all 54 correctness properties pass
  - Test complete user workflows
  - Verify security hardening checklist
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties (100 iterations each)
- Unit tests validate specific examples, edge cases, and error conditions
- Integration tests validate component interactions
- E2E tests validate complete user workflows
- The implementation follows a bottom-up approach: database → backend → frontend → integration
- Checkpoints ensure incremental validation at key milestones
- All 54 correctness properties from the design document are implemented as property-based tests
- Team isolation is critical for security and must be thoroughly tested
- The migration preserves core functionality while modernizing the architecture
