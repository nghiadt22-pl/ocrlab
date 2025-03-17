"""
Tests for the Vector Database module.

This module contains tests for the VectorDatabase class and related functionality.
"""

import os
import unittest
import json
import sys
from unittest.mock import patch, MagicMock, mock_open
from typing import Dict, Any, List

import pytest

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.vector_search.vector_db import (
    VectorDatabase,
    MockVectorDatabase,
    create_vector_database
)


class TestVectorDatabase(unittest.TestCase):
    """Tests for the VectorDatabase class."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "AZURE_SEARCH_SERVICE": "test-search-service",
            "AZURE_SEARCH_API_KEY": "test-api-key"
        })
        self.env_patcher.start()
        
        # Create a client for testing
        self.vector_db = VectorDatabase()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        vector_db = VectorDatabase()
        self.assertEqual(vector_db.search_service_name, "test-search-service")
        self.assertEqual(vector_db.search_api_key, "test-api-key")
        self.assertEqual(vector_db.index_name, "documents-index")
    
    def test_init_with_params(self):
        """Test initialization with parameters."""
        vector_db = VectorDatabase(
            search_service_name="custom-service",
            search_api_key="custom-key",
            index_name="custom-index"
        )
        self.assertEqual(vector_db.search_service_name, "custom-service")
        self.assertEqual(vector_db.search_api_key, "custom-key")
        self.assertEqual(vector_db.index_name, "custom-index")
    
    @patch("services.vector_search.vector_db.requests.post")
    def test_store_document_chunks(self, mock_post):
        """Test storing document chunks."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Create test data
        file_id = "test-file-id"
        user_id = "test-user-id"
        chunks = [
            {
                "id": "chunk-1",
                "content": "This is the first chunk",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {
                    "page_number": 1,
                    "source": "text"
                }
            },
            {
                "id": "chunk-2",
                "content": "This is the second chunk",
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {
                    "page_number": 2,
                    "source": "table"
                }
            }
        ]
        
        # Call the method to test
        result = self.vector_db.store_document_chunks(file_id, user_id, chunks)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("https://test-search-service.search.windows.net", args[0])
        self.assertIn("api-version", args[0])
        self.assertIn("Content-Type", kwargs["headers"])
        self.assertIn("api-key", kwargs["headers"])
        
        # Verify the request body
        request_body = json.loads(kwargs["data"])
        self.assertEqual(len(request_body["value"]), 2)
        self.assertEqual(request_body["value"][0]["id"], "chunk-1")
        self.assertEqual(request_body["value"][0]["content"], "This is the first chunk")
        self.assertEqual(request_body["value"][0]["file_id"], file_id)
        self.assertEqual(request_body["value"][0]["user_id"], user_id)
    
    @patch("services.vector_search.vector_db.requests.post")
    def test_search_documents(self, mock_post):
        """Test searching documents."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "chunk-1",
                    "content": "This is the first chunk",
                    "file_id": "test-file-id",
                    "user_id": "test-user-id",
                    "metadata": {
                        "page_number": 1,
                        "source": "text"
                    },
                    "@search.score": 0.95
                },
                {
                    "id": "chunk-2",
                    "content": "This is the second chunk",
                    "file_id": "test-file-id",
                    "user_id": "test-user-id",
                    "metadata": {
                        "page_number": 2,
                        "source": "table"
                    },
                    "@search.score": 0.85
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Create test data
        query = "test query"
        user_id = "test-user-id"
        embedding = [0.1, 0.2, 0.3]
        
        # Call the method to test
        results = self.vector_db.search_documents(query, user_id, embedding)
        
        # Verify the result
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "chunk-1")
        self.assertEqual(results[0]["content"], "This is the first chunk")
        self.assertEqual(results[0]["file_id"], "test-file-id")
        self.assertEqual(results[0]["score"], 0.95)
        
        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("https://test-search-service.search.windows.net", args[0])
        self.assertIn("api-version", args[0])
        self.assertIn("Content-Type", kwargs["headers"])
        self.assertIn("api-key", kwargs["headers"])
        
        # Verify the request body
        request_body = json.loads(kwargs["data"])
        self.assertEqual(request_body["search"], query)
        self.assertEqual(request_body["filter"], f"user_id eq '{user_id}'")
        self.assertEqual(request_body["vectors"][0]["value"], embedding)
        self.assertEqual(request_body["vectors"][0]["fields"], "embedding")
        self.assertEqual(request_body["select"], "id,content,file_id,user_id,metadata")
        self.assertEqual(request_body["top"], 10)


class TestMockVectorDatabase(unittest.TestCase):
    """Tests for the MockVectorDatabase class."""

    def setUp(self):
        """Set up test environment."""
        self.vector_db = MockVectorDatabase()
    
    def test_store_document_chunks(self):
        """Test storing document chunks."""
        # Create test data
        file_id = "test-file-id"
        user_id = "test-user-id"
        chunks = [
            {
                "id": "chunk-1",
                "content": "This is the first chunk",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {
                    "page_number": 1,
                    "source": "text"
                }
            },
            {
                "id": "chunk-2",
                "content": "This is the second chunk",
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {
                    "page_number": 2,
                    "source": "table"
                }
            }
        ]
        
        # Call the method to test
        result = self.vector_db.store_document_chunks(file_id, user_id, chunks)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the chunks were stored
        self.assertEqual(len(self.vector_db.documents), 2)
        self.assertEqual(self.vector_db.documents[0]["id"], "chunk-1")
        self.assertEqual(self.vector_db.documents[0]["content"], "This is the first chunk")
        self.assertEqual(self.vector_db.documents[0]["file_id"], file_id)
        self.assertEqual(self.vector_db.documents[0]["user_id"], user_id)
    
    def test_search_documents(self):
        """Test searching documents."""
        # Store some test documents
        file_id = "test-file-id"
        user_id = "test-user-id"
        chunks = [
            {
                "id": "chunk-1",
                "content": "This is a document about vector search",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {
                    "page_number": 1,
                    "source": "text"
                }
            },
            {
                "id": "chunk-2",
                "content": "This is a document about machine learning",
                "embedding": [0.4, 0.5, 0.6],
                "metadata": {
                    "page_number": 2,
                    "source": "text"
                }
            }
        ]
        self.vector_db.store_document_chunks(file_id, user_id, chunks)
        
        # Call the method to test
        results = self.vector_db.search_documents("vector search", user_id, [0.1, 0.2, 0.3])
        
        # Verify the result
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "chunk-1")
        self.assertEqual(results[0]["content"], "This is a document about vector search")
        self.assertEqual(results[0]["file_id"], file_id)
        self.assertTrue("score" in results[0])


class TestCreateVectorDatabase(unittest.TestCase):
    """Tests for the create_vector_database function."""

    def test_create_vector_database_with_env_vars(self):
        """Test creating a VectorDatabase with environment variables."""
        # Mock environment variables
        with patch.dict(os.environ, {
            "AZURE_SEARCH_SERVICE": "test-search-service",
            "AZURE_SEARCH_API_KEY": "test-api-key"
        }):
            # Call the function to test
            vector_db = create_vector_database()
            
            # Verify the result
            self.assertIsInstance(vector_db, VectorDatabase)
            self.assertEqual(vector_db.search_service_name, "test-search-service")
            self.assertEqual(vector_db.search_api_key, "test-api-key")
    
    def test_create_vector_database_with_params(self):
        """Test creating a VectorDatabase with parameters."""
        # Call the function to test
        vector_db = create_vector_database(
            service_name="custom-service",
            api_key="custom-key",
            index_name="custom-index"
        )
        
        # Verify the result
        self.assertIsInstance(vector_db, VectorDatabase)
        self.assertEqual(vector_db.search_service_name, "custom-service")
        self.assertEqual(vector_db.search_api_key, "custom-key")
        self.assertEqual(vector_db.index_name, "custom-index")
    
    def test_create_mock_vector_database(self):
        """Test creating a MockVectorDatabase."""
        # Call the function to test
        vector_db = create_vector_database(use_mock=True)
        
        # Verify the result
        self.assertIsInstance(vector_db, MockVectorDatabase)
    
    def test_create_mock_vector_database_without_credentials(self):
        """Test creating a MockVectorDatabase when credentials are missing."""
        # Mock environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Call the function to test
            vector_db = create_vector_database()
            
            # Verify the result
            self.assertIsInstance(vector_db, MockVectorDatabase)


if __name__ == "__main__":
    unittest.main() 