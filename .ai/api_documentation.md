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

**Endpoint:** `POST /api/upload`

**Headers:**
- `x-user-id` (required): The ID of the user uploading the file
- `x-folder-id` (required): The ID of the folder to upload the file to
- `content-type`: The MIME type of the file
- `content-disposition`: Contains the filename (e.g., `attachment; filename="example.pdf"`)

**Body:**
- Binary file content

**Response:**
- `201 Created`: File uploaded successfully
  ```json
  {
    "file": {
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
  }
  ```
- `400 Bad Request`: Missing required parameters or invalid file
  ```json
  {
    "error": "Folder ID is required in x-folder-id header"
  }
  ```
- `404 Not Found`: Folder not found
  ```json
  {
    "error": "Folder not found or you don't have permission to access it"
  }
  ```
- `500 Internal Server Error`: Upload or database error
  ```json
  {
    "error": "Failed to upload file: [error message]"
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

Search for documents using natural language queries.

**Endpoint:** `POST /api/query`

**Headers:**
- `x-user-id` (required): The ID of the user
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "query": "financial statements for 2024",
  "folder_id": 1,
  "limit": 10,
  "offset": 0
}
```

**Parameters:**
- `query` (required): The search query text
- `folder_id` (optional): Filter results to a specific folder
- `limit` (optional): Maximum number of results to return (default: 10)
- `offset` (optional): Number of results to skip for pagination (default: 0)

**Response:**
- `200 OK`: Search results
  ```json
  {
    "results": [
      {
        "id": "doc-123",
        "text": "Financial statements for the fiscal year 2024 show a significant increase in revenue...",
        "score": 0.89,
        "filename": "Q4_financials_2024.pdf",
        "page": 1,
        "folder_id": 1,
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": "doc-456",
        "text": "The balance sheet from 2024 indicates strong liquidity positions across all departments...",
        "score": 0.72,
        "filename": "annual_report_2024.pdf",
        "page": 5,
        "folder_id": 1,
        "created_at": "2024-01-20T14:45:00Z"
      }
    ]
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "Query parameter is required"
  }
  ```
- `500 Internal Server Error`: Search error
  ```json
  {
    "error": "Failed to execute search: [error message]"
  }
  ```

### Index Document

Manually index a document in the vector database.

**Endpoint:** `POST /api/index`

**Headers:**
- `x-user-id` (required): The ID of the user
- `Content-Type`: `application/json`

**Request Body:**
```json
{
  "file_id": "file-123"
}
```

**Parameters:**
- `file_id` (required): The ID of the file to index

**Response:**
- `200 OK`: Indexing started successfully
  ```json
  {
    "message": "Document indexing started",
    "file_id": "file-123",
    "status": "processing"
  }
  ```
- `400 Bad Request`: Missing required parameters
  ```json
  {
    "error": "File ID is required"
  }
  ```
- `404 Not Found`: File not found
  ```json
  {
    "error": "File not found or you don't have permission to access it"
  }
  ```
- `500 Internal Server Error`: Indexing error
  ```json
  {
    "error": "Failed to index document: [error message]"
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
    "file_id": "file-123",
    "user_id": "user-456",
    "status": "completed",
    "processing_time": 3.5,
    "extracted_content": {
      "paragraphs": 15,
      "tables": 2,
      "images": 3,
      "handwritten_items": 1
    },
    "summary": "This document contains financial projections for Q1 2024, including revenue forecasts and expense breakdowns...",
    "keywords": ["financial", "projections", "revenue", "2024", "expenses"]
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