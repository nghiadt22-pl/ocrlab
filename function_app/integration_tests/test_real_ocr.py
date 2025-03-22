"""
Real-mode integration test for OCR processing functionality.
This script tests the OCR processing with the actual Azure Document Intelligence service.
"""
import os
import sys
import json
import logging
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocrlab-test")

# Add parent directory to path to import function_app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required functions
from function_app import process_document, extract_document_content, chunk_text
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
from datetime import timedelta

def test_real_ocr_processing():
    """Test OCR processing with real Azure Document Intelligence service."""
    
    # Print current environment settings
    logger.info("Testing OCR processing with real Azure Document Intelligence service")
    
    # Check for required environment variables
    required_vars = [
        'DOCUMENT_INTELLIGENCE_ENDPOINT',
        'DOCUMENT_INTELLIGENCE_API_KEY',
        'AzureWebJobsStorage'
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
    
    # Upload a test PDF to blob storage
    test_pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                 "test_pdfs", "sample.pdf")
    
    if not os.path.exists(test_pdf_path):
        logger.error(f"Test PDF not found at: {test_pdf_path}")
        logger.error("Please place a sample.pdf file in the test_pdfs directory")
        return False
    
    logger.info(f"Using test PDF: {test_pdf_path}")
    
    try:
        # Get blob service client
        connection_string = os.environ.get('AzureWebJobsStorage')
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Create a test container if it doesn't exist
        container_name = "ocrlabtest"
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
        blob_name = f"test/{test_id}/sample.pdf"
        
        # Upload test PDF
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        logger.info(f"Uploading test PDF to {container_name}/{blob_name}")
        with open(test_pdf_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
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
        
        # Log results
        logger.info(f"Processing complete!")
        logger.info(f"Text length: {len(ocr_result['text'])} characters")
        logger.info(f"Pages: {ocr_result['page_count']}")
        logger.info(f"Tables: {len(ocr_result['tables'])}")
        logger.info(f"Chunks: {len(text_chunks)}")
        
        # Log sample of extracted text
        sample_text = ocr_result['text'][:500] + "..." if len(ocr_result['text']) > 500 else ocr_result['text']
        logger.info(f"Sample text: {sample_text}")
        
        # Clean up - delete test blob
        logger.info(f"Cleaning up - deleting test blob {container_name}/{blob_name}")
        blob_client.delete_blob()
        
        return True
    except Exception as e:
        logger.error(f"Error during real OCR test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_real_ocr_processing()
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1) 