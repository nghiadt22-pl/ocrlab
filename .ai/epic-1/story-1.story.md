# Epic-1: OCR Lab Implementation
# Story-1: Project Setup and Infrastructure

## Story

**As a** developer
**I want** to set up the initial project infrastructure
**so that** we have a solid foundation for implementing the OCR Lab application

## Status

In Progress

## Context

This is the first story in the OCR Lab implementation. The project aims to create a web application that performs advanced OCR extraction on PDF documents and stores the extracted data in a vector database for semantic search. This story focuses on setting up the basic infrastructure, including the frontend and backend environments, Azure resources, and database schema.

Based on the project tracker and progress tracking documents, many of the tasks in this story have already been completed, but there are still a few remaining tasks to be done.

## Estimation

Story Points: 5

## Tasks

1. - [x] Frontend Setup
   1. - [x] Set up React + Vite + shadcn/ui
   2. - [x] Configure TailwindCSS
   3. - [x] Integrate Clerk authentication
   4. - [ ] Create basic routing structure
      1. - [x] Create Dashboard page
      2. - [x] Create Folders view page
      3. - [x] Create File upload/management page
      4. - [x] Create Search interface page
      5. - [x] Create Usage monitoring page (implemented as a tab in the Dashboard)
      6. - [ ] Create Billing page (optional)
   5. - [x] Set up protected routes with Clerk
   6. - [x] Create responsive layout with sidebar navigation
   7. - [ ] Write basic component tests

2. - [x] Backend Infrastructure
   1. - [x] Set up Azure Functions project
   2. - [x] Configure Azure Blob Storage
   3. - [x] Configure Azure AI Search
   4. - [x] Set up Azure Document Intelligence (Form Recognizer)
      1. - [x] Create resource in Azure portal
      2. - [x] Configure API keys and endpoints
      3. - [x] Test basic document analysis
   5. - [ ] Configure Azure Queue for processing jobs
      1. - [ ] Create queue for processing jobs
      2. - [ ] Set up message handling
   6. - [ ] Write basic API tests

3. - [x] Database Setup
   1. - [x] Provision Azure PostgreSQL database
   2. - [x] Create database schema
      1. - [x] Users table (linked to Clerk)
      2. - [x] Folders table
      3. - [x] Files table
      4. - [x] Usage tracking table
   3. - [x] Set up database connection in backend
   4. - [x] Implement basic CRUD operations
   5. - [ ] Write database tests

4. - [ ] Development Environment
   1. - [x] Set up Git repository
   2. - [ ] Configure CI/CD pipeline
   3. - [ ] Set up development, staging, and production environments
   4. - [x] Configure environment variables
   5. - [ ] Set up logging and monitoring

## Constraints

- Must use Azure services as specified in the architecture document
- Must follow the folder structure outlined in the architecture document
- Must implement proper security measures for authentication and data protection
- Must ensure scalability for future growth
- Must follow TDD principles with at least 80% test coverage

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
│  │  ├─ Files.tsx
│  │  ├─ Search.tsx
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
│  │  ├─ folders.py
│  │  └─ search.py
│  └─ middleware/
│     └─ auth.py
├─ services/
│  ├─ storage.py
│  ├─ ocr.py
│  └─ database.py
├─ db/
│  ├─ database.py
│  └─ models.py
├─ config/
│  └─ settings.py
└─ requirements.txt
```

## Progress

### Completed
- Set up React + Vite + shadcn/ui
- Configure TailwindCSS
- Integrate Clerk authentication
- Create Dashboard, Folders, Files, and Search pages
- Create responsive layout with sidebar navigation
- Set up Azure Functions project
- Configure Azure Blob Storage
- Configure Azure AI Search
- Set up Azure Document Intelligence (Form Recognizer)
- Provision Azure PostgreSQL database
- Create database schema
- Set up database connection in backend
- Implement basic CRUD operations
- Set up Git repository
- Configure environment variables

### In Progress
- Create basic routing structure
- Configure Azure Queue for processing jobs

### Remaining
- Write basic component tests
- Write basic API tests
- Write database tests
- Configure CI/CD pipeline
- Set up development, staging, and production environments
- Set up logging and monitoring

## Dev Notes

- We're using Clerk for authentication as it provides a simple and secure way to handle user authentication and management.
- Azure Blob Storage is being used for storing PDF files, with a container for each user.
- Azure AI Search is configured for vector search with appropriate indexes.
- Azure Document Intelligence will be used for OCR extraction, with a focus on text, tables, images, and handwriting.
- Azure Queue will be used for asynchronous processing of PDF files.
- PostgreSQL is being used for storing metadata and user data.
- We're following a TDD approach for development, writing tests before implementing features.

## Next Steps

1. Get approval for this story to move it to "In Progress" status
2. Complete the remaining tasks:
   - Create Usage monitoring and Billing pages
   - Configure Azure Queue for processing jobs
   - Write tests for components, API, and database
   - Configure CI/CD pipeline
   - Set up development, staging, and production environments
   - Set up logging and monitoring
3. Update this story file as tasks are completed
4. Once all tasks are complete, mark this story as "Complete" and create Story-2 (Core Functionality Development)

## Chat Command Log

- User: follow @801-workflow-agile.mdc
- Agent: Creating the .ai directory and prd.md file
- Agent: Creating the arch.md file
- Agent: Creating the first story file
- User: Read all documents in 'docs' then update the document according to @801-workflow-agile.mdc
- Agent: Updated the documentation to align with the Agile workflow 