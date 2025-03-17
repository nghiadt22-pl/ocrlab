"""
Vector Database Module

This module provides functionality for integrating with Azure AI Search
to store and retrieve document embeddings.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class VectorDatabase:
    """
    Class for integrating with Azure AI Search vector database.
    
    This class provides methods for storing and retrieving document embeddings
    in Azure AI Search.
    """
    
    def __init__(
        self,
        search_service_name: Optional[str] = None,
        search_api_key: Optional[str] = None,
        index_name: str = "documents-index"
    ):
        """
        Initialize the VectorDatabase.
        
        Args:
            search_service_name: The Azure AI Search service name.
            search_api_key: The Azure AI Search API key.
            index_name: The name of the search index.
        """
        self.search_service_name = search_service_name or os.environ.get("AZURE_SEARCH_SERVICE")
        self.search_api_key = search_api_key or os.environ.get("AZURE_SEARCH_API_KEY")
        self.index_name = index_name
        
        if not self.search_service_name or not self.search_api_key:
            logger.warning("Azure AI Search credentials not provided. Vector database operations will not work.")
        
        logger.info(f"VectorDatabase initialized with index {index_name}")
    
    def store_document_chunks(self, file_id: str, user_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks in the vector database.
        
        Args:
            file_id: The ID of the file.
            user_id: The ID of the user.
            chunks: Document chunks with embeddings.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.search_service_name or not self.search_api_key:
            logger.warning("Azure AI Search credentials not available. Unable to store document chunks.")
            return False
        
        logger.info(f"Storing {len(chunks)} document chunks for file {file_id}")
        
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents.models import VectorizedQuery
            
            # Create the search client
            search_client = SearchClient(
                endpoint=f"https://{self.search_service_name}.search.windows.net/",
                index_name=self.index_name,
                credential=AzureKeyCredential(self.search_api_key)
            )
            
            # Prepare documents for indexing
            documents = []
            for chunk in chunks:
                document = {
                    "id": f"{file_id}_{chunk['id']}",
                    "file_id": file_id,
                    "user_id": user_id,
                    "chunk_id": chunk["id"],
                    "content": chunk["text"],
                    "page_number": chunk.get("page_number", 1),
                    "vector": chunk.get("embedding", [])
                }
                
                # Add metadata if available
                if "metadata" in chunk:
                    for key, value in chunk["metadata"].items():
                        if key not in document:
                            document[key] = value
                
                # Add key phrases if available
                if "key_phrases" in chunk:
                    document["key_phrases"] = chunk["key_phrases"]
                
                documents.append(document)
            
            # Upload documents in batches (max 1000 documents per batch)
            batch_size = 1000
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                try:
                    results = search_client.upload_documents(documents=batch)
                    success_count = sum(1 for r in results if r.succeeded)
                    logger.info(f"Indexed {success_count}/{len(batch)} documents in batch {i // batch_size + 1}")
                except Exception as e:
                    logger.error(f"Error indexing batch {i // batch_size + 1}: {str(e)}")
            
            logger.info(f"Successfully stored document chunks for file {file_id}")
            return True
        except ImportError as e:
            logger.error(f"Required libraries not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error storing document chunks: {str(e)}")
            return False
    
    def search_documents(self, query: str, user_id: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents in the vector database.
        
        Args:
            query: The search query.
            user_id: The ID of the user.
            limit: The maximum number of results to return.
            filters: Additional filters to apply to the search.
        
        Returns:
            List[Dict[str, Any]]: The search results.
        """
        if not self.search_service_name or not self.search_api_key:
            logger.warning("Azure AI Search credentials not available. Unable to search documents.")
            return []
        
        logger.info(f"Searching for documents with query: {query}")
        
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents.models import VectorizedQuery
            
            # Create the search client
            search_client = SearchClient(
                endpoint=f"https://{self.search_service_name}.search.windows.net/",
                index_name=self.index_name,
                credential=AzureKeyCredential(self.search_api_key)
            )
            
            # Build the filter string
            filter_str = f"user_id eq '{user_id}'"
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_str += f" and {key} eq '{value}'"
                    elif isinstance(value, (int, float)):
                        filter_str += f" and {key} eq {value}"
                    elif isinstance(value, list):
                        if value and isinstance(value[0], str):
                            filter_str += f" and {key}/any(t: t eq '{value[0]}'"
                            for v in value[1:]:
                                filter_str += f" or t eq '{v}'"
                            filter_str += ")"
            
            # Perform the search
            results = search_client.search(
                search_text=query,
                filter=filter_str,
                top=limit,
                include_total_count=True
            )
            
            # Process the results
            search_results = []
            for result in results:
                item = {
                    "id": result["id"],
                    "file_id": result["file_id"],
                    "content": result["content"],
                    "page_number": result.get("page_number", 1),
                    "score": result["@search.score"]
                }
                
                # Add other fields from the result
                for key, value in result.items():
                    if key not in ["id", "file_id", "content", "page_number", "@search.score"] and not key.startswith("@"):
                        item[key] = value
                
                search_results.append(item)
            
            logger.info(f"Found {len(search_results)} search results for query: {query}")
            return search_results
        except ImportError as e:
            logger.error(f"Required libraries not available: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def delete_file_chunks(self, file_id: str, user_id: str) -> bool:
        """
        Delete all chunks for a specific file.
        
        Args:
            file_id: The ID of the file.
            user_id: The ID of the user.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.search_service_name or not self.search_api_key:
            logger.warning("Azure AI Search credentials not available. Unable to delete file chunks.")
            return False
        
        logger.info(f"Deleting chunks for file {file_id}")
        
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            
            # Create the search client
            search_client = SearchClient(
                endpoint=f"https://{self.search_service_name}.search.windows.net/",
                index_name=self.index_name,
                credential=AzureKeyCredential(self.search_api_key)
            )
            
            # First, find all documents for this file
            results = search_client.search(
                search_text="*",
                filter=f"file_id eq '{file_id}' and user_id eq '{user_id}'",
                include_total_count=True,
                select=["id"]
            )
            
            # Collect document IDs
            doc_ids = [result["id"] for result in results]
            
            if not doc_ids:
                logger.info(f"No chunks found for file {file_id}")
                return True
            
            logger.info(f"Found {len(doc_ids)} chunks to delete for file {file_id}")
            
            # Delete documents in batches
            batch_size = 1000
            for i in range(0, len(doc_ids), batch_size):
                batch = doc_ids[i:i+batch_size]
                try:
                    results = search_client.delete_documents(
                        documents=[{"id": doc_id} for doc_id in batch]
                    )
                    success_count = sum(1 for r in results if r.succeeded)
                    logger.info(f"Deleted {success_count}/{len(batch)} documents in batch {i // batch_size + 1}")
                except Exception as e:
                    logger.error(f"Error deleting batch {i // batch_size + 1}: {str(e)}")
            
            logger.info(f"Successfully deleted chunks for file {file_id}")
            return True
        except ImportError as e:
            logger.error(f"Required libraries not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file chunks: {str(e)}")
            return False


class MockVectorDatabase(VectorDatabase):
    """
    Mock implementation of VectorDatabase for testing purposes.
    """
    
    def __init__(self, index_name: str = "documents-index"):
        """
        Initialize the MockVectorDatabase.
        
        Args:
            index_name: The name of the mock search index.
        """
        super().__init__("mock", "mock", index_name)
        self.documents = []
        logger.info("MockVectorDatabase initialized")
    
    def store_document_chunks(self, file_id: str, user_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks in the mock vector database.
        
        Args:
            file_id: The ID of the file.
            user_id: The ID of the user.
            chunks: Document chunks with embeddings.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Storing {len(chunks)} document chunks for file {file_id} (mock)")
        
        for chunk in chunks:
            document = {
                "id": f"{file_id}_{chunk['id']}",
                "file_id": file_id,
                "user_id": user_id,
                "chunk_id": chunk["id"],
                "content": chunk["text"],
                "page_number": chunk.get("page_number", 1),
                "vector": chunk.get("embedding", [])
            }
            
            # Add metadata if available
            if "metadata" in chunk:
                for key, value in chunk["metadata"].items():
                    if key not in document:
                        document[key] = value
            
            # Add key phrases if available
            if "key_phrases" in chunk:
                document["key_phrases"] = chunk["key_phrases"]
            
            self.documents.append(document)
        
        logger.info(f"Successfully stored document chunks for file {file_id} (mock)")
        return True
    
    def search_documents(self, query: str, user_id: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents in the mock vector database.
        
        Args:
            query: The search query.
            user_id: The ID of the user.
            limit: The maximum number of results to return.
            filters: Additional filters to apply to the search.
        
        Returns:
            List[Dict[str, Any]]: The search results.
        """
        logger.info(f"Searching for documents with query: {query} (mock)")
        
        # Filter documents by user_id
        results = [doc for doc in self.documents if doc["user_id"] == user_id]
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, (str, int, float)):
                    results = [doc for doc in results if doc.get(key) == value]
                elif isinstance(value, list):
                    results = [doc for doc in results if doc.get(key) in value]
        
        # Perform basic text matching
        if query != "*":
            query_terms = query.lower().split()
            scored_results = []
            for doc in results:
                content = doc["content"].lower()
                score = sum(1 for term in query_terms if term in content)
                if score > 0:
                    doc_copy = doc.copy()
                    doc_copy["@search.score"] = score
                    scored_results.append(doc_copy)
            
            # Sort by score (descending)
            results = sorted(scored_results, key=lambda x: x["@search.score"], reverse=True)
        else:
            # Add mock scores for all documents
            for doc in results:
                doc["@search.score"] = 1.0
        
        # Limit the number of results
        results = results[:limit]
        
        # Format the results
        search_results = []
        for result in results:
            item = {
                "id": result["id"],
                "file_id": result["file_id"],
                "content": result["content"],
                "page_number": result.get("page_number", 1),
                "score": result.get("@search.score", 1.0)
            }
            
            # Add other fields from the result
            for key, value in result.items():
                if key not in ["id", "file_id", "content", "page_number", "@search.score"] and not key.startswith("@"):
                    item[key] = value
            
            search_results.append(item)
        
        logger.info(f"Found {len(search_results)} search results for query: {query} (mock)")
        return search_results
    
    def delete_file_chunks(self, file_id: str, user_id: str) -> bool:
        """
        Delete all chunks for a specific file from the mock vector database.
        
        Args:
            file_id: The ID of the file.
            user_id: The ID of the user.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Deleting chunks for file {file_id} (mock)")
        
        # Count documents to delete
        count_before = len(self.documents)
        
        # Filter out documents for this file
        self.documents = [doc for doc in self.documents if not (doc["file_id"] == file_id and doc["user_id"] == user_id)]
        
        # Calculate how many were deleted
        count_deleted = count_before - len(self.documents)
        logger.info(f"Deleted {count_deleted} chunks for file {file_id} (mock)")
        
        return True


def create_vector_database(search_service_name: Optional[str] = None, search_api_key: Optional[str] = None, index_name: str = "documents-index") -> Union[VectorDatabase, MockVectorDatabase]:
    """
    Create a VectorDatabase or MockVectorDatabase instance.
    
    Args:
        search_service_name: The Azure AI Search service name.
        search_api_key: The Azure AI Search API key.
        index_name: The name of the search index.
    
    Returns:
        Union[VectorDatabase, MockVectorDatabase]: A VectorDatabase or MockVectorDatabase instance.
    """
    # Check if we're in mock mode
    connection_string = os.environ.get("AzureWebJobsStorage")
    if connection_string == "mock":
        return MockVectorDatabase(index_name)
    
    # Use provided credentials or environment variables
    service_name = search_service_name or os.environ.get("AZURE_SEARCH_SERVICE")
    api_key = search_api_key or os.environ.get("AZURE_SEARCH_API_KEY")
    
    # If either credential is missing, fall back to mock database
    if not service_name or not api_key:
        logger.warning("Azure AI Search credentials not available. Using MockVectorDatabase instead.")
        return MockVectorDatabase(index_name)
    
    return VectorDatabase(service_name, api_key, index_name)
