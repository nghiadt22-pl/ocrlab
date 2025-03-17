"""
Tests for the image extraction module.

This module contains tests for the ImageExtractor class and related functionality.
"""

import os
import sys
import unittest
import base64
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.document_intelligence.image_extraction import (
    ImageExtractor,
    create_image_extractor
)
from services.document_intelligence.client import DocumentIntelligenceClient


class TestImageExtractor(unittest.TestCase):
    """Tests for the ImageExtractor class."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock client
        self.mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Create an ImageExtractor with the mock client
        self.extractor = ImageExtractor(self.mock_client)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.extractor.client, self.mock_client)
    
    def test_extract_images(self):
        """Test extracting images from a document."""
        # Mock the analyze_document method of the client
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "width": 612,
                        "height": 792,
                        "unit": "pixel",
                        "images": [
                            {
                                "confidence": 0.95,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 100, 300, 100, 300, 200, 100, 200]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "visual_elements": [
                    {
                        "kind": "image",
                        "confidence": 0.9,
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [400, 100, 500, 100, 500, 200, 400, 200]
                            }
                        ]
                    }
                ],
                "figures": [
                    {
                        "confidence": 0.85,
                        "bounding_regions": [
                            {
                                "page_number": 2,
                                "polygon": [100, 100, 300, 100, 300, 200, 100, 200]
                            }
                        ]
                    }
                ]
            }
        }
        self.mock_client.analyze_document.return_value = mock_result
        
        # Call the method to test
        result = self.extractor.extract_images(b"test document")
        
        # Verify the client was called correctly
        self.mock_client.analyze_document.assert_called_once_with(b"test document", model_id="prebuilt-document")
        
        # Verify the result
        self.assertEqual(len(result["images"]), 3)
        self.assertEqual(result["image_count"], 3)
        
        # Verify the first image (from pages)
        self.assertEqual(result["images"][0]["page_number"], 1)
        self.assertEqual(result["images"][0]["confidence"], 0.95)
        self.assertIsNotNone(result["images"][0]["bounding_box"])
        self.assertIsNotNone(result["images"][0]["content"])
        
        # Verify the second image (from visual_elements)
        self.assertEqual(result["images"][1]["page_number"], 1)
        self.assertEqual(result["images"][1]["confidence"], 0.9)
        self.assertIsNotNone(result["images"][1]["bounding_box"])
        self.assertIsNotNone(result["images"][1]["content"])
        
        # Verify the third image (from figures)
        self.assertEqual(result["images"][2]["page_number"], 2)
        self.assertEqual(result["images"][2]["confidence"], 0.85)
        self.assertIsNotNone(result["images"][2]["bounding_box"])
        self.assertIsNotNone(result["images"][2]["content"])
    
    def test_extract_images_empty(self):
        """Test extracting images from a document with no images."""
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
        result = self.extractor.extract_images(b"test document")
        
        # Verify the result
        self.assertEqual(len(result["images"]), 0)
        self.assertEqual(result["image_count"], 0)
    
    def test_extract_images_method(self):
        """Test the _extract_images method."""
        # Create a mock result
        mock_result = {
            "analyze_result": {
                "pages": [
                    {
                        "page_number": 1,
                        "images": [
                            {
                                "confidence": 0.95,
                                "bounding_regions": [
                                    {
                                        "page_number": 1,
                                        "polygon": [100, 100, 300, 100, 300, 200, 100, 200]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Call the method to test
        images = self.extractor._extract_images(mock_result)
        
        # Verify the result
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["page_number"], 1)
        self.assertEqual(images[0]["confidence"], 0.95)
        self.assertIsNotNone(images[0]["bounding_box"])
        self.assertIsNotNone(images[0]["content"])
    
    def test_get_image_content_with_url(self):
        """Test getting image content with URL."""
        # Create a mock image with URL
        image = {
            "url": "https://example.com/image.png"
        }
        
        # Call the method to test
        content = self.extractor._get_image_content(image)
        
        # Verify the result
        self.assertEqual(content, "https://example.com/image.png")
    
    def test_get_image_content_with_data(self):
        """Test getting image content with binary data."""
        # Create a mock image with binary data
        image_data = b"test image data"
        image = {
            "data": image_data,
            "mime_type": "image/png"
        }
        
        # Call the method to test
        with patch("base64.b64encode", return_value=b"dGVzdCBpbWFnZSBkYXRh"):
            content = self.extractor._get_image_content(image)
        
        # Verify the result
        self.assertEqual(content, "data:image/png;base64,dGVzdCBpbWFnZSBkYXRh")
    
    def test_get_image_content_fallback(self):
        """Test getting image content with fallback."""
        # Create a mock image with no URL or data
        image = {}
        
        # Call the method to test
        content = self.extractor._get_image_content(image)
        
        # Verify the result
        self.assertEqual(content, "https://placehold.co/600x400/png")
    
    def test_deduplicate_images(self):
        """Test deduplicating images."""
        # Create mock images with overlapping bounding boxes
        images = [
            {
                "id": "image-1",
                "page_number": 1,
                "confidence": 0.95,
                "bounding_box": {
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 100
                }
            },
            {
                "id": "image-2",
                "page_number": 1,
                "confidence": 0.9,
                "bounding_box": {
                    "x": 110,
                    "y": 110,
                    "width": 180,
                    "height": 80
                }
            },
            {
                "id": "image-3",
                "page_number": 2,
                "confidence": 0.85,
                "bounding_box": {
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 100
                }
            }
        ]
        
        # Call the method to test
        deduplicated = self.extractor._deduplicate_images(images)
        
        # Verify the result
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(deduplicated[0]["id"], "image-1")  # First image on page 1
        self.assertEqual(deduplicated[1]["id"], "image-3")  # First image on page 2
    
    def test_deduplicate_images_no_bounding_box(self):
        """Test deduplicating images with no bounding box."""
        # Create mock images with no bounding box
        images = [
            {
                "id": "image-1",
                "page_number": 1,
                "confidence": 0.95
            },
            {
                "id": "image-2",
                "page_number": 1,
                "confidence": 0.9
            }
        ]
        
        # Call the method to test
        deduplicated = self.extractor._deduplicate_images(images)
        
        # Verify the result
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(deduplicated[0]["id"], "image-1")
        self.assertEqual(deduplicated[1]["id"], "image-2")
    
    def test_calculate_overlap(self):
        """Test calculating overlap between bounding boxes."""
        # Create two overlapping bounding boxes
        box1 = {
            "x": 100,
            "y": 100,
            "width": 200,
            "height": 100
        }
        box2 = {
            "x": 150,
            "y": 150,
            "width": 200,
            "height": 100
        }
        
        # Call the method to test
        overlap = self.extractor._calculate_overlap(box1, box2)
        
        # Verify the result
        self.assertGreater(overlap, 0)
        self.assertLess(overlap, 1)
    
    def test_calculate_overlap_no_overlap(self):
        """Test calculating overlap between non-overlapping bounding boxes."""
        # Create two non-overlapping bounding boxes
        box1 = {
            "x": 100,
            "y": 100,
            "width": 100,
            "height": 100
        }
        box2 = {
            "x": 300,
            "y": 300,
            "width": 100,
            "height": 100
        }
        
        # Call the method to test
        overlap = self.extractor._calculate_overlap(box1, box2)
        
        # Verify the result
        self.assertEqual(overlap, 0)
    
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


class TestCreateImageExtractor(unittest.TestCase):
    """Tests for the create_image_extractor function."""
    
    def test_create_extractor(self):
        """Test creating an ImageExtractor."""
        # Create a mock client
        mock_client = MagicMock(spec=DocumentIntelligenceClient)
        
        # Call the function to test
        extractor = create_image_extractor(mock_client)
        
        # Verify the result
        self.assertIsInstance(extractor, ImageExtractor)
        self.assertEqual(extractor.client, mock_client)


if __name__ == "__main__":
    unittest.main()
