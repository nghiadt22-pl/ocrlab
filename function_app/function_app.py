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
import sys
import time
import uuid
import re
import math
from datetime import datetime, date
import traceback

# Import database modules
from database.connection import get_db_session
from database import crud
from database.models import User, Folder, File, UsageStat

# Import Azure Document Intelligence
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError

# Azure Storage and Search
from azure.storage.queue import QueueServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocrlab')

# Verify environment variables on startup
def verify_environment_variables():
    """Verify that all required environment variables are set."""
    required_vars = [
        'POSTGRES_CONNECTION_STRING',
        'AzureWebJobsStorage',
        'CLERK_API_KEY'
    ]
    
    # Optional in mock mode, required in production
    if os.environ.get('AzureWebJobsStorage') != "mock":
        required_vars.extend([
            'DOCUMENT_INTELLIGENCE_ENDPOINT',
            'DOCUMENT_INTELLIGENCE_API_KEY'
        ])
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.warning("Some functionality may not work correctly without these variables.")
    else:
        logger.info("All required environment variables are set.")

# Run verification on startup
verify_environment_variables()

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
@app.function_name("UploadFile")
@app.route(route="api/files", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    """Handle file upload and queue it for OCR processing."""
    try:
        # Extract user ID from request
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(401, "Unauthorized: User ID not provided")
            
        # Parse request form data
        req_body = req.get_json()
        if not req_body:
            return create_error_response(400, "Bad request: No form data provided")
        
        folder_id = req_body.get('folder_id')
        name = req_body.get('name')
        mime_type = req_body.get('mime_type')
        size_bytes = req_body.get('size_bytes')
        sas_url = req_body.get('sas_url')  # SAS URL for the uploaded file
        blob_path = req_body.get('blob_path')  # Path in blob storage
        
        if not all([name, blob_path]):
            return create_error_response(400, "Bad request: Missing required fields")
        
        # Get or create user
        db = get_db_session()
        try:
            # Check user exists in DB
            user = crud.get_user(db, user_id)
            if not user:
                return create_error_response(404, f"User not found: {user_id}")
                
            # Validate folder_id if provided
            if folder_id:
                folder = crud.get_folder(db, folder_id)
                if not folder:
                    return create_error_response(404, f"Folder not found: {folder_id}")
                if folder.user_id != user_id:
                    return create_error_response(403, "Unauthorized: You do not have access to this folder")
            
            # Create file record in database
            file = crud.create_file(
                db, 
                name=name, 
                folder_id=folder_id, 
                user_id=user_id,
                blob_path=blob_path,
                size_bytes=size_bytes,
                mime_type=mime_type,
                status='queued'  # Initial status
            )
            
            # Log file creation
            logger.info(f"File {name} created with ID {file.id}")
            
            # Queue file for OCR processing
            queue_client = get_queue_client()
            
            # Prepare message
            message = {
                'file_id': file.id,
                'user_id': user_id
            }
            
            # Encode message as JSON
            message_json = json.dumps(message)
            
            # Send message to queue
            queue_client.send_message(message_json)
            
            # Return success response
            return func.HttpResponse(
                body=json.dumps({
                    "id": file.id,
                    "name": file.name,
                    "folder_id": file.folder_id,
                    "status": file.status,
                    "created_at": file.created_at.isoformat() if file.created_at else None
                }),
                status_code=201,
                mimetype="application/json"
            )
        finally:
            if 'db' in locals():
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

# OCR Processing Queue Function
@app.function_name("ProcessOCRQueue")
@app.queue_trigger(arg_name="msg", queue_name="ocr-processing-queue", connection="AzureWebJobsStorage")
def process_ocr_queue(msg: func.QueueMessage) -> None:
    """
    Process files from the OCR queue using Azure Document Intelligence.
    
    This function is triggered by messages in the ocr-processing-queue.
    Each message should contain a JSON object with file_id and user_id.
    """
    try:
        # Get message data
        message_text = msg.get_body().decode('utf-8')
        logger.info(f"Processing OCR queue message: {message_text}")
        
        message_data = json.loads(message_text)
        file_id = message_data.get('file_id')
        user_id = message_data.get('user_id')
        
        if not file_id or not user_id:
            logger.error(f"Invalid queue message: missing file_id or user_id: {message_text}")
            return
        
        # Get file from database
        db = get_db_session()
        try:
            file = crud.get_file(db, file_id)
            
            if not file:
                logger.error(f"File not found: {file_id}")
                return
        
            # Update file status to processing
            file = crud.update_file(db, file_id, {
                'status': 'processing',
                'attempts': file.attempts + 1,
                'last_attempt_at': datetime.datetime.utcnow()
            })
            
            # Get blob URL with SAS token
            from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
            from datetime import datetime, timedelta
            
            # Get connection string from environment variable
            connection_string = os.environ.get('AzureWebJobsStorage')
            
            # Check if we're in mock mode for testing
            if connection_string == "mock":
                # Mock processing for testing
                logger.info(f"Mock: Processing OCR for file {file_id}")
                
                # Create mock result
                ocr_result = {
                    "text": f"Mock OCR content for file {file_id}",
                    "tables": [{"row_count": 2, "column_count": 2, "cells": []}],
                    "pages": [{"page_number": 1, "width": 8.5, "height": 11.0}],
                    "page_count": 1,
                    "images": []
                }
                
                # Update file with mock results
                file = crud.update_file(db, file_id, {
                    'status': 'complete',
                    'processed_at': datetime.utcnow(),
                    'file_metadata': {
                        'ocr_result': ocr_result,
                        'page_count': 1,
                        'chunks': ['Mock OCR content for file ' + str(file_id)]
                    }
                })
                
                # Update usage stats
                crud.update_usage_stats(db, user_id, datetime.utcnow().date(), 1, 0, 0)
                
                logger.info(f"Mock: OCR processing completed for file {file_id}")
                return
            
            # Get blob service client
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            
            # Get container and blob name from file.blob_path
            blob_path = file.blob_path
            container_name, blob_name = blob_path.split('/', 1)
            
            # Get blob client
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            
            # Generate SAS token for blob
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=container_name,
                blob_name=blob_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1)
            )
            
            # Create blob URL with SAS token
            blob_url = f"{blob_client.url}?{sas_token}"
            
            # Process document with Azure Document Intelligence
            analyze_result = process_document(blob_url)
            
            # Extract content from analyze result
            ocr_result = extract_document_content(analyze_result)
            
            # Chunk text for vector database
            text_chunks = chunk_text(ocr_result['text'])
            
            # Update file with OCR results
            file = crud.update_file(db, file_id, {
                'status': 'complete',
                'processed_at': datetime.utcnow(),
                'file_metadata': {
                    'ocr_result': ocr_result,
                    'page_count': ocr_result['page_count'],
                    'chunks': text_chunks
                }
            })
            
            # Update usage stats
            crud.update_usage_stats(db, user_id, datetime.utcnow().date(), ocr_result['page_count'], 0, 0)
            
            logger.info(f"OCR processing completed for file {file_id}")
        except Exception as e:
            logger.error(f"Error processing OCR for file {file_id}: {str(e)}")
            
            # Update file status to error
            if 'file' in locals() and file:
                crud.update_file(db, file_id, {
                    'status': 'error',
                    'error_message': str(e)
                })
        finally:
            if 'db' in locals():
                db.close()
    except Exception as e:
        logger.error(f"Error processing OCR queue message: {str(e)}")

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

