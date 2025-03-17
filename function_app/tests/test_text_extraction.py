"""
Tests for the text extraction module.

This module contains tests for the TextExtractor class and related functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.text_extraction import (
    TextExtractor,
    create_text_extractor
)
from services.document_intelligence.client import DocumentIntelligenceClient


class TestTextExtractor(unittest.TestCase):
    """Tests for the TextExtractor class."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock client
        self.mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Create a TextExtractor with the mock client
        self.extractor = TextExtractor(self.mock_client)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.extractor.client, self.mock_client)
    
    def test_extract_text(self):
        """Test extracting text from a document."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {
                "paragraphs": [
                    {
                        "content": "This is a test paragraph.",
                        "confidence": 0.95,
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    }
                ],
                "pages": [
                    {
                        "page_number": 1,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel"
                    }
                ],
                "languages": [
                    {
                        "locale": "en",
                        "confidence": 0.9
                    }
                ]
            }
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_text(b"test document")
        
        # Verify the client was called correctly
        self.mock_client.analyze_document.assert_called_once_with(b"test document", model_id="prebuilt-layout")
        
        # Verify the result
        self.assertEqual(len(result["paragraphs"]), 1)
        self.assertEqual(result["paragraphs"][0]["content"], "This is a test paragraph.")
        self.assertEqual(result["paragraphs"][0]["confidence"], 0.95)
        self.assertEqual(result["paragraphs"][0]["page_number"], 1)
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["page_count"], 1)
    
    def test_extract_paragraphs(self):
        """Test extracting paragraphs from analysis result."""
        # Create a mock result
        mock_result = {
            "analyze_result": {
                "paragraphs": [
                    {
                        "content": "Paragraph 1",
                        "confidence": 0.95,
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    },
                    {
                        "content": "Paragraph 2",
                        "confidence": 0.9,
                        "bounding_regions": [
                            {
                                "page_number": 2,
                                "polygon": [100, 200, 300, 200, 300, 250, 100, 250]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Call the method to test
        paragraphs = self.extractor._extract_paragraphs(mock_result)
        
        # Verify the result
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0]["content"], "Paragraph 1")
        self.assertEqual(paragraphs[0]["confidence"], 0.95)
        self.assertEqual(paragraphs[0]["page_number"], 1)
        self.assertEqual(paragraphs[1]["content"], "Paragraph 2")
        self.assertEqual(paragraphs[1]["confidence"], 0.9)
        self.assertEqual(paragraphs[1]["page_number"], 2)
    
    def test_extract_content_by_page(self):
        """Test extracting content by page from analysis result."""
        # Create a mock result
        mock_result = {
            "analyze_result": {
                "paragraphs": [
                    {
                        "content": "Paragraph on page 1",
                        "confidence": 0.95,
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    },
                    {
                        "content": "Another paragraph on page 1",
                        "confidence": 0.9,
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 200, 300, 200, 300, 250, 100, 250]
                            }
                        ]
                    },
                    {
                        "content": "Paragraph on page 2",
                        "confidence": 0.85,
                        "bounding_regions": [
                            {
                                "page_number": 2,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    }
                ],
                "pages": [
                    {
                        "page_number": 1,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel"
                    },
                    {
                        "page_number": 2,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel"
                    }
                ]
            }
        }
        
        # Call the method to test
        pages = self.extractor._extract_content_by_page(mock_result)
        
        # Verify the result
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0]["page_number"], 1)
        self.assertEqual(pages[0]["width"], 612)
        self.assertEqual(pages[0]["height"], 792)
        self.assertEqual(len(pages[0]["paragraphs"]), 2)
        self.assertEqual(pages[0]["paragraphs"][0]["content"], "Paragraph on page 1")
        self.assertEqual(pages[0]["paragraphs"][1]["content"], "Another paragraph on page 1")
        self.assertEqual(pages[0]["text"], "Paragraph on page 1\nAnother paragraph on page 1")
        
        self.assertEqual(pages[1]["page_number"], 2)
        self.assertEqual(len(pages[1]["paragraphs"]), 1)
        self.assertEqual(pages[1]["paragraphs"][0]["content"], "Paragraph on page 2")
        self.assertEqual(pages[1]["text"], "Paragraph on page 2")
    
    def test_get_page_text(self):
        """Test getting page text from paragraphs."""
        # Create mock paragraphs
        paragraphs = [
            {"content": "Paragraph 1"},
            {"content": "Paragraph 2"},
            {"content": "Paragraph 3"}
        ]
        
        # Call the method to test
        text = self.extractor._get_page_text(paragraphs)
        
        # Verify the result
        self.assertEqual(text, "Paragraph 1\nParagraph 2\nParagraph 3")
    
    def test_get_page_number(self):
        """Test getting page number from an element."""
        # Test with bounding regions
        element = {
            "bounding_regions": [
                {
                    "page_number": 3
                }
            ]
        }
        self.assertEqual(self.extractor._get_page_number(element), 3)
        
        # Test without bounding regions
        element = {}
        self.assertEqual(self.extractor._get_page_number(element), 1)
    
    def test_extract_bounding_box(self):
        """Test extracting bounding box from an element."""
        # Test with polygon
        element = {
            "bounding_regions": [
                {
                    "polygon": [100, 100, 300, 100, 300, 200, 100, 200]
                }
            ]
        }
        bounding_box = self.extractor._extract_bounding_box(element)
        self.assertEqual(bounding_box["x"], 100)
        self.assertEqual(bounding_box["y"], 100)
        self.assertEqual(bounding_box["width"], 200)
        self.assertEqual(bounding_box["height"], 100)
        
        # Test without polygon
        element = {
            "bounding_regions": [
                {}
            ]
        }
        self.assertIsNone(self.extractor._extract_bounding_box(element))
        
        # Test without bounding regions
        element = {}
        self.assertIsNone(self.extractor._extract_bounding_box(element))
    
    def test_determine_document_type(self):
        """Test determining document type from analysis result."""
        # Test with document type
        result = {
            "analyze_result": {
                "documents": [
                    {
                        "doc_type": "invoice"
                    }
                ]
            }
        }
        self.assertEqual(self.extractor._determine_document_type(result), "invoice")
        
        # Test without document type
        result = {
            "analyze_result": {}
        }
        self.assertEqual(self.extractor._determine_document_type(result), "general")
    
    def test_extract_language(self):
        """Test extracting language from analysis result."""
        # Test with language
        result = {
            "analyze_result": {
                "languages": [
                    {
                        "locale": "fr"
                    }
                ]
            }
        }
        self.assertEqual(self.extractor._extract_language(result), "fr")
        
        # Test without language
        result = {
            "analyze_result": {}
        }
        self.assertEqual(self.extractor._extract_language(result), "en")
    
    def test_get_page_count(self):
        """Test getting page count from analysis result."""
        # Test with pages
        result = {
            "analyze_result": {
                "pages": [
                    {"page_number": 1},
                    {"page_number": 2},
                    {"page_number": 3}
                ]
            }
        }
        self.assertEqual(self.extractor._get_page_count(result), 3)
        
        # Test without pages
        result = {
            "analyze_result": {}
        }
        self.assertEqual(self.extractor._get_page_count(result), 0)


class TestCreateTextExtractor(unittest.TestCase):
    """Tests for the create_text_extractor function."""
    
    def test_create_extractor(self):
        """Test creating a TextExtractor."""
        # Create a mock client
        mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Call the function to test
        extractor = create_text_extractor(mock_client)
        
        # Verify the result
        self.assertIsInstance(extractor, TextExtractor)
        self.assertEqual(extractor.client, mock_client)


if __name__ == "__main__":
    unittest.main() 