# OCR Lab API Documentation

This document provides detailed information about the OCR Lab API endpoints, including request/response formats, authentication requirements, and examples.

## Authentication

All API endpoints require authentication using the Clerk authentication system. The user ID should be included in the `x-user-id` header for all requests.

## Folder Management

### List Folders

Retrieves all folders for a user.

**Endpoint:** `GET /api/folders`

**Headers:**
- `x-user-id` (required): The ID of the user to get folders for

**Response:**
- `200 OK`: List of folders
  ```json
  {
    "folders": [
      {
        "id": 1,
        "name": "Home",
        "user_id": "user_123",
        "created_at": "2023-03-07T11:20:39.648450+00:00",
        "updated_at": "2023-03-07T11:20:39.648450+00:00"
      },
      {
        "id": 2,
        "name": "Work",
        "user_id": "user_123",
        "created_at": "2023-03-07T11:25:39.648450+00:00",
        "updated_at": "2023-03-07T11:25:39.648450+00:00"
      }
    ]
  }
  ```
- `400 Bad Request`: Missing user_id parameter
  ```json
  {
    "error": "User ID is required in x-user-id header"
  }
  ```
- `500 Internal Server Error`: Database error
  ```json
  {
    "error": "Failed to list folders: [error message]"
  }
  ```

### Create Folder

Creates a new folder for a user.

**Endpoint:** `POST /api/folders`

**Headers:**
- `x-user-id` (required): The ID of the user to create the folder for
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "name": "New Folder"
}
```

**Response:**
- `201 Created`: Folder created successfully
  ```json
  {
    "folder": {
      "id": 3,
      "name": "New Folder",
      "user_id": "user_123",
      "created_at": "2023-03-07T11:30:39.648450+00:00",
      "updated_at": "2023-03-07T11:30:39.648450+00:00"
    }
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Missing required parameters: user_id and name"
  }
  ```
- `500 Internal Server Error`: Database error
  ```json
  {
    "error": "Failed to create folder: [error message]"
  }
  ```

### Delete Folder

Deletes a folder.

**Endpoint:** `DELETE /api/folders/{folder_id}`

**Path Parameters:**
- `folder_id`: The ID of the folder to delete

**Headers:**
- `x-user-id` (required): The ID of the user who owns the folder

**Response:**
- `200 OK`: Folder deleted successfully
  ```json
  {
    "success": true,
    "message": "Folder deleted successfully"
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Missing required parameters: folder_id and user_id"
  }
  ```
- `404 Not Found`: Folder not found
  ```json
  {
    "error": "Folder not found or you don't have permission to delete it"
  }
  ```
- `500 Internal Server Error`: Database error
  ```json
  {
    "error": "Failed to delete folder: [error message]"
  }
  ```

## File Management

### Upload File

Uploads a file to Azure Blob Storage and creates a file record in the database.

**Endpoint:** `POST /api/files`

**Headers:**
- `x-user-id` (required): The ID of the user uploading the file
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "name": "example.pdf",
  "folder_id": 3,
  "mime_type": "application/pdf",
  "size_bytes": 1048576,
  "blob_path": "test-upload/example.pdf"
}
```

**Response:**
- `201 Created`: File uploaded successfully
  ```json
  {
    "id": 1,
    "name": "example.pdf",
    "folder_id": 3,
    "status": "queued",
    "created_at": "2023-03-07T12:34:56.789012+00:00"
  }
  ```
- `400 Bad Request`: Missing required parameters or invalid file
  ```json
  {
    "error": "Bad request: Missing required fields"
  }
  ```
- `404 Not Found`: Folder not found
  ```json
  {
    "error": "Folder not found: {folder_id}"
  }
  ```
- `500 Internal Server Error`: Upload or database error
  ```json
  {
    "error": "Failed to upload file: [error message]"
  }
  ```

### Process Document

Processes a document using Azure Document Intelligence and then indexes it in Azure AI Search.

**Endpoint:** `POST /api/process_document`

**Headers:**
- `x-user-id` (required): The ID of the user
- `Content-Type`: `application/pdf` (or other supported document type)

**Query Parameters:**
- `title` (optional): Title for the document
- `id` (optional): Custom ID for the document
- `file_id` (optional): ID of the file in the database

**Body:**
- Binary file content (the actual document to process)

**Implementation Notes:**
- The implementation directly uses Azure Document Intelligence to process the document
- The document is chunked and vector embeddings are generated for each chunk
- Chunks are indexed in Azure AI Search with proper metadata
- Results include only chunks that successfully received vector embeddings

**Response:**
- `200 OK`: Document processing completed
  ```json
  {
    "document_id": "doc_Financial_Report",
    "title": "Financial Report",
    "chunks_count": 10,
    "indexed_count": 10,
    "failed_count": 0
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Document content is required"
  }
  ```
- `500 Internal Server Error`: Processing error
  ```json
  {
    "error": "Error processing document: [error message]"
  }
  ```

### List Files

Retrieves all files in a folder.

**Endpoint:** `GET /api/files`

**Headers:**
- `x-user-id` (required): The ID of the user

**Query Parameters:**
- `folder_id` (required): The ID of the folder to get files from

**Response:**
- `200 OK`: List of files
  ```json
  {
    "files": [
      {
        "id": 1,
        "name": "example.pdf",
        "folder_id": 3,
        "blob_url": "https://storage.azure.com/container/20230307123456_abcd1234_example.pdf",
        "status": "uploaded",
        "size_bytes": 1048576,
        "content_type": "application/pdf",
        "created_at": "2023-03-07T12:34:56.789012+00:00",
        "updated_at": "2023-03-07T12:34:56.789012+00:00"
      }
    ]
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Folder ID is required in query parameters"
  }
  ```
