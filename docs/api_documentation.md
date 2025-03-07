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

*Documentation for search endpoints will be added once implemented.*

## Usage Tracking

*Documentation for usage tracking endpoints will be added once implemented.* 