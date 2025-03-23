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
import time
import uuid
import re
import math
from datetime import datetime, date, timedelta
import traceback

# Import database modules
from database.connection import get_db_session
from database import crud
from database.models import User, Folder, File, UsageStat

# Import Azure Document Intelligence
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError

# Azure Storage and Search
from azure.storage.queue import QueueServiceClient
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery, QueryType
from openai import AzureOpenAI

# Import the services
from services.chunking import ChunkingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ocrlab')

# Initialize clients at global scope
document_intelligence_client = None
openai_client = None
ai_search_client = None
blob_service_client = None

def initialize_azure_clients():
    """Initialize Azure clients at module level for better performance."""
    global document_intelligence_client, openai_client, ai_search_client, blob_service_client
    
    # Initialize Document Intelligence client
    try:
        doc_endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        doc_key = os.environ.get("DOCUMENT_INTELLIGENCE_API_KEY") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if doc_endpoint and doc_key:
            document_intelligence_client = DocumentIntelligenceClient(doc_endpoint, AzureKeyCredential(doc_key))
            logger.info("Document Intelligence client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Document Intelligence client: {str(e)}")
    
    # Initialize OpenAI client
    try:
        api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
        api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
        
        if api_key and api_endpoint and api_version:
            openai_client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=api_endpoint,
                timeout=30.0
            )
            logger.info("Azure OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
    
    # Initialize AI Search client
    try:
        search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
        search_key = os.environ.get("AZURE_AISEARCH_KEY")
        search_index = os.environ.get("AZURE_AISEARCH_INDEX")
        
        if search_endpoint and search_key and search_index:
            ai_search_client = SearchClient(search_endpoint, search_index, AzureKeyCredential(search_key))
            logger.info("Azure AI Search client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure AI Search client: {str(e)}")
    
    # Initialize Blob Storage client
    try:
        connection_string = os.environ.get("AzureWebJobsStorage")
        
        if connection_string:
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            logger.info("Azure Blob Storage client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Blob Storage client: {str(e)}")

def get_document_intelligence_client():
    """
    Get the Document Intelligence client, initializing it if necessary.
    
    Returns:
        DocumentIntelligenceClient: The initialized client
    """
    global document_intelligence_client
    
    # If client already initialized, return it
    if document_intelligence_client is not None:
        return document_intelligence_client
    
    # Initialize client
    try:
        doc_endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        doc_key = os.environ.get("DOCUMENT_INTELLIGENCE_API_KEY") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not doc_endpoint or not doc_key:
            raise ValueError("Missing Document Intelligence endpoint or key environment variables")
        
        document_intelligence_client = DocumentIntelligenceClient(doc_endpoint, AzureKeyCredential(doc_key))
        logger.info("Document Intelligence client initialized on demand")
        return document_intelligence_client
    except Exception as e:
        logger.error(f"Failed to initialize Document Intelligence client: {str(e)}")
        raise

def get_openai_client():
    """
    Get the Azure OpenAI client, initializing it if necessary.
    
    Returns:
        AzureOpenAI: The initialized client
    """
    global openai_client
    
    # If client already initialized, return it
    if openai_client is not None:
        return openai_client
    
    # Initialize client
    try:
        api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
        api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
        
        if not api_key or not api_endpoint or not api_version:
            raise ValueError("Missing OpenAI API environment variables")
        
        openai_client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=api_endpoint,
            timeout=30.0
        )
        logger.info("Azure OpenAI client initialized on demand")
        return openai_client
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
        raise

def get_search_client():
    """
    Get the Azure AI Search client, initializing it if necessary.
    
    Returns:
        SearchClient: The initialized client
    """
    global ai_search_client
    
    # If client already initialized, return it
    if ai_search_client is not None:
        return ai_search_client
    
    # Initialize client
    try:
        search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
        search_key = os.environ.get("AZURE_AISEARCH_KEY")
        search_index = os.environ.get("AZURE_AISEARCH_INDEX")
        
        if not search_endpoint or not search_key or not search_index:
            raise ValueError("Missing Azure AI Search environment variables")
        
        ai_search_client = SearchClient(search_endpoint, search_index, AzureKeyCredential(search_key))
        logger.info("Azure AI Search client initialized on demand")
        return ai_search_client
    except Exception as e:
        logger.error(f"Failed to initialize Azure AI Search client: {str(e)}")
        raise

def get_blob_service_client():
    """
    Get the Azure Blob Storage client, initializing it if necessary.
    
    Returns:
        BlobServiceClient: The initialized client
    """
    global blob_service_client
    
    # If client already initialized, return it
    if blob_service_client is not None:
        return blob_service_client
    
    # Initialize client
    try:
        connection_string = os.environ.get("AzureWebJobsStorage")
        
        if not connection_string:
            raise ValueError("Missing Azure Storage connection string")
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        logger.info("Azure Blob Storage client initialized on demand")
        return blob_service_client
    except Exception as e:
        logger.error(f"Failed to initialize Azure Blob Storage client: {str(e)}")
        raise

