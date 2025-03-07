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
        
        # Get the file from the request
        files = req.files.get('file')
        if not files:
            return create_error_response(400, "No file found in request")
        
        # Get the first file if multiple were uploaded
        file = files[0] if isinstance(files, list) else files
        
        # Get file properties
        filename = file.filename
        content_type = file.content_type
        file_contents = file.read()
        file_size = len(file_contents)
        
        if file_size <= 0:
            return create_error_response(400, "Empty file uploaded")
        
        # Get blob storage connection string from environment variable
        connection_string = os.environ.get('AzureWebJobsStorage')
        if not connection_string:
            logger.error("Missing storage connection string")
            return create_error_response(500, "Storage configuration error")
        
        # Create a unique blob name using user_id, folder_id and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        blob_name = f"{user_id}/{folder_id}/{timestamp}_{filename}"
        
        # Upload to blob storage
        from azure.storage.blob import BlobServiceClient, ContentSettings
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = os.environ.get('STORAGE_CONTAINER_NAME', 'ocrlab-files')
        
        # Create container if it doesn't exist
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            return create_error_response(500, f"Failed to create storage container: {str(e)}")
        
        # Upload the file
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(
            file_contents,
            overwrite=True,
            content_settings=content_settings
        )
        
        # Get the blob URL
        blob_url = blob_client.url
        
        # Save file metadata to database (TODO: implement database connection)
        # For now, we'll just return the file information
        file_data = {
            "id": 1,  # This would normally be assigned by the database
            "name": filename,
            "folder_id": int(folder_id),
            "blob_url": blob_url,
            "status": "uploaded",
            "size_bytes": file_size,
            "content_type": content_type,
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
        top = req_body.get('top', 5)  # Default to 5 results
        
        # Connect to Azure Search Service
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search credentials from environment
        endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT', 'https://testpl.search.windows.net/')
        search_api_key = os.environ.get('AZURE_AISEARCH_KEY')
        search_index_name = os.environ.get('AZURE_AISEARCH_INDEX', 'test-upload')
        
        if not search_api_key or search_api_key == 'default-key-for-development':
            logger.warning("Using mock search service because API key not configured")
            # Return mock data for testing
            mock_results = [
                {
                    "id": "mock-doc-1",
                    "text": "This is a sample document that matches your query: " + query,
                    "score": 0.95,
                    "filename": "sample.pdf",
                    "blobUrl": "https://example.com/sample.pdf",
                    "pageNumber": 1
                }
            ]
            return func.HttpResponse(
                body=json.dumps({
                    "results": mock_results,
                    "note": "Mock results - Azure Search API key not configured"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Create the search client
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=search_index_name,
            credential=AzureKeyCredential(search_api_key)
        )
                        
        # Set up search options
        # Filter by user_id from metadata for multi-tenancy security
        select_fields = ["id", "content", "metadata"]
        
        # Perform search query
        try:
            # Regular search (not semantic) since semantic requires special configuration
            results = search_client.search(
                search_text=query,
                select=select_fields,
                top=top
            )
            
            # Process and format the results
            formatted_results = []
            for result in results:
                # Extract metadata if available
                metadata = {}
                if "metadata" in result and result["metadata"]:
                    try:
                        metadata = json.loads(result["metadata"])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse metadata JSON for document {result.get('id', '')}")
                
                # Skip documents not owned by this user (if user_id in metadata)
                result_user_id = metadata.get("user_id")
                if result_user_id and result_user_id != user_id:
                    continue
                    
                # Format the result
                formatted_result = {
                    "id": result.get("id", ""),
                    "text": result.get("content", ""),
                    "score": result["@search.score"] if "@search.score" in result else 0,
                    "filename": metadata.get("filename", ""),
                    "blobUrl": metadata.get("blobUrl", ""),
                    "pageNumber": metadata.get("pageNumber", 1)
                }
                
                formatted_results.append(formatted_result)
            
            return func.HttpResponse(
                body=json.dumps({"results": formatted_results}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logger.error(f"Error during search operation: {str(e)}")
            return create_error_response(500, f"Error during search operation: {str(e)}")
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

# Document Indexing Functions
@app.route(route="index", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def index_document(req: func.HttpRequest) -> func.HttpResponse:
    """Index document content in Azure AI Search."""
    try:
        # Get the request body
        req_body = req.get_json()
        if not req_body:
            return create_error_response(400, "Request body is required")
            
        # Validate required fields
        if 'id' not in req_body:
            return create_error_response(400, "Document ID is required")
        if 'content' not in req_body or not req_body['content']:
            return create_error_response(400, "Document content is required")
        
        # Get user ID from headers for multi-tenancy
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        # Connect to Azure Search Service
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search credentials from environment
        endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT', 'https://testpl.search.windows.net/')
        search_api_key = os.environ.get('AZURE_AISEARCH_KEY')
        search_index_name = os.environ.get('AZURE_AISEARCH_INDEX', 'test-upload')
        
        if not search_api_key or search_api_key == 'default-key-for-development':
            logger.warning("Using mock search service because API key not configured. Would index document with ID: " + req_body['id'])
            # Return success for testing without actual search service
            return func.HttpResponse(
                body=json.dumps({
                    "success": True, 
                    "message": "Document indexed successfully (MOCK MODE)", 
                    "note": "Azure Search API key not configured - document not actually indexed"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        # Create the search client
        admin_client = SearchClient(
            endpoint=endpoint,
            index_name=search_index_name,
            credential=AzureKeyCredential(search_api_key)
        )
        
        # Prepare the document for indexing according to the index schema
        # Schema: id (String), content (String), content_vector (SingleCollection), metadata (String)
        
        # Create a combined metadata object as a JSON string
        metadata_dict = {}
        
        # Add basic metadata
        if 'metadata' in req_body:
            try:
                if isinstance(req_body['metadata'], str):
                    metadata_dict = json.loads(req_body['metadata'])
                else:
                    metadata_dict = req_body['metadata']
            except json.JSONDecodeError:
                logger.warning("Invalid metadata JSON, using empty metadata")
        
        # Add user ID to metadata for multi-tenancy tracking without schema changes
        metadata_dict['user_id'] = user_id
        
        # Create the search document with only the fields in the schema
        search_document = {
            'id': req_body['id'],
            'content': req_body['content'],
            'metadata': json.dumps(metadata_dict)
        }
        
        # Add content_vector if provided in the request
        if 'content_vector' in req_body and isinstance(req_body['content_vector'], list):
            search_document['content_vector'] = req_body['content_vector']
        
        # Index the document
        try:
            result = admin_client.upload_documents(documents=[search_document])
            
            # Check result
            success = all(r.succeeded for r in result)
            if not success:
                logger.error(f"Error indexing document: {result[0].error_message}")
                return create_error_response(500, f"Error indexing document: {result[0].error_message}")
            
            return func.HttpResponse(
                body=json.dumps({"success": True, "message": "Document indexed successfully"}),
                status_code=200,
                mimetype="application/json"
            )
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            return create_error_response(500, f"Error during document indexing: {str(e)}")
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        return create_error_response(500, f"Failed to index document: {str(e)}")