# Azure API Integration Guide

This document provides details about the Azure services integration in the Document Intelligence application.

## Azure Blob Storage Integration

**Purpose**: Store uploaded PDF documents for processing.

**Implementation**: `src/lib/azure-storage.ts`

### Key Features:

- Direct REST API integration using fetch API and XMLHttpRequest
- SAS token authentication for secure uploads
- Progress tracking for uploads
- Fallback to simulation mode when Azure Storage is unavailable

### Usage Example:

```typescript
import { uploadFileToBlob } from './lib/azure-storage';

// Upload a file with progress tracking
const blobUrl = await uploadFileToBlob(file, (progress) => {
  console.log(`Upload progress: ${progress}%`);
});
```

## Azure AI Document Intelligence Integration

**Purpose**: Process PDF documents to extract structured content.

**Implementation**: `src/lib/azure-ai.ts`

### Key Features:

- Document submission to the Azure AI Document Intelligence API
- Polling mechanism to track processing status
- Transformation of Azure results into application data model
- Extraction of paragraphs, tables, figures, and handwritten text

### Usage Example:

```typescript
import { processPdfDocument } from './lib/azure-ai';

// Process a PDF document with progress tracking
const result = await processPdfDocument(file, (progress) => {
  console.log(`Processing progress: ${progress}%`);
});
```

## Azure AI Search Integration

**Purpose**: Index extracted content for future search and retrieval.

**Implementation**: `src/lib/azure-search.ts`

### Key Features:

- Document indexing in Azure AI Search
- Conversion of processed documents to search-friendly format
- Search functionality for indexed content
- Fallback to simulation mode when Azure Search is unavailable

### Configuration:

Required environment variables:
```env
AZURE_AISEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_AISEARCH_KEY=your-search-admin-key
AZURE_AISEARCH_INDEX=your-index-name
```

### Usage Example:

```typescript
import { indexDocumentInSearch, searchDocuments } from './lib/azure-search';

// Index a processed document
await indexDocumentInSearch(processedDocument, blobUrl);

// Search for documents
const searchResults = await searchDocuments("query text");
```

## Error Handling Strategy

The application implements a progressive error handling strategy:

1. **Attempt direct API integration**: Try to use Azure services directly
2. **Provide clear error messages**: If services are unavailable, show user-friendly messages
3. **Implement fallbacks**: Use simulation mode to allow the application to function without Azure services
4. **Continue processing**: Even if one service fails (e.g., Azure Search), continue with other functionality

This approach ensures the application remains functional even when some cloud services are unavailable.
