
# Developer Guide

This document provides guidance for developers working on the Document Intelligence application.

## Project Setup

### Prerequisites

- Node.js (v16 or later)
- npm, yarn, or bun package manager

### Installation

1. Clone the repository
2. Install dependencies:
```
npm install
```
3. Start the development server:
```
npm run dev
```

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── ui/            # shadcn/ui components
│   ├── FileUpload.tsx # File upload component
│   ├── ProcessingView.tsx # Processing status component
│   └── ResultView.tsx # Results display component
├── lib/               # Utility functions and API integrations
│   ├── azure-ai.ts    # Azure AI Document Intelligence integration
│   ├── azure-search.ts # Azure AI Search integration
│   ├── azure-storage.ts # Azure Blob Storage integration
│   ├── types.ts       # TypeScript type definitions
│   └── utils.ts       # General utility functions
├── pages/             # Page components
│   ├── Index.tsx      # Main application page
│   ├── SignIn.tsx     # Sign-in page
│   └── SignUp.tsx     # Sign-up page
├── App.tsx            # Main application component
└── main.tsx           # Application entry point
```

## Key TypeScript Types

The application uses several key TypeScript interfaces:

### ContentType

```typescript
export type ContentType = 'paragraph' | 'table' | 'figure' | 'handwriting';
```

### ExtractedItem

```typescript
export interface ExtractedItem {
  id: string;
  type: ContentType;
  content: string | string[][] | string; // Text for paragraphs/handwriting, 2D array for tables, base64 for figures
  confidence: number;
  pageNumber: number;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}
```

### ProcessedDocument

```typescript
export interface ProcessedDocument {
  id: string;
  filename: string;
  extractedContent: ExtractedItem[];
  processedAt: Date;
}
```

### UploadStatus

```typescript
export interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
  progress?: number;
  message?: string;
  error?: string;
}
```

## Adding New Features

### Adding a New Content Type

1. Add the new content type to the `ContentType` type in `src/lib/types.ts`
2. Update the `transformAzureResults` function in `src/lib/azure-ai.ts` to extract the new content type
3. Update the `ExtractedContent` component to render the new content type
4. Add a new tab for the content type in the `ResultView` component

### Implementing New Azure Services

1. Create a new integration file in the `src/lib` directory
2. Add service-specific configuration (endpoints, API keys, etc.)
3. Implement functions for interacting with the service
4. Add fallback/simulation mode for resilience
5. Update relevant components to use the new service

## Best Practices

### Error Handling

- Always include try/catch blocks around API calls
- Provide user-friendly error messages
- Implement fallback mechanisms where possible
- Use the toast notification system for important messages

### Performance

- Optimize file uploads by tracking progress
- Use pagination for large result sets
- Implement debouncing for search functionality
- Consider lazy loading for components that display large datasets

### Security

- Never expose API keys in client-side code (current implementation is for demo purposes only)
- In production, use Azure Key Vault or environment variables on the server
- Implement proper authentication and authorization for accessing Azure resources
- Use SAS tokens with limited time validity for blob storage access
