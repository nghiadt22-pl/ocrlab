"""
Main entry point for the OCR Lab backend Azure Functions app.
"""
import json
import logging
import os
import azure.functions as func
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocrlab')

# Create the function app
app = func.FunctionApp()

# Helper functions
def get_user_id(req):
    """Extract user ID from request headers."""
    return req.headers.get('x-user-id')

def create_error_response(status_code, message):
    """Create a standardized error response."""
    return func.HttpResponse(
        body=json.dumps({"error": message}),
        status_code=status_code,
        mimetype="application/json"
    )

# Folder Management Functions
@app.route(route="folders", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_folders(req: func.HttpRequest) -> func.HttpResponse:
    """List all folders for a user."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        # TODO: Implement folder listing logic
        # For now, return mock data
        folders = [
            {
                "id": 1,
                "name": "Home",
                "user_id": user_id,
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
        ]
        
        return func.HttpResponse(
            body=json.dumps({"folders": folders}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}")
        return create_error_response(500, f"Failed to list folders: {str(e)}")

@app.route(route="folders", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def create_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new folder for a user."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        req_body = req.get_json()
        if not req_body or 'name' not in req_body:
            return create_error_response(400, "Folder name is required")
        
        folder_name = req_body.get('name')
        
        # TODO: Implement folder creation logic
        # For now, return mock data
        new_folder = {
            "id": 2,
            "name": folder_name,
            "user_id": user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            body=json.dumps({"folder": new_folder}),
            status_code=201,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return create_error_response(500, f"Failed to create folder: {str(e)}")

@app.route(route="folders/{folder_id}", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def delete_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a folder."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        folder_id = req.route_params.get('folder_id')
        if not folder_id:
            return create_error_response(400, "Folder ID is required")
        
        # TODO: Implement folder deletion logic
        
        return func.HttpResponse(
            body=json.dumps({
                "success": True,
                "message": "Folder deleted successfully"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error deleting folder: {str(e)}")
        return create_error_response(500, f"Failed to delete folder: {str(e)}")

# File Management Functions
@app.route(route="upload", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    """Upload a file to Azure Blob Storage."""
    try:
        user_id = get_user_id(req)
        folder_id = req.headers.get('x-folder-id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not folder_id:
            return create_error_response(400, "Folder ID is required in x-folder-id header")
        
        # TODO: Implement file upload logic
        # For now, return mock data
        file_data = {
            "id": 1,
            "name": "example.pdf",
            "folder_id": int(folder_id),
            "blob_url": "https://storage.azure.com/container/example.pdf",
            "status": "uploaded",
            "size_bytes": 1048576,
            "content_type": "application/pdf",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            body=json.dumps({"file": file_data}),
            status_code=201,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return create_error_response(500, f"Failed to upload file: {str(e)}")

@app.route(route="files", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    """List all files in a folder."""
    try:
        user_id = get_user_id(req)
        folder_id = req.params.get('folder_id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not folder_id:
            return create_error_response(400, "Folder ID is required in query parameters")
        
        # TODO: Implement file listing logic
        # For now, return mock data
        files = [
            {
                "id": 1,
                "name": "example.pdf",
                "folder_id": int(folder_id),
                "blob_url": "https://storage.azure.com/container/example.pdf",
                "status": "uploaded",
                "size_bytes": 1048576,
                "content_type": "application/pdf",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
        ]
        
        return func.HttpResponse(
            body=json.dumps({"files": files}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return create_error_response(500, f"Failed to list files: {str(e)}")

@app.route(route="files", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a file."""
    try:
        user_id = get_user_id(req)
        file_id = req.params.get('id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not file_id:
            return create_error_response(400, "File ID is required in query parameters")
        
        # TODO: Implement file deletion logic
        
        return func.HttpResponse(
            body=json.dumps({
                "success": True,
                "message": "File deleted successfully"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return create_error_response(500, f"Failed to delete file: {str(e)}")

# Search Functions
@app.route(route="query", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def search_query(req: func.HttpRequest) -> func.HttpResponse:
    """Perform a semantic search query."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return create_error_response(400, "Query is required")
        
        query = req_body.get('query')
        n = req_body.get('n', 5)  # Default to 5 results
        
        # TODO: Implement search logic
        # For now, return mock data
        results = [
            {
                "text": "This is a sample text chunk that matches the query.",
                "file_id": 1,
                "file_name": "example.pdf",
                "page_number": 1,
                "score": 0.95
            }
        ]
        
        return func.HttpResponse(
            body=json.dumps({"results": results}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        return create_error_response(500, f"Failed to perform search: {str(e)}")

# Usage Tracking Functions
@app.route(route="usage", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_usage(req: func.HttpRequest) -> func.HttpResponse:
    """Get usage statistics for a user."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        # TODO: Implement usage tracking logic
        # For now, return mock data
        usage_data = {
            "pages_processed": 100,
            "queries_made": 50,
            "storage_used_bytes": 10485760,
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        return func.HttpResponse(
            body=json.dumps({"usage": usage_data}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Error retrieving usage data: {str(e)}")
        return create_error_response(500, f"Failed to retrieve usage data: {str(e)}")

# Queue Trigger for OCR Processing
@app.function_name("ProcessOCRQueue")
@app.queue_trigger(arg_name="msg", queue_name="ocr-processing-queue", 
                  connection="AzureWebJobsStorage")
def process_ocr_queue(msg: func.QueueMessage) -> None:
    """Process OCR jobs from the queue."""
    try:
        message_body = msg.get_body().decode('utf-8')
        logger.info(f"Processing OCR job: {message_body}")
        
        # TODO: Implement OCR processing logic
        # 1. Get file from Blob Storage
        # 2. Process with Azure Document Intelligence
        # 3. Store results in database and vector store
        # 4. Update file status
        
        logger.info(f"OCR processing completed for job: {message_body}")
    except Exception as e:
        logger.error(f"Error processing OCR job: {str(e)}") 