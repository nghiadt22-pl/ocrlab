"""
Tests for the handwriting extraction module.

This module contains tests for the HandwritingExtractor class and related functionality.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.handwriting_extraction import (
    HandwritingExtractor,
    create_handwriting_extractor
)
from services.document_intelligence.client import DocumentIntelligenceClient


class TestHandwritingExtractor(unittest.TestCase):
    """Tests for the HandwritingExtractor class."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock client
        self.mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Create a HandwritingExtractor with the mock client
        self.extractor = HandwritingExtractor(self.mock_client)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.extractor.client, self.mock_client)
    
    def test_extract_handwriting(self):
        """Test extracting handwritten text from a document."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {
                "styles": [
                    {
                        "is_handwritten": True,
                        "confidence": 0.95,
                        "span": {
                            "offset": 0,
                            "length": 10
                        },
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    }
                ],
                "spans": [
                    {
                        "offset": 0,
                        "length": 10,
                        "content": "Handwritten"
                    }
                ],
                "pages": [
                    {
                        "page_number": 1,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel",
                        "lines": [
                            {
                                "content": "Handwritten line",
                                "is_handwritten": True,
                                "confidence": 0.9,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 200, 300, 200, 300, 250, 100, 250]
                                    }
                                ]
                            }
                        ],
                        "words": [
                            {
                                "content": "Handwritten",
                                "is_handwritten": True,
                                "confidence": 0.85,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 300, 200, 300, 200, 350, 100, 350]
                                    }
                                ]
                            },
                            {
                                "content": "word",
                                "is_handwritten": True,
                                "confidence": 0.8,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [220, 300, 300, 300, 300, 350, 220, 350]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_handwriting(b"test document")
        
        # Verify the client was called correctly
        self.mock_client.analyze_document.assert_called_once_with(b"test document", model_id="prebuilt-read")
        
        # Verify the result
        self.assertGreater(len(result["handwritten_items"]), 0)
        self.assertEqual(result["handwriting_count"], len(result["handwritten_items"]))
        
        # Verify at least one handwritten item was extracted
        self.assertIn("content", result["handwritten_items"][0])
        self.assertIn("confidence", result["handwritten_items"][0])
        self.assertIn("page_number", result["handwritten_items"][0])
    
    def test_extract_handwriting_empty(self):
        """Test extracting handwritten text from a document with no handwriting."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel"
                    }
                ]
            }
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_handwriting(b"test document")
        
        # Verify the result
        self.assertEqual(len(result["handwritten_items"]), 0)
        self.assertEqual(result["handwriting_count"], 0)
    
    def test_extract_handwritten_items_from_styles(self):
        """Test extracting handwritten items from styles."""
        # Create a mock result with styles
        mock_result = {
            "analyze_result": {
                "styles": [
                    {
                        "is_handwritten": True,
                        "confidence": 0.95,
                        "span": {
                            "offset": 0,
                            "length": 10
                        },
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                            }
                        ]
                    }
                ],
                "spans": [
                    {
                        "offset": 0,
                        "length": 10,
                        "content": "Handwritten"
                    }
                ]
            }
        }
        
        # Call the method to test
        items = self.extractor._extract_handwritten_items(mock_result)
        
        # Verify the result
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["content"], "Handwritten")
        self.assertEqual(items[0]["confidence"], 0.95)
        self.assertEqual(items[0]["page_number"], 1)
    
    def test_extract_handwritten_items_from_lines(self):
        """Test extracting handwritten items from lines."""
        # Create a mock result with handwritten lines
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "lines": [
                            {
                                "content": "Handwritten line",
                                "is_handwritten": True,
                                "confidence": 0.9,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 200, 300, 200, 300, 250, 100, 250]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Call the method to test
        items = self.extractor._extract_handwritten_items(mock_result)
        
        # Verify the result
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["content"], "Handwritten line")
        self.assertEqual(items[0]["confidence"], 0.9)
        self.assertEqual(items[0]["page_number"], 1)
    
    def test_extract_handwritten_items_from_words(self):
        """Test extracting handwritten items from words."""
        # Create a mock result with handwritten words
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "words": [
                            {
                                "content": "Handwritten",
                                "is_handwritten": True,
                                "confidence": 0.85,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 300, 200, 300, 200, 350, 100, 350]
                                    }
                                ]
                            },
                            {
                                "content": "word",
                                "is_handwritten": True,
                                "confidence": 0.8,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [220, 300, 300, 300, 300, 350, 220, 350]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Call the method to test
        items = self.extractor._extract_handwritten_items(mock_result)
        
        # Verify the result
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["content"], "Handwritten")
        self.assertEqual(items[0]["confidence"], 0.85)
        self.assertEqual(items[0]["page_number"], 1)
        self.assertEqual(items[1]["content"], "word")
        self.assertEqual(items[1]["confidence"], 0.8)
        self.assertEqual(items[1]["page_number"], 1)
    
    def test_find_content_for_span(self):
        """Test finding content for a span."""
        # Create mock spans
        spans = [
            {
                "offset": 0,
                "length": 10,
                "content": "Handwritten"
            },
            {
                "offset": 11,
                "length": 4,
                "content": "text"
            }
        ]
        
        # Call the method to test
        content = self.extractor._find_content_for_span(spans, 0, 10)
        
        # Verify the result
        self.assertEqual(content, "Handwritten")
        
        # Test with non-matching span
        content = self.extractor._find_content_for_span(spans, 5, 5)
        self.assertIsNone(content)
    
    def test_find_bounding_box_for_span(self):
        """Test finding bounding box for a span."""
        # Create a mock result
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "lines": [
                            {
                                "span": {
                                    "offset": 0,
                                    "length": 10
                                },
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 100, 300, 100, 300, 150, 100, 150]
                                    }
                                ]
                            }
                        ],
                        "words": [
                            {
                                "span": {
                                    "offset": 11,
                                    "length": 4
                                },
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 200, 200, 200, 200, 250, 100, 250]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Call the method to test for line span
        bounding_box = self.extractor._find_bounding_box_for_span(mock_result, 0, 10)
        
        # Verify the result
        self.assertIsNotNone(bounding_box)
        self.assertEqual(bounding_box["x"], 100)
        self.assertEqual(bounding_box["y"], 100)
        self.assertEqual(bounding_box["width"], 200)
        self.assertEqual(bounding_box["height"], 50)
        
        # Call the method to test for word span
        bounding_box = self.extractor._find_bounding_box_for_span(mock_result, 11, 4)
        
        # Verify the result
        self.assertIsNotNone(bounding_box)
        self.assertEqual(bounding_box["x"], 100)
        self.assertEqual(bounding_box["y"], 200)
        self.assertEqual(bounding_box["width"], 100)
        self.assertEqual(bounding_box["height"], 50)
        
        # Test with non-matching span
        bounding_box = self.extractor._find_bounding_box_for_span(mock_result, 5, 5)
        self.assertIsNone(bounding_box)
    
    def test_get_page_number_from_style(self):
        """Test getting page number from a style element."""
        # Test with bounding regions
        style = {
            "bounding_regions": [
                {
                    "page_number": 3
                }
            ]
        }
        self.assertEqual(self.extractor._get_page_number_from_style(style), 3)
        
        # Test without bounding regions
        style = {}
        self.assertEqual(self.extractor._get_page_number_from_style(style), 1)
    
    def test_merge_handwritten_items(self):
        """Test merging handwritten items."""
        # Create mock items
        items = [
            {
                "id": "handwriting-1",
                "content": "First",
                "confidence": 0.9,
                "page_number": 1,
                "bounding_box": {
                    "x": 100,
                    "y": 100,
                    "width": 100,
                    "height": 50
                }
            },
            {
                "id": "handwriting-2",
                "content": "Second",
                "confidence": 0.85,
                "page_number": 1,
                "bounding_box": {
                    "x": 100,
                    "y": 160,
                    "width": 100,
                    "height": 50
                }
            },
            {
                "id": "handwriting-3",
                "content": "Third",
                "confidence": 0.8,
                "page_number": 2,
                "bounding_box": {
                    "x": 100,
                    "y": 100,
                    "width": 100,
                    "height": 50
                }
            }
        ]
        
        # Call the method to test
        merged = self.extractor._merge_handwritten_items(items)
        
        # Verify the result
        self.assertEqual(len(merged), 2)  # Two groups: one for page 1, one for page 2
        
        # Verify the first merged item (from page 1)
        self.assertEqual(merged[0]["content"], "First Second")
        self.assertAlmostEqual(merged[0]["confidence"], 0.875)  # Average of 0.9 and 0.85
        self.assertEqual(merged[0]["page_number"], 1)
        self.assertEqual(merged[0]["merged_count"], 2)
        
        # Verify the second merged item (from page 2)
        self.assertEqual(merged[1]["content"], "Third")
        self.assertEqual(merged[1]["confidence"], 0.8)
        self.assertEqual(merged[1]["page_number"], 2)
        self.assertEqual(merged[1]["merged_count"], 1)
    
    def test_merge_handwritten_items_empty(self):
        """Test merging empty handwritten items list."""
        # Call the method to test with empty list
        merged = self.extractor._merge_handwritten_items([])
        
        # Verify the result
        self.assertEqual(merged, [])
    
    def test_are_items_close(self):
        """Test checking if items are close to each other."""
        # Create two items that are close vertically
        item1 = {
            "bounding_box": {
                "x": 100,
                "y": 100,
                "width": 100,
                "height": 50
            }
        }
        item2 = {
            "bounding_box": {
                "x": 100,
                "y": 140,
                "width": 100,
                "height": 50
            }
        }
        
        # Call the method to test
        are_close = self.extractor._are_items_close(item1, item2)
        
        # Verify the result
        self.assertTrue(are_close)
        
        # Create two items that are not close vertically
        item1 = {
            "bounding_box": {
                "x": 100,
                "y": 100,
                "width": 100,
                "height": 50
            }
        }
        item2 = {
            "bounding_box": {
                "x": 100,
                "y": 200,
                "width": 100,
                "height": 50
            }
        }
        
        # Call the method to test
        are_close = self.extractor._are_items_close(item1, item2)
        
        # Verify the result
        self.assertFalse(are_close)
        
        # Test with items without bounding box
        item1 = {}
        item2 = {}
        
        # Call the method to test
        are_close = self.extractor._are_items_close(item1, item2)
        
        # Verify the result
        self.assertFalse(are_close)
    
    def test_create_merged_item(self):
        """Test creating a merged item from a group of items."""
        # Create a group of items
        items = [
            {
                "id": "handwriting-1",
                "content": "First",
                "confidence": 0.9,
                "page_number": 1,
                "bounding_box": {
                    "x": 100,
                    "y": 100,
                    "width": 100,
                    "height": 50
                }
            },
            {
                "id": "handwriting-2",
                "content": "Second",
                "confidence": 0.8,
                "page_number": 1,
                "bounding_box": {
                    "x": 100,
                    "y": 160,
                    "width": 120,
                    "height": 60
                }
            }
        ]
        
        # Call the method to test
        merged = self.extractor._create_merged_item(items)
        
        # Verify the result
        self.assertEqual(merged["content"], "First Second")
        self.assertEqual(merged["confidence"], 0.85)  # Average of 0.9 and 0.8
        self.assertEqual(merged["page_number"], 1)
        self.assertEqual(merged["merged_count"], 2)
        
        # Verify the bounding box encompasses both items
        self.assertEqual(merged["bounding_box"]["x"], 100)
        self.assertEqual(merged["bounding_box"]["y"], 100)
        self.assertEqual(merged["bounding_box"]["width"], 120)
        self.assertEqual(merged["bounding_box"]["height"], 120)
        
        # Test with a single item
        merged = self.extractor._create_merged_item([items[0]])
        
        # Verify the result is the same as the original item
        self.assertEqual(merged, items[0])
    
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
        
        # Test with direct bounding_box
        element = {
            "bounding_box": {
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 100
            }
        }
        bounding_box = self.extractor._extract_bounding_box(element)
        self.assertEqual(bounding_box["x"], 100)
        self.assertEqual(bounding_box["y"], 100)
        self.assertEqual(bounding_box["width"], 200)
        self.assertEqual(bounding_box["height"], 100)
        
        # Test without polygon or bounding_box
        element = {
            "bounding_regions": [
                {}
            ]
        }
        self.assertIsNone(self.extractor._extract_bounding_box(element))
        
        # Test without bounding regions
        element = {}
        self.assertIsNone(self.extractor._extract_bounding_box(element))


class TestCreateHandwritingExtractor(unittest.TestCase):
    """Tests for the create_handwriting_extractor function."""
    
    def test_create_extractor(self):
        """Test creating a HandwritingExtractor."""
        # Create a mock client
        mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Call the function to test
        extractor = create_handwriting_extractor(mock_client)
        
        # Verify the result
        self.assertIsInstance(extractor, HandwritingExtractor)
        self.assertEqual(extractor.client, mock_client)


if __name__ == "__main__":
    unittest.main()