def generate_blob_sas_url(container_name, blob_path, permissions=None, expiry_hours=1):
    """
    Generate a SAS URL for accessing a blob.
    
    Args:
        container_name: Name of the container
        blob_path: Path to the blob within the container
        permissions: BlobSasPermissions object, defaults to read only
        expiry_hours: Number of hours until the SAS token expires
        
    Returns:
        str: The full SAS URL to the blob
    """
    try:
        # Get the blob service client
        blob_service_client = get_blob_service_client()
        
        # Set default permissions to read if not specified
        if permissions is None:
            permissions = BlobSasPermissions(read=True)
        
        # Create an expiry time
        expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        # Get the account key from the connection string
        connection_string = os.environ.get("AzureWebJobsStorage")
        account_name = None
        account_key = None
        
        # Parse the connection string to get account name and key
        for part in connection_string.split(';'):
            if part.startswith('AccountName='):
                account_name = part.split('=', 1)[1]
            elif part.startswith('AccountKey='):
                account_key = part.split('=', 1)[1]
        
        if not account_name or not account_key:
            raise ValueError("Could not extract account name or key from connection string")
        
        # Generate the SAS token
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_path,
            account_key=account_key,
            permission=permissions,
            expiry=expiry_time
        )
        
        # Get the blob URL
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_path)
        
        # Construct the full SAS URL
        sas_url = f"{blob_client.url}?{sas_token}"
        
        return sas_url
    except Exception as e:
        logger.error(f"Error generating SAS URL: {str(e)}")
        raise

# Initialize clients when module loads
initialize_azure_clients()

# Create the function app
app = func.FunctionApp()

# Helper functions and standardized utilities
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

def create_success_response(data, status_code=200):
    """Create a standardized success response."""
    return func.HttpResponse(
        body=json.dumps(data),
        status_code=status_code,
        mimetype="application/json"
    )

def validate_user_request(req):
    """Validate that a request has a user ID."""
    user_id = get_user_id(req)
    if not user_id:
        return None, create_error_response(401, "Unauthorized: User ID not provided")
    return user_id, None

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
@app.route(route="api/folders", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_folders(req: func.HttpRequest) -> func.HttpResponse:
    """List all folders for a user."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
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
            
            return create_success_response({"folders": folders_data})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}")
        return create_error_response(500, f"Failed to list folders: {str(e)}")

@app.route(route="api/folders", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def create_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new folder for a user."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
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
            
            return create_success_response({"folder": folder_data}, 201)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return create_error_response(500, f"Failed to create folder: {str(e)}")

@app.route(route="api/folders/{folder_id}", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def delete_folder(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a folder."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
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
                return create_success_response({
                    "success": True,
                    "message": "Folder deleted successfully"
                })
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
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
            
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
                mime_type=mime_type
            )
            
            # Log file creation
            logger.info(f"File {name} created with ID {file.id}")
            
            # Queue file for OCR processing
            queue_client = get_queue_client()
            
            # Prepare message
            message = {
                'file_id': file.id,
                'user_id': user_id,
                'blob_path': blob_path
            }
            
            # Encode message as JSON
            message_json = json.dumps(message)
            
            # Send message to queue
            queue_client.send_message(message_json)
            
            # Return success response
            return create_success_response({
                "id": file.id,
                "name": file.name,
                "folder_id": file.folder_id,
                "status": file.status,
                "created_at": file.created_at.isoformat() if file.created_at else None
            }, 201)
        finally:
            if 'db' in locals():
                db.close()
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return create_error_response(500, f"Failed to upload file: {str(e)}")

@app.route(route="api/files", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_files(req: func.HttpRequest) -> func.HttpResponse:
    """List all files in a folder."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
            
        folder_id_str = req.params.get('folder_id')
        
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
            
            return create_success_response({"files": files_data})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return create_error_response(500, f"Failed to list files: {str(e)}")

@app.route(route="api/files/{file_id}", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a file."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
            
        file_id_str = req.route_params.get('file_id')
        if not file_id_str:
            return create_error_response(400, "File ID is required in route parameters")
        
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
                
                return create_success_response({
                    "success": True,
                    "message": "File deleted successfully"
                })
            else:
                return create_error_response(500, "Failed to delete file")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return create_error_response(500, f"Failed to delete file: {str(e)}")

# Search Functions
@app.route(route="api/query", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def search_query(req: func.HttpRequest) -> func.HttpResponse:
    """Perform a vector search query."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return create_error_response(400, "Query is required")
        
        query = req_body.get('query')
        top = req_body.get('top', 5)  # Default to 5 results
        
        # Connect to Azure Search Service
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search credentials from environment
        endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT')
        search_api_key = os.environ.get('AZURE_AISEARCH_KEY')
        search_index_name = os.environ.get('AZURE_AISEARCH_INDEX')
        
        if not endpoint or not search_api_key or not search_index_name:
            logger.error("Azure AI Search not properly configured")
            return create_error_response(500, "Search service not properly configured")
        
        # Create the search client
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=search_index_name,
            credential=AzureKeyCredential(search_api_key)
        )
                        
        # Set up search options
        # Select only fields that actually exist in the index
        select_fields = ["chunk_id", "chunk", "title", "header_1", "header_2", "header_3", "user_id"]
        
        # Perform search query
        try:
            # Use standard search since semantic requires special configuration
            results = search_client.search(
                search_text=query,
                select=select_fields,
                top=top
            )
            
            # Process and format the results
            formatted_results = []
            for result in results:
                # Check if this document belongs to the user
                result_user_id = result.get("user_id", "")
                if result_user_id and result_user_id != user_id:
                    continue
                    
                # Format the result
                formatted_result = {
                    "id": result.get("chunk_id", ""),
                    "text": result.get("chunk", ""),
                    "score": result["@search.score"] if "@search.score" in result else 0,
                    "filename": result.get("title", ""),
                    "title": result.get("title", ""),
                    "page": result.get("header_2", "").replace("Page ", "") if result.get("header_2", "").startswith("Page ") else "",
                    "type": result.get("header_3", "")
                }
                
                formatted_results.append(formatted_result)
            
            # Update usage statistics to count this query
            try:
                db = get_db_session()
                crud.update_queries_made(db, user_id, 1)
                db.close()
            except Exception as e:
                logger.error(f"Error updating query usage statistics: {str(e)}")
            
            return create_success_response({"results": formatted_results})
        except Exception as e:
            logger.error(f"Error during search operation: {str(e)}")
            return create_error_response(500, f"Error during search operation: {str(e)}")
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        return create_error_response(500, f"Failed to perform search: {str(e)}")

# Usage Tracking Functions
@app.route(route="api/usage", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_usage(req: func.HttpRequest) -> func.HttpResponse:
    """Get usage statistics for a user."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
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
            
            return create_success_response({"usage": usage_data})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error retrieving usage data: {str(e)}")
        return create_error_response(500, f"Failed to retrieve usage data: {str(e)}")

# Document Processing Functions
@app.function_name("ProcessDocument")
@app.route(route="api/process_document", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def process_document(req: func.HttpRequest) -> func.HttpResponse:
    """Process a document through OCR, chunking, embedding, and indexing."""
    try:
        # Extract user ID from request headers
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(401, "Unauthorized: User ID not provided")
        
        # Get document from request
        document_bytes = req.get_body()
        if not document_bytes:
            return create_error_response(400, "Document content is required")
        
        # Get document metadata from request parameters
        document_title = req.params.get('title', 'Untitled document')
        document_id = req.params.get('id', f'doc_{document_title.replace(" ", "_")}')
        file_id = req.params.get('file_id')
        
        # Update file status in database if file_id is provided
        if file_id:
            try:
                db = get_db_session()
                file = crud.get_file(db, int(file_id), user_id)
                if not file:
                    db.close()
                    return create_error_response(404, f"File not found: {file_id}")
                
                # Update file status to processing
                crud.update_file_status(db, int(file_id), "processing")
                db.close()
            except Exception as e:
                logger.error(f"Error updating file status: {str(e)}")
                if 'db' in locals():
                    db.close()
        
        # Process document with Azure Document Intelligence
        try:
            # Get Document Intelligence client
            document_client = get_or_create_document_intelligence_client()
            
            # Process document
            poller = document_client.begin_analyze_document("prebuilt-layout", body=document_bytes)
            result = poller.result()
            
            # Extract structured content from result
            structured_content = extract_document_content(result)
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            # Update file status to error if file_id is provided
            if file_id:
                try:
                    db = get_db_session()
                    crud.update_file_status(db, int(file_id), "error", str(e))
                    db.close()
                except Exception as db_error:
                    logger.error(f"Error updating file status: {str(db_error)}")
                    if 'db' in locals():
                        db.close()
            return create_error_response(500, f"Error processing document with Document Intelligence: {str(e)}")
        
        # Chunk document content
        try:
            chunking_service = ChunkingService()
            chunks = chunking_service.chunk_document(structured_content, document_id, document_title)
        except Exception as e:
            logger.error(f"Error chunking document: {str(e)}")
            # Update file status to error if file_id is provided
            if file_id:
                try:
                    db = get_db_session()
                    crud.update_file_status(db, int(file_id), "error", str(e))
                    db.close()
                except Exception as db_error:
                    logger.error(f"Error updating file status: {str(db_error)}")
                    if 'db' in locals():
                        db.close()
            return create_error_response(500, f"Error chunking document: {str(e)}")
        
        # Generate embeddings for chunks using Azure OpenAI directly
        try:
            # Get credentials from environment variables
            api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
            api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
            deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
            
            if not api_key or not api_endpoint or not api_version or not deployment:
                raise ValueError("Azure OpenAI credentials not fully configured")
            
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            
            # Create the OpenAI client
            openai_client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=api_endpoint,
                timeout=30.0
            )
            
            # Process one chunk at a time (required for Azure OpenAI)
            chunks_with_vectors = []
            processed_count = 0
            
            for chunk_index, chunk in enumerate(chunks):
                try:
                    # Add delay between requests to avoid rate limiting
                    if processed_count > 0:
                        time.sleep(2)  # 2 second delay between chunks
                    
                    logger.info(f"Processing chunk {chunk_index+1}/{len(chunks)} with ID {chunk.get('id', 'unknown')}")
                    
                    # Truncate text if it's too long
                    text = chunk["text"]
                    max_text_length = 8000
                    if len(text) > max_text_length:
                        logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length}")
                        text = text[:max_text_length]
                    
                    # Generate embedding
                    response = openai_client.embeddings.create(
                        input=text,
                        model=deployment
                    )
                    
                    # Add embedding to the chunk
                    chunk["vector"] = response.data[0].embedding
                    chunks_with_vectors.append(chunk)
                    processed_count += 1
                    
                    logger.info(f"Successfully processed chunk {processed_count}/{len(chunks)}")
                    
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {chunk_index+1}/{len(chunks)}: {str(e)}")
                    # Don't retry - just skip this chunk and continue with the next one
            
            logger.info(f"Successfully generated embeddings for {len(chunks_with_vectors)} of {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Update file status to error if file_id is provided
            if file_id:
                try:
                    db = get_db_session()
                    crud.update_file_status(db, int(file_id), "error", str(e))
                    db.close()
                except Exception as db_error:
                    logger.error(f"Error updating file status: {str(db_error)}")
                    if 'db' in locals():
                        db.close()
            return create_error_response(500, f"Error generating embeddings: {str(e)}")
        
        # Index chunks in Azure AI Search directly
        try:
            # Get credentials from environment variables
            endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
            key = os.environ.get("AZURE_AISEARCH_KEY")
            index_name = os.environ.get("AZURE_AISEARCH_INDEX")
            
            if not endpoint or not key or not index_name:
                raise ValueError("Azure AI Search credentials not fully configured")
            
            logger.info(f"Indexing {len(chunks_with_vectors)} chunks for user {user_id}")
            
            # Create search client
            search_client = SearchClient(endpoint, index_name, AzureKeyCredential(key))
            
            # Prepare search documents - ONLY include chunks that got embeddings
            search_documents = []
            
            for chunk in chunks_with_vectors:
                # Include the parent document ID in the chunk ID to ensure uniqueness
                chunk_id = chunk["id"]
                
                # Create the search document
                search_document = {
                    "chunk_id": chunk_id,  # Primary key field
                    "text_parent_id": chunk["parent_id"],
                    "chunk": chunk["text"],
                    "title": chunk["document_title"],
                    "header_1": chunk.get("document_title", ""),  # Use document title as header_1
                    "header_2": f"Page {chunk['page']}",     # Use page number as header_2
                    "header_3": chunk["type"].capitalize(),   # Use type as header_3
                    "content_vector": chunk["vector"],
                    "user_id": user_id  # Include user_id for multi-tenancy
                }
                search_documents.append(search_document)
            
            # Split into batches if there are many documents
            batch_size = 1000  # Azure Search can handle up to 1000 documents in a single request
            
            indexed_count = 0
            failed_count = 0
            
            for i in range(0, len(search_documents), batch_size):
                batch = search_documents[i:i + batch_size]
                logger.info(f"Uploading batch of {len(batch)} documents to search index")
                
                # Upload documents to search index
                upload_result = search_client.upload_documents(documents=batch)
                
                # Log the results
                success_count = len([r for r in upload_result if r.succeeded])
                batch_failed_count = len([r for r in upload_result if not r.succeeded])
                
                indexed_count += success_count
                failed_count += batch_failed_count
                
                logger.info(f"Batch upload results: {success_count} succeeded, {batch_failed_count} failed")
                
                # If any failed, log detailed errors
                if batch_failed_count > 0:
                    for i, result in enumerate(upload_result):
                        if not result.succeeded:
                            logger.error(f"Error indexing document {i}: {result.status_code} - {result.message}")
            
            # Create result summary
            index_result = {
                "total_count": len(search_documents),
                "indexed_count": indexed_count,
                "failed_count": failed_count
            }
            
        except Exception as e:
            logger.error(f"Error indexing chunks: {str(e)}")
            # Update file status to error if file_id is provided
            if file_id:
                try:
                    db = get_db_session()
                    crud.update_file_status(db, int(file_id), "error", str(e))
                    db.close()
                except Exception as db_error:
                    logger.error(f"Error updating file status: {str(db_error)}")
                    if 'db' in locals():
                        db.close()
            return create_error_response(500, f"Error indexing chunks: {str(e)}")
        
        # Update file status to complete if file_id is provided
        if file_id:
            try:
                db = get_db_session()
                crud.update_file_status(db, int(file_id), "complete")
                # Update usage statistics
                pages_processed = len(set(chunk["page"] for chunk in chunks))
                crud.update_pages_processed(db, user_id, pages_processed)
                db.close()
            except Exception as e:
                logger.error(f"Error updating file status: {str(e)}")
                if 'db' in locals():
                    db.close()
        
        # Return success response with processing results
        return create_success_response({
            "document_id": document_id,
            "title": document_title,
            "chunks_count": len(chunks),
            "indexed_count": index_result["indexed_count"],
            "failed_count": index_result["failed_count"]
        })
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return create_error_response(500, f"Error processing document: {str(e)}")

# Vector Search Functions
@app.function_name("VectorSearch")
@app.route(route="api/vector_search", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def vector_search(req: func.HttpRequest) -> func.HttpResponse:
    """Perform a vector search query using embeddings."""
    try:
        # Extract user ID from request headers
        user_id = get_user_id(req)
        if not user_id:
            return create_error_response(401, "Unauthorized: User ID not provided")
        
        # Get request body
        req_body = req.get_json()
        if not req_body:
            return create_error_response(400, "Request body is required")
        
        # Extract query and parameters
        query = req_body.get('query')
        top_k = req_body.get('top_k', 5)
        
        if not query:
            return create_error_response(400, "query parameter is required")
        
        # Check required environment variables upfront
        api_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get("AZURE_OPENAI_API_KEY")
        api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        search_endpoint = os.environ.get("AZURE_AISEARCH_ENDPOINT")
        search_key = os.environ.get("AZURE_AISEARCH_KEY")
        search_index = os.environ.get("AZURE_AISEARCH_INDEX")
        
        missing_vars = []
        if not api_key:
            missing_vars.append("AZURE_OPENAI_API_KEY")
        if not api_endpoint:
            missing_vars.append("AZURE_OPENAI_ENDPOINT")
        if not api_version:
            missing_vars.append("AZURE_OPENAI_API_VERSION")
        if not deployment:
            missing_vars.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        if not search_endpoint:
            missing_vars.append("AZURE_AISEARCH_ENDPOINT")
        if not search_key:
            missing_vars.append("AZURE_AISEARCH_KEY")
        if not search_index:
            missing_vars.append("AZURE_AISEARCH_INDEX")
            
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            return create_error_response(500, f"Search service not properly configured: {error_msg}")
        
        # Generate embeddings for the query using Azure OpenAI directly
        try:
            logger.info(f"Generating embeddings using Azure OpenAI: endpoint={api_endpoint}, deployment={deployment}")
            
            # Create the OpenAI client
            openai_client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=api_endpoint,
                timeout=30.0
            )
            
            # Truncate text if it's too long
            max_text_length = 8000  # Approximate character limit for 8K tokens
            if len(query) > max_text_length:
                logger.warning(f"Query too long ({len(query)} chars), truncating to {max_text_length}")
                query = query[:max_text_length]
            
            # Generate embedding
            response = openai_client.embeddings.create(
                input=query,
                model=deployment
            )
            
            # Extract the embedding from the response
            query_vector = response.data[0].embedding
            logger.info(f"Generated embedding with {len(query_vector)} dimensions")
            
        except Exception as e:
            logger.error(f"Error generating query embeddings: {str(e)}")
            return create_error_response(500, f"Error generating query embeddings: {str(e)}")
        
        # Perform search using Azure AI Search directly
        try:
            logger.info(f"Performing vector search in Azure AI Search: endpoint={search_endpoint}, index={search_index}")
            
            # Create search client
            search_client = SearchClient(search_endpoint, search_index, AzureKeyCredential(search_key))
            
            # Build filter expression for user_id (multi-tenancy)
            filter_expression = f"user_id eq '{user_id}'"
            
            # Define vector query
            vector_queries = [
                {
                    "vector": query_vector,
                    "k": top_k,
                    "fields": "content_vector",
                    "kind": "vector"
                }
            ]
            
            # Execute search
            search_results = search_client.search(
                search_text=None,  # No text search
                vector_queries=vector_queries,
                filter=filter_expression,
                top=top_k,
                include_total_count=True
            )
            
            # Process results
            results = []
            for result in search_results:
                results.append({
                    "text": result.get("chunk", ""),
                    "page": int(result.get("header_2", "Page 0").replace("Page ", "")) if result.get("header_2") else 0,
                    "type": result.get("header_3", "Unknown").lower() if result.get("header_3") else "unknown",
                    "score": result.get("@search.score", 0.0),
                    "document_title": result.get("title", ""),
                    "parent_id": result.get("text_parent_id", "")
                })
            
            logger.info(f"Found {len(results)} results for vector search")
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            return create_error_response(500, f"Error performing vector search: {str(e)}")
        
        # Update usage statistics to count this query
        try:
            db = get_db_session()
            crud.update_queries_made(db, user_id, 1)
            db.close()
        except Exception as e:
            logger.error(f"Error updating query usage statistics: {str(e)}")
            if 'db' in locals():
                db.close()
        
        # Return results
        return create_success_response({"results": results})
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        return create_error_response(500, f"Error performing search: {str(e)}")

# Helper function for OCR Processing Queue
def process_document_from_queue(file_id, user_id, blob_path):
    """Process a document from the OCR queue using our new implementation."""
    try:
        logger.info(f"Processing document from queue: file_id={file_id}, user_id={user_id}")
        
        # Check required environment variables upfront
        container_name = os.environ.get("BLOB_CONTAINER_NAME")
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        
        if not container_name:
            error_msg = "Missing required environment variable: BLOB_CONTAINER_NAME"
            logger.error(error_msg)
            
            # Update file status to error
            db = get_db_session()
            crud.update_file_status(db, file_id, "error", error_msg)
            db.close()
            return
        
        if not deployment:
            error_msg = "Missing required environment variable: AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            logger.error(error_msg)
            
            # Update file status to error
            db = get_db_session()
            crud.update_file_status(db, file_id, "error", error_msg)
            db.close()
            return
        
        # Get the file from the database
        db = get_db_session()
        file = crud.get_file(db, file_id, user_id)
        if not file:
            logger.error(f"File not found: {file_id}")
            db.close()
            return
        
        # Update file status to processing
        crud.update_file_status(db, file_id, "processing")
        db.close()
        
        # Get the document content from blob storage
        try:
            # Use the getter function to access blob service client
            blob_service_client = get_blob_service_client()
                
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_path)
            
            document_bytes = blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading blob: {str(e)}")
            db = get_db_session()
            crud.update_file_status(db, file_id, "error", f"Error downloading blob: {str(e)}")
            db.close()
            return
        
        # Process the document with Azure Document Intelligence directly
        document_client = get_or_create_document_intelligence_client()
        
        # Process document
        poller = document_client.begin_analyze_document("prebuilt-layout", body=document_bytes)
        result = poller.result()
        
        # Extract structured content from result
        structured_content = extract_document_content(result)
        
        # Chunk the document
        chunking_service = ChunkingService()
        document_id = f"file_{file_id}"
        document_title = file.name
        chunks = chunking_service.chunk_document(structured_content, document_id, document_title)
        
        # Use global OpenAI client
        openai = get_openai_client()
        
        # Process one chunk at a time (required for Azure OpenAI)
        chunks_with_vectors = []
        processed_count = 0
        
        for chunk_index, chunk in enumerate(chunks):
            try:
                # Add delay between requests to avoid rate limiting
                if processed_count > 0:
                    time.sleep(2)  # 2 second delay between chunks
                
                logger.info(f"Processing chunk {chunk_index+1}/{len(chunks)} with ID {chunk.get('id', 'unknown')}")
                
                # Truncate text if it's too long
                text = chunk["text"]
                max_text_length = 8000
                if len(text) > max_text_length:
                    logger.warning(f"Text too long ({len(text)} chars), truncating to {max_text_length}")
                    text = text[:max_text_length]
                
                # Generate embedding
                response = openai.embeddings.create(
                    input=text,
                    model=deployment
                )
                
                # Add embedding to the chunk
                chunk["vector"] = response.data[0].embedding
                chunks_with_vectors.append(chunk)
                processed_count += 1
                
                logger.info(f"Successfully processed chunk {processed_count}/{len(chunks)}")
                
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk_index+1}/{len(chunks)}: {str(e)}")
        
        logger.info(f"Successfully generated embeddings for {len(chunks_with_vectors)} of {len(chunks)} chunks")
        
        # Get search client for the index
        search_client = get_search_client()
        
        # Prepare search documents - ONLY include chunks that got embeddings
        search_documents = []
        
        for chunk in chunks_with_vectors:
            # Include the parent document ID in the chunk ID to ensure uniqueness
            chunk_id = chunk["id"]
            
            # Create the search document
            search_document = {
                "chunk_id": chunk_id,  # Primary key field
                "text_parent_id": chunk["parent_id"],
                "chunk": chunk["text"],
                "title": chunk["document_title"],
                "header_1": chunk.get("document_title", ""),  # Use document title as header_1
                "header_2": f"Page {chunk['page']}",     # Use page number as header_2
                "header_3": chunk["type"].capitalize(),   # Use type as header_3
                "content_vector": chunk["vector"],
                "user_id": user_id  # Include user_id for multi-tenancy
            }
            search_documents.append(search_document)
        
        # Split into batches if there are many documents
        batch_size = 1000  # Azure Search can handle up to 1000 documents in a single request
        
        indexed_count = 0
        failed_count = 0
        
        for i in range(0, len(search_documents), batch_size):
            batch = search_documents[i:i + batch_size]
            logger.info(f"Uploading batch of {len(batch)} documents to search index")
            
            # Upload documents to search index
            upload_result = search_client.upload_documents(documents=batch)
            
            # Log the results
            success_count = len([r for r in upload_result if r.succeeded])
            batch_failed_count = len([r for r in upload_result if not r.succeeded])
            
            indexed_count += success_count
            failed_count += batch_failed_count
            
            logger.info(f"Batch upload results: {success_count} succeeded, {batch_failed_count} failed")
            
            # If any failed, log detailed errors
            if batch_failed_count > 0:
                for i, result in enumerate(upload_result):
                    if not result.succeeded:
                        logger.error(f"Error indexing document {i}: {result.status_code} - {result.message}")
        
        # Create result summary
        index_result = {
            "total_count": len(search_documents),
            "indexed_count": indexed_count,
            "failed_count": failed_count
        }
        
        # Update file status
        db = get_db_session()
        crud.update_file_status(db, file_id, "complete")
        
        # Update usage statistics
        pages_processed = len(set(chunk["page"] for chunk in chunks))
        crud.update_pages_processed(db, user_id, pages_processed)
        
        db.close()
        
        logger.info(f"Successfully processed document: file_id={file_id}, chunks={len(chunks)}, indexed={indexed_count}")
    except Exception as e:
        logger.error(f"Error processing document from queue: {str(e)}")
        try:
            db = get_db_session()
            crud.update_file_status(db, file_id, "error", str(e))
            db.close()
        except Exception as db_error:
            logger.error(f"Error updating file status: {str(db_error)}")
            if 'db' in locals():
                db.close()

# Update OCR Processing Queue Function
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
        blob_path = message_data.get('blob_path')
        
        if not file_id or not user_id or not blob_path:
            logger.error(f"Invalid queue message: missing required fields: {message_text}")
            return
        
        # Process the document using our new implementation
        process_document_from_queue(file_id, user_id, blob_path)
    except Exception as e:
        logger.error(f"Error processing OCR queue message: {str(e)}")

# Document Indexing Functions
@app.route(route="api/index", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
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
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
        
        # Connect to Azure Search Service
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure Search credentials from environment
        endpoint = os.environ.get('AZURE_AISEARCH_ENDPOINT')
        search_api_key = os.environ.get('AZURE_AISEARCH_KEY')
        search_index_name = os.environ.get('AZURE_AISEARCH_INDEX')
        
        if not endpoint or not search_api_key or not search_index_name:
            logger.error("Azure AI Search not properly configured")
            return create_error_response(500, "Search service not properly configured")
        
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
            
            return create_success_response({"success": True, "message": "Document indexed successfully"})
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            return create_error_response(500, f"Error during document indexing: {str(e)}")
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        return create_error_response(500, f"Failed to index document: {str(e)}")

# Document Processing Status Function
@app.route(route="api/processing-status/{file_id}", auth_level=func.AuthLevel.ANONYMOUS)
def processing_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get the processing status of a file."""
    try:
        user_id, error_response = validate_user_request(req)
        if error_response:
            return error_response
            
        file_id_str = req.route_params.get('file_id')
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
            
            return create_success_response({"processing": processing_data})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error retrieving processing status: {str(e)}")
        return create_error_response(500, f"Failed to retrieve processing status: {str(e)}")

# Helper functions for Azure Document Intelligence - this fixes the recursive call issue
def get_or_create_document_intelligence_client():
    """Create Azure Document Intelligence client."""
    try:
        # Get API key and endpoint from environment variables
        endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        api_key = os.environ.get("DOCUMENT_INTELLIGENCE_API_KEY") or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
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

def extract_document_content(result):
    """Extract content from document result with structure information"""
    structured_content = {
        "paragraphs": [],
        "tables": [],
        "figures": [],
        "handwriting": []
    }
    
    # Extract paragraphs
    for paragraph in result.paragraphs:
        structured_content["paragraphs"].append({
            "text": paragraph.content,
            "page": paragraph.bounding_regions[0].page_number if paragraph.bounding_regions else 1,
            "confidence": paragraph.confidence if hasattr(paragraph, 'confidence') else 1.0
        })
        
    # Extract tables
    for table in result.tables:
        table_content = []
        for row_idx in range(table.row_count):
            row_content = []
            for col_idx in range(table.column_count):
                cell_content = ""
                for cell in table.cells:
                    if cell.row_index == row_idx and cell.column_index == col_idx:
                        cell_content = cell.content
                        break
                row_content.append(cell_content)
            table_content.append(row_content)
        
        structured_content["tables"].append({
            "content": table_content,
            "page": table.bounding_regions[0].page_number if table.bounding_regions else 1,
            "row_count": table.row_count,
            "column_count": table.column_count
        })
    
    # Extract figures/images with captions
    for page in result.pages:
        for figure_idx, figure in enumerate(getattr(page, 'figures', [])):
            caption = f"Figure {figure_idx+1}"
            # If OCR was performed on the figure, include that text
            figure_text = ""
            if hasattr(figure, 'content'):
                figure_text = figure.content
            
            structured_content["figures"].append({
                "text": figure_text,
                "caption": caption,
                "page": page.page_number
            })
    
    # Extract handwriting - updated to handle API changes
    try:
        # Handle case for API version with styles
        if hasattr(result, 'styles'):
            for style in result.styles:
                if style.is_handwritten and hasattr(style, 'spans'):
                    for span in style.spans:
                        if hasattr(span, 'offset') and hasattr(span, 'length'):
                            # Try to extract handwritten text using a safer approach
                            try:
                                # Find the text from content using offset and length if available
                                handwritten_text = ""
                                current_page = 1
                                
                                for page in result.pages:
                                    current_page = page.page_number
                                    if hasattr(page, 'lines'):
                                        for line in page.lines:
                                            # Check if line is within the span range - API versions differ in how this is represented
                                            # Some versions use span.offset in line, others check line attributes directly
                                            is_in_span = False
                                            
                                            # Method 1: Check using offset - older API
                                            if hasattr(line, 'span') and hasattr(line.span, 'offset'):
                                                is_in_span = (span.offset <= line.span.offset < (span.offset + span.length))
                                            # Method 2: Try to infer from content and position - newer API
                                            elif hasattr(line, 'content'):
                                                # Use line's content as handwritten text
                                                is_in_span = True
                                            
                                            if is_in_span:
                                                handwritten_text += line.content + " "
                                
                                if handwritten_text:
                                    structured_content["handwriting"].append({
                                        "text": handwritten_text.strip(),
                                        "page": current_page
                                    })
                            except Exception as e:
                                logger.warning(f"Error extracting handwritten text from span: {str(e)}")
        
        # Alternative method: If the API doesn't provide styles, look for handwritten content in pages directly
        if len(structured_content["handwriting"]) == 0:
            for page in result.pages:
                if hasattr(page, 'lines'):
                    # Since we can't reliably determine handwriting, include all content
                    # In a real scenario, you might want to use a model or heuristics to identify handwriting
                    page_text = " ".join([line.content for line in page.lines if hasattr(line, 'content')])
                    if page_text.strip():
                        structured_content["handwriting"].append({
                            "text": page_text,
                            "page": page.page_number
                        })
                        
    except Exception as e:
        logger.warning(f"Error extracting handwriting: {str(e)}")
        # Continue processing other content types rather than failing completely
    
    return structured_content

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

def query_documents(query, user_id, include_vectors=False, top_k=5, search_filter=None):
    """
    Search for documents using the vector search index.
    
    Args:
        query: The search query
        user_id: The user ID to filter results by
        include_vectors: Whether to include vectors in the response
        top_k: Number of results to return
        search_filter: Additional filter to apply to the search
        
    Returns:
        List[Dict]: A list of search results
    """
    try:
        # Get the search client
        search_client = get_search_client()
        
        # Get the OpenAI client for generating embeddings
        openai = get_openai_client()
        
        # Get the deployment name for the embedding model
        deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        if not deployment:
            raise ValueError("Missing required environment variable: AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        
        # Generate embedding for the query
        response = openai.embeddings.create(
            input=query,
            model=deployment
        )
        query_vector = response.data[0].embedding
        
        # Build the filter
        filter_str = f"user_id eq '{user_id}'"
        if search_filter:
            filter_str = f"{filter_str} and {search_filter}"
            
        # Define the vector search parameters
        vector_query = VectorizedQuery(
            vector=query_vector,
            fields=["content_vector"],
            k=top_k
        )
        
        # Execute the search
        results = search_client.search(
            search_text=query,
            filter=filter_str,
            top=top_k,
            vector_queries=[vector_query],
            select=["chunk_id", "text_parent_id", "chunk", "title", "header_1", "header_2", "header_3"],
            include_total_count=True
        )
        
        # Process the results
        processed_results = []
        for result in results:
            item = {
                "id": result["chunk_id"],
                "parent_id": result["text_parent_id"],
                "title": result["title"],
                "header_1": result.get("header_1", ""),
                "header_2": result.get("header_2", ""),
                "header_3": result.get("header_3", ""),
                "content": result["chunk"],
                "score": result["@search.score"]
            }
            
            # Only include vectors if requested
            if include_vectors and hasattr(result, "@search.vector_score"):
                item["vector_score"] = result["@search.vector_score"]
                
            processed_results.append(item)
        
        # Add metadata about the search
        response = {
            "results": processed_results,
            "count": len(processed_results),
            "total": results.get_count()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        raise
