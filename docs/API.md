# API Documentation

## Base URL
- Local Development: `http://localhost:7071/api`
- Production: `https://testpl.azurewebsites.net/api`

## Endpoints

### File Upload
```http
POST /upload
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="example.pdf"

[binary file data]
```

**Response**
```json
{
  "url": "https://pencillabtest.blob.core.windows.net/test-upload/1234567890-example.pdf"
}
```

**Error Response**
```json
{
  "error": "Error message"
}
```

### Document Indexing
```http
POST /index
Content-Type: application/json

{
  "id": "doc123",
  "content": "Document content...",
  "filename": "example.pdf",
  "processedAt": "2024-03-05T12:34:56Z",
  "blobUrl": "https://..."
}
```

**Response**
```json
{
  "result": "Document indexed successfully"
}
```

**Error Response**
```json
{
  "error": "Error message"
}
```

### Document Search
```http
POST /search
Content-Type: application/json

{
  "query": "search terms"
}
```

**Response**
```json
{
  "value": [
    {
      "id": "doc123",
      "filename": "example.pdf",
      "content": "Matching content...",
      "pageNumber": 1,
      "contentType": "paragraph",
      "confidence": 0.95,
      "blobUrl": "https://...",
      "processedAt": "2024-03-05T12:34:56Z"
    }
  ]
}
```

**Error Response**
```json
{
  "error": "Error message"
}
```

## Error Codes

- `400`: Bad Request - Missing or invalid parameters
- `401`: Unauthorized - Authentication failed
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource doesn't exist
- `500`: Internal Server Error - Server-side error

## CORS

Allowed Origins:
- `http://localhost:8080`
- `http://localhost:5173`
- `http://localhost:4173`
- Production domain (TBD)

Allowed Methods:
- GET
- POST
- PUT
- DELETE
- OPTIONS

Allowed Headers:
- Content-Type
- Content-Disposition
- Authorization

## Rate Limiting

- Maximum file size: 100MB
- Maximum requests per minute: TBD
- Maximum concurrent uploads: TBD

## Authentication

Currently using anonymous authentication for development.
Future implementation will use Azure AD B2C.

## Examples

### Upload File (JavaScript)
```javascript
const response = await fetch('http://localhost:7071/api/upload', {
  method: 'POST',
  headers: {
    'Content-Type': file.type,
    'Content-Disposition': `attachment; filename="${file.name}"`
  },
  body: file
});

const data = await response.json();
console.log('File URL:', data.url);
```

### Search Documents (JavaScript)
```javascript
const response = await fetch('http://localhost:7071/api/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'search terms'
  })
});

const data = await response.json();
console.log('Search results:', data.value);
```

## Known Limitations

1. File Upload
   - Maximum file size: 100MB
   - Supported formats: PDF, PNG, JPEG, TIFF
   - Single file upload only

2. Search
   - Maximum query length: 1000 characters
   - Results limited to 50 items per page
   - Basic text search only (semantic search coming soon)

3. Document Processing
   - OCR works best with clear, scanned documents
   - Table extraction may have limitations with complex layouts
   - Handwriting recognition accuracy varies 

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