"""
Tests for the Document Intelligence client module.

This module contains tests for the DocumentIntelligenceClient class and related functionality.
"""

import os
import unittest
import json
import sys
from unittest.mock import patch, MagicMock, mock_open
from typing import Dict, Any

import pytest
from azure.core.exceptions import ServiceRequestError, ClientAuthenticationError, ResourceNotFoundError

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.client import (
    DocumentIntelligenceClient,
    create_document_intelligence_client
)


class TestDocumentIntelligenceClient(unittest.TestCase):
    """Tests for the DocumentIntelligenceClient class."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "https://test-endpoint.cognitiveservices.azure.com/",
            "AZURE_DOCUMENT_INTELLIGENCE_KEY": "test-api-key"
        })
        self.env_patcher.start()
        
        # Create a client for testing
        self.client = DocumentIntelligenceClient()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        client = DocumentIntelligenceClient()
        self.assertEqual(client.endpoint, "https://test-endpoint.cognitiveservices.azure.com/")
        self.assertEqual(client.api_key, "test-api-key")
    
    def test_init_with_params(self):
        """Test initialization with parameters."""
        client = DocumentIntelligenceClient(
            endpoint="https://custom-endpoint.cognitiveservices.azure.com/",
            api_key="custom-api-key"
        )
        self.assertEqual(client.endpoint, "https://custom-endpoint.cognitiveservices.azure.com/")
        self.assertEqual(client.api_key, "custom-api-key")
    
    def test_init_missing_endpoint(self):
        """Test initialization with missing endpoint."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                DocumentIntelligenceClient(api_key="test-api-key")
    
    def test_init_missing_api_key(self):
        """Test initialization with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                DocumentIntelligenceClient(endpoint="https://test-endpoint.cognitiveservices.azure.com/")
    
    @patch("services.document_intelligence.client.AzureDocumentIntelligenceClient")
    def test_get_document_intelligence_client(self, mock_client_class):
        """Test getting a document intelligence client."""
        self.client.get_document_intelligence_client()
        mock_client_class.assert_called_once_with(
            endpoint="https://test-endpoint.cognitiveservices.azure.com/",
            credential=self.client.credential
        )
    
    def test_analyze_document_success(self):
        """Test successful document analysis."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"analyze_result": {"paragraphs": []}}
        mock_poller.result.return_value = mock_result
        mock_client.begin_analyze_document.return_value = mock_poller
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            result = self.client.analyze_document(b"test document", "prebuilt-layout")
            
            # Verify the client was called correctly
            mock_client.begin_analyze_document.assert_called_once_with("prebuilt-layout", b"test document")
            
            # Verify the result was processed correctly
            self.assertEqual(result, {"analyze_result": {"paragraphs": []}})
    
    def test_analyze_document_retry_success(self):
        """Test document analysis with retry."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"analyze_result": {"paragraphs": []}}
        mock_poller.result.return_value = mock_result
        
        # First call raises an error, second call succeeds
        mock_client.begin_analyze_document.side_effect = [
            ServiceRequestError("Test error"),
            mock_poller
        ]
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                result = self.client.analyze_document(b"test document", "prebuilt-layout")
                
                # Verify the client was called twice
                self.assertEqual(mock_client.begin_analyze_document.call_count, 2)
                
                # Verify sleep was called
                mock_sleep.assert_called_once()
                
                # Verify the result was processed correctly
                self.assertEqual(result, {"analyze_result": {"paragraphs": []}})
    
    def test_analyze_document_max_retries(self):
        """Test document analysis with maximum retries."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        
        # All calls raise an error
        mock_client.begin_analyze_document.side_effect = ServiceRequestError("Test error")
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                with self.assertRaises(Exception) as context:
                    self.client.analyze_document(b"test document", "prebuilt-layout")
                
                # Verify the client was called the maximum number of times
                self.assertEqual(mock_client.begin_analyze_document.call_count, 3)
                
                # Verify sleep was called twice (after first and second attempts)
                self.assertEqual(mock_sleep.call_count, 2)
                
                # Verify the error message
                self.assertIn("Document analysis failed", str(context.exception))
    
    def test_analyze_document_resource_not_found(self):
        """Test document analysis with resource not found error."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        
        # Call raises a resource not found error
        mock_client.begin_analyze_document.side_effect = ResourceNotFoundError("Model not found")
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            with self.assertRaises(Exception) as context:
                self.client.analyze_document(b"test document", "nonexistent-model")
            
            # Verify the client was called once
            mock_client.begin_analyze_document.assert_called_once()
            
            # Verify the error message
            self.assertIn("Model 'nonexistent-model' not found", str(context.exception))
    
    def test_get_available_models_success(self):
        """Test successful retrieval of available models."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        mock_model = MagicMock()
        mock_model.to_dict.return_value = {"modelId": "prebuilt-layout"}
        mock_client.list_operations.return_value = [mock_model]
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            result = self.client.get_available_models()
            
            # Verify the client was called correctly
            mock_client.list_operations.assert_called_once()
            
            # Verify the result was processed correctly
            self.assertEqual(result, [{"modelId": "prebuilt-layout"}])
    
    def test_get_available_models_retry_success(self):
        """Test retrieval of available models with retry."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        mock_model = MagicMock()
        mock_model.to_dict.return_value = {"modelId": "prebuilt-layout"}
        
        # First call raises an error, second call succeeds
        mock_client.list_operations.side_effect = [
            ServiceRequestError("Test error"),
            [mock_model]
        ]
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                result = self.client.get_available_models()
                
                # Verify the client was called twice
                self.assertEqual(mock_client.list_operations.call_count, 2)
                
                # Verify sleep was called
                mock_sleep.assert_called_once()
                
                # Verify the result was processed correctly
                self.assertEqual(result, [{"modelId": "prebuilt-layout"}])
    
    def test_get_available_models_max_retries(self):
        """Test retrieval of available models with maximum retries."""
        # Mock the document intelligence client
        mock_client = MagicMock()
        
        # All calls raise an error
        mock_client.list_operations.side_effect = ServiceRequestError("Test error")
        
        with patch.object(self.client, "get_document_intelligence_client", return_value=mock_client):
            with patch("time.sleep") as mock_sleep:  # Mock sleep to speed up test
                with self.assertRaises(Exception) as context:
                    self.client.get_available_models()
                
                # Verify the client was called the maximum number of times
                self.assertEqual(mock_client.list_operations.call_count, 3)
                
                # Verify sleep was called twice (after first and second attempts)
                self.assertEqual(mock_sleep.call_count, 2)
                
                # Verify the error message
                self.assertIn("Failed to get available models", str(context.exception))


class TestCreateDocumentIntelligenceClient(unittest.TestCase):
    """Tests for the create_document_intelligence_client function."""
    
    def test_create_client(self):
        """Test creating a client."""
        with patch("services.document_intelligence.client.DocumentIntelligenceClient") as mock_client:
            create_document_intelligence_client(
                endpoint="https://test-endpoint.cognitiveservices.azure.com/",
                api_key="test-api-key"
            )
            mock_client.assert_called_once_with(
                endpoint="https://test-endpoint.cognitiveservices.azure.com/",
                api_key="test-api-key"
            )


if __name__ == "__main__":
    unittest.main() 