# Helper functions for Azure Document Intelligence
def get_document_intelligence_client():
    """Create Azure Document Intelligence client."""
    try:
        # Get API key and endpoint from environment variables
        endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
        api_key = os.environ.get("DOCUMENT_INTELLIGENCE_API_KEY")
        
        if not endpoint or not api_key:
            logger.error("Missing Document Intelligence configuration")
            raise ValueError("Document Intelligence not properly configured")
            
        # Create client
        credential = AzureKeyCredential(api_key)
        client = DocumentIntelligenceClient(endpoint, credential)
        return client
    except Exception as e:
        logger.error(f"Error creating Document Intelligence client: {str(e)}")
        raise

def process_document(blob_url: str, model: str = "prebuilt-layout"):
    """
    Process a document using Azure Document Intelligence.
    
    Args:
        blob_url: The SAS URL to the document in Azure Blob Storage
        model: The model to use (prebuilt-layout, prebuilt-document, etc.)
        
    Returns:
        AnalyzeResult: The result of the document analysis
    """
    try:
        client = get_document_intelligence_client()
        
        # Check if we're in mock mode for testing
        if os.environ.get('AzureWebJobsStorage') == "mock":
            logger.info(f"Mock: Processing document at {blob_url}")
            # Return mock data for testing
            return {
                "content": "This is mock OCR content for testing.",
                "tables": [{"rowCount": 2, "columnCount": 2, "cells": []}],
                "pages": [{"pageNumber": 1, "width": 8.5, "height": 11.0}]
            }
            
        # Start the document analysis process using the new method
        # Use AnalyzeDocumentRequest with url_source parameter
        from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
        
        # Create the request with url_source parameter
        request = AnalyzeDocumentRequest(url_source=blob_url)
        
        # Call begin_analyze_document with the request
        poller = client.begin_analyze_document(model, body=request)
        result = poller.result()
        
        return result
    except ResourceNotFoundError as e:
        logger.error(f"Document not found: {str(e)}")
        raise
    except ServiceRequestError as e:
        logger.error(f"Service request error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

def extract_document_content(analyze_result):
    """
    Extract content from Document Intelligence analyze result.
    
    Args:
        analyze_result: The result from Azure Document Intelligence
        
    Returns:
        dict: Extracted content including text, tables, and images
    """
    try:
        # For mock data
        if isinstance(analyze_result, dict) and "content" in analyze_result:
            return {
                "text": analyze_result["content"],
                "tables": analyze_result.get("tables", []),
                "pages": analyze_result.get("pages", []),
                "page_count": len(analyze_result.get("pages", [])),
                "images": []
            }
            
        # Extract full text content
        text = analyze_result.content
        
        # Extract tables
        tables = []
        for table in analyze_result.tables:
            table_data = {
                "row_count": table.row_count,
                "column_count": table.column_count,
                "cells": []
            }
            
            # Process cells
            for cell in table.cells:
                cell_data = {
                    "row_index": cell.row_index,
                    "column_index": cell.column_index,
                    "row_span": cell.row_span,
                    "column_span": cell.column_span,
                    "content": cell.content
                }
                table_data["cells"].append(cell_data)
                
            tables.append(table_data)
            
        # Extract page information
        pages = []
        for page in analyze_result.pages:
            page_data = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": []
            }
            
            # Extract lines if available
            if hasattr(page, "lines"):
                for line in page.lines:
                    line_data = {
                        "content": line.content,
                        "bounding_box": line.polygon if hasattr(line, "polygon") else None
                    }
                    page_data["lines"].append(line_data)
                    
            pages.append(page_data)
            
        # Extract images (if available)
        images = []
        if hasattr(analyze_result, "images") and analyze_result.images:
            for img in analyze_result.images:
                image_data = {
                    "page_number": getattr(img, "page_number", None),
                    "bounding_box": getattr(img, "bounding_box", None),
                    # Add any additional image metadata
                }
                images.append(image_data)
        
        return {
            "text": text,
            "tables": tables,
            "pages": pages,
            "page_count": len(pages),
            "images": images
        }
    except Exception as e:
        logger.error(f"Error extracting document content: {str(e)}")
        raise

