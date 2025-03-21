# Story 2: PostgreSQL Database Implementation

**Status: In Progress**
**Type: Backend**
**Priority: High**
**Epic: 1 - Core Infrastructure**

## Objective
Implement the PostgreSQL database structure for OCR LAB, including all necessary tables for user management, file/folder metadata, and usage statistics.

## Background
The application requires a robust relational database to store user data, file metadata, and usage statistics. PostgreSQL was chosen for its reliability, JSONB support, and ability to handle complex queries efficiently.

## Acceptance Criteria
1. ✅ Database schema created with all necessary tables:
   - Users table (synced with Clerk)
   - Folders table (with nested folder support)
   - Files table (with metadata and processing status)
   - Usage statistics table

2. ✅ Basic CRUD operations implemented:
   - User management functions
   - Folder operations (create, read, update, delete)
   - File metadata operations
   - Usage tracking functions

3. ✅ Database indexes created for optimal performance:
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
    id INTEGER PRIMARY KEY DEFAULT nextval('folders_id_seq'::regclass),
    name VARCHAR(255) NOT NULL,
    parent_id INTEGER REFERENCES folders(id),
    user_id VARCHAR(255) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    path TEXT[] NOT NULL,
    UNIQUE (user_id, name, parent_id)
);

-- Files table
CREATE TABLE files (
    id INTEGER PRIMARY KEY DEFAULT nextval('files_id_seq'::regclass),
    name VARCHAR(255) NOT NULL,
    folder_id INTEGER REFERENCES folders(id) ON DELETE CASCADE,
    user_id VARCHAR(255) REFERENCES users(id),
    blob_path TEXT NOT NULL,
    size_bytes BIGINT,
    mime_type VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
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
```

## Tasks
1. [x] Set up PostgreSQL database in Azure
   - [x] Create database instance
   - [x] Configure basic networking
   - [x] Set up basic logging

2. [x] Create database models and schemas
   - [x] Implement tables according to schema
   - [x] Add basic validation through constraints
   - [x] Create database indexes

3. [x] Create database access layer
   - [x] Implement CRUD operations
   - [x] Create helper functions

4. [x] Write unit tests
   - [x] Test database models
   - [x] Test CRUD operations
   - [x] Test error handling

5. [x] Create documentation
   - [x] Document schema design
   - [x] Document API access patterns
   - [x] Include setup instructions

## Dependencies
- Azure PostgreSQL instance
- SQLAlchemy ORM
- psycopg2-binary for PostgreSQL adapter

## Risks and Mitigations
1. **Risk**: Performance bottlenecks
   - **Mitigation**: Proper indexing and monitoring from the start

## Notes
- Database connection is available at: pltest.postgres.database.azure.com
- User: adminn
- Database: postgres
- Database functionality integrated with API endpoints in function_app.py
- Database schema includes proper foreign key relationships and indexes for optimal query performance

## Definition of Done
- [x] All tasks completed and tested
- [x] Documentation updated
- [x] Unit tests passing
- [x] Performance tests completed 

## Implementation Notes
- The original schema used UUIDs for primary keys, but the current implementation uses integer IDs for folders and files
- Added CASCADE deletion for files when parent folders are deleted
- Database schema created on July 18, 2024
- CRUD operations implemented and tested
- Full database integration with API endpoints completed on July 18, 2024 