- `404 Not Found`: Folder not found
  ```json
  {
    "error": "Folder not found or you don't have permission to access it"
  }
  ```
- `500 Internal Server Error`: Database error
  ```json
  {
    "error": "Failed to manage files: [error message]"
  }
  ```

### Delete File

Deletes a file.

**Endpoint:** `DELETE /api/files`

**Headers:**
- `x-user-id` (required): The ID of the user

**Query Parameters:**
- `id` (required): The ID of the file to delete

**Response:**
- `200 OK`: File deleted successfully
  ```json
  {
    "success": true,
    "message": "File deleted successfully"
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "File ID is required in query parameters"
  }
  ```
- `404 Not Found`: File not found
  ```json
  {
    "error": "File not found or you don't have permission to delete it"
  }
  ```
- `500 Internal Server Error`: Database error
  ```json
  {
    "error": "Failed to manage files: [error message]"
  }
  ```

## Search

### Query Documents

Search for documents using text search capabilities, matching against document content.

**Endpoint:** `POST /api/query`

**Headers:**
- `x-user-id` (required): The ID of the user
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "query": "financial statements for 2024",
  "top": 10
}
```

**Parameters:**
- `query` (required): The search query text
- `top` (optional): Maximum number of results to return (default: 5)

**Implementation Notes:**
- The implementation uses Azure AI Search with standard text search capabilities
- User ID is used to filter results for multi-tenancy security
- Usage statistics are updated to count queries made

**Response:**
- `200 OK`: Search results
  ```json
  {
    "results": [
      {
        "id": "chunk-123",
        "text": "Financial statements for the fiscal year 2024 show a significant increase in revenue...",
        "score": 0.89,
        "filename": "Q4 Financial Report 2024",
        "title": "Q4 Financial Report 2024",
        "page": "5",
        "type": "Table"
      },
      {
        "id": "chunk-456",
        "text": "The balance sheet from 2024 indicates strong liquidity positions across all departments...",
        "score": 0.72,
        "filename": "Annual Report 2024",
        "title": "Annual Report 2024", 
        "page": "12",
        "type": "Paragraph"
      }
    ]
  }
  ```

### Vector Search Documents

Search for documents using vector search for semantic similarity. This endpoint leverages embeddings for more relevant results based on meaning rather than exact keyword matches.

**Endpoint:** `POST /api/vector_search`

**Headers:**
- `x-user-id` (required): The ID of the user
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "query": "financial statements for 2024",
  "top_k": 10
}
```

**Parameters:**
- `query` (required): The search query text
- `top_k` (optional): Maximum number of results to return (default: 5)

**Implementation Notes:**
- The implementation uses Azure AI Search with vector search capabilities
- Text from the query is converted to vector embeddings via Azure OpenAI
- User ID is used to filter results for multi-tenancy security
- Usage statistics are updated to count queries made

**Response:**
- `200 OK`: Search results
  ```json
  {
    "results": [
      {
        "text": "Financial statements for the fiscal year 2024 show a significant increase in revenue...",
        "page": 5,
        "type": "table",
        "score": 0.89,
        "document_title": "Q4 Financial Report 2024",
        "parent_id": "doc-123"
      },
      {
        "text": "The balance sheet from 2024 indicates strong liquidity positions across all departments...",
        "page": 12,
        "type": "paragraph",
        "score": 0.72,
        "document_title": "Annual Report 2024",
        "parent_id": "doc-456"
      }
    ]
  }
  ```

## Document Processing

### Processing Status

Check the status of document processing.

**Endpoint:** `GET /api/processing-status/{file_id}`

**Path Parameters:**
- `file_id` (required): The ID of the file to check status for

**Headers:**
- `x-user-id` (required): The ID of the user who owns the file

**Response:**
- `200 OK`: Processing status
  ```json
  {
    "processing": {
      "file_id": 123,
      "name": "document.pdf",
      "status": "completed",
      "progress": 100,
      "error": null,
      "started_at": "2023-03-07T12:34:56.789012+00:00",
      "completed_at": "2023-03-07T12:40:12.345678+00:00",
      "pages_processed": 10,
      "total_pages": 10,
      "attempts": 1
    }
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Missing file ID in route parameters"
  }
  ```
- `404 Not Found`: File not found
  ```json
  {
    "error": "File not found or processing information not available"
  }
  ```
- `500 Internal Server Error`: Server error
  ```json
  {
    "error": "Error getting processing status: [error message]"
  }
  ```

## Usage Tracking

### Get Usage Statistics

Retrieves usage statistics for a user.

**Endpoint:** `GET /api/usage`

**Headers:**
- `x-user-id` (required): The ID of the user

**Response:**
- `200 OK`: Usage statistics
  ```json
  {
    "storage": {
      "used_bytes": 12582912,
      "limit_bytes": 1073741824,
      "percentage": 1.17
    },
    "requests": {
      "current_month": 152,
      "limit_per_month": 1000,
      "percentage": 15.2
    },
    "documents": {
      "count": 25,
      "processed": 22,
      "pending": 3
    }
  }
  ```
- `400 Bad Request`: Missing user ID
  ```json
  {
    "error": "User ID is required in x-user-id header"
  }
  ```
- `500 Internal Server Error`: Server error
  ```json
  {
    "error": "Failed to get usage statistics: [error message]"
  }
  ```

## Deployment Information

The API is available at the following base URLs:

- **Development:** `http://localhost:7071/api/`
- **Production:** `https://testpl.azurewebsites.net/api/`

**Note:** The processing status endpoint has a non-standard URL pattern with a double "api" prefix in the production environment. The correct URL is:

`https://testpl.azurewebsites.net/api/api/processing-status/{file_id}`

This URL pattern will be standardized in a future update.