def chunk_text(text, max_chunk_size=1000, overlap=100):
    """
    Split text into overlapping chunks for vector database storage.
    
    Args:
        text: The text to chunk
        max_chunk_size: Maximum characters per chunk
        overlap: Number of characters of overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    
    while start < len(text):
        # Define end position for this chunk
        end = min(start + max_chunk_size, len(text))
        
        # If we're not at the end of the text, try to break at a sentence
        if end < len(text):
            # Look for sentence boundaries (., !, ?) followed by space
            for delimiter in [". ", "! ", "? "]:
                last_delimiter = text.rfind(delimiter, start, end)
                if last_delimiter != -1:
                    end = last_delimiter + 2  # Include the delimiter and space
                    break
                    
        chunks.append(text[start:end])
        
        # Move start position with overlap
        start = end - overlap if end - overlap > start else end
        
    return chunks

# Timer-triggered retry function for failed OCR jobs
@app.function_name("RetryFailedOCRJobs")
@app.timer_trigger(schedule="0 */15 * * * *", arg_name="myTimer", run_on_startup=False)
def retry_failed_ocr_jobs(myTimer: func.TimerRequest) -> None:
    """
    Periodically checks for failed OCR jobs and retries them.
    Runs every 15 minutes and looks for files with 'error' status
    and less than MAX_RETRY_ATTEMPTS attempts.
    """
    MAX_RETRY_ATTEMPTS = 3
    MAX_AGE_HOURS = 24  # Don't retry files older than this
    
    if myTimer.past_due:
        logger.info('Retry timer is past due')
    
    logger.info('Checking for failed OCR jobs to retry')
    
    try:
        # Get files with error status that haven't exceeded max attempts
        db = get_db_session()
        try:
            # Calculate the cutoff time (don't retry files older than MAX_AGE_HOURS)
            cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=MAX_AGE_HOURS)
            
            # Get failed files from database
            failed_files = crud.get_failed_files(db, max_attempts=MAX_RETRY_ATTEMPTS, cutoff_time=cutoff_time)
            
            if not failed_files:
                logger.info("No failed OCR jobs to retry")
                return
                
            logger.info(f"Found {len(failed_files)} failed OCR jobs to retry")
            
            # Get the queue client
            queue_client = get_queue_client()
            
            # Retry each file
            for file in failed_files:
                logger.info(f"Queuing retry for file {file.id}: attempt {file.attempts + 1} of {MAX_RETRY_ATTEMPTS}")
                
                # Send message to OCR processing queue
                message = {
                    'file_id': file.id,
                    'user_id': file.user_id,
                    'retry': True,
                    'attempt': file.attempts + 1
                }
                
                # Update file status to indicate it's being retried
                crud.update_file(db, file.id, {
                    'status': 'queued',
                    'error_message': f"Previous error: {file.error_message}. Retrying job."
                })
                
                # Encode message as JSON and send to queue
                message_json = json.dumps(message)
                queue_client.send_message(message_json)
                
                logger.info(f"Requeued file {file.id} for OCR processing")
            
            logger.info(f"Retry job completed: queued {len(failed_files)} files for reprocessing")
        except Exception as e:
            logger.error(f"Error retrying failed OCR jobs: {str(e)}")
        finally:
            if 'db' in locals():
                db.close()
    except Exception as e:
        logger.error(f"Error in retry timer function: {str(e)}")
