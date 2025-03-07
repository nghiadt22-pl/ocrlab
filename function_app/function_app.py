import azure.functions as func
import logging
import json
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    CorsOptions,
    SearchField
)
import os
from datetime import datetime

app = func.FunctionApp()

def add_cors_headers(resp: func.HttpResponse, req: func.HttpRequest) -> func.HttpResponse:
    origin = req.headers.get('origin', '')
    
    # List of allowed origins
    allowed_origins = [
        '*'
    ]
    
    # Check if the origin is allowed
    if origin in allowed_origins:
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Content-Disposition, Authorization'
        resp.headers['Access-Control-Max-Age'] = '86400'
    
    return resp

def ensure_search_index_exists():
    """Checks if the search index exists."""
    try:
        # Get search configuration
        search_endpoint = os.environ["AZURE_AISEARCH_ENDPOINT"]
        search_key = os.environ["AZURE_AISEARCH_KEY"]
        index_name = os.environ["AZURE_AISEARCH_INDEX"]

        # Create an index client
        credential = AzureKeyCredential(search_key)
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

        # Check if index exists
        index = index_client.get_index(name=index_name)
        logging.info(f"Search index {index_name} exists")
        return True
    except Exception as e:
        logging.error(f"Error checking search index: {str(e)}")
        return False

@app.function_name(name="upload")
@app.route(route="upload", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get file from request
        file_data = req.get_body()
        if not file_data:
            resp = func.HttpResponse(
                json.dumps({"error": "No file content"}),
                status_code=400,
                mimetype="application/json"
            )
            return add_cors_headers(resp, req)

        # Get content type and filename from headers
        content_type = req.headers.get('content-type', 'application/octet-stream')
        content_disposition = req.headers.get('content-disposition', '')
        filename = 'unknown'
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')

        # Azure Storage configuration
        connection_string = os.environ["DEPLOYMENT_STORAGE_CONNECTION_STRING"]
        container_name = os.environ["AZURE_BLOB_CONTAINER_NAME"]

        # Create blob client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        # Create unique blob name
        blob_name = f"{datetime.now().timestamp()}-{filename}"
        blob_client = container_client.get_blob_client(blob_name)
        
        # Create content settings
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition=content_disposition
        )
        
        # Upload file
        blob_client.upload_blob(file_data, blob_type="BlockBlob", content_settings=content_settings)

        # Return the blob URL
        resp = func.HttpResponse(
            json.dumps({"url": blob_client.url}),
            status_code=200,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

    except Exception as e:
        logging.error(f'Error uploading file: {str(e)}')
        resp = func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

@app.function_name(name="index_document")
@app.route(route="index", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def index_document(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing document indexing request.')

    try:
        # Ensure search index exists
        if not ensure_search_index_exists():
            resp = func.HttpResponse(
                json.dumps({"error": "Failed to create or update search index"}),
                status_code=500,
                mimetype="application/json"
            )
            return add_cors_headers(resp, req)

        # Get request body
        request_body = req.get_json()
        if not request_body:
            resp = func.HttpResponse(
                json.dumps({"error": "No request body"}),
                status_code=400,
                mimetype="application/json"
            )
            return add_cors_headers(resp, req)

        # Validate required fields
        required_fields = ["id", "content"]
        missing_fields = [field for field in required_fields if field not in request_body]
        if missing_fields:
            resp = func.HttpResponse(
                json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"}),
                status_code=400,
                mimetype="application/json"
            )
            return add_cors_headers(resp, req)

        # Azure Search configuration
        search_endpoint = os.environ["AZURE_AISEARCH_ENDPOINT"]
        search_key = os.environ["AZURE_AISEARCH_KEY"]
        index_name = os.environ["AZURE_AISEARCH_INDEX"]

        # Create search client
        credential = AzureKeyCredential(search_key)
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )

        # Prepare the document for indexing
        search_document = {
            "id": request_body["id"],
            "content": request_body["content"],
            "metadata": request_body.get("metadata", ""),
        }

        # Add content_vector if provided
        if "content_vector" in request_body:
            if not isinstance(request_body["content_vector"], list) or len(request_body["content_vector"]) != 1536:
                resp = func.HttpResponse(
                    json.dumps({"error": "content_vector must be a list of 1536 float values"}),
                    status_code=400,
                    mimetype="application/json"
                )
                return add_cors_headers(resp, req)
            search_document["content_vector"] = request_body["content_vector"]

        # Index the document
        result = search_client.upload_documents(documents=[search_document])

        resp = func.HttpResponse(
            json.dumps({"result": "Document indexed successfully"}),
            status_code=200,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

    except Exception as e:
        logging.error(f'Error indexing document: {str(e)}')
        resp = func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

@app.function_name(name="search")
@app.route(route="search", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def search_documents(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing search request.')

    try:
        # Get request body
        request_body = req.get_json()
        if not request_body or ('query' not in request_body and 'vector' not in request_body):
            resp = func.HttpResponse(
                json.dumps({"error": "No search query or vector provided"}),
                status_code=400,
                mimetype="application/json"
            )
            return add_cors_headers(resp, req)

        # Azure Search configuration
        search_endpoint = os.environ["AZURE_AISEARCH_ENDPOINT"]
        search_key = os.environ["AZURE_AISEARCH_KEY"]
        index_name = os.environ["AZURE_AISEARCH_INDEX"]

        # Create search client
        credential = AzureKeyCredential(search_key)
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )

        # Set up search parameters
        select_fields = request_body.get('select', ['id', 'content', 'metadata'])
        
        # Perform vector search if vector is provided
        if 'vector' in request_body:
            results = search_client.search(
                search_text=None,
                select=select_fields,
                vector=request_body['vector'],
                vector_fields='content_vector',
                top=3
            )
        # Otherwise perform text search
        else:
            results = search_client.search(
                search_text=request_body['query'],
                select=select_fields,
                top=3
            )

        # Convert results to list
        documents = [doc for doc in results]

        resp = func.HttpResponse(
            json.dumps({"value": documents}),
            status_code=200,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

    except Exception as e:
        logging.error(f'Error searching documents: {str(e)}')
        resp = func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
        return add_cors_headers(resp, req)

@app.function_name(name="upload_options")
@app.route(route="upload", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_options(req: func.HttpRequest) -> func.HttpResponse:
    resp = func.HttpResponse(status_code=200)
    return add_cors_headers(resp, req)

@app.function_name(name="index_options")
@app.route(route="index", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def index_options(req: func.HttpRequest) -> func.HttpResponse:
    resp = func.HttpResponse(status_code=200)
    return add_cors_headers(resp, req)

@app.function_name(name="search_options")
@app.route(route="search", methods=["OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def search_options(req: func.HttpRequest) -> func.HttpResponse:
    resp = func.HttpResponse(status_code=200)
    return add_cors_headers(resp, req) 