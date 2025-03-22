"""
Main entry point for the OCR Lab backend Azure Functions app.
"""
import json
import logging
import os
import azure.functions as func
import datetime
import base64
from typing import Optional, List, Dict, Any
import requests  # Add this import for making HTTP requests to Clerk API

# Import database modules
from database.connection import get_db_session
from database import crud
from database.models import User, Folder, File, UsageStat

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

def get_or_create_user(user_id: str, email: Optional[str] = None) -> Optional[User]:
    """Get or create a user in the database."""
    try:
        db = get_db_session()
        user = crud.get_user(db, user_id)
        
        if not user and email:
            # Create user if it doesn't exist
            user = crud.create_user(db, user_id, email)
            logger.info(f"Created new user with ID {user_id}")
        elif not user:
            # Can't create user without email
            logger.error(f"User {user_id} not found and no email provided")
            return None
            
        return user
    except Exception as e:
        logger.error(f"Error getting or creating user: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def get_queue_client(queue_name="ocr-processing-queue"):
    """Get a queue client for the specified queue."""
    try:
        from azure.storage.queue import QueueServiceClient
        
        # Get connection string from environment variable
        connection_string = os.environ.get('AzureWebJobsStorage')
        if not connection_string:
            logger.error("Missing storage connection string")
            raise ValueError("Storage configuration error")
        
        # Handle mock mode for testing
        if connection_string == "mock":
            logger.info("Using mock queue client for testing")
            # Return a mock queue client
            class MockQueueClient:
                def create_queue(self):
                    logger.info("Mock: Queue created")
                    return True
                
                def send_message(self, message):
                    logger.info(f"Mock: Message sent to queue: {message}")
                    # Process the message immediately for testing
                    try:
                        message_data = json.loads(message)
                        logger.info(f"Mock: Processing OCR job: {message}")
                        logger.info(f"Mock: OCR processing completed for job: {message}")
                    except Exception as e:
                        logger.error(f"Mock: Error processing OCR job: {str(e)}")
                    return True
            
            return MockQueueClient()
        
        # Create the queue client
        queue_service_client = QueueServiceClient.from_connection_string(connection_string)
        queue_client = queue_service_client.get_queue_client(queue_name)
        
        # Create the queue if it doesn't exist
        try:
            queue_client.create_queue()
        except Exception as e:
            # Queue already exists or other error
            logger.info(f"Queue creation note: {str(e)}")
        
        return queue_client
    except Exception as e:
        logger.error(f"Error getting queue client: {str(e)}")
        raise

# Helper function to get Clerk API key from environment variables
def get_clerk_api_key():
    """Get the Clerk API key from environment variables."""
    api_key = os.environ.get('CLERK_API_KEY')
    if not api_key:
        logger.error("Missing Clerk API key")
        raise ValueError("Clerk API key not configured")
    return api_key

# Clerk API helper
def get_users_from_clerk():
    """Fetch all users from Clerk API."""
    try:
        api_key = get_clerk_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Clerk API URL for listing users
        url = "https://api.clerk.dev/v1/users"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch users from Clerk: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        # Check if the response is already a list or a dict with a 'data' key
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'data' in data:
            return data.get('data', [])
        else:
            logger.warning(f"Unexpected response format from Clerk API: {type(data)}")
            return []
    except Exception as e:
        logger.error(f"Error fetching users from Clerk: {str(e)}")
        return []

# TimeTrigger function to sync Clerk users with database
@app.function_name("ClerkSyncTimer")
@app.timer_trigger(schedule="*/15 * * * * *", arg_name="myTimer", run_on_startup=True)
def clerk_sync_timer(myTimer: func.TimerRequest) -> None:
    """
    Syncs Clerk users with PostgreSQL database every 15 seconds.
    This ensures our database stays in sync with Clerk's user management.
    """
    if myTimer.past_due:
        logger.info('Clerk sync timer is past due')
    
    logger.info('Clerk sync timer triggered')
    
    try:
        # Get users from Clerk
        clerk_users = get_users_from_clerk()
        
        if not clerk_users:
            logger.info('No users found in Clerk or error occurred')
            return
        
        # Sync users with database
        db = get_db_session()
        try:
            # Count of users processed
            created_count = 0
            updated_count = 0
            
            for user in clerk_users:
                # Extract user data from Clerk response
                user_id = user.get('id')
                
                # Get the primary email address
                email = None
                email_addresses = user.get('email_addresses', [])
                for email_obj in email_addresses:
                    if email_obj.get('id') and email_obj.get('email_address'):
                        if email_obj.get('primary', False):
                            email = email_obj.get('email_address')
                            break
                        elif not email:  # Use the first email if no primary is found
                            email = email_obj.get('email_address')
                
                if not user_id or not email:
                    logger.warning(f"Incomplete user data from Clerk: id={user_id}, email={email}")
                    continue
                
                # Check if user exists in our database
                existing_user = crud.get_user(db, user_id)
                
                if existing_user:
                    # Update user data if needed
                    if existing_user.email != email:
                        existing_user.email = email
                        existing_user.updated_at = datetime.datetime.utcnow()
                        db.commit()
                        updated_count += 1
                else:
                    # Create new user
                    crud.create_user(db, user_id, email)
                    created_count += 1
            
            logger.info(f"Clerk sync completed: {created_count} users created, {updated_count} users updated")
        except Exception as e:
            logger.error(f"Error syncing users with database: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error in Clerk sync timer: {str(e)}")

# Folder Management Functions
@app.route(route="folders", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_folders(req: func.HttpRequest) -> func.HttpResponse:
    """List all folders for a user."""
    try:
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        
        # Get parent_id from query parameters if provided
        parent_id_str = req.params.get('parent_id')
        parent_id = int(parent_id_str) if parent_id_str else None
        
        # Get folder list from database
        db = get_db_session()
        try:
            folders = crud.get_folders_by_user(db, user_id, parent_id)
            
            # Convert folder objects to dictionary for JSON serialization
            folders_data = []
            for folder in folders:
                folders_data.append({
                    "id": folder.id,
                    "name": folder.name,
                    "parent_id": folder.parent_id,
                    "user_id": folder.user_id,
                    "path": folder.path,
                    "created_at": folder.created_at.isoformat() if folder.created_at else None,
                    "updated_at": folder.updated_at.isoformat() if folder.updated_at else None
                })
            
            return func.HttpResponse(
                body=json.dumps({"folders": folders_data}),
                status_code=200,
                mimetype="application/json"
            )
        finally:
            db.close()
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
        parent_id = req_body.get('parent_id')  # Optional parent_id
        
        # Get or create user
        email = req.headers.get('x-user-email')
        user = get_or_create_user(user_id, email)
        if not user:
            return create_error_response(500, "Failed to find or create user")
        
        # Create folder in database
        db = get_db_session()
        try:
            new_folder = crud.create_folder(db, folder_name, user_id, parent_id)
            
            # Convert folder object to dictionary for JSON serialization
            folder_data = {
                "id": new_folder.id,
                "name": new_folder.name,
                "parent_id": new_folder.parent_id,
                "user_id": new_folder.user_id,
                "path": new_folder.path,
                "created_at": new_folder.created_at.isoformat() if new_folder.created_at else None,
                "updated_at": new_folder.updated_at.isoformat() if new_folder.updated_at else None
            }
            
            return func.HttpResponse(
                body=json.dumps({"folder": folder_data}),
                status_code=201,
                mimetype="application/json"
            )
        finally:
            db.close()
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
        
        folder_id_str = req.route_params.get('folder_id')
        if not folder_id_str:
            return create_error_response(400, "Folder ID is required")
        
        folder_id = int(folder_id_str)
        
        # Delete folder from database
        db = get_db_session()
        try:
            # Verify the folder belongs to this user
            folder = crud.get_folder(db, folder_id)
            if not folder:
                return create_error_response(404, "Folder not found")
            
            if folder.user_id != user_id:
                return create_error_response(403, "You don't have permission to delete this folder")
            
            # Delete the folder
            success = crud.delete_folder(db, folder_id)
            
            if success:
                return func.HttpResponse(
                    body=json.dumps({
                        "success": True,
                        "message": "Folder deleted successfully"
                    }),
                    status_code=200,
                    mimetype="application/json"
                )
            else:
                return create_error_response(500, "Failed to delete folder")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error deleting folder: {str(e)}")
        return create_error_response(500, f"Failed to delete folder: {str(e)}")

# File Management Functions
@app.route(route="upload", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    """Upload a file to Azure Blob Storage."""
    try:
        user_id = get_user_id(req)
        folder_id_str = req.headers.get('x-folder-id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not folder_id_str:
            return create_error_response(400, "Folder ID is required in x-folder-id header")
            
        folder_id = int(folder_id_str)
        
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
        
        # Handle mock mode for testing
        if connection_string == "mock":
            logger.info(f"Mock: File {filename} uploaded to blob storage")
            blob_url = f"https://mock-storage.com/{blob_name}"
            
            # Get or create user
            email = req.headers.get('x-user-email')
            user = get_or_create_user(user_id, email)
            if not user:
                return create_error_response(500, "Failed to find or create user")
            
            # Save file to database
            db = get_db_session()
            try:
                file_obj = crud.create_file(
                    db, 
                    filename, 
                    user_id, 
                    blob_url,
                    file_size,
                    content_type,
                    folder_id
                )
                
                # Add a message to the OCR processing queue
                try:
                    # Create a message with the file information
                    message = {
                        "file_id": file_obj.id,
                        "user_id": user_id,
                        "folder_id": folder_id,
                        "blob_name": blob_name,
                        "container_name": "mock-container",
                        "filename": filename,
                        "content_type": content_type,
                        "size_bytes": file_size,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    
                    # Get the queue client and send the message
                    queue_client = get_queue_client()
                    
                    # Convert message to JSON string and encode as Base64 for Azure Functions compatibility
                    message_json = json.dumps(message)
                    message_bytes = message_json.encode('utf-8')
                    message_base64 = base64.b64encode(message_bytes).decode('utf-8')
                    
                    # Send the Base64-encoded message
                    queue_client.send_message(message_base64)
                    
                    # Update the file status to "processing"
                    file_obj = crud.update_file_status(db, file_obj.id, "processing")
                    
                    logger.info(f"Added file {filename} to OCR processing queue")
                except Exception as e:
                    logger.error(f"Error adding to queue: {str(e)}")
                    # Continue even if queue fails - we'll still return the file info
                
                # Convert file object to dictionary for JSON serialization
                file_data = {
                    "id": file_obj.id,
                    "name": file_obj.name,
                    "folder_id": file_obj.folder_id,
                    "blob_path": file_obj.blob_path,
                    "status": file_obj.status,
                    "size_bytes": file_obj.size_bytes,
                    "mime_type": file_obj.mime_type,
                    "created_at": file_obj.created_at.isoformat() if file_obj.created_at else None,
                    "updated_at": file_obj.updated_at.isoformat() if file_obj.updated_at else None
                }
                
                return func.HttpResponse(
                    body=json.dumps({"file": file_data}),
                    status_code=201,
                    mimetype="application/json"
                )
            finally:
                db.close()
        
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
        
        # Get or create user
        email = req.headers.get('x-user-email')
        user = get_or_create_user(user_id, email)
        if not user:
            return create_error_response(500, "Failed to find or create user")
        
        # Save file to database
        db = get_db_session()
        try:
            file_obj = crud.create_file(
                db, 
                filename, 
                user_id, 
                blob_url,
                file_size,
                content_type,
                folder_id
            )
            
            # Add a message to the OCR processing queue
            try:
                # Create a message with the file information
                message = {
                    "file_id": file_obj.id,
                    "user_id": user_id,
                    "folder_id": folder_id,
                    "blob_name": blob_name,
                    "container_name": container_name,
                    "filename": filename,
                    "content_type": content_type,
                    "size_bytes": file_size,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Get the queue client and send the message
                queue_client = get_queue_client()
                
                # Convert message to JSON string and encode as Base64 for Azure Functions compatibility
                message_json = json.dumps(message)
                message_bytes = message_json.encode('utf-8')
                message_base64 = base64.b64encode(message_bytes).decode('utf-8')
                
                # Send the Base64-encoded message
                queue_client.send_message(message_base64)
                
                # Update the file status to "processing"
                file_obj = crud.update_file_status(db, file_obj.id, "processing")
                
                logger.info(f"Added file {filename} to OCR processing queue")
            except Exception as e:
                logger.error(f"Error adding to queue: {str(e)}")
                # Continue even if queue fails - we'll still return the file info
            
            # Convert file object to dictionary for JSON serialization
            file_data = {
                "id": file_obj.id,
                "name": file_obj.name,
                "folder_id": file_obj.folder_id,
                "blob_path": file_obj.blob_path,
                "status": file_obj.status,
                "size_bytes": file_obj.size_bytes,
                "mime_type": file_obj.mime_type,
                "created_at": file_obj.created_at.isoformat() if file_obj.created_at else None,
                "updated_at": file_obj.updated_at.isoformat() if file_obj.updated_at else None
            }
            
            return func.HttpResponse(
                body=json.dumps({"file": file_data}),
                status_code=201,
                mimetype="application/json"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return create_error_response(500, f"Failed to upload file: {str(e)}")

@app.route(route="files", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    """List all files in a folder."""
    try:
        user_id = get_user_id(req)
        folder_id_str = req.params.get('folder_id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not folder_id_str:
            return create_error_response(400, "Folder ID is required in query parameters")

        folder_id = int(folder_id_str)
        
        # Get file list from database
        db = get_db_session()
        try:
            files = crud.get_files_by_folder(db, folder_id, user_id)
            
            # Convert file objects to dictionary for JSON serialization
            files_data = []
            for file in files:
                files_data.append({
                    "id": file.id,
                    "name": file.name,
                    "folder_id": file.folder_id,
                    "blob_path": file.blob_path,
                    "status": file.status,
                    "size_bytes": file.size_bytes,
                    "mime_type": file.mime_type,
                    "created_at": file.created_at.isoformat() if file.created_at else None,
                    "updated_at": file.updated_at.isoformat() if file.updated_at else None,
                    "processed_at": file.processed_at.isoformat() if file.processed_at else None
                })
            
            return func.HttpResponse(
                body=json.dumps({"files": files_data}),
                status_code=200,
                mimetype="application/json"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return create_error_response(500, f"Failed to list files: {str(e)}")

@app.route(route="files", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a file."""
    try:
        user_id = get_user_id(req)
        file_id_str = req.params.get('id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not file_id_str:
            return create_error_response(400, "File ID is required in query parameters")
        
        file_id = int(file_id_str)
        
        # Delete file from database
        db = get_db_session()
        try:
            # Verify the file belongs to this user
            file = crud.get_file(db, file_id)
            if not file:
                return create_error_response(404, "File not found")
            
            if file.user_id != user_id:
                return create_error_response(403, "You don't have permission to delete this file")
            
            # Delete the file
            success = crud.delete_file(db, file_id)
            
            if success:
                # TODO: Also delete the blob from storage
                
                return func.HttpResponse(
                    body=json.dumps({
                        "success": True,
                        "message": "File deleted successfully"
                    }),
                    status_code=200,
                    mimetype="application/json"
                )
            else:
                return create_error_response(500, "Failed to delete file")
        finally:
            db.close()
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
            
            # Update usage statistics to count this query
            try:
                db = get_db_session()
                crud.update_queries_made(db, user_id, 1)
                db.close()
            except Exception as e:
                logger.error(f"Error updating query usage statistics: {str(e)}")
            
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
            
            # Update usage statistics to count this query
            try:
                db = get_db_session()
                crud.update_queries_made(db, user_id, 1)
                db.close()
            except Exception as e:
                logger.error(f"Error updating query usage statistics: {str(e)}")
            
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
        
        # Get date range parameters (defaults to today)
        from datetime import date, timedelta
        today = date.today()
        
        # Default to last 30 days if not specified
        start_date_str = req.params.get('start_date')
        end_date_str = req.params.get('end_date')
        
        try:
            start_date = date.fromisoformat(start_date_str) if start_date_str else today - timedelta(days=30)
            end_date = date.fromisoformat(end_date_str) if end_date_str else today
        except ValueError:
            return create_error_response(400, "Invalid date format. Use ISO format (YYYY-MM-DD)")
        
        # Get usage stats from database
        db = get_db_session()
        try:
            # Make sure we have stats for today
            stats_today = crud.get_or_create_usage_stat(db, user_id)
            
            # Get all stats for the date range
            stats = crud.get_usage_stats_by_user(db, user_id, start_date, end_date)
            
            # Calculate aggregated usage
            total_pages = sum(stat.pages_processed for stat in stats)
            total_queries = sum(stat.queries_made for stat in stats)
            total_storage = sum(stat.storage_bytes for stat in stats)
            
            # Get the most recent update time
            last_updated = max((stat.updated_at for stat in stats), default=None)
            
            # Format the usage data for the response
            usage_data = {
                "total": {
                    "pages_processed": total_pages,
                    "queries_made": total_queries,
                    "storage_bytes": total_storage,
                    "last_updated": last_updated.isoformat() if last_updated else None
                },
                "today": {
                    "pages_processed": stats_today.pages_processed,
                    "queries_made": stats_today.queries_made,
                    "storage_bytes": stats_today.storage_bytes,
                    "last_updated": stats_today.updated_at.isoformat() if stats_today.updated_at else None
                },
                "daily": [
                    {
                        "date": stat.date.isoformat(),
                        "pages_processed": stat.pages_processed,
                        "queries_made": stat.queries_made,
                        "storage_bytes": stat.storage_bytes
                    }
                    for stat in stats
                ]
            }
            
            return func.HttpResponse(
                body=json.dumps({"usage": usage_data}),
                status_code=200,
                mimetype="application/json"
            )
        finally:
            db.close()
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
        # Parse the message content - no need to decode Base64 as Azure Functions does it automatically
        message_text = msg.get_body().decode('utf-8')
        message = json.loads(message_text)
        
        logger.info(f"Processing OCR job: {message}")
        
        # Extract message data
        file_id = message.get('file_id')
        user_id = message.get('user_id')
        blob_name = message.get('blob_name')
        container_name = message.get('container_name')
        filename = message.get('filename')
        
        if not all([file_id, user_id, blob_name, container_name]):
            logger.error(f"Missing required fields in message: {message}")
            return
        
        # 1. Get blob storage connection
        connection_string = os.environ.get('AzureWebJobsStorage')
        if not connection_string:
            logger.error("Missing storage connection string")
            return
            
        # 2. Download the file from blob storage
        from azure.storage.blob import BlobServiceClient
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Create a temp file to store the downloaded document
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            download_stream = blob_client.download_blob()
            temp_file.write(download_stream.readall())
        
        # 3. Process the document with Azure Document Intelligence
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Document Intelligence credentials from environment
        di_endpoint = os.environ.get('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        di_key = os.environ.get('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not di_endpoint or not di_key:
            logger.error("Missing Document Intelligence credentials")
            os.unlink(temp_file_path)  # Clean up the temp file
            return
        
        # Initialize the Document Intelligence Client
        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=di_endpoint,
            credential=AzureKeyCredential(di_key)
        )
        
        # Process the document with layout analysis
        with open(temp_file_path, "rb") as document_file:
            logger.info(f"Starting OCR processing for file {filename}")
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-layout", 
                body=document_file
            )
            result = poller.result()
        
        # Log detailed information about the OCR result
        logger.info(f"Document analysis complete for {filename}")
        logger.info(f"Pages found: {len(result.pages)}")
        
        # Log first page details
        if result.pages:
            page = result.pages[0]
            logger.info(f"First page details - Page number: {page.page_number}, Lines: {len(page.lines)}")
            # Log first few lines of content
            if page.lines and len(page.lines) > 0:
                sample_content = "\n".join([line.content for line in page.lines[:5]])
                logger.info(f"Sample content:\n{sample_content}")
        else:
            logger.warning(f"No pages found in document {filename}")
        
        # Clean up the temp file
        os.unlink(temp_file_path)
        
        # 4. Extract text and content
        document_text = ""
        page_texts = {}
        page_count = len(result.pages)
        
        # Process each page of the document
        for page in result.pages:
            page_number = page.page_number
            
            # Extract the text from lines
            page_content = ""
            for line in page.lines:
                page_content += line.content + "\n"
            
            page_texts[page_number] = page_content
            document_text += page_content + "\n\n"
        
        # 5. Index each page in the search service
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search credentials from environment
        search_endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT')
        search_api_key = os.environ.get('AZURE_AISEARCH_KEY')
        search_index_name = os.environ.get('AZURE_AISEARCH_INDEX')
        
        if not search_endpoint or not search_api_key or not search_index_name:
            logger.error("Missing Azure AI Search credentials")
            return
        
        # Create the search client
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index_name,
            credential=AzureKeyCredential(search_api_key)
        )
        
        # Index each page
        indexed_pages = 0
        for page_number, page_content in page_texts.items():
            if not page_content.strip():
                logger.warning(f"Empty content for page {page_number}, skipping indexing")
                continue
                
            # Create a unique document ID
            document_id = f"{user_id}-{file_id}-{page_number}"
            
            # Create metadata
            metadata = {
                "user_id": user_id,
                "file_id": file_id,
                "filename": filename,
                "pageNumber": page_number,
                "totalPages": page_count,
                "blobUrl": blob_client.url,
            }
            
            # Create the search document
            search_document = {
                "id": document_id,
                "content": page_content,
                "metadata": json.dumps(metadata)
            }
            
            # Index the document
            try:
                result = search_client.upload_documents(documents=[search_document])
                if result[0].succeeded:
                    indexed_pages += 1
                    logger.info(f"Indexed page {page_number} of {filename}")
                else:
                    logger.error(f"Failed to index page {page_number}: {result[0].error_message}")
            except Exception as e:
                logger.error(f"Error indexing page {page_number}: {str(e)}")
        
        # 6. Update the file status in the database
        db = get_db_session()
        try:
            # Create the metadata to save with the file
            file_metadata = {
                "pageCount": page_count,
                "indexedPages": indexed_pages,
                "contentLength": len(document_text),
                "processedAt": datetime.datetime.now().isoformat()
            }
            
            # Update the file status
            success = False
            if indexed_pages > 0:
                # Update the file to completed status with metadata
                file_obj = crud.update_file_status(db, file_id, "completed", file_metadata)
                success = file_obj is not None
                
                # Update the user's usage statistics
                if success:
                    crud.update_pages_processed(db, user_id, page_count)
                    logger.info(f"Updated usage statistics for user {user_id} with {page_count} pages")
            else:
                # If we failed to index any pages, mark as error
                error_message = f"Failed to index any pages from the document"
                file_obj = crud.update_file_status(db, file_id, "error", error_message=error_message)
                success = file_obj is not None
            
            if success:
                logger.info(f"Updated file status for {filename} to {file_obj.status}")
            else:
                logger.error(f"Failed to update file status for {filename}")
        except Exception as e:
            logger.error(f"Error updating file status: {str(e)}")
        finally:
            db.close()
            
        logger.info(f"OCR processing completed for {filename}. Indexed {indexed_pages} of {page_count} pages.")
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

# Document Processing Status Function
@app.route(route="processing-status/{file_id}", auth_level=func.AuthLevel.ANONYMOUS)
def processing_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get the processing status of a file."""
    try:
        user_id = get_user_id(req)
        file_id_str = req.route_params.get('file_id')
        
        if not user_id:
            return create_error_response(400, "User ID is required in x-user-id header")
        if not file_id_str:
            return create_error_response(400, "File ID is required in route parameters")
            
        file_id = int(file_id_str)
        
        # Get file status from database
        db = get_db_session()
        try:
            file = crud.get_file(db, file_id)
            
            if not file:
                return create_error_response(404, f"File with ID {file_id} not found")
                
            # Verify the file belongs to this user
            if file.user_id != user_id:
                return create_error_response(403, "You don't have permission to access this file")
            
            # Extract metadata
            metadata = file.file_metadata or {}
            
            # Format the processing status response
            processing_data = {
                "file_id": file.id,
                "name": file.name,
                "status": file.status,
                "progress": 100 if file.status == "completed" else (50 if file.status == "processing" else 0),
                "error": file.error_message,
                "started_at": file.created_at.isoformat() if file.created_at else None,
                "completed_at": file.processed_at.isoformat() if file.processed_at else None,
                "pages_processed": metadata.get("indexedPages", 0),
                "total_pages": metadata.get("pageCount", 0),
                "attempts": file.attempts
            }
            
            return func.HttpResponse(
                body=json.dumps({"processing": processing_data}),
                status_code=200,
                mimetype="application/json"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error retrieving processing status: {str(e)}")
        return create_error_response(500, f"Failed to retrieve processing status: {str(e)}")
