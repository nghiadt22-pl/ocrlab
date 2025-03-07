# Unified System Architecture

## Overview
The Document Intelligence application is a cloud-based document processing system built on Azure services. It provides OCR capabilities, document storage, and semantic search functionality through a modern web interface.

## System Overview
The application allows users to upload PDF documents for processing using Azure AI Document Intelligence. The application extracts text, tables, figures, and handwriting from documents, and indexes this content in Azure AI Search for future retrieval.

```
┌────────────────┐     ┌────────────────┐     ┌──────────────────────┐
│                │     │                │     │                      │
│  React Client  │────▶│  Azure Storage │────▶│  Azure AI Document   │
│                │     │                │     │     Intelligence     │
└────────────────┘     └────────────────┘     └──────────────────────┘
        │                                               │
        │                                               ▼
        │                                     ┌──────────────────────┐
        │                                     │                      │
        └────────────────────────────────────▶│   Azure AI Search    │
                                              │                      │
                                              └──────────────────────┘
```

## Core Components

### Frontend (Next.js/React)
- Web interface for document upload and search
- Built with React and TypeScript
- Uses ShadcnUI for components
- Deployed on Vercel

### Backend (Azure Functions)
- Serverless API endpoints
- Python-based implementation
- Handles file uploads, document processing, and search
- Endpoints:
  - `/api/upload`: File upload to Blob Storage
  - `/api/index`: Document indexing
  - `/api/search`: Document search

### Storage
- **Azure Blob Storage**
  - Stores uploaded documents
  - Container: test-upload
  - Uses direct upload with SAS tokens

### Search
- **Azure AI Search**
  - Indexes processed documents
  - Provides full-text and semantic search
  - Index: testpl_index_6
  - Environment Variables:
    - AZURE_AISEARCH_ENDPOINT
    - AZURE_AISEARCH_KEY
    - AZURE_AISEARCH_INDEX

### Document Processing
- **Azure Document Intelligence**
  - OCR processing
  - Table extraction
  - Layout analysis
  - Handwriting recognition

## Data Flow
1. User uploads document through web interface
2. Document is stored in Azure Blob Storage
3. Azure Function triggers document processing
4. Extracted content is indexed in Azure AI Search
5. Search results are available through web interface

## Error Handling & Resilience
The application includes fallback mechanisms for each Azure service:

- If the Azure Blob Storage upload fails, it uses a simulated upload
- If Azure AI Document Intelligence is unavailable, it provides helpful error messages
- If Azure AI Search indexing fails, the application continues processing and displays results

This resilience ensures that users can still use core functionality even when some cloud services are unavailable.

## Security
- CORS enabled for specific origins
- Anonymous authentication for development
- Environment variables for sensitive data

## Environment Variables
```env
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=
AZURE_BLOB_CONTAINER_NAME=

# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=
AZURE_DOCUMENT_INTELLIGENCE_KEY=

# Azure AI Search
AZURE_AISEARCH_ENDPOINT=
AZURE_AISEARCH_KEY=
AZURE_AISEARCH_INDEX=
```

## Development Setup
1. Install dependencies:
   ```bash
   npm install
   cd function_app
   pip install -r requirements.txt
   ```

2. Start development servers:
   ```bash
   # Frontend
   npm run dev

   # Backend
   cd function_app
   func start
   ```

## Deployment
- Frontend: Vercel
- Backend: Azure Functions
- Configuration through environment variables 