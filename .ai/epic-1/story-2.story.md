# Story 2: PostgreSQL Database Implementation

**Status: Draft**
**Type: Backend**
**Priority: High**
**Epic: 1 - Core Infrastructure**

## Objective
Implement the PostgreSQL database structure for OCR LAB, including all necessary tables for user management, file/folder metadata, and usage statistics.

## Background
The application requires a robust relational database to store user data, file metadata, and usage statistics. PostgreSQL was chosen for its reliability, JSONB support, and ability to handle complex queries efficiently.

## Acceptance Criteria
1. Database schema created with all necessary tables:
   - Users table (synced with Clerk)
   - Folders table (with nested folder support)
   - Files table (with metadata and processing status)
   - Usage statistics table
   - Processing queue status table

2. Basic CRUD operations implemented:
   - User management functions
   - Folder operations (create, read, update, delete)
   - File metadata operations
   - Usage tracking functions

3. Database indexes created for optimal performance:
   - Primary and foreign keys
   - Common query paths
   - Full-text search capabilities where needed

## Technical Details

### Database Schema

```sql
-- Users table (synced with Clerk)
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,  -- Clerk user ID
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- Folders table
CREATE TABLE folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES folders(id),
    user_id VARCHAR(255) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    path TEXT[] NOT NULL,
    UNIQUE (user_id, parent_id, name)
);

-- Files table
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    folder_id UUID REFERENCES folders(id),
    user_id VARCHAR(255) REFERENCES users(id),
    blob_path TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),
    status VARCHAR(50) NOT NULL,  -- pending, processing, completed, error
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Usage statistics table
CREATE TABLE usage_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) REFERENCES users(id),
    date DATE NOT NULL,
    pages_processed INTEGER DEFAULT 0,
    queries_made INTEGER DEFAULT 0,
    storage_bytes BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, date)
);

-- Processing queue table
CREATE TABLE processing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id),
    status VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Required Indexes

```sql
-- Folders indexes
CREATE INDEX idx_folders_user_id ON folders(user_id);
CREATE INDEX idx_folders_parent_id ON folders(parent_id);
CREATE INDEX idx_folders_path ON folders USING gin(path);

-- Files indexes
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_folder_id ON files(folder_id);
CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_files_metadata ON files USING gin(metadata);

-- Usage stats indexes
CREATE INDEX idx_usage_stats_user_id_date ON usage_stats(user_id, date);

-- Processing queue indexes
CREATE INDEX idx_processing_queue_status ON processing_queue(status);
CREATE INDEX idx_processing_queue_file_id ON processing_queue(file_id);
```

## Tasks
1. [ ] Set up PostgreSQL database in Azure
   - [ ] Create database instance
   - [ ] Configure basic networking
   - [ ] Set up basic logging

2. [ ] Create database models and schemas
   - [ ] Implement SQLAlchemy models
   - [ ] Add basic validation
   - [ ] Create database indexes

3. [ ] Create database access layer
   - [ ] Implement CRUD operations
   - [ ] Create helper functions

4. [ ] Write unit tests
   - [ ] Test database models
   - [ ] Test CRUD operations
   - [ ] Test error handling

5. [ ] Create documentation
   - [ ] Document schema design
   - [ ] Add API documentation
   - [ ] Include setup instructions

## Dependencies
- Azure PostgreSQL instance
- SQLAlchemy ORM
- psycopg2-binary for PostgreSQL adapter

## Risks and Mitigations
1. **Risk**: Performance bottlenecks
   - **Mitigation**: Proper indexing and monitoring from the start

## Notes
- Monitor query performance from the start
- Keep track of database size and growth rate

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Documentation updated
- [ ] Unit tests passing
- [ ] Performance tests completed 