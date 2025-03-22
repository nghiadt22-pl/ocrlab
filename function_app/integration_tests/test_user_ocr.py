"""
User-specific OCR test with real documents.
Tests OCR processing on a specific user's documents from test_pdfs directory.
"""
import os
import sys
import json
import logging
import uuid
from datetime import datetime
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocrlab-user-test")

# Verify that we're running the correct script
logger.info("Running test_user_ocr.py script...")

# Check for environment variables
required_vars = [
    'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT',
    'AZURE_DOCUMENT_INTELLIGENCE_KEY',
    'AZURE_STORAGE_CONNECTION_STRING',
    'DB_HOST', 
    'DB_USER', 
    'DB_PASSWORD',
    'DB_PORT',
    'DB_DATABASE'
]

# Check if environment variables are already set, otherwise try to load from .env file
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        logger.info("Attempting to load variables from .env file")
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv package not installed. Cannot load .env file automatically.")

# Map environment variables from .env to the ones expected by function_app.py
os.environ['DOCUMENT_INTELLIGENCE_ENDPOINT'] = os.environ.get('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', '')
os.environ['DOCUMENT_INTELLIGENCE_API_KEY'] = os.environ.get('AZURE_DOCUMENT_INTELLIGENCE_KEY', '')
os.environ['AzureWebJobsStorage'] = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', '')

# Print all env variables to debug (hiding sensitive values)
logger.info("Environment variables after setting:")
for key, value in os.environ.items():
    if any(x in key.lower() for x in ['key', 'password', 'secret', 'connection']):
        logger.info(f"{key}: ***")
    else:
        logger.info(f"{key}: {value}")

# Add parent directory to path to import function_app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required functions and modules
from function_app import process_document, extract_document_content, chunk_text
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
from datetime import timedelta
from database.connection import get_db_session
from database import crud
from database.models import User, Folder, File
from sqlalchemy import create_engine, text

