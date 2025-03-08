# Epic-1: OCR Lab Implementation
# Story-1: Project Setup and Infrastructure

## Story

**As a** developer
**I want** to set up the initial project infrastructure
**so that** we have a solid foundation for implementing the OCR Lab application

## Status

Draft

## Context

This is the first story in the OCR Lab implementation. The project aims to create a web application that performs advanced OCR extraction on PDF documents and stores the extracted data in a vector database for semantic search. This story focuses on setting up the basic infrastructure, including the frontend and backend environments, Azure resources, and database schema.

Based on the project tracker and progress tracking documents, some of the tasks in this story have already been completed, but we'll include them for completeness and tracking purposes.

## Estimation

Story Points: 5

## Tasks

1. - [ ] Frontend Setup
   1. - [ ] Set up React + Vite + shadcn/ui
   2. - [ ] Configure TailwindCSS
   3. - [ ] Integrate Clerk authentication
   4. - [ ] Create basic routing structure
   5. - [ ] Set up protected routes with Clerk
   6. - [ ] Create responsive layout with sidebar navigation
   7. - [ ] Write basic component tests

2. - [ ] Backend Infrastructure
   1. - [ ] Set up Azure Functions project
   2. - [ ] Configure Azure Blob Storage
   3. - [ ] Configure Azure AI Search
   4. - [ ] Set up Azure Document Intelligence (Form Recognizer)
   5. - [ ] Configure Azure Queue for processing jobs
   6. - [ ] Set up message handling for the queue
   7. - [ ] Write basic API tests

3. - [ ] Database Setup
   1. - [ ] Provision Azure PostgreSQL database
   2. - [ ] Create database schema
      1. - [ ] Users table (linked to Clerk)
      2. - [ ] Folders table
      3. - [ ] Files table
      4. - [ ] Usage tracking table
   3. - [ ] Set up database connection in backend
   4. - [ ] Implement basic CRUD operations
   5. - [ ] Write database tests

4. - [ ] Development Environment
   1. - [ ] Set up Git repository
   2. - [ ] Configure CI/CD pipeline
   3. - [ ] Set up development, staging, and production environments
   4. - [ ] Configure environment variables
   5. - [ ] Set up logging and monitoring

## Constraints

- Must use Azure services as specified in the architecture document
- Must follow the folder structure outlined in the architecture document
- Must implement proper security measures for authentication and data protection
- Must ensure scalability for future growth

## Data Models / Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Folders Table
```sql
CREATE TABLE folders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Files Table
```sql
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    folder_id INTEGER NOT NULL,
    blob_url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'uploading',
    size_bytes BIGINT NOT NULL,
    content_type VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
);
```

### Usage Table
```sql
CREATE TABLE usage (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    pages_processed INTEGER DEFAULT 0,
    queries_made INTEGER DEFAULT 0,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Structure

### Frontend Structure
```
frontend/
├─ src/
│  ├─ components/
│  │  ├─ layout/
│  │  │  ├─ Sidebar.tsx
│  │  │  ├─ Header.tsx
│  │  │  └─ Layout.tsx
│  │  └─ ui/
│  │     └─ (shadcn components)
│  ├─ pages/
│  │  ├─ Dashboard.tsx
│  │  ├─ Folders.tsx
│  │  └─ Login.tsx
│  ├─ hooks/
│  │  └─ useAuth.ts
│  ├─ services/
│  │  └─ api.ts
│  ├─ App.tsx
│  └─ main.tsx
├─ public/
│  └─ index.html
└─ package.json
```

### Backend Structure
```
backend/
├─ api/
│  ├─ routes/
│  │  ├─ files.py
│  │  └─ folders.py
│  └─ middleware/
│     └─ auth.py
├─ services/
│  ├─ storage.py
│  └─ database.py
├─ db/
│  ├─ database.py
│  └─ models.py
├─ config/
│  └─ settings.py
└─ requirements.txt
```

## Dev Notes

- We'll use Clerk for authentication as it provides a simple and secure way to handle user authentication and management.
- Azure Blob Storage will be used for storing PDF files, with a container for each user.
- Azure AI Search will be configured for vector search with appropriate indexes.
- Azure Document Intelligence will be used for OCR extraction, with a focus on text, tables, images, and handwriting.
- Azure Queue will be used for asynchronous processing of PDF files.
- PostgreSQL will be used for storing metadata and user data.
- We'll follow a TDD approach for development, writing tests before implementing features.

## Chat Command Log

- User: follow @801-workflow-agile.mdc
- Agent: Creating the .ai directory and prd.md file
- Agent: Creating the arch.md file
- Agent: Creating the first story file 