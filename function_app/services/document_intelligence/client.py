"""
Azure Document Intelligence Client Module

This module provides a client for interacting with the Azure Document Intelligence service.
It includes functionality for authentication, client creation, and error handling.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, Union, List

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, ResourceNotFoundError
from azure.ai.documentintelligence import DocumentIntelligenceClient as AzureDocumentIntelligenceClient

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class DocumentIntelligenceClient:
    """
    Client for interacting with Azure Document Intelligence service.
    
    This class provides methods for analyzing documents, managing models,
    and handling errors with retries.
    """
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Document Intelligence client.
        
        Args:
            endpoint: The Azure Document Intelligence endpoint URL.
                      If not provided, it will be read from the AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT environment variable.
            api_key: The Azure Document Intelligence API key.
                     If not provided, it will be read from the AZURE_DOCUMENT_INTELLIGENCE_KEY environment variable.
        
        Raises:
            ValueError: If the endpoint or API key is not provided and not found in environment variables.
        """
        self.endpoint = endpoint or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.api_key = api_key or os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not self.endpoint:
            raise ValueError("Document Intelligence endpoint not provided and AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not found in environment variables")
        
        if not self.api_key:
            raise ValueError("Document Intelligence API key not provided and AZURE_DOCUMENT_INTELLIGENCE_KEY not found in environment variables")
        
        self.credential = AzureKeyCredential(self.api_key)
        logger.info(f"Document Intelligence client initialized with endpoint: {self.endpoint}")
    
    def get_document_intelligence_client(self) -> AzureDocumentIntelligenceClient:
        """
        Get a Document Intelligence client for analyzing documents.
        
        Returns:
            AzureDocumentIntelligenceClient: A client for analyzing documents.
        """
        return AzureDocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
    
    def analyze_document(self, document_bytes: bytes, model_id: str = "prebuilt-layout") -> Dict[str, Any]:
        """
        Analyze a document using the specified model.
        
        Args:
            document_bytes: The document content as bytes.
            model_id: The model ID to use for analysis. Defaults to "prebuilt-layout".
        
        Returns:
            Dict[str, Any]: The analysis results.
        
        Raises:
            Exception: If the document analysis fails after retries.
        """
        client = self.get_document_intelligence_client()
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Analyzing document with model: {model_id} (Attempt {attempt + 1}/{MAX_RETRIES})")
                poller = client.begin_analyze_document(model_id, document_bytes)
                result = poller.result()
                logger.info("Document analysis completed successfully")
                return result.to_dict()
            
            except (ServiceRequestError, ClientAuthenticationError) as e:
                logger.warning(f"Authentication or request error: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to analyze document after {MAX_RETRIES} attempts")
                    raise Exception(f"Document analysis failed: {str(e)}")
            
            except ResourceNotFoundError as e:
                logger.error(f"Resource not found: {str(e)}")
                raise Exception(f"Model '{model_id}' not found: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error during document analysis: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to analyze document after {MAX_RETRIES} attempts")
                    raise Exception(f"Document analysis failed: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available document models.
        
        Returns:
            List[Dict[str, Any]]: A list of available models.
        
        Raises:
            Exception: If retrieving the models fails after retries.
        """
        client = self.get_document_intelligence_client()
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Getting available models (Attempt {attempt + 1}/{MAX_RETRIES})")
                models = list(client.list_operations())
                logger.info(f"Retrieved {len(models)} available models")
                return [model.to_dict() for model in models]
            
            except (ServiceRequestError, ClientAuthenticationError) as e:
                logger.warning(f"Authentication or request error: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to get available models after {MAX_RETRIES} attempts")
                    raise Exception(f"Failed to get available models: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error while getting available models: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to get available models after {MAX_RETRIES} attempts")
                    raise Exception(f"Failed to get available models: {str(e)}")


# Factory function to create a Document Intelligence client
def create_document_intelligence_client(
    endpoint: Optional[str] = None, 
    api_key: Optional[str] = None
) -> DocumentIntelligenceClient:
    """
    Create a Document Intelligence client.
    
    Args:
        endpoint: The Azure Document Intelligence endpoint URL.
                  If not provided, it will be read from the AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT environment variable.
        api_key: The Azure Document Intelligence API key.
                 If not provided, it will be read from the AZURE_DOCUMENT_INTELLIGENCE_KEY environment variable.
    
    Returns:
        DocumentIntelligenceClient: A client for interacting with Azure Document Intelligence.
    """
    return DocumentIntelligenceClient(endpoint=endpoint, api_key=api_key) 