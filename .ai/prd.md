# OCR LAB - Product Requirements Document (PRD)

**Status: Approved**

## Executive Summary

OCR LAB is a web application that performs advanced OCR extraction on PDF documents (including tables, images, and handwritten text) and then stores the extracted data in a vector database for semantic search and retrieval-augmented generation. It includes file/folder management, usage monitoring, and a simple REST API for querying relevant document chunks and optional pay-as-you-go billing.

## Problem Statement

Organizations and individuals struggle with extracting and searching through information locked in PDF documents, especially when those documents contain complex elements like tables, images, and handwritten text. Current solutions often:
- Fail to accurately extract structured data like tables
- Cannot process handwritten text effectively
- Don't provide semantic search capabilities
- Lack a simple API for integration with other systems

OCR LAB solves these problems by providing an end-to-end solution for PDF document processing, extraction, and semantic search.

## User Flow (Step-by-Step)

1. **Sign Up / Login**  
   - User registers for an account (via Clerk).  
   - On the first login, a default "Home" folder is created, or the user can create custom folders.
   - Authentication is handled securely through Clerk's authentication system.

2. **Create Folder & Upload PDFs**  
   - User clicks "Create Folder" to organize documents.
   - Folders can be nested for better organization.
   - User uploads one or multiple PDFs (up to 100MB per file).
   - Bulk upload is supported for efficiency.
   - Files enter a processing queue with status tracking.
   - Progress indicators show upload and processing status.

3. **OCR & Metadata Extraction (Asynchronous)**  
   - A Python microservice retrieves PDFs from Azure Blob Storage.
   - The service performs OCR using Azure Document Intelligence to extract:
     - Regular text with formatting preservation
     - Tables (converted to structured data)
     - Images (with content description)
     - Handwritten text
   - The system generates:
     - Document summaries
     - Keywords for improved search
     - JSON metadata for structured access
   - All text chunks and metadata are stored in:
     - **Postgres** for file metadata and usage stats.  
     - **Vector DB** (Azure AI Search) for semantic search.
   - Text is chunked appropriately for optimal vector search.

4. **View & Search Extracted Data**  
   - Once OCR completes, the file status changes to "Complete."
   - Users can browse files and see extracted content.
   - Users can query the data via:  
     - A basic search bar in the front-end with filters.
     - Advanced search options for metadata filtering.
     - A REST API with `POST {"query": "<question>", "n": 5}` for top-5 relevant chunks.
   - Search results highlight the matching text and provide context.

5. **Download & Delete**  
   - Users can download the original PDFs.
   - Users can delete a file, which removes:
     - The PDF from Azure Blob Storage
     - Its embeddings from the vector DB
     - All metadata from Postgres
   - Deletion is confirmed to prevent accidental data loss.

6. **Usage Tracking & Billing** (Optional, depending on user tier)  
   - The system logs:
     - Pages processed
     - Queries made
     - Storage used
   - A usage dashboard displays these metrics with charts and trends.
   - Pay-as-you-go billing is integrated via HitPay.
   - Usage limits can be set with notifications.

## Tech Stack & APIs

1. **Front-End:**  
   - **Vite** + React for fast development and optimal performance.
   - **shadcn/ui** for a responsive, minimal user interface.
   - **Clerk** for authentication and user management.
   - **TailwindCSS** for styling.
   - **React Query** for data fetching and state management.

2. **Back-End Services:**  
   - **Azure Blob Storage** for PDF file storage.  
   - **Azure Queue** for asynchronous OCR processing.  
   - **Azure Functions (Python)** to handle:
     - OCR extraction with Azure Document Intelligence.  
     - Summaries/keywords/metadata generation.  
     - Vector embeddings creation and storage.
   - **Postgres (Azure Postgres)** for:
     - User management
     - File/folder metadata
     - Usage statistics
     - Billing information

3. **Vector Database:**  
   - **Azure AI Search** for storing embeddings of text chunks.
   - Configured for semantic search with appropriate indexes.

4. **REST API:**  
   - A minimal set of endpoints including:
     - `POST /api/query` - Semantic search
     - `GET /api/files` - List files
     - `POST /api/files` - Upload files
     - `DELETE /api/files/{id}` - Delete files
     - `GET /api/folders` - List folders
     - `POST /api/folders` - Create folders
     - `DELETE /api/folders/{id}` - Delete folders
     - `GET /api/usage` - Get usage statistics

5. **Optional Services:**  
   - **HitPay** for payment processing.  
   - **Sentry** for error logging and monitoring.

## Core Features

1. **File & Folder Management**  
   - Create, list, and delete folders
   - Upload, list, and delete files
   - Organize documents in a hierarchical structure
   - Bulk operations for efficiency

2. **OCR Extraction (Advanced)**  
   - Extract text with formatting preservation
   - Extract tables as structured data
   - Extract and describe image content
   - Process handwritten text
   - Uses Azure Document Intelligence for high accuracy

3. **Document Summaries & Metadata**  
   - Generate concise document summaries
   - Extract keywords for improved search
   - Create structured JSON metadata
   - Include table/image data as text and JSON

4. **Vector Database Storage**  
   - Store text chunks with appropriate context
   - Create and store embeddings for semantic search
   - Link metadata to embeddings for rich results
   - Support for retrieval-augmented generation (RAG)

5. **Semantic Search & REST API**  
   - Natural language query processing
   - Return most relevant document chunks
   - Include context and metadata in results
   - Filter by file, folder, or metadata
   - Simple REST API for integration

6. **Usage Monitoring & Billing**  
   - Track pages processed
   - Track queries made
   - Monitor storage usage
   - Display usage metrics in dashboard
   - Support pay-as-you-go pricing
   - Integrate with HitPay for payments

7. **Compliance & Security**
   - API key authentication for external clients
   - Secure data storage and transmission
   - User data isolation
   - Audit logging for sensitive operations

## In-Scope vs. Out-of-Scope

**In-Scope**  
- **End-to-End OCR Pipeline** (including tables/images/handwriting)
- **Document Summaries, Keywords, JSON Metadata**
- **Folder & File Management** (create/delete folders, upload/delete files)
- **Storing and Indexing Extracted Data** in Postgres (metadata) + Vector DB (embeddings)
- **Simple REST API** for semantic search queries (top-n chunks)
- **Basic Dashboard** for usage (pages processed, queries made)
- **Basic Billing Integration** (HitPay) and usage-based pricing

**Out-of-Scope**  
- **Extensive Document Editing** (e.g., rewriting or rearranging extracted text in the UI)
- **Complex Role-Based Access Control** beyond basic user ownership
- **Granular Analytics** or advanced analytics dashboards
- **Large-Scale Real-Time Processing** for high-throughput OCR
- **Non-PDF Formats** (MVP is focused on PDFs only)
- **Heavy Customization of Summaries/Keywords**

## Task Sequence

1. **Project Setup and Infrastructure**
   - Set up development environment
   - Configure Azure resources
   - Set up database schema
   - Implement authentication

2. **Core Functionality Development**
   - Implement folder management
   - Implement file upload and storage
   - Develop OCR processing pipeline
   - Implement vector database integration

3. **User Interface Development**
   - Create responsive layout
   - Implement folder browsing interface
   - Develop file management UI
   - Create search interface

4. **API and Advanced Features**
   - Implement REST API endpoints
   - Develop usage tracking
   - Integrate billing (optional)

5. **Testing and Deployment**
   - Write and run tests
   - Deploy to production
   - Create documentation
   - Monitor and optimize

## Unknowns, Assumptions, and Risks

### Unknowns
- Exact performance characteristics of Azure Document Intelligence with complex documents
- Optimal chunking strategy for vector search
- User adoption and usage patterns

### Assumptions
- Users have PDF documents that require OCR and search
- Azure services will provide adequate performance and reliability
- The proposed tech stack will meet all requirements

### Risks
- Azure Document Intelligence may not handle all document types equally well
- Vector search performance may degrade with large document collections
- Integration between multiple Azure services may introduce complexity

## Success Metrics
- User adoption and retention
- Accuracy of OCR extraction
- Search result relevance
- System performance and reliability
- User satisfaction with the interface and features

## Timeline
- Phase 1 (Project Setup): 2 weeks
- Phase 2 (Core Functionality): 4 weeks
- Phase 3 (UI Development): 3 weeks
- Phase 4 (Advanced Features): 2 weeks
- Phase 5 (Testing and Deployment): 2 weeks

Total estimated time: 13 weeks 