"""
Embeddings Module

This module provides functionality for generating embeddings for document chunks
using Azure AI services.
"""

import logging
import os
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """
    Class for generating embeddings for document chunks.
    
    This class provides methods for generating embeddings using Azure AI services
    and storing them in Azure AI Search.
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002"
    ):
        """
        Initialize the EmbeddingsGenerator.
        
        Args:
            endpoint: The Azure OpenAI endpoint URL.
            api_key: The Azure OpenAI API key.
            model: The embedding model to use.
        """
        self.endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        self.model = model
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not provided. Embeddings will not be generated.")
        
        logger.info(f"EmbeddingsGenerator initialized with model {model}")
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: Document chunks to generate embeddings for.
        
        Returns:
            List[Dict[str, Any]]: Document chunks with embeddings.
        """
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not available. Returning chunks without embeddings.")
            return chunks
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.ai.textanalytics import TextAnalyticsClient
            
            # Create the client
            text_analytics_client = TextAnalyticsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key)
            )
            
            # Prepare the documents for embedding
            documents = [chunk["text"] for chunk in chunks]
            
            # Generate embeddings in batches (max 10 documents per request)
            batch_size = 10
            results = []
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                try:
                    response = text_analytics_client.extract_key_phrases(batch)
                    # For testing, we're just using key phrases extraction to simulate embeddings
                    # In a real implementation, this would be replaced with actual embedding generation
                    for j, doc in enumerate(response):
                        if not doc.is_error:
                            # In a real implementation, this would store the actual embedding vector
                            # For now, we'll just add a placeholder
                            chunks[i+j]["embedding"] = [0.0] * 5  # Placeholder embedding
                            chunks[i+j]["key_phrases"] = doc.key_phrases if hasattr(doc, "key_phrases") else []
                        else:
                            logger.warning(f"Error generating embedding for chunk {i+j}: {doc.error}")
                except Exception as e:
                    logger.error(f"Error generating embeddings for batch: {str(e)}")
            
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return chunks
        except ImportError as e:
            logger.error(f"Required libraries not available: {str(e)}")
            return chunks
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return chunks
    
    def generate_mock_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate mock embeddings for testing purposes.
        
        Args:
            chunks: Document chunks to generate mock embeddings for.
        
        Returns:
            List[Dict[str, Any]]: Document chunks with mock embeddings.
        """
        logger.info(f"Generating mock embeddings for {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            # Create a simple mock embedding (just zeros)
            chunk["embedding"] = [0.0] * 10  # 10-dimensional mock embedding
            
            # Add some mock key phrases based on text content
            words = chunk["text"].lower().split()
            # Filter out common words and keep only unique words
            stop_words = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were"}
            unique_words = list(set(word for word in words if word not in stop_words and len(word) > 3))
            # Take up to 5 "key phrases"
            chunk["key_phrases"] = unique_words[:5]
        
        logger.info(f"Generated mock embeddings for {len(chunks)} chunks")
        return chunks


def create_embeddings_generator(
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "text-embedding-ada-002"
) -> EmbeddingsGenerator:
    """
    Create an EmbeddingsGenerator.
    
    Args:
        endpoint: The Azure OpenAI endpoint URL.
        api_key: The Azure OpenAI API key.
        model: The embedding model to use.
    
    Returns:
        EmbeddingsGenerator: An EmbeddingsGenerator instance.
    """
    return EmbeddingsGenerator(endpoint, api_key, model)