def test_user_ocr_processing():
    """Test OCR processing with real files for a specific user."""
    
    # User information
    USER_ID = "user_2tpkxxIIKb0ghgy1HLYZkEsUqFA"
    USER_EMAIL = "nghia@pencillabs.io"
    
    logger.info(f"Testing OCR processing for user {USER_EMAIL} (ID: {USER_ID})")
    
    # Check for required environment variables
    required_vars = [
        'DOCUMENT_INTELLIGENCE_ENDPOINT',
        'DOCUMENT_INTELLIGENCE_API_KEY',
        'AzureWebJobsStorage',
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
        'DB_PORT',
        'DB_DATABASE'
    ]
    
    # Check if all required variables are set
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables before running the test")
        return False
    
    # Check if we're in mock mode
    if os.environ.get('AzureWebJobsStorage') == "mock":
        logger.warning("AzureWebJobsStorage is set to 'mock'. This test will not use real Azure services.")
        logger.warning("Set AzureWebJobsStorage to a real connection string for proper testing.")
        return False
    
    # Calculate the database connection string for debugging
    encoded_password = urllib.parse.quote_plus(os.environ.get('DB_PASSWORD'))
    db_url = f"postgresql://{os.environ.get('DB_USER')}:{encoded_password}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_DATABASE')}"
    logger.info(f"Database connection URL (password hidden): postgresql://{os.environ.get('DB_USER')}:***@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_DATABASE')}")
    
    # Test database connection before proceeding
    try:
        engine = create_engine(db_url)
        connection = engine.connect()
        result = connection.execute(text("SELECT 1"))
        connection.close()
        logger.info("Database connection test successful!")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return False
    
    # Get a database session
    db = get_db_session()
    try:
        # Get or create user
        user = crud.get_user(db, USER_ID)
        if not user:
            logger.info(f"Creating test user: {USER_EMAIL}")
            user = crud.create_user(db, USER_ID, USER_EMAIL)
        
        # Create a test folder for the user if it doesn't exist
        folder_name = "OCR Test Folder"
        
        # Check if folder exists by getting all folders for the user
        folders = crud.get_folders_by_user(db, USER_ID, None)
        folder = None
        for f in folders:
            if f.name == folder_name:
                folder = f
                break
                
        if not folder:
            logger.info(f"Creating test folder: {folder_name}")
            folder = crud.create_folder(db, folder_name, USER_ID)
        
        # Get list of PDFs in test_pdfs directory
        test_pdfs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                    "test_pdfs")
        pdf_files = [f for f in os.listdir(test_pdfs_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            logger.error("No PDF files found in test_pdfs directory")
            return False
        
        logger.info(f"Found {len(pdf_files)} PDF files in test_pdfs directory")
        # Use the first PDF file for testing
        test_pdf_filename = pdf_files[0]
        test_pdf_path = os.path.join(test_pdfs_dir, test_pdf_filename)
        
        logger.info(f"Using test PDF: {test_pdf_path}")
        
        # Get blob service client
        connection_string = os.environ.get('AzureWebJobsStorage')
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Create a test container if it doesn't exist
        container_name = "ocrlabusertest"
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                logger.info(f"Creating test container: {container_name}")
                container_client.create_container()
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            return False
        
        # Generate unique blob name
        test_id = str(uuid.uuid4())
        blob_name = f"{USER_ID}/{folder.id}/{test_id}_{test_pdf_filename}"
        blob_path = f"{container_name}/{blob_name}"
        
        # Upload test PDF
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        logger.info(f"Uploading test PDF to {container_name}/{blob_name}")
        with open(test_pdf_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        # Get file size
        file_size = os.path.getsize(test_pdf_path)
        
        # Create file record in database
        file = crud.create_file(
            db,
            name=test_pdf_filename,
            folder_id=folder.id,
            user_id=USER_ID,
            blob_path=blob_path,
            size_bytes=file_size,
            mime_type="application/pdf"
        )
        
        # Set the file status to queued
        file = crud.update_file_status(db, file.id, "queued")
        
        logger.info(f"Created file record with ID {file.id}")
        
        # Generate SAS token for the blob
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
        logger.info("Processing document with Azure Document Intelligence...")
        analyze_result = process_document(blob_url)
        
        # Extract content from analyze result
        logger.info("Extracting content from analyze result...")
        ocr_result = extract_document_content(analyze_result)
        
        # Chunk text for vector database
        logger.info("Chunking text...")
        text_chunks = chunk_text(ocr_result['text'])
        
        # Update file with OCR results
        file = crud.update_file_status(
            db, 
            file.id, 
            "complete", 
            metadata={
                'ocr_result': ocr_result,
                'page_count': ocr_result['page_count'],
                'chunks': text_chunks
            }
        )
        
        # Update usage stats
        crud.update_pages_processed(db, USER_ID, ocr_result['page_count'], datetime.utcnow().date())
        
        # Log results
        logger.info(f"Processing complete for file ID {file.id}!")
        logger.info(f"Text length: {len(ocr_result['text'])} characters")
        logger.info(f"Pages: {ocr_result['page_count']}")
        logger.info(f"Tables: {len(ocr_result['tables'])}")
        logger.info(f"Chunks: {len(text_chunks)}")
        
        # Log sample of extracted text
        sample_text = ocr_result['text'][:500] + "..." if len(ocr_result['text']) > 500 else ocr_result['text']
        logger.info(f"Sample text: {sample_text}")
        
        # Check if file was processed successfully
        updated_file = crud.get_file(db, file.id)
        if updated_file and updated_file.status == 'complete':
            logger.info("File successfully processed and updated in database!")
        else:
            logger.error(f"File processing failed: status = {updated_file.status if updated_file else 'unknown'}")
            return False
        
        # Clean up - delete test blob (optional, commented out to keep test data)
        # logger.info(f"Cleaning up - deleting test blob {container_name}/{blob_name}")
        # blob_client.delete_blob()
        
        return True
    except Exception as e:
        logger.error(f"Error during user OCR test: {str(e)}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_user_ocr_processing()
    if success:
        logger.info("✅ User OCR test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ User OCR test failed!")
        sys.exit(1) 