"""
Integration tests for OCR processing functionality.
"""
import os
import json
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ["AzureWebJobsStorage"] = "mock"
os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"] = "https://mock-endpoint.cognitiveservices.azure.com/"
os.environ["DOCUMENT_INTELLIGENCE_API_KEY"] = "mock-key"

# Import after setting environment variables
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from function_app import process_document, extract_document_content, chunk_text

class TestOCRProcessing(unittest.TestCase):
    """Test OCR processing functionality."""
    
    def test_process_document_mock_mode(self):
        """Test process_document function in mock mode."""
        # Test with mock mode enabled
        result = process_document("https://example.com/mock-document.pdf")
        
        # Verify result contains expected mock data
        self.assertIn("content", result)
        self.assertEqual(result["content"], "This is mock OCR content for testing.")
        self.assertIn("tables", result)
        self.assertIn("pages", result)
    
    @patch('function_app.get_document_intelligence_client')
    def test_process_document_with_mocked_client(self, mock_get_client):
        """Test process_document with a mocked Document Intelligence client."""
        # Create mock client and response
        mock_client = MagicMock()
        mock_poller = MagicMock()
        mock_result = MagicMock()
        
        # Setup mock to return our mocked objects
        mock_get_client.return_value = mock_client
        mock_client.begin_analyze_document_from_url.return_value = mock_poller
        mock_poller.result.return_value = mock_result
        
        # Set properties on mock result
        mock_result.content = "Sample document content for testing."
        mock_result.pages = []
        mock_result.tables = []
        
        # Call function with test URL
        os.environ["AzureWebJobsStorage"] = "UseDevelopmentStorage=true"  # Disable mock mode
        result = process_document("https://example.com/test-document.pdf")
        
        # Verify client was called correctly
        mock_client.begin_analyze_document_from_url.assert_called_once_with(
            "prebuilt-layout", 
            "https://example.com/test-document.pdf"
        )
        
        # Restore mock mode
        os.environ["AzureWebJobsStorage"] = "mock"
        
        # Verify result is our mock object
        self.assertEqual(result, mock_result)
    
    def test_extract_document_content(self):
        """Test extract_document_content function."""
        # Test with mock data format
        mock_result = {
            "content": "Test document content.",
            "tables": [{"rowCount": 2, "columnCount": 3, "cells": []}],
            "pages": [{"pageNumber": 1, "width": 8.5, "height": 11.0}]
        }
        
        result = extract_document_content(mock_result)
        
        # Verify result
        self.assertEqual(result["text"], "Test document content.")
        self.assertEqual(len(result["tables"]), 1)
        self.assertEqual(len(result["pages"]), 1)
        self.assertEqual(result["page_count"], 1)
    
    def test_chunk_text(self):
        """Test text chunking function."""
        # Create a long test text with sentences
        test_text = "This is sentence one. This is sentence two. " * 20
        
        # Test chunking with default parameters
        chunks = chunk_text(test_text)
        
        # Verify chunks
        self.assertTrue(len(chunks) > 1, "Text should be split into multiple chunks")
        for chunk in chunks:
            self.assertTrue(len(chunk) <= 1000, "Chunk size should not exceed max_chunk_size")
        
        # Test with empty text
        empty_chunks = chunk_text("")
        self.assertEqual(empty_chunks, [], "Empty text should result in empty chunks list")
        
        # Test with small text that doesn't need chunking
        small_text = "This is a small text."
        small_chunks = chunk_text(small_text)
        self.assertEqual(len(small_chunks), 1, "Small text should be a single chunk")
        self.assertEqual(small_chunks[0], small_text)

if __name__ == '__main__':
    unittest.